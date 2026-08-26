#!/usr/bin/env python3
"""Nielsen's 10 Usability Heuristics evaluation checklist runner.

Prints the 10 heuristics with a concrete probe question each, so a UX review
is systematic instead of vibes. Optionally scores a self-assessment passed as
10 marks (y/n/?) to compute a quick severity snapshot.

This is a thinking aid, not a verdict: usability is judged by observing real
users, not by a checklist. (Nielsen, 1994.)

Usage:
  heuristics.py                 # print the 10 heuristics + probes
  heuristics.py yyn?ynyyyn      # score 10 chars (y=ok, n=violated, ?=unsure)

ASCII output only. Standard library only.
"""
import sys

HEURISTICS = [
    ("Visibility of system status", "Does every action get immediate, clear feedback?"),
    ("Match system & real world", "Do words/flows match users' language and expectations?"),
    ("User control & freedom", "Is there an obvious undo / exit / cancel?"),
    ("Consistency & standards", "Same thing named/placed the same way? Follows platform conventions?"),
    ("Error prevention", "Are destructive/likely mistakes blocked before they happen?"),
    ("Recognition over recall", "Are options/info visible, not memorized from a prior screen?"),
    ("Flexibility & efficiency", "Shortcuts for experts without burdening novices?"),
    ("Aesthetic & minimalist", "Any element that competes with the essential ones is removed?"),
    ("Help users with errors", "Plain-language error + cause + how to recover (no codes)?"),
    ("Help & documentation", "If help is needed, is it findable and task-focused?"),
]


def print_list():
    print("Nielsen's 10 Usability Heuristics (1994) - review probes:\n")
    for i, (name, probe) in enumerate(HEURISTICS, 1):
        print(f"{i:>2}. {name}")
        print(f"    probe: {probe}")
    print("\nReminder: confirm with 5 real users (finds ~most issues) - checklist is not proof.")


def score(marks):
    marks = marks.strip().lower()
    if len(marks) != 10 or any(c not in "yn?" for c in marks):
        print("score needs exactly 10 chars from {y,n,?}")
        sys.exit(1)
    violated = [HEURISTICS[i][0] for i, c in enumerate(marks) if c == "n"]
    unsure = [HEURISTICS[i][0] for i, c in enumerate(marks) if c == "?"]
    ok = marks.count("y")
    print(f"self-assessment: {ok}/10 ok, {len(violated)} violated, {len(unsure)} unsure\n")
    if violated:
        print("FIX (violated):")
        for v in violated:
            print(f"  - {v}")
    if unsure:
        print("VERIFY (unsure):")
        for u in unsure:
            print(f"  - {u}")
    if not violated and not unsure:
        print("no self-reported violations - still test with real users.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_list()
    else:
        score(sys.argv[1])
