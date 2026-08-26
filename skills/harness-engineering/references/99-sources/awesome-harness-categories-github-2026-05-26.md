---
name: awesome-harness-categories-github-2026-05-26
topic: ai-boost/awesome-harness-engineering — 실제 카테고리 목록 1차 자료
category: 99-sources
added: 2026-05-26
source: https://github.com/ai-boost/awesome-harness-engineering
tags: [awesome-harness, components, taxonomy, primary-source]
status: active
---

# awesome-harness-engineering 실제 카테고리 (확인일 2026-05-26)

## 본 references의 부분 부정확
> references/01-fundamentals/12-standard-components.md: "6묶음 × 2 = 12개 카테고리"

→ **실제 리포는 11개 Design Primitives + Foundations + Reference Implementations + Security/Sandbox + Evals + Templates + Related Lists**. "12"라는 숫자는 본 references의 임의 분류이며 awesome-harness-engineering 공식 분류와 정확히 일치하지 않음.

## 실제 카테고리 (verbatim from README)

```
📐 Foundations
🧩 Design Primitives
  🔄 Agent Loop
  🗺️ Planning & Task Decomposition
  📦 Context Delivery & Compaction
  🔧 Tool Design
  🔌 Skills & MCP                  ← Skills와 MCP가 한 카테고리로 묶임
  🛡️ Permissions & Authorization
  🧠 Memory & State
  ⚙️ Task Runners & Orchestration
  ✔️ Verification & CI Integration
  👁️ Observability & Tracing
  🐛 Debugging & Developer Experience
  🧑‍💼 Human-in-the-Loop
🔍 Reference Implementations
🔒 Security, Sandbox & Permissions
✅ Evals & Verification
📋 Templates
📚 Related Awesome Lists
```

Design Primitives는 **11개** (Skills & MCP를 1개 카테고리로). 본 references는 이를 2개로 쪼개 "12"로 셈.

## 주요 인용

> "Harness engineering is the discipline of designing the scaffolding — context delivery, tool interfaces, planning artifacts, verification loops, memory systems, and sandboxes — that surrounds an AI agent and determines whether it succeeds or fails on real tasks."

> "Every component here exists because the model can't do it alone — and the best harnesses are designed knowing those components will become unnecessary as models improve."

> "tool design is agent UX"

## 시사점
- "12 카테고리"라는 표현은 본 references의 약간의 부풀림.
- 정확하게는 **11개 Design Primitives + 메타 카테고리들**.
- 본 references는 Skills와 MCP를 분리해서 12로 만들었으나 출처 리포는 묶음.

## 출처
- https://github.com/ai-boost/awesome-harness-engineering (확인일 2026-05-26)
