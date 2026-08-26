"""ffmpeg_lint.py - ffmpeg command smell detector (stdlib only, regex heuristic).

Detects (matching dev-media-ffmpeg SKILL.md antipattern catalog):
  [F1] re-encoding when stream copy might do (-c:v libx264/libx265 without resolution/bitrate change)
  [F3] RTSP input without tcp transport (-i rtsp://... and no -rtsp_transport tcp)
  [F5] recording without segmenting (long .mp4 output, no -f segment)

Scans .sh / .py / .txt containing ffmpeg command lines.

Usage:
  python ffmpeg_lint.py <file_or_dir> [...]
  python ffmpeg_lint.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with 'ffmpeg-ok:' comment.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    for i, line in enumerate(text.splitlines(), 1):
        if "ffmpeg" not in line or "ffmpeg-ok:" in line:
            continue
        # [F1] software re-encode without an actual transform (no scale/-b:v/-s)
        if re.search(r"-c(:v)?\s+(libx264|libx265|libvpx|libaom)", line):
            transforms = re.search(r"(-vf\s+scale|-s\s+\d+x\d+|-b:v|-crf|-r\s+\d)", line)
            if not transforms:
                findings.append(f"{label}:{i}: [F1] software re-encode without scale/bitrate/fps change - "
                                "is '-c copy' enough? re-encoding burns CPU + loses quality")
        # [F3] rtsp input without tcp transport
        if re.search(r"-i\s+rtsp://", line) and "-rtsp_transport tcp" not in line:
            findings.append(f"{label}:{i}: [F3] RTSP input without -rtsp_transport tcp - "
                            "UDP drops/corrupts frames; add tcp + reconnect wrapper")
        # [F5] long recording to single mp4 without segmenting
        if re.search(r"-i\s+rtsp://", line) and re.search(r"\.mp4|\.mkv", line) \
                and "-f segment" not in line and "-c copy" in line:
            findings.append(f"{label}:{i}: [F5] RTSP recording without -f segment - "
                            "single huge file: crash-fragile, no rotation; segment (e.g. 600s)")
    return sorted(set(findings))


DEMO = '''\
ffmpeg -i input.mp4 -c:v libx264 output.mkv
ffmpeg -i rtsp://cam/ch1 -c copy record.mp4
ffmpeg -rtsp_transport tcp -i rtsp://cam/ch1 -c copy -f segment -segment_time 600 ch_%Y%m%d.mp4
'''


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo>"):
            print("  " + ln)
        print("Usage: python ffmpeg_lint.py <file_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, _dirs, fs in os.walk(p):
                paths.extend(os.path.join(root, f) for f in fs if f.endswith((".sh", ".py", ".txt", ".conf")))
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
