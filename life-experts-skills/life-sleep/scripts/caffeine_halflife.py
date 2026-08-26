#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
caffeine_halflife.py — 카페인 반감기 기반 취침 시 체내 잔류 카페인 추정기

지수 감소 모델: C(t) = C0 * 0.5 ** (t / half_life)
- 반감기(half_life)는 개인차가 큼: NIH StatPearls 기준 평균 약 4~5시간, 범위 약 2~12시간(as-of 2026-06,
  출처 sources.md). 기본값 5~6h는 보수적 추정. 흡연·일부 약물은 단축, 임신·간기능 저하·경구피임약·일부 약물은 연장될 수 있음.
- 본 계산기는 의료 자문이 아니라 '대략의 감각'을 주기 위한 교육용 추정기다.

표준 라이브러리만 사용.

사용 예:
  python caffeine_halflife.py --doses "14:00=150,16:30=80" --bedtime 23:00
  python caffeine_halflife.py --doses "21:00=250" --bedtime 23:30 --halflife 6 --threshold 50
"""

import argparse
import sys
from datetime import datetime, timedelta

# Windows 콘솔(cp949)에서 한글/유니코드 출력 깨짐·에러 방지
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def parse_time(s: str) -> datetime:
    """HH:MM 문자열을 오늘 날짜 기준 datetime으로."""
    s = s.strip()
    hh, mm = s.split(":")
    base = datetime(2000, 1, 1)  # 날짜는 의미 없음, 시각 차이만 사용
    return base.replace(hour=int(hh), minute=int(mm))


def parse_doses(s: str):
    """'14:00=150,16:30=80' -> [(datetime, 150.0), ...]"""
    out = []
    for chunk in s.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        t_str, mg_str = chunk.split("=")
        out.append((parse_time(t_str), float(mg_str)))
    return out


def remaining_at(doses, when: datetime, half_life_h: float) -> float:
    """when 시각에 남아있는 총 카페인(mg) 추정. 섭취 이후 시간만 감소 적용."""
    total = 0.0
    for t, mg in doses:
        delta = when - t
        # 자정을 넘긴 취침(예: 02:00)은 음수가 되므로 +24h 보정
        hours = delta.total_seconds() / 3600.0
        if hours < 0:
            hours += 24.0
        total += mg * (0.5 ** (hours / half_life_h))
    return total


def cutoff_time(bedtime: datetime, threshold_mg: float, half_life_h: float, dose_mg: float) -> datetime:
    """단일 dose_mg 한 잔이 취침 시 threshold_mg 이하가 되려면 늦어도 언제 마셔야 하나."""
    if dose_mg <= threshold_mg:
        return bedtime  # 한 잔 자체가 이미 임계 이하면 컷오프 의미 없음
    # threshold = dose * 0.5**(h/half) -> h = half * log2(dose/threshold)
    import math
    hours_needed = half_life_h * math.log2(dose_mg / threshold_mg)
    return bedtime - timedelta(hours=hours_needed)


def fmt(dt: datetime) -> str:
    return dt.strftime("%H:%M")


def main():
    ap = argparse.ArgumentParser(description="카페인 반감기 기반 취침 시 잔류 카페인 추정")
    ap.add_argument("--doses", required=True,
                    help='섭취 기록 "HH:MM=mg,HH:MM=mg" 예: "14:00=150,16:30=80"')
    ap.add_argument("--bedtime", required=True, help="취침 시각 HH:MM")
    ap.add_argument("--halflife", type=float, default=5.5,
                    help="카페인 반감기(시간), 기본 5.5 (약 5~6시간, 확인 필요)")
    ap.add_argument("--threshold", type=float, default=50.0,
                    help="취침 시 권고 잔류 상한(mg), 기본 50 (교육적 기준, 확인 필요)")
    ap.add_argument("--ref-dose", type=float, default=150.0,
                    help="컷오프 계산용 기준 한 잔 용량(mg), 기본 150 (드립커피 1잔 가정)")
    args = ap.parse_args()

    doses = parse_doses(args.doses)
    bedtime = parse_time(args.bedtime)

    total_at_bed = remaining_at(doses, bedtime, args.halflife)
    total_intake = sum(mg for _, mg in doses)

    print("=" * 56)
    print(" 카페인 잔류 추정 (지수 감소 모델, 교육용 — 의료 자문 아님)")
    print("=" * 56)
    print(f" 반감기 가정      : {args.halflife} 시간 (약 5~6시간, 확인 필요)")
    print(f" 취침 시각        : {fmt(bedtime)}")
    print(f" 총 섭취량        : {total_intake:.0f} mg")
    print("-" * 56)
    print(" 섭취 내역별 취침 시 잔류:")
    for t, mg in doses:
        r = remaining_at([(t, mg)], bedtime, args.halflife)
        print(f"   {fmt(t)}  {mg:>5.0f} mg  ->  취침 시 {r:>6.1f} mg")
    print("-" * 56)
    print(f" 취침 시 총 잔류량: {total_at_bed:.1f} mg")
    print(f" 권고 상한        : {args.threshold:.0f} mg")
    if total_at_bed > args.threshold:
        print(f" 판정            : 초과 (+{total_at_bed - args.threshold:.1f} mg) — 수면 방해 가능")
    else:
        print(f" 판정            : 상한 이하 — 비교적 양호")
    print("-" * 56)
    co = cutoff_time(bedtime, args.threshold, args.halflife, args.ref_dose)
    print(f" 권고 컷오프      : 한 잔({args.ref_dose:.0f}mg) 기준, {fmt(co)} 이후 카페인 자제")
    print(f"   (취침 {((bedtime - co).total_seconds()/3600.0):.1f}시간 전까지)")
    print("=" * 56)
    print(" * 반감기는 개인차가 큽니다(흡연 단축 / 임신·일부약물 연장).")
    print(" * 불면이 2주+ 지속되면 수면클리닉/의사 상담을 권합니다.")


if __name__ == "__main__":
    main()
