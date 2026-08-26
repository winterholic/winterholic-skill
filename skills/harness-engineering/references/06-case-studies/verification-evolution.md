---
name: verification-evolution
topic: verification-before-completion 스킬의 56/D → 89/A 진화 — 골격→평가→보강→재평가 루프
category: 06-case-studies
added: 2026-05-26
source: work-history 2026-05-26 (line 175-243, 267-305, 324-357)
tags: [case-study, verification, skills-estimate, iteration]
status: active
verification_note: 외부 검증 X — 사용자 셋업 내부 사례. work-history·skills-estimate 점수 등 1차 사료는 내부 기록.
---

# Case Study — verification-before-completion (56 → 89, 4회 반복)

## 핵심 한 줄
**"완성도 자체평가는 후한 편향이 강하다"** — Generator/Evaluator 분리해 골격(56/D)을 4회 반복으로 89/A까지 끌어올린 사례. 본 스킬 신설 표준 절차의 원형.

## 진화 흐름

| 단계 | 점수 | 무엇이 부족했나 | 보강 |
|------|------|----------------|------|
| 1차 골격 | 56/D | 본질·트리거·SKIP·이득 4축 중 SKIP/이득이 모호, fallback 처리 없음 | D2 사용자 거부 fallback 추가, 회귀 시나리오(TP 6 + FP 2 + Conflict 2 = 10건) 추가 |
| 2차 보강 | 72/B | 본문은 채워졌으나 비유 부족 → 직관 안 잡힘, README 없음 | E1 비유 ("식당 셰프 — '간 봤어요, 짜지 않음' 한 줄 동봉") 추가 |
| 3차 보강 | 86/A | F1 README 부재 | references/README.md 신규 |
| 4차 보강 | 89/A | 안정 영역, Stop hook 승격 대기 (A급 4주 연속 조건) | (없음 — 운영 단계) |

## 무엇이 결정적이었나

1. **자체평가 후 객관 평가** — 사용자가 skills-estimate 정량 도구 호출. self-eval은 75/B로 후하게 나왔으나 도구는 56/D. **Generator/Evaluator 분리 효과**
2. **회귀 시나리오 명시** — TP(true positive 6건) + FP(false positive 2건) + Conflict(다른 스킬과 충돌 2건). 트리거 정확도 검증 가능
3. **카테고리별 가중치** — E1 친절함이 30% 가중. 작은 비유 한 줄이 점수 +3
4. **결정 직후 재평가** — 보강 후 다시 평가. 점수 변화 추적 → 정체 시 다른 축 시도

## 이 패턴이 가르치는 것

- 새 스킬 신설 시 **자체평가 후 반드시 객관 평가** 한 번
- 한 번에 A급 못 가도 OK. **반복 루프**가 핵심
- 가중치 큰 카테고리(E1 친절함·D2 fallback) 우선 보강이 비용 대비 효과 큼
- A급 진입 후에도 4주 운영 데이터 누적 → Stop hook 승격 검토

## 본 스킬과의 연계

이 case는 [[stop-hook-promotion-criteria]]의 입력 자료. verification이 A급 4주 연속(2026-05-26 시점 1주차) 후 Stop hook 승격 결정 시점에 본 case 다시 본다.

## 관련 자료
- [[systematic-debugging-evolution]] — 동일 절차로 진행된 자매 사례
- [[stop-hook-promotion-criteria]] — 승격 판단
- [[skills-estimate-methodology]] *(예정)* — 평가 도구 자체

## 출처
- work-history 2026-05-26: line 175-243, 267-305, 324-357
- skills-estimate 평가 보고서 (2026-05-26)
