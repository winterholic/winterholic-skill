"""react_check.py - React source smell detector (stdlib only).

Detects (matching dev-react SKILL.md antipattern catalog):
  [R1] useEffect whose body is only setState calls (derived-state sync)
  [R3] eslint-disable of react-hooks/exhaustive-deps
  [R5] key={index} in a .map() callback
  [R7] bare fetch().then(setX) inside useEffect

Heuristic, regex-based (no JS parser in stdlib) - aimed at the common shapes.
Silence a line with '// react-ok: <reason>'.

Usage:
  python react_check.py <src_file_or_dir> [...]
  python react_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

RE_DISABLE_DEPS = re.compile(r"eslint-disable.*react-hooks/exhaustive-deps")
RE_INDEX_KEY = re.compile(r"\.map\(\s*\(\s*\w+\s*,\s*(\w+)\s*\)\s*=>[^)]*key=\{(\1)\}", re.S)
RE_EFFECT = re.compile(r"useEffect\(\s*\(\)\s*=>\s*\{(.*?)\}\s*,\s*\[(.*?)\]\s*\)", re.S)
RE_FETCH_THEN_SET = re.compile(r"fetch\([^)]*\)[\s\S]{0,120}?\.then\([^)]*set[A-Z]\w*")


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def line_of(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    def silenced(ln: int) -> bool:
        return 0 < ln <= len(lines) and "react-ok:" in lines[ln - 1]

    for m in RE_DISABLE_DEPS.finditer(text):
        ln = line_of(m.start())
        if not silenced(ln):
            findings.append(f"{label}:{ln}: [R3] exhaustive-deps disabled - stale closure risk; "
                            "restructure instead of silencing")

    for m in RE_INDEX_KEY.finditer(text):
        ln = line_of(m.start())
        if not silenced(ln):
            findings.append(f"{label}:{ln}: [R5] key={{index}} in map - state sticks to wrong rows "
                            "on insert/remove; use a stable id")

    for m in RE_EFFECT.finditer(text):
        body = m.group(1)
        ln = line_of(m.start())
        if silenced(ln):
            continue
        stmts = [s.strip() for s in re.split(r"[;\n]", body) if s.strip() and not s.strip().startswith("//")]
        if stmts and all(re.match(r"^set[A-Z]\w*\(", s) for s in stmts):
            findings.append(f"{label}:{ln}: [R1] useEffect body is only setState - derived state; "
                            "compute during render (or useMemo)")
        if RE_FETCH_THEN_SET.search(body):
            findings.append(f"{label}:{ln}: [R7] bare fetch().then(setX) in effect - race/cache/cancel "
                            "missing; use a data library or ignore-flag cleanup")
    return sorted(set(findings))


def iter_files(paths: list[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d != "node_modules"]
                out.extend(os.path.join(root, f) for f in files
                           if f.endswith((".jsx", ".tsx", ".js", ".ts")))
        else:
            out.append(p)
    return out


DEMO = """\
function Bad({ first, last, items }) {
  const [full, setFull] = useState("");
  useEffect(() => { setFull(first + " " + last); }, [first, last]);
  useEffect(() => {
    fetch("/api/candles").then(r => r.json()).then(setData);
  }, []);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { sync(); }, []);
  return items.map((x, i) => <Row key={i} item={x} />);
}
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo.tsx>"):
            print("  " + ln)
        print("Usage: python react_check.py <src_or_dir> ...")
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
