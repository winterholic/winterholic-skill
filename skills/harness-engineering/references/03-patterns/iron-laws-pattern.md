---
name: iron-laws-pattern
topic: Iron Laws — 도그마틱 룰의 가치와 한계
category: 03-patterns
added: 2026-05-26
source: 내부 분석 + obra/superpowers 외부 관찰
tags: [iron-law, dogma, enforcement, prompt-pressure, trade-off]
status: partial
verification_note: "Iron Law" 표현·"NO X WITHOUT Y" 패턴은 obra/superpowers GitHub의 SKILL 본문에서 확인 가능. Anthropic 공식 패턴 아님 — 커뮤니티 관행.
---

# Iron Laws 패턴

## 핵심 한 줄
**"NO X WITHOUT Y" 형태의 도그마틱 룰**로 LLM의 합리화·우회를 차단. 비즈니스 로직엔 강력하지만 trivial 작업엔 과부하 — **이벤트성 트리거**로 한정 적용이 정답.

## 본문

### Iron Law 정의
- **단순·강한 룰**: "X 없이는 Y 금지" 한 줄
- **합리화 차단**: "예외" 만들기 어렵게 설계
- **Red Flags 표 동반**: skip을 정당화하는 단어들 미리 명시 ("just this once", "good enough" 같은)
- **우회 차단 문구**: "Violating the letter is violating the spirit"

### superpowers의 3개 Iron Laws

| 룰 | 도메인 |
|----|--------|
| NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST | TDD |
| NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST | Debugging |
| NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE | Verification |

### 메커니즘 — 코드 아닌 프롬프트 강제력
- 결정론적 게이트는 없음 (hook 차단 아님)
- 순수 **프롬프트 압력**: Iron Law 헤더 + Red Flags + 우회 차단 문구
- SessionStart hook이 매 세션 SKILL 전문 주입 → auto-trigger 강제
- self-policing 유도

### Iron Law의 양면성

**강력한 자리**
- 비즈니스 로직, 중요 모듈
- 검증 빠뜨리면 큰 사고
- 디버깅 회피로 같은 버그 재발

**과부하 자리**
- 오타 수정, import 정리
- dep 버전 업, CSS 두 줄 변경
- 5단계 의식을 매번 치르는 비효율

### 한정 적용 — 이벤트성 트리거
통째 도입 대신 **이벤트성 트리거**로 한정.

| Iron Law | 트리거 이벤트 |
|----------|--------------|
| verification | "완료/끝났/통과/됐어" 단어 발생 시 |
| systematic-debugging | 같은 에러 두 번째 시도부터 |
| receiving-review | 리뷰·피드백 응답 시 |

이렇게 두면 trivial 작업·기본 응답과 충돌 없이 작동.

### Iron Law를 hook으로 승격할 때
- Skill 수준에서 무시되는 빈도가 높다 → hook으로 결정론적 차단
- 예: "응답에 '완료/통과' 단어 있는데 직전 턴에 Bash/Read 실행 없으면 차단"
- 우선 Skill로 시작 → UX 부담 보고 판단

### CLAUDE.md "Default to discussion"과의 정합
- Iron Law는 명령형 작업 시에만 작동해야 함
- 토론·질문 컨텍스트에서 발동되면 사용자 의도와 충돌
- SKIP 키워드("자세히/왜 그런지/근거/설계")가 정합 보장

## 관련 자료
- [[skill-description-tuning]] — 트리거 정밀화
- [[components/hooks]] — Skill을 hook으로 승격
- [[anti-patterns/rule-over-enforcement]] — Iron Law 통째 적용의 위험
- [[../05-decision-trees/stop-hook-promotion-criteria]] — hook 승격 판단

## 출처
- **외부 (커뮤니티 관행, Anthropic 공식 아님)**:
  - obra/superpowers — https://github.com/obra/superpowers — Iron Law 표현·"NO X WITHOUT Y" SKILL 본문 다수
  - obra/superpowers-skills — https://github.com/obra/superpowers-skills
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html` (섹션 3.3, 6, 7.1)
