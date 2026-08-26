#!/usr/bin/env python3
"""Startup unit-economics & runway calculator.

  runway   = cash / net_monthly_burn
  LTV      = (ARPU * gross_margin) / monthly_churn_rate
  CAC      = sales+marketing spend / new customers
  payback  = CAC / (ARPU * gross_margin)        (months to recover CAC)
  NRR      = (start_MRR + expansion - churn - contraction) / start_MRR

Why both LTV:CAC AND payback: a 5:1 ratio with 20-month payback still ties up
cash; a healthy company needs both a good ratio and fast cash recovery
(SKILL.md antipattern 4).

Not accounting/tax advice. ASCII output only. Standard library only.

Usage:
  runway.py                                   # demo
  runway.py runway CASH NET_BURN
  runway.py ltv ARPU MARGIN CHURN             # margin 0..1, churn monthly 0..1
  runway.py payback CAC ARPU MARGIN
  runway.py nrr START EXPANSION CHURN CONTRACTION
"""
import sys


def runway(cash, burn):
    if burn <= 0:
        return float("inf")
    return cash / burn


def ltv(arpu, margin, churn):
    if churn <= 0:
        raise ValueError("churn must be > 0")
    return (arpu * margin) / churn


def payback(cac, arpu, margin):
    denom = arpu * margin
    if denom <= 0:
        raise ValueError("arpu*margin must be > 0")
    return cac / denom


def nrr(start, expansion, churn, contraction):
    if start <= 0:
        raise ValueError("start MRR must be > 0")
    return (start + expansion - churn - contraction) / start


def demo():
    print("=== runway ===")
    print(f"  cash=600k, net burn=50k/mo -> {runway(600000,50000):.0f} months")
    print("\n=== unit economics ===")
    arpu, margin, churn, cac = 50.0, 0.8, 0.03, 300.0
    l = ltv(arpu, margin, churn)
    pb = payback(cac, arpu, margin)
    print(f"  ARPU={arpu}/mo, margin={margin*100:.0f}%, monthly churn={churn*100:.0f}%, CAC={cac}")
    print(f"  LTV = {l:.0f}")
    print(f"  LTV:CAC = {l/cac:.1f}  ({'healthy' if l/cac>=3 else 'thin/loss'})")
    print(f"  payback = {pb:.1f} months")
    print("\n=== NRR ===")
    r = nrr(100000, 15000, 8000, 3000)
    print(f"  start=100k, +exp 15k, -churn 8k, -contraction 3k -> NRR {r*100:.0f}%"
          f"  ({'expanding' if r>=1 else 'leaking'})")


if __name__ == "__main__":
    a = sys.argv
    try:
        if len(a) == 1:
            demo()
        elif a[1] == "runway" and len(a) == 4:
            print(f"runway = {runway(float(a[2]), float(a[3])):.1f} months")
        elif a[1] == "ltv" and len(a) == 5:
            print(f"LTV = {ltv(float(a[2]), float(a[3]), float(a[4])):.0f}")
        elif a[1] == "payback" and len(a) == 5:
            print(f"payback = {payback(float(a[2]), float(a[3]), float(a[4])):.1f} months")
        elif a[1] == "nrr" and len(a) == 6:
            print(f"NRR = {nrr(float(a[2]),float(a[3]),float(a[4]),float(a[5]))*100:.0f}%")
        else:
            print("usage: runway.py | runway CASH BURN | ltv ARPU MARGIN CHURN | payback CAC ARPU MARGIN | nrr START EXP CHURN CONTRACT")
            sys.exit(1)
    except ValueError as e:
        print(f"error: {e}")
        sys.exit(1)
