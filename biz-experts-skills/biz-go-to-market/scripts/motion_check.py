#!/usr/bin/env python3
"""GTM 모션 선택 + 단위경제 게이트 판정기.

5축(각 'plg'/'slg')의 다수결로 모션을 추천하고, 단위경제(LTV vs CAC)로
그 모션이 지속 가능한지 게이트를 건다. 저가 제품에 SLG를 붙이면
CAC가 LTV를 초과해 팔수록 손실(안티패턴 1)임을 숫자로 드러낸다.

사용:
    python motion_check.py                 # 데모
    python motion_check.py gtm.json        # JSON 입력

JSON 형식:
    {
      "axes": {"price":"plg","complexity":"plg","buyer":"plg",
               "contract":"plg","time_to_value":"slg"},
      "arpu_month": 30, "expected_months": 24, "cac": 900
    }
    - axes 각 값: "plg" 또는 "slg" (5개 축)
    - 단위경제 필드는 선택(있으면 게이트 판정)
"""
import json
import sys

AXES = ("price", "complexity", "buyer", "contract", "time_to_value")


def recommend_motion(axes):
    plg = sum(1 for a in AXES if axes.get(a) == "plg")
    slg = sum(1 for a in AXES if axes.get(a) == "slg")
    if plg >= 3:
        return "PLG 주도", plg, slg
    if slg >= 3:
        return "SLG 주도", plg, slg
    return "하이브리드(PLG 유입 → 세일즈 확장)", plg, slg


def unit_economics(p):
    arpu = p.get("arpu_month")
    months = p.get("expected_months")
    cac = p.get("cac")
    if arpu is None or months is None or cac is None:
        return None
    ltv = arpu * months
    ratio = ltv / cac if cac else float("inf")
    ok = ratio >= 3.0  # 통상 LTV:CAC >= 3 목표(참고치)
    return ltv, cac, ratio, ok


def run(p):
    axes = p.get("axes", {})
    motion, plg, slg = recommend_motion(axes)
    print("=== GTM 모션 판정 ===")
    print(f"  축 다수결: PLG {plg} / SLG {slg}")
    print(f"  추천 모션: {motion}")
    ue = unit_economics(p)
    if ue:
        ltv, cac, ratio, ok = ue
        print(f"\n  단위경제 게이트: LTV {ltv:.0f} / CAC {cac:.0f} = {ratio:.1f}x")
        if ok:
            print("  ✅ LTV:CAC >= 3 — 모션 채택 가능")
        else:
            print("  ⚠️ LTV:CAC < 3 — 이 모션은 팔수록 손실 위험(저가에 SLG?). "
                  "모션 재검토 또는 CAC 절감 필요.")
    else:
        print("\n  (단위경제 미입력 — arpu_month·expected_months·cac 넣으면 게이트 판정)")
    print("\n※ 정밀 CAC/LTV·코호트 계산은 → biz-finance-fpa.")


# 데모: $30 저가 제품인데 time_to_value만 SLG쪽 → PLG 주도, 그러나 CAC 900이면 게이트 실패
DEMO = {
    "axes": {"price": "plg", "complexity": "plg", "buyer": "plg",
             "contract": "plg", "time_to_value": "slg"},
    "arpu_month": 30, "expected_months": 24, "cac": 900,
}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            run(json.load(f))
    else:
        run(DEMO)
