#!/usr/bin/env python3
"""여행 경비 대략 추정기 (life-travel).

항목별 + 예비비로 분해해 '뭉뚱그린 총액'의 누수를 막는 감 잡기용.
1일 단가 × 일수 + 고정비(항공) 구조. 단가·환율은 직접 보정(확인 필요).
표준 라이브러리만 사용.

사용:
    python travel_budget.py --days 4 --people 2 \
        --air 35 --lodging-per-night 12 --food-per-day 6 \
        --transport-per-day 3 --activity 10 --misc-per-day 2
"""
from __future__ import annotations

import argparse

RESERVE_RATE = 0.12  # 예비비 비율(10~15% 권장 중간값)


def estimate(a: argparse.Namespace) -> dict:
    nights = max(0, a.days - 1)
    per_person = {
        "항공(왕복)": a.air,
        "숙소": a.lodging_per_night * nights / max(1, a.people),  # 객실 분담 가정
        "식비": a.food_per_day * a.days,
        "현지교통": a.transport_per_day * a.days,
        "입장/액티비티": a.activity,
        "통신/기타": a.misc_per_day * a.days,
    }
    subtotal_pp = sum(per_person.values())
    reserve_pp = subtotal_pp * RESERVE_RATE
    total_pp = subtotal_pp + reserve_pp
    total_group = total_pp * a.people
    return {
        "per_person_items": {k: round(v, 1) for k, v in per_person.items()},
        "reserve_pp": round(reserve_pp, 1),
        "total_per_person": round(total_pp, 1),
        "total_group": round(total_group, 1),
        "people": a.people,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="여행 경비 대략 추정 (만원, 1인 기준 항목)")
    p.add_argument("--days", type=int, required=True, help="총 여행 일수")
    p.add_argument("--people", type=int, default=1, help="인원")
    p.add_argument("--air", type=float, default=0, help="항공 왕복(1인, 만원)")
    p.add_argument("--lodging-per-night", type=float, default=0,
                   help="1박 숙소비(객실 기준, 만원) — 인원으로 분담")
    p.add_argument("--food-per-day", type=float, default=0, help="1일 식비(1인)")
    p.add_argument("--transport-per-day", type=float, default=0, help="1일 현지교통(1인)")
    p.add_argument("--activity", type=float, default=0, help="입장/액티비티 총액(1인)")
    p.add_argument("--misc-per-day", type=float, default=0, help="1일 통신/기타(1인)")
    a = p.parse_args()

    r = estimate(a)
    print(f"=== 여행 경비 추정 ({a.days}일 / {a.people}인, 만원, 확인 필요) ===")
    print("[1인 기준 항목]")
    for k, v in r["per_person_items"].items():
        print(f"  {k:<14}: {v:>6.1f}")
    print(f"  {'예비비(12%)':<14}: {r['reserve_pp']:>6.1f}")
    print(f"  {'1인 합계':<14}: {r['total_per_person']:>6.1f}")
    print(f"\n[총 {a.people}인 합계]: {r['total_group']:.1f} 만원")
    print("\n※ 단가·환율은 예시 - 항공/숙소 실시세, 환율로 보정하세요.")
    print("※ 항목별 분해 + 예비비가 '뭉뚱그린 총액'의 누수를 막습니다.")


if __name__ == "__main__":
    main()
