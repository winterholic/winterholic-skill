---
name: mcp-vs-skill
topic: 외부 도구/서비스 통합을 MCP 서버로 만들지 Skill로 만들지
category: 05-decision-trees
added: 2026-05-26
source: https://modelcontextprotocol.io · https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
tags: [decision-tree, mcp, skill, integration]
status: active
verification_note: MCP "USB-C for AI applications" 정의 검증 완료. Skill progressive disclosure 3-level 정의 검증 완료.
---

# 결정 트리 — MCP vs Skill

## 핵심 한 줄
**MCP = 외부 시스템과 도구 호출 프로토콜 / Skill = Claude 안에서 실행되는 워크플로우 묶음.** 둘은 경쟁이 아니라 다른 레이어.

## 본질 차이

| 항목 | MCP 서버 | Skill |
|------|----------|-------|
| 위치 | 별도 프로세스 (로컬·원격) | `~/.claude/skills/` 안 |
| 실행 | 외부 프로세스가 도구 호출 받음 | Claude 컨텍스트에 SKILL.md 로드 |
| 발견 | `claude_desktop_config.json` 또는 `~/.claude/mcp.json` 등록 | description 트리거 자동 |
| 적합 | 외부 API·DB·파일시스템 접근, 인증·토큰 관리 | 절차·체크리스트·결정 트리·템플릿 |
| 비용 | 프로세스 관리 + 도구 호출 라운드트립 | 로드 토큰만 |
| 업데이트 | 서버 코드 재배포 | 파일 수정 |
| 권한 | 도구 단위 사용자 허락 | 호출 시 일반 tool 권한 |

## 결정 트리

```
1. 외부 시스템(DB·API·파일시스템 등)을 호출해야 하는가?
   ├─ YES → 2번
   └─ NO  → Skill (절차·결정·템플릿이면 무조건 Skill)

2. Claude의 기본 도구(Bash, WebFetch, Read 등)로 해결 가능한가?
   ├─ YES → Skill에 절차만 적어도 충분. MCP는 과잉
   │        예: gh CLI로 PR 다루기 → /pr-review Skill로 충분
   │
   └─ NO  → 3번 (네이티브 SDK·인증·세션 관리 필요)

3. 호출이 반복적이고 다중 turn 사용되는가?
   ├─ YES → MCP 서버 (프로토콜 안정성)
   │        예: Linear·Notion·Obsidian 같은 서비스 통합
   │
   └─ NO  → 일회성이면 Bash 한 줄 + 사용자 직접 실행
```

## 함께 쓰는 패턴

MCP와 Skill은 **조합 가능**:
- MCP가 외부 시스템 도구 제공 (mcp__obsidian__write_file 등)
- Skill이 그 도구를 언제·어떻게 쓸지 안내 (예: handoff Skill이 obsidian MCP 도구를 호출)

## 본 사용자 셋업 사례

| 통합 | 방식 | 이유 |
|------|------|------|
| vault | MCP (`mcp__obsidian__*`) | 파일 다수, 인증 없음, 자주 호출 |
| GitHub | gh CLI + Skill (/pr-review) | 기본 도구로 충분 |
| Notion | MCP (`mcp__claude_ai_Notion__*`) | 외부 API + 인증 |
| Linear | (해당 없음) | 도입 안 함 |

## 안티 패턴

- **CLI로 충분한데 MCP 만들기** — 유지보수 비용 폭발
- **MCP 도구를 워크플로우 없이 던지기** — 사용자는 언제 어떤 도구 쓸지 모름 → Skill로 절차 묶기
- **Skill에 외부 API 호출 코드 직접 박기** — 인증·재시도·세션 관리 안 됨 → MCP가 맞음

## 관련 자료
- [[skill-vs-hook-vs-claude-md]]
- [[plugin-marketplace]] *(예정)* — Plugin은 MCP+Skill+hook 묶음 배포 단위

## 출처
- **공식 (확인일 2026-05-26)**:
  - https://modelcontextprotocol.io/ — MCP "USB-C for AI applications" verbatim
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview — Skill 3-level progressive disclosure
  - https://code.claude.com/docs/en/skills — Claude Code Skills
  - https://code.claude.com/docs/en/discover-plugins — Plugin MCP 통합 카테고리
- 사용자 셋업 참조 (확인 필요)
