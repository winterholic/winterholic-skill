"""팩터 회귀 — 알파/베타 분해 + t-stat. (표준 라이브러리만, statsmodels 불필요)

사용: python factor_alpha.py           # 데모
임포트: from factor_alpha import ols_alpha
입력: 포트 초과수익 리스트 + 팩터 수익률 리스트들(같은 길이).
"""


def _inv(M):
    n = len(M)
    A = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(M)]
    for col in range(n):
        p = max(range(col, n), key=lambda r: abs(A[r][col]))
        A[col], A[p] = A[p], A[col]
        d = A[col][col]
        A[col] = [v / d for v in A[col]]
        for r in range(n):
            if r != col and A[r][col]:
                f = A[r][col]
                A[r] = [rv - f * cv for rv, cv in zip(A[r], A[col])]
    return [row[n:] for row in A]


def ols_alpha(y, factors, names=None):
    """y(초과수익) ~ const + factors. 반환: 계수·t-stat. 알파는 t>=2 정도여야 유의."""
    n = len(y)
    X = [[1.0] + [f[i] for f in factors] for i in range(n)]
    k = len(X[0])
    XtX = [[sum(X[r][i] * X[r][j] for r in range(n)) for j in range(k)] for i in range(k)]
    Xty = [sum(X[r][i] * y[r] for r in range(n)) for i in range(k)]
    XtX_inv = _inv(XtX)
    b = [sum(XtX_inv[i][j] * Xty[j] for j in range(k)) for i in range(k)]
    resid = [y[r] - sum(X[r][i] * b[i] for i in range(k)) for r in range(n)]
    s2 = sum(e * e for e in resid) / (n - k)
    se = [(s2 * XtX_inv[i][i]) ** 0.5 for i in range(k)]
    t = [b[i] / se[i] if se[i] else float("nan") for i in range(k)]
    labels = ["alpha"] + (names or [f"f{i+1}" for i in range(k - 1)])
    return {lab: {"coef": round(b[i], 5), "t": round(t[i], 2)} for i, lab in enumerate(labels)}


def ic_weights(ics):
    """IC 가중 합성: w_i = IC_i / sum(|IC|). 음(-) IC 팩터는 제외/역방향 검토."""
    tot = sum(abs(v) for v in ics.values())
    return {k: round(v / tot, 3) for k, v in ics.items()}


if __name__ == "__main__":
    import random
    random.seed(7)
    mkt = [random.gauss(0.005, 0.04) for _ in range(120)]
    hml = [random.gauss(0.002, 0.02) for _ in range(120)]
    y = [0.001 + 1.0 * m + 0.4 * h + random.gauss(0, 0.01) for m, h in zip(mkt, hml)]
    print("== 데모: 월간 120개월, 진짜 alpha=0.1%/월 ==")
    print(ols_alpha(y, [mkt, hml], names=["MKT", "HML"]))
    print("IC 가중:", ic_weights({"Value": 0.04, "Mom": 0.05, "Quality": 0.03}))
