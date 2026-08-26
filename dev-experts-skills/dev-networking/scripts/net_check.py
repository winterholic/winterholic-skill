"""net_check.py - network safety smell detector (stdlib only, regex heuristic).

Detects (matching dev-networking SKILL.md antipattern catalog):
  [N3]  TLS verification disabled (verify=False / rejectUnauthorized: false / InsecureSkipVerify)
  [N2]  HTTP request without a timeout (requests/httpx call lacking timeout=)
  [N3b] plaintext http:// URL literal (non-localhost)

Scans .py / .js / .ts / .go sources.

Usage:
  python net_check.py <file_or_dir> [...]
  python net_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with 'net-ok:' comment.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

RE_VERIFY_OFF = re.compile(r"(verify\s*=\s*False|rejectUnauthorized\s*:\s*false|InsecureSkipVerify\s*:\s*true)", re.I)
RE_REQUEST = re.compile(r"(requests|httpx|session|client)\.(get|post|put|delete|patch|request)\s*\(", re.I)
RE_TIMEOUT = re.compile(r"timeout\s*=", re.I)
RE_HTTP_URL = re.compile(r"""["']http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)[^"']+["']""")


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def add(ln: int, code: str, msg: str):
        if 0 < ln <= len(lines) and "net-ok:" in lines[ln - 1]:
            return
        findings.append(f"{label}:{ln}: [{code}] {msg}")

    for m in RE_VERIFY_OFF.finditer(text):
        add(text.count("\n", 0, m.start()) + 1, "N3",
            "TLS verification disabled - opens MITM; keep verify on (add CA to trust store if needed)")
    for m in RE_HTTP_URL.finditer(text):
        add(text.count("\n", 0, m.start()) + 1, "N3b",
            "plaintext http:// URL - use https (data + integrity exposed in transit)")

    # timeout: look at each request call's parenthesized args (single+multiline)
    for m in RE_REQUEST.finditer(text):
        start = m.end() - 1
        depth, j = 0, start
        while j < len(text):
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        call = text[start:j + 1]
        ln = text.count("\n", 0, m.start()) + 1
        if not RE_TIMEOUT.search(call):
            add(ln, "N2", "HTTP call without timeout - hangs forever if peer stalls; set connect/read timeout")
    return sorted(set(findings))


DEMO = '''\
r = requests.get("http://example.com/data")
s = httpx.post(url, json=body, verify=False)
ok = requests.get(url, timeout=10)  # ok
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python net_check.py <file_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, dirs, fs in os.walk(p):
                dirs[:] = [d for d in dirs if d != "node_modules"]
                paths.extend(os.path.join(root, f) for f in fs
                             if f.endswith((".py", ".js", ".ts", ".go")))
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
