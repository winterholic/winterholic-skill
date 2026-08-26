---
name: caveman-evolution
topic: caveman 스킬 — 압축 응답 모드. 강도 6단계 + 자동 트리거 + SKIP 룰의 정교한 트리거 설계 사례
category: 06-case-studies
added: 2026-05-26
source: 사용자 셋업 현황 (skills 목록) + work-history 2026-05-26 (caveman 카테고리 협조 언급)
tags: [case-study, caveman, trigger-design, intensity-levels]
status: active
verification_note: 외부 검증 X — 사용자 셋업 내부 사례. work-history·skills-estimate 점수 등 1차 사료는 내부 기록.
---

# Case Study — caveman (91.4/A+)

## 핵심 한 줄
**"발화 의도 → 발동 강도"를 6단계로 매핑하고 SKIP 룰로 false positive를 잡는** 정교한 트리거 설계. 본 사용자 셋업에서 가장 높은 점수(91.4/A+).

## 설계 특징

1. **강도 6단계**: lite, full(기본), ultra, wenyan-lite, wenyan-full, wenyan-ultra. 한 스킬이지만 컨텍스트별 출력 형태가 6가지
2. **자동 트리거 5개 카테고리**:
   - 명시적 짧음 요청 ("짧게", "TL;DR", "핵심만")
   - 빠른 진행·캐주얼 톤 ("ㄱㄱ", "빨리", "당장")
   - 디버깅 반복 루프 ("왜 안 돼", "버그", "고쳐줘")
   - 확인성 질문 ("맞아?", "되나?", "있어?")
   - 의사결정 확인 ("이거 해도 돼", "괜찮아?")
3. **SKIP 룰** — 같은 메시지에 "자세히/설명해줘/이유는/근거/원리/RFC/회고" 등이 함께 있으면 자동 트리거 무시. **false positive 차단**
4. **세션 영속성** — 한 번 발동되면 끝까지 유지. 해제 명령("stop caveman", "원래대로")로만 종료
5. **자동 비활성 전환** — 보안 경고·되돌릴 수 없는 작업·다단계 순서 안내에서는 일시적으로 일반 문체. 끝나면 재개

## 무엇이 가르치는가

1. **트리거는 카테고리화** — 단일 키워드 나열보다 의도별 분류가 정밀도 높임
2. **SKIP 룰 필수** — 자동 발동 스킬은 SKIP 없으면 사용자 짜증. 반대 의도 키워드 명시
3. **강도 자체가 한 축의 결정** — 사용자 발화의 강도(짜증·다급함·캐주얼)에 따라 출력 강도 매핑
4. **자동 일시 해제** — 강제 발동 영역에 "정확성 우선" 출구를 박아둠. 신뢰 비용 ↓

## 본 사용자 최우선 가치와의 정합

본 사용자 최우선 가치 = **trivial 작업 속도 손해 경계**. caveman이 이 가치를 가장 직접적으로 충족 — trivial 발화에 자동 발동, 비-trivial 발화엔 SKIP. 다른 신설 스킬(verification·systematic)도 강도 자동 선택 권장의 원형이 됨.

## 본 스킬과의 연계

- [[skill-description-tuning]] *(예정)* — caveman description 양식이 표준
- [[trigger-category-pattern]] *(예정)* — 5 카테고리 + SKIP 룰 패턴
- [[systematic-debugging-evolution]] — caveman 카테고리(3)와 협조하는 패턴

## 관련 자료
- [[handoff-evolution]]
- [[verification-evolution]]
- [[systematic-debugging-evolution]]

## 출처
- 본 사용자 skills 목록의 caveman description (5 카테고리 + SKIP)
- work-history 2026-05-26 line 176, 178 (트리거 카테고리 협조 언급)
- skills-estimate 91.4/A+ 평가
