---
name: session-distill
description: "주간 세션 증류 — work-history(이미 해석된 맥락)를 입력으로 2회 이상 반복된 마찰을 추출해, memory·하네스(CLAUDE.md/hook/스킬) 개선 후보를 '제안만' 한다(자동 기록 X, 사람 검수 후 승격). 주로 토요일 오전 로컬 cron이 `claude -p` headless로 호출해 배치 실행되며, 사용자가 '세션 증류', 'session distill', '주간 회고 돌려', '하네스 개선점 뽑아', 'weekly review', '반복된 마찰 뽑아줘'를 언급하면 수동으로도 트리거. harness-engineering 학습루프의 분석 단계(굳히기 전)를 담당 — 굳히기 자문은 harness-engineering, 새 스킬 생성은 skill-creator, 스킬 채점은 skills-estimate로 위임. 단순 work-history 조회나 즉석 memory 저장 요청, 1회성 회고에는 발동 안 함."
---

# Session Distill — 주간 세션 증류

## 무엇을·왜

여러 세션에 걸쳐 사용자가 반복해서 같은 교정을 하거나, 같은 하네스 마찰(시끄러운 hook, 비대한 CLAUDE.md, 안 걸리는 스킬 트리거)이 되풀이되는데도 그게 규칙·메모리·설정으로 **굳혀지지 않으면**, 매번 같은 마찰을 다시 겪는다. 이 스킬은 그 반복을 자동으로 **탐지·증류**해서 개선 후보를 모아둔다.

핵심 발상(chopratejas/headroom의 `learn` 루프에서 흡수):

- 사용자 셋업엔 이미 **output**(CLAUDE.md·memory)과 좋은 **input**(work-history = 이미 해석된 맥락)이 있다. 빠진 건 그 사이의 **자동 증류 단계** 하나뿐 — 이 스킬이 그걸 채운다.
- raw transcript를 LLM으로 digest할 필요 없다. work-history가 이미 "무슨 의도로 무엇을 했나"로 해석돼 있으므로 **digest가 끝난 입력**이다. 바로 패턴만 뽑는다.

이 스킬은 **탐지·증류만 자동**, **기록은 사람**이 한다. 그래야 프리픽스(CLAUDE.md/memory) bloat로 지시가 희석되는 걸 막는다.

## 4대 원칙 (어기지 말 것)

1. **증거 임계값 2회+** — 서로 다른 세션/날짜에서 **2회 이상** 반복돼야 후보로 승격. 1회성은 노이즈라 버린다(과적합 방지).
2. **마커블록만 건드린다** — 후보는 오직 `_candidates.md`의 `<!-- distill:start -->`~`<!-- distill:end -->` 블록 안에만 쓴다. 사용자가 손으로 쓴 영역·실제 memory 파일·CLAUDE.md는 **절대 자동 수정 금지**. 재실행해도 같은 블록을 갱신할 뿐 중복이 쌓이지 않는다(멱등).
3. **merge·dedup, 모순일 때만 drop** — 이미 있는 후보는 증거 횟수만 올린다. 이미 채택된 memory/CLAUDE.md 규칙과 겹치면 제외. 새 증거가 기존 후보와 **모순**되면 합치지 말고 그 후보를 drop(설익은 신호 제거, bloat 방지).
4. **배치·오프라인** — 실시간 작업 루프에 끼어들지 않는다. 주말 cron으로 떨어져 돌기 때문에 실패해도 평일 작업에 손실 0.

## 실행 흐름

### 1단계 — 입력 수집

```bash
# 기본: 최근 7일 work-history (인자로 기간 조정 가능)
ls -t "~/.claude/artifacts/work-history/"*.md | head -8
```

- 최근 **7일치** work-history `.md`를 읽는다(주간). cron이 토요일 오전에 돌므로 직전 한 주가 대상.
- 기존 후보 파일 `~/.claude/projects/<project-id>/memory/_candidates.md`와, 이미 채택된 것들(`MEMORY.md` + `memory/*.md` + 글로벌 `~/.claude/CLAUDE.md`)을 함께 읽어 **dedup 기준선**으로 삼는다.

### 2단계 — 마찰 추출 (2회+ 반복만)

work-history를 훑어 **서로 다른 날짜/세션에서 2회 이상** 나타난 것만 후보로. 두 갈래로 본다:

**A. 사용자 → 클로드 마찰 (→ memory feedback 후보)**
- 반복된 교정·되돌림 요청 ("아까처럼 하지 마", "다시 되돌려")
- 반복 실수 패턴 (같은 류 오류를 여러 세션에서 반복)
- 반복 선호 표명 (매번 같은 방식·톤·포맷을 요구)
- 실수 신호 누적 — `;;` / `ㅡㅡ` 가 같은 맥락에서 반복 (기존 `feedback_mistake_signals` memory 참조)

