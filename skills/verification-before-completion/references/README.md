# verification-before-completion — 사용 가이드

이 스킬은 Claude가 "완료/통과/동작/수정"을 주장하기 전 **방금 실행한 검증 evidence**를 응답에 의무 포함시킨다. "fresh"가 핵심 — 이전 턴의 결과 재인용·예측·일반론은 evidence가 아니다.

## 한 줄로 무엇을 하나

식당에서 셰프가 "다 됐어요"가 아니라 "방금 간 봤어요, 짜지 않음"이라 답하게 만든다. 응답 옆에 작은 검증 한 줄.

## 디렉토리 구조

```
verification-before-completion/
├── SKILL.md          # 본문 — Iron Law, 트리거, SKIP, 외부 의존성, Evidence 형식, 강도 자동 선택, 4요소 질의
└── references/
    ├── README.md     # 이 파일 — 사용 가이드·운영 절차
    └── match-tests.md # 회귀 시나리오 (TP 6 + FP 2 + Conflict 2 = 10)
```

## 운영 절차

| 상황 | 절차 |
|------|------|
| 새 트리거 키워드 추가 | description 갱신 → match-tests.md에 TP 시나리오 1+ 추가 → 동일 메시지로 실사용 검증 |
| false positive 발견 | match-tests.md에 FP 시나리오 추가 → SKIP 키워드 또는 트리거 정밀도 보강 |
| 다른 스킬과 충돌 | match-tests.md Conflict 섹션에 시나리오 추가 → SKILL.md "다른 스킬과의 관계" 섹션 보강 |
| 정량 평가 | skills-estimate 스킬에 본 SKILL.md 경로 전달. 목표 A 등급(85+) |

## 활용 시나리오 (예시)

- **example-org api-gateway 새 endpoint**: "엔드포인트 추가 완료" 응답 시 자동 발동 → `pytest tests/test_orders.py` 실행 + 결과 인용
- **nxt-api-spec 함수 추가**: "함수 추가했어요" 응답 시 → `python -c "import run; print(run._call_ka10063.__doc__)"` import 검증
- **vault 파일 정리**: "정리 완료" 응답 시 → `wc -l <file>` 또는 `head -10 <file>` 결과 인용

## 강도 조절

|  강도  | 발동 조건 | Evidence |
|--------|----------|---------|
| **lite** (default 80%) | typo·rename·import·CSS·주석 같은 trivial Edit | 이미 보여준 Edit 결과 자체. 새 명령 실행 없음 |
| **full** (15%) | 함수·로직·리팩터링 | 직전 Bash 호출 재인용 OK + 새 명령 0~1개 |
| **ultra** (5%) | 새 endpoint·API·DB 스키마·테스트 추가, 또는 사용자 "확실히" 명시 | 새 명령 1~3개 실행, evidence 의무 |

## 회귀 검증

새 키워드 추가·SKIP 조정 후엔 `match-tests.md`의 모든 시나리오를 머릿속으로 실행하고 기대 동작과 일치하는지 확인. 5개 이상 실패하면 정밀도 재검토.

## 관련 스킬

- **caveman**: 강도만 조정, verification 룰은 유지
- **handoff**: 인계 문서의 "## 현재 상태" 완료 항목도 evidence 동반
- **systematic-debugging**: fix 후 회귀 검증은 verification 룰 적용
- **skills-estimate**: 정량 평가 도구
