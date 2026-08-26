---
name: context-anxiety-anthropic-managed-agents-2026-05-26
topic: Sonnet 4.5 "context anxiety" — Anthropic 공식 용어 1차 자료
category: 99-sources
added: 2026-05-26
source: https://www.anthropic.com/engineering/managed-agents · https://www.anthropic.com/engineering/harness-design-long-running-apps
tags: [context-anxiety, sonnet-4.5, compaction, reset, primary-source]
status: active
---

# Context Anxiety — Anthropic 공식 1차 자료

## 핵심 인용

### "Scaling Managed Agents" (Anthropic Engineering)

> "Claude Sonnet 4.5 would wrap up tasks prematurely as it sensed its context limit approaching—a behavior sometimes called 'context anxiety.'"

> "We addressed this by adding context resets to the harness."

> "Compaction lets Claude save a summary of its context window and the memory tool lets Claude write context to files, enabling learning across sessions."

### "Harness design for long-running application development"

> "Claude Sonnet 4.5 exhibited context anxiety strongly enough that compaction alone wasn't sufficient to enable strong long task performance"

> "A reset provides a clean slate, at the cost of the handoff artifact having enough state for the next agent to pick up the work cleanly."

### "Effective harnesses for long-running agents"

> "a two-fold solution to enable the Claude Agent SDK to work effectively across many contexts: an initializer agent that sets up the environment on the first run, and a coding agent that is tasked with making incremental progress in every session"

> "each new session begins with no memory of what came before"

> "leaving clear artifacts for the next session"

> "claude-progress.txt file that keeps a log of what agents have done, and an initial git commit"

> "work on only one feature at a time. This incremental approach turned out to be critical"

## 본 references와 정합성
- references/03-patterns/context-reset-vs-compaction.md 핵심 주장 ("Anthropic이 Sonnet 4.5에서 직접 검증", "Reset이 Compaction을 이긴다") 모두 공식 1차 자료로 확증. ✅
- 단 "Reset이 Compaction을 이긴다"는 본 references 표현은 약간 과한 단순화 — 공식 입장은 "compaction alone wasn't sufficient" + "reset provides clean slate at the cost of handoff artifact". Opus 4.5에선 context anxiety 거의 사라져 reset 안 써도 됨 (managed-agents 글).

## 출처
- https://www.anthropic.com/engineering/managed-agents (확인일 2026-05-26)
- https://www.anthropic.com/engineering/harness-design-long-running-apps (확인일 2026-05-26)
- https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents (확인일 2026-05-26)