**B. 하네스 마찰 (→ CLAUDE.md/hook/스킬 개선 후보)**
- 같은 hook이 반복적으로 시끄럽다고 언급됨 → hook 조정 후보 (`hook-noise` 안티패턴)
- CLAUDE.md/메모리가 길어 지시가 흐려진다는 정황 → 정리 후보 (`description-bloat`·`memory-overuse`)
- 어떤 스킬이 떠야 할 때 안 뜨거나 엉뚱하게 뜸 → description 트리거 튜닝 후보
- 매번 수동으로 하는 동일 절차가 반복됨 → 스킬/스크립트화 후보

추출 시 각 후보에 **근거(어느 날짜·어떤 맥락에서 몇 번)**를 반드시 붙인다. 근거 없는 추론은 적지 않는다.

### 3단계 — dedup·merge

- 이미 `MEMORY.md`/`memory/*.md`/`CLAUDE.md`에 반영된 규칙과 같은 취지면 **제외**.
- `_candidates.md`에 같은 후보가 이미 있으면 **증거 횟수·날짜만 갱신**(중복 추가 X).
- 새 증거가 기존 후보와 모순되면 그 후보를 **drop**하고 로그에 한 줄 남긴다.

### 4단계 — 후보 출력 (제안만)

`~/.claude/projects/<project-id>/memory/_candidates.md`의 마커블록을 **통째로 다시 쓴다**(블록 밖은 손대지 않음). 형식:

```markdown
<!-- distill:start -->
<!-- 이 블록은 session-distill이 자동 생성·갱신한다. 채택할 항목만 골라 실제 memory/CLAUDE.md로 옮기고, 여기서 지우면 된다. 직접 편집해도 다음 실행 때 덮어쓰일 수 있으니 채택/기각만. -->
_마지막 증류: 2026-06-14 (대상: 06-08~06-14)_

### 후보 1 — [memory] 응답 끝에 항상 다음 작업 제안 금지
- **유형**: memory(feedback) 후보
- **증거**: 06-09(슬랙 건 "그만 제안해"), 06-12(PR 리뷰 "또 그러네ㅡㅡ") — 2회
- **제안**: feedback memory 1줄 — "요청 안 한 후속 작업 제안 자제"
- **상태**: ⬜ 미검토

### 후보 2 — [harness] stop-checklist hook이 조회만 한 턴에도 발동
- **유형**: hook 개선 후보
- **증거**: 06-10(2회), 06-13(1회) — 3회 "이거 왜 또 떠"
- **제안**: PostToolUse 마커 조건에서 read-only Bash 제외 검토 → harness-engineering 굳히기 자문 권장
- **상태**: ⬜ 미검토
<!-- distill:end -->
```

- 각 후보: 한 줄 제목 + 유형 + 근거(날짜·횟수) + 구체 제안 + 상태 체크박스.
- **절대 자동으로 실제 memory/CLAUDE.md/hook을 고치지 않는다.** 여기까지가 이 스킬의 끝.

### 5단계 — 사람 검수·승격 (스킬 밖)

실행 종료 시 사용자에게 "이번 주 후보 N건, `_candidates.md` 확인" 한 줄만 보고. 승격(실제 memory 작성·CLAUDE.md 수정·hook 조정)은 사용자가 검수 후 결정하며, 하네스 변경이면 `harness-engineering` 자문을 거친다.

## Headless 실행 계약 (cron이 부르는 법)

토요일 오전 cron(launchd)이 아래처럼 호출한다. 스킬은 이 호출을 전제로 동작한다:

```bash
cd ~ && claude -p \
  "session-distill 스킬을 실행하라. 지난 7일 work-history를 증류해 _candidates.md 마커블록을 갱신하고, 후보 건수만 요약 출력하라." \
  --allowedTools "Read,Write,Edit,Bash,Grep,Glob"
```

- 비대화형(headless)이라 사용자에게 되물을 수 없다 → **막히면 추측하지 말고** 그 사실을 `_candidates.md` 블록 안에 `<!-- distill:error ... -->` 한 줄로 남기고 종료.
- 권한이 없어 work-history를 못 읽으면 동일하게 에러 라인만 남기고 깨끗이 종료(배치라 손실 0).
- 실제 cron/launchd 등록은 별도 설정(이 스킬 파일 범위 밖).

## 안티 스코프 (하지 말 것)

- ❌ 실제 memory/CLAUDE.md/hook 자동 수정 — 제안까지만.
- ❌ 1회성 사건을 후보로 — 2회+ 증거 필수.
- ❌ 마커블록 밖(사용자 수기 영역) 수정.
- ❌ 이미 채택된 규칙 재제안 — dedup으로 거른다.
- ❌ 백업본(.bak) 생성 — `_candidates.md`는 그냥 덮어쓴다(`feedback_no_auto_backup`).
