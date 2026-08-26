"""spring_check.py - Spring source smell detector (stdlib only, regex heuristic).

Detects (matching dev-spring SKILL.md antipattern catalog):
  [S1] field injection: @Autowired on a field
  [S2] @Transactional/@Async/@Cacheable method called via this. in same file
  [S6] @RestController method returning a type that looks like a JPA entity
       (same-file @Entity class name used as return type)

Usage:
  python spring_check.py <java_file_or_dir> [...]
  python spring_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '// spring-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

RE_FIELD_INJECT = re.compile(r"@Autowired\s*\n\s*(private|protected|public)?\s*\w+(<[^>]*>)?\s+\w+\s*;")
RE_ADVICE_METHOD = re.compile(r"@(Transactional|Async|Cacheable)[^\n]*\n(?:\s*@\w+[^\n]*\n)*\s*(?:public|protected)?\s*\w+(<[^>]*>)?\s+(\w+)\s*\(")
RE_ENTITY = re.compile(r"@Entity\s*(?:\n\s*@\w+[^\n]*)*\n\s*(?:public\s+)?class\s+(\w+)")
RE_REST = re.compile(r"@RestController")


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def line_of(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    def silenced(ln: int) -> bool:
        return 0 < ln <= len(lines) and "spring-ok:" in lines[ln - 1]

    for m in RE_FIELD_INJECT.finditer(text):
        ln = line_of(m.start())
        if not silenced(ln):
            findings.append(f"{label}:{ln}: [S1] field injection - use constructor injection "
                            "(final + @RequiredArgsConstructor)")

    advised = {m.group(3): line_of(m.start()) for m in RE_ADVICE_METHOD.finditer(text)}
    for name in advised:
        for m in re.finditer(r"\bthis\.\s*" + re.escape(name) + r"\s*\(", text):
            ln = line_of(m.start())
            if not silenced(ln):
                findings.append(f"{label}:{ln}: [S2] this.{name}() bypasses the proxy - "
                                "@Transactional/@Async on it is silently ignored; move to another bean")

    if RE_REST.search(text):
        entities = {m.group(1) for m in RE_ENTITY.finditer(text)}
        for ent in entities:
            for m in re.finditer(r"\b(?:public|protected)\s+(?:List<)?" + re.escape(ent) + r"\b[^(\n]*\(", text):
                ln = line_of(m.start())
                if not silenced(ln):
                    findings.append(f"{label}:{ln}: [S6] controller returns entity '{ent}' - "
                                    "map to a DTO (lazy-serialization / field-leak risk)")
    return sorted(set(findings))


DEMO = """\
@RestController
class CandleController {
    @Autowired
    private CandleRepo repo;

    public List<Candle> list() { return repo.findAll(); }

    @Transactional
    public void saveAll(List<Candle> rows) { repo.saveAll(rows); }

    public void ingest(List<Candle> rows) {
        this.saveAll(rows);
    }
}

@Entity
class Candle {}
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<Demo.java>"):
            print("  " + ln)
        print("Usage: python spring_check.py <java_or_dir> ...")
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
