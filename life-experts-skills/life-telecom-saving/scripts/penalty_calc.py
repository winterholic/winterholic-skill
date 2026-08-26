#!/usr/bin/env python3
"""통신 약정 위약금(할인반환금) + 단말 잔여할부 분리 추정 계산기.

핵심 메시지: '위약금'으로 묶어 오해하는 두 금액을 분리한다.
  - 할인반환금(진짜 추가 손실): 약정으로 받은 요금 할인의 일부를 환수
  - 단말 잔여 할부원금: 어차피 낼 기기값(위약금 아님)

주의: 실제 할인반환금 산식은 통신사·약정 종류·경과기간 구간별로 다르다.
여기서는 '간이 선형 모델'로 추정한다 — 정확액은 반드시 통신사 고지로 확인(확인 필요).
표준 라이브러리만 사용.
"""

from __future__ import annotations


def discount_return_linear(
    monthly_discount: float,
    total_months: int,
    elapsed_months: int,
    return_ratio_cap: float = 1.0,
) -> float:
    """간이 할인반환금 추정 (선형 모델).

    누적 받은 할인 = monthly_discount * elapsed_months.
    중도해지 시 잔여기간 비중만큼 환수한다고 단순 가정.
    실제 통신사는 경과 구간별 환수율(초기 100% → 후반 체감)을 쓰므로
    이 값은 '상한 근처의 보수적 추정'으로 해석할 것.

    return_ratio_cap: 누적 할인 대비 환수 상한(0~1). 보통 누적 할인의 일부만 환수.
    """
    if total_months <= 0:
        raise ValueError("total_months는 1 이상이어야 합니다")
    if not (0 <= elapsed_months <= total_months):
        raise ValueError("elapsed_months는 0~total_months 범위여야 합니다")

    received_discount = monthly_discount * elapsed_months
    remaining_ratio = (total_months - elapsed_months) / total_months
    estimated = received_discount * remaining_ratio * return_ratio_cap
    return round(estimated, 0)


def device_remaining(installment_monthly: float, remaining_months: int) -> float:
    """단말 잔여 할부원금 = 어차피 낼 돈(위약금 아님)."""
    if remaining_months < 0:
        raise ValueError("remaining_months는 0 이상")
    return round(installment_monthly * remaining_months, 0)


def summarize(
    monthly_discount: float,
    total_months: int,
    elapsed_months: int,
    installment_monthly: float = 0.0,
    device_remaining_months: int = 0,
    return_ratio_cap: float = 1.0,
) -> dict:
    drr = discount_return_linear(
        monthly_discount, total_months, elapsed_months, return_ratio_cap
    )
    dev = device_remaining(installment_monthly, device_remaining_months)
    return {
        "할인반환금_추정(진짜 추가 손실)": drr,
        "단말_잔여할부원금(어차피 낼 돈)": dev,
        "해지 시 즉시 부담 합계": round(drr + dev, 0),
        "주의": "할인반환금은 간이 추정 (정확액은 통신사 고지 확인, 확인 필요)",
    }


if __name__ == "__main__":
    # 예시: 월 1.5만원 할인, 24개월 약정 중 16개월 경과, 단말 할부 월 3만원 잔여 8개월
    result = summarize(
        monthly_discount=15000,
        total_months=24,
        elapsed_months=16,
        installment_monthly=30000,
        device_remaining_months=8,
        return_ratio_cap=1.0,
    )
    print("=== 통신 약정 해지 비용 분리 추정 ===")
    for k, v in result.items():
        print(f"{k}: {v}")
    print()
    print("해석: '해지하면 위약금 폭탄'의 상당 부분이 어차피 낼 단말 할부원금인 경우가 많다.")
    print("      진짜 추가 손실은 할인반환금뿐. 분리해서 전환 결정을 내려라.")
