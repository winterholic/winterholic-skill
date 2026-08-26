---
name: rule-over-enforcement
topic: 룰 과강제 — Iron Law 통째 적용으로 trivial 작업까지 의식화
category: 04-anti-patterns
added: 2026-05-26
source: 내부 분석 + obra/superpowers 관찰 + Anthropic "Building Effective Agents"
tags: [anti-pattern, iron-law, over-enforcement, trivial-tasks]
status: partial
verification_note: Anthropic "Building Effective Agents"는 evaluator-optimizer 패턴 사용 조건으로 "first-attempt quality already meets requirements면 X", "time/cost constraints outweigh quality면 X"를 명시 — 본 안티 패턴 정신과 정합.
---

# 룰 과강제 안티 패턴

## 핵심 한 줄
**모든 작업에 5단계 의식·Iron Law를 강제**하면 trivial 작업의 비용이 폭발한다. 룰은 강력할수록 적용 범위를 좁혀야 한다.

## 본문

### 증상
- 오타 수정·import 정리에도 TDD RED-GREEN-REFACTOR 강제
- CSS 두 줄 변경에도 brainstorming → plan → review 5단계
- "Default to discussion" 발화에도 의식 절차 의무
- "급하다/짧게" 요청에도 verification 게이트 5분 소요
- 모든 디버깅에 root-cause-tracing 4단계 강제

### 왜 안 되는가
- **trivial과 critical 구분 실패**: 5분짜리 작업이 30분 됨
- **사용자 워크플로우 파괴**: 빠른 반복 불가
- **무시 학습**: 매번 과부하 → 사용자가 룰 자체를 우회하기 시작
- **caveman·default-to-discussion 같은 다른 룰과 정면 충돌**

### Iron Law의 정상 적용 vs 과강제

| 정상 | 과강제 |
|------|--------|
| 이벤트성 트리거 (완료 주장 시) | 모든 응답에 verification |
| 두 번째 시도부터 root-cause | 첫 디버깅부터 4단계 |
| 비즈니스 로직 PR 시 TDD | typo 수정에도 RED 강제 |
| 큰 작업 시작 시 brainstorming | 1줄 응답에도 Socratic |

### superpowers 통째 도입이 위험한 이유
- 14+개 스킬 + SessionStart hook이 매 세션 강제 주입
- "You CANNOT rationalize your way out of this" 같은 도그마틱 어조
- 한국어 환경에선 트리거 false negative + 영어 키워드 false positive 둘 다 발생
- caveman·handoff·default-to-discussion과 충돌

### 교정 — 한정 적용 설계
1. **이벤트성 트리거**: "완료 주장/두 번째 디버깅/리뷰 응답" 같은 특정 이벤트만
2. **SKIP 키워드 공유**: 다른 룰의 SKIP 키워드("자세히/근거/짧게")를 함께 인식
3. **강도 모드**: lite/full/ultra 같은 강도 옵션으로 작업 크기에 맞춤
4. **trivial 화이트리스트**: typo/import/CSS 변경 같은 작업은 게이트 면제

### 사용자 셋업의 정답 (참조)
superpowers 14개 중 cherry-pick 3개만 한국어 트리거로 재작성:
- `verification-before-completion`: "완료/끝났/통과" 단어 시
- `systematic-debugging`: 두 번째 시도부터
- `receiving-code-review`: CLAUDE.md 한 줄 흡수

→ 통째 도입의 18점 vs cherry-pick 24-27점 (도입 우선순위 표 참조)

### 룰 추가 전 체크리스트
- [ ] 이벤트성 트리거로 한정 가능한가
- [ ] SKIP 키워드 정의됐는가
- [ ] 기존 룰(caveman/handoff/default-to-discussion)과 충돌 검증했는가
- [ ] trivial 작업 화이트리스트가 있는가
- [ ] Skill로 시작 후 hook 승격 단계 설계됐는가

## 관련 자료
- [[iron-laws-pattern]] — 정상 적용
- [[skill-description-tuning]] — SKIP 키워드
- [[../05-decision-trees/stop-hook-promotion-criteria]] — hook 승격 판단

## 출처
- **Anthropic 공식 (확인일 2026-05-26)**:
  - https://www.anthropic.com/research/building-effective-agents — "find the simplest solution possible, and only increase complexity when needed" 정신
- **외부**: obra/superpowers — https://github.com/obra/superpowers (Iron Law 통째 적용 사례)
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html` (섹션 3.3, 7.1, 7.4, 8.3)
