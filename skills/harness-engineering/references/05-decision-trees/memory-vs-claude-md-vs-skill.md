---
name: memory-vs-claude-md-vs-skill
topic: 사용자 정보·룰·워크플로우를 메모리·CLAUDE.md·Skill 중 어디에 굳힐지
category: 05-decision-trees
added: 2026-05-26
source: 내부 분석 + Claude Code memory docs · Anthropic Skills docs
tags: [decision-tree, memory, claude-md, skill, learning-loop, persistence]
status: partial
verification_note: 4가지 memory type (user/feedback/project/reference) 분류는 사용자 셋업의 auto-memory 동작 관찰 — Anthropic 공식 docs에서 명시적 4-type 분류는 미확인. memory file precedence 공식 동작은 [[../02-components/claude-md]] 참조.
---

# 결정 트리 — Memory vs CLAUDE.md vs Skill

## 핵심 한 줄
**메모리 = 사용자에 대한 사실 / CLAUDE.md = 항상 적용할 룰 / Skill = 트리거 기반 워크플로우.** 본 사용자 학습 루프의 "굳히기 결정" 핵심.

## 셋 다 "지속성"이지만 결이 다르다

| 항목 | 메모리 | CLAUDE.md | Skill |
|------|--------|-----------|-------|
| 본질 | 사용자에 관한 사실·선호 | 행동 규약 | 발동형 워크플로우 |
| 주체 | Claude 자동 작성 | 사용자가 직접 작성 | 사용자+Claude 협업 |
| 발동 | 관련 컨텍스트에서 자동 회수 | 매 turn 컨텍스트 로드 | description 트리거 |
| 예시 | "사용자는 commit/push를 명시 요청에만" | "한국어로 응답" | "/handoff 발동 시 인계 문서 작성" |
| 변경 빈도 | 자주 (대화 흐름에 따라) | 드물게 | 중간 |
| 비용 | 회수 시에만 | 매 turn 토큰 | 발동 시에만 |

## 결정 트리

```
새로 굳히려는 항목이 무엇인가?

1. 사용자가 누구·뭘 좋아함·어떤 도구 씀 같은 "사실"인가?
   ├─ YES → 메모리 (type: user)
   │        예: "사용자는 Python 10년 차, React는 처음"
   │
   └─ NO → 2번

2. 사용자가 명시적으로 "이렇게 해 / 이거 하지 마"라고 한 규약인가?
   ├─ YES → 2-a: 모든 작업에 항상 적용? 
   │              ├─ YES → CLAUDE.md (글로벌 또는 프로젝트)
   │              └─ NO  → 메모리 (type: feedback)
   │        예 (CLAUDE.md): "한국어 응답", "git push 금지"
   │        예 (메모리): "이 사용자는 mock DB 테스트 싫어함 (사고 경험 있음)"
   │
   └─ NO → 3번

3. 진행 중 작업·프로젝트 상태인가?
   ├─ YES → 메모리 (type: project) 또는 work-history
   │        예: "auth 리팩터는 legal 요구사항이 발단"
   │
   └─ NO → 4번

4. 외부 시스템 위치 정보인가?
   ├─ YES → 메모리 (type: reference)
   │        예: "버그는 Linear INGEST 프로젝트에 기록됨"
   │
   └─ NO → 5번

5. 특정 발화에 발동할 워크플로우/도구·체크리스트인가?
   ├─ YES → Skill
   │        예: /handoff, /caveman, /verification
   │
   └─ NO → 일회성, 굳히지 않음
```

## 학습 루프 굳히기 — 본 사용자 약점

본 사용자 학습 루프 평가에서 **분석(11/20) + 정리(8/20)** 가 약점. 5요소 중 굳히기 자체는 양호(15/20)지만, **"어디에 굳힐지 잘못 골라서"** 같은 지적이 반복되는 경우가 있음:

- ❌ 행동 규약을 메모리에 적음 → 메모리는 회수가 컨텍스트 기반 → 안 회수되면 미발동
- ❌ 사용자 사실을 CLAUDE.md에 적음 → 항상 토큰 차지, 변경 비용 큼
- ❌ 트리거 기반 워크플로우를 CLAUDE.md에 적음 → 매 turn 노이즈

**올바른 분리**:
- 사실 → 메모리
- 항상 적용 규약 → CLAUDE.md
- 트리거 워크플로우 → Skill

## 메모리 type 4가지 (Anthropic auto-memory)

CLAUDE.md auto-memory 섹션 참조:
- **user**: 사용자 정체성·역할·지식
- **feedback**: 사용자가 준 행동 가이드 (corrections + confirmations 둘 다)
- **project**: 진행 중 작업·왜·언제까지
- **reference**: 외부 시스템 위치 정보

## 안티 패턴

- **메모리에 코드 패턴·관행 적기** → 코드 읽으면 알 수 있는 건 메모리 ❌
- **메모리에 일회성 task 상태** → work-history나 plan에. 메모리는 세션 간 지속용
- **CLAUDE.md에 페르소나 외 모든 룰 다 적기** → 200줄 초과 truncate

## 관련 자료
- [[skill-vs-hook-vs-claude-md]] — hook과의 경계
- [[learning-loop-diagnosis]] — 학습 루프 진단 *(예정)*
- [[memory-curation]] — 메모리 정리 *(예정)*

## 출처
- **공식 (확인일 2026-05-26)**:
  - https://code.claude.com/docs/en/memory — memory file 계층·precedence 공식 동작 (충돌 시 임의 선택 경고 포함)
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview — Skill 트리거 메커니즘
  - https://code.claude.com/docs/en/hooks — hook 강제 layer
- 사용자 메모리 4개 사례: `~/.claude/projects/<project-id>/memory/`
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html`
