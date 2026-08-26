#!/usr/bin/env python3
"""Copy critique linter for sales/marketing copy (English + Korean aware).

Flags the signals behind SKILL.md antipatterns:
  - we/our vs you/your balance (antipattern 5: copy should star the reader)
  - specificity: presence of digits/% (antipattern 4: abstract claims)
  - hedge/weak words (maybe, kind of, leading, innovative...) that dilute
  - sentence length (long sentences hurt readability)
  - CTA signal (is there an action verb cluster?)

This is a SIGNAL checker, not a judge. Great copy can break a rule on purpose;
absence of a signal is a prompt to look, not a failure.

Usage:
  copy_lint.py            # demo
  copy_lint.py FILE
  copy_lint.py -          # stdin

ASCII output only. Standard library only.
"""
import re
import sys

WE = ["we ", "we'", "our ", "ours", "us ", "저희", "우리"]
YOU = ["you ", "you'", "your ", "yours", "당신", "고객님", "여러분"]
HEDGE = ["maybe", "kind of", "sort of", "innovative", "revolutionary", "leading",
         "world-class", "best-in-class", "synergy", "cutting-edge", "seamless",
         "혁신적", "최고의", "최첨단", "획기적"]
CTA_VERBS = ["start", "get", "try", "buy", "join", "download", "sign up", "book",
             "claim", "see", "시작", "받기", "가입", "신청", "구매", "보기", "다운로드"]

DEMO = ("Innovative, world-class platform. We built our cutting-edge engine so our "
        "customers can do more. Our mission is seamless productivity. Learn more.")


def count_any(text, needles):
    low = text.lower()
    return sum(low.count(n) for n in needles)


def analyze(text):
    we = count_any(text, WE)
    you = count_any(text, YOU)
    digits = len(re.findall(r"\d", text))
    hedges = [h for h in HEDGE if h in text.lower()]
    sents = [s for s in re.split(r"[.!?\n]+", text) if s.strip()]
    avg_words = (sum(len(s.split()) for s in sents) / len(sents)) if sents else 0
    cta = [v for v in CTA_VERBS if v in text.lower()]
    return {"we": we, "you": you, "digits": digits, "hedges": hedges,
            "avg_words": avg_words, "cta": cta}


def report(text, name):
    a = analyze(text)
    print(f"copy lint: {name}\n")
    # reader focus
    if a["you"] >= a["we"]:
        print(f"  [ok]      reader focus: you/your={a['you']} >= we/our={a['we']}")
    else:
        print(f"  [FLAG]    reader focus: we/our={a['we']} > you/your={a['you']}  -> make the reader the subject")
    # specificity
    if a["digits"] >= 1:
        print(f"  [ok]      specificity: {a['digits']} digit(s) present")
    else:
        print("  [FLAG]    specificity: no numbers -> add a concrete figure (count/price/time)")
    # hedges
    if a["hedges"]:
        print(f"  [FLAG]    weak/hype words: {', '.join(a['hedges'])}  -> replace with proof")
    else:
        print("  [ok]      no obvious hype/hedge words")
    # length
    if a["avg_words"] > 20:
        print(f"  [FLAG]    avg sentence {a['avg_words']:.0f} words -> shorten (<20)")
    else:
        print(f"  [ok]      avg sentence {a['avg_words']:.0f} words")
    # cta
    if a["cta"]:
        print(f"  [ok]      CTA signal: {', '.join(a['cta'])}")
    else:
        print("  [FLAG]    no CTA verb -> tell the reader the next action")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        report(DEMO, "DEMO")
    elif sys.argv[1] == "-":
        report(sys.stdin.read(), "<stdin>")
    else:
        try:
            with open(sys.argv[1], encoding="utf-8") as f:
                report(f.read(), sys.argv[1])
        except OSError as e:
            print(f"cannot read {sys.argv[1]}: {e}")
            sys.exit(1)
