---
name: mcp
topic: MCP — Model Context Protocol, "Agent용 USB-C"
category: 02-components
added: 2026-05-26
source: https://modelcontextprotocol.io/
tags: [mcp, tools, integration, security]
status: revised-2026-05-26
revision_note: 공식 modelcontextprotocol.io 정의·transports 검증. 미검증 수치는 "확인 필요" 표시.
---

# MCP — Model Context Protocol

## 핵심 한 줄
**외부 시스템을 표준화된 방식으로 LLM에 연결**하는 오픈 프로토콜. Anthropic 공식 표현: *"Think of MCP like a USB-C port for AI applications."*

## 본문

### 공식 정의 (verbatim, modelcontextprotocol.io)

> "MCP (Model Context Protocol) is an open-source standard for connecting AI applications to external systems."

> "Using MCP, AI applications like Claude or ChatGPT can connect to data sources (e.g. local files, databases), tools (e.g. search engines, calculators) and workflows (e.g. specialized prompts)—enabling them to access key information and perform tasks."

> "Just as USB-C provides a standardized way to connect electronic devices, MCP provides a standardized way to connect AI applications to external systems."

### 클라이언트 채택 (공식 명시)
Claude, ChatGPT, Visual Studio Code, Cursor 등 광범위. MCP는 "build once and integrate everywhere" 정신.

### Transports
- **stdio**: 로컬 프로세스 — 가장 단순
- **HTTP** (Streamable HTTP 권장 — 확인 필요): 원격 서비스
- 과거 SSE도 있으나 현재 권장 transport는 streamable HTTP로 통합되는 추세 (확인 필요)

### 2026 현황 — 확인 필요 수치
- 이전 references의 "840+ MCP 서버, 월간 170,000+ 개발자 방문" 수치는 외부 보도 인용, 1차 자료 미확인 — **확인 필요**, 시점별 변동
- 확실히 검증 가능한 사실: Plugin Marketplace의 External Integrations 카테고리에 github, gitlab, linear, asana, notion, figma, vercel, supabase, slack, sentry 등 MCP 서버가 번들로 배포됨

### Skills vs MCP — 언제 어느 것?

| 상황 | 선택 |
|------|------|
| 외부 서비스 통합 (GitHub, Linear, Slack 등) | MCP |
| LLM 작업 절차·메서드론 | Skill |
| 정적 도메인 지식 | Skill |
| 동적 데이터 접근 | MCP |
| 사내 시스템 연동 | MCP (직접 작성) |

상세 판단: [[../05-decision-trees/mcp-vs-skill]]

### MCP 서버 작성
- `mcp-builder` 스킬 활용 (사용자 셋업)
- Python(FastMCP) 또는 Node/TypeScript(MCP SDK)
- 도구 스키마·에러 컨벤션 표준 준수

### 보안 이슈 — 확인 필요
이전 references의 "2026-01 SentinelOne 감사: plugin 보안 결함", "2026-02 Snyk: 13% critical 결함" 같은 구체 수치는 외부 보도 인용으로 1차 자료에서 직접 확인 못함 — **확인 필요**.

확실히 검증 가능: Claude Code 공식 docs는 "Plugins and marketplaces are highly trusted components that can execute arbitrary code on your machine with your user privileges. Only install plugins and add marketplaces from sources you trust." (https://code.claude.com/docs/en/discover-plugins) 라고 명시.

### permission-gated 노출
- settings.json의 permissions로 MCP 도구별 allow/deny 제어
- 처음 만나는 도구는 ask 모드로 시작 → 신뢰 확인 후 allow 승격

## 관련 자료
- [[skills]] — 도구가 아닌 절차의 자리
- [[hooks]] — PreToolUse로 MCP 호출 게이트
- [[plugins]] — MCP 서버를 묶어서 배포하는 단위
- [[../05-decision-trees/mcp-vs-skill]] — 어디에 둘지

## 출처
- **공식 (확인일 2026-05-26)**: https://modelcontextprotocol.io/ — "USB-C for AI applications" verbatim
- https://code.claude.com/docs/en/discover-plugins — Plugin Marketplace 내 MCP 통합 카테고리
