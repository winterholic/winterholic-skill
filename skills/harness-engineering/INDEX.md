# INDEX — Harness Engineering 책갈피

본 스킬 진입점. 사용자 발화에서 키워드 잡고 grep으로 reference 1개 찾는다. 3축 정렬.

---

## 1축 — 키워드별 (사용자 발화 → reference)

### 기본 개념
- "하네스가 뭐야" / "harness 개념" → [harness-concept](references/01-fundamentals/harness-concept.md)
- "prompt vs context vs harness 차이" → [prompt-vs-context-vs-harness](references/01-fundamentals/prompt-vs-context-vs-harness.md)
- "하네스 컴포넌트 뭐뭐 있어" → [12-standard-components](references/01-fundamentals/12-standard-components.md) · [claude-code-7-components](references/01-fundamentals/claude-code-7-components.md)
- "2026년 트렌드" / "최근 Anthropic 동향" → [2026-trends](references/01-fundamentals/2026-trends.md)

### 컴포넌트 선택
- "스킬로 만들까 hook으로 갈까" → [skill-vs-hook-vs-claude-md](references/05-decision-trees/skill-vs-hook-vs-claude-md.md)
- "메모리에 둘까 CLAUDE.md에 둘까" → [memory-vs-claude-md-vs-skill](references/05-decision-trees/memory-vs-claude-md-vs-skill.md)
- "MCP vs Skill" → [mcp-vs-skill](references/05-decision-trees/mcp-vs-skill.md)
- "Stop hook 승격 기준" → [stop-hook-promotion-criteria](references/05-decision-trees/stop-hook-promotion-criteria.md)

### 컴포넌트별 상세
- CLAUDE.md → [claude-md](references/02-components/claude-md.md)
- Hooks → [hooks](references/02-components/hooks.md)
- Memory → [memory](references/02-components/memory.md)
- Skills → [skills](references/02-components/skills.md)
- Subagents → [subagents](references/02-components/subagents.md)
- MCP → [mcp](references/02-components/mcp.md)
- Plugins → [plugins](references/02-components/plugins.md)

### Skill 설계
- "description 길이 괜찮나" / "description 트리거 잘 안 됨" → [skill-description-tuning](references/03-patterns/skill-description-tuning.md)
- "progressive disclosure가 뭐" → [progressive-disclosure](references/03-patterns/progressive-disclosure.md)
- "iron law 적용해야 하나" → [iron-laws-pattern](references/03-patterns/iron-laws-pattern.md)

### Context Window
- "context reset vs compaction" / "context anxiety" → [context-reset-vs-compaction](references/03-patterns/context-reset-vs-compaction.md)

### LLM 이론 (프롬프트·컨텍스트 거동의 학술 근거)
- "컨텍스트 길수록 성능 떨어지나" / "context rot" / "많이 넣을수록 좋은 거 아냐" / "긴 프롬프트 트레이드오프" / "effective context length" / "lost in the middle" → [context-rot-length-vs-performance](references/07-llm-theory/context-rot-length-vs-performance.md)
- "FC/툴 프롬프트 설계 원칙" / "function calling 프롬프트" → *(예정)* `07-llm-theory/function-calling-prompt-design`
- "context engineering" / "attention budget" / "고신호 토큰" → *(예정)* `07-llm-theory/context-engineering-principles`
- "프롬프트 완성도 평가" / "LLM-as-judge 편향" / "eval 설계" → *(예정)* `07-llm-theory/prompt-evaluation-methodology`

### 자가 평가·학습 루프
- "Generator/Evaluator 분리해야 하나" → [generator-evaluator-separation](references/03-patterns/generator-evaluator-separation.md)

### 안티 패턴
- "이 hook이 매번 발동돼서 시끄러워" → [hook-noise](references/04-anti-patterns/hook-noise.md)
- "claude.md 너무 길어진 거 같은데" → [description-bloat](references/04-anti-patterns/description-bloat.md)
- "메모리 너무 많아" / "메모리 정리해야" → [memory-overuse](references/04-anti-patterns/memory-overuse.md)
- "룰 너무 강하게 강제" → [rule-over-enforcement](references/04-anti-patterns/rule-over-enforcement.md)
- "그냥 while 루프 돌리면 안 돼" → [loop-and-a-dream](references/04-anti-patterns/loop-and-a-dream.md)

### 메서드 (교수 모드)
- "최신 정보 확인해줘" / "Anthropic 업데이트 반영" → [research-methodology](references/03-patterns/research-methodology.md)

---

## 2축 — 결정 시점별 (지금 무슨 결정을 하려는가)

