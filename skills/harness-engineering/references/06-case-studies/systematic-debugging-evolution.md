---
name: systematic-debugging-evolution
topic: systematic-debugging 스킬의 66/C → 87/A 진화 — 결정 트리·도메인 특화 fallback의 효과
category: 06-case-studies
added: 2026-05-26
source: work-history 2026-05-26 (line 176-243, 274-305, 324-357)
tags: [case-study, systematic-debugging, skills-estimate, root-cause]
status: active
verification_note: 외부 검증 X — 사용자 셋업 내부 사례. work-history·skills-estimate 점수 등 1차 사료는 내부 기록.
---

# Case Study — systematic-debugging (66 → 87, 3회 반복)

## 핵심 한 줄
**"5턴 우왕좌왕 → 1턴 root cause"** 를 만든 디버깅 절차 스킬. verification과 자매 신설로 같은 절차 거쳐 B+ → A. **도메인 특화 fallback**(Phase 1 진행 질의)이 결정적.

## 진화 흐름

| 단계 | 점수 | 부족 | 보강 |
|------|------|------|------|
| 1차 골격 | 66/C | 4단계 절차는 있으나 거부 fallback 모호, 비유 없음 | D2 거부 fallback ("다 멈춰/다시 1차로/그냥 caveman으로" 부분 발동 분기) |
| 2차 보강 | 77/B | 친절함(E1) 약함 | E1 비유 ("의사 진료 — 첫 진료엔 타이레놀 OK, 둘째 진료엔 4단계 문진") |
| 3차 보강 | 83/B+ | F1 README 없음, A 진입 2점 모자람 | references/README.md 신규 |
| 4차 보강 | 87/A | 안정 영역 | (운영 단계) |

## verification과 다른 점

- **도메인 특화 fallback**: verification은 "evidence 명령 질의", systematic은 "Phase 1 진행 질의". 같은 D2 카테고리지만 도메인 맞춤
- **비유 유형 다름**: verification은 "끝맺음 후 한 줄 동봉"(셰프), systematic은 "단계별 진단 강도 조절"(의사). 둘 다 사용자 직관과 맞물림
- **트리거 카테고리 협조**: caveman(3) 카테고리와 협조. 디버깅 발화 + 압축 발화가 동시 등장하면 systematic이 우선, caveman은 톤만

## 무엇이 가르치는가

1. **자매 스킬 동시 신설** 절약 효과 — verification·systematic을 같은 슬롯에서 진행, 절차 공통 90%
2. **카테고리 가중치 활용** — D2(거부 fallback) 20% + E1(친절) 30%로 50% 차지. 두 축만 잡으면 +20점 가능
3. **+2점이 A 진입 결정** — 83 → 85 cliff. README 한 장 추가가 cliff 넘기

## 본 스킬과의 연계

이 case는 본 사용자 학습 루프의 **굳히기 결정** 모범 사례. 메모리 누적(분석 11/20)은 약한데, 스킬 신설 절차(굳히기 15/20)는 양호한 영역이라는 진단의 근거.

## 관련 자료
- [[verification-evolution]] — 자매 사례
- [[caveman-evolution]] — 톤 협조 사례
- [[learning-loop-diagnosis]] *(예정)* — 5요소 평가

## 출처
- work-history 2026-05-26: line 176-243, 274-305, 324-357
- skills-estimate 평가 보고서 (2026-05-26)
