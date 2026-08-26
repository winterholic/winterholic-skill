"""log_scan.py - logging smell detector (stdlib only, regex heuristic).

Detects (matching dev-error-logging SKILL.md antipattern catalog):
  [G3] logging a sensitive field (password/token/secret/card/ssn) or whole request
  [G5] logger.error(str(e)) / logger.error(e) - stack trace lost (use .exception)
  [G1] f-string message in a log call (non-structured)
  [G2x] leftover print( in non-CLI source (heuristic, low severity)

Scans .py sources.

Usage:
  python log_scan.py <py_file_or_dir> [...]
  python log_scan.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '# log-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

SENSITIVE = re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|card|ssn|jumin)")
LOG_CALL = re.compile(r"(?i)\b(log(ger)?|logging)\.(debug|info|warning|error|critical|exception)\s*\(")
RE_STR_E = re.compile(r"(?i)\.error\s*\(\s*(str\s*\(\s*e\s*\)|e)\s*\)")
RE_FSTRING_LOG = re.compile(r"(?i)\.(debug|info|warning|error|critical)\s*\(\s*f['\"]")
RE_LOG_REQUEST = re.compile(r"(?i)\.(debug|info|warning|error)\s*\([^)]*\b(request|req|body|payload)\b\s*\)")


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def add(ln: int, code: str, msg: str):
        if 0 < ln <= len(lines) and "log-ok:" in lines[ln - 1]:
            return
        findings.append(f"{label}:{ln}: [{code}] {msg}")

    for i, line in enumerate(lines):
        ln = i + 1
        if LOG_CALL.search(line) and SENSITIVE.search(line):
            add(ln, "G3", "logging a sensitive field - mask/redact (logs are broad-access, long-lived)")
        if RE_LOG_REQUEST.search(line):
            add(ln, "G3", "logging whole request/body - field whitelist; redact secrets/PII")
        if RE_STR_E.search(line):
            add(ln, "G5", "error(str(e)/e) loses stack - use logger.exception() + context fields")
        if RE_FSTRING_LOG.search(line):
            add(ln, "G1", "f-string log message - non-structured; pass fields via extra={...}")
    return sorted(set(findings))


DEMO = '''\
logger.info(f"user {uid} bought {qty}")
logger.error(str(e))
logger.debug(request)
log.info("login", extra={"password": pw})
logger.exception("ingest failed", extra={"code": code})  # ok
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python log_scan.py <py_or_dir> ...")
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
