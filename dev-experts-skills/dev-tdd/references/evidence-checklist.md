# evidence + 출고 전 체크리스트

> 실증·정직한 한계의 본문은 `evidence-and-limits.md`. 이 파일은 출처 요약 + 출고 체크 + 점검 주기(gold-standard 3절 형식).

## 실증·출처

- **Kent Beck, *Test-Driven Development: By Example* (2002)** — 가짜 구현·삼각측량(triangulation)·명백한 구현 3전략, TODO 리스트, Money 예제의 원전. 안티패턴 1~6의 뿌리.
- **Kent Beck "Canon TDD" (tidyfirst.substack.com, 2023-12)** — 저자 본인이 "정전(canon) TDD"의 5단계(리스트 → 1개 테스트 → 통과 → 정리 → 반복)를 재정리하고, 흔한 변질(리스트 생략·red 생략·통째 구현)을 직접 지목. 워크플로우 5단계와 안티패턴 2·3의 1차 권위 출처(2026 현재 TDD 정의 논쟁의 기준점).
- **Nagappan et al. (2008)** "Realizing quality improvement through test driven development" (Empirical Software Engineering, MS·IBM 4팀) — 출하 전 결함 밀도 40~90% 감소, 초기 개발 시간 15~35% 증가(확인 필요: 팀별 수치 원문 재대조). "공짜가 아니라 트레이드오프"의 표준 출처.
- **Bookout v. Toyota / Michael Barr (2013)** — ETCS 코드의 전역 변수 남용·단위 테스트 부재·복잡도 증언(공개 슬라이드 + EETimes 보도). SKILL.md 실전 케이스 출처. "테스트 가능성은 만들 때 결정된다"의 실증.
- 메타 연구 주의: TDD 효과 연구는 효과 크기가 들쭉날쭉(과제 크기·숙련도 교란) — "항상 우월"은 연구가 지지하지 않는다. 일관 신호는 결함 감소·초기 비용·커버리지 자연 상승.
- 도구는 dev-testing을 따른다(pytest 9.x, 2026) — TDD 자체는 도구 무관 방법론이라 부패가 느리다.

## 출고 전 체크리스트 (TDD 작업 단위)

- [ ] 모든 신규 테스트가 red를 거쳤다 (처음부터 green이었던 테스트 0)
- [ ] 사이클당 행동 1개 — 한 커밋에 테스트 3개+ 동시 추가 없음
- [ ] 마지막 상태가 green (red 상태로 중단·핸드오프 금지, 불가피하면 WIP 명시)
- [ ] refactor 커밋에 행동 변경 없음 (green→green)
- [ ] 하드코딩 잔재 없음 (삼각측량 완료) 또는 TODO에 명시
- [ ] TODO 리스트를 먼저 썼다 (Canon TDD 1단계 — 생략이 흔한 변질)
- [ ] 적합도 ✕ 영역(UI 픽셀·일회성 스크립트)을 TDD로 강제하지 않았다
- [ ] 기대값 불명 항목은 추측 RED 대신 `skip`/보류 + "확인 필요"

## 점검 주기 (부패 느림 — 연 1회)

- 방법론 본체는 거의 불변 — Beck의 Canon TDD(2023)가 현재 기준선이며 더 새 정의 논쟁이 나오면 그때 갱신.
- 도구 명령(러너·커버리지)은 dev-testing의 점검 주기에 위임 — 현재 pytest 9.x.
- ledger에서 "보폭 과대로 막힌" 사이클 3회 패턴 → 스텝 분할 휴리스틱 보강.
