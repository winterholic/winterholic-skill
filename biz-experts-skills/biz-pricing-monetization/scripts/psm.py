#!/usr/bin/env python3
"""van Westendorp Price Sensitivity Meter (PSM) helper.

Given the four PSM survey questions' cumulative response curves, find the
classic intersection points that bound an acceptable price RANGE.

The four questions (each respondent gives a price for each):
  too_cheap     : so cheap you'd doubt its quality
  cheap         : a bargain / good value
  expensive     : starting to feel expensive (but would still consider)
  too_expensive : so expensive you would not buy

Intersections (van Westendorp, ESOMAR 1976):
  OPP (Optimal Price Point) : "too cheap" curve x "too expensive" curve
  IPP (Indifference Price)  : "cheap" x "expensive"
  PMC (Point of Marginal Cheapness)   : "too cheap" x "expensive"
  PME (Point of Marginal Expensiveness): "cheap" x "too expensive"
  Acceptable range = [PMC, PME]

CAUTION (SKILL.md / evidence.md): PSM gives a price RANGE, not the final price,
and does NOT measure demand/volume (pair with Gabor-Granger or conjoint).
Stated-preference bias applies. Not advice. ASCII only. Std lib only.

Usage:
  psm.py                      # demo with synthetic responses
  psm.py FILE.csv             # CSV with header: too_cheap,cheap,expensive,too_expensive
                              # one row per respondent (prices)
"""
import sys
import csv


def _curves(rows, grid):
    n = len(rows)
    tc = [r["too_cheap"] for r in rows]
    ch = [r["cheap"] for r in rows]
    ex = [r["expensive"] for r in rows]
    te = [r["too_expensive"] for r in rows]

    def share_ge(vals, p):   # share whose threshold >= p  (falling curve)
        return sum(1 for v in vals if v >= p) / n

    def share_le(vals, p):   # share whose threshold <= p  (rising curve)
        return sum(1 for v in vals if v <= p) / n

    return {
        "too_cheap": [share_ge(tc, p) for p in grid],      # falling
        "cheap": [share_ge(ch, p) for p in grid],          # falling
        "expensive": [share_le(ex, p) for p in grid],      # rising
        "too_expensive": [share_le(te, p) for p in grid],  # rising
    }


def _cross(grid, a, b):
    """First price where curve a and curve b cross."""
    prev = None
    for i, p in enumerate(grid):
        d = a[i] - b[i]
        if prev is not None and (prev == 0 or (prev < 0) != (d < 0)):
            return p
        prev = d
    return None


def psm(rows):
    allp = [v for r in rows for v in r.values()]
    lo, hi = min(allp), max(allp)
    step = max((hi - lo) / 200.0, 1e-9)
    grid = [lo + i * step for i in range(201)]
    c = _curves(rows, grid)
    return {
        "OPP": _cross(grid, c["too_cheap"], c["too_expensive"]),
        "IPP": _cross(grid, c["cheap"], c["expensive"]),
        "PMC": _cross(grid, c["too_cheap"], c["expensive"]),
        "PME": _cross(grid, c["cheap"], c["too_expensive"]),
    }


def _fmt(x):
    return "n/a" if x is None else f"{x:,.0f}"


def report(rows):
    r = psm(rows)
    print(f"respondents: {len(rows)}")
    print(f"  OPP (optimal price point)        = {_fmt(r['OPP'])}")
    print(f"  IPP (indifference price point)   = {_fmt(r['IPP'])}")
    print(f"  PMC (marginal cheapness)         = {_fmt(r['PMC'])}")
    print(f"  PME (marginal expensiveness)     = {_fmt(r['PME'])}")
    print(f"  acceptable range = [{_fmt(r['PMC'])} .. {_fmt(r['PME'])}]")
    print("  note: this is a RANGE, not the final price; PSM ignores demand/volume.")


def demo():
    import random
    random.seed(7)
    rows = []
    for _ in range(300):
        base = random.uniform(8, 14)
        rows.append({
            "too_cheap": base * 0.5,
            "cheap": base * 0.8,
            "expensive": base * 1.3,
            "too_expensive": base * 1.8,
        })
    print("=== PSM demo (synthetic, base ~ 8..14) ===")
    report(rows)


def load_csv(path):
    rows = []
    with open(path, newline="") as f:
        for d in csv.DictReader(f):
            rows.append({k: float(d[k]) for k in
                         ("too_cheap", "cheap", "expensive", "too_expensive")})
    if not rows:
        raise ValueError("no rows")
    return rows


if __name__ == "__main__":
    a = sys.argv
    if len(a) == 1:
        demo()
    elif len(a) == 2:
        try:
            report(load_csv(a[1]))
        except (OSError, ValueError, KeyError) as e:
            print(f"error: {e}")
            sys.exit(1)
    else:
        print("usage: psm.py | psm.py FILE.csv "
              "(header: too_cheap,cheap,expensive,too_expensive)")
        sys.exit(1)
