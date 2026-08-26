"""sql_check.py - regex-based SQL smell detector (stdlib only).

Detects (matching dev-postgres SKILL.md antipattern catalog):
  [Q3] function/cast wrapped around a column in WHERE   (catalog #3, heuristic)
  [Q4] OFFSET pagination                                (catalog #4)
  [QS] SELECT * in non-trivial query                    (column bloat / index-only scan killer)
  [QL] LIKE/ILIKE with leading wildcard '%...'          (cannot use btree index)

Scans .sql files and SQL string literals inside .py files.

Usage:
  python sql_check.py <file_or_dir> [...]
  python sql_check.py              (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Heuristic - silence a line with comment 'sql-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

CHECKS: list[tuple[str, re.Pattern[str], str]] = [
    ("Q4", re.compile(r"\bOFFSET\s+(\d{3,}|[:%$@]?\w*offset\w*)", re.I),
     "OFFSET pagination - linear cost at deep pages; use keyset (WHERE key < :cursor)"),
    ("QS", re.compile(r"\bSELECT\s+\*\s+FROM\b", re.I),
     "SELECT * - fetches unused columns, blocks index-only scans; list columns"),
    ("QL", re.compile(r"\b(I?LIKE)\s+'%", re.I),
     "leading-wildcard LIKE - btree index unusable; consider pg_trgm GIN or full-text"),
    # date(col) = / lower(col) = / col::type = in WHERE-ish context
    ("Q3", re.compile(r"\bWHERE\b[^;]{0,200}?\b(date|lower|upper|trunc|to_char)\s*\(\s*\w+[\w.]*\s*\)\s*[=<>]", re.I | re.S),
     "function around column in WHERE - plain index unusable; rewrite as range or add expression index"),
    ("Q3", re.compile(r"\bWHERE\b[^;]{0,200}?\w+::\w+\s*[=<>]", re.I | re.S),
     "cast on column in WHERE - index unusable; cast the literal side instead"),
]


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    for code, pattern, msg in CHECKS:
        for m in pattern.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            line = text.splitlines()[line_no - 1] if line_no <= len(text.splitlines()) else ""
            if "sql-ok:" in line:
                continue
            findings.append(f"{label}:{line_no}: [{code}] {msg}")
    return sorted(set(findings))


def extract_sql_from_py(source: str) -> str:
    """Cheap pass: just scan the whole file text - SQL keywords rarely false-positive in py."""
    return source


def iter_files(paths: list[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                out.extend(os.path.join(root, f) for f in files if f.endswith((".sql", ".py")))
        else:
            out.append(p)
    return out


DEMO = """\
SELECT * FROM candles WHERE date(ts) = '2026-06-11';
SELECT code, close FROM candles WHERE code = :c ORDER BY base_date LIMIT 50 OFFSET 100000;
SELECT name FROM stocks WHERE name LIKE '%전자';
SELECT code, close FROM candles WHERE code = :c AND base_date >= :d;  -- clean
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python sql_check.py <file_or_dir> ...")
        return 0

    total = 0
    for path in iter_files(argv):
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"{path}: not found - skipped")
            continue
        except UnicodeDecodeError:
            with open(path, encoding="cp949", errors="replace") as f:
                text = f.read()
            print(f"{path}: not utf-8 (read as cp949) - encoding smell, see dev-python P6")
        if path.endswith(".py"):
            text = extract_sql_from_py(text)
        for ln in scan_text(text, path):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
