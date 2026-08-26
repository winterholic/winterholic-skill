"""queue_check.py - queue consumer smell detector (stdlib only, regex heuristic).

Detects (matching dev-messaging-queue SKILL.md antipattern catalog):
  [Q2] requeue/retry in except without attempt counting (infinite poison loop shape)
  [Q3] ack/basic_ack before the processing call in the same block (at-most-once by accident)

Scans .py sources.

Usage:
  python queue_check.py <py_file_or_dir> [...]
  python queue_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '# queue-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

RE_REQUEUE = re.compile(r"except[^\n]*:\s*\n(?:\s+[^\n]*\n){0,4}?\s+\w*\.?(requeue|nack|xadd|put|publish|send)\(", re.M)
RE_ATTEMPT = re.compile(r"(attempt|retry|tries|count|max_)", re.I)
RE_ACK_FIRST = re.compile(r"\.(ack|basic_ack|xack)\s*\([^\n]*\)\s*\n(?:\s+[^\n]*\n){0,3}?\s+\w*(process|handle|do_work|consume_one)\w*\(", re.M)


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def line_of(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    def silenced(ln: int) -> bool:
        return 0 < ln <= len(lines) and "queue-ok:" in lines[ln - 1]

    for m in RE_REQUEUE.finditer(text):
        ln = line_of(m.start())
        # look around for attempt counting in a small window
        window = "\n".join(lines[max(0, ln - 4):ln + 4])
        if not RE_ATTEMPT.search(window) and not silenced(ln):
            findings.append(f"{label}:{ln}: [Q2] requeue in except without attempt count - "
                            "poison message loops forever; count retries then DLQ")
    for m in RE_ACK_FIRST.finditer(text):
        ln = line_of(m.start())
        if not silenced(ln):
            findings.append(f"{label}:{ln}: [Q3] ack before processing - crash mid-work loses the message "
                            "(at-most-once); ack after success + idempotent consumer")
    return sorted(set(findings))


DEMO = '''\
def worker(ch, msg):
    ch.basic_ack(msg.tag)
    process(msg)

def consume(q):
    try:
        handle(q.get())
    except Exception:
        q.put(msg)
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python queue_check.py <py_or_dir> ...")
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
