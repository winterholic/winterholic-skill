#!/usr/bin/env python3
"""RICE / ICE priority calculator for product backlog triage.

RICE = (Reach * Impact * Confidence) / Effort   (Intercom model)
  Reach:      # users/events affected per time period (e.g., per quarter)
  Impact:     per-user impact score {3=massive,2=high,1=medium,0.5=low,0.25=minimal}
  Confidence: how sure are we, as a fraction {1.0=high/quant, 0.8=medium, 0.5=low}
  Effort:     person-months (or person-weeks; keep unit consistent)

ICE = Impact * Confidence * Ease, each scored 1..10 (Sean Ellis lightweight model)

Why these defaults: Confidence forces honesty — without data you cap at 0.5 so a
loud guess cannot outrank a measured bet. Impact uses Intercom's discrete tiers to
avoid false precision (no one can tell 7 from 8 on a 1-10 impact scale).

Standard library only. Run with no args for a demo.
"""
import sys

IMPACT_TIERS = {"massive": 3.0, "high": 2.0, "medium": 1.0, "low": 0.5, "minimal": 0.25}
CONF_TIERS = {"high": 1.0, "medium": 0.8, "low": 0.5}  # high=quant data, low=guess


def rice(reach, impact, confidence, effort):
    if effort <= 0:
        raise ValueError("effort must be > 0 (person-months/weeks)")
    return (reach * impact * confidence) / effort


def ice(impact, confidence, ease):
    for n, v in (("impact", impact), ("confidence", confidence), ("ease", ease)):
        if not 1 <= v <= 10:
            raise ValueError(f"{n} must be 1..10 (got {v})")
    return impact * confidence * ease


def demo():
    print("=== RICE demo (effort in person-months) ===")
    items = [
        # name, reach/qtr, impact_tier, confidence_tier, effort
        ("Dark mode (system follow)", 4000, "low", "low", 1.0),
        ("Onboarding checklist", 12000, "high", "medium", 2.0),
        ("Enterprise SSO (1 big client)", 300, "medium", "high", 3.0),
    ]
    scored = []
    for name, reach, imp, conf, eff in items:
        score = rice(reach, IMPACT_TIERS[imp], CONF_TIERS[conf], eff)
        scored.append((score, name, reach, imp, conf, eff))
    scored.sort(reverse=True)
    print(f"{'RICE':>8}  {'item':<32} reach  impact/conf  effort")
    for score, name, reach, imp, conf, eff in scored:
        print(f"{score:8.0f}  {name:<32} {reach:>5}  {imp}/{conf}  {eff}pm")
    print("\nNote: SSO ranks low on RICE despite a loud client (Reach=300).")
    print("RICE makes the opportunity cost visible vs HiPPO prioritization.\n")

    print("=== ICE demo (1..10 each) ===")
    for name, i, c, e in [("Referral nudge", 7, 6, 8), ("Full redesign", 9, 4, 2)]:
        print(f"  {name:<18} ICE={ice(i, c, e):>4}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        demo()
    elif sys.argv[1] == "rice" and len(sys.argv) == 6:
        r, i, c, e = (float(x) for x in sys.argv[2:6])
        print(f"RICE = {rice(r, i, c, e):.1f}")
    elif sys.argv[1] == "ice" and len(sys.argv) == 5:
        i, c, e = (float(x) for x in sys.argv[2:5])
        print(f"ICE = {ice(i, c, e):.1f}")
    else:
        print("usage: rice.py                       # demo")
        print("       rice.py rice REACH IMPACT CONF EFFORT")
        print("       rice.py ice IMPACT CONF EASE")
        sys.exit(1)
