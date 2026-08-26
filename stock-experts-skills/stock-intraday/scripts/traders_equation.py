"""Trader's Equation — 기대값·손익분기 승률·비용 반영. (표준 라이브러리만)

사용: python traders_equation.py       # 데모
임포트: from traders_equation import expectancy, breakeven_winrate
"""


def expectancy(win_rate, reward, risk, cost=0.0):
    """기대값 = 승률 x (보상-비용) - 패율 x (위험+비용). 양(+)일 때만 진입.

    reward/risk/cost는 동일 단위(틱·원·%). cost는 편도 수수료+세금+슬리피지의 왕복 합산.
    """
    return win_rate * (reward - cost) - (1 - win_rate) * (risk + cost)


def breakeven_winrate(reward, risk, cost=0.0):
    """손익분기 승률 = (위험+비용) / (보상+위험). 이보다 높은 승률이어야 우위."""
    return (risk + cost) / (reward + risk)


def position_risk_ok(account, risk_per_trade, max_pct=0.01):
    """거래당 리스크가 계좌의 0.5~1% 이내인지(기본 1%)."""
    return risk_per_trade <= account * max_pct


if __name__ == "__main__":
    print("== 데모: 5분봉 High 2 셋업 (틱 단위) ==")
    ev = expectancy(win_rate=0.55, reward=8, risk=4, cost=0.8)
    be = breakeven_winrate(reward=8, risk=4, cost=0.8)
    print(f"기대값: {ev:+.2f}틱/회 | 손익분기 승률: {be*100:.1f}% (실제 55% 가정)")
    print(f"비용 0이면 손익분기 {breakeven_winrate(8, 4)*100:.1f}% -> 비용이 우위를 {((be-breakeven_winrate(8,4))*100):.1f}%p 깎음")
    print("계좌 1억·거래당 리스크 80만원 ->", "OK" if position_risk_ok(1e8, 8e5) else "초과(축소 필요)")
