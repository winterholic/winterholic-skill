"""CAN SLIM 체크 — 정량 기준 판정 + base 깊이 + 진입/손절 가격. (표준 라이브러리만)

사용: python canslim_check.py          # 데모
임포트: from canslim_check import canslim_quant, base_and_stops
"""


def canslim_quant(eps_qoq_yoy_pct, sales_yoy_pct, eps_3y_cagr_pct, roe_pct, rs_percentile):
    """정량 4기준(C·A·L) 판정. S/I/M·N은 정성 — 별도 확인."""
    checks = {
        "C: 분기EPS YoY >= +25%": eps_qoq_yoy_pct >= 25,
        "C보강: 매출 YoY >= +25%": sales_yoy_pct >= 25,
        "A: 3년 EPS CAGR >= +25%": eps_3y_cagr_pct >= 25,
        "A보강: ROE >= 17%": roe_pct >= 17,
        "L: RS 백분위 >= 80": rs_percentile >= 80,
    }
    passed = sum(checks.values())
    return {"체크": checks, "통과": f"{passed}/5",
            "비고": "S(수급)·I(기관)·N(신고가/변화)·M(시장)은 정성 확인 필수"}


def base_and_stops(base_high, base_low, entry=None, stop_pct=0.075):
    """base 깊이(정상 12~33%) + pivot 진입가 + -7~8% 손절가."""
    depth = (base_high - base_low) / base_high * 100
    pivot = base_high * 1.001          # 손잡이/박스 상단 +0.1% 부근
    entry = entry if entry is not None else pivot
    stop = entry * (1 - stop_pct)
    max_chase = pivot * 1.05           # pivot +5% 초과 추격 금지(extended)
    return {"base깊이%": round(depth, 1), "정상범위(12~33%)": 12 <= depth <= 33,
            "pivot": round(pivot, 0), "진입": round(entry, 0),
            "손절(-7.5%)": round(stop, 0), "추격한계(+5%)": round(max_chase, 0)}


if __name__ == "__main__":
    print("== 데모: (가상) H성장주 ==")
    print(canslim_quant(eps_qoq_yoy_pct=32, sales_yoy_pct=27, eps_3y_cagr_pct=28,
                        roe_pct=21, rs_percentile=88))
    print(base_and_stops(base_high=45200, base_low=36500))
