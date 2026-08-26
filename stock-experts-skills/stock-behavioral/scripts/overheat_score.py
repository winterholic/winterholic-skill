"""과열/공포 합성 점수 - 수급·심리 지표 백분위 입력 -> 진자 위치. (표준 라이브러리만)

사용: python overheat_score.py         # 데모
임포트: from overheat_score import overheat_score
입력: 각 지표의 '자국 역사 대비 백분위(0~100)'. 절대값 비교 금지(README·KRX 규칙).
"""

DEFAULT_WEIGHTS = {
    "신용융자잔고": 0.30,      # 높을수록 과열
    "거래대금": 0.20,
    "신고가종목비율": 0.15,
    "개인순매수강도": 0.20,
    "변동성지수_역순": 0.15,   # VIX/VKOSPI 낮음(=안일) -> 높은 백분위로 입력
}


def overheat_score(percentiles, weights=None):
    """가중 합성 0~100. 80+ 탐욕 정점(역발상 경계) / 20- 공포 정점(역발상 기회)."""
    w = weights or DEFAULT_WEIGHTS
    used = {k: v for k, v in percentiles.items() if k in w}
    tot_w = sum(w[k] for k in used)
    score = sum(percentiles[k] * w[k] for k in used) / tot_w
    if score >= 80:
        zone = "탐욕 정점 - 추격 금지, 사전규칙 점검, 역발상 매도 후보"
    elif score >= 60:
        zone = "탐욕 우위 - 신규 진입 보수적으로"
    elif score > 40:
        zone = "중립"
    elif score > 20:
        zone = "공포 우위 - 관심 종목 분할 접근 검토"
    else:
        zone = "공포 정점 - 역발상 매수 후보(단 사이징은 portfolio-risk)"
    return {"점수": round(score, 1), "진자 위치": zone, "사용 지표": list(used)}


if __name__ == "__main__":
    print("== 데모: (가상) 과열 국면 ==")
    print(overheat_score({"신용융자잔고": 97, "거래대금": 90, "신고가종목비율": 85,
                          "개인순매수강도": 92, "변동성지수_역순": 80}))
