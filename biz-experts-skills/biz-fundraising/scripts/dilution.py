#!/usr/bin/env python3
"""Startup dilution / cap-table helper.

Shows what a priced round does to ownership, including the common gotcha that
the option pool is usually created PRE-money (so it dilutes founders, not the
new investor).

Definitions:
  pre-money   : company value before new money
  post-money  : pre + investment
  investor %  : investment / post-money
  pool (pre)  : new option pool carved from pre-money -> dilutes existing holders

Why this matters: a "higher valuation" with a big pre-money pool can leave
founders with LESS than a lower valuation with a smaller/post pool
(SKILL.md antipattern 1/6). Always reason in fully-diluted terms.

Usage:
  dilution.py                                  # demo
  dilution.py round PRE INVEST [POOL_PCT]      # POOL_PCT = new pre-money pool, e.g. 0.10

Not legal/financial advice. Verify with counsel. ASCII output only. Std lib only.
"""
import sys


def priced_round(pre, invest, pool_pct=0.0):
    """Return ownership after a priced round.
    pool_pct: target post-round option pool, created pre-money (dilutes founders).
    Model: existing founders start at 100% of pre-money cap.
    """
    post = pre + invest
    investor_pct = invest / post
    # pool created pre-money: it occupies pool_pct of post-money cap, taken from pre-money holders
    pool_share = pool_pct
    founder_share = 1.0 - investor_pct - pool_share
    return {"post": post, "investor": investor_pct, "pool": pool_share, "founders": founder_share}


def demo():
    print("=== priced round demo ===")
    for pre, inv, pool in [(8e6, 2e6, 0.0), (8e6, 2e6, 0.10), (12e6, 2e6, 0.15)]:
        r = priced_round(pre, inv, pool)
        print(f"  pre={pre/1e6:.0f}M invest={inv/1e6:.0f}M pool(pre)={pool*100:.0f}%"
              f"  -> post={r['post']/1e6:.0f}M | investor {r['investor']*100:4.1f}% |"
              f" pool {r['pool']*100:4.1f}% | founders {r['founders']*100:4.1f}%")
    print("\nNote: higher pre (12M) + 15% pre-money pool can leave founders")
    print("LESS than lower pre (8M) + smaller pool. Valuation headline != ownership.")
    print("\n=== cumulative dilution over rounds ===")
    own = 1.0
    for name, inv_pct in [("seed", 0.20), ("A", 0.22), ("B", 0.18)]:
        own *= (1 - inv_pct)
        print(f"  after {name} (-{inv_pct*100:.0f}%): founders hold {own*100:.1f}%")


if __name__ == "__main__":
    a = sys.argv
    if len(a) == 1:
        demo()
    elif a[1] == "round" and len(a) in (4, 5):
        pre, inv = float(a[2]), float(a[3])
        pool = float(a[4]) if len(a) == 5 else 0.0
        r = priced_round(pre, inv, pool)
        print(f"post-money: {r['post']:.0f}")
        print(f"investor: {r['investor']*100:.1f}% | pool: {r['pool']*100:.1f}% | founders: {r['founders']*100:.1f}%")
    else:
        print("usage: dilution.py | round PRE INVEST [POOL_PCT]")
        sys.exit(1)
