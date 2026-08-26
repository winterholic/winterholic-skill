# 재작성 vs 리팩터링 판단·strangler·실증·체크리스트

## 재작성 vs 점진 리팩터링 판단표

| 조건 | 가리키는 쪽 |
|---|---|
| 코드가 작동하고 있고 사용자가 있다 | 리팩터링 (Netscape 교훈) |
| 불만이 가독성·변경 비용 | 리팩터링 — 그게 정의상 리팩터링이 푸는 문제 |
| 플랫폼 자체가 수명 종료(미지원 언어·런타임) | 재작성 후보 |
| 규모가 작고(수천 줄↓) 명세가 코드 밖에 존재(테스트·문서) | 재작성 비용이 감당 가능 |
| 불만이 도메인 모델 자체(처음부터 잘못 나눔) | 부분 재설계 — strangler로 |
| "내가 안 짠 코드라 싫다" | 어느 쪽도 아님 — 코드 읽기(dev-legacy-code) |

재작성을 택해도 **빅뱅 전환은 금지** — 아래 strangler가 유일한 안전 경로.

## Strangler Fig 경로 (점진 대체)

1. 새 구현을 **옆에** 만든다(기존 무중단).
2. 트래픽/데이터의 일부를 새 쪽으로(라우팅·이중 기록) — sample-service 수집기라면: 새 파이프라인이 같은 기간을 병행 수집 → 결과 대조(dev-data-engineering 적재 검증으로 기계 비교).
3. 대조 통과 범위를 늘리며 옛 경로 축소.
4. 옛 코드 제거는 마지막 — 제거가 첫 단계인 계획은 strangler가 아니라 빅뱅이다.

## 실증·출처

- **Joel Spolsky, "Things You Should Never Do, Part I" (2000-04-06)** — Netscape 전면 재작성 분석. SKILL.md 실전 케이스 원 출처. (1차 원문: https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/ — 저자 본인 블로그, 웹 확인됨)
- **Fowler, *Refactoring* 2판 (2018)** — 냄새 카탈로그·기법 절차·"두 모자"(Kent Beck 인용)의 원전. 온라인 색인: https://refactoring.com/catalog/ (저자 공식 카탈로그, "to support my book Refactoring 2nd Edition" 명시 — 웹 확인됨. Extract/Inline/Move Function·Split Phase 등 본 스킬 인용 기법명 일치).
- **Sandi Metz, "The Wrong Abstraction" (2016-01-20)** — "duplication is far cheaper than the wrong abstraction"(원래 RailsConf 2014 발표에서 나온 표현을 글로 정리). 안티패턴 5(3의 규칙)의 근거. (1차 원문: https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction — 저자 본인 블로그, 웹 확인됨)
- **3의 규칙(Rule of Three)** — Fowler가 Don Roberts에게 귀속한 규칙("세 번째에 리팩터링한다"), 안티패턴 5의 직접 출처. *Refactoring* 2판 수록(웹 확인됨).
- **Fowler, "StranglerFigApplication" (2004, martinfowler.com)** — 점진 대체 패턴 원전. 1차 원문: https://martinfowler.com/bliki/StranglerFigApplication.html (저자 bliki, 웹 확인됨).
- 오픈소스 차용 표기: 리팩터링 보조류 스킬 다수(색인 인지, 본문 비복사). **역흡수**: 재작성 판단표·테스트 부재 시 legacy-code 강제 위임·냄새의 정량 보조(advisory 스캐너) 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (리팩터링 PR/커밋)

- [ ] 손대기 전 테스트 green 확인 (없으면 legacy-code 경유 흔적)
- [ ] 커밋마다 변환 1종, 테스트 파일 diff 0
- [ ] 기능 변경 커밋과 분리 (제목 refactor: 접두)
- [ ] 냄새·동기가 PR 설명에 1줄 (취향 아님 증명)
- [ ] 이름 변경분: 동적 접근 grep 수행 (Python/JS)
- [ ] 통합한 중복: 3회째였나, 옵션 플래그가 생기지 않았나
- [ ] 전후 테스트 결과 동일 (개수·green)
- [ ] 보류한 냄새가 기록됨 (범위 절제의 증거)

## 점검 주기 (부패 느림 — 연 1회)

- ledger에서 "리팩터링 중 깨뜨림" 패턴 3회 → 해당 기법의 함정 절 보강
