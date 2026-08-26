#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""life-personal-finance 계산기 — 비상금 목표액 / 복리 미래가치 / 저축률.

표준 라이브러리만 사용(argparse). 인자 없이 실행하면 데모(기본값 예시)가 출력된다.
모든 결과는 추정치이며 투자 권유가 아니다. 세제·수익률은 가정값이다.

사용 예:
  python finance_calc.py                         # 데모(기본값 예시)
  python finance_calc.py emergency --monthly 250 --months 6
  python finance_calc.py compound --principal 1000 --monthly 50 --rate 5 --years 20
  python finance_calc.py savings --income 400 --saving 120
"""
import argparse


def fmt(man: float) -> str:
    """만원 단위 숫자를 한국식 '억/만원' 문자열로."""
    man = round(man)
    if abs(man) >= 10000:
        eok, rest = divmod(int(man), 10000)
        return f"{eok}억 {rest:,}만원" if rest else f"{eok}억원"
    return f"{int(man):,}만원"


def emergency_fund(monthly_expense: float, months: int) -> float:
    """비상금 목표액(만원) = 월 필수지출 x 보유 개월."""
    return monthly_expense * months


def future_value(principal: float, monthly: float, annual_rate_pct: float, years: int) -> dict:
    """복리 미래가치(만원). 원금 일시금 + 매월 적립, 월복리 가정.

    명목 연수익률을 12로 나눈 월이율 적용(세전, 인플레 미반영).
    """
    r = annual_rate_pct / 100 / 12
    n = years * 12
    if r == 0:
        fv_principal = principal
        fv_contrib = monthly * n
    else:
        fv_principal = principal * (1 + r) ** n
        fv_contrib = monthly * (((1 + r) ** n - 1) / r)
    total = fv_principal + fv_contrib
    invested = principal + monthly * n
    return {
        "총평가액": total,
        "총납입원금": invested,
        "추정수익": total - invested,
    }


def savings_rate(income: float, saving: float) -> float:
    """단순 저축률(%) = 월 저축액 / 월 소득 x 100."""
    if income <= 0:
        return 0.0
    return saving / income * 100


DISCLAIMER = "※ 추정치이며 투자 권유가 아닙니다. 수익률·세제는 가정값이니 본인 상황과 공식 출처(금감원 1332·국세청 126)로 확인하세요."


def run_emergency(a):
    target = emergency_fund(a.monthly, a.months)
    print(f"[비상금 목표] 월 필수지출 {fmt(a.monthly)} x {a.months}개월")
    print(f"  -> 목표 비상금: {fmt(target)} (즉시 인출 가능한 예금/파킹통장 권장)")
    print(DISCLAIMER)


def run_compound(a):
    res = future_value(a.principal, a.monthly, a.rate, a.years)
    print(f"[복리 미래가치] 원금 {fmt(a.principal)} + 매월 {fmt(a.monthly)}, 연 {a.rate}% 가정, {a.years}년")
    print(f"  -> 총 평가액(세전·추정): {fmt(res['총평가액'])}")
    print(f"  -> 총 납입원금: {fmt(res['총납입원금'])} / 추정 수익: {fmt(res['추정수익'])}")
    print(DISCLAIMER)


def run_savings(a):
    rate = savings_rate(a.income, a.saving)
    print(f"[저축률] 월 소득 {fmt(a.income)} 중 저축 {fmt(a.saving)}")
    print(f"  -> 저축률: {rate:.1f}%")
    print(DISCLAIMER)


def demo():
    print("=== finance_calc 데모 (기본값 예시) ===\n")
    print("# 1) 비상금 (월지출 250만원, 6개월)")
    run_emergency(argparse.Namespace(monthly=250, months=6))
    print()
    print("# 2) 복리 (원금 1,000만원 + 월 50만원, 연 5%, 20년)")
    run_compound(argparse.Namespace(principal=1000, monthly=50, rate=5, years=20))
    print()
    print("# 3) 저축률 (월소득 400만원, 저축 120만원)")
    run_savings(argparse.Namespace(income=400, saving=120))


def build_parser():
    p = argparse.ArgumentParser(description="개인 재무 계산기(추정·투자 권유 아님)")
    sub = p.add_subparsers(dest="cmd")

    e = sub.add_parser("emergency", help="비상금 목표액")
    e.add_argument("--monthly", type=float, default=250, help="월 필수지출(만원)")
    e.add_argument("--months", type=int, default=6, help="보유 개월(3~6 권장)")
    e.set_defaults(func=run_emergency)

    c = sub.add_parser("compound", help="복리 미래가치")
    c.add_argument("--principal", type=float, default=1000, help="초기 원금(만원)")
    c.add_argument("--monthly", type=float, default=50, help="매월 적립(만원)")
    c.add_argument("--rate", type=float, default=5, help="연 명목수익률(%)")
    c.add_argument("--years", type=int, default=20, help="투자 기간(년)")
    c.set_defaults(func=run_compound)

    s = sub.add_parser("savings", help="단순 저축률")
    s.add_argument("--income", type=float, default=400, help="월 소득(만원)")
    s.add_argument("--saving", type=float, default=120, help="월 저축(만원)")
    s.set_defaults(func=run_savings)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not args.cmd:
        demo()
        return
    args.func(args)


if __name__ == "__main__":
    main()
