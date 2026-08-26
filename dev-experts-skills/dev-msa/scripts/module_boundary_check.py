"""module_boundary_check.py - package boundary import checker (stdlib only).

Rule (dev-msa SKILL.md quantitative table): packages talk through their public
interface (the package __init__ or a designated api module) - importing another
top-level package's INTERNAL module directly couples to its guts.

  [M1] from <other_pkg>.<internal> import ...   (crosses into internals)
  ok:  from <other_pkg> import ...              (public interface)
  ok:  from <other_pkg>.api import ...          ('api' treated as public)

Usage:
  python module_boundary_check.py <src_root> [...]
  python module_boundary_check.py          (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '# boundary-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import ast
import os
import sys

PUBLIC_SUBMODULES = {"api", "models", "types"}  # conventionally shared surfaces


def top_packages(root: str) -> set[str]:
    out = set()
    for name in os.listdir(root):
        p = os.path.join(root, name)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "__init__.py")):
            out.add(name)
    return out


def scan_file(path: str, my_pkg: str, packages: set[str], src_lines: list[str]) -> list[str]:
    try:
        tree = ast.parse("\n".join(src_lines))
    except SyntaxError as e:
        return [f"{path}:{e.lineno}: [PARSE] {e.msg}"]
    findings = []
    for node in ast.walk(tree):
        mod = None
        if isinstance(node, ast.ImportFrom) and node.module:
            mod = node.module
        elif isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if parts[0] in packages and parts[0] != my_pkg and len(parts) >= 2 \
                        and parts[1] not in PUBLIC_SUBMODULES:
                    if "boundary-ok:" not in src_lines[node.lineno - 1]:
                        findings.append(
                            f"{path}:{node.lineno}: [M1] imports internals of '{parts[0]}' "
                            f"({alias.name}) - go through its public interface")
            continue
        if mod:
            parts = mod.split(".")
            if parts[0] in packages and parts[0] != my_pkg and len(parts) >= 2 \
                    and parts[1] not in PUBLIC_SUBMODULES:
                if "boundary-ok:" not in src_lines[node.lineno - 1]:
                    findings.append(
                        f"{path}:{node.lineno}: [M1] imports internals of '{parts[0]}' "
                        f"({mod}) - go through its public interface")
    return findings


def run(root: str) -> list[str]:
    packages = top_packages(root)
    findings: list[str] = []
    for pkg in packages:
        for dirpath, _dirs, files in os.walk(os.path.join(root, pkg)):
            for f in files:
                if not f.endswith(".py"):
                    continue
                path = os.path.join(dirpath, f)
                try:
                    with open(path, encoding="utf-8") as fh:
                        lines = fh.read().splitlines()
                except (OSError, UnicodeDecodeError):
                    continue
                findings += scan_file(path, pkg, packages, lines)
    return findings


def demo() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "collector"))
        os.makedirs(os.path.join(td, "api"))
        open(os.path.join(td, "collector", "__init__.py"), "w").close()
        open(os.path.join(td, "collector", "clean.py"), "w").close()
        open(os.path.join(td, "api", "__init__.py"), "w").close()
        with open(os.path.join(td, "api", "routes.py"), "w", encoding="utf-8") as f:
            f.write("from collector.clean import normalize_tick\n"   # M1
                    "from collector import get_candles\n")           # ok
        print("demo mode - two packages, one internal import:")
        for ln in run(td):
            print("  " + ln.replace(td, "<demo>"))


def main(argv: list[str]) -> int:
    if not argv:
        demo()
        print("Usage: python module_boundary_check.py <src_root> ...")
        return 0
    total = 0
    for root in argv:
        if not os.path.isdir(root):
            print(f"{root}: not a directory - skipped")
            continue
        for ln in run(root):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
