"""dns_check.py - DNS/email-auth zone smell detector (stdlib only, regex heuristic).

Detects (matching dev-dns-domain-email SKILL.md antipattern catalog):
  [D4a] CNAME on the root/apex (conflicts with MX/NS - RFC violation)
  [D4b] MX record pointing at an IP literal (must be a hostname)
  [D5]  DMARC policy p=reject/quarantine without staging from p=none (flag for review)
  [D2]  missing email auth: has MX but no SPF / no DMARC record in the zone

Input: a zone-file-ish text (one record per line: name TTL? IN TYPE value).

Usage:
  python dns_check.py <zonefile> [...]
  python dns_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def scan_zone(text: str, label: str) -> list[str]:
    findings: list[str] = []
    has_mx = has_spf = has_dmarc = False
    lines = text.splitlines()

    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith(";") or line.startswith("#"):
            continue
        if "dns-ok:" in raw:
            continue
        parts = line.split()
        # find TYPE token (A/AAAA/CNAME/MX/TXT/NS) and the rest
        types = {"A", "AAAA", "CNAME", "MX", "TXT", "NS"}
        tix = next((j for j, p in enumerate(parts) if p.upper() in types), None)
        if tix is None:
            continue
        name = parts[0]
        rtype = parts[tix].upper()
        value = " ".join(parts[tix + 1:])

        is_root = name in ("@", "") or name.rstrip(".").count(".") == 1 and not name.startswith("www")

        if rtype == "CNAME" and (name in ("@",) or name.rstrip(".") and name.count(".") <= 1 and name in ("@", "")):
            findings.append(f"{label}:{i}: [D4a] CNAME on apex/root '{name}' - violates RFC; conflicts with MX/NS; use A/ALIAS")
        if rtype == "CNAME" and name == "@":
            pass
        if rtype == "MX":
            has_mx = True
            target = value.split()[-1] if value else ""
            if IP_RE.match(target):
                findings.append(f"{label}:{i}: [D4b] MX points at IP '{target}' - MX must name a host (with its own A record)")
        if rtype == "TXT":
            v = value.lower()
            if "v=spf1" in v:
                has_spf = True
            if "v=dmarc1" in v:
                has_dmarc = True
                if ("p=reject" in v or "p=quarantine" in v):
                    findings.append(f"{label}:{i}: [D5] DMARC {('p=reject' if 'p=reject' in v else 'p=quarantine')} - "
                                    "stage from p=none first (monitor reports, align senders), then tighten")

    if has_mx and not has_spf:
        findings.append(f"{label}: [D2] has MX but no SPF (v=spf1) - mail will be flagged/spam")
    if has_mx and not has_dmarc:
        findings.append(f"{label}: [D2] has MX but no DMARC (v=DMARC1) - add p=none + rua to start")
    return findings


DEMO = """\
@        3600 IN A     203.0.113.10
@        3600 IN CNAME example-cdn.net.
www      3600 IN CNAME @
@        3600 IN MX 10 192.0.2.5
mail     3600 IN A     203.0.113.11
_dmarc   3600 IN TXT   "v=DMARC1; p=reject; rua=mailto:d@example.com"
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no zonefile) - scanning built-in sample:")
        for ln in scan_zone(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python dns_check.py <zonefile> ...")
        return 0

    total = 0
    for path in argv:
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"{path}: not found - skipped")
            continue
        for ln in scan_zone(text, path):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
