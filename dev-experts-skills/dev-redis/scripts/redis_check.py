"""redis_check.py - Redis usage smell detector (stdlib only, regex heuristic).

Detects (matching dev-redis SKILL.md antipattern catalog):
  [R2] SET/HSET without TTL nearby (no ex=/expire in the statement or next lines)
  [R5] KEYS command usage (blocks the single thread)
  [R5b] HGETALL / SMEMBERS on unknown-size collections (review flag)

Scans .py (redis-py style) sources.

Usage:
  python redis_check.py <py_file_or_dir> [...]
  python redis_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '# redis-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

RE_SET = re.compile(r"\.h?set\s*\(", re.I)
RE_TTL_HINT = re.compile(r"\b(ex|px|exat|keepttl)\s*=|\.expire\s*\(", re.I)
RE_KEYS = re.compile(r"\.keys\s*\(")
RE_BIGREAD = re.compile(r"\.(hgetall|smembers)\s*\(")


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    for i, line in enumerate(lines):
        if "redis-ok:" in line:
            continue
        ln = i + 1
        if RE_SET.search(line):
            # widen only while the call's parens are still open (multi-line call)
            window = line
            j = i
            while window.count("(") > window.count(")") and j + 1 < len(lines):
                j += 1
                window += "\n" + lines[j]
            # .expire() on the immediately following line also counts
            if j + 1 < len(lines) and ".expire(" in lines[j + 1]:
                window += "\n" + lines[j + 1]
            if not RE_TTL_HINT.search(window):
                findings.append(f"{label}:{ln}: [R2] SET without TTL - every cache key needs expiry "
                                "(permanent data belongs in the DB)")
        if RE_KEYS.search(line):
            findings.append(f"{label}:{ln}: [R5] KEYS command - blocks Redis; use SCAN or version-key invalidation")
        if RE_BIGREAD.search(line):
            findings.append(f"{label}:{ln}: [R5b] HGETALL/SMEMBERS - O(collection); fine if small and bounded, "
                            "split the structure if it grows")
    return findings


DEMO = '''\
r.set("user:1:profile", payload)
r.set("rank:v1:daily", data, ex=300)
stale = r.keys("user:*")
fields = r.hgetall("portfolio:1")
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python redis_check.py <py_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, _dirs, fs in os.walk(p):
                paths.extend(os.path.join(root, f) for f in fs if f.endswith(".py"))
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
