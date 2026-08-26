---
name: progressive-disclosure-anthropic-docs-2026-05-26
topic: Anthropic 공식 docs · engineering 블로그 - Progressive Disclosure 1차 자료 백업
category: 99-sources
added: 2026-05-26
source: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview · https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
tags: [progressive-disclosure, skills, primary-source, anthropic-official]
status: active
---

# Progressive Disclosure — Anthropic 공식 자료 (검증일 2026-05-26)

## 핵심 인용

### Engineering 블로그 "Equipping agents for the real world with Agent Skills"

> "This metadata is the **first level** of _progressive disclosure_: it provides just enough information for Claude to know when each skill should be used without loading all of it into context."

> "The actual body of this file is the **second level** of detail. If Claude thinks the skill is relevant to the current task, it will load the skill by reading its full `SKILL.md` into context."

> "These additional linked files are the **third level** (and beyond) of detail, which Claude can choose to navigate and discover only as needed."

> "At startup, the agent pre-loads the `name` and `description` of every installed skill into its system prompt."

### Platform docs "Agent Skills Overview" - 3 levels with token cost table

| Level | When Loaded | Token Cost | Content |
|-------|------------|------------|---------|
| Level 1: Metadata | Always (at startup) | ~100 tokens per Skill | `name` and `description` from YAML frontmatter |
| Level 2: Instructions | When Skill is triggered | Under 5k tokens | SKILL.md body with instructions and guidance |
| Level 3+: Resources | As needed | Effectively unlimited | Bundled files executed via bash without loading contents into context |

### SKILL.md 공식 필드 제약

- `name`: 최대 64자, 소문자·숫자·하이픈만, "anthropic"·"claude" 예약어 금지
- `description`: 최대 1024자, non-empty, XML 태그 금지
- "The `description` should include both what the Skill does and when Claude should use it."

## 본 references와 정합성
- references/02-components/skills.md, references/03-patterns/progressive-disclosure.md 양쪽 모두 본 1차 자료와 정합. 단 정확한 토큰 cost (~100/Skill, <5k SKILL.md)와 1024자 description 제약은 보강 필요.

## 출처
- https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills (확인일 2026-05-26)
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview (확인일 2026-05-26)
