"""event_check.py - event-driven smell detector (stdlib only).

Detects (matching dev-event-driven SKILL.md antipattern catalog):
  [E1] dual write: commit() closely followed by publish/emit/send (same function)
  [E4] command-shaped event class name (SendX.../NotifyX.../UpdateX...Event)

Usage:
  python event_check.py <py_file_or_dir> [...]
  python event_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '# event-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import ast
import os
import re
import sys

PUBLISH_NAMES = re.compile(r"(publish|emit|send_event|produce)", re.I)
COMMAND_PREFIX = re.compile(r"^(Send|Notify|Update|Create|Delete|Process|Do)[A-Z]\w*Event$")


def _dotted(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def scan_source(src: str, label: str) -> list[str]:
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [f"{label}:{e.lineno}: [PARSE] {e.msg}"]
    lines = src.splitlines()
    findings: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and COMMAND_PREFIX.match(node.name):
            if "event-ok:" not in lines[node.lineno - 1]:
                findings.append(f"{label}:{node.lineno}: [E4] '{node.name}' is a command in disguise - "
                                "events state facts (past tense); commands go to a known handler")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            calls = [(sub.lineno, _dotted(sub.func)) for sub in ast.walk(node)
                     if isinstance(sub, ast.Call)]
            commit_lines = [ln for ln, name in calls if name.endswith(".commit")]
            publish_lines = [(ln, name) for ln, name in calls if PUBLISH_NAMES.search(name.split(".")[-1])]
            for c_ln in commit_lines:
                for p_ln, p_name in publish_lines:
                    if 0 < p_ln - c_ln <= 5 and "event-ok:" not in lines[p_ln - 1]:
                        findings.append(
                            f"{label}:{p_ln}: [E1] '{p_name}' right after commit (line {c_ln}) - "
                            "dual write; crash between them loses the event (use outbox)")
    return sorted(set(findings))


DEMO = '''\
class SendEmailToUserEvent:
    pass

def place_order(session, broker, order):
    session.add(order)
    session.commit()
    broker.publish("order_placed", order.id)
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_source(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python event_check.py <py_or_dir> ...")
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
                src = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        for ln in scan_source(src, path):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
