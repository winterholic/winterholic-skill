# evidence + 출고 전 체크리스트

## 실증·출처

- **Hibernate ORM 7.4 What's New / 공식 문서** (docs.hibernate.org/orm/7.4, 2026-05) — 버전 라벨 + HHH000104(컬렉션 fetch 페이징 인메모리) 경고. 안티패턴 2·실전 케이스의 1차 출처. **확인됨**: 인메모리 페이징은 7.x에서도 의도된 설계이며 "수정"되지 않음 — 처방은 `hibernate.query.fail_on_pagination_over_collection_fetch=true`로 예외 승격(5.2.13+ 제공, Vlad Mihalcea vladmihalcea.com 문서가 표준 해설).
- **김영한, 자바 ORM 표준 JPA 프로그래밍 + 인프런 활용 시리즈** — 영속성 컨텍스트 중심 설명·기본 LAZY·용도별 조회·DTO 직접 조회 규율의 한국어 표준.
- **Jakarta Persistence 3.2** (Jakarta EE 11, Spring Boot 4.0 라인) — ToOne 기본 EAGER / ToMany 기본 LAZY 명세(P3b 검출의 근거), 기본 생성자 요구. 확인 필요: Boot 3.x 프로젝트는 Jakarta Persistence 3.1 + Hibernate 6.x.
- **APM 벤더 성능 분류(Datadog·New Relic 문서들)** — N+1이 상시 최상위 카테고리(확인 필요: 개별 통계 인용 시 원문).
- 오픈소스 차용 표기: JPA 가이드류 다수(색인 인지, 본문 비복사). **역흡수**: 쿼리 카운트 단언의 기계화·"변경이면 엔티티, 표시면 DTO" 단일 기준·SQLAlchemy 개념 대응 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (JPA 코드 출고 시)

- [ ] 전 연관 LAZY 명시 (`jpa_check.py` 0건)
- [ ] 핵심 조회에 쿼리 카운트 단언
- [ ] show_sql/p6spy로 발행 SQL 눈 확인 (개발 중)
- [ ] HHH000104 경고 0 (가능하면 `fail_on_pagination_over_collection_fetch=true`로 예외 승격)
- [ ] 엔티티: 만능 setter 없음·protected 기본 생성자·의도 메서드
- [ ] 양방향은 필요 입증 + 편의 메서드 1곳
- [ ] 읽기 전용 화면은 DTO 직접 조회 검토함
- [ ] 벌크(1천 행+)는 JPA 루프 아님
- [ ] 벌크 연산에 clearAutomatically
- [ ] 엔티티가 컨트롤러 밖 비노출 (dev-spring #6)

## 점검 주기 (부패 보통 — 반기)

- Hibernate ORM 마이너/메이저 추적(현 7.4, 8.0 개발 중) — 통계 API·경고 코드·페이징 동작 변경만
- 쿼리 카운트 단언이 여전히 도는지 (통계 설정 유실 방지)
- 프로젝트 Boot 버전 vs 라벨(4.0=Hibernate 7.x / 3.x=6.x) 정합 재확인
