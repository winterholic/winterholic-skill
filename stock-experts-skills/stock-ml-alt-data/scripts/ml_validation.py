"""금융 ML 검증 도구 — 삼중장벽 라벨링 + DSR(축소 샤프). (표준 라이브러리만)

사용: python ml_validation.py          # 데모
임포트: from ml_validation import triple_barrier, deflated_sharpe
"""
import math
from statistics import NormalDist

_N = NormalDist()


def triple_barrier(prices, entry_idx, tp_pct, sl_pct, max_hold):
    """세 장벽 중 먼저 닿는 것으로 라벨: 익절 +1 / 손절 -1 / 시간만료 0."""
    p0 = prices[entry_idx]
    upper, lower = p0 * (1 + tp_pct), p0 * (1 - sl_pct)
    for t in range(entry_idx + 1, min(entry_idx + max_hold + 1, len(prices))):
        if prices[t] >= upper:
            return {"label": 1, "exit": t, "이유": "익절 장벽"}
        if prices[t] <= lower:
            return {"label": -1, "exit": t, "이유": "손절 장벽"}
    return {"label": 0, "exit": min(entry_idx + max_hold, len(prices) - 1), "이유": "시간 만료"}


def deflated_sharpe(sr_hat, n_trials, T, skew=0.0, kurt=3.0, var_across_trials=None):
    """DSR(Bailey & López de Prado): 시도 횟수를 반영해 샤프를 디플레이트.

    sr_hat: 관측 샤프(기간 단위와 T 일치). n_trials: 시도한 전략/파라미터 수.
    반환: DSR(0~1 확률). 0.95 이상이어야 '운이 아닌 스킬'로 신뢰.
    """
    v = var_across_trials if var_across_trials is not None else sr_hat ** 2 * 0.5
    g = 0.5772156649
    e = math.e
    sr0 = math.sqrt(v) * ((1 - g) * _N.inv_cdf(1 - 1 / n_trials) + g * _N.inv_cdf(1 - 1 / (n_trials * e)))
    denom = math.sqrt(max(1e-12, 1 - skew * sr_hat + (kurt - 1) / 4 * sr_hat ** 2))
    z = (sr_hat - sr0) * math.sqrt(T - 1) / denom
    return _N.cdf(z)


if __name__ == "__main__":
    prices = [100, 101, 99.5, 102, 104, 106, 103, 101, 100, 98]
    print("== 데모 ==")
    print("삼중장벽(익절+5%/손절-3%/10봉):", triple_barrier(prices, 0, 0.05, 0.03, 10))
    dsr = deflated_sharpe(sr_hat=0.12, n_trials=50, T=1250)   # 일간 샤프 0.12(연 ~1.9), 50회 시도, 5년
    print(f"DSR: {dsr:.3f} -> {'신뢰 가능(>0.95)' if dsr > 0.95 else '과적합 의심: 시도 수 대비 약함'}")
