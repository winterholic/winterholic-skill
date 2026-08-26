# evidence + 출고 전 체크리스트

## 실증·출처

- **Evans, *Domain-Driven Design* (2003)** — 유비쿼터스 언어·바운디드 컨텍스트·전략 설계의 원전. "전략 설계를 책 뒤에 두어 아무도 거기까지 못 읽었다 — 앞에 뒀어야 했다"는 회고는 QCon London 2009 강연 "What I've learned about DDD since the book"에서 명시 (요약: https://gojko.net/2009/03/12/qcon-london-2009-eric-evans-what-ive-learned-about-ddd-since-the-book/ — 강연 직후 정리된 1차 노트) — 안티패턴 1의 근거.
- **Vernon, *Implementing DDD* (2013)** — 애그리거트 설계 4규칙(작게·진짜 불변식만·ID 참조·결과적 일관성). 정량 기준(엔티티 1~3)의 출처. 같은 4규칙의 **무료 1차 출처**는 이 책에 앞선 에세이 시리즈 *Effective Aggregate Design*(Vernon, 2011, 3부작): https://www.dddcommunity.org/library/vernon_2011/ (DDD 커뮤니티 공식 라이브러리에서 PDF 직접 호스팅 — 웹 확인됨) — 인용 시 이쪽이 검증·재인용에 유리.
- **NASA, Mars Climate Orbiter Mishap Investigation Board Phase I Report (1999-11-10)** — 단위 혼동 사고의 공식 보고서. 1차 PDF: https://llis.nasa.gov/llis_lib/pdf/1009464main1_0641-mr.pdf (NASA Lessons Learned Information System 호스팅 — 웹 확인됨). 정확한 사실: 근본 원인은 지상 SM_FORCES 소프트웨어가 추력 임펄스를 **파운드힘-초**로 출력하고 궤도 계산은 **뉴턴-초**로 기대(4.45배 오차), 당사자는 NASA/JPL ↔ Lockheed Martin. SKILL.md 본문의 "운동량"은 엄밀히는 임펄스(impulse)·"두 팀"은 두 기관임 — 비유의 골자(같은 데이터가 두 컨텍스트에서 다른 단위)는 정확.
- **Fowler, "AnemicDomainModel" (2003-11-25)** — 빈약한 모델 비판의 표준 출처(안티패턴 2): https://martinfowler.com/bliki/AnemicDomainModel.html (저자 공식 사이트 — 웹 확인됨, Evans 본인과의 대화·DDD 인용 포함). 단 "DTO+함수가 적합한 곳도 있다"는 반론(지원 도메인)도 함께 정직하게.
- 오픈소스 차용 표기: DDD 교육류 자료 다수(색인 인지, 본문 비복사). **역흡수**: 대부분 전술 패턴 강의 중심 — 핵심/지원/일반 배분표·1인용 이벤트 스토밍·용어-코드 일치 기계 검사 부재가 본 스킬 차별점.

## 출고 전 체크리스트 (도메인 모델링 출고 시)

- [ ] 시나리오 문장이 도메인 언어로 존재 (기술 용어 0)
- [ ] 용어집 갱신 + `glossary_check.py` 0건 (코드-언어 일치)
- [ ] 애그리거트마다 지키는 불변식이 한 문장으로 적혀 있다
- [ ] 1트랜잭션 1애그리거트 — 위반 지점은 이벤트로 전환됨
- [ ] 애그리거트 간 객체 참조 없음 (ID 참조)
- [ ] 불변식이 단위 테스트로 박혀 있다
- [ ] 핵심/지원 구분 — 지원 도메인에 전술 패턴 미적용 확인
- [ ] 외부 시스템 접점에 ACL(변환층) 존재
- [ ] 도메인 이벤트가 과거형 이름 + 커밋 후 발행

## 점검 주기 (부패 느림 — 연 1회)

- 용어집 vs 실제 코드 이름 드리프트 재검 (도구 실행)
- ledger의 "경계 잘못 그음" 패턴 3회 → 판별 표 보강
