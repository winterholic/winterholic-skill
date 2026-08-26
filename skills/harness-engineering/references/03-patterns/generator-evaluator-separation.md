---
name: generator-evaluator-separation
topic: Generator + Evaluator 분리 — skeptical evaluator 별도 튜닝이 tractable
category: 03-patterns
added: 2026-05-26
source: https://www.anthropic.com/engineering/harness-design-long-running-apps · https://www.anthropic.com/research/building-effective-agents
tags: [generator-evaluator, evaluator-optimizer, multi-agent, subagent, anthropic-validated]
status: revised-2026-05-26
revision_note: Anthropic 공식 1차 자료에서 verbatim 인용 확보. 정식 패턴명 "Evaluator-Optimizer" 병기.
---

# Generator + Evaluator 분리 패턴

## 핵심 한 줄
**self-eval은 후한 편향**이 있다. 코드를 만든 에이전트와 평가하는 에이전트를 분리하고, evaluator는 별도로 skeptical하게 튜닝하는 게 가장 검증된 접근. Anthropic 공식 verbatim: *"Tuning a standalone evaluator to be skeptical turns out to be far more tractable than making a generator critical of its own work."*

## 본문

### Anthropic 공식 검증 (verbatim 인용)

**1) "Harness design for long-running application development"** — 3-agent 아키텍처:

> "The final result was a three-agent architecture—planner, generator, and evaluator—that produced rich full-stack applications over multi-hour autonomous coding sessions."

> "Separating the agent doing the work from the agent judging it proves to be a strong lever to address this issue."

> **"Tuning a standalone evaluator to be skeptical turns out to be far more tractable than making a generator critical of its own work."**

> "Once that external feedback exists, the generator has something concrete to iterate against."

**2) "Building Effective Agents"** — 정식 패턴명은 **Evaluator-Optimizer**:

> "In the evaluator-optimizer workflow, one LLM call generates a response while another provides evaluation and feedback in a loop."

> 사용 조건: "LLM responses can be demonstrably improved when a human articulates their feedback, and ... the LLM can provide such feedback."

→ 본 references의 "Generator-Evaluator separation"은 동의어. Anthropic 공식 명칭은 **Evaluator-Optimizer**이며, 본 references는 의미 변형 표현을 사용한 것.

### 패턴 구조
```
[Planner (옵션)] → [Generator] ──결과──> [Evaluator (skeptical)] 
                       ↑                          ↓
                       └──── feedback loop ───────┘
```

3-agent 버전은 Planner까지 분리하는 Anthropic harness-design 구현이며, 단순 evaluator-optimizer는 2-agent.

### 왜 같은 컨텍스트에선 안 되는가
- 컨텍스트 안에서 본인이 쓴 텍스트는 **commitment bias**가 작동 (사용자 측 추론, 공식 문헌 외)
- "내가 방금 만든 게 옳다"는 쪽으로 기울어짐 — Anthropic 표현 "self-policing"에 의존하는 한계
- subagent로 분리하면 격리된 컨텍스트에서 처음 보는 코드처럼 평가

### Claude Code 구현
- **subagent_type 분리**: code-reviewer, security-reviewer 등
- **agent-teams plugin**: team-review, multi-reviewer-patterns
- **code-reviewer는 Read 권한만**: Write 없이 검증에만 집중

### 평가 다양성 (multi-reviewer)
- 단일 evaluator도 편향 가능
- 여러 reviewer를 dimension별로 (정확성, 보안, 가독성, 성능) 병렬 실행
- 결과 deduplication + severity calibration + 통합 리포트

### Self-review와의 차이
- **Self-review (작성자 본인)**: PR 올리기 전 자기 코드 점검 — 가치 있지만 한계
- **Peer review (다른 에이전트)**: 격리된 시선 — 더 효과적
- 두 단계 다 거치는 게 베스트

### 사용 시점 (공식 가이드)
- "first-attempt quality already meets requirements"인 경우 X
- "evaluation criteria are subjective or unclear"인 경우 X
- "time and cost constraints outweigh quality improvements"인 경우 X
- "real-time applications requiring immediate responses"인 경우 X
→ trivial 작업엔 과부하. 가치 있는 영역에 한정.

### CLAUDE.md 룰과의 연계
사용자 셋업의 `feedback_response_style` 메모: "리뷰 받으면 즉답 동의 금지, 검증 후 동의 또는 푸시백" — 한 컨텍스트 안에서도 "방금 받은 피드백"을 비판적으로 보라는 룰. evaluator의 정신을 single-agent 안에 흡수한 형태.

### Stripe 사례 — 확인 필요
이전 버전 references가 "Stripe 주당 1,300 AI PR"을 generator-evaluator 패턴 적용 사례로 단정했으나, 외부 자료 확인 결과:
- **Stripe minions 1,300 PRs/week 사실** ✅ (Lenny's Newsletter, ByteByteGo, InfoQ 등 다수 보도)
- **Claude Code 직접 사용 여부**: 정황은 있으나 1차 자료에 명시 안 됨 — "확인 필요"
- generator-evaluator 패턴을 명시적으로 채택했다는 공식 표명은 없음 — 보도된 것은 "autonomous coding agents that ship PRs"라는 일반적 표현

### Opus 4.5 이후 변화
Anthropic 보고: Opus 4.5에선 context anxiety가 거의 사라져 single continuous session도 가능. 단, generator-evaluator 분리의 본질(편향 방지)은 모델 무관하게 유효.

## 관련 자료
- [[../02-components/subagents]] — subagent 컴포넌트
- [[../02-components/plugins]] — agent-teams plugin
- [[../01-fundamentals/2026-trends]] — Multi-agent 트렌드
- [[../99-sources/generator-evaluator-anthropic-harness-design-2026-05-26]] — 공식 verbatim 인용 백업

## 출처
- **Anthropic 공식 (확인일 2026-05-26)**:
  - https://www.anthropic.com/engineering/harness-design-long-running-apps — 3-agent 아키텍처, "skeptical evaluator ... tractable" verbatim
  - https://www.anthropic.com/research/building-effective-agents — Evaluator-Optimizer 공식 패턴명
  - https://github.com/anthropics/anthropic-cookbook/blob/main/patterns/agents/evaluator_optimizer.ipynb — 코드 예시
- Stripe minions 사례 (1차 자료): Lenny's Newsletter (lennysnewsletter.com/p/this-week-on-how-i-ai-how-stripe), InfoQ 2026-03 보도
