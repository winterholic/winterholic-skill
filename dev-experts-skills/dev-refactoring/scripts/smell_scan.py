"""smell_scan.py - quantitative code smell assistant for Python files (stdlib only).

Reports (matching dev-refactoring SKILL.md quantitative table):
  [S-LONG]  function over 30 lines        (extract candidate - judgment still required)
  [S-PARAM] function with 4+ parameters   (parameter object candidate)
  [S-DUP]   duplicated 5-line blocks across the scanned set (3+ occurrences -> rule of three)

This is an assistant, not a verdict: cohesive long functions can be fine.
Usage:
  python smell_scan.py <py_file_or_dir> [...]
  python smell_scan.py            (no args: self-demo)

Exit code: always 0 (advisory tool - smells are candidates, not violations).
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import ast
import os
import sys
from collections import defaultdict

LONG_FUNC = 30   # lines - SKILL.md quantitative starting point
MAX_PARAMS = 4   # params - long parameter list smell
DUP_WINDOW = 5   # lines per duplicate block
DUP_MIN = 3      # rule of three


def scan_functions(tree: ast.Module, label: str) -> list[str]:
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            length = (node.end_lineno or node.lineno) - node.lineno + 1
            if length > LONG_FUNC:
                out.append(f"{label}:{node.lineno}: [S-LONG] '{node.name}' is {length} lines "
                           f"(> {LONG_FUNC}) - extract named chunks?")
            params = [a for a in node.args.args if a.arg not in ("self", "cls")]
            params += node.args.kwonlyargs
            if len(params) >= MAX_PARAMS:
                out.append(f"{label}:{node.lineno}: [S-PARAM] '{node.name}' takes {len(params)} params "
                           "- parameter object candidate")
    return out


def normalized_lines(text: str) -> list[str]:
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


def find_duplicates(files: dict[str, list[str]]) -> list[str]:
    blocks: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for label, lines in files.items():
        for i in range(len(lines) - DUP_WINDOW + 1):
            key = tuple(lines[i:i + DUP_WINDOW])
            blocks[key].append(f"{label}:{i + 1}")
    out = []
    for key, locs in blocks.items():
        if len(locs) >= DUP_MIN:
            out.append(f"[S-DUP] {DUP_WINDOW}-line block x{len(locs)} ({', '.join(locs[:4])}...) "
                       f"- rule of three met: '{key[0][:40]}...'")
    return out


DEMO = '''\
def load(path, code, start, end, retries, verbose):
    pass

def a():
    x = 1
    y = 2
    z = x + y
    w = z * 2
    return w

def b():
    x = 1
    y = 2
    z = x + y
    w = z * 2
    return w

def c():
    x = 1
    y = 2
    z = x + y
    w = z * 2
    return w
'''


def main(argv: list[str]) -> int:
    files: dict[str, list[str]] = {}
    findings: list[str] = []

    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        tree = ast.parse(DEMO)
        findings += scan_functions(tree, "<demo>")
        files["<demo>"] = normalized_lines(DEMO)
        findings += find_duplicates(files)
        for ln in findings:
            print("  " + ln)
        print("Usage: python smell_scan.py <py_or_dir> ...")
        return 0

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
            tree = ast.parse(text)
        except (FileNotFoundError, SyntaxError) as e:
            print(f"{path}: skipped ({e.__class__.__name__})")
            continue
        findings += scan_functions(tree, path)
        files[path] = normalized_lines(text)
    findings += find_duplicates(files)
    for ln in findings:
        print(ln)
    print(f"{len(findings)} candidate(s) - advisory only, judge cohesion before extracting")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
