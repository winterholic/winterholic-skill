---
name: hook-events-claude-code-docs-2026-05-26
topic: Claude Code Hook Events — 공식 docs 전체 목록 (~29개)
category: 99-sources
added: 2026-05-26
source: https://code.claude.com/docs/en/hooks
tags: [hooks, claude-code, primary-source, events]
status: active
---

# Claude Code 공식 Hook Events 전체 목록 (확인일 2026-05-26)

## 본 references의 잘못된 주장
> references/02-components/hooks.md: "Claude Code에는 **12~13개의 hook point**가 있다"

→ **틀림.** 실제 공식 docs 기준 29개에 가까움 (2026-05-26 확인).

## 공식 Hook Events 분류

### Session Lifecycle (3)
- **SessionStart** — session begins or resumes
- **Setup** — `--init-only`, `--init`, `--maintenance` 모드 시작
- **SessionEnd** — session terminates

### Per-Turn (4)
- **UserPromptSubmit** — prompt 제출, Claude 처리 직전
- **UserPromptExpansion** — user-typed command가 prompt로 확장될 때
- **Stop** — Claude가 응답 종료
- **StopFailure** — API 에러로 turn 종료

### Agentic Loop / Tool Use (6)
- **PreToolUse** — tool 호출 직전
- **PostToolUse** — tool 호출 성공 후
- **PostToolUseFailure** — tool 호출 실패 후
- **PostToolBatch** — 병렬 tool 호출 배치 완료
- **PermissionRequest** — permission dialog 출현
- **PermissionDenied** — auto mode classifier가 tool 호출 거부

### Subagent & Team (3)
- **SubagentStart** — subagent spawn
- **SubagentStop** — subagent 종료
- **TeammateIdle** — agent team teammate가 idle 진입 예정

### Task Management (2)
- **TaskCreated** — `TaskCreate`로 task 생성 중
- **TaskCompleted** — task 완료 표시 중

### Context & Configuration (4)
- **InstructionsLoaded** — CLAUDE.md/`.claude/rules/*.md` 로드
- **ConfigChange** — 세션 중 config 파일 변경
- **CwdChanged** — working directory 변경
- **FileChanged** — watched file 변경

### Worktree (2)
- **WorktreeCreate**, **WorktreeRemove**

### Compaction (2)
- **PreCompact** — context compaction 직전
- **PostCompact** — context compaction 완료 후

### User Interaction (3)
- **Notification**, **Elicitation**, **ElicitationResult**

## 시사점
- 본 references는 큰 수정 필요. "12~13개"는 명백한 hallucination.
- 특히 PostToolUseFailure, PostToolBatch, PermissionRequest, SubagentStart/Stop, TaskCreated/Completed, InstructionsLoaded, PostCompact 등 본 references가 누락한 강력한 자리들이 다수.

## 출처
- https://code.claude.com/docs/en/hooks (확인일 2026-05-26, WebFetch 추출)
