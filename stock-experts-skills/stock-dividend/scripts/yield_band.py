"""배당 계산기 — 역사적 수익률 밴드·배당 안전성. (표준 라이브러리만)

사용: python yield_band.py             # 데모
임포트: from yield_band import yield_band_position, dividend_safety
"""


def yield_band_position(yearly_high_yields, yearly_low_yields, current_yield, band_pct=0.10):
    """역사적 배당수익률 밴드에서 현재 위치 판정.

    입력: 최근 10년 내외의 '연도별 최고 수익률(=주가 저점)'과 '연도별 최저 수익률(=주가 고점)' 리스트.
    Weiss 규칙: 역사적 고수익률의 ±10% 범위 진입 = 저평가(매수), 저수익률 ±10% = 고평가(매도).
    """
    band_high = sum(yearly_high_yields) / len(yearly_high_yields)   # 평균 고수익률(저평가선)
    band_low = sum(yearly_low_yields) / len(yearly_low_yields)      # 평균 저수익률(고평가선)
    if current_yield >= band_high * (1 - band_pct):
        zone = "저평가(매수 구간)"
    elif current_yield <= band_low * (1 + band_pct):
        zone = "고평가(매도 구간)"
    else:
        zone = "중립(보유)"
    return {"밴드 고(저평가선)%": round(band_high, 2), "밴드 저(고평가선)%": round(band_low, 2),
            "현재%": current_yield, "판정": zone}


def dividend_safety(dps_total, net_income, fcf, net_debt, ebit, interest_expense):
    """배당 안전성 3종: payout(이익 대비) / FCF 커버리지 / 이자보상배율."""
    payout = dps_total / net_income if net_income > 0 else None
    fcf_cover = fcf / dps_total if dps_total > 0 else None
    icr = ebit / interest_expense if interest_expense > 0 else None
    flags = []
    if payout is None or payout > 0.8:
        flags.append("payout 과다(>80%) 또는 적자 — 삭감 위험")
    if fcf_cover is not None and fcf_cover < 1.2:
        flags.append("FCF 커버리지 부족(<1.2x)")
    if icr is not None and icr < 3:
        flags.append("이자보상 취약(<3x)")
    return {"payout": None if payout is None else round(payout, 2),
            "FCF커버리지x": None if fcf_cover is None else round(fcf_cover, 2),
            "이자보상x": None if icr is None else round(icr, 1),
            "경고": flags or ["없음"]}


if __name__ == "__main__":
    print("== 데모: (가상) F금융지주 ==")
    print(yield_band_position(
        yearly_high_yields=[5.8, 6.1, 5.9, 6.3, 6.0], yearly_low_yields=[3.4, 3.6, 3.5, 3.7, 3.3],
        current_yield=6.2))
    print(dividend_safety(dps_total=2800, net_income=10000, fcf=9000, net_debt=5000,
                          ebit=13000, interest_expense=2000))
