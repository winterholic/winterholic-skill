"""java_check.py - Java source smell detector (stdlib only, regex heuristic).

Detects (matching dev-java SKILL.md antipattern catalog):
  [J1] equals() overridden without hashCode() in the same file
  [J5] java.util.Date / Calendar import (use java.time)
  [J3] e.printStackTrace() (not handling)
  [J2] raw generic type in declarations (List x = / Map y =)

Usage:
  python java_check.py <java_file_or_dir> [...]
  python java_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '// java-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

RE_EQUALS = re.compile(r"\bpublic\s+boolean\s+equals\s*\(\s*Object\b")
RE_HASH = re.compile(r"\bpublic\s+int\s+hashCode\s*\(")
RE_DATE = re.compile(r"import\s+java\.util\.(Date|Calendar)\s*;")
RE_PST = re.compile(r"\.printStackTrace\s*\(")
RE_RAW = re.compile(r"\b(List|Map|Set|Collection)\s+\w+\s*[=;]")


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def silenced(ln: int) -> bool:
        return 0 < ln <= len(lines) and "java-ok:" in lines[ln - 1]

    if RE_EQUALS.search(text) and not RE_HASH.search(text):
        ln = text[:RE_EQUALS.search(text).start()].count("\n") + 1
        findings.append(f"{label}:{ln}: [J1] equals() without hashCode() - contract broken; "
                        "hash collections will silently misbehave (or use a record)")

    for pattern, code, msg in (
        (RE_DATE, "J5", "java.util.Date/Calendar - mutable legacy; use java.time"),
        (RE_PST, "J3", "printStackTrace() is not handling - log with context or rethrow"),
        (RE_RAW, "J2", "raw generic type - loses type safety; parameterize (List<Tick>)"),
    ):
        for m in pattern.finditer(text):
            ln = text[:m.start()].count("\n") + 1
            if not silenced(ln):
                findings.append(f"{label}:{ln}: [{code}] {msg}")
    return sorted(set(findings))


DEMO = """\
import java.util.Date;
import java.util.List;

class Tick {
    public boolean equals(Object o) { return true; }
    void load() {
        List rows = fetch();
        try { parse(rows); } catch (Exception e) { e.printStackTrace(); }
    }
}
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<Demo.java>"):
            print("  " + ln)
        print("Usage: python java_check.py <java_or_dir> ...")
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
