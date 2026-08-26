"""test_smells.py - ast-based test smell detector (stdlib only).

Detects (matching dev-testing SKILL.md antipattern catalog):
  [T4a] test function without any assert            (catalog #4)
  [T4b] duplicate test function name in same module (catalog #4 - silent shadowing)
  [T3]  time.sleep() inside a test                  (catalog #3 - flaky source)

Usage:
  python test_smells.py <file_or_dir> [...]
  python test_smells.py              (no args: self-demo on built-in sample)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Notes:
  - 'assert' includes pytest.raises / unittest self.assert* / pytest.approx use.
  - Only functions named test_* in files named test_*.py / *_test.py are checked.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import ast
import os
import sys


def _dotted(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def _has_assertion(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for node in ast.walk(fn):
        if isinstance(node, ast.Assert):
            return True
        if isinstance(node, ast.Call):
            name = _dotted(node.func)
            # pytest.raises / pytest.warns count as the test's assertion
            if name in ("pytest.raises", "pytest.warns", "pytest.deprecated_call"):
                return True
            # unittest style: self.assertEqual etc.
            if ".assert" in "." + name.lower():
                return True
        if isinstance(node, ast.With):
            for item in node.items:
                if isinstance(item.context_expr, ast.Call) and _dotted(
                    item.context_expr.func
                ) in ("pytest.raises", "pytest.warns"):
                    return True
    return False


def scan_source(source: str, label: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [f"{label}:{e.lineno}: [PARSE] {e.msg}"]

    findings: list[tuple[int, str, str]] = []
    seen: dict[str, int] = {}  # test name -> first def line (per module scope walk)

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test"):
            continue

        if node.name in seen:
            findings.append(
                (node.lineno, "T4b",
                 f"duplicate test name '{node.name}' (first at line {seen[node.name]}) - "
                 "later def silently shadows earlier one")
            )
        else:
            seen[node.name] = node.lineno

        if not _has_assertion(node):
            findings.append(
                (node.lineno, "T4a", f"test '{node.name}' has no assertion - always passes")
            )

        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and _dotted(sub.func) == "time.sleep":
                findings.append(
                    (sub.lineno, "T3",
                     f"time.sleep in test '{node.name}' - flaky source; poll a condition "
                     "with timeout or inject a clock")
                )

    return [f"{label}:{line}: [{code}] {msg}" for line, code, msg in sorted(set(findings))]


def iter_test_files(paths: list[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for f in files:
                    if f.endswith(".py") and (f.startswith("test_") or f.endswith("_test.py")):
                        out.append(os.path.join(root, f))
        else:
            out.append(p)
    return out


DEMO = '''\
import time

def test_create_user(client):
    client.post("/users", json={"name": "a"})   # no assert!

def test_fetch_retries():
    time.sleep(2)
    assert fetch() is not None

def test_create_user(client):                    # duplicate: shadows line 3
    r = client.post("/users", json={"name": "a"})
    assert r.status_code == 201
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_source(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python test_smells.py <file_or_dir> ...")
        return 0

    total = 0
    for path in iter_test_files(argv):
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
