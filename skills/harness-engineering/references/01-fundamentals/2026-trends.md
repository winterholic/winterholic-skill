---
name: 2026-trends
topic: 2026 하네스 엔지니어링 핵심 트렌드 6가지
category: 01-fundamentals
added: 2026-05-26
source: 다수 1차 자료 — Anthropic engineering 블로그·Claude Code docs·외부 보도
tags: [trends, 2026, skills, plugin-marketplace, mcp]
status: revised-2026-05-26
revision_note: 각 트렌드별 공식 1차 자료 URL 첨부. Plugin Marketplace·MCP 수치 등 확인 못한 부분은 "확인 필요" 표시.
---

# 2026 하네스 엔지니어링 트렌드

## 핵심 한 줄
2026년 하네스 흐름 6개: ① Skills/progressive disclosure ② Plugin Marketplace 공식 출범 ③ MCP 확산 ④ Generator/Evaluator 분리 ⑤ Context Reset + Handoff Artifact ⑥ "모델 commodity, 하네스 IP".

## 본문

### ① Skills 도입 — Progressive Disclosure
단일 거대 system prompt → 다수 작은 dynamically-loaded skills로의 전환.
- **3단계 lazy load**: metadata (~100 tokens) → SKILL.md body (<5k) → bundled files (unlimited)
- **공식 출시**: Anthropic 공식 GA는 2025년 (Claude API beta header `skills-2025-10-02` 기준)
- description-based triggering — Claude는 under-trigger 경향, "pushy" description 권장 (사용자 운영 관행)

출처: [[../99-sources/progressive-disclosure-anthropic-docs-2026-05-26]]

### ② Plugin Marketplace 공식 출범 (2026-05경)
`anthropics/claude-plugins-official` — Claude Code 시작 시 자동 로드되는 공식 마켓플레이스.
- 외부 보도 기준 **55+ 큐레이트 플러그인** (확인 필요 — 시점별 변동)
- `anthropics/claude-plugins-community` 커뮤니티 마켓플레이스도 별도 존재
- 1st-party 카테고리: github, gitlab, linear, asana, notion, figma, vercel, supabase, slack, sentry 등 외부 시스템 통합 + commit-commands, pr-review-toolkit 같은 워크플로우
- "Plugin = MCP + slash commands + skills + hooks + LSP servers" 번들 (공식)

이전 references의 "2026-05-22 공식 출범"·"30+ 내부 + 15+ 외부" 수치는 한 시점의 스냅샷이며 시간이 지나면서 변동 — **확인 필요**.

출처: https://code.claude.com/docs/en/discover-plugins (확인일 2026-05-26)

### ③ MCP 확산 — "Agent용 USB-C"
Anthropic 공식 표현 (modelcontextprotocol.io):
> "Think of MCP like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect electronic devices, MCP provides a standardized way to connect AI applications to external systems."

- 클라이언트: Claude, ChatGPT, VS Code, Cursor 등 광범위 채택
- transports: stdio, HTTP (Streamable HTTP가 최신 권장 — 확인 필요), 과거 SSE도 지원
- 이전 references의 "840+ MCP 서버, 월간 170,000+ 개발자 방문" 수치는 외부 보도 인용이며 **확인 필요** (시점별 변동)
- 보안 우려: 2026-01 SentinelOne·2026-02 Snyk 보고는 외부 보도 — **확인 필요** (특정 % 수치는 1차 자료 검증 못함)

출처: https://modelcontextprotocol.io/ (확인일 2026-05-26)

### ④ Multi-agent Harness — Generator + Evaluator 분리
Anthropic이 long-running 실험에서 공식 검증한 핵심 패턴.

> "Tuning a standalone evaluator to be skeptical turns out to be far more tractable than making a generator critical of its own work" — Anthropic Engineering

- 3-agent 아키텍처: planner + generator + evaluator
- 정식 패턴명: **Evaluator-Optimizer** (Anthropic "Building Effective Agents")
- Stripe minions 주당 1,300 PRs/week — 사실 ✅ (외부 보도 다수), 단 Claude/Anthropic 직접 사용 명시는 **확인 필요**

출처: [[../99-sources/generator-evaluator-anthropic-harness-design-2026-05-26]]

### ⑤ Context Reset + Handoff Artifact — Sonnet 4.5 대응
Anthropic 직접 검증.
- Sonnet 4.5에서 **"context anxiety"** 용어 공식 도입
- "Compaction alone wasn't sufficient" → context resets 추가
- Handoff artifact: `claude-progress.txt` + initial git commit
- Initializer agent + coding agent 패턴
- **Opus 4.5에선 anxiety 거의 사라져 reset 제거**, single continuous session으로 운영

출처: [[../99-sources/context-anxiety-anthropic-managed-agents-2026-05-26]]

### ⑥ Commodity Shift — "모델은 commodity, 하네스가 IP"
- 출처: Addy Osmani "Agent Harness Engineering" 블로그, Louis Bouchard, MindStudio 등 커뮤니티 의견
- "If you're not the model, you're the harness." — Viv Trivedy (커뮤니티 인용)
- "A decent model with a great harness beats a great model with a bad harness." — Addy Osmani
- 단 "4개 경쟁 팀이 비슷한 하네스 구조로 수렴" 같은 구체 주장은 TechTimes 등 2차 보도 — **확인 필요**, Anthropic 공식 입장 아님
- 직접 검증 가능한 사실: awesome-harness-engineering 같은 GitHub 큐레이션 리스트가 다수 등장, Anthropic의 "harness design" 시리즈 글이 명시적으로 "harness" 용어 사용

### 트렌드별 대응 액션

| 트렌드 | 내가 해야 할 것 |
|--------|----------------|
| Skills/PD | 큰 SKILL.md를 metadata + references로 쪼개기 |
| Plugin Marketplace | 자주 쓰는 워크플로우를 plugin으로 묶기 |
| MCP | 외부 서비스 통합은 MCP 서버로 (직접 API 호출 X) |
| Generator/Evaluator | 코드 작성과 리뷰를 다른 에이전트로 분리 |
| Context Reset | handoff 스킬로 세션 명시 종료 (모델 따라 필요성 다름) |
| Commodity Shift | 하네스를 git 관리, 평가 시스템 구축 |

## 관련 자료
- [[harness-concept]] — commodity shift의 배경
- [[../02-components/skills]] — Skills 컴포넌트 상세
- [[../02-components/plugins]] — Plugin Marketplace
- [[../02-components/mcp]] — MCP 컴포넌트
- [[../03-patterns/progressive-disclosure]] — Skills 핵심 패턴
- [[../03-patterns/generator-evaluator-separation]] — Multi-agent 패턴
- [[../03-patterns/context-reset-vs-compaction]] — Reset/Handoff 패턴

## 출처
- **Anthropic 공식 (확인일 2026-05-26)**:
  - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
  - https://www.anthropic.com/engineering/harness-design-long-running-apps
  - https://www.anthropic.com/engineering/managed-agents
  - https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
  - https://code.claude.com/docs/en/discover-plugins
  - https://modelcontextprotocol.io/
- **GitHub/외부**:
  - https://github.com/anthropics/claude-plugins-official
  - https://github.com/anthropics/claude-plugins-community
  - Stripe 1,300 PRs: Lenny's Newsletter, InfoQ 2026-03
