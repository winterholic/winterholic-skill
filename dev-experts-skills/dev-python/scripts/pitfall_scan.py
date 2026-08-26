"""pitfall_scan.py - ast-based Python anti-pattern detector (stdlib only).

Detects (matching dev-python SKILL.md antipattern catalog):
  [P1] mutable default argument        (catalog #1)
  [P3] bare except / silent swallow    (catalog #3)
  [P2] blocking call inside async def  (catalog #2)
  [P6] open() without encoding=        (catalog #6, Windows cp949 trap)

Usage:
  python pitfall_scan.py <file.py> [more.py ...]
  python pitfall_scan.py            (no args: runs self-demo on built-in sample)

Exit code: 0 = clean, 1 = findings, 2 = usage/parse error.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import ast
import sys

# Blocking calls that freeze the event loop when used inside `async def`.
# Names are matched on the dotted call root (requests.get -> "requests").
# Kept minimal on purpose: high-confidence offenders only, to avoid noise.
BLOCKING_ROOTS = {"requests", "urllib", "subprocess", "socket"}
BLOCKING_EXACT = {"time.sleep", "input"}

MUTABLE_DEFAULT_NODES = (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)


def _dotted(node: ast.AST) -> str:
    """Best-effort dotted name of a call target ('time.sleep', 'requests.get')."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


class PitfallVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.findings: list[tuple[int, str, str]] = []  # (line, code, message)
        self._async_depth = 0

    # --- P1: mutable defaults -------------------------------------------
    def _check_defaults(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for default in list(node.args.defaults) + [d for d in node.args.kw_defaults if d]:
            if isinstance(default, MUTABLE_DEFAULT_NODES):
                self.findings.append(
                    (default.lineno, "P1",
                     f"mutable default in '{node.name}()' - use None + create inside")
                )
            if isinstance(default, ast.Call):
                self.findings.append(
                    (default.lineno, "P1",
                     f"call as default in '{node.name}()' - evaluated once at def time")
                )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_defaults(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_defaults(node)
        self._async_depth += 1
        self.generic_visit(node)
        self._async_depth -= 1

    # --- P3: bare/silent except -----------------------------------------
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        is_bare = node.type is None
        is_broad = isinstance(node.type, ast.Name) and node.type.id in ("Exception", "BaseException")
        body_is_silent = all(isinstance(s, (ast.Pass, ast.Continue)) for s in node.body)
        if is_bare:
            self.findings.append((node.lineno, "P3", "bare 'except:' - swallows SystemExit/KeyboardInterrupt too"))
        elif is_broad and body_is_silent:
            self.findings.append((node.lineno, "P3", "broad except with silent body - log or re-raise"))
        self.generic_visit(node)

    # --- P2 + P6: calls --------------------------------------------------
    def visit_Call(self, node: ast.Call) -> None:
        name = _dotted(node.func)
        root = name.split(".", 1)[0]
        if self._async_depth > 0 and (name in BLOCKING_EXACT or root in BLOCKING_ROOTS):
            self.findings.append(
                (node.lineno, "P2", f"blocking call '{name}' inside async def - freezes event loop")
            )
        if name == "open":
            has_encoding = any(kw.arg == "encoding" for kw in node.keywords)
            # binary mode does not take encoding; detect via positional/keyword mode containing 'b'
            mode = ""
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                mode = str(node.args[1].value)
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    mode = str(kw.value.value)
            if not has_encoding and "b" not in mode:
                self.findings.append(
                    (node.lineno, "P6", "open() without encoding= - cp949 on Windows, add encoding='utf-8'")
                )
        self.generic_visit(node)


def scan_source(source: str, label: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [f"{label}:{e.lineno}: [PARSE] {e.msg}"]
    v = PitfallVisitor()
    v.visit(tree)
    return [f"{label}:{line}: [{code}] {msg}" for line, code, msg in sorted(v.findings)]


DEMO = '''\
import time, requests

def add(item, bucket=[]):
    bucket.append(item)
    return bucket

async def fetch(url):
    r = requests.get(url)
    time.sleep(1)
    return r

def load(path):
    try:
        return open(path).read()
    except:
        pass
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        lines = scan_source(DEMO, "<demo>")
        for ln in lines:
            print("  " + ln)
        print(f"{len(lines)} finding(s). Usage: python pitfall_scan.py <file.py> ...")
        return 0

    total = 0
    for path in argv:
        try:
            with open(path, encoding="utf-8") as f:
                src = f.read()
        except FileNotFoundError:
            print(f"{path}: not found - skipped")
            continue
        except UnicodeDecodeError:
            # fall back so the scan still runs on legacy-encoded files
            with open(path, encoding="cp949", errors="replace") as f:
                src = f.read()
            print(f"{path}: not utf-8 (read as cp949) - that itself is a P6 smell")
        lines = scan_source(src, path)
        for ln in lines:
            print(ln)
        total += len(lines)
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
