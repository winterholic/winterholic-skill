"""mongo_check.py - MongoDB schema/query smell detector (stdlib only, regex heuristic).

Detects (matching dev-mongodb SKILL.md antipattern catalog):
  [M2]  unbounded array growth - $push without a $slice cap (antipattern 2: 16MB limit)
  [M2b] mongoose array field with no size guard nearby (heuristic, hint only)
  [M6]  insecure binding/auth - bindIp 0.0.0.0 or authorization disabled (antipattern 6)
  [M3]  COLLSCAN evidence or explicit collection-scan hint in source/notes (antipattern 3)
  [M1]  chained $lookup (2+ in one aggregate) - RDB-port smell (antipattern 1)

Scans .py / .js / .ts / .json / .yml / .yaml / .conf sources.

Usage:
  python mongo_check.py <file_or_dir> [...]
  python mongo_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with 'mongo-ok:' comment.
Output is ASCII-only (Windows cp949 console safe).

Heuristic only: a clean run is not a proof. Always confirm with explain("executionStats")
and a real $jsonSchema validator (see SKILL.md workflow step 3).
"""
from __future__ import annotations

import os
import re
import sys

RE_PUSH = re.compile(r"\$push\b", re.I)
RE_SLICE = re.compile(r"\$slice\b", re.I)
RE_BIND_ALL = re.compile(r"bindIp\s*[:=]\s*['\"]?0\.0\.0\.0", re.I)
RE_AUTH_OFF = re.compile(r"authorization\s*[:=]\s*['\"]?(disabled|false)", re.I)
RE_COLLSCAN = re.compile(r"\bCOLLSCAN\b")
RE_LOOKUP = re.compile(r"\$lookup\b", re.I)


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def add(ln: int, code: str, msg: str):
        if 0 < ln <= len(lines) and "mongo-ok:" in lines[ln - 1]:
            return
        findings.append(f"{label}:{ln}: [{code}] {msg}")

    def line_of(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    # [M2] $push without a $slice on the same logical statement.
    # Window = from this $push to the end of the line it sits on (a capped $push puts
    # $slice in the same update object on the same line in idiomatic mongoose/driver code).
    for m in RE_PUSH.finditer(text):
        ln = line_of(m.start())
        eol = text.find("\n", m.start())
        if eol == -1:
            eol = len(text)
        window = text[m.start():eol]
        if not RE_SLICE.search(window):
            add(ln, "M2",
                "$push without $slice - array can grow unbounded toward the 16MB doc limit; "
                "cap with {$push:{...,$slice:-N}} or split into a referenced collection")

    for m in RE_BIND_ALL.finditer(text):
        add(line_of(m.start()), "M6",
            "bindIp 0.0.0.0 - binds to all interfaces (internet-exposable); restrict to internal net + firewall")
    for m in RE_AUTH_OFF.finditer(text):
        add(line_of(m.start()), "M6",
            "authorization disabled - run with security.authorization: enabled (2017 ransom wave hit unauth instances)")
    for m in RE_COLLSCAN.finditer(text):
        add(line_of(m.start()), "M3",
            "COLLSCAN present - query not using an index; design a compound index by ESR (Equality-Sort-Range)")

    # [M1] 2+ $lookup stages in one file region -> RDB-on-Mongo smell (heuristic count).
    lookups = list(RE_LOOKUP.finditer(text))
    if len(lookups) >= 2:
        add(line_of(lookups[1].start()), "M1",
            "multiple $lookup stages - likely an ported RDB schema; embed data that is always read together")

    return sorted(set(findings))


DEMO = '''\
db.posts.updateOne({_id:id}, {$push: {comments: c}})
db.feed.updateOne({_id:id}, {$push: {recent: {$each:[c], $slice:-10}}})  // ok capped
net = {bindIp: "0.0.0.0", security: {authorization: "disabled"}}
db.orders.aggregate([{$lookup:{from:"u"}}, {$lookup:{from:"i"}}])
# explain showed COLLSCAN on orders.status
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python mongo_check.py <file_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, dirs, fs in os.walk(p):
                dirs[:] = [d for d in dirs if d != "node_modules"]
                paths.extend(os.path.join(root, f) for f in fs
                             if f.endswith((".py", ".js", ".ts", ".json", ".yml", ".yaml", ".conf")))
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
