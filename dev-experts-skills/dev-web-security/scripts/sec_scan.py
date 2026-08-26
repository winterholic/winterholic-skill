"""sec_scan.py - web security smell detector (stdlib only, regex heuristic).

Detects (matching dev-web-security SKILL.md antipattern catalog):
  [W1a] f-string / % / + into a SQL-looking string (injection)
  [W1b] subprocess/os.system with shell=True or string command
  [W2]  innerHTML = / dangerouslySetInnerHTML / template |safe with a variable
  [W4]  hardcoded secret literal (api_key/password/token = "...")

Scans .py / .js / .ts / .tsx / .html sources.

Usage:
  python sec_scan.py <file_or_dir> [...]
  python sec_scan.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with 'sec-ok:' comment.
Heuristic - aims at the common shapes, not a substitute for a real SAST tool.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

SQLISH = re.compile(r"(select|insert|update|delete)\s", re.I)
CHECKS = [
    ("W1a", re.compile(r"""(?:execute|executemany|query|raw)\s*\(\s*f?["'][^"']*\{""", re.I),
     "f-string/interpolation into SQL - use parameter binding (%s, [param])"),
    ("W1a", re.compile(r"""["'][^"']*(?:select|insert|update|delete)[^"']*["']\s*[+%]\s*\w""", re.I),
     "string concatenation into SQL - use parameter binding"),
    ("W1b", re.compile(r"(subprocess\.(run|call|Popen|check_output)\([^)]*shell\s*=\s*True|os\.system\s*\()"),
     "shell command with shell=True / os.system - use arg list, shell=False"),
    ("W2", re.compile(r"(\.innerHTML\s*=|dangerouslySetInnerHTML)"),
     "raw HTML injection sink - sanitize (DOMPurify) or use text binding"),
    ("W2", re.compile(r"\{\{[^}]*\|\s*safe\s*\}\}"),
     "template |safe filter - disables escaping; ensure input is sanitized"),
    ("W4", re.compile(r"""(?i)(api[_-]?key|secret|password|passwd|token)\s*[=:]\s*["'][^"']{8,}["']"""),
     "hardcoded secret literal - move to env/secret manager; rotate if committed"),
]


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()
    for code, pattern, msg in CHECKS:
        for m in pattern.finditer(text):
            ln = text.count("\n", 0, m.start()) + 1
            line = lines[ln - 1] if ln <= len(lines) else ""
            if "sec-ok:" in line:
                continue
            # W1a second pattern is broad; keep only if it really looks SQL
            findings.append(f"{label}:{ln}: [{code}] {msg}")
    return sorted(set(findings))


DEMO = '''\
cur.execute(f"SELECT * FROM users WHERE id = {uid}")
os.system("convert " + filename)
el.innerHTML = userInput;
API_KEY = "sk-live-abcd1234efgh"
safe = cur.execute("SELECT 1 WHERE x = %s", [x])  # ok
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python sec_scan.py <file_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, dirs, fs in os.walk(p):
                dirs[:] = [d for d in dirs if d != "node_modules"]
                paths.extend(os.path.join(root, f) for f in fs
                             if f.endswith((".py", ".js", ".ts", ".tsx", ".html")))
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
