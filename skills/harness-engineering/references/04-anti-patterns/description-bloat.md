---
name: description-bloat
topic: Description 비대 — frontmatter에 모든 걸 박아넣음
category: 04-anti-patterns
added: 2026-05-26
source: 내부 분석 + Anthropic Skills 공식 제약
tags: [anti-pattern, skills, frontmatter, context-bloat]
status: revised-2026-05-26
revision_note: description 1024자 hard limit (Anthropic 공식)을 명시. 본 안티 패턴의 실증적 근거가 됨.
---

# Description 비대 안티 패턴

## 핵심 한 줄
**SKILL.md frontmatter의 description에 본문까지 박아넣어** 매 세션 컨텍스트를 부풀리는 안티 패턴. progressive disclosure 정신과 정면 충돌.

> **근저 학술 물리**: [[../07-llm-theory/context-rot-length-vs-performance]] — 매 세션 frontmatter 로드 = 길이 누적 = context rot 직접 사례. Chroma 18모델 전부 길이↑ 시 성능↓. description 비대는 "광고 윈도우 ≠ effective length"의 일상 버전.

## 본문

### 증상
- `description: |` 안에 5~10페이지 분량의 설명·예시·룰
- 트리거 키워드뿐 아니라 절차·결과 형식·예외 처리까지 다 들어감
- 매 세션 frontmatter가 컨텍스트에 로드 → 토큰 압박
- 스킬 10개만 돼도 컨텍스트의 큰 부분 차지

### 왜 발생하는가
- "description이 풍부할수록 트리거 정밀해진다"는 오해
- 본문(core)을 따로 두는 progressive disclosure 패턴 미숙
- references/ 폴더를 안 쓰고 모든 걸 SKILL.md 한 파일에 박는 습관

### 진짜 description의 역할
- **트리거 결정에 필요한 최소 정보**만
- 키워드 + SKIP 키워드 + 카테고리 분류
- 절차·예시·예외는 본문(core) 또는 references로

### 좋은 description 분량 가이드

| 요소 | 권장 분량 |
|------|----------|
| 한 줄 정의 | 1줄 |
| 트리거 키워드 (카테고리별) | 5-15줄 |
| SKIP 키워드 | 2-5줄 |
| 강도/모드 옵션 (있으면) | 2-5줄 |
| **합계** | 보통 20-50줄 이내 |

### 비대 description 진단
- 50줄 초과 → 본문으로 옮길 거리 있는지 확인
- 100줄 초과 → 거의 확실히 비대
- "예시" 섹션이 description에 있다 → 본문으로
- "예외 처리" 디테일이 description에 있다 → 본문으로

### 교정
1. **본문 분리**: description은 트리거에만 집중
2. **references/ 활용**: 상세 자료는 lazy load 영역으로
3. **인덱스 패턴**: SKILL.md 본문에 "상세는 references/X 참조" 포인터

### 사용자 셋업의 description-space 경합 우려
- 스킬 24개 × 100토큰 description = 2400토큰 = 컨텍스트의 ~1.5%
- 비대해지면 5%, 10%까지 — 다른 자료가 밀려남
- frontmatter는 캐시되지만 cache miss나 invalidate 시 비용 발생

## 관련 자료
- [[progressive-disclosure]] — 정상 패턴
- [[skill-description-tuning]] — description 정밀화
- [[components/skills]] — Skill 컴포넌트

## 출처
- **Anthropic 공식 (확인일 2026-05-26)**:
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview — description 필드 hard limit 1024자, ~100 토큰/Skill 명시
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html` (섹션 7.1)
- [[../99-sources/progressive-disclosure-anthropic-docs-2026-05-26]] — 공식 제약 백업
