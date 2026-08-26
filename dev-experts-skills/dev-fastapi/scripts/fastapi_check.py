"""fastapi_check.py - ast-based FastAPI anti-pattern detector (stdlib only).

Detects (matching dev-fastapi SKILL.md antipattern catalog):
  [F1] blocking call inside `async def` endpoint     (catalog #1)
  [F2] route returns value but no response_model=    (catalog #2, heuristic)
  [F6] deprecated @app.on_event                      (catalog #6)
  [F7] CORS allow_origins=['*'] with credentials     (catalog #7)

Usage:
  python fastapi_check.py <file_or_dir> [...]
  python fastapi_check.py              (no args: self-demo on built-in sample)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
F2 is a heuristic (no type inference) - silence per-route by adding
response_model=None explicitly, which states the intent.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import ast
import os
import sys

# Same high-confidence blocking roots as dev-python pitfall_scan.
BLOCKING_ROOTS = {"requests", "urllib", "subprocess", "socket"}
BLOCKING_EXACT = {"time.sleep", "input"}
ROUTE_METHODS = {"get", "post", "put", "delete", "patch", "head", "options"}


def _dotted(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def _route_decorator(dec: ast.expr) -> ast.Call | None:
    """Return the Call node if decorator looks like @app.get(...) / @router.post(...)."""
    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
        if dec.func.attr in ROUTE_METHODS:
            return dec
    return None


class FastapiVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.findings: list[tuple[int, str, str]] = []

    def _check_endpoint(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        route = None
        for dec in node.decorator_list:
            # F6: @app.on_event("startup"/"shutdown")
            if isinstance(dec, ast.Call) and _dotted(dec.func).endswith(".on_event"):
                self.findings.append((dec.lineno, "F6", "@on_event is deprecated - use lifespan context"))
            r = _route_decorator(dec)
            if r is not None:
                route = r
        if route is None:
            return

        # F2: returns a value but decorator has no response_model kwarg (heuristic)
        has_rm = any(kw.arg == "response_model" for kw in route.keywords)
        returns_value = any(
            isinstance(s, ast.Return) and s.value is not None for s in ast.walk(node)
        )
        if returns_value and not has_rm:
            self.findings.append(
                (node.lineno, "F2",
                 f"route '{node.name}' returns value without response_model= "
                 "(field-leak risk; add model or response_model=None to state intent)")
            )

        # F1: blocking calls inside async endpoint
        if isinstance(node, ast.AsyncFunctionDef):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    name = _dotted(sub.func)
                    if name in BLOCKING_EXACT or name.split(".", 1)[0] in BLOCKING_ROOTS:
                        self.findings.append(
                            (sub.lineno, "F1",
                             f"blocking call '{name}' in async endpoint '{node.name}' - "
                             "use def (threadpool) or an async client")
                        )

    visit_FunctionDef = _check_endpoint  # type: ignore[assignment]
    visit_AsyncFunctionDef = _check_endpoint  # type: ignore[assignment]

    # F7: add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)
    def visit_Call(self, node: ast.Call) -> None:
        if _dotted(node.func).endswith(".add_middleware"):
            kw = {k.arg: k.value for k in node.keywords if k.arg}
            origins = kw.get("allow_origins")
            creds = kw.get("allow_credentials")
            wildcard = isinstance(origins, (ast.List, ast.Tuple)) and any(
                isinstance(e, ast.Constant) and e.value == "*" for e in origins.elts
            )
            creds_true = isinstance(creds, ast.Constant) and creds.value is True
            if wildcard and creds_true:
                self.findings.append(
                    (node.lineno, "F7",
                     "CORS wildcard origins with allow_credentials=True - "
                     "browsers reject this combo; list origins explicitly")
                )
        self.generic_visit(node)


def scan_source(source: str, label: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [f"{label}:{e.lineno}: [PARSE] {e.msg}"]
    v = FastapiVisitor()
    # NodeVisitor with overridden visit_* must recurse manually for nested defs
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            v._check_endpoint(node)
        elif isinstance(node, ast.Call):
            v.visit_Call(node)
    # de-dup (walk + generic_visit can hit a Call twice)
    uniq = sorted(set(v.findings))
    return [f"{label}:{line}: [{code}] {msg}" for line, code, msg in uniq]


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
import time, requests
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True)

@app.on_event("startup")
def init():
    pass

@app.get("/users/{uid}")
async def get_user(uid: int):
    r = requests.get(f"http://internal/users/{uid}")
    time.sleep(0.1)
    return r.json()
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_source(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python fastapi_check.py <file_or_dir> ...")
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
