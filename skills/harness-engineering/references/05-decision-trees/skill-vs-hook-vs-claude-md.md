---
name: skill-vs-hook-vs-claude-md
topic: 새 룰·동작을 Skill·Hook·CLAUDE.md 중 어디에 굳힐지 결정
category: 05-decision-trees
added: 2026-05-26
source: 내부 분석 + Claude Code Skills/Hooks 공식 docs
tags: [decision-tree, skill, hook, claude-md, persistence]
status: revised-2026-05-26
revision_note: CLAUDE.md "200줄 초과 truncate" 같은 정확 임계치는 공식 docs에서 명시적 확인 못함 — Anthropic 공식 입장은 "충돌 시 임의 선택" 경고.
---

# 결정 트리 — Skill vs Hook vs CLAUDE.md

## 핵심 한 줄
**자동 강제(hook) > 모든 세션 적용(CLAUDE.md) > 트리거 기반(Skill)** 순으로 좁혀라. 더 좁은 도구를 쓸 수 있으면 그쪽이 정답.

## 결정 트리

```
1. 사용자가 잊어도 자동으로 강제돼야 하는가?
   ├─ YES → Hook (Stop/PreToolUse/UserPromptSubmit/SessionStart)
   │        - Stop: 응답 마무리 직전 체크 (work-history 강제 등)
   │        - PreToolUse: 위험 명령 차단
   │        - UserPromptSubmit: 사용자 입력에 컨텍스트 주입
   │        - SessionStart: 세션 시작 시 1회 알림
   │        ⚠ 매번 발동 → 노이즈 위험. 임계치 분명할 때만
   │
   └─ NO → 2번
   
2. 모든 작업·세션에 영향을 주는 기본 룰인가?
   ├─ YES → CLAUDE.md (글로벌 또는 프로젝트별)
   │        - 글로벌: ~/.claude/CLAUDE.md (모든 프로젝트)
   │        - 프로젝트: <repo>/.claude/CLAUDE.md (해당 repo만)
   │        - 항상 컨텍스트에 로드됨 → 짧고 압축적으로
   │        ⚠ 200줄 넘으면 truncate 위험. progressive disclosure 위반
   │
   └─ NO → 3번
   
3. 특정 발화·상황에만 발동하면 되는가?
   ├─ YES → Skill (~/.claude/skills/<name>/SKILL.md)
   │        - description 트리거에 한국어 키워드 풍부히
   │        - 본문은 references/로 분리 (progressive disclosure)
   │        - 발동 안 하면 토큰 0
   │
   └─ NO → 사용자 정보 누적용이면 메모리(feedback_*.md), 아니면 일회성
```

## 비교 표

| 항목 | Hook | CLAUDE.md | Skill |
|------|------|-----------|-------|
| 발동 | 자동 (이벤트) | 항상 (컨텍스트 로드) | 트리거 발화 시 |
| 토큰 비용 | 낮음 (출력만) | 매 turn 입력 토큰 차지 | 발동 시에만 |
| 강제력 | 강 (차단 가능) | 중 (모델 준수에 의존) | 약 (트리거 미스 시 미발동) |
| 디버깅 | 어려움 (이벤트 추적) | 쉬움 (파일 1개) | 중간 (description 튜닝 필요) |
| 적합 | 안전·검증·체크리스트 | 페르소나·기본 규약 | 도메인 작업·워크플로우 |

## 함정

- **모든 걸 hook으로 강제**: 노이즈 폭발. Stop hook 매번 발동 → 사용자가 무시 시작 → 죽은 룰
- **CLAUDE.md 비대화**: 200줄 초과 시 truncate. progressive disclosure 원칙 위반. → 큰 자료는 Skill로
- **Skill description 부실**: 트리거 키워드 부족 → 발동 안 함. 한국어 발화 변형 30~40개 박는 게 안전
- **메모리에 룰 적기**: 메모리는 "사용자 정보"용. 행동 강제는 hook/CLAUDE.md/Skill. → [[memory-vs-claude-md-vs-skill]] 참조

## 본 사용자 셋업 사례

| 룰 | 어디에 | 왜 |
|----|--------|-----|
| work-history 작성 강제 | Stop hook | 잊어도 자동 발동 필요 |
| Korean 응답 | CLAUDE.md 글로벌 | 모든 세션 기본 |
| caveman 압축 | Skill | 특정 발화에만 |
| handoff 인계 | Skill + CLAUDE.md 1줄 룰 | 트리거 기반이지만 첫 행동 강제 필요 |
| 사용자 git 정책 | feedback 메모리 + CLAUDE.md | 정보(메모리) + 룰(CLAUDE.md) 이중화 |

## 관련 자료
- [[memory-vs-claude-md-vs-skill]] — 메모리와의 경계
- [[stop-hook-promotion-criteria]] — Skill → hook 승격 시점
- [[research-methodology]] — Anthropic 최신 docs 확인 절차

## 출처
- **공식 (확인일 2026-05-26)**:
  - https://code.claude.com/docs/en/skills — Claude Code Skills
  - https://code.claude.com/docs/en/hooks — Claude Code Hooks (~29개 events)
  - https://code.claude.com/docs/en/memory — memory file 계층
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview — Skills frontmatter 제약
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html`
