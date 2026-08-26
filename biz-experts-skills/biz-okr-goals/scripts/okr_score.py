#!/usr/bin/env python3
"""OKR 0~1 채점 계산기.

KR별 점수(0.0~1.0)를 입력하면 O별 평균과 전사 달성도를 산출하고,
Google re:Work 관행(sweet spot 0.6~0.7, >0.7 지속 시 "야심 부족")에 따라
경고를 붙인다. 채점 척도는 조직마다 다르므로 결과는 참고용이다.

사용:
    python okr_score.py                # 데모(내장 예시)
    python okr_score.py okr.json       # JSON 입력

JSON 형식:
    {
      "Objective 1": {"type": "aspirational", "krs": [0.6, 0.5, 0.8]},
      "Objective 2": {"type": "commit",       "krs": [1.0, 0.9]}
    }
    - type: "aspirational"(stretch, 0.7=성공) | "commit"(1.0 기대)
"""
import json
import sys

# Google re:Work 관행값 (evidence.md §2 검증). 조직별로 다름 — 교리 아님.
SWEET_LOW, SWEET_HIGH = 0.6, 0.7


def score_objective(krs):
    """KR 점수 리스트 → O 점수(단순 평균, re:Work 방식)."""
    if not krs:
        return 0.0
    return sum(krs) / len(krs)


def assess(o_type, o_score):
    """유형·점수로 코멘트. aspirational은 0.7도 성공, commit은 1.0 기대."""
    if o_type == "commit":
        if o_score >= 1.0:
            return "달성(commit=1.0 기대 충족)"
        return f"미달(commit형은 1.0 기대 — 우선순위/실행 점검)"
    # aspirational(stretch)
    if o_score > SWEET_HIGH:
        return f"초과({o_score:.2f}>0.7) — 지속되면 '야심 부족, 더 크게' 신호(re:Work)"
    if SWEET_LOW <= o_score <= SWEET_HIGH:
        return f"sweet spot(0.6~0.7) — 적정 야심"
    return f"저조({o_score:.2f}<0.6) — 목표 과대 or 실행 격차, 회고에서 원인 분리"


def run(okrs):
    all_o = []
    print("=== OKR 채점 (0~1) ===")
    for name, data in okrs.items():
        o_type = data.get("type", "aspirational")
        krs = data.get("krs", [])
        o_score = score_objective(krs)
        all_o.append(o_score)
        kr_str = ", ".join(f"{k:.2f}" for k in krs)
        print(f"\n[{name}]  ({o_type})")
        print(f"  KR: {kr_str}")
        print(f"  O 점수: {o_score:.2f}  → {assess(o_type, o_score)}")
    if all_o:
        overall = sum(all_o) / len(all_o)
        print(f"\n전체 평균 O 점수: {overall:.2f}")
        if overall > SWEET_HIGH:
            print("  ⚠️ 전반적으로 0.7 초과 지속 = 목표가 안전할 수 있음(야심 상향 검토).")
    print("\n※ 채점 척도는 조직마다 다름 — 위 관행값은 Google re:Work 기준(교리 아님).")


DEMO = {
    "O1: 신규 사용자가 첫 주에 핵심 가치를 경험": {
        "type": "aspirational", "krs": [0.65, 0.5, 0.8]
    },
    "O2: 결제 안정성 확보": {"type": "commit", "krs": [1.0, 0.9]},
}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            run(json.load(f))
    else:
        run(DEMO)
