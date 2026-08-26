"""dependency_direction.py - inner-layer purity checker (stdlib only).

Rule (dev-clean-architecture SKILL.md): the domain package imports only the
standard library and itself - never adapters/frameworks.

  [A1] domain file imports an adapter/outer package
  [A2] domain file imports a known framework (fastapi/sqlalchemy/requests/...)

Usage:
  python dependency_direction.py <src_root> [--domain domain]
  python dependency_direction.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '# arch-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import ast
import os
import sys

FRAMEWORKS = {"fastapi", "sqlalchemy", "requests", "httpx", "django", "flask",
              "psycopg", "psycopg2", "redis", "boto3", "pydantic", "starlette",
              "aiohttp", "celery", "kafka"}
STDLIB_HINT = getattr(sys, "stdlib_module_names", frozenset())


def scan_domain_file(path: str, domain_pkg: str, sibling_pkgs: set[str]) -> list[str]:
    try:
        with open(path, encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src)
    except (OSError, SyntaxError) as e:
        return [f"{path}: skipped ({e.__class__.__name__})"]
    lines = src.splitlines()
    findings = []
    for node in ast.walk(tree):
        roots: list[tuple[int, str]] = []
        if isinstance(node, ast.Import):
            roots = [(node.lineno, a.name.split(".")[0]) for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            roots = [(node.lineno, node.module.split(".")[0])]
        for lineno, root in roots:
            if "arch-ok:" in lines[lineno - 1]:
                continue
            if root == domain_pkg:
                continue
            if root in FRAMEWORKS:
                findings.append(f"{path}:{lineno}: [A2] domain imports framework '{root}' - "
                                "policy must not know the delivery mechanism")
            elif root in sibling_pkgs:
                findings.append(f"{path}:{lineno}: [A1] domain imports outer package '{root}' - "
                                "dependencies point inward only")
            elif STDLIB_HINT and root not in STDLIB_HINT:
                findings.append(f"{path}:{lineno}: [A2] domain imports third-party '{root}' - "
                                "verify it is policy-safe (pure lib ok, I/O lib not)")
    return findings


def run(src_root: str, domain_pkg: str) -> list[str]:
    domain_dir = os.path.join(src_root, domain_pkg)
    if not os.path.isdir(domain_dir):
        return [f"error: {domain_dir} not found"]
    siblings = {d for d in os.listdir(src_root)
                if os.path.isdir(os.path.join(src_root, d)) and d != domain_pkg}
    findings: list[str] = []
    for dirpath, _dirs, files in os.walk(domain_dir):
        for f in files:
            if f.endswith(".py"):
                findings += scan_domain_file(os.path.join(dirpath, f), domain_pkg, siblings)
    return findings


def demo() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "domain"))
        os.makedirs(os.path.join(td, "adapters"))
        with open(os.path.join(td, "domain", "rules.py"), "w", encoding="utf-8") as f:
            f.write("import datetime\n"
                    "from fastapi import HTTPException\n"     # A2
                    "from adapters.repo import save\n")        # A1
        print("demo mode - domain file with two violations:")
        for ln in run(td, "domain"):
            print("  " + ln.replace(td, "<demo>"))


def main(argv: list[str]) -> int:
    if not argv:
        demo()
        print("Usage: python dependency_direction.py <src_root> [--domain domain]")
        return 0
    domain_pkg = "domain"
    if "--domain" in argv:
        i = argv.index("--domain")
        domain_pkg = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    total = 0
    for root in argv:
        for ln in run(root, domain_pkg):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
