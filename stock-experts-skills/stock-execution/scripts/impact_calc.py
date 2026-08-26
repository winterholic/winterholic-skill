"""실행 비용 계산 — 제곱근 법칙 시장충격·분할 스케줄·IS 분해. (표준 라이브러리만)

사용: python impact_calc.py            # 데모
임포트: from impact_calc import sqrt_impact_bp, pov_schedule, is_decompose
"""
import math


def sqrt_impact_bp(daily_vol_pct, q_over_adv, Y=1.0):
    """제곱근 법칙: 충격 ≈ Y x 일변동성 x sqrt(주문량/ADV).

    Y는 시장·종목별 보정계수(0.5~1.5, 실측 TCA로 보정). 반환: bp.
    """
    return Y * daily_vol_pct * math.sqrt(q_over_adv) * 100


def pov_schedule(order_qty, adv, pov=0.10):
    """참여율(POV) 기반 분할: 소요 일수와 일별 수량."""
    daily = adv * pov
    days = math.ceil(order_qty / daily)
    return {"일별수량": int(daily), "소요일수": days,
            "권고": "소형주·유동성 절벽은 POV 5~8%로 보수적으로"}


def is_decompose(decision_price, avg_fill_price, filled_ratio, final_price, side="buy"):
    """Implementation Shortfall 분해(bp): 체결비용 + 미체결 기회비용.

    체결비용 = (체결가-결정가)/결정가, 기회비용 = 미체결분 x (최종가-결정가)/결정가.
    """
    sgn = 1 if side == "buy" else -1
    trading = sgn * (avg_fill_price - decision_price) / decision_price * filled_ratio
    opportunity = sgn * (final_price - decision_price) / decision_price * (1 - filled_ratio)
    return {"체결비용bp": round(trading * 1e4, 1), "기회비용bp": round(opportunity * 1e4, 1),
            "IS합계bp": round((trading + opportunity) * 1e4, 1)}


if __name__ == "__main__":
    print("== 데모: ADV 25% 매수주문, 일변동성 2% ==")
    print(f"한 번에 체결 시 충격 추정: {sqrt_impact_bp(2.0, 0.25):.0f}bp")
    print(f"3일 분할(일 8.3%) 시: {sqrt_impact_bp(2.0, 0.083):.0f}bp/일")
    print(pov_schedule(order_qty=500_000, adv=2_000_000, pov=0.08))
    print(is_decompose(decision_price=10000, avg_fill_price=10035, filled_ratio=0.95, final_price=10120))
