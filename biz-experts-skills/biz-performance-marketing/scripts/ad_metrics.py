#!/usr/bin/env python3
"""Performance-marketing unit-economics calculator.

Computes the numbers that gate whether to scale paid spend:
  ROAS      = revenue / ad_spend                 (per-channel return)
  MER       = total_revenue / total_ad_spend     (blended; catches what last-click hides)
  CAC       = ad_spend / new_customers
  LTV:CAC   = ltv / cac                           (>= ~3 is a common healthy target)
  Payback   = cac / monthly_gross_margin_per_cust (months to recover CAC)

Why payback matters: a 3:1 LTV:CAC over 5 years can still bankrupt you if the
cash takes 20 months to come back. Scale needs both ratio AND payback.

Usage:
  ad_metrics.py                                   # demo
  ad_metrics.py roas REVENUE SPEND
  ad_metrics.py cac SPEND NEW_CUSTOMERS
  ad_metrics.py unit LTV CAC MONTHLY_MARGIN_PER_CUST

ASCII output only. Standard library only.
"""
import sys


def roas(rev, spend):
    if spend <= 0:
        raise ValueError("spend must be > 0")
    return rev / spend


def cac(spend, customers):
    if customers <= 0:
        raise ValueError("customers must be > 0")
    return spend / customers


def unit(ltv, cac_v, monthly_margin):
    ratio = ltv / cac_v if cac_v else float("inf")
    payback = cac_v / monthly_margin if monthly_margin > 0 else float("inf")
    return ratio, payback


def verdict_ratio(r):
    if r >= 3:
        return "healthy (>=3)"
    if r >= 1:
        return "thin (1-3): improve LTV/CAC before scaling"
    return "LOSS (<1): each customer loses money"


def demo():
    print("=== ROAS / MER demo ===")
    print(f"  channel A ROAS = 8000/2000 = {roas(8000,2000):.1f}")
    print(f"  blended  MER  = 30000/12000 = {roas(30000,12000):.1f}  (blended catches last-click inflation)\n")
    print("=== CAC demo ===")
    c = cac(12000, 150)
    print(f"  CAC = 12000/150 = {c:.0f}\n")
    print("=== unit economics demo ===")
    ratio, payback = unit(240, 80, 12)
    print(f"  LTV=240, CAC=80, monthly margin/cust=12")
    print(f"  LTV:CAC = {ratio:.1f}  -> {verdict_ratio(ratio)}")
    print(f"  payback = {payback:.1f} months  (cash recovery time)")


if __name__ == "__main__":
    a = sys.argv
    if len(a) == 1:
        demo()
    elif a[1] == "roas" and len(a) == 4:
        print(f"ROAS = {roas(float(a[2]), float(a[3])):.2f}")
    elif a[1] == "cac" and len(a) == 4:
        print(f"CAC = {cac(float(a[2]), float(a[3])):.2f}")
    elif a[1] == "unit" and len(a) == 5:
        r, p = unit(float(a[2]), float(a[3]), float(a[4]))
        print(f"LTV:CAC = {r:.2f} ({verdict_ratio(r)}); payback = {p:.1f} months")
    else:
        print("usage: ad_metrics.py | roas REV SPEND | cac SPEND CUST | unit LTV CAC MONTHLY_MARGIN")
        sys.exit(1)
