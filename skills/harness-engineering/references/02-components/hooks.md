---
name: hooks
topic: Hooks — 결정론적 control layer
category: 02-components
added: 2026-05-26
source: Claude Code 공식 docs https://code.claude.com/docs/en/hooks
tags: [hooks, control-layer, deterministic, settings]
status: revised-2026-05-26
revision_note: 기존에 "12~13개 hook"이라고 적혀 있었으나 공식 docs 기준 ~29개로 확인. 외부 1차 자료 기반으로 전면 보정.
---

# Hooks — 결정론적 컨트롤 레이어

## 핵심 한 줄
**LLM 판단을 신뢰 못 할 자리**에 결정론적 게이트를 두는 자리. Claude Code에는 **29개 가까운 hook event**가 정의돼 있으며 (2026-05-26 공식 docs 확인), session·turn·tool·subagent·context·worktree·interaction 카테고리로 분류된다.

## 본문

### 공식 hook events (2026-05-26 확인)

전체 목록은 [[../99-sources/hook-events-claude-code-docs-2026-05-26]] 백업 참조. 카테고리 요약:

| 카테고리 | 대표 events |
|---------|-------------|
| **Session Lifecycle** | SessionStart, Setup, SessionEnd |
| **Per-Turn** | UserPromptSubmit, UserPromptExpansion, Stop, StopFailure |
| **Tool Use** | PreToolUse, PostToolUse, PostToolUseFailure, PostToolBatch, PermissionRequest, PermissionDenied |
| **Subagent & Team** | SubagentStart, SubagentStop, TeammateIdle |
| **Task** | TaskCreated, TaskCompleted |
| **Context & Config** | InstructionsLoaded, ConfigChange, CwdChanged, FileChanged |
| **Worktree** | WorktreeCreate, WorktreeRemove |
| **Compaction** | PreCompact, PostCompact |
| **Interaction** | Notification, Elicitation, ElicitationResult |

이전 버전에서 "12~13개"라 적었던 부분은 **부정확**이었음. 실제로는 위 카테고리 합계로 ~29개. 사용자 셋업이 활용 중인 것은 그 중 일부 (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, PreCompact).

### 자주 쓰이는 hook 패턴

| hook | 시점 | 대표 용도 |
|------|------|----------|
| **SessionStart** | 세션 시작 | additionalContext 주입 (예: superpowers가 SKILL 부트스트랩) |
| **UserPromptSubmit** | 사용자 입력 직후 | 턴 시작 마커, flag 초기화 |
| **PreToolUse** | 도구 실행 직전 | 위험 명령 차단, 권한 게이트 |
| **PostToolUse** | 도구 실행 성공 후 | 상태 추적, flag 설정 |
| **PostToolUseFailure** | 도구 실행 실패 후 | 실패 학습·로깅 (사용자 셋업에서 미활용) |
| **Stop** | 응답 직전 | 응답 게이트 (예: work-history 미작성 reminder) |
| **PreCompact** | 자동 압축 직전 | 압축 전 핵심 정보 저장 |
| **SubagentStart/Stop** | subagent 라이프사이클 | multi-agent 관측 |

### Hook 구현 형태
공식 docs는 shell command, MCP server, HTTP webhook 등을 지원. 본 references 이전 버전이 "judge hook"(LLM judge로 동적 평가)을 별도 분류로 적었지만 이는 **공식 분류가 아닌 임의 표현**이므로 제거.

### 좋은 hook 설계 원칙
- **결정론적 룰만**: "X가 있으면 Y" 같은 if-then. LLM 호출은 비용·지연 발생
- **빠를 것**: PreToolUse가 느리면 사용성 파괴
- **차단보다 알림**: hard block은 신중하게, soft reminder 우선
- **노이즈 최소화**: 같은 reminder 반복은 무시되기 시작 — "success is silent, failures are verbose"

### Skill과의 역할 분담
- **Skill**: 권유 톤, LLM이 자연스럽게 트리거
- **Hook**: 강제 차단, LLM 우회 불가
- 우선 Skill로 시작 → 효과 보고 hook으로 승격 결정

## 관련 자료
- [[claude-md]] — 정책 자리
- [[../03-patterns/iron-laws-pattern]] — Iron Law를 hook으로 강제하는 선택
- [[../04-anti-patterns/hook-noise]] — hook 노이즈
- [[../05-decision-trees/stop-hook-promotion-criteria]] — Skill을 hook으로 승격 판단
- [[../99-sources/hook-events-claude-code-docs-2026-05-26]] — 공식 hook events 전체 목록 백업

## 출처
- **공식 (확인일 2026-05-26)**: https://code.claude.com/docs/en/hooks — "29개 가까운 hook event"는 이 페이지의 카테고리·이벤트 명세를 합산한 결과
- disler/claude-code-hooks-mastery — https://github.com/disler/claude-code-hooks-mastery
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html`
