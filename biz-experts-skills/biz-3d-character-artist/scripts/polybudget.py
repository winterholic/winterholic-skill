#!/usr/bin/env python3
"""Polycount budget guide + over-budget check for game-ready characters.

Gives a STARTING-POINT triangle budget per target tier, and checks whether a
given mesh's triangle count fits. These are industry rules of thumb, not laws:
the project's technical artist and engine guidelines always win (how many
characters on screen at once, target platform, LOD strategy).

Tiers (triangles), per common industry references (verify per project):
  mobile        : 5,000 - 15,000
  pc_npc        : 30,000 - 50,000
  aaa_hero      : 80,000 - 120,000

Why a range, not a number: budget depends on concurrent character count and
LODs. A hero shown alone affords more than 20 NPCs in a crowd.

Usage:
  polybudget.py                     # show tiers
  polybudget.py mobile 18000        # check a mesh against a tier
  polybudget.py check <tris>        # which tier does <tris> fit?

ASCII output only. Standard library only.
"""
import sys

TIERS = {
    "mobile":   (5_000, 15_000),
    "pc_npc":   (30_000, 50_000),
    "aaa_hero": (80_000, 120_000),
}


def show():
    print("Triangle budget tiers (starting points - TA/engine guideline wins):\n")
    for name, (lo, hi) in TIERS.items():
        print(f"  {name:<10} {lo:>8,} - {hi:>8,} tris")
    print("\nTip: spend triangles on deformation/silhouette; fake surface detail with normal maps.")


def check_tier(tier, tris):
    if tier not in TIERS:
        print(f"unknown tier '{tier}' (use: {', '.join(TIERS)})")
        sys.exit(1)
    lo, hi = TIERS[tier]
    if tris < lo:
        v = f"UNDER budget ({tris:,} < {lo:,}) - fine, or add detail where it deforms"
    elif tris > hi:
        v = f"OVER budget ({tris:,} > {hi:,}) - retopo / move detail to normal map"
    else:
        v = f"within budget ({lo:,}-{hi:,})"
    print(f"{tier}: {tris:,} tris -> {v}")


def which(tris):
    fits = [n for n, (lo, hi) in TIERS.items() if lo <= tris <= hi]
    print(f"{tris:,} tris fits tier(s): {', '.join(fits) if fits else 'none (between/over tiers)'}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        show()
    elif len(sys.argv) == 3 and sys.argv[1] in TIERS:
        check_tier(sys.argv[1], int(sys.argv[2].replace(",", "")))
    elif len(sys.argv) == 3 and sys.argv[1] == "check":
        which(int(sys.argv[2].replace(",", "")))
    else:
        print("usage: polybudget.py | <tier> <tris> | check <tris>")
        sys.exit(1)
