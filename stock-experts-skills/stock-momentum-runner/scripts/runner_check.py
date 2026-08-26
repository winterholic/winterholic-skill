"""stock-momentum-runner 계산기 — 미장 급등주(러너) 정량 판정.

표준 라이브러리만 사용. 데모: `python scripts/runner_check.py`
임포트: `from runner_check import rvol, float_rotation, dilution_risk, adr_stop_ok, size_by_risk, runner_grade`

모든 임계값은 출발점(heuristic)일 뿐 — 최신 실데이터로 재확인할 것.
"""


def rvol(today_volume, avg_daily_volume):
    """상대거래량(Relative Volume). 2배↑면 관심, 5배↑면 강한 관심."""
    if avg_daily_volume <= 0:
        raise ValueError("avg_daily_volume must be > 0")
    return today_volume / avg_daily_volume


def float_rotation(today_volume, float_shares):
    """플로트 로테이션 = 당일거래량 / 유통주식. 1회↑면 유통물량이 하루에 한 번 다 회전(과열·스퀴즈 신호)."""
    if float_shares <= 0:
        raise ValueError("float_shares must be > 0")
    return today_volume / float_shares


def dilution_risk(has_active_shelf_s3, atm_424b5_last_90d, reverse_split_last_12m,
                  cash_runway_quarters, warrants_overhang_pct):
    """희석 리스크 점수(0~100, 높을수록 위험). 급등주 최대 함정 = 회사가 고점에 물량을 찍어냄.

    - has_active_shelf_s3: 유효 S-3/F-3 선반등록 존재(장전된 총) → +25
    - atm_424b5_last_90d: 최근 90일 424B5/ATM 관련 filing 건수 → 건당 +12(최대 36)
    - reverse_split_last_12m: 최근 12개월 액면병합(생존 신호) → +20
    - cash_runway_quarters: 현금 소진까지 남은 분기(<2면 급전 필요) → <2:+15, <4:+8
    - warrants_overhang_pct: 워런트/전환사채 오버행(유통 대비 %) → pct*0.3(최대 20)
    """
    score = 0
    if has_active_shelf_s3:
        score += 25
    score += min(atm_424b5_last_90d * 12, 36)
    if reverse_split_last_12m:
        score += 20
    if cash_runway_quarters is not None:
        if cash_runway_quarters < 2:
            score += 15
        elif cash_runway_quarters < 4:
            score += 8
    score += min(warrants_overhang_pct * 0.3, 20)
    score = min(round(score), 100)
    band = "치명(회피/숏편향)" if score >= 60 else "높음(축소·빠른 회전)" if score >= 35 else "보통" if score >= 15 else "낮음"
    return {"dilution_score": score, "band": band}


def adr_stop_ok(entry, stop, adr_pct):
    """Qullamaggie 규율: 손절폭이 ADR(평균일중변동%)보다 넓으면 트레이드 스킵.

    반환: 손절폭%, 허용여부. stop은 당일 저가(LoD) 등 구조적 손절가.
    """
    if entry <= 0:
        raise ValueError("entry must be > 0")
    risk_pct = (entry - stop) / entry * 100
    return {"stop_risk_pct": round(risk_pct, 2), "adr_pct": adr_pct,
            "ok": risk_pct <= adr_pct, "reason": "손절폭 ≤ ADR" if risk_pct <= adr_pct else "손절폭 > ADR → 스킵"}


def size_by_risk(account, risk_per_trade_pct, entry, stop):
    """리스크 기반 사이징. 한 트레이드에 계좌의 risk_per_trade_pct(%)만 건다(급등주는 0.25~1% 권장).

    반환: 주문 주식수, 실제 위험금액. 급등주는 슬리피지·갭 위험이 커 사이즈를 작게.
    """
    per_share_risk = entry - stop
    if per_share_risk <= 0:
        raise ValueError("entry must be > stop (long only)")
    dollar_risk = account * (risk_per_trade_pct / 100)
    shares = int(dollar_risk // per_share_risk)
    return {"shares": shares, "dollar_risk": round(shares * per_share_risk, 2),
            "risk_pct_of_account": round(shares * per_share_risk / account * 100, 3)}


def runner_grade(change_pct, rvol_x, float_shares_m, has_catalyst, dilution_score):
    """러너 후보 종합 등급(A/B/C/회피). 5요소 결합.

    강한 러너 조건(경험칙): 갭/변동 +10%↑, RVOL 5배↑, 저플로트(<20M), 진짜 촉매, 낮은 희석.
    """
    pts = 0
    pts += 2 if change_pct >= 20 else 1 if change_pct >= 10 else 0
    pts += 2 if rvol_x >= 5 else 1 if rvol_x >= 2 else 0
    pts += 2 if float_shares_m < 20 else 1 if float_shares_m < 100 else 0
    pts += 2 if has_catalyst else 0
    # 희석은 감점(veto성)
    if dilution_score >= 60:
        return {"points": pts, "grade": "회피", "note": "희석 치명 — 셋업 좋아도 롱 회피(스퀴즈만 노림)"}
    pts += 1 if dilution_score < 15 else 0
    grade = "A" if pts >= 7 else "B" if pts >= 5 else "C" if pts >= 3 else "회피"
    return {"points": pts, "grade": grade}


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows cp949 콘솔에서 한글·em-dash 출력 보장
    except Exception:
        pass
    print("=== stock-momentum-runner 데모 (가상 종목 XYZ) ===")
    print("RVOL:", round(rvol(48_000_000, 6_000_000), 2), "배")
    print("Float rotation:", round(float_rotation(48_000_000, 12_000_000), 2), "회")
    dr = dilution_risk(has_active_shelf_s3=True, atm_424b5_last_90d=2,
                       reverse_split_last_12m=False, cash_runway_quarters=3, warrants_overhang_pct=15)
    print("Dilution:", dr)
    st = adr_stop_ok(entry=4.20, stop=3.95, adr_pct=9.0)
    print("ADR stop:", st)
    sz = size_by_risk(account=25_000, risk_per_trade_pct=0.5, entry=4.20, stop=3.95)
    print("Size:", sz)
    print("Grade:", runner_grade(change_pct=18, rvol_x=8, float_shares_m=12,
                                  has_catalyst=True, dilution_score=dr["dilution_score"]))
