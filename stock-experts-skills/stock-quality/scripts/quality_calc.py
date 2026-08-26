"""퀄리티 계산기 — ROIC·owner's earnings·ROIC-WACC 스프레드·내재가치(영구성장). (표준 라이브러리만)

사용: python quality_calc.py           # 데모
임포트: from quality_calc import roic, owner_earnings, intrinsic_perpetuity
"""


def roic(nopat, invested_capital):
    """ROIC = NOPAT / 투하자본.

    NOPAT = 영업이익 x (1 - 실효세율).
    투하자본 = 순운전자본 + 순유형자산 (또는 자기자본 + 순차입금).
    """
    return nopat / invested_capital


def owner_earnings(net_income, dep_amort, maint_capex, wc_increase):
    """Owner's Earnings = 순이익 + 감가상각 - 유지보수CapEx - 운전자본 증가."""
    return net_income + dep_amort - maint_capex - wc_increase


def spread(roic_val, wacc):
    """초과수익 스프레드. 양(+)이 7~10년 지속돼야 해자로 인정."""
    return roic_val - wacc


def intrinsic_perpetuity(oe, growth, discount):
    """내재가치(영구성장 모델) = OE x (1+g) / (r - g).

    주의: g >= r이면 무의미. g는 보수적으로(장기 명목성장 수준 이하).
    정밀 평가는 stock-deepvalue references/valuation-methods.md의 DCF/역DCF 사용.
    """
    if growth >= discount:
        return None
    return oe * (1 + growth) / (discount - growth)


if __name__ == "__main__":
    print("== 데모: (가상) B소비재, 단위 억원 ==")
    r = roic(nopat=540, invested_capital=3000)
    print(f"ROIC {r*100:.1f}% vs WACC 8.0% -> 스프레드 {spread(r, 0.08)*100:+.1f}%p")
    oe = owner_earnings(net_income=500, dep_amort=120, maint_capex=90, wc_increase=30)
    print("Owner's Earnings:", oe, "억원")
    iv = intrinsic_perpetuity(oe, growth=0.03, discount=0.09)
    print(f"내재가치(g3%·r9%): {iv:,.0f}억원 | 시총 6,200억이면 MOS {((iv-6200)/iv)*100:+.1f}%")
