"""auth_scan.py - auth implementation smell detector (stdlib only, regex heuristic).

Detects (matching dev-auth SKILL.md antipattern catalog):
  [A1] weak hash on a password (md5/sha1/sha256 applied to password-like var)
  [A6] token/jwt stored in localStorage / sessionStorage
  [A2] long JWT expiry (expiresIn/exp days or hours large)
  [A1b] non-constant-time secret compare (token/secret/key == ...)

Scans .py / .js / .ts / .tsx sources.

Usage:
  python auth_scan.py <file_or_dir> [...]
  python auth_scan.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with 'auth-ok:' comment.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

CHECKS = [
    ("A1", re.compile(r"(?i)(md5|sha1|sha256|sha224)\s*\([^)]*(password|passwd|pwd)"),
     "fast hash on a password - use argon2id/bcrypt (fast hashes are GPU-crackable)"),
    ("A6", re.compile(r"(localStorage|sessionStorage)\.(setItem|getItem)\s*\(\s*['\"][^'\"]*(token|jwt|auth)",
                      re.I),
     "token in localStorage/sessionStorage - XSS-stealable; prefer memory or HttpOnly cookie"),
    ("A2", re.compile(r"(?i)(expiresIn|exp)\s*[:=]\s*['\"]?\s*(\d+)\s*(d|day|days|h|hour|hours)"),
     "long-lived token - access tokens should be minutes; use refresh rotation"),
    ("A1b", re.compile(r"(?i)\b\w*(token|secret|passwd|password|api[_-]?key|signature)\w*\s*==\s*\w"),
     "non-constant-time compare on a secret - timing leak; use hmac.compare_digest"),
]


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()
    for code, pattern, msg in CHECKS:
        for m in pattern.finditer(text):
            ln = text.count("\n", 0, m.start()) + 1
            line = lines[ln - 1] if ln <= len(lines) else ""
            if "auth-ok:" in line:
                continue
            # A2: only flag if value looks large-ish (hours>=1 / any days)
            if code == "A2":
                num, unit = m.group(2), m.group(3).lower()
                if unit.startswith("h") and int(num) < 1:
                    continue
            findings.append(f"{label}:{ln}: [{code}] {msg}")
    return sorted(set(findings))


DEMO = '''\
hashed = sha256(password.encode()).hexdigest()
localStorage.setItem("auth_token", jwt);
const token = jwt.sign(payload, secret, { expiresIn: "7d" });
if (request_token == stored_token):
    grant()
ok = hmac.compare_digest(a, b)  # ok
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python auth_scan.py <file_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, dirs, fs in os.walk(p):
                dirs[:] = [d for d in dirs if d != "node_modules"]
                paths.extend(os.path.join(root, f) for f in fs
                             if f.endswith((".py", ".js", ".ts", ".tsx")))
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
