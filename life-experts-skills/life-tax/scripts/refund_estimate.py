"""소득공제 vs 세액공제 절세효과 비교 + 종합소득세 개략 추정 (데모).

면책: 교육용 개략 계산이다. 실제 세액은 누진공제·각종 공제·지방소득세·감면을
모두 반영해야 하며 세율 구간은 매년 개정된다. 반드시 홈택스/국세청 126 확인.
표준 라이브러리만 사용.

핵심 교훈 시연:
- 소득공제는 '과세표준'을 줄여 (공제액 × 한계세율)만큼 절세
- 세액공제는 '산출세액'을 직접 줄여 (공제대상액 × 공제율)만큼 절세
- 같은 금액이라도 둘의 효과는 세율구간/공제율에 따라 크게 다르다
"""

# 2023~2025 적용 종합소득세 누진세율 구간 (지방소득세 10% 별도) — 2026 기준 확인 필요.
# (하한 초과금액, 세율) 형태의 한계세율 테이블. 공식 출처: 국세청.
BRACKETS = [
    (0, 0.06),
    (14_000_000, 0.15),
    (50_000_000, 0.24),
    (88_000_000, 0.35),
    (150_000_000, 0.38),
    (300_000_000, 0.40),
    (500_000_000, 0.42),
    (1_000_000_000, 0.45),
]


def income_tax(taxable: float) -> float:
    """과세표준에 대한 산출세액(지방세 제외)을 누진 계산."""
    tax = 0.0
    for i, (floor, rate) in enumerate(BRACKETS):
        upper = BRACKETS[i + 1][0] if i + 1 < len(BRACKETS) else float("inf")
        if taxable > floor:
            tax += (min(taxable, upper) - floor) * rate
        else:
            break
    return tax


def marginal_rate(taxable: float) -> float:
    rate = BRACKETS[0][1]
    for floor, r in BRACKETS:
        if taxable > floor:
            rate = r
    return rate


def compare(taxable_base: float, amount: float, credit_rate: float) -> None:
    """동일 금액(amount)을 소득공제로 넣을 때 vs 세액공제로 넣을 때 절세액 비교."""
    base_tax = income_tax(taxable_base)

    # 소득공제: 과세표준에서 차감
    deduction_tax = income_tax(max(0, taxable_base - amount))
    deduction_saving = base_tax - deduction_tax

    # 세액공제: 산출세액에서 (대상액 × 공제율) 직접 차감
    credit_saving = amount * credit_rate

    mr = marginal_rate(taxable_base)
    print(f"  과세표준 {taxable_base:,.0f}원, 한계세율 {mr*100:.0f}% (지방세 별도)")
    print(f"  대상금액 {amount:,.0f}원을:")
    print(f"   - 소득공제로 → 절세 약 {deduction_saving:,.0f}원 (= 금액 × 한계세율)")
    print(f"   - 세액공제({credit_rate*100:.1f}%)로 → 절세 약 {credit_saving:,.0f}원")
    diff = credit_saving - deduction_saving
    winner = "세액공제" if diff > 0 else "소득공제"
    print(f"   ⇒ 이 구간에선 {winner}가 {abs(diff):,.0f}원 더 유리\n")


if __name__ == "__main__":
    print("=== 소득공제 vs 세액공제 절세효과 비교 (데모) ===\n")
    print("[저소득 구간: 과세표준 1,200만원, 100만원 납입, 세액공제율 16.5% 가정]")
    compare(12_000_000, 1_000_000, 0.165)

    print("[고소득 구간: 과세표준 1억원, 100만원 납입, 세액공제율 13.2% 가정]")
    compare(100_000_000, 1_000_000, 0.132)

    print("교훈: 한계세율이 공제율보다 낮으면 세액공제가, 높으면 소득공제가 유리.")
    print("프리랜서 3.3% 선납 예시:")
    fee = 30_000_000
    withheld = fee * 0.033
    print(f"  외주 {fee:,.0f}원 → 3.3% 선납 {withheld:,.0f}원은 '완납' 아님.")
    print("  5월에 경비 차감 후 실제 세액과 비교해 환급/추가납부 정산해야 함.")
