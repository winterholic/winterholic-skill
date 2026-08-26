#!/usr/bin/env python3
"""AARRR funnel drop-off analyzer + viral k-factor calculator.

Two tools growth marketers use constantly:

1) Funnel: given counts at each stage, show step conversion and find the biggest
   leak. The biggest leak (not the top of funnel) is usually where to work.

2) Viral k-factor: k = invites_per_user * invite_conversion_rate.
   k >= 1 means each user brings >=1 new user -> self-sustaining viral growth.
   Most products have k < 1; viral loops then *amplify* paid/organic, not replace.

Why find-the-leak first: pouring acquisition into a funnel that leaks at
activation just scales the loss (SKILL.md antipattern 3).

Usage:
  funnel.py                          # demo
  funnel.py funnel 1000 400 250 120  # stage counts (top->bottom)
  funnel.py k 1.5 0.3                # invites_per_user, conversion_rate

ASCII output only. Standard library only.
"""
import sys

AARRR = ["Acquisition", "Activation", "Retention", "Revenue"]


def funnel(counts):
    if len(counts) < 2:
        raise ValueError("need >= 2 stage counts")
    steps = []
    worst = (1.0, 0)  # (conv, index)
    for i in range(1, len(counts)):
        prev, cur = counts[i - 1], counts[i]
        conv = cur / prev if prev else 0.0
        steps.append(conv)
        if conv < worst[0]:
            worst = (conv, i - 1)
    return steps, worst


def kfactor(invites_per_user, conv):
    return invites_per_user * conv


def demo():
    counts = [1000, 400, 250, 120]
    print("=== AARRR funnel demo ===")
    steps, (wc, wi) = funnel(counts)
    for i, conv in enumerate(steps):
        a = AARRR[i] if i < len(AARRR) else f"stage{i}"
        b = AARRR[i + 1] if i + 1 < len(AARRR) else f"stage{i+1}"
        flag = "  <== biggest leak" if i == wi else ""
        print(f"  {a:>12} -> {b:<12} {counts[i]:>5} -> {counts[i+1]:<5} ({conv*100:5.1f}%){flag}")
    overall = counts[-1] / counts[0]
    print(f"  overall: {overall*100:.1f}% ({counts[0]} -> {counts[-1]})")
    print("  action: fix the biggest leak before buying more top-of-funnel.\n")

    print("=== viral k-factor demo ===")
    for inv, c in [(1.5, 0.3), (3.0, 0.4)]:
        k = kfactor(inv, c)
        verdict = "self-sustaining (k>=1)" if k >= 1 else "sub-viral (amplifies other channels)"
        print(f"  invites/user={inv}, conv={c}  -> k={k:.2f}  {verdict}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        demo()
    elif sys.argv[1] == "funnel" and len(sys.argv) >= 4:
        counts = [float(x) for x in sys.argv[2:]]
        steps, (wc, wi) = funnel(counts)
        for i, conv in enumerate(steps):
            print(f"  step {i+1}: {counts[i]:.0f} -> {counts[i+1]:.0f} = {conv*100:.1f}%")
        print(f"  biggest leak at step {wi+1} ({wc*100:.1f}%)")
    elif sys.argv[1] == "k" and len(sys.argv) == 4:
        k = kfactor(float(sys.argv[2]), float(sys.argv[3]))
        print(f"k = {k:.2f} ({'self-sustaining' if k >= 1 else 'sub-viral'})")
    else:
        print("usage: funnel.py | funnel C1 C2 .. | k INVITES CONV")
        sys.exit(1)
