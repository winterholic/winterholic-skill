"""특수상황 계산기 — Magic Formula 랭킹 + 합병차익 스프레드. (표준 라이브러리만)

사용: python magic_formula.py          # 데모
임포트: from magic_formula import earnings_yield, roc, magic_rank, arb_annualized, arb_expected
"""


def earnings_yield(ebit, ev):
    """Earnings Yield = EBIT / EV. 자본구조 무관 저평가 척도."""
    return ebit / ev


def roc(ebit, net_working_capital, net_fixed_assets):
    """Return on Capital = EBIT / (순운전자본 + 순고정자산)."""
    return ebit / (net_working_capital + net_fixed_assets)


def magic_rank(stocks):
    """[{name, ebit, ev, nwc, nfa}, ...] -> EY·ROC 각각 순위 합산(낮을수록 좋음)."""
    for s in stocks:
        s["ey"] = earnings_yield(s["ebit"], s["ev"])
        s["roc"] = roc(s["ebit"], s["nwc"], s["nfa"])
    ey_rank = {s["name"]: i for i, s in enumerate(sorted(stocks, key=lambda x: -x["ey"]), 1)}
    roc_rank = {s["name"]: i for i, s in enumerate(sorted(stocks, key=lambda x: -x["roc"]), 1)}
    out = [{"name": s["name"], "EY%": round(s["ey"] * 100, 1), "ROC%": round(s["roc"] * 100, 1),
            "종합순위점수": ey_rank[s["name"]] + roc_rank[s["name"]]} for s in stocks]
    return sorted(out, key=lambda x: x["종합순위점수"])


def arb_annualized(spread_pct, days_to_close):
    """합병차익 연율화 수익률(%) = 스프레드% x (365 / 종결까지 일수)."""
    return spread_pct * 365 / days_to_close


def arb_expected(gain_pct, prob_close, loss_pct_if_break):
    """기대값(%) = 성사확률 x 이익% - (1-성사확률) x 무산 시 손실%."""
    return prob_close * gain_pct - (1 - prob_close) * loss_pct_if_break


if __name__ == "__main__":
    print("== 데모 ==")
    demo = [
        {"name": "갑", "ebit": 300, "ev": 1600, "nwc": 400, "nfa": 700},
        {"name": "을", "ebit": 220, "ev": 2400, "nwc": 600, "nfa": 900},
        {"name": "병", "ebit": 180, "ev": 900, "nwc": 300, "nfa": 500},
    ]
    for row in magic_rank(demo):
        print(row)
    print(f"합병차익: 스프레드 4% / 90일 -> 연율화 {arb_annualized(4, 90):.1f}%")
    print(f"기대값: 성사 90% x +4% vs 무산 시 -15% -> {arb_expected(4, 0.9, 15):+.2f}%")
