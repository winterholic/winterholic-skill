#!/usr/bin/env python3
"""이사 비용 대략 추정기 (life-moving).

전화 견적 미끼를 거르기 위한 '감 잡기'용 추정이다. 실제 금액은
방문/영상 견적으로 보정해야 하며, 아래 단가는 예시 기본값(확인 필요)이다.
표준 라이브러리만 사용.

사용:
    python moving_cost.py --type pack --rooms 2 --floor 5 --no-elevator \
        --ac 1 --waste 1
    python moving_cost.py --type van --rooms 1
"""
from __future__ import annotations

import argparse

# 예시 기본 단가(만원) — 지역·성수기·짐 양에 따라 크게 변동, 반드시 실견적으로 보정(확인 필요)
BASE_BY_TYPE = {
    "pack": {0: 35, 1: 55, 2: 85, 3: 120},   # 포장이사
    "semi": {0: 25, 1: 40, 2: 60, 3: 85},    # 반포장
    "van": {0: 15, 1: 22, 2: 35, 3: 50},     # 용달/일반
}
LADDER_COST = 12        # 사다리차(엘리베이터 없는 고층)
AC_COST = 10            # 에어컨 1대 분리+설치
WASTE_COST = 8          # 대형 폐기물 처리(건당)
PEAK_MULT = 1.20        # 성수기/주말/손없는날 가산


def estimate(args: argparse.Namespace) -> dict:
    table = BASE_BY_TYPE[args.type]
    rooms = max(0, min(args.rooms, 3))
    base = table[rooms]

    add = 0.0
    breakdown = {"기본": float(base)}

    # 엘리베이터 없고 3층 이상이면 사다리차 가정
    if args.no_elevator and args.floor >= 3:
        add += LADDER_COST
        breakdown["사다리차"] = float(LADDER_COST)

    if args.ac:
        c = AC_COST * args.ac
        add += c
        breakdown[f"에어컨x{args.ac}"] = float(c)

    if args.waste:
        c = WASTE_COST * args.waste
        add += c
        breakdown[f"폐기물x{args.waste}"] = float(c)

    subtotal = base + add
    total = subtotal * (PEAK_MULT if args.peak else 1.0)
    if args.peak:
        breakdown["성수기가산"] = round(total - subtotal, 1)

    return {"breakdown": breakdown, "total_manwon": round(total, 1)}


def main() -> None:
    p = argparse.ArgumentParser(description="이사 비용 대략 추정 (감 잡기용)")
    p.add_argument("--type", choices=["pack", "semi", "van"], default="semi",
                   help="pack=포장 semi=반포장 van=용달")
    p.add_argument("--rooms", type=int, default=1, help="방 수(0=원룸,최대3)")
    p.add_argument("--floor", type=int, default=1, help="새 집/현 집 중 높은 층")
    p.add_argument("--no-elevator", action="store_true", help="엘리베이터 없음")
    p.add_argument("--ac", type=int, default=0, help="에어컨 대수")
    p.add_argument("--waste", type=int, default=0, help="대형 폐기물 건수")
    p.add_argument("--peak", action="store_true", help="성수기/주말/손없는날")
    args = p.parse_args()

    r = estimate(args)
    print("=== 이사 비용 대략 추정 (만원, 확인 필요) ===")
    for k, v in r["breakdown"].items():
        print(f"  {k:<12}: {v:>6.1f}")
    print(f"  {'합계':<12}: {r['total_manwon']:>6.1f}")
    print("\n※ 예시 단가 기준 감 잡기용. 실제 금액은 방문/영상 견적으로 보정.")
    print("※ 항목별 견적서를 받아 '빠진 항목(사다리차/가전/폐기물)'을 확인하세요.")


if __name__ == "__main__":
    main()
