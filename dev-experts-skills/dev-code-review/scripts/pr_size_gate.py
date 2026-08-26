"""pr_size_gate.py - PR size measurement + split suggestion (stdlib only).

Reads `git diff --numstat <range>` output (file or stdin) and reports:
  total churn vs the 400-line review budget (SmartBear-derived starting point),
  grouping by top-level directory to suggest natural split seams.

Usage:
  git diff --numstat main...HEAD | python pr_size_gate.py -
  python pr_size_gate.py <numstat.txt>
  python pr_size_gate.py              (no args: self-demo; stdin only with '-')

Exit code: 0 = within budget, 1 = over budget, 2 = usage error.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import sys
from collections import defaultdict

# 400-line precision-review budget: review defect detection drops sharply
# beyond ~400 LoC per session (SmartBear/Cisco study) - starting point, not law.
BUDGET = 400
GENERATED_HINTS = ("lock", ".min.", "generated", "snapshot", "__snapshots__")


def parse_numstat(lines: list[str]) -> list[tuple[int, int, str]]:
    rows = []
    for line in lines:
        parts = line.strip().split("\t")
        if len(parts) != 3:
            continue
        add, dele, path = parts
        if add == "-" or dele == "-":      # binary
            continue
        rows.append((int(add), int(dele), path))
    return rows


def report(rows: list[tuple[int, int, str]]) -> int:
    if not rows:
        print("no diff rows parsed - pipe `git diff --numstat <range>` in")
        return 2
    reviewable = [(a, d, p) for a, d, p in rows
                  if not any(h in p.lower() for h in GENERATED_HINTS)]
    skipped = len(rows) - len(reviewable)
    total = sum(a + d for a, d, _ in reviewable)

    by_dir: dict[str, int] = defaultdict(int)
    for a, d, p in reviewable:
        top = p.split("/")[0] if "/" in p else "(root)"
        by_dir[top] += a + d

    print(f"reviewable churn: {total} lines across {len(reviewable)} files"
          + (f" ({skipped} generated/lock files excluded)" if skipped else ""))
    for top, churn in sorted(by_dir.items(), key=lambda kv: -kv[1]):
        print(f"  {top:<24} {churn:>6} lines")

    if total <= BUDGET:
        print(f"OK: within the {BUDGET}-line precision budget")
        return 0
    print(f"OVER: {total} > {BUDGET} - consider splitting; natural seams above "
          "(refactor-only commits first, feature after - dev-refactoring #3)")
    return 1


DEMO = """\
120\t30\tcollector/clean.py
85\t10\tcollector/loader.py
220\t40\tapi/routes.py
3\t1\tREADME.md
1500\t0\tpackage-lock.json
"""


def main(argv: list[str]) -> int:
    # stdin only on explicit '-' (isatty is unreliable under CI/agent harnesses
    # and would block forever waiting for input)
    if argv and argv[0] == "-":
        lines = sys.stdin.read().splitlines()
    elif argv:
        try:
            with open(argv[0], encoding="utf-8") as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            print(f"error: {argv[0]} not found")
            return 2
    else:
        print("demo mode (no input) - sample numstat:")
        return report(parse_numstat(DEMO.splitlines()))
    return report(parse_numstat(lines))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
