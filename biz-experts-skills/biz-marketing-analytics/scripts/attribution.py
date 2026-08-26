#!/usr/bin/env python3
"""Attribution model comparison for a conversion path.

Given an ordered list of touchpoint channels leading to ONE conversion, split
the credit under several rule-based models so you can SEE how much the chosen
model changes the story (the point: the model is an assumption, not truth).

Models:
  first   : 100% to first touch
  last    : 100% to last touch (the common default; biases toward harvesting channels)
  linear  : equal split
  position: 40% first, 40% last, 20% split among middle (U-shaped)

None of these is causal. Causation needs incrementality experiments
(SKILL.md antipattern 2). This tool exists to expose model sensitivity.

Usage:
  attribution.py                                  # demo
  attribution.py google_ads email organic direct  # path (first->last)

ASCII output only. Standard library only.
"""
import sys
from collections import defaultdict


def first(path):
    c = defaultdict(float); c[path[0]] += 1.0; return c

def last(path):
    c = defaultdict(float); c[path[-1]] += 1.0; return c

def linear(path):
    c = defaultdict(float)
    for t in path:
        c[t] += 1.0 / len(path)
    return c

def position(path):
    c = defaultdict(float)
    if len(path) == 1:
        c[path[0]] += 1.0
    elif len(path) == 2:
        c[path[0]] += 0.5; c[path[-1]] += 0.5
    else:
        c[path[0]] += 0.4; c[path[-1]] += 0.4
        mid = path[1:-1]
        for t in mid:
            c[t] += 0.2 / len(mid)
    return c

MODELS = [("first", first), ("last", last), ("linear", linear), ("position", position)]


def compare(path):
    channels = list(dict.fromkeys(path))  # unique, keep order
    rows = {name: fn(path) for name, fn in MODELS}
    header = "channel".ljust(16) + "".join(n.rjust(10) for n, _ in MODELS)
    print(header)
    print("-" * len(header))
    for ch in channels:
        line = ch.ljust(16) + "".join(f"{rows[n][ch]*100:9.0f}%" for n, _ in MODELS)
        print(line)
    print("\nSame path, different story per model -> the model is an assumption.")
    print("For causal credit, run an incrementality holdout, not a model.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("path: google_ads -> email -> organic -> direct\n")
        compare(["google_ads", "email", "organic", "direct"])
    else:
        compare(sys.argv[1:])
