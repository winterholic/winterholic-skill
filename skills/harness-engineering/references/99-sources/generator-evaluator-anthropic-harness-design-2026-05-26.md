---
name: generator-evaluator-anthropic-harness-design-2026-05-26
topic: Anthropic engineering — Generator/Evaluator 분리와 skeptical evaluator 1차 자료
category: 99-sources
added: 2026-05-26
source: https://www.anthropic.com/engineering/harness-design-long-running-apps · https://www.anthropic.com/research/building-effective-agents
tags: [generator-evaluator, multi-agent, skeptical-evaluator, primary-source]
status: active
---

# Generator + Evaluator 분리 — Anthropic 공식 1차 자료

## 핵심 인용

### "Harness design for long-running application development" (Anthropic Engineering)

> "The final result was a three-agent architecture—planner, generator, and evaluator—that produced rich full-stack applications over multi-hour autonomous coding sessions."

> "Separating the agent doing the work from the agent judging it proves to be a strong lever to address this issue."

> **"Tuning a standalone evaluator to be skeptical turns out to be far more tractable than making a generator critical of its own work"**

> "Once that external feedback exists, the generator has something concrete to iterate against."

> "Claude Sonnet 4.5 exhibited context anxiety strongly enough that compaction alone wasn't sufficient to enable strong long task performance" — (별도 어딘가 발췌, 본 글 내 인용 — context anxiety 용어 출처)

### "Building Effective Agents" (Anthropic Research)

> "In the evaluator-optimizer workflow, one LLM call generates a response while another provides evaluation and feedback in a loop."

> Use when "LLM responses can be demonstrably improved when a human articulates their feedback, and ... the LLM can provide such feedback."

## 본 references와 정합성
- references/03-patterns/generator-evaluator-separation.md 의 핵심 주장 "skeptical evaluator 별도 튜닝이 더 tractable"은 Anthropic harness-design 글 거의 verbatim. ✅ 완전 확증.
- 단 정식 패턴명은 "Evaluator-Optimizer" (Anthropic Building Effective Agents) — 본 references는 "Generator-Evaluator separation"이라는 변형 표현. 동의어로 봐도 무방하나 공식 명칭 병기 권장.

## 출처
- https://www.anthropic.com/engineering/harness-design-long-running-apps (확인일 2026-05-26)
- https://www.anthropic.com/research/building-effective-agents (확인일 2026-05-26)
- https://github.com/anthropics/anthropic-cookbook/blob/main/patterns/agents/evaluator_optimizer.ipynb (참조)
