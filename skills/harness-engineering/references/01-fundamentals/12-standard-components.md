---
name: 12-standard-components
topic: 하네스의 표준 구성 요소 — awesome-harness-engineering 카테고리 분류
category: 01-fundamentals
added: 2026-05-26
source: https://github.com/ai-boost/awesome-harness-engineering
tags: [components, taxonomy, awesome-harness-engineering]
status: revised-2026-05-26
revision_note: "12 카테고리"라는 표현은 본 references의 임의 분류. 실제 리포는 11개 Design Primitives + 메타 카테고리. 정확한 목록으로 보정.
---

# 하네스 표준 구성 요소 (awesome-harness-engineering 분류)

## 핵심 한 줄
업계가 수렴한 하네스 카테고리는 **11개 Design Primitives** + Foundations/Reference/Security/Evals/Templates 같은 메타 카테고리들. 자신의 셋업에서 어느 칸이 비었는지 진단할 때 쓴다.

## 본문

### awesome-harness-engineering 실제 구조 (verbatim, 2026-05-26 확인)

```
Foundations
Design Primitives (11개)
  - Agent Loop
  - Planning & Task Decomposition
  - Context Delivery & Compaction
  - Tool Design
  - Skills & MCP                   ← 한 카테고리로 묶임
  - Permissions & Authorization
  - Memory & State
  - Task Runners & Orchestration
  - Verification & CI Integration
  - Observability & Tracing
  - Debugging & Developer Experience
  - Human-in-the-Loop
Reference Implementations
Security, Sandbox & Permissions
Evals & Verification
Templates
Related Awesome Lists
```

이전 버전 references는 "12 카테고리"로 정리했으나, 출처 리포는 **Design Primitives 11개**. Skills와 MCP를 분리해 12로 만든 것은 본 references의 임의 분류였음.

### 핵심 인용 (verbatim)

> "Harness engineering is the discipline of designing the scaffolding — context delivery, tool interfaces, planning artifacts, verification loops, memory systems, and sandboxes — that surrounds an AI agent and determines whether it succeeds or fails on real tasks."

> "Every component here exists because the model can't do it alone — and the best harnesses are designed knowing those components will become unnecessary as models improve."

> "tool design is agent UX"

### 진단용 체크리스트 (Design Primitives 기반)
자기 하네스에서 다음을 채워본다. 빈 칸이 우선순위 후보.

- [ ] **Agent Loop**: 어떤 루프로 도는가? 무한 루프 방지 장치?
- [ ] **Planning & Task Decomposition**: plan 단계 분리? 승인 게이트?
- [ ] **Context Delivery & Compaction**: 토큰 예산, 캐시 전략, reset 정책
- [ ] **Tool Design**: 도구 스키마 일관성, 에러 컨벤션, lazy schema load
- [ ] **Skills & MCP**: progressive disclosure, MCP 통합 표준
- [ ] **Permissions & Authorization**: deny-first, 위험 작업 게이트
- [ ] **Memory & State**: 세션 간 지속, 인덱싱, freshness
- [ ] **Task Runners & Orchestration**: 격리 환경, multi-agent file ownership
- [ ] **Verification & CI Integration**: 완료 주장 검증 절차
- [ ] **Observability & Tracing**: 어디가 막혔는지 추적 가능?
- [ ] **Debugging & DevEx**: introspection, 빠른 반복
- [ ] **Human-in-the-Loop**: 승인 게이트, HITL 워크플로우

### Claude Code와의 매핑
[[claude-code-7-components]]가 Anthropic 7대 컴포넌트로 보는 시각이며, awesome-harness의 11개 Design Primitives와 1:N 또는 N:1 매핑.

## 관련 자료
- [[harness-concept]] — 상위 개념
- [[claude-code-7-components]] — Claude Code 매핑
- [[../02-components/skills]] · [[../02-components/hooks]] · [[../02-components/memory]] — 각 컴포넌트 상세
- [[../99-sources/awesome-harness-categories-github-2026-05-26]] — verbatim 카테고리 백업

## 출처
- **공식 (확인일 2026-05-26)**: https://github.com/ai-boost/awesome-harness-engineering — README 카테고리 분류 verbatim
