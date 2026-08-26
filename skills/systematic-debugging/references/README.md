# systematic-debugging — 사용 가이드

이 스킬은 **같은 버그 2차 시도부터** fix 제안을 멈추고 4단계 root cause 조사를 강제한다. 첫 시도는 caveman의 빠른 답에 양보하고, 두 번째부터 발동.

## 한 줄로 무엇을 하나

의사 진료 비유 — 첫 진료엔 타이레놀 처방 OK. 두 번째 진료에 같은 처방이 위험하듯, 두 번째 디버깅엔 4단계 문진을 강제한다.

## 4단계 한눈에

```
Phase 1 (root-cause-tracing)  — 콜스택 역추적, "이 값이 어디서 왔나?"
Phase 2 (business logic)       — 진입점 값·변환 함수·외부 API 스키마 검증
Phase 3 (defense-in-depth)     — env·OS·버전·의존성·dev/prod diff 격리
Phase 4 (logging hypothesis)   — 가설 → 예측 로그 → 실제 로그 비교 → 폐기/확정
```

Phase 1 끝나기 전 fix 제안 금지. 가설 폐기 시 Phase 1로 복귀.

## 디렉토리 구조

```
systematic-debugging/
├── SKILL.md          # 본문 — Iron Law, 트리거, SKIP, 외부 의존성, 4단계 절차, 강도·자가 점검
└── references/
    ├── README.md     # 이 파일 — 사용 가이드·운영 절차
    └── match-tests.md # 회귀 시나리오 (TP 6 + FP 2 + Conflict 2 = 10)
```

## 운영 절차

| 상황 | 절차 |
|------|------|
| 새 트리거 키워드 추가 | description 갱신 → match-tests.md에 TP 시나리오 1+ 추가 → caveman 카테고리(3)과의 위계 재확인 |
| 첫 시도에서 발동(false positive) | FP 시나리오 추가 → "디버깅 2회+ 판정"의 키워드 정밀도 보강 |
| Phase가 너무 깊어짐 | SKILL.md "판단 불가 시 (4요소)"의 사용자 1회 질의 절차 활용 |
| 사용자가 "Phase 그만" 요청 | Phase 3·4 생략하고 fix 제안, 응답 끝에 생략 표기 |

## 활용 시나리오 (예시)

- **NXT API 401 반복**: 1차 "Authorization 확인" (caveman 짧은 답) → 2차 "또 401" → 본 스킬 발동 → Phase 1 `_get_token()` raw 응답 dump → 응답 키가 `token`인데 코드는 `access_token` 가정 → root cause 1턴
- **example-org api-gateway 500 반복**: 1차 "request body 확인" → 2차 "또 500" → Phase 1 콜스택 → Phase 3 dev/prod env diff → 흔한 root cause(DB 인덱스·env var typo·minor 버전 차이)
- **KRX API 빈 배열 반복**: 1차 "stex_tp 확인" → 2차 "값 넣어도 빈 배열" → Phase 1 응답 raw → Phase 2 스키마 매칭 → ESG ETP 필드명 차이 또는 구독 미설정

## 강도 조절

| 강도 | 발동 조건 | 비용 |
|------|----------|------|
| **off** (1차) | 첫 디버깅 — caveman 짧은 답만 | 0 |
| **shallow** (2차) | 같은 에러 2번째 — Phase 1·2만 | +1~2턴 |
| **deep** (3차+ 또는 명시 root cause) | Phase 1~4 전체 | +3~5턴 |

## 회귀 검증

`match-tests.md`의 TP 6개 + FP 2개 + Conflict 2개를 새 키워드 추가·SKIP 조정 후 머릿속으로 실행. 특히 caveman과의 1차/2차 위계가 깨지지 않는지 확인.

## 관련 스킬

- **caveman**: 1차는 caveman 짧은 답, 2차부터 본 스킬
- **verification-before-completion**: Phase 2 evidence 인용·fix 후 회귀 검증
- **handoff**: 인계 시 "## 시도했지만 실패한 접근"에 Phase 1~4 결과 요약
- **skills-estimate**: 정량 평가 도구
