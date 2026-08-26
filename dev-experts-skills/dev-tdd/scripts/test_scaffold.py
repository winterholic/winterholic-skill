"""test_scaffold.py - generate red-by-default pytest skeletons from a module (stdlib only).

Reads a .py file, finds public functions (and public methods of public classes),
and emits a test skeleton where every test fails with pytest.fail("TODO") -
embodying red-first: scaffolds must be made green one cycle at a time.

Usage:
  python test_scaffold.py <module.py>            (prints skeleton to stdout)
  python test_scaffold.py <module.py> -o tests/  (writes tests/test_<module>.py, refuses to overwrite)
  python test_scaffold.py                        (no args: self-demo)

Exit code: 0 ok, 1 refused overwrite, 2 usage/parse error.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import ast
import os
import sys


def public_functions(tree: ast.Module) -> list[str]:
    """Top-level public function names + 'Class.method' for public methods."""
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                names.append(node.name)
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not sub.name.startswith("_"):
                        names.append(f"{node.name}.{sub.name}")
    return names


def render(module_name: str, names: list[str]) -> str:
    lines = [
        '"""Auto-generated red-first scaffold - make green one cycle at a time."""',
        "import pytest",
        "",
        f"# from {module_name} import ...   # TODO: import the behavior under test",
        "",
    ]
    if not names:
        lines.append("# no public functions found - write the first RED test by hand")
    for n in names:
        test_name = "test_" + n.lower().replace(".", "_")
        lines += [
            "",
            f"def {test_name}():",
            "    # Arrange: smallest input that exercises one behavior",
            "    # Act:     call it (one line)",
            "    # Assert:  state the expected value, then delete the fail() below",
            f'    pytest.fail("TODO: RED first - {n}")',
        ]
    return "\n".join(lines) + "\n"


DEMO = '''\
def normalize_tick(raw):
    ...

def _private_helper():
    ...

class Portfolio:
    def add(self, tick):
        ...
    def total(self):
        ...
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no file given) - scaffolding built-in sample:")
        tree = ast.parse(DEMO)
        print(render("sample", public_functions(tree)))
        print("Usage: python test_scaffold.py <module.py> [-o tests_dir]")
        return 0

    src_path = argv[0]
    out_dir = None
    if "-o" in argv:
        i = argv.index("-o")
        if i + 1 >= len(argv):
            print("error: -o needs a directory")
            return 2
        out_dir = argv[i + 1]

    try:
        with open(src_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except FileNotFoundError:
        print(f"error: {src_path} not found")
        return 2
    except SyntaxError as e:
        print(f"error: {src_path}:{e.lineno}: {e.msg}")
        return 2

    module_name = os.path.splitext(os.path.basename(src_path))[0]
    text = render(module_name, public_functions(tree))

    if out_dir is None:
        print(text)
        return 0

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"test_{module_name}.py")
    if os.path.exists(out_path):
        # never clobber existing tests - they may already be green
        print(f"refused: {out_path} already exists (append by hand)")
        return 1
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"wrote {out_path} ({len(public_functions(tree))} red test(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
