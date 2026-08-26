# evidence + 출고 전 체크리스트

> 실증 사례 본문은 `evidence.md`. 이 파일은 출처 요약 + 출고 체크 + 점검 주기(gold-standard 3절 형식).

## 실증·출처

- **Diátaxis 프레임워크** (diataxis.fr, Daniele Procida — 2026 현재 활성 유지) — 문서를 독자 필요에 따라 tutorial(학습)·how-to(과업)·reference(정보)·explanation(이해) 4분면으로 나누는 표준. Django·Cloudflare·Gatsby 등 다수 프로젝트 공식 채택. "이 문서는 4분면 중 무엇인가"가 구조 결정의 1차 기준.
- **Google Technical Writing 코스** (developers.google.com/tech-writing, 무료 공개) — 역피라미드(결론 먼저)·능동태·짧은 문장·용어 일관성의 표준 출처. 기술 문서의 스타일 기준선.
- **ADR (Architecture Decision Record)** — Michael Nygard "Documenting Architecture Decisions" (2011) 원전. 결정문이 아니라 **맥락문**(당시 제약 X에서 A 선택, B는 ~때문에 기각)이라는 SKILL.md 운용 요체의 출처.
- **역피라미드** — 저널리즘(결론→핵심→상세)의 기술 문서 이식. 검색 진입·스캔 독서 전제에서 "첫 화면에 답이 없으면 이탈"의 근거.
- **Getting Started 부패** — 생태계 반복 실증(이슈 트래커 "docs outdated" 라벨·SO "공식 문서 말고 이렇게" 답변). 코드와 달리 CI가 없어 깨져도 알림이 없다는 비용 구조가 "릴리즈 체크리스트에 실수행 1회" 방어의 근거.
- 출처 종합: 구글 Technical Writing · Diátaxis · ADR 원전 · 오픈소스 문서 운영 관행 집적. 2026-06 기준 모두 활성·안정.

## 출고 전 체크리스트 (기술 문서 출고 시)

- [ ] 이 문서의 Diátaxis 유형이 하나로 정해졌다 (tutorial/how-to/reference/explanation 혼재 아님)
- [ ] 첫 문단만 남겨도 독자가 핵심 행동을 할 수 있다 (역피라미드 — 결론이 뒤에 묻히지 않음)
- [ ] Getting Started/설치 명령을 깨끗한 환경에서 실제로 1회 수행했다 (복붙 가능)
- [ ] 변하는 값(버전·엔드포인트·키)이 단일 출처에 있고 나머지는 참조
- [ ] 코드 예제가 실행 검증됨 (doctest/mdbook test류 또는 수동 1회)
- [ ] 능동태·짧은 문장 — 한 문장 한 개념, 모호 대명사("이것/그것") 점검
- [ ] 아키텍처 결정이면 ADR 1장(맥락/대안/결정/트레이드오프 반 페이지) 동반
- [ ] 6개월 뒤·신규 입사자 독자 기준으로 전제 지식이 명시됨
- [ ] 독자 신고 채널(Edit 링크·피드백)이 있다

## 점검 주기 (부패 보통 — 반기, 단 Getting Started는 릴리즈마다)

- **Getting Started·설치·CLI 예제**: 의존 버전/명령이 바뀌는 릴리즈마다 재수행 — 부패가 가장 빠른 자산(첫인상). 릴리즈 체크리스트에 항목으로 고정.
- Diátaxis·Google Tech Writing·ADR 원전은 안정(연 1회 변화 확인이면 충분) — 프레임워크 자체는 2026 현재 변동 없음.
- ledger에서 "문서대로 했는데 실패" 신고 3회 패턴 → 해당 경로를 자동 검증 대상으로 승격.
