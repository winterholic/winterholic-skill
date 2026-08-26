"""unit_check.py - systemd unit file smell detector (stdlib only).

Detects (matching dev-linux-ops SKILL.md antipattern catalog):
  [L1] no Restart= in [Service]                  (silent death)
  [L4] runs as root (no User=) for app services  (catalog #4)
  [L3] ExecStart not an absolute path            (catalog #3 - PATH assumption)
  [LN] network-dependent service without After=network-online.target

Usage:
  python unit_check.py <unit_file_or_dir> [...]
  python unit_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '# unit-ok: <reason>' comment in the unit file.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys


def scan_unit(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()
    body = "\n".join(l for l in lines if "unit-ok:" not in l)

    in_service = "[Service]" in body
    if not in_service:
        return []  # not a service unit (timer/socket) - out of scope

    if not re.search(r"^\s*Restart\s*=", body, re.M):
        findings.append(f"{label}:1: [L1] no Restart= - service dies silently; add Restart=on-failure")

    if not re.search(r"^\s*User\s*=", body, re.M):
        findings.append(f"{label}:1: [L4] no User= - runs as root; create a service user")

    for i, line in enumerate(lines, 1):
        if "unit-ok:" in line:
            continue
        m = re.match(r"^\s*ExecStart\s*=\s*(-?)(\S+)", line)
        if m and not m.group(2).startswith("/"):
            findings.append(
                f"{label}:{i}: [L3] ExecStart '{m.group(2)}' not absolute - cron/systemd have no shell PATH"
            )

    # network heuristic: mentions of http/api/fetch/collector in name or Exec
    looks_networky = re.search(r"(collector|api|fetch|http|bot|sync)", body, re.I)
    if looks_networky and "network-online.target" not in body:
        findings.append(
            f"{label}:1: [LN] network-looking service without After=network-online.target "
            "- may start before DNS/route is up (boot race)"
        )
    return findings


def iter_units(paths: list[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                out.extend(os.path.join(root, f) for f in files if f.endswith(".service"))
        else:
            out.append(p)
    return out


DEMO = """\
[Unit]
Description=stock collector

[Service]
ExecStart=python -m collector.run
WorkingDirectory=/srv/sample-service

[Install]
WantedBy=multi-user.target
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_unit(DEMO, "<demo.service>"):
            print("  " + ln)
        print("Usage: python unit_check.py <unit_file_or_dir> ...")
        return 0

    total = 0
    for path in iter_units(argv):
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"{path}: not found - skipped")
            continue
        for ln in scan_unit(text, path):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
