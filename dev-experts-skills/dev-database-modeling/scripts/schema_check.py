"""schema_check.py - DDL smell detector (stdlib only, regex heuristic).

Detects (matching dev-database-modeling SKILL.md type table):
  [M-FLOAT] float/real/double column whose name smells like money (price/amount/fee/...)
  [M-TS]    timestamp without time zone (naive)
  [M-FK]    *_id column with no REFERENCES in the same statement (orphan-able)
  [M-CHAR]  char(n) fixed-width (padding trap)

Scans .sql files.

Usage:
  python schema_check.py <sql_file_or_dir> [...]
  python schema_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '-- schema-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

MONEY = re.compile(r"(price|amount|fee|cost|balance|total|close|open|high|low)", re.I)
RE_FLOAT = re.compile(r"^\s*(\w+)\s+(float|real|double precision)\b", re.I | re.M)
RE_NAIVE_TS = re.compile(r"^\s*(\w+)\s+timestamp\b(?!\s*tz| with time zone)", re.I | re.M)
RE_ID_COL = re.compile(r"^\s*(\w+_id)\s+\w+", re.I | re.M)
RE_CHAR = re.compile(r"^\s*(\w+)\s+char\s*\(\s*\d+\s*\)", re.I | re.M)


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def line_of(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    def silenced(ln: int) -> bool:
        return 0 < ln <= len(lines) and "schema-ok:" in lines[ln - 1]

    for m in RE_FLOAT.finditer(text):
        ln = line_of(m.start())
        if MONEY.search(m.group(1)) and not silenced(ln):
            findings.append(f"{label}:{ln}: [M-FLOAT] money-like '{m.group(1)}' as {m.group(2)} - "
                            "use numeric or integer minor units (0.1 is not 0.1 in binary)")
    for m in RE_NAIVE_TS.finditer(text):
        ln = line_of(m.start())
        if not silenced(ln):
            findings.append(f"{label}:{ln}: [M-TS] '{m.group(1)}' naive timestamp - use timestamptz (UTC)")
    for m in RE_ID_COL.finditer(text):
        ln = line_of(m.start())
        line = lines[ln - 1]
        if "references" not in line.lower() and not silenced(ln):
            # crude: also accept a later ALTER/FOREIGN KEY mentioning the column
            if not re.search(r"foreign key\s*\(\s*" + re.escape(m.group(1)), text, re.I):
                findings.append(f"{label}:{ln}: [M-FK] '{m.group(1)}' without REFERENCES - "
                                "orphan rows possible; constrain it (and index the FK)")
    for m in RE_CHAR.finditer(text):
        ln = line_of(m.start())
        if not silenced(ln):
            findings.append(f"{label}:{ln}: [M-CHAR] '{m.group(1)}' char(n) - space padding trap; use text + CHECK")
    return sorted(set(findings))


DEMO = """\
CREATE TABLE candles (
  id bigint PRIMARY KEY,
  code char(6),
  close float,
  ingested_at timestamp,
  run_id bigint,
  UNIQUE (code, ingested_at)
);
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo.sql>"):
            print("  " + ln)
        print("Usage: python schema_check.py <sql_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, _dirs, fs in os.walk(p):
                paths.extend(os.path.join(root, f) for f in fs if f.endswith(".sql"))
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
