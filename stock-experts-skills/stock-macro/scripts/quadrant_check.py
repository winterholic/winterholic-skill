"""매크로 사분면 판정 — 성장x인플레 지표 입력 -> 4계절 + 자산 매핑. (표준 라이브러리만)

사용: python quadrant_check.py         # 데모
임포트: from quadrant_check import quadrant
"""

ASSET_MAP = {
    ("up", "up"): ["원자재", "물가채", "이머징채"],
    ("up", "down"): ["주식", "국채"],
    ("down", "up"): ["원자재", "물가채", "금", "현금"],
    ("down", "down"): ["국채", "물가채", "현금"],
}


def quadrant(pmi, pmi_3m_delta, cpi_yoy, cpi_3m_trend):
    """판정 임계: 성장 = PMI 50 기준 + 3개월 방향 / 인플레 = CPI YoY 3개월 추세.

    PMI>50이면서 상승 또는 PMI<50이지만 뚜렷이 반등(+1.5p)이면 성장 up.
    cpi_3m_trend: 최근 3개월 CPI YoY 변화(%p). +0.2p 이상이면 인플레 up.
    """
    growth = "up" if (pmi > 50 and pmi_3m_delta >= 0) or (pmi <= 50 and pmi_3m_delta >= 1.5) else "down"
    inflation = "up" if cpi_3m_trend >= 0.2 else "down"
    return {
        "사분면": f"성장{'↑' if growth == 'up' else '↓'} x 인플레{'↑' if inflation == 'up' else '↓'}",
        "수혜 자산": ASSET_MAP[(growth, inflation)],
        "근거": f"PMI {pmi}({pmi_3m_delta:+.1f}p/3m), CPI YoY 추세 {cpi_3m_trend:+.1f}%p/3m",
        "주의": "2022형(주식·채권 동반 하락) 레짐이면 금·현금·실물 보강. 판정은 지표 2개 이상 교차확인.",
    }


if __name__ == "__main__":
    print("== 데모 ==")
    print(quadrant(pmi=47.5, pmi_3m_delta=-1.2, cpi_yoy=2.1, cpi_3m_trend=-0.4))
    print(quadrant(pmi=53.0, pmi_3m_delta=+0.8, cpi_yoy=3.8, cpi_3m_trend=+0.5))