### 새 룰 발견 — 어디에 굳힐까
1. 자동 강제? → hook · 모든 세션? → CLAUDE.md · 트리거 발동? → Skill · 사용자 정보? → 메모리
→ [skill-vs-hook-vs-claude-md](references/05-decision-trees/skill-vs-hook-vs-claude-md.md) · [memory-vs-claude-md-vs-skill](references/05-decision-trees/memory-vs-claude-md-vs-skill.md)
> 근저 압력: 모든 굳히기는 컨텍스트 비용 추가 → [context-rot](references/07-llm-theory/context-rot-length-vs-performance.md). 이득 > 비용일 때만.

### 기존 스킬 발동 부정확 — 무엇을 고칠까
→ [skill-description-tuning](references/03-patterns/skill-description-tuning.md) · CLAUDE.md "Skill Check" 우선순위 정렬
> 근저 압력: description 트리거는 brittleness(Sclar 포맷 ±76점) + length 둘 다의 영향권 → [context-rot](references/07-llm-theory/context-rot-length-vs-performance.md) §2-2.

### Hook 너무 자주 발동
→ [hook-noise](references/04-anti-patterns/hook-noise.md)
> 근저 압력: 매 발동 = 무관 신호 누적 → S2A의 잠재표현 오염 ([context-rot](references/07-llm-theory/context-rot-length-vs-performance.md) §2-1).

### 학습 루프 약함 진단
→ 5요소 채점 → 약점 1개 보강 → 케이스: [verification-evolution](references/06-case-studies/verification-evolution.md) · [systematic-debugging-evolution](references/06-case-studies/systematic-debugging-evolution.md)

### 새 외부 도구 도입 — MCP vs Skill vs Plugin
→ [mcp-vs-skill](references/05-decision-trees/mcp-vs-skill.md) · [plugins](references/02-components/plugins.md)
> 근저 압력: 새 도구 = 매 세션 컨텍스트 점유 + 툴 description 자체가 distractor 가능 → [context-rot](references/07-llm-theory/context-rot-length-vs-performance.md).

### Stop hook 승격 시점
→ [stop-hook-promotion-criteria](references/05-decision-trees/stop-hook-promotion-criteria.md)
> 근저 압력: hook 승격 = 매 턴 비용 영구화. 노이즈 누적 시 S2A 오염. ([hook-noise](references/04-anti-patterns/hook-noise.md) + [context-rot](references/07-llm-theory/context-rot-length-vs-performance.md))

### 새 스킬 신설
→ [progressive-disclosure](references/03-patterns/progressive-disclosure.md) · [skill-description-tuning](references/03-patterns/skill-description-tuning.md) · [generator-evaluator-separation](references/03-patterns/generator-evaluator-separation.md)
> 근저 압력: 스킬 자체가 context rot 회피의 implementation. progressive disclosure ≡ "focused > full"의 design화 ([context-rot](references/07-llm-theory/context-rot-length-vs-performance.md) §5).

### 장기 작업 — 컨텍스트 어떻게 운영
→ [context-reset-vs-compaction](references/03-patterns/context-reset-vs-compaction.md)

---

## 3축 — 사용자 셋업 컨텍스트 (06-case-studies)

본 사용자가 이미 운영 중인 셋업. 비슷한 결정 다시 마주치면 여기 먼저.

- caveman (91.4/A+) — [caveman-evolution](references/06-case-studies/caveman-evolution.md)
- handoff (88.9/A) — [handoff-evolution](references/06-case-studies/handoff-evolution.md)
- verification (89/A) — [verification-evolution](references/06-case-studies/verification-evolution.md)
- systematic-debugging (87/A) — [systematic-debugging-evolution](references/06-case-studies/systematic-debugging-evolution.md)

---

## 4축 — 1차 자료 백업 (99-sources)

reference 주장의 원본 출처 발췌. reference가 stale 의심되거나 인용 진위 확인할 때 여기 대조.

- [awesome-harness-categories (11 Design Primitives)](references/99-sources/awesome-harness-categories-github-2026-05-26.md) ← `12-standard-components`
- [context anxiety (Anthropic managed-agents)](references/99-sources/context-anxiety-anthropic-managed-agents-2026-05-26.md) ← `context-reset-vs-compaction`
- [Generator-Evaluator (Anthropic harness-design)](references/99-sources/generator-evaluator-anthropic-harness-design-2026-05-26.md) ← `generator-evaluator-separation`
- [hook events 29개 (Claude Code docs)](references/99-sources/hook-events-claude-code-docs-2026-05-26.md) ← `hooks`
- [progressive disclosure 3-level (Anthropic docs)](references/99-sources/progressive-disclosure-anthropic-docs-2026-05-26.md) ← `progressive-disclosure`
- [context rot (Chroma + Lost-in-Middle + RULER + NoLiMa)](references/99-sources/context-rot-chroma-2025-07-14.md) ← `context-rot-length-vs-performance`

---

*(예정)* 표시는 없음 — 추가 토픽은 사용자 발화 시 신규 작성.
