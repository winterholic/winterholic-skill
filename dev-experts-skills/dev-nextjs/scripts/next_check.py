"""next_check.py - Next.js App Router smell detector (stdlib only).

Detects (matching dev-nextjs SKILL.md antipattern catalog):
  [N1] 'use client' in route segment files (page/layout/template)
  [N2] non-NEXT_PUBLIC env accessed in a client file ('use client' present)
  [N2b] NEXT_PUBLIC_ name that looks secret (KEY/SECRET/TOKEN)
  [N3] suppressHydrationWarning usage (flag for review)

Usage:
  python next_check.py <app_dir_or_file> [...]
  python next_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '// next-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

ROUTE_FILES = {"page.tsx", "page.jsx", "layout.tsx", "layout.jsx", "template.tsx", "template.jsx"}
RE_USE_CLIENT = re.compile(r"^\s*['\"]use client['\"]", re.M)
RE_ENV = re.compile(r"process\.env\.([A-Z0-9_]+)")
RE_SUPPRESS = re.compile(r"suppressHydrationWarning")
SECRETISH = re.compile(r"(KEY|SECRET|TOKEN|PASSWORD|PRIVATE)", re.I)


def scan_text(text: str, label: str, fname: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def line_of(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    def silenced(ln: int) -> bool:
        return 0 < ln <= len(lines) and "next-ok:" in lines[ln - 1]

    is_client = bool(RE_USE_CLIENT.search(text))

    if fname in ROUTE_FILES and is_client:
        findings.append(f"{label}:1: [N1] 'use client' in route file '{fname}' - "
                        "whole subtree goes client; move interactivity to leaf components")

    for m in RE_ENV.finditer(text):
        name = m.group(1)
        ln = line_of(m.start())
        if silenced(ln):
            continue
        if is_client and not name.startswith("NEXT_PUBLIC_") and name not in ("NODE_ENV",):
            findings.append(f"{label}:{ln}: [N2] env '{name}' in client file - "
                            "undefined in browser; if truly public use NEXT_PUBLIC_, else move server-side")
        if name.startswith("NEXT_PUBLIC_") and SECRETISH.search(name[12:]):
            findings.append(f"{label}:{ln}: [N2b] '{name}' - NEXT_PUBLIC_ means shipped to browser; "
                            "secrets must not carry this prefix")

    for m in RE_SUPPRESS.finditer(text):
        ln = line_of(m.start())
        if not silenced(ln):
            findings.append(f"{label}:{ln}: [N3] suppressHydrationWarning - "
                            "verify mismatch is intentional (time/locale), not a bug being hidden")
    return sorted(set(findings))


def iter_files(paths: list[str]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in ("node_modules", ".next")]
                for f in files:
                    if f.endswith((".tsx", ".jsx", ".ts", ".js")):
                        out.append((os.path.join(root, f), f))
        else:
            out.append((p, os.path.basename(p)))
    return out


DEMO = """\
'use client'
export default function Page() {
  const key = process.env.API_SECRET;
  const pub = process.env.NEXT_PUBLIC_API_TOKEN;
  return <time suppressHydrationWarning>{new Date().toLocaleString()}</time>;
}
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (scanning built-in sample as page.tsx):")
        for ln in scan_text(DEMO, "<demo/page.tsx>", "page.tsx"):
            print("  " + ln)
        print("Usage: python next_check.py <app_dir> ...")
        return 0

    total = 0
    for path, fname in iter_files(argv):
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"{path}: not found - skipped")
            continue
        except UnicodeDecodeError:
            with open(path, encoding="cp949", errors="replace") as f:
                text = f.read()
        for ln in scan_text(text, path, fname):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
