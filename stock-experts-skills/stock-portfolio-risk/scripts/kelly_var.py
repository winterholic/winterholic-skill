"""사이징·리스크 계산 — Kelly·VaR/CVaR·변동성 타게팅. (표준 라이브러리만)

사용: python kelly_var.py              # 데모
임포트: from kelly_var import kelly_invest, kelly_bet, var_cvar, vol_target_mult
"""
from statistics import NormalDist

_N = NormalDist()


def kelly_invest(mu, rf, sigma, fraction=0.5):
    """투자형 Kelly: f* = (mu - rf) / sigma^2. 기본 ½켈리(추정오차 안전마진)."""
    f_full = (mu - rf) / sigma ** 2
    return {"full_kelly": round(f_full, 3), "적용비중": round(f_full * fraction, 3)}


def kelly_bet(p, b):
    """베팅형 Kelly: f* = (b*p - q) / b. p=승률, b=손익비(odds)."""
    return (b * p - (1 - p)) / b


def var_cvar(value, mu, sigma, conf=0.95):
    """모수적(정규) VaR·CVaR. mu/sigma는 보유기간 기준 수익률 평균·표준편차.

    주의: 정규 가정은 꼬리 과소평가 — 결과는 '최소' 위험으로 읽고 stock-tail-risk로 보강.
    """
    z = _N.inv_cdf(1 - conf)
    var = -(mu + z * sigma) * value
    pdf_z = _N.pdf(z)
    cvar = -(mu - sigma * pdf_z / (1 - conf)) * value
    return {"VaR": round(var, 1), "CVaR": round(cvar, 1), "신뢰수준": conf}


def vol_target_mult(target_vol, realized_vol, cap=1.5):
    """변동성 타게팅 레버리지 배수 = 목표/실현 변동성 (상한 cap)."""
    return min(target_vol / realized_vol, cap)


if __name__ == "__main__":
    print("== 데모 ==")
    print("투자형 Kelly(mu 12%·rf 3%·sigma 25%):", kelly_invest(0.12, 0.03, 0.25))
    print(f"베팅형 Kelly(승률 55%·손익비 2): f*={kelly_bet(0.55, 2):.3f}")
    print("1개월 VaR/CVaR(포트 1억·mu 0.8%·sigma 6%):", var_cvar(10000, 0.008, 0.06))
    print(f"변동성 타게팅(목표 10%·실현 16%): x{vol_target_mult(0.10, 0.16):.2f}")
