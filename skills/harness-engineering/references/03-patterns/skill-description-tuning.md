---
name: skill-description-tuning
topic: Skill description 정밀화 — "pushy" 트리거 + SKIP 키워드
category: 03-patterns
added: 2026-05-26
source: 내부 분석 + Anthropic Skills docs · 사용자 운영 관행
tags: [skill, description, triggering, false-positive, korean-keywords]
status: partial
verification_note: "Pay special attention to the name and description" 부분은 Anthropic 공식. "pushy description", "SKIP 키워드", "한국어·영어 병기"는 사용자 운영 관행 (공식 가이드 아님).
---

# Skill Description Tuning

## 핵심 한 줄
**Claude는 under-trigger 경향**이라 description을 의도적으로 pushy하게 쓴다. 한국어·영어 키워드 병기 + SKIP 키워드 + 카테고리 분류로 false positive 함께 잡는다.

> **근저 학술 물리**: [[../07-llm-theory/context-rot-length-vs-performance]] — description은 brittleness(Sclar: 포맷·구분자 차이만으로 ±76점) + length(context rot) 둘 다의 영향권. "pushy하게 쓰되 너무 길면 매 세션 비용" 트레이드오프의 1차 근거.

## 본문

### 핵심 관찰
- Claude는 **발동 안 하는 쪽으로 기우는 경향**
- description이 모호하면 정확한 상황에서도 스킬이 안 켜짐
- 그래서 description은 의도적으로 "pushy" — 트리거 키워드를 명시 나열

### 좋은 description의 4요소
1. **트리거 키워드 명시 나열**: "다음 표현이 메시지에 있으면 자동 발동"
2. **언어 병기**: 한국어·영어 양쪽 키워드
3. **SKIP 키워드**: 함께 있으면 발동 안 할 단어 명시
4. **카테고리 분류**: 키워드를 의미 그룹으로 묶어 디버깅 쉽게

### caveman 스킬 예 (A+, 91.4점)
```yaml
description: |
  자동 트리거 5개 카테고리:
  (1) 명시적 짧음 요청: "짧게", "간단히", "TL;DR" ...
  (2) 빠른 진행·캐주얼 톤: "ㄱㄱ", "ㅇㅇ", "빨리" ...
  (3) 디버깅 반복 루프: "왜 안 돼", "에러 봐줘" ...
  (4) 확인성 질문: "맞아?", "되나?" ...
  (5) 의사결정 확인: "이거 해도 돼", "괜찮아?" ...
  
  SKIP: "자세히", "설명해줘", "왜 그런지", "근거", "원리", "설계", "RFC" ...
```

### Description-space 경합
- frontmatter는 매 세션 컨텍스트에 로드됨
- 너무 많은 스킬 × 너무 긴 description = 컨텍스트 압박
- 해결: 트리거 키워드는 풍부하게, 본문 설명은 줄이고 references로 옮김

### 한국어 환경 주의점
- 영어 SKILL.md 그대로 두면 한국어 발화에 false negative
- 영어 키워드만 있는 description이 우연히 발화에 매칭되면 false positive
- **한국어 사용자는 description을 한국어로 재작성** 필수 (영어 키워드 병기 OK)

### 정밀화 방법
1. **사용 로그 관찰**: 어떤 발화에서 발동/안 발동했는가
2. **false positive 키워드 → SKIP에 추가**
3. **false negative 발화 → 트리거 키워드 추가**
4. **`skills-estimate`로 정량 채점**: 14개 항목 rubric

### 트리거 키워드 작성 팁
- 사용자가 실제 쓰는 표현 (감탄사, 줄임말 포함)
- 동의어·유사 표현 모두 나열
- "EXPLICIT 호출 키워드" vs "암묵적 트리거"를 구분 표시

## 관련 자료
- [[components/skills]] — Skill 컴포넌트
- [[progressive-disclosure]] — frontmatter 부담 줄이기
- [[anti-patterns/description-bloat]] — 비대 위험

## 출처
- **Anthropic 공식 (확인일 2026-05-26)**:
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview — "Pay special attention to the name and description of your skill" verbatim, description 1024자 hard limit
  - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills — startup pre-load 정의
- **사용자 운영 관행** (공식 아님): "pushy" description, SKIP 키워드, 한국어·영어 병기, skills-estimate 14항목 rubric
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html`
