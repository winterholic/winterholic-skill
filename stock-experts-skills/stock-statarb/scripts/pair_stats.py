"""페어 통계 — 헤지비율·z-score·half-life·Hurst. (표준 라이브러리만)

사용: python pair_stats.py             # 데모
임포트: from pair_stats import hedge_beta, zscore, half_life, hurst
주의: 공적분 검정(ADF/Johansen)은 statsmodels 필요 — 여기선 half-life·Hurst로 평균회귀성을 보조 판정.
"""
import math


def hedge_beta(y, x):
    """OLS 헤지비율: y ~ a + b*x."""
    n = len(y)
    mx, my = sum(x) / n, sum(y) / n
    b = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / sum((xi - mx) ** 2 for xi in x)
    return b


def spread_series(y, x, beta):
    return [yi - beta * xi for yi, xi in zip(y, x)]


def zscore(spread, window=None):
    s = spread[-window:] if window else spread
    m = sum(s) / len(s)
    sd = (sum((v - m) ** 2 for v in s) / (len(s) - 1)) ** 0.5
    return (spread[-1] - m) / sd


def half_life(spread):
    """OU 반감기: ds_t = a + b*s_{t-1} 회귀 -> HL = -ln(2)/ln(1+b). b>=0이면 평균회귀 아님(None)."""
    s_lag = spread[:-1]
    ds = [spread[i + 1] - spread[i] for i in range(len(spread) - 1)]
    b = hedge_beta(ds, s_lag)
    if b >= 0:
        return None
    return -math.log(2) / math.log(1 + b)


def hurst(series, lags=(2, 4, 8, 16, 32)):
    """분산법 Hurst: H<0.5 평균회귀 / ~0.5 랜덤워크 / >0.5 추세."""
    pts = []
    for lag in lags:
        diffs = [series[i + lag] - series[i] for i in range(len(series) - lag)]
        m = sum(diffs) / len(diffs)
        sd = (sum((d - m) ** 2 for d in diffs) / (len(diffs) - 1)) ** 0.5
        if sd > 0:
            pts.append((math.log(lag), math.log(sd)))
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    return sum((p[0] - mx) * (p[1] - my) for p in pts) / sum((p[0] - mx) ** 2 for p in pts)


if __name__ == "__main__":
    import random
    random.seed(3)
    x, s = [100.0], [0.0]
    for _ in range(499):
        x.append(x[-1] + random.gauss(0, 1))
        s.append(s[-1] * 0.9 + random.gauss(0, 0.5))   # 평균회귀 스프레드(OU)
    y = [0.92 * xi + si for xi, si in zip(x, s)]
    b = hedge_beta(y, x)
    sp = spread_series(y, x, b)
    print("== 데모: 합성 공적분 페어 (진짜 beta=0.92) ==")
    print(f"beta {b:.3f} | z-score {zscore(sp, 60):+.2f} | half-life {half_life(sp):.1f}일 | Hurst {hurst(sp):.2f}")
    print("판정: HL 짧고 Hurst<0.5면 평균회귀 후보. 진입 |z|>=2, 손절 |z|>=3.5, 시간손절 = HL x 3~4배")
