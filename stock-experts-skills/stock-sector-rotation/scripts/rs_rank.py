"""섹터 상대강도 랭킹 — RS-Ratio·RS-Momentum 단순화 버전. (표준 라이브러리만)

사용: python rs_rank.py                # 데모
임포트: from rs_rank import rs_rank
입력: {섹터명: 종가 리스트}, 벤치마크 종가 리스트 (같은 길이, 일/주 단위 동일).
"""


def rs_rank(sectors, benchmark, ratio_window=50, mom_window=10):
    """RS-Ratio = (섹터/벤치 비율)의 현재값/이동평균 x 100. >100이면 시장 대비 강세.
    RS-Momentum = RS-Ratio의 mom_window 기간 변화율. 둘 다 양이면 'Leading'."""
    out = []
    for name, closes in sectors.items():
        ratio = [c / b for c, b in zip(closes, benchmark)]
        ma = sum(ratio[-ratio_window:]) / ratio_window
        rs_now = ratio[-1] / ma * 100
        ma_prev = sum(ratio[-ratio_window - mom_window:-mom_window]) / ratio_window
        rs_prev = ratio[-1 - mom_window] / ma_prev * 100
        mom = rs_now - rs_prev
        if rs_now > 100 and mom > 0:
            phase = "Leading(강세 지속)"
        elif rs_now > 100:
            phase = "Weakening(강세 약화)"
        elif mom > 0:
            phase = "Improving(개선)"
        else:
            phase = "Lagging(약세)"
        out.append({"섹터": name, "RS-Ratio": round(rs_now, 1), "RS-Mom": round(mom, 2), "국면": phase})
    return sorted(out, key=lambda r: -r["RS-Ratio"])


if __name__ == "__main__":
    print("== 데모: 합성 3섹터 (80일) ==")
    bench = [100 + i * 0.1 for i in range(80)]
    sectors = {
        "에너지": [100 + i * 0.30 for i in range(80)],
        "IT": [100 + i * 0.10 for i in range(80)],
        "필수소비재": [100 + i * 0.02 for i in range(80)],
    }
    for row in rs_rank(sectors, bench):
        print(row)
