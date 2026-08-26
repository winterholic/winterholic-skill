"""역DCF-lite — 현재 주가가 내포한 성장률 역산. (표준 라이브러리만)

"이 가격이 정당화되려면 몇 % 성장해야 하나"를 묻는 도구. 성장주 과열 점검용.
사용: python implied_growth.py         # 데모
임포트: from implied_growth import implied_growth
"""


def _dcf_value(fcf0, growth, years, terminal_multiple, discount):
    """1단계: years년간 g 성장 -> 종료 시 FCF x terminal_multiple로 회수 가정."""
    pv = 0.0
    fcf = fcf0
    for t in range(1, years + 1):
        fcf *= (1 + growth)
        pv += fcf / (1 + discount) ** t
    pv += fcf * terminal_multiple / (1 + discount) ** years
    return pv


def implied_growth(market_cap, fcf0, years=10, terminal_multiple=15, discount=0.10,
                   lo=-0.5, hi=1.0, tol=1e-4):
    """시총 = DCF가 되는 성장률 g를 이분법으로 역산. 반환: 연 성장률(소수).

    fcf0 <= 0이면 역산 불가(None) -> 흑자전환 시나리오로 따로 평가.
    """
    if fcf0 <= 0:
        return None
    for _ in range(100):
        mid = (lo + hi) / 2
        v = _dcf_value(fcf0, mid, years, terminal_multiple, discount)
        if abs(v - market_cap) < market_cap * tol:
            return mid
        if v < market_cap:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


if __name__ == "__main__":
    print("== 데모: (가상) D테크, 단위 억원 ==")
    g = implied_growth(market_cap=50000, fcf0=600, years=10, terminal_multiple=15, discount=0.10)
    print(f"시총 5조 / FCF 600억 -> 내포 성장률: 연 {g*100:.1f}% x 10년")
    print("판정: 내포 성장률이 업계 최고 실적(예: 25~30%)을 넘으면 가격이 비현실적 기대를 반영")
