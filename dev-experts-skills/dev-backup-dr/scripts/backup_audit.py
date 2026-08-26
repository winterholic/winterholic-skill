"""backup_audit.py - backup strategy auditor (stdlib only).

Reads a simple backup-policy file (key: value lines or JSON) describing your
setup and flags 3-2-1 / rehearsal / verification / offsite gaps.

Policy keys (any of):
  copies: 3
  media_types: disk,cloud
  offsite: true|false
  last_restore_test: 2026-03-01   (or 'never')
  integrity_check: true|false
  immutable_copy: true|false
  monitoring: true|false

Usage:
  python backup_audit.py <policy.txt|policy.json> [...]
  python backup_audit.py            (no args: self-demo)

Exit code: 0 = all good, 1 = gaps found, 2 = usage error.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import json
import os
import sys


def parse_policy(text: str) -> dict:
    text = text.strip()
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}
    policy: dict = {}
    for line in text.splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        policy[k.strip()] = v.strip()
    return policy


def truthy(v) -> bool:
    return str(v).strip().lower() in ("true", "yes", "1", "on")


def audit(policy: dict, label: str) -> list[str]:
    findings: list[str] = []
    try:
        copies = int(policy.get("copies", 0))
    except ValueError:
        copies = 0
    media = str(policy.get("media_types", "")).replace(" ", "")
    media_count = len([m for m in media.split(",") if m])

    if copies < 3:
        findings.append(f"{label}: [B2] copies={copies} (<3) - 3-2-1 wants 3 copies")
    if media_count < 2:
        findings.append(f"{label}: [B2] media_types count={media_count} (<2) - 3-2-1 wants 2 media")
    if not truthy(policy.get("offsite")):
        findings.append(f"{label}: [B2] offsite=false - a fire/theft/ransomware takes one site whole")
    lrt = str(policy.get("last_restore_test", "never")).lower()
    if lrt in ("never", "", "none"):
        findings.append(f"{label}: [B1] no restore rehearsal - an unrestored backup is a belief (GitLab 2017)")
    if not truthy(policy.get("integrity_check")):
        findings.append(f"{label}: [B4] integrity_check=false - 'backup succeeded' != restorable")
    if not truthy(policy.get("immutable_copy")):
        findings.append(f"{label}: [B5] no immutable/offline copy - ransomware encrypts online backups too")
    if not truthy(policy.get("monitoring")):
        findings.append(f"{label}: [B6] monitoring=false - silent backup failure goes unnoticed for weeks")
    return findings


DEMO = """\
copies: 2
media_types: disk
offsite: false
last_restore_test: never
integrity_check: false
immutable_copy: false
monitoring: false
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no policy file) - auditing built-in sample (a typical weak setup):")
        for ln in audit(parse_policy(DEMO), "<demo>"):
            print("  " + ln)
        print("Usage: python backup_audit.py <policy.txt|policy.json> ...")
        return 0

    total = 0
    for path in argv:
        try:
            with open(path, encoding="utf-8") as f:
                policy = parse_policy(f.read())
        except FileNotFoundError:
            print(f"{path}: not found - skipped")
            continue
        for ln in audit(policy, path):
            print(ln)
            total += 1
    print(f"total: {total} gap(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
