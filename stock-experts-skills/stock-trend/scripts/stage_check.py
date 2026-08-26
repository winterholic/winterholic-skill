"""스테이지 체크 — 30주MA 기울기·주가 위치·돌파 거래량 배수·Mansfield RS. (표준 라이브러리만)

사용: python stage_check.py            # 데모
임포트: from stage_check import stage_check, mansfield_rs
입력: 주봉 종가·거래량 리스트(과거->최근), 최소 40주 권장.
"""


def _sma(xs, n):
    return [sum(xs[i - n + 1:i + 1]) / n for i in range(n - 1, len(xs))]


def stage_check(weekly_closes, weekly_volumes, ma_weeks=30, slope_lookback=4):
    """Stage 판정 보조: 30주MA 기울기 + 주가 위치 + 최근 거래량 배수."""
    if len(weekly_closes) < ma_weeks + slope_lookback:
        return {"오류": f"주봉 {ma_weeks + slope_lookback}개 이상 필요"}
    ma = _sma(weekly_closes, ma_weeks)
    slope_pct = (ma[-1] / ma[-1 - slope_lookback] - 1) * 100
    price_above = weekly_closes[-1] > ma[-1]
    avg_vol = sum(weekly_volumes[-14:-1]) / 13          # 직전 13주 평균
    vol_mult = weekly_volumes[-1] / avg_vol
    if abs(slope_pct) < 0.7:
        ma_state = "평탄(Stage 1 또는 3 후보)"
    elif slope_pct > 0:
        ma_state = "상향(Stage 2 후보)"
    else:
        ma_state = "하향(Stage 4 후보)"
    return {"30주MA": round(ma[-1], 1), f"MA기울기({slope_lookback}주)%": round(slope_pct, 2),
            "MA상태": ma_state, "주가>MA": price_above, "금주 거래량배수": round(vol_mult, 2),
            "돌파유효(거래량>1.4x)": vol_mult >= 1.4}


def mansfield_rs(stock_closes, index_closes, n=52):
    """Mansfield RS = (주가/지수 비율)을 n주 평균 대비 % 편차로. 0 위 + 상승이면 시장 대비 강세."""
    ratio = [s / i for s, i in zip(stock_closes, index_closes)]
    if len(ratio) < n + 4:
        return {"오류": f"{n + 4}개 이상 필요"}
    base = _sma(ratio, n)
    rs_now = (ratio[-1] / base[-1] - 1) * 100
    rs_prev = (ratio[-5] / base[-5] - 1) * 100 if len(base) >= 5 else None
    return {"RS(0선 기준)": round(rs_now, 2),
            "추세": "상승" if (rs_prev is not None and rs_now > rs_prev) else "하락/횡보"}


if __name__ == "__main__":
    import math
    print("== 데모: 합성 데이터(저점 횡보 -> 상승 전환) ==")
    closes = [100 + (0 if i < 40 else (i - 40) * 1.5) + math.sin(i) for i in range(60)]
    vols = [1000] * 59 + [1650]
    print(stage_check(closes, vols))
    idx = [200 + i * 0.3 for i in range(60)]
    print(mansfield_rs(closes, idx, n=40))
