"""indirection_probe.py - over-abstraction assistant for Python files (stdlib only).

Reports (matching dev-design-patterns SKILL.md quantitative table):
  [P-DELEG] function whose body only delegates to one call (indirection layer)
  [P-ABS]   ABC/Protocol-looking class whose every method raises NotImplementedError / is ...
            (flag: does a second implementation actually exist?)

Advisory only - delegation can be a legitimate boundary (adapter/facade).
Usage:
  python indirection_probe.py <py_file_or_dir> [...]
  python indirection_probe.py            (no args: self-demo)

Exit code: always 0 (advisory).
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import ast
import os
import sys


def is_delegate_only(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    body = [s for s in fn.body if not isinstance(s, ast.Expr) or not isinstance(s.value, ast.Constant)]
    if len(body) != 1:
        return False
    stmt = body[0]
    if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Call):
        return True
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        return True
    return False


def is_abstract_stub(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    body = [s for s in fn.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    if not body:
        return True  # docstring-only / ellipsis-only
    if len(body) == 1:
        s = body[0]
        if isinstance(s, ast.Raise) and s.exc is not None:
            name = getattr(getattr(s.exc, "func", s.exc), "id", "")
            return name == "NotImplementedError"
        if isinstance(s, ast.Pass):
            return True
    return False


def scan(tree: ast.Module, label: str) -> list[str]:
    out: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_delegate_only(node):
            out.append(f"{label}:{node.lineno}: [P-DELEG] '{node.name}' only delegates - "
                       "is this layer earning its keep? (fine if it's a named boundary)")
        if isinstance(node, ast.ClassDef):
            methods = [m for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
            if methods and all(is_abstract_stub(m) for m in methods):
                out.append(f"{label}:{node.lineno}: [P-ABS] '{node.name}' is all-abstract - "
                           "does a second implementation exist? (single-impl interface = fake flexibility)")
    return out


DEMO = '''\
class SourceProvider:
    def fetch(self, code):
        raise NotImplementedError
    def auth(self):
        raise NotImplementedError

def get_candles(code):
    return repo.get_candles(code)

def normalize(t):
    t = fix_tz(t)
    return validate(t)
'''


def main(argv: list[str]) -> int:
    findings: list[str] = []
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        findings = scan(ast.parse(DEMO), "<demo>")
        for ln in findings:
            print("  " + ln)
        print("Usage: python indirection_probe.py <py_or_dir> ...")
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
                tree = ast.parse(f.read())
        except (FileNotFoundError, SyntaxError) as e:
            print(f"{path}: skipped ({e.__class__.__name__})")
            continue
        findings += scan(tree, path)
    for ln in findings:
        print(ln)
    print(f"{len(findings)} candidate(s) - advisory; boundaries can legitimately delegate")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
