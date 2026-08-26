#!/usr/bin/env python3
"""handoff 민감 정보 치환기.

표준입력(또는 인자로 받은 파일들)에서 API 키·토큰·자격증명·PII로 의심되는
토큰을 찾아 [REDACTED]로 치환하고, 결과를 표준출력으로 내보낸다.
치환 건수는 표준에러(stderr)에 "민감 정보 N건 처리" 한 줄로 보고한다
(stdout은 정제된 본문만 담겨 파이프로 바로 파일에 쓸 수 있게).

사용:
    python3 redact.py < draft.md > clean.md
    python3 redact.py draft.md              # 파일 인자 → stdout
    python3 redact.py --check draft.md      # 치환 없이 탐지 건수만 stderr로

종료코드: 민감 정보를 1건 이상 발견하면 1, 없으면 0 (--check 시에도 동일).
CI나 훅에서 "민감 정보 있으면 실패" 게이트로 쓸 수 있다.
"""
from __future__ import annotations

import argparse
import re
import sys

REPLACEMENT = "[REDACTED]"

# (이름, 정규식) — SKILL.md "민감 정보 제거" 규칙과 동일 패턴 + 보강.
# 순서 주의: 더 구체적인 패턴(Bearer 토큰 등)을 일반 패턴보다 먼저 둔다.
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("openai_key", re.compile(r"sk-[A-Za-z0-9_-]{16,}")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{16,}")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("slack_token", re.compile(r"xox[bpoas]-[A-Za-z0-9-]{10,}")),
    ("bearer", re.compile(r"Bearer\s+[A-Za-z0-9._\-]+")),
    ("password_kv", re.compile(r"(?i)(password|passwd|pwd|secret|token)\s*[=:]\s*\S+")),
    ("email", re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")),
    ("krn_rrn", re.compile(r"\b\d{6}-\d{7}\b")),  # 한국 주민등록번호 형태
]


def redact(text: str) -> tuple[str, int]:
    """text를 정제하고 (정제본, 총 치환 건수)를 돌려준다."""
    total = 0
    for _name, pat in PATTERNS:
        text, n = pat.subn(REPLACEMENT, text)
        total += n
    return text, total


def count(text: str) -> int:
    """치환하지 않고 매칭 건수만 센다(--check)."""
    return sum(len(pat.findall(text)) for _name, pat in PATTERNS)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="handoff 민감 정보 [REDACTED] 치환기")
    parser.add_argument("files", nargs="*", help="입력 파일들 (생략 시 표준입력)")
    parser.add_argument("--check", action="store_true",
                        help="치환 없이 탐지 건수만 보고")
    args = parser.parse_args(argv)

    if args.files:
        text = "".join(open(f, encoding="utf-8").read() for f in args.files)
    else:
        text = sys.stdin.read()

    if args.check:
        n = count(text)
        print(f"민감 정보 {n}건 탐지", file=sys.stderr)
        return 1 if n else 0

    cleaned, n = redact(text)
    sys.stdout.write(cleaned)
    print(f"민감 정보 {n}건 처리", file=sys.stderr)
    return 1 if n else 0


if __name__ == "__main__":
    raise SystemExit(main())
