"""jpa_check.py - JPA mapping smell detector (stdlib only, regex heuristic).

Detects (matching dev-spring-jpa SKILL.md antipattern catalog):
  [P3] fetch = FetchType.EAGER anywhere
  [P3b] @ManyToOne / @OneToOne without explicit fetch (defaults to EAGER!)
  [P5] @Entity class with public setters (all-purpose mutation)
  [P2] join fetch on a collection together with Pageable in same repository file

Usage:
  python jpa_check.py <java_file_or_dir> [...]
  python jpa_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '// jpa-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

RE_EAGER = re.compile(r"fetch\s*=\s*FetchType\.EAGER")
RE_TOONE_NOFETCH = re.compile(r"@(ManyToOne|OneToOne)\s*(?:\(([^)]*)\))?")
RE_ENTITY = re.compile(r"@Entity")
RE_SETTER = re.compile(r"public\s+void\s+set[A-Z]\w*\s*\(")
RE_COLLECTION_FETCH = re.compile(r"join\s+fetch\s+\w+\.\w+s\b", re.I)  # plural heuristic
RE_PAGEABLE = re.compile(r"\bPageable\b")


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def line_of(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    def silenced(ln: int) -> bool:
        return 0 < ln <= len(lines) and "jpa-ok:" in lines[ln - 1]

    for m in RE_EAGER.finditer(text):
        ln = line_of(m.start())
        if not silenced(ln):
            findings.append(f"{label}:{ln}: [P3] FetchType.EAGER - per-use fetch joins instead; "
                            "EAGER makes every query drag the association")

    for m in RE_TOONE_NOFETCH.finditer(text):
        args = m.group(2) or ""
        if "fetch" not in args:
            ln = line_of(m.start())
            if not silenced(ln):
                findings.append(f"{label}:{ln}: [P3b] @{m.group(1)} without fetch= - "
                                "defaults to EAGER; declare LAZY explicitly")

    if RE_ENTITY.search(text):
        setters = RE_SETTER.findall(text)
        if len(setters) >= 3:
            ln = line_of(RE_ENTITY.search(text).start())
            if not silenced(ln):
                findings.append(f"{label}:{ln}: [P5] entity with {len(setters)} public setters - "
                                "use intent-named methods; dirty checking will persist any change")

    if RE_COLLECTION_FETCH.search(text) and RE_PAGEABLE.search(text):
        ln = line_of(RE_COLLECTION_FETCH.search(text).start())
        if not silenced(ln):
            findings.append(f"{label}:{ln}: [P2] collection join fetch + Pageable in same file - "
                            "check HHH000104: paging may happen in memory")
    return sorted(set(findings))


DEMO = """\
@Entity
class Order {
    @ManyToOne
    Member member;
    @OneToMany(fetch = FetchType.EAGER)
    List<Item> items;
    public void setStatus(String s) {}
    public void setMember(Member m) {}
    public void setItems(List<Item> i) {}
}
interface OrderRepo {
    @Query("select o from Order o join fetch o.items")
    Page<Order> findAllWithItems(Pageable p);
}
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<Demo.java>"):
            print("  " + ln)
        print("Usage: python jpa_check.py <java_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, _dirs, fs in os.walk(p):
                paths.extend(os.path.join(root, f) for f in fs if f.endswith(".java"))
        else:
            paths.append(p)
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        for ln in scan_text(text, path):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
