#!/usr/bin/env python3
"""Cohort retention + stickiness helper for product analytics.

1) Retention curve: given a cohort's active counts by period (period 0 = signup),
   show retention % vs period 0 and flag whether the curve appears to FLATTEN
   (a flattening curve is the signal of product-market fit / a healthy floor;
   a curve heading to 0 means churn, not growth).

2) Stickiness: DAU/MAU ratio (rough engagement proxy; benchmark varies by product
   type, so treat as relative, not absolute).

Why cohorts, not totals: total/MAU can rise from new inflow while every cohort
churns out (SKILL.md antipattern 1/3). Cohorts reveal the truth.

Usage:
  cohort.py                         # demo
  cohort.py ret 1000 420 310 280 275 270   # active counts per period from cohort
  cohort.py stick 1200 5000         # DAU MAU

ASCII output only. Standard library only.
"""
import sys


def retention(counts):
    if len(counts) < 2 or counts[0] <= 0:
        raise ValueError("need period-0 size > 0 and >=2 periods")
    base = counts[0]
    pct = [c / base for c in counts]
    # flatten heuristic: last 3 deltas all small (<2 percentage points)
    flat = None
    if len(pct) >= 4:
        deltas = [abs(pct[i] - pct[i - 1]) for i in range(len(pct) - 2, len(pct))]
        flat = all(d < 0.02 for d in deltas)
    return pct, flat


def demo():
    counts = [1000, 420, 310, 280, 275, 270]
    pct, flat = retention(counts)
    print("=== cohort retention demo (period 0 = signup) ===")
    for i, (c, p) in enumerate(zip(counts, pct)):
        bar = "#" * int(p * 40)
        print(f"  P{i}: {c:>5} ({p*100:5.1f}%) {bar}")
    if flat:
        print("  -> curve appears to FLATTEN near a floor: healthy retention signal.")
    else:
        print("  -> not yet flattening: watch for churn-to-zero (leaky bucket).")
    print()
    print("=== stickiness demo ===")
    dau, mau = 1200, 5000
    print(f"  DAU/MAU = {dau}/{mau} = {dau/mau*100:.1f}% (relative proxy; benchmark varies)")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        demo()
    elif sys.argv[1] == "ret" and len(sys.argv) >= 4:
        counts = [float(x) for x in sys.argv[2:]]
        pct, flat = retention(counts)
        for i, p in enumerate(pct):
            print(f"  P{i}: {p*100:.1f}%")
        print("flattening: " + ("yes (healthy floor)" if flat else "no/unknown"))
    elif sys.argv[1] == "stick" and len(sys.argv) == 4:
        dau, mau = float(sys.argv[2]), float(sys.argv[3])
        print(f"DAU/MAU = {dau/mau*100:.1f}%")
    else:
        print("usage: cohort.py | ret C0 C1 .. | stick DAU MAU")
        sys.exit(1)
