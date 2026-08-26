"""GARP 계산기 — PEG·PEGY·EPS CAGR 평활화. (표준 라이브러리만)

사용: python peg_calc.py               # 데모
임포트: from peg_calc import peg, pegy, eps_cagr_smoothed
"""


def peg(per, growth_pct):
    """PEG = PER / 연간 EPS 성장률(%). <1.0 저평가 후보, >2.0 과대평가.

    성장률은 trailing 3~5년 CAGR을 기본으로 쓰고, forward 추정은 교차검증용.
    성장률 <= 0이면 PEG 무의미(None).
    """
    if growth_pct <= 0:
        return None
    return per / growth_pct


def pegy(per, growth_pct, div_yield_pct):
    """PEGY = PER / (EPS 성장률% + 배당수익률%). 배당 큰 stalwart용."""
    denom = growth_pct + div_yield_pct
    if denom <= 0:
        return None
    return per / denom


def eps_cagr_smoothed(eps_series):
    """다년 EPS 리스트(과거->최근)로 CAGR(%) 산출.

    한국처럼 단년 변동이 크면 시작·끝을 인접 연도와 평균해 평활화한다(원소 4개 이상일 때).
    시작값 <= 0이면 CAGR 정의 불가(None) -> 성장률은 절대액 추세로 따로 판단.
    """
    n = len(eps_series)
    if n < 2:
        return None
    if n >= 4:
        begin = (eps_series[0] + eps_series[1]) / 2
        end = (eps_series[-2] + eps_series[-1]) / 2
        years = n - 2
    else:
        begin, end, years = eps_series[0], eps_series[-1], n - 1
    if begin <= 0 or end <= 0:
        return None
    return ((end / begin) ** (1 / years) - 1) * 100


if __name__ == "__main__":
    print("== 데모: (가상) C기업 ==")
    g = eps_cagr_smoothed([520, 610, 700, 890, 1050])  # 5년 EPS
    print(f"EPS CAGR(평활): {g:.1f}%")
    print(f"PEG(PER 18): {peg(18, g):.2f}  | PEGY(배당 1%): {pegy(18, g, 1.0):.2f}")
    print("판정: PEG<1.0 저평가 후보 / ~1.0 정당 / >2.0 과대")
