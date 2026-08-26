"""딥밸류 계산기 — NCAV·NNWC·Graham Number·안전마진. (표준 라이브러리만 사용)

사용: python deepvalue_calc.py          # 데모 실행
임포트: from deepvalue_calc import ncav, nnwc, graham_number, mos
단위: 금액은 동일 단위(예: 억원)로 통일해 입력한다.
"""


def ncav(current_assets, total_liabilities):
    """NCAV = 유동자산 - 총부채. net-net 기준: 시총 < NCAV × 2/3."""
    return current_assets - total_liabilities


def nnwc(cash, receivables, inventory, total_liabilities,
         w_cash=1.0, w_recv=0.75, w_inv=0.5):
    """NNWC(보수적 청산가치).

    Graham 자산 보정계수: 현금성 100% / 매출채권 ~75% / 재고 ~50%.
    무형자산·선급금은 0으로 계산(인자에서 제외)한다.
    """
    return cash * w_cash + receivables * w_recv + inventory * w_inv - total_liabilities


def graham_number(eps, bvps):
    """Graham Number = sqrt(22.5 x EPS x BVPS). EPS>0, BVPS>0일 때만 유효."""
    if eps <= 0 or bvps <= 0:
        return None
    return (22.5 * eps * bvps) ** 0.5


def mos(intrinsic, price):
    """안전마진 = (내재가치 - 가격) / 내재가치."""
    return (intrinsic - price) / intrinsic


def netnet_screen(market_cap, current_assets, total_liabilities):
    """net-net 판정: 시총 < NCAV x 2/3 여부와 청산 안전마진을 반환."""
    v = ncav(current_assets, total_liabilities)
    threshold = v * 2 / 3
    return {
        "NCAV": v,
        "기준(2/3 NCAV)": round(threshold, 1),
        "net-net": market_cap < threshold,
        "청산 안전마진%": round(mos(threshold, market_cap) * 100, 1) if threshold > 0 else None,
    }


if __name__ == "__main__":
    print("== 데모: (가상) A기업, 단위 억원 ==")
    print("net-net:", netnet_screen(market_cap=800, current_assets=2000, total_liabilities=800))
    print("NNWC:", nnwc(cash=500, receivables=600, inventory=600, total_liabilities=800), "억원")
    gn = graham_number(eps=900, bvps=9500)
    print("Graham Number:", round(gn, 0), "원 | 주가 12,000 대비 MOS:", round(mos(gn, 12000) * 100, 1), "%")
