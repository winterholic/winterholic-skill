#!/usr/bin/env python3
"""Engineering org sizing helper for a CTO/eng leader.

Estimates how many engineering managers and how many layers a team of N
engineers needs, using span-of-control heuristics.

Heuristics (industry common, NOT laws — see SKILL.md, treat as starting point):
  - First dedicated manager around 12-15 engineers (below that, the lead manages).
  - Healthy manager span of control: 5-8 direct reports (default 6).
  - Above ~8 a manager is stretched; below ~4 is usually over-management.

Why span 5-8: fewer than 4 reports rarely justifies a full-time manager (better
as a tech lead who still codes); more than 8 erodes 1:1 quality and coaching.

Standard library only. Run with no args for a demo.
"""
import sys

FIRST_MANAGER_AT = 12   # engineers; below this the founding lead manages directly
SPAN = 6                # target direct reports per manager (mid of 5-8)


def org_shape(engineers, span=SPAN):
    if engineers < 0:
        raise ValueError("engineers must be >= 0")
    if engineers < FIRST_MANAGER_AT:
        return {"managers": 0, "layers": 1,
                "note": f"<{FIRST_MANAGER_AT}: lead/CTO manages directly, no dedicated manager yet"}
    layers = 1
    nodes = engineers
    total_managers = 0
    # build management layers until the top spans within one manager
    while nodes > span:
        mgrs = -(-nodes // span)  # ceil
        total_managers += mgrs
        nodes = mgrs
        layers += 1
    return {"managers": total_managers, "layers": layers,
            "note": f"span={span}; top layer has {nodes} node(s)"}


def demo():
    print(f"(first manager ~{FIRST_MANAGER_AT} eng, target span {SPAN})\n")
    print(f"{'engineers':>9}  {'managers':>8}  {'layers':>6}  note")
    for n in (6, 12, 20, 40, 80, 150):
        s = org_shape(n)
        print(f"{n:>9}  {s['managers']:>8}  {s['layers']:>6}  {s['note']}")
    print("\nReading: at 40 eng you need ~9 managers across 3 layers.")
    print("Don't copy a later-stage org chart (antipattern 2): grow layers only when span breaks.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        demo()
    elif len(sys.argv) in (2, 3):
        n = int(sys.argv[1])
        span = int(sys.argv[2]) if len(sys.argv) == 3 else SPAN
        s = org_shape(n, span)
        print(f"{n} engineers -> {s['managers']} managers, {s['layers']} layers ({s['note']})")
    else:
        print("usage: org_sizing.py [ENGINEERS] [SPAN]")
        sys.exit(1)
