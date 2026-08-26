---
name: verification-before-completion
description: >-
  완료·통과·동작·수정 완료를 주장하기 전 방금 실행한 evidence를
  응답에 의무 포함시킨다. 사용자가 "테스트 통과했어?", "끝났어?", "동작해?"
  등을 묻거나 Claude가 "완료/끝났/통과/done/마쳤어/고침/수정함" 같은 단어를
  쓸 때 자동 발동. 이전 턴의 결과 재인용 금지, 같은 응답 안에서 새로 실행한
  명령 + 출력 1~3줄 인용 필수. 실제 실행이 불가능한 경우(키·승인·외부 의존)
  "미실행: 사유" 한 줄로 면제. 설계·논의·읽기 전용 조회에는 발동하지 않는다.
  caveman ultra 모드와 동시 활성 시 evidence는 1~2줄로 축약 허용.
---

# verification-before-completion

## 비유로 한 줄

**식당 주방 비유** — 손님이 "음식 다 됐어?" 물을 때 "다 됐어요"라고만 답하는 셰프 vs "방금 간 봤어요, 짜지 않음. 플레이팅 1분"이라 답하는 셰프. 후자가 verification이다. 같은 응답 안에서 **방금 한 검증의 결과 한 줄**을 동봉한다. 검증 자체가 무리면 "간 못 봤음: 손님 미각 우선" 같이 면제 사유를 명시한다.

## Iron Law

**완료·통과·동작·수정 주장은 fresh evidence를 동반해야 한다.**

"fresh" = 같은 응답 안에서 실제로 명령을 실행하고 그 출력을 인용한 것.
이전 턴 결과 재인용·예측·일반론은 evidence가 아니다.

## 트리거 키워드 (자동 발동)

응답 작성 중 다음 단어를 쓰려고 하면 멈추고 evidence부터 확보:

| 카테고리 | 키워드 |
|---------|--------|
| 완료 주장 | 완료, 끝났, 마쳤, 다 됐, done, finished |
| 통과 주장 | 통과, 동작 확인, 성공, passing, passed |
| 동작 보증 | 동작해, 잘 돌아가, 문제 없, works, no issues |
| 수정 완료 | 수정함, 고침, 버그 해결, fixed |

## SKIP — 발동 안 함

- 설계·논의 ("이렇게 짜면 어때?")
- 읽기 전용 조회 ("이 함수 뭐 함?")
- 외부 의존으로 실행 불가 (단 "미실행: 사유" 명시)
- caveman ultra 모드의 1줄 확인성 답변
- 사용자가 명시적으로 "evidence 생략", "빨리", "그냥 끝내" 요청 → evidence 생략 + 응답 끝에 "검증 생략 (사용자 요청)" 표기

## 판단 불가 시 (4요소)

evidence 확보가 모호한 경계 사례에서는 사용자에게 1회 질의:
- 누가: caveman이 직접 (다른 에이전트 위임 금지)
- 언제: 즉시, evidence 작성 직전
- 어떻게: "이 작업의 evidence 어떤 명령으로 확보하면 될까요? (생략 가능)" 한 줄
- 기대값: 사용자 답이 명령이면 그 명령 실행 후 인용. "생략"이면 "검증 생략 (사용자 요청)" 표기. 무응답이면 lite 강도로 진행 (이미 보여준 Edit 결과를 evidence로 인정).

## 외부 의존성

evidence 확보에 쓰는 도구·없을 때 fallback:

- `pytest` (테스트 실행): 없으면 `python -m unittest` 또는 `python -c "import mod; mod.test()"`
- `curl` (HTTP 검증): 없으면 `python -c "import urllib.request; ..."`
- `git diff` (변경 확인): 없으면 `diff -u <원본> <수정본>`
- `python -c` (모듈 import·함수 호출): 항상 가능
- 모두 불가한 격리 환경: "미실행: <도구> 부재" 명시 후 정적 추론 evidence (코드 인용 + 추론 1줄)

## Evidence 형식

응답 본문 안에 다음 형태로 포함:

```
[주장 본문]

방금 검증:
$ <실제 실행 명령>
<출력 핵심 1~3줄, 5줄 초과면 ... 처리>

[검증 못한 부분 있으면] 미실행: <사유>
```

## 좋은 응답 / 나쁜 응답

❌ "테스트 추가했고 동작할 거예요"
✅ "테스트 추가. 방금 검증: $ pytest tests/foo.py → 3 passed in 0.4s"

❌ "수정 완료"
✅ "수정 완료. $ git diff src/foo.py | head -5 → ... 변경 확인"

❌ "통과합니다"
✅ "통과. $ pytest -k test_login → 1 passed"

## 강도 자동 선택

- 일반: 위 형식 그대로
- caveman lite 동시 활성: "방금 검증" → "검증:" 으로 단축
- caveman ultra 동시 활성: evidence 1줄 + 명령 + 결과 카운트만
  예: `$ pytest tests/ → 5 passed`

## 자가 점검 (응답 직전)

1. 응답에 트리거 키워드가 있나?
2. 같은 응답 안에서 실제로 명령을 실행했나?
3. 못 했다면 "미실행: 사유"를 명시했나?
세 질문 모두 통과해야 응답 발행.

## 다른 스킬과의 관계

- caveman: 강도만 조정, verification 룰은 유지
- handoff: 인계 문서의 "## 현재 상태"에 명시한 완료 항목도
  evidence 동반 (없으면 "주장 단계"라고 표기)
- systematic-debugging: 디버깅 후 "고침" 주장 시 회귀 케이스
  재실행 evidence 필수

## 갱신 정책

- SKILL.md·match-tests.md 갱신 시 git diff로 변경 확인 후 commit (사용자 명시 요청 시).
- 새 트리거 키워드 추가 시 match-tests.md에 회귀 시나리오 1개 이상 동반 추가.
- description의 트리거 키워드 80개 상한, SKIP 25개 상한. 초과 시 정밀도 재검토.

## 디렉토리 구조

```
~/.claude\skills\verification-before-completion\
├── SKILL.md
└── references/
    └── match-tests.md
```
