---
name: plugins
topic: Plugins — MCP·skill·agent·hook·LSP를 묶은 배포 단위
category: 02-components
added: 2026-05-26
source: https://code.claude.com/docs/en/discover-plugins
tags: [plugins, marketplace, bundle, versioning]
status: revised-2026-05-26
revision_note: Claude Code 공식 docs 기반으로 plugin 구성 요소·marketplace 동작 정확화. 미검증 보안 수치는 "확인 필요".
---

# Plugins — 플러그인 컴포넌트

## 핵심 한 줄
Plugin은 **skills + agents + hooks + MCP servers + LSP servers + slash commands**를 묶어 배포·설치·관리하는 단위 (Claude Code 공식). 공식 마켓플레이스 `anthropics/claude-plugins-official`이 Claude Code 시작 시 자동 로드.

## 본문

### 공식 정의 (verbatim)

> "Plugins extend Claude Code with skills, agents, hooks, and MCP servers."
> "The official Anthropic marketplace (`claude-plugins-official`) is automatically available when you start Claude Code."

### Plugin이 담을 수 있는 것 (공식 docs 명시)
- **Skills** — `~/.claude/skills/<name>` 형태로 namespaced
- **Agents** — subagent 정의
- **Hooks** — settings.json hook 등록
- **MCP servers** — 외부 시스템 통합
- **LSP servers** — Language Server Protocol (코드 인텔리전스)
- **Slash commands** — `/<plugin-name>:<command>` 형태로 namespaced

이전 references는 "MCP servers + slash commands + skills"만 적었으나 hooks·LSP·agents도 포함이 정확.

### 공식 마켓플레이스 카테고리 (공식 docs verbatim)

| 카테고리 | 예시 plugin |
|---------|-------------|
| **Code intelligence (LSP)** | clangd-lsp, gopls-lsp, pyright-lsp, rust-analyzer-lsp, typescript-lsp 등 11개 언어 |
| **External integrations** | github, gitlab, atlassian, asana, linear, notion, figma, vercel, firebase, supabase, slack, sentry |
| **Development workflows** | commit-commands, pr-review-toolkit, agent-sdk-dev, plugin-dev |
| **Output styles** | explanatory-output-style, learning-output-style |

### 두 가지 공식 마켓플레이스
- `claude-plugins-official` — Anthropic 큐레이트, 시작 시 자동 로드
- `claude-plugins-community` — 자동 검증·안전 스크리닝 통과한 3rd-party, 수동 add

### Plugin 설치 scope
- **User scope**: 모든 프로젝트에 적용 (기본)
- **Project scope**: 해당 repo collaborator 전체에 적용
- **Local scope**: 본인+해당 repo만

### 대표 외부 플러그인 (사용자 셋업 참조)
- **obra/superpowers**: 14+개 스킬 + SessionStart hook + 부트스트랩 (커뮤니티)
- **agent-teams**: multi-agent orchestration (13개 슬래시 명령)

### Skill 단일 배포 vs Plugin 배포

| 상황 | 선택 |
|------|------|
| SKILL.md 1개만 공유 | Skill 단일 |
| 여러 SKILL + MCP + 슬래시 명령어 묶음 | Plugin |
| 버전 관리 필요 | Plugin |
| SessionStart 등 hook 포함 | Plugin |
| LSP 코드 인텔리전스 | Plugin (필수) |

### 보안 우려
공식 docs warning:
> "Plugins and marketplaces are highly trusted components that can execute arbitrary code on your machine with your user privileges. Only install plugins and add marketplaces from sources you trust."

- 이전 references의 "2026-02 Snyk 13% critical 결함" 수치는 외부 보도 인용 — **확인 필요**
- 검증된 출처만 설치 권장 (공식 입장)

### 통째 도입 vs Cherry-pick
Plugin은 묶음 단위지만, 통째 도입은 신중해야 함.
- 14+개 스킬 다 트리거되면 description-space 경합
- 메서드론이 기존 워크플로우와 충돌 가능
- 가치 있는 스킬만 cherry-pick해서 자기 셋업에 흡수하는 접근이 안전

(예: superpowers 14개 중 사용자 셋업에 가치 있는 건 3개로 평가됨 — `verification-before-completion`, `systematic-debugging+root-cause-tracing`, `receiving-code-review`)

## 관련 자료
- [[skills]] — plugin의 주요 구성 요소
- [[mcp]] — plugin의 주요 구성 요소
- [[subagents]] — agent-teams plugin의 핵심
- [[hooks]] — plugin이 hook 포함 가능
- [[../01-fundamentals/2026-trends]] — Plugin Marketplace 트렌드

## 출처
- **공식 (확인일 2026-05-26)**:
  - https://code.claude.com/docs/en/discover-plugins — plugin 구성·marketplace·설치·security
  - https://github.com/anthropics/claude-plugins-official
  - https://github.com/anthropics/claude-plugins-community
- obra/superpowers — https://github.com/obra/superpowers
- 마켓플레이스 카탈로그 — https://claude.com/plugins
