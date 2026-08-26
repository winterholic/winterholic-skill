---
name: subagents
topic: Subagents — 격리된 컨텍스트의 병렬 에이전트
category: 02-components
added: 2026-05-26
source: https://www.anthropic.com/engineering/harness-design-long-running-apps · https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
tags: [subagents, parallel, file-ownership, generator-evaluator]
status: revised-2026-05-26
revision_note: Anthropic effective-context-engineering 글의 sub-agent 인용 추가.
---

# Subagents — 서브에이전트 컴포넌트

## 핵심 한 줄
**독립 컨텍스트·격리 권한**으로 돌아가는 별도 에이전트. parent 컨텍스트 오염 없이 병렬 작업·generator/evaluator 분리에 쓴다. Anthropic이 long-running·context-engineering 양쪽에서 공식 권장하는 패턴.

## 본문

### Anthropic 공식 인용

**"Effective context engineering for AI agents"**:
> "Each subagent might explore extensively, using tens of thousands of tokens or more, but returns only a condensed, distilled summary of its work (often 1,000-2,000 tokens)."
> "The detailed search context remains isolated within sub-agents, while the lead agent focuses on synthesizing and analyzing the results."

**"Harness design for long-running application development"**:
> "Separating the agent doing the work from the agent judging it proves to be a strong lever to address this issue."
> 3-agent architecture: planner + generator + evaluator

### 핵심 메커니즘
- `Agent` 도구의 `subagent_type` 파라미터로 호출
- 독립 컨텍스트 윈도우 — parent의 메시지 히스토리 안 봄
- 격리 권한 — subagent_type별로 도구 권한 다름
- 결과는 parent에 condensed summary로 반환 (수천 토큰 단위)

### 왜 격리가 가치인가
- **컨텍스트 오염 방지** (공식 인용): 검색·실험으로 parent 컨텍스트 부풀리지 않음
- **권한 분리**: code-reviewer는 Write 없이 Read만, 등
- **병렬 실행**: file ownership boundary로 충돌 없는 동시 작업

### Generator + Evaluator 패턴
[[../03-patterns/generator-evaluator-separation]] 참조. Anthropic harness-design 공식 검증 패턴.

### 사용자 셋업의 agent-teams (참조)
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, teammateMode: tmux.

13개 명령:
- team-feature · team-debug · team-review · team-spawn
- team-status · team-delegate · team-shutdown
- team-communication-protocols
- multi-reviewer-patterns · parallel-debugging · parallel-feature-development
- task-coordination-strategies · team-composition-patterns

### File ownership boundary
병렬 작업 시 충돌 방지의 핵심.
- 각 subagent에게 **소유 파일 집합** 명시
- 다른 에이전트의 소유 파일은 읽기만 가능
- 통합은 별도 단계로 분리

### Plan Mode와의 조합
- Plan mode에서 작업 분해 → 각 task를 fresh subagent로 dispatch
- 매 task 후 code-reviewer subagent로 review gate
- 통합 책임은 orchestrator (parent) 에이전트

## 관련 자료
- [[skills]] — 스킬과의 차이 (스킬은 같은 컨텍스트, subagent는 격리)
- [[../03-patterns/generator-evaluator-separation]] — Anthropic 검증 패턴
- [[plugins]] — agent-teams는 plugin 형태로 배포
- [[../99-sources/generator-evaluator-anthropic-harness-design-2026-05-26]] — 공식 verbatim 인용

## 출처
- **Anthropic 공식 (확인일 2026-05-26)**:
  - https://www.anthropic.com/engineering/harness-design-long-running-apps — 3-agent 아키텍처
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents — sub-agent isolation, condensed summary 패턴
