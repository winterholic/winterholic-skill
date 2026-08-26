"""ts_check.py - TypeScript source smell detector (stdlib only).

Detects (matching dev-typescript SKILL.md antipattern catalog):
  [T1] explicit ': any' annotation / 'as any'
  [T2] double assertion 'as unknown as'
  [T4] enum declaration
  [T7] @ts-ignore (any), or @ts-expect-error without reason text

Usage:
  python ts_check.py <ts_file_or_dir> [...]
  python ts_check.py             (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '// ts-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

CHECKS: list[tuple[str, re.Pattern[str], str]] = [
    ("T2", re.compile(r"\bas\s+unknown\s+as\b"),
     "double assertion - design smell; fix the type or validate at runtime"),
    ("T1", re.compile(r"\bas\s+any\b"),
     "'as any' - silences all downstream checks; use unknown + narrowing"),
    ("T1", re.compile(r":\s*any\b(?!\w)"),
     "explicit ': any' - infectious; use unknown / a real type / generics"),
    ("T4", re.compile(r"^\s*(export\s+)?(const\s+)?enum\s+\w+", re.M),
     "enum - prefer literal union ('a' | 'b') or as-const object"),
    ("T7", re.compile(r"//\s*@ts-ignore"),
     "@ts-ignore - suppresses forever; use @ts-expect-error with a reason"),
    ("T7", re.compile(r"//\s*@ts-expect-error\s*$", re.M),
     "@ts-expect-error without reason - add why on the same line"),
]


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()
    for code, pattern, msg in CHECKS:
        for m in pattern.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            line = lines[line_no - 1] if line_no <= len(lines) else ""
            if "ts-ok:" in line:
                continue
            findings.append(f"{label}:{line_no}: [{code}] {msg}")
    return sorted(set(findings))


def iter_files(paths: list[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d != "node_modules"]
                out.extend(os.path.join(root, f) for f in files if f.endswith((".ts", ".tsx")))
        else:
            out.append(p)
    return out


DEMO = """\
enum Status { Active, Inactive }
function handle(e: any) {
  const user = res.data as unknown as User;
  // @ts-ignore
  doThing(user);
  // @ts-expect-error
  legacy(user);
  // @ts-expect-error lib types miss the overload (issue #12)
  legacy2(user);
}
const ok: unknown = JSON.parse(s);  // clean
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo.ts>"):
            print("  " + ln)
        print("Usage: python ts_check.py <ts_or_dir> ...")
        return 0

    total = 0
    for path in iter_files(argv):
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"{path}: not found - skipped")
            continue
        except UnicodeDecodeError:
            with open(path, encoding="cp949", errors="replace") as f:
                text = f.read()
        for ln in scan_text(text, path):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
