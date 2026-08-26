"""테일 헤지 계산 — volatility tax·헤지의 기하평균 기여 비교. (표준 라이브러리만)

사용: python hedge_budget.py           # 데모
임포트: from hedge_budget import geo_mean_approx, hedge_compare
"""


def geo_mean_approx(arith, sigma):
    """기하평균 ≈ 산술평균 - sigma^2/2 (volatility tax). 입력·반환 모두 소수(0.08=8%)."""
    return arith - sigma ** 2 / 2


def hedge_compare(base_arith, base_sigma, hedge_cost, sigma_reduction):
    """헤지 전후 기하평균 비교 — '비용'이 아니라 복리 기여로 평가(Spitznagel).

    hedge_cost: 연간 보험료(소수). sigma_reduction: 헤지로 줄어드는 변동성(소수, 예 0.06=6%p 축소).
    """
    no_hedge = geo_mean_approx(base_arith, base_sigma)
    hedged = geo_mean_approx(base_arith - hedge_cost, base_sigma - sigma_reduction)
    return {
        "무헤지 기하평균%": round(no_hedge * 100, 2),
        "헤지 기하평균%": round(hedged * 100, 2),
        "복리 기여%p": round((hedged - no_hedge) * 100, 2),
        "판정": "cost-effective(채택)" if hedged > no_hedge else "보험료가 복리를 갉음(축소/대체)",
    }


def recovery_needed(drawdown):
    """-D% 손실 후 본전까지 필요한 수익률. 예: -50% -> +100%."""
    return drawdown / (1 - drawdown)


if __name__ == "__main__":
    print("== 데모 ==")
    print(f"산술 8%·변동성 25% -> 기하 {geo_mean_approx(0.08, 0.25)*100:.2f}% (vol tax {0.25**2/2*100:.2f}%p)")
    print(hedge_compare(base_arith=0.08, base_sigma=0.25, hedge_cost=0.007, sigma_reduction=0.07))
    print(f"-60% 손실 후 본전: +{recovery_needed(0.60)*100:.0f}% 필요")
