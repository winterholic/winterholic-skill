#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calorie_macro.py — TDEE / 목표 칼로리 / 매크로(단백질·탄수·지방) 개략 계산기

근거(확인 필요):
- BMR: Mifflin-St Jeor 공식 (1990) — 임상에서 널리 쓰는 추정식, 오차 ±10% 수준
- 활동계수(PAL): 통상 1.2~1.9 범위 (좌식~고강도)
- 단백질 권장: 체중당 g/kg (감량/유지/근증가 목적별 차등) — 출처: ISSN position stand 등, 확인 필요
- 1kg 체지방 ≈ 약 7700kcal (경험칙, 확인 필요)

주의: 추정 도구일 뿐 진단·처방이 아니다. 기저질환·극단적 식이는 의사/임상영양사 상담.
표준 라이브러리만 사용.
"""

import sys
from dataclasses import dataclass

# Windows 콘솔(cp949) 환경에서도 한글/em-dash가 깨지지 않도록 UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 활동계수 (PAL) — 라벨: 배수 (확인 필요, 통상 범위)
ACTIVITY = {
    "좌식":       1.2,   # 거의 운동 안 함, 사무직
    "가벼움":     1.375, # 주 1~3회 가벼운 운동
    "보통":       1.55,  # 주 3~5회 운동
    "활발":       1.725, # 주 6~7회 강한 운동
    "매우활발":   1.9,   # 육체노동 + 하루 2회 운동 등
}

# 목표별 단백질 권장 (g/kg 체중) — 운동영양 목적별 차등(감량 시 근손실 방어 위해 고단백).
# 일반 유지 RDA는 한국인 영양소 섭취기준 ≈0.91 g/kg과 별개 개념. 출처: ISSN/Morton(2018), 확인 필요
PROTEIN_PER_KG = {
    "감량":   2.0,   # 칼로리 적자 중 근손실 방어 (고단백)
    "유지":   1.6,
    "근증가": 1.8,   # 벌크업
}

# 목표별 칼로리 조정 비율 (TDEE 대비)
GOAL_ADJUST = {
    "감량":   -0.15,  # -15% (완만한 적자 권장, 극단 금지)
    "유지":    0.0,
    "근증가": +0.10,  # +10% (린벌크)
}

KCAL_PER_G = {"protein": 4, "carb": 4, "fat": 9}
KCAL_PER_KG_FAT = 7700  # 1kg 체지방 환산 (경험칙, 확인 필요)


@dataclass
class Profile:
    sex: str          # "남" / "여"
    age: int          # 세
    height_cm: float
    weight_kg: float
    activity: str     # ACTIVITY 키
    goal: str         # GOAL_ADJUST 키


def bmr_mifflin(p: Profile) -> float:
    """Mifflin-St Jeor 기초대사량(kcal/day)."""
    base = 10 * p.weight_kg + 6.25 * p.height_cm - 5 * p.age
    if p.sex == "남":
        return base + 5
    elif p.sex == "여":
        return base - 161
    raise ValueError("sex는 '남' 또는 '여'")


def tdee(p: Profile) -> float:
    if p.activity not in ACTIVITY:
        raise ValueError(f"activity는 {list(ACTIVITY)} 중 하나")
    return bmr_mifflin(p) * ACTIVITY[p.activity]


def target_calories(p: Profile) -> float:
    if p.goal not in GOAL_ADJUST:
        raise ValueError(f"goal은 {list(GOAL_ADJUST)} 중 하나")
    return tdee(p) * (1 + GOAL_ADJUST[p.goal])


def macros(p: Profile):
    """단백질 우선 배분 → 지방 25% → 나머지 탄수.
    반환: dict(g, kcal, %)
    """
    cal = target_calories(p)
    protein_g = PROTEIN_PER_KG[p.goal] * p.weight_kg
    protein_kcal = protein_g * KCAL_PER_G["protein"]

    fat_kcal = cal * 0.25            # 지방 25% (총칼로리 비율, 통상 20~35%)
    fat_g = fat_kcal / KCAL_PER_G["fat"]

    carb_kcal = cal - protein_kcal - fat_kcal
    carb_g = max(carb_kcal, 0) / KCAL_PER_G["carb"]

    def row(g, kcal):
        return {"g": round(g, 1), "kcal": round(kcal), "pct": round(kcal / cal * 100, 1)}

    return {
        "protein": row(protein_g, protein_kcal),
        "fat": row(fat_g, fat_kcal),
        "carb": row(carb_g, carb_kcal),
    }


def weekly_weight_change_kg(p: Profile) -> float:
    """목표 칼로리 기준 주간 예상 체중변화(kg, 음수=감량). 경험칙."""
    daily_delta = target_calories(p) - tdee(p)
    return daily_delta * 7 / KCAL_PER_KG_FAT


SAFE_WEEKLY_LOSS = (-1.0, 0.0)  # 권장 주간 감량 상한 ≈ 체중 0.5~1%/주, 확인 필요


def report(p: Profile) -> str:
    bmr = bmr_mifflin(p)
    td = tdee(p)
    tc = target_calories(p)
    m = macros(p)
    wk = weekly_weight_change_kg(p)

    lines = []
    lines.append("=" * 52)
    lines.append(f"입력: {p.sex} {p.age}세 {p.height_cm}cm {p.weight_kg}kg "
                 f"활동={p.activity} 목표={p.goal}")
    lines.append("-" * 52)
    lines.append(f"BMR(기초대사량, Mifflin-St Jeor): {bmr:.0f} kcal/day")
    lines.append(f"TDEE(총소비, x{ACTIVITY[p.activity]}):     {td:.0f} kcal/day")
    lines.append(f"목표 칼로리({p.goal} {GOAL_ADJUST[p.goal]*100:+.0f}%): {tc:.0f} kcal/day")
    lines.append("-" * 52)
    lines.append(f"단백질: {m['protein']['g']:>5}g  {m['protein']['kcal']:>4}kcal  "
                 f"({m['protein']['pct']}%)  [{PROTEIN_PER_KG[p.goal]}g/kg]")
    lines.append(f"탄수화물: {m['carb']['g']:>5}g  {m['carb']['kcal']:>4}kcal  ({m['carb']['pct']}%)")
    lines.append(f"지방:   {m['fat']['g']:>5}g  {m['fat']['kcal']:>4}kcal  ({m['fat']['pct']}%)")
    lines.append("-" * 52)
    lines.append(f"예상 주간 체중변화: {wk:+.2f} kg/주 (체지방 7700kcal 환산, 경험칙)")
    lo, hi = SAFE_WEEKLY_LOSS
    if wk < lo:
        lines.append(f"  [경고] 주 {abs(wk):.2f}kg 감량은 권장 상한(≈1kg/주)을 초과 — "
                     f"근손실·요요·건강 위험. 적자를 완화하세요.")
    lines.append("=" * 52)
    lines.append("주의: 추정값이며 진단·처방이 아닙니다. 모든 계수는 '확인 필요'.")
    lines.append("기저질환(당뇨·신장질환 등)·극단적 식이는 의사/임상영양사 상담.")
    return "\n".join(lines)


def _demo():
    print("[데모 1] 감량 목표 — 남 30세 175cm 80kg, 보통 활동")
    print(report(Profile("남", 30, 175, 80, "보통", "감량")))
    print()
    print("[데모 2] 근증가(벌크업) — 여 27세 162cm 55kg, 활발 활동")
    print(report(Profile("여", 27, 162, 55, "활발", "근증가")))
    print()
    print("[데모 3] 위험 케이스 — 좌식인데 극단 적자 흉내(저체중 무리 감량 경고 확인)")
    # 좌식 + 감량이라도 -15%면 안전 범위. 위험은 사용자가 임의로 더 줄일 때 발생함을 설명용으로
    p = Profile("여", 22, 165, 48, "좌식", "감량")
    print(report(p))


if __name__ == "__main__":
    _demo()
