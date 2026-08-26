---
name: skills
topic: Skills — Progressive Disclosure로 lazy load되는 전문 지식
category: 02-components
added: 2026-05-26
source: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview · https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
tags: [skills, skill-md, progressive-disclosure, triggering]
status: revised-2026-05-26
revision_note: Anthropic 공식 docs로 SKILL.md 필드 제약·정확한 토큰 cost 보강.
---

# Skills — Skill 컴포넌트

## 핵심 한 줄
**3단계 progressive disclosure**(metadata → SKILL.md body → bundled files)로 lazy load되는 전문 지식 묶음. description-based triggering으로 자동 발동된다. Anthropic 공식 분류로 확정된 패턴.

## 본문

### 구조 (공식 권장 예시)
```
skill-name/
├── SKILL.md          # frontmatter(metadata) + 본문(instructions)
├── REFERENCE.md      # 상세 참조 자료
├── FORMS.md          # 특정 워크플로우 가이드
└── scripts/          # 실행 스크립트 (bash로 호출, 코드는 context에 안 들어감)
```

본 사용자 셋업은 `references/` 폴더 패턴을 쓰는데, 공식 예시는 `FORMS.md`·`REFERENCE.md` 같은 flat 파일도 OK. 둘 다 Level 3 lazy load.

### 3단계 progressive disclosure (공식 표 verbatim)

| 단계 | 내용 | 토큰 비용 | 로드 시점 |
|------|------|----------|----------|
| **Level 1: Metadata** | YAML frontmatter (name, description) | **~100 토큰/Skill** | 항상 (startup) |
| **Level 2: Instructions** | SKILL.md body | **<5k 토큰** | 트리거 발동 시 |
| **Level 3+: Resources** | bundled files, scripts | **사실상 무제한** (필요 시 bash로 호출, 스크립트 코드는 context에 안 들어감) | 명시적으로 읽을 때만 |

> "At startup, the agent pre-loads the `name` and `description` of every installed skill into its system prompt." — Anthropic engineering

### SKILL.md frontmatter 공식 필드 제약 (2026-05-26 확인)

| 필드 | 필수 | 제약 |
|------|------|------|
| `name` | 필수 | 최대 64자, 소문자·숫자·하이픈만, "anthropic"/"claude" 예약어 금지, XML 태그 금지 |
| `description` | 필수 | non-empty, **최대 1024자**, XML 태그 금지 |

→ description은 1024자 hard limit. 본 references의 description-bloat.md가 권장하는 50줄 가이드와 함께 보면, 1024자(약 30-40줄)가 사실상 상한.

### description-based triggering
- Anthropic 공식: "Pay special attention to the `name` and `description` of your skill. Claude will use these when deciding whether to trigger the skill in response to its current task."
- 사용자 셋업 운영 경험: Claude는 **under-trigger 경향** → description을 명시적·"pushy"하게 작성
- 한국어 환경에선 한국어·영어 키워드 병기 권장 (사용자 운영 관행, 공식 가이드 아님)
- SKIP 키워드도 명시해 false positive 방지 (사용자 내부 관행, 공식 docs에는 SKIP 패턴 별도 언급 없음)

### Skills의 도달 가능 환경 (공식)
- **Claude API**: code-execution-2025-08-25, skills-2025-10-02, files-api-2025-04-14 베타 헤더 필요
- **Claude Code**: filesystem 기반, `~/.claude/skills/` 또는 `<project>/.claude/skills/`
- **claude.ai**: zip 업로드, 개인별 (org-wide 공유 불가)

### 14+개 스킬을 묶는 단위 (superpowers 외부 사례 — 비공식)
- 카테고리 폴더: architecture / collaboration / debugging / meta / problem-solving / research / testing / using-skills
- 부트스트랩 스킬이 SessionStart hook으로 다른 스킬 트리거를 강제하는 패턴

### SKILL 신설 vs 보강 판단 (내부 관행)
- **신설**: 명확한 트리거 키워드 + 독립 영역 + 자주 발동
- **기존 스킬 보강**: 부분 겹침 + 트리거 모호 + 가끔 발동
- 무분별 신설은 description-space 경합 → false positive 증가

### Skill 평가 (내부 관행)
사용자 셋업 `skills-estimate` 패턴: 14개 항목 rubric으로 채점. **공식 평가 시스템 아님**, 사용자 자체 도구.

## 관련 자료
- [[claude-md]] · [[memory]] · [[hooks]] — 다른 컴포넌트와 역할 분담
- [[../03-patterns/progressive-disclosure]] — 3단계 PD 패턴
- [[../03-patterns/skill-description-tuning]] — description 정밀화
- [[../04-anti-patterns/description-bloat]] — description 비대 안티 패턴
- [[../05-decision-trees/skill-vs-hook-vs-claude-md]] — 어디에 둘지
- [[../99-sources/progressive-disclosure-anthropic-docs-2026-05-26]] — 공식 인용 백업

## 출처
- **Anthropic 공식 (확인일 2026-05-26)**:
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview — Level 1/2/3 토큰 cost 표, name/description 필드 제약
  - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills — progressive disclosure 정의·"first/second/third level" verbatim
  - https://code.claude.com/docs/en/skills — Claude Code Skills
  - https://github.com/anthropics/skills — open-source skills repo
