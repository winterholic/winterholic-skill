#!/usr/bin/env python3
"""Screen-spec completeness linter for Korean-style service planning docs.

Checks a screen spec (plain text / markdown) for the elements that, when missing,
cause developers and QA to improvise: the 4 screen states, exception branches,
permission matrix, and data sources. This encodes antipatterns 1-7 in SKILL.md.

It is a CHECKLIST, not a parser: it looks for signal keywords. Absence is a flag,
presence is not proof of quality (a human still reviews content).

Usage:
  spec_lint.py            # run on built-in demo spec
  spec_lint.py FILE       # lint a real spec file
  spec_lint.py -          # read spec from stdin (explicit dash only)

Standard library only. ASCII output only.
"""
import sys

# (label, any-of keywords). Korean + English so it works on either doc style.
CHECKS = [
    ("empty state",     ["empty", "빈 상태", "빈상태", "데이터가 없", "없을 때", "no data"]),
    ("loading state",   ["loading", "로딩", "스켈레톤", "skeleton"]),
    ("error state",     ["error", "에러", "오류", "실패 시", "재시도", "retry"]),
    ("exception branch",["예외", "분기", "edge", "엣지", "if ", "일 때", "경우"]),
    ("permission/role", ["권한", "role", "롤", "관리자", "비로그인", "matrix", "매트릭스"]),
    ("data source",     ["api", "출처", "필드", "정렬", "페이징", "갱신", "endpoint"]),
    ("policy ref",      ["정책", "policy", "p-", "규칙", "rule"]),
    ("concrete copy",   ["\"", "“", "”", "문구", "메시지", "안내"]),
]

DEMO = """## 장바구니 화면
- 영역: 상품목록 / 수량 / 금액 / 결제 버튼
- 정상: 담은 상품을 담은순 정렬로 표시 (출처: 장바구니 API)
- 빈 상태: "담은 상품이 없어요" + 추천 상품 CTA
- 로딩: 스켈레톤
- 에러: "불러오지 못했어요" + 재시도 버튼
- 예외: 품절이면 비활성+표기(정책 P-CART-02), 재고<수량이면 수량 자동 조정
- 권한: 비로그인은 로컬 저장 후 로그인 유도
"""


def lint(text):
    low = text.lower()
    results = []
    for label, kws in CHECKS:
        hit = any(k.lower() in low for k in kws)
        results.append((label, hit))
    return results


def report(text, name):
    results = lint(text)
    passed = sum(1 for _, h in results if h)
    print(f"spec lint: {name}  ({passed}/{len(results)} checks present)\n")
    for label, hit in results:
        mark = "[ok]" if hit else "[MISSING]"
        print(f"  {mark:>9}  {label}")
    missing = [l for l, h in results if not h]
    if missing:
        print(f"\n  -> add before handoff: {', '.join(missing)}")
    else:
        print("\n  -> all signal elements present (human review still required)")
    return passed == len(results)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        report(DEMO, "DEMO (cart screen)")
    elif sys.argv[1] == "-":
        report(sys.stdin.read(), "<stdin>")
    else:
        try:
            with open(sys.argv[1], encoding="utf-8") as f:
                report(f.read(), sys.argv[1])
        except OSError as e:
            print(f"cannot read {sys.argv[1]}: {e}")
            sys.exit(1)
