#!/usr/bin/env python3
"""파트너 스코어카드 계산기.

파트너 평가 4축(1~5)을 입력하면 유형별 가중치로 종합 점수를 내고
진행/조건부/보류 권고를 붙인다. Crossbeam류 taxonomy(evidence.md §1)에 따라
채널 파트너는 인센티브 정렬, 기술 파트너는 실행 능력에 가중을 더 준다.

사용:
    python partner_scorecard.py                 # 데모
    python partner_scorecard.py partner.json    # JSON 입력

JSON 형식:
    {
      "name": "Acme", "type": "channel",
      "fit": 5, "execution": 3, "reputation": 4, "incentive": 2
    }
    - type: "channel"(인센티브 가중) | "tech"(실행 가중) | "strategic"(균등)
    - 각 축 1~5
"""
import json
import sys

# 유형별 가중치 (합=1.0). evidence.md §1·§3 기반: 채널=인센티브 중요, 기술=실행 중요.
WEIGHTS = {
    "channel":   {"fit": 0.25, "execution": 0.20, "reputation": 0.20, "incentive": 0.35},
    "tech":      {"fit": 0.25, "execution": 0.35, "reputation": 0.20, "incentive": 0.20},
    "strategic": {"fit": 0.25, "execution": 0.25, "reputation": 0.25, "incentive": 0.25},
}
AXIS_LABEL = {
    "fit": "전략 적합성", "execution": "실행 능력",
    "reputation": "평판·안정성", "incentive": "인센티브 정렬",
}


def evaluate(p):
    t = p.get("type", "strategic")
    w = WEIGHTS.get(t, WEIGHTS["strategic"])
    weighted = sum(p[axis] * w[axis] for axis in w)  # 1~5 척도 유지
    # 권고: 인센티브 정렬 2 이하는 win-lose 위험 → 종합 높아도 조건부 강등
    if p.get("incentive", 5) <= 2:
        verdict = "조건부 — 인센티브 재설계 전 MOU 보류(win-lose 위험, 안티패턴 2·4)"
    elif weighted >= 4.0:
        verdict = "진행 — 실행 계획·KPI·종료 조항 확정 후 체결"
    elif weighted >= 3.0:
        verdict = "조건부 — 약한 축 보강 후 재평가"
    else:
        verdict = "보류 — 적합도 부족(큰 이름이라도 억지 딜 금지)"
    return t, w, weighted, verdict


def run(p):
    t, w, weighted, verdict = evaluate(p)
    print(f"=== 파트너 스코어카드: {p.get('name','?')} (유형: {t}) ===")
    for axis in ("fit", "execution", "reputation", "incentive"):
        print(f"  {AXIS_LABEL[axis]:12} {p.get(axis,'-')}/5  (가중 {w[axis]:.2f})")
    print(f"\n  가중 종합: {weighted:.2f}/5")
    print(f"  권고: {verdict}")
    print("\n※ 큰 계약·독점·데이터 조항은 변호사 검토 필수(관할별 상이).")


DEMO = {"name": "대형 SaaS", "type": "tech",
        "fit": 5, "execution": 3, "reputation": 4, "incentive": 2}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            run(json.load(f))
    else:
        run(DEMO)
