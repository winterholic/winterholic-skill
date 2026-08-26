"""cv_check.py - computer vision pipeline smell detector (stdlib only, regex heuristic).

Detects (matching dev-computer-vision SKILL.md antipattern catalog):
  [V1] per-frame heavy inference: model/detect call directly inside a frame read loop
       with no motion/sample gate in the loop
  [V2] hardcoded confidence threshold literal (conf=/score_threshold=/confidence=)
  [V6] alert/notify call directly inside the per-frame loop (single-frame decision)

Scans .py sources.

Usage:
  python cv_check.py <py_file_or_dir> [...]
  python cv_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '# cv-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

RE_FRAMELOOP = re.compile(r"while\s+.*:|for\s+\w+\s+in\s+.*(frames|capture|stream|cap\.read)", re.I)
RE_INFER = re.compile(r"(\.(detect|predict|infer|forward)\s*\(|model\s*\()", re.I)
RE_GATE = re.compile(r"(motion|diff|absdiff|background|sample|skip|every|%\s*\w+\s*==)", re.I)
RE_CONF = re.compile(r"(?i)\b(conf|confidence|score_thr\w*|conf_thr\w*)\s*=\s*0?\.\d+")
RE_NOTIFY = re.compile(r"(?i)\b(notify|send_alert|send_message|alert|telegram|push)\s*\(")


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def add(ln: int, code: str, msg: str):
        if 0 < ln <= len(lines) and "cv-ok:" in lines[ln - 1]:
            return
        findings.append(f"{label}:{ln}: [{code}] {msg}")

    # find frame-loop line ranges (crude: from a read()/capture loop to dedent end-of-file window)
    loop_lines = [i for i, l in enumerate(lines)
                  if re.search(r"(cap\.read|\.read\(\)|in\s+frames|VideoCapture|while\s+True)", l, re.I)]

    for m in RE_CONF.finditer(text):
        add(text.count("\n", 0, m.start()) + 1, "V2",
            "hardcoded confidence threshold - let the use case decide (security=low+filter, alert=high); measure")

    # heuristic: inference / notify inside ~25 lines after a frame-loop marker, with no gate nearby
    for lstart in loop_lines:
        block = "\n".join(lines[lstart:lstart + 25])
        gated = bool(RE_GATE.search(block))
        for m in RE_INFER.finditer(block):
            ln = lstart + 1 + block.count("\n", 0, m.start())
            if not gated:
                add(ln, "V1", "inference in frame loop without a motion/sample gate - "
                    "consumer can't keep up with the stream; gate frames first")
            break
        for m in RE_NOTIFY.finditer(block):
            ln = lstart + 1 + block.count("\n", 0, m.start())
            add(ln, "V6", "alert inside per-frame loop - single-frame decision is noisy; "
                "require N consecutive / track over time")
            break
    return sorted(set(findings))


DEMO = '''\
cap = cv2.VideoCapture(rtsp)
while True:
    ok, frame = cap.read()
    boxes = model.detect(frame, conf=0.25)
    if boxes:
        send_alert("object!")
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python cv_check.py <py_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, _dirs, fs in os.walk(p):
                paths.extend(os.path.join(root, f) for f in fs if f.endswith(".py"))
        else:
            paths.append(p)
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        for ln in scan_text(text, path):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
