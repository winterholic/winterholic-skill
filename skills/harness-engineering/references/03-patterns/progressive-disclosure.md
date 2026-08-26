---
name: progressive-disclosure
topic: Progressive Disclosure — metadata → SKILL.md body → bundled files 3단계 lazy load
category: 03-patterns
added: 2026-05-26
source: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills · https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
tags: [progressive-disclosure, lazy-load, skills, context-budget]
status: revised-2026-05-26
revision_note: Anthropic engineering 블로그 verbatim 인용 추가, 공식 토큰 cost 표 도입.
---

# Progressive Disclosure 패턴

## 핵심 한 줄
**필요할 때만 본문을 끌어오는 3단계 lazy load**. Anthropic이 공식 design principle로 명명한 패턴이며, Skills의 "table of contents → chapter → appendix" 구조에서 가장 명확하게 드러난다.

> **근저 학술 물리**: [[../07-llm-theory/context-rot-length-vs-performance]] — progressive disclosure는 context rot 회피의 implementation 그 자체. "고신호 토큰만 추려 넣기"(Chroma LongMemEval: focused ~300 tok ≫ full ~113k tok)를 design 차원에서 강제. 둘은 동전의 양면.

## 본문

### Anthropic 공식 정의 (verbatim)

> "Like a well-organized manual that starts with a table of contents, then specific chapters, and finally a detailed appendix, skills let Claude load information only as needed."

> "This metadata is the **first level** of _progressive disclosure_: it provides just enough information for Claude to know when each skill should be used without loading all of it into context."

> "The actual body of this file is the **second level** of detail."

> "These additional linked files are the **third level** (and beyond) of detail, which Claude can choose to navigate and discover only as needed."

### 3단계 구조 + 공식 토큰 cost

| 단계 | 내용 | 토큰 비용 | 로드 시점 |
|------|------|----------|----------|
| **Level 1: Metadata** | frontmatter (name, description) | **~100 토큰/Skill** (공식 docs 명시) | 매 세션 startup |
| **Level 2: Instructions** | SKILL.md body | **<5k 토큰** (공식 가이드라인) | 트리거 발동 시 |
| **Level 3+: Resources** | bundled files, scripts, references | 사실상 무제한 (lazy load) | 명시적 읽기/실행 시만 |

### 왜 이 구조인가
- **토큰 예산**: 모든 자료를 매 턴 컨텍스트에 넣을 수 없음
- **하지만 깊이는 필요**: 한 줄 답으로 끝나지 않는 도메인 지식
- **타협**: 인덱스만 항상 보고, 필요 시 본문 호출
- **Skills 아키텍처가 보장**: 스크립트 코드는 실행 결과만 컨텍스트로 들어옴 → 무제한 번들 가능

### Skill 작성 시 적용 (공식 예시 구조)
```
my-skill/
├── SKILL.md            # frontmatter + 핵심 본문
├── REFERENCE.md        # 상세 API/스펙
├── FORMS.md            # 특정 워크플로우 가이드
└── scripts/
    └── helper.py       # bash 실행, 코드는 context X
```

본 사용자 셋업의 `references/` 폴더 패턴도 이 3단계 정신과 일치 — Level 3 자료를 한 폴더로 정리한 변형.

### 본 스킬 (harness-engineering) 적용
- `SKILL.md`: 진입점·라우팅 (Level 2)
- `references/01-fundamentals/`: 개념 정리 (Level 3)
- `references/02-components/`: 컴포넌트 상세 (Level 3)
- `references/03-patterns/`: 패턴 (Level 3)
- `references/04-anti-patterns/`: 안티 패턴 (Level 3)
- `references/05-decision-trees/`: 의사결정 트리 (Level 3)
- `references/99-sources/`: 1차 자료 백업 (Level 3+)

### CLAUDE.md에도 같은 정신
- 글로벌 CLAUDE.md는 짧게 + 큰 자료는 별도 파일 + "필요 시 읽기" 포인터
- 단 CLAUDE.md는 항상 컨텍스트에 로드되므로 엄밀히는 Skill의 Level 1+2 혼합 자리. progressive disclosure는 Skill 전용 공식 패턴이며 CLAUDE.md는 그 정신을 차용하는 형태.

### 흔한 실수
- **flat SKILL.md**: 1500줄짜리 본문에 모든 걸 박아넣음 (Level 2 비대)
- **references 안 만들고 본문 부풀림**: 본문 매번 다 로드되는데 정작 안 쓰는 부분이 80%
- **인덱스 부재**: references만 잔뜩 있고 어느 걸 언제 읽으라는 안내가 없음
- **description 1024자 초과 시도**: 공식 hard limit (description-bloat 참조)

## 관련 자료
- [[../02-components/skills]] — Skill 구조
- [[../02-components/claude-md]] — CLAUDE.md에도 적용
- [[../04-anti-patterns/description-bloat]] — frontmatter 비대 안티 패턴
- [[../99-sources/progressive-disclosure-anthropic-docs-2026-05-26]] — 공식 verbatim 인용 백업

## 출처
- **Anthropic 공식 (확인일 2026-05-26)**:
  - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills — "first/second/third level of progressive disclosure" verbatim
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview — Level 1/2/3 토큰 cost 표 (~100/Skill, <5k SKILL.md, unlimited resources)
