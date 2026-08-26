# biz-prd-writing — 템플릿 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 웹 검증. 1단계 참조.

## 1. PRD 템플릿 (적정 해상도)
문제/배경 → 목표(성공 지표+측정+확인 시점) → 비목표(Non-goals) → 사용자·시나리오 → 해법 개요(상세 UI는 디자인으로 위임) → 유저스토리+수용기준 → 의존성/리스크/열린 질문 → 출시·측정 계획.

## 2. 아마존 PR/FAQ (Working Backwards)
- PR(보도자료): 출시됐다 가정, 고객 관점 1페이지. 못 쓰면 만들지 마라.
- FAQ: 고객 FAQ + 내부 FAQ(왜 우리·리스크·기술 난제).
- 회의는 6페이지 산문 문서 침묵 독서로 시작(불릿 PPT 금지).
> 반복 강도(검증): Working Backwards 공식 자료가 "PR/FAQ를 **10번 이상** 고쳐 쓰고 시니어 리더와 **5회 이상** 만나 다듬는 일이 드물지 않다"고 명시. 단 첫 초안은 며칠이 아니라 **몇 시간** 안에 — 빠른 옵션 탐색이 목적. (출처: workingbackwards.com PR/FAQ 프로세스.)

## 3. Shape Up (Basecamp, 무료 공개)
appetite(쓸 의향 시간)로 범위 고정 → shaped work → betting table → 6주 사이클 + 2주 cooldown. **circuit breaker 교정**: 사이클 안에 못 끝내면 기본적으로 **연장이 아니라 취소(cancel)** 된다(흔히 반대로 오해).

## 4. 유저스토리 & 수용기준 (출처·계보 교정)
- 스토리 템플릿 "As a [role], I want [goal], so that [benefit]" = **Connextra 포맷**(런던 XP팀 ~2001). **Mike Cohn이 발명한 게 아니라** *User Stories Applied*(2004)로 대중화.
- INVEST = Independent·Negotiable·Valuable·Estimable·Small·Testable — **Bill Wake, 2003-08-17** ("INVEST in Good Stories, and SMART Tasks"). https://xp123.com/invest-in-good-stories-and-smart-tasks/
- 수용기준 Given-When-Then(Gherkin): **Chris Matts & Dan North (~2004)** 공동, North가 2006 글로 공개. Cucumber가 표준화. North 단독 귀속 금지.

## 4b. 실전 템플릿 (→ `prd-templates.md`)
PRD 8섹션 복사용 템플릿·PR/FAQ 7블록 보도자료 양식·GWT 수용기준 예시집(안티패턴 vs 검증가능)·Shape Up pitch·완성 PRD 예시(결제 재시도)는 별도 파일로 분리.
- **PR/FAQ 7블록**: Heading·Subheading·Summary·Problem·Solution·Quotes·Getting Started. 첫 초안은 몇 시간, 이후 10회+ 개정·5회+ 시니어 리뷰. "이 한 페이지 못 쓰면 만들 가치 없다."
- **GWT 검증가능성**: 입력상황·동작·결과가 모두 구체·관찰가능해야 QA가 통과 판정. 정상 경로만이 아니라 거절/타임아웃/중복 등 부정 경로도 별도 GWT.
- **circuit breaker = 취소**: Shape Up 사이클 안에 못 끝내면 기본은 연장이 아니라 취소.

## 5. 출처 (검증)
- Colin Bryar & Bill Carr, *Working Backwards* (St. Martin's Press, 2021). https://workingbackwards.com/ · PR/FAQ 프로세스 https://workingbackwards.com/concepts/working-backwards-pr-faq-process/
- Ryan Singer, *Shape Up* (Basecamp, 2019, 무료 전문). https://basecamp.com/shapeup
- Mike Cohn, *User Stories Applied* (Addison-Wesley, 2004). https://www.mountaingoatsoftware.com/
- Dan North, "Introducing BDD" (2006-03). https://dannorth.net/blog/introducing-bdd/ · Gherkin 공식 https://cucumber.io/docs/gherkin/reference/ · BDD 역사 https://cucumber.io/docs/bdd/history/
- Bill Wake, INVEST (2003). https://xp123.com/invest-in-good-stories-and-smart-tasks/
