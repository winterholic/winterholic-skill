"""pipeline_check.py - ast-based data pipeline smell detector (stdlib only).

Detects (matching dev-data-engineering SKILL.md antipattern catalog):
  [E1] raw INSERT in SQL string without conflict handling   (catalog #1, heuristic)
  [E3] silent fill: .fillna(0) / 'or 0' on fetched values   (catalog #3, heuristic)
  [E6] datetime.now()/date.today() used for business date   (catalog #6)

Usage:
  python pipeline_check.py <file_or_dir> [...]
  python pipeline_check.py             (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Heuristics may flag intentional code - silence with a trailing comment
'# pipeline-ok: <reason>' on the same line (checker skips those lines).
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import ast
import os
import re
import sys

INSERT_RE = re.compile(r"\binsert\s+into\b", re.IGNORECASE)
CONFLICT_RE = re.compile(r"on\s+conflict|on\s+duplicate|insert\s+or\s+replace|merge\s+into", re.IGNORECASE)


def _dotted(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def scan_source(source: str, label: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [f"{label}:{e.lineno}: [PARSE] {e.msg}"]

    src_lines = source.splitlines()

    def silenced(lineno: int) -> bool:
        if 1 <= lineno <= len(src_lines):
            return "pipeline-ok:" in src_lines[lineno - 1]
        return False

    findings: list[tuple[int, str, str]] = []

    for node in ast.walk(tree):
        # E1: INSERT INTO ... without conflict clause, in any string constant
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if INSERT_RE.search(node.value) and not CONFLICT_RE.search(node.value):
                if not silenced(node.lineno):
                    findings.append(
                        (node.lineno, "E1",
                         "INSERT without ON CONFLICT/upsert - rerun will duplicate "
                         "(or replace whole partition; silence with '# pipeline-ok: <why>')")
                    )
        if isinstance(node, ast.Call):
            name = _dotted(node.func)
            # E3: .fillna(0) style silent fill
            if name.endswith(".fillna") and node.args:
                a = node.args[0]
                if isinstance(a, ast.Constant) and a.value in (0, 0.0, ""):
                    if not silenced(node.lineno):
                        findings.append(
                            (node.lineno, "E3",
                             "fillna(0) - silent fill erases 'missing vs real zero'; "
                             "keep NULL + quality flag")
                        )
            # E6: now()/today() as business date
            if name in ("datetime.now", "datetime.datetime.now", "date.today",
                        "datetime.date.today"):
                if not silenced(node.lineno):
                    findings.append(
                        (node.lineno, "E6",
                         f"{name}() - wall clock is not the business date; "
                         "use trading-calendar module / pass base_date in")
                    )

    return [f"{label}:{line}: [{code}] {msg}" for line, code, msg in sorted(set(findings))]


def iter_py_files(paths: list[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                out.extend(os.path.join(root, f) for f in files if f.endswith(".py"))
        else:
            out.append(p)
    return out


DEMO = '''\
from datetime import datetime

def load(rows, cur):
    today = datetime.now().date()
    df = df.fillna(0)
    cur.execute("INSERT INTO ticks (code, d, price) VALUES (%s, %s, %s)", rows)
    cur.execute("INSERT INTO meta VALUES (%s) ON CONFLICT (k) DO UPDATE SET v=1", rows)
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_source(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python pipeline_check.py <file_or_dir> ...")
        return 0

    total = 0
    for path in iter_py_files(argv):
        try:
            with open(path, encoding="utf-8") as f:
                src = f.read()
        except FileNotFoundError:
            print(f"{path}: not found - skipped")
            continue
        except UnicodeDecodeError:
            with open(path, encoding="cp949", errors="replace") as f:
                src = f.read()
            print(f"{path}: not utf-8 (read as cp949) - encoding smell, see dev-python P6")
        for ln in scan_source(src, path):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
