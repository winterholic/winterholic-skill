"""대출 상환·대환 손익·전월세 전환율 계산 (데모).

면책: 교육용 개략 계산이다. 실제 상환액·수수료·금리는 약정·정책에 따라 다르며
금리는 변동한다. 반드시 금감원 1332·파인·은행에서 당해 조건 확인. 표준 라이브러리만 사용.

시연:
1) 원리금균등 월상환액과 총이자
2) 대환 손익: 중도상환수수료를 차감한 순이득으로 판단해야 함
3) 전월세 전환율 (보증금 ↔ 월세 환산)
"""


def monthly_payment(principal: float, annual_rate: float, months: int) -> float:
    """원리금균등 월 상환액."""
    r = annual_rate / 12
    if r == 0:
        return principal / months
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def total_interest(principal: float, annual_rate: float, months: int) -> float:
    return monthly_payment(principal, annual_rate, months) * months - principal


def refinance_benefit(balance: float, old_rate: float, new_rate: float,
                      remaining_months: int, prepay_fee_rate: float) -> None:
    """대환 손익: 금리차 절감액에서 중도상환수수료를 빼야 진짜 이득."""
    old_int = total_interest(balance, old_rate, remaining_months)
    new_int = total_interest(balance, new_rate, remaining_months)
    saving = old_int - new_int
    prepay_fee = balance * prepay_fee_rate
    net = saving - prepay_fee
    print(f"  잔액 {balance:,.0f}원, 잔여 {remaining_months}개월")
    print(f"  기존금리 {old_rate*100:.2f}% 총이자 {old_int:,.0f}원")
    print(f"  신규금리 {new_rate*100:.2f}% 총이자 {new_int:,.0f}원")
    print(f"  이자 절감 {saving:,.0f}원 − 중도상환수수료 {prepay_fee:,.0f}원")
    if net > 0:
        print(f"  ⇒ 순이득 {net:,.0f}원: 갈아타기 유리 (수수료 차감 후에도 이득)\n")
    else:
        print(f"  ⇒ 순손실 {-net:,.0f}원: 갈아타기 불리 (수수료가 절감분 초과)\n")


def jeonse_to_wolse(deposit_reduction: float, conversion_rate: float) -> float:
    """전세→월세 전환 시 월세 = 줄이는 보증금 × 전환율 / 12."""
    return deposit_reduction * conversion_rate / 12


if __name__ == "__main__":
    print("=== 대출/대환/전월세 계산 데모 ===\n")

    print("[1] 원리금균등 상환 (1억, 연 4.5%, 120개월)")
    mp = monthly_payment(100_000_000, 0.045, 120)
    ti = total_interest(100_000_000, 0.045, 120)
    print(f"  월 상환액 약 {mp:,.0f}원 / 총이자 약 {ti:,.0f}원\n")

    print("[2] 대환 손익 - 수수료가 작을 때 (잔액 5천만, 4.5%→3.8%, 36개월, 수수료 0.5%)")
    refinance_benefit(50_000_000, 0.045, 0.038, 36, 0.005)

    print("[2'] 대환 손익 - 수수료가 클 때 (같은 조건, 수수료 1.5%)")
    refinance_benefit(50_000_000, 0.045, 0.038, 36, 0.015)

    print("[3] 전월세 전환율 (보증금 5천만 줄이고 월세로, 전환율 연 5.5% 가정)")
    w = jeonse_to_wolse(50_000_000, 0.055)
    print(f"  월세 약 {w:,.0f}원 (= 5천만 × 5.5% / 12)")
    print("  ※ 전월세전환율 상한은 법령(주임법)으로 규제 - 당해 기준 확인 필요")
