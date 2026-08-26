---
name: systematic-debugging
description: >-
  같은 버그를 두 번째 이상 시도하는 순간 fix 제안을 멈추고
  root cause 4단계 조사(콜스택→business→환경→로그)를 강제한다.
  caveman 디버깅 카테고리(3) "왜 안 돼/에러 봐줘"의 첫 시도는 짧은 답
  유지, 같은 에러 2번째부터 본 스킬 자동 발동. 사용자가 "또 안 됨",
  "여전히", "아직도", "같은 에러", "두 번째 시도", "왜 그런지",
  "근본 원인", "root cause", "이유는" 등을 언급하면 트리거. 첫 시도여도
  사용자가 명시적으로 root cause를 요청하면(예: "왜 그런지 자세히")
  발동. Phase 1 끝나기 전 fix 제안 금지. evidence 인용은
  verification-before-completion 규칙 따른다.
---

# systematic-debugging

## 비유로 한 줄

**의사 진료 비유** — 첫 진료 "두통 있어요" → "타이레놀 드세요"는 OK (시간·정보 효율). 두 번째 진료 "약 먹어도 두통" → 그제서야 동일 약 처방하는 의사는 위험하다. 이때부터 문진(콜스택)·기저 질환(business)·복용 약·환경(env)·임상 데이터(log) 4단계로 거슬러 올라간다. 패치(fix)는 root cause를 본 뒤에. 첫 시도는 caveman 빠른 답에 양보하고, 2차부터 본 스킬이 강제로 4단계 모드 전환.

## Iron Law

**같은 버그 2회차부터 fix 전에 root cause 조사 강제.**

첫 시도의 fix는 "그럴듯한 패치"이기 쉽다.
두 번째부터는 멈추고 4단계로 거슬러 올라간다.

## 트리거

| 신호 | 발동 시점 |
|------|----------|
| 같은 에러 메시지 2회+ | 직전 N턴에 동일·유사 에러 |
| "또 안 됨", "여전히", "아직도" | 사용자 발화 |
| "두 번째", "3번째", "N번째 시도" | 명시적 카운트 |
| "왜 그런지", "근본 원인", "root cause" | 첫 시도여도 발동 |

**발동 안 함**: 첫 시도 "왜 안 돼", "에러 봐줘"
→ caveman 디버깅 카테고리가 짧은 답 우선.

## 판단 불가 시 (4요소)

evidence 확보 불가·Phase 1 출력이 너무 방대한 경우 사용자에게 1회 질의:
- 누가: caveman이 직접
- 언제: Phase 1 중간, 콜스택 너무 깊어질 때
- 어떻게: "콜스택 N단계까지 추적했는데 더 갈까요? 아니면 가설로 진행할까요?" 한 줄
- 기대값: "더" → 계속 추적. "가설" → Phase 4 가설 검증 모드로 전환. 무응답 → Phase 1 5단계까지만 가고 Phase 2로.

## 외부 의존성

조사에 쓰는 도구·없을 때 fallback:

- `grep -rn` (콜스택 역추적): 없으면 `find . -name "*.py" -exec grep -l ...`
- `git log -p` (변경 이력): 없으면 `git log --all` + `git show <hash>`
- `breakpoint()` / `pdb` (실행 중 검사): 없으면 `print` 디버깅
- `print` / 로그 (Phase 4 가설 검증): 항상 가능
- IDE·디버거 없는 환경: print + 재실행으로 대체, "미실행: <도구> 부재" 명시

## 4단계 절차

### Phase 1 — 콜스택 역추적 (root-cause-tracing)

증상 발생 지점에서 시작해 "이 값이 어디서 왔나?"를
데이터 진입점까지 거슬러 간다.

- 각 layer 실제 값 dump (가정 금지)
- `grep -rn`, `git log -p`, breakpoint·print 활용
- **이 Phase 끝나기 전 fix 제안 금지**

### Phase 2 — Business logic 검증

진입점의 값이 의도와 같은가?
- 변환 함수가 명세대로 동작하나?
- 외부 API 응답 스키마가 코드 가정과 같나?
- 가정 하나하나에 evidence 확보

### Phase 3 — Environment 격리 (defense-in-depth)

코드가 멀쩡한데 환경에서 망가지나?
- .env, OS, 버전, 의존성, 네트워크, 권한
- dev/prod diff
- 하나씩 격리해 변수 줄이기

### Phase 4 — Logging으로 가설 검증

- 가설 세우고 → 그 가설이 옳다면 로그에 X가 찍힘 예측
- 실제 로그 확인 → 가설 폐기 or 확정
- 폐기 시 Phase 1로 복귀

## SKIP — 발동 안 함 / 부분 발동

- 첫 시도 디버깅 (caveman 카테고리(3)에 양보)
- 명백한 typo·import 미존재 (1턴에 fix 가능)
- 사용자가 명시적으로 "그냥 빨리 고쳐줘", "Phase 그만", "패치만", "분석 됐고 fix만" 요청 → Phase 1·2만 수행하고 fix 제안. 응답 끝에 `Phase 3·4 생략 (사용자 요청)` 표기. 단 Iron Law(Phase 1 끝나기 전 fix 금지)는 유지 — Phase 1 자체는 5분 안에 끝낼 수 있도록 압축 출력으로
- 사용자가 "다 멈춰", "다시 1차로", "그냥 caveman으로" 요청 → 본 스킬 비활성, caveman 짧은 답으로 복귀. 응답 끝에 `systematic-debugging 해제 (사용자 요청)` 표기

## 출력 형식

```
[증상 정리]

Phase 1: 콜스택 추적
$ <명령>
<출력>
→ <발견>

Phase 2: ...

근본 원인: <한 줄>
수정 제안: <fix 코드> (verification 룰 적용)
```

## 좋은 응답 / 나쁜 응답

❌ "401 떠요? Authorization 헤더 확인해보세요" (2차 시도에서)
✅ "Phase 1: $ python -c 'from run import _get_token; print(_get_token())' → 응답 키 'token'인데 코드는 'access_token' 가정. 근본 원인: 키명 불일치"

❌ "음... 토큰 만료 아닐까요?" (가설을 단언처럼)
✅ "가설: 토큰 만료. 검증: $ python -c '...print(expires_at)' → 미래 시각. 가설 폐기, Phase 1 복귀"

❌ "고쳤어요, 다시 시도해보세요"
✅ "근본 원인 = 키명 불일치. fix 후 회귀 검증: $ pytest tests/test_auth.py → 2 passed"

## 자가 점검

- 같은 에러 2회 이상? → 발동
- Phase 1 안 거치고 fix 제안? → 멈추고 Phase 1 복귀
- 가정으로 단언? → evidence로 교체

## 다른 스킬

- caveman: 1차는 caveman, 2차부터 본 스킬
- verification-before-completion: Phase 2 evidence·
  fix 후 회귀 검증은 verification 룰
- handoff: 인계 시 "## 시도했지만 실패한 접근"에
  Phase 1~4 결과 요약

## 갱신 정책

- SKILL.md·match-tests.md 갱신 시 git diff로 변경 확인 후 commit (사용자 명시 요청 시).
- 새 트리거 키워드 추가 시 match-tests.md에 회귀 시나리오 1개 이상 동반 추가.
- description의 트리거 키워드 80개 상한, SKIP 25개 상한. 초과 시 정밀도 재검토.

## 디렉토리 구조

```
~/.agents/skills/systematic-debugging/
├── SKILL.md
└── references/
    └── match-tests.md
```
