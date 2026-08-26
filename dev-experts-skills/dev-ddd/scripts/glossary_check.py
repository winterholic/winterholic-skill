"""glossary_check.py - ubiquitous language vs code consistency checker (stdlib only).

Input: a glossary markdown file with a table containing a code-name column
       (third column: | term | definition | code_name |), plus source dirs.

Checks:
  [G1] glossary code_name not found anywhere in sources (dead vocabulary)
  [G2] banned vague identifiers in sources (Manager, Data, Info, Item, Util as exact class names)

Usage:
  python glossary_check.py <glossary.md> <src_dir> [...]
  python glossary_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

BANNED_CLASS = re.compile(r"^\s*class\s+(\w*(?:Manager|Helper|Util|Info|Data))\b", re.M)
ROW = re.compile(r"^\|([^|]+)\|([^|]+)\|([^|]+)\|", re.M)


def parse_glossary(text: str) -> list[tuple[str, str]]:
    """Return (term, code_name) pairs, skipping header/divider rows."""
    out = []
    for m in ROW.finditer(text):
        term, _defn, code = (g.strip() for g in m.groups())
        if not code or set(code) <= {"-", " "} or code.lower() in ("code_name", "코드 이름"):
            continue
        out.append((term, code))
    return out


def gather_source(paths: list[str]) -> str:
    chunks = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for f in files:
                    if f.endswith((".py", ".ts", ".tsx", ".sql")):
                        try:
                            with open(os.path.join(root, f), encoding="utf-8") as fh:
                                chunks.append(fh.read())
                        except (OSError, UnicodeDecodeError):
                            continue
        elif os.path.isfile(p):
            with open(p, encoding="utf-8") as fh:
                chunks.append(fh.read())
    return "\n".join(chunks)


def check(glossary: str, source: str) -> list[str]:
    findings = []
    for term, code in parse_glossary(glossary):
        # accept snake_case / CamelCase variants of the code name
        variants = {code, code.lower(), re.sub(r"(?<!^)(?=[A-Z])", "_", code).lower()}
        if not any(v in source for v in variants):
            findings.append(f"[G1] glossary term '{term}' -> code '{code}' not found in sources "
                            "- dead vocabulary or naming drift")
    for m in BANNED_CLASS.finditer(source):
        findings.append(f"[G2] vague class name '{m.group(1)}' - name the domain concept instead")
    return findings


DEMO_GLOSSARY = """\
| 용어 | 정의 | 코드 이름 |
|---|---|---|
| TradingDay | KRX 개장일 | trading_day |
| Candle | 종목x거래일 시세 막대 | Candle |
| SettlementPrice | 정산 가격 | SettlementPrice |
"""

DEMO_SOURCE = """\
class Candle: ...
def is_trading_day(d): ...
class TickDataManager: ...
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode - checking built-in glossary vs sample source:")
        for ln in check(DEMO_GLOSSARY, DEMO_SOURCE):
            print("  " + ln)
        print("Usage: python glossary_check.py <glossary.md> <src_dir> ...")
        return 0
    if len(argv) < 2:
        print("error: need <glossary.md> and at least one source path")
        return 2
    try:
        with open(argv[0], encoding="utf-8") as f:
            glossary = f.read()
    except FileNotFoundError:
        print(f"error: {argv[0]} not found")
        return 2
    source = gather_source(argv[1:])
    findings = check(glossary, source)
    for ln in findings:
        print(ln)
    print(f"total: {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
