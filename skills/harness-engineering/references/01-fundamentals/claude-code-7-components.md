---
name: claude-code-7-components
topic: Claude Code 하네스의 컴포넌트 — 사용자 셋업 분류 7개
category: 01-fundamentals
added: 2026-05-26
source: 내부 분석 + Claude Code 공식 docs
tags: [claude-code, components, architecture]
status: revised-2026-05-26
revision_note: "7대 컴포넌트"는 사용자 셋업 분류이며 Anthropic 공식 분류가 아님을 명시. hook 개수 ~29개로 수정.
---

# Claude Code 하네스의 컴포넌트 — 사용자 분류 7개

## 핵심 한 줄
awesome-harness-engineering의 11개 Design Primitives를 Claude Code 환경에 매핑하면 사용자 셋업 기준 7개 — 시스템 프롬프트, 도구, 메모리, 훅, 스킬, 서브에이전트, 플랜·태스크. **Anthropic 공식 "Claude Code 7대 컴포넌트" 분류는 아님** — 본 references의 정리 도구.

## 본문

### 7대 컴포넌트 (사용자 셋업 분류)

| 컴포넌트 | 구체 예 | 핵심 메커니즘 |
|---------|---------|--------------|
| **① 시스템 프롬프트** | `CLAUDE.md` (user·project·local), `settings.json` | 매 세션 컨텍스트 로드 |
| **② 도구 (Tools)** | Bash·Read·Edit·Write·Skill·Agent·ToolSearch·MCP | permission-gated 노출, lazy schema load |
| **③ 메모리** | auto memory(`MEMORY.md`), 사용자 셋업 `feedback_*.md` | 세션 간 persist, 인덱스만 메인 컨텍스트 |
| **④ 훅 (Hooks)** | SessionStart·UserPromptSubmit·PreToolUse·PostToolUse·Stop·PreCompact 등 **~29개** (2026-05-26 공식 docs) | 결정론적 control layer, shell/MCP/HTTP 형태 |
| **⑤ Skills** | SKILL.md (frontmatter + body + bundled files) | 3단계 progressive disclosure, description-based triggering |
| **⑥ 서브에이전트** | `Agent` 도구의 `subagent_type`, agent-teams (실험적) | 독립 컨텍스트·격리 권한, generator/evaluator 분리 |
| **⑦ 플랜·태스크** | Plan mode, TaskCreate, TaskList | 실행 전 plan 산출·승인 후 실행, 진척 추적 |

### 컴포넌트별 역할 관계
- **①·③**이 매 턴 컨텍스트의 anchor (system prompt + memory)
- **②**가 모델의 손발 — permission-gated로 안전 확보
- **④**가 결정론적 게이트 — LLM 판단을 신뢰 못 할 자리에 배치
- **⑤**가 lazy-loaded 전문 지식 — description 기반 자동 트리거
- **⑥**가 컨텍스트 격리 — parent 컨텍스트 오염 방지 (Anthropic 공식 검증 패턴)
- **⑦**이 장기 작업의 골격 — plan → execute → verify 분리

### awesome-harness 11개 Design Primitives → 사용자 분류 매핑

| awesome-harness 카테고리 | Claude Code 컴포넌트 |
|-------------------------|---------------------|
| Agent Loop · Planning | ⑦ 플랜·태스크 |
| Tool Design | ② 도구 |
| Context Delivery & Compaction | ① 시스템 프롬프트 + ⑤ Skills |
| Skills & MCP | ② 도구 (MCP는 도구의 한 종류) + ⑤ Skills |
| Memory & State | ③ 메모리 |
| Permissions & Authorization | ④ 훅 (PreToolUse·PermissionRequest 등) + settings.json |
| Task Runners & Orchestration | ⑥ 서브에이전트 |
| Verification & CI | ④ 훅 (Stop) + ⑤ Skills (verification-before-completion) |
| Observability & Tracing | settings statusline + 훅 로그 |
| Debugging & DevEx | ⑦ Plan mode + ④ 훅 |
| Human-in-the-Loop | ⑦ Plan mode 승인 + permissions ask 모드 |

## 관련 자료
- [[12-standard-components]] — awesome-harness 11개 Design Primitives 원본
- [[../02-components/claude-md]] · [[../02-components/hooks]] · [[../02-components/memory]] · [[../02-components/skills]] · [[../02-components/subagents]] · [[../02-components/mcp]] · [[../02-components/plugins]] — 각 컴포넌트 상세

## 출처
- **공식 (확인일 2026-05-26)**:
  - https://code.claude.com/docs/en/skills
  - https://code.claude.com/docs/en/hooks
  - https://code.claude.com/docs/en/claude-directory
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html`
- WaveSpeed, "Claude Code Agent Harness: Architecture Breakdown" (커뮤니티) — https://wavespeed.ai/blog/posts/claude-code-agent-harness-architecture/
