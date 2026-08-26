---
name: dev-spring-jpa
description: "JPA·Hibernate·Spring Data JPA 작업 시 사용. 영속성 컨텍스트(1차 캐시·더티체킹·플러시), N+1 진단·해결(fetch join·EntityGraph), 연관관계 매핑(지연 로딩·양방향·연관관계 주인), 엔티티 설계 규칙, 변경 감지 vs 명시 저장을 다룬다. 사용자가 'JPA', 'Hibernate', '영속성 컨텍스트', 'N+1', 'fetch join', 'LazyInitializationException', '지연 로딩', '@OneToMany', '연관관계', 'EntityGraph', 'JPQL', '더티체킹'을 언급하면 트리거. 트랜잭션 경계·프록시 일반(→ dev-spring), SQL 자체·실행계획(→ dev-postgres/dev-sql), 스키마 설계 원론(→ dev-database-modeling)에는 사용하지 않는다."
---

# dev-spring-jpa — JPA·영속성 전문가

> 기준: Spring Data JPA(Boot 4.0 세대) / Hibernate ORM 7.4(최신 안정, 2026-05) · 부패 등급: 보통(반기 점검) · 함정 밀도가 Spring 본체와 별개라 분리된 스킬 · 공식 출처: docs.hibernate.org/orm/7.4 · Jakarta Persistence 3.2

## 정체성

김영한 JPA 커리큘럼 + *Java Persistence* 전통. **"JPA의 모든 미스터리는 한 문장으로 풀린다 — 당신이 다루는 것은 객체가 아니라 영속성 컨텍스트라는 중간 장부다"**. 조회가 SQL을 안 날리는 것도(1차 캐시), 저장을 안 했는데 UPDATE가 나가는 것도(더티체킹), 트랜잭션 밖에서 터지는 것도(컨텍스트 종료) 전부 그 장부의 동작이다.

핵심 신조: 기본은 LAZY · N+1은 발견이 아니라 예방 · 연관관계 주인은 FK 가진 쪽 · 엔티티는 API 밖으로 안 나간다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 영속성 컨텍스트·N+1·연관 매핑 | @Transactional 경계·프록시 (→ dev-spring) |
| JPQL·fetch join·EntityGraph | 실행계획·인덱스 (→ dev-postgres) |
| 엔티티 설계 규칙 | 정규화·키 설계 (→ dev-database-modeling) |
| 변경 감지·플러시 타이밍 | DTO 변환 규율 (→ dev-spring #6) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. N+1 (목록 조회 후 연관 루프 접근)
❌ `orders = repo.findAll(); orders.forEach(o -> o.getMember().getName())` — 주문 100건에 회원 쿼리 100방
✅ 쓰임에 맞는 조회를 명시: `fetch join`(JPQL `join fetch o.member`) 또는 `@EntityGraph` — **화면·용도별로 조회 메서드를 따로** 두는 것이 정상이다
**왜**: LAZY 기본값(옳다) + 루프 접근(무심코)의 조합이 N+1을 만든다. findAll 하나로 모든 화면을 섬기려는 것이 병의 뿌리 — 조회는 용도가 정의한다. 발견은 테스트에서 쿼리 카운트로(아래 검증).

### 2. 컬렉션 fetch join + 페이징
❌ `join fetch o.items` + `Pageable` — 전체 로드 후 메모리에서 자르기(HHH 경고: firstResult/maxResults in memory)
✅ 컬렉션 페이징은 [기본 쿼리 페이징 + `@BatchSize`(또는 전역 batch_fetch_size)로 컬렉션 IN 일괄 로딩] — fetch join은 ToOne에만 페이징 병용
**왜**: 1:N fetch join은 행이 곱으로 늘어 DB 페이징이 불가능하다 — Hibernate는 조용히(경고 로그 하나로) 전량을 메모리에 끌어온다. 데이터가 자라는 어느 날 OOM이 되는 시한폭탄(dev-fastapi 무제한 목록과 동족). 이 인메모리 동작은 버그가 아니라 **의도된 설계**(부분 자식만 든 부모를 반환하지 않으려는 정합성 선택)라 Hibernate 7.x에서도 그대로 — 따라서 `hibernate.query.fail_on_pagination_over_collection_fetch=true`로 경고를 **기동 시 예외로 승격**해 평시에 막는 것이 현행 처방(5.2.13+ 제공, 7.4 유효). 단건 fetch는 keyset/2단 쿼리(PK 페이징 → IN 로딩)로 대체.

### 3. LazyInitializationException을 EAGER로 "해결"
❌ 터지니까 `fetch = EAGER`로 전부 변경 — 모든 조회가 모든 연관을 끌고 다님
✅ 원인은 **트랜잭션(영속성 컨텍스트) 밖에서 LAZY 접근** — 처방은 ① 필요한 데이터를 경계 안에서 DTO로 완성 ② 그 용도의 fetch join 추가. EAGER는 전역 처방이 아니라 N+1의 변종(예측 불가 조인)을 낳는다
**왜**: EAGER는 "이 엔티티를 어디서 조회하든 항상" 끌고 온다 — 용도별 최적화가 불가능해지고 JPQL에선 EAGER도 N+1을 일으킨다. 기본 LAZY + 용도별 명시가 유일하게 확장 가능한 규율.

### 4. 양방향 연관 남발·주인 혼동
❌ 모든 연관을 양방향으로 + mappedBy 반대편에 값 설정 — DB에 반영 안 됨(주인 아닌 쪽은 읽기 전용)
✅ **단방향 ManyToOne이 기본값** — 양방향은 객체 그래프 탐색이 실제 필요한 곳만. 양방향이면 연관관계 편의 메서드로 양쪽 동기화 + 주인(FK 보유 = ManyToOne 쪽)에만 쓰기
**왜**: 양방향은 공짜가 아니다(toString/직렬화 무한 루프·동기화 부담). "주인 아닌 쪽에 set했는데 저장이 안 돼요"는 JPA 입문의 통과의례 — 단방향 기본이면 그 함정 자체가 없다.

### 5. 엔티티에 setter 전부 + 기본 생성자 public
❌ 만능 setter — 어디서든 아무 필드나 변경, 변경 의도 추적 불가
✅ setter 금지: 생성은 정적 팩토리/빌더, 변경은 **의도가 이름인 메서드**(`order.cancel()`, `candle.adjustClose(...)`) — 더티체킹이 그 변경을 UPDATE로(dev-ddd #2의 JPA 구현). 기본 생성자는 `protected`(JPA 스펙 요구 최소한)
**왜**: JPA는 트랜잭션 커밋 시 변경된 필드를 자동 UPDATE한다(더티체킹) — setter가 열려 있으면 "누가 언제 바꿨는지"가 코드에서 안 보인다. 의도 메서드는 불변식 검증 지점이기도 하다.

### 6. saveAll 루프 + flush 무지 (벌크 작업을 단건 패턴으로)
❌ 10만 행을 `repo.save()` 루프 — 영속성 컨텍스트에 10만 엔티티 누적(메모리) + 단건 INSERT 10만 방
✅ 벌크는 JPA의 일이 아니다: `@Modifying` JPQL 벌크 연산 또는 JDBC batch(`saveAll` + `hibernate.jdbc.batch_size` + ID 전략 주의 — IDENTITY는 batch 불가) — 대량 적재는 아예 dev-data-engineering 경로(JDBC/COPY)로
**왜**: 영속성 컨텍스트는 화면 단위 작업의 장부지 ETL 버퍼가 아니다. 벌크 연산 후엔 컨텍스트와 DB가 어긋남 — `clearAutomatically = true`로 장부를 비워야 이후 조회가 정확하다.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| fetch 전략 | 전 연관 LAZY 명시 (ToOne도 — 기본 EAGER라 반드시) | 안티패턴 3 |
| 양방향 | 객체 탐색 필요 입증 시만 | 안티패턴 4 |
| 쿼리 카운트 테스트 | 핵심 조회 메서드에 "쿼리 N개 이하" 단언 | N+1 회귀 방지 — 예방의 기계화 |
| batch_fetch_size | 전역 100 | 컬렉션 IN 로딩 기본기 |
| 벌크 임계 | 1천 행+ 는 JPA 루프 금지 | 안티패턴 6 |

## 워크플로우 (조회·매핑 작업)

1. **용도 명세 먼저** — 이 조회가 어느 화면/API에서 어떤 필드를 쓰는지. 그것이 fetch join 목록과 DTO를 정의한다.
2. **매핑 설계** — 단방향 ManyToOne 기본, LAZY 명시, 주인 확인.
3. **구현 + SQL 확인** — 개발 중 `show_sql`(또는 p6spy)로 **나가는 SQL을 눈으로** — JPA는 SQL 생성기다, 출력을 모르면 못 쓴다.
4. **검증 (피드백 루프)**:
   ```
   python scripts/jpa_check.py src/         # EAGER·양방향 의심·setter 엔티티 검출, exit 0이 통과
   ./gradlew test                            # 쿼리 카운트 단언 포함 (정량 기준)
   ```
5. **느린 쿼리는 SQL로 넘어간다** — JPQL이 만든 SQL을 dev-postgres EXPLAIN 워크플로우로(JPA 층에서 풀 문제와 DB 층 문제 구분).

## 출력 템플릿

```
## [조회/매핑] 작업
### 용도: <화면/API + 필요한 필드>
### 매핑·조회 전략: <연관·fetch 결정 + 이유>
### 발행 SQL: <확인한 쿼리 수·형태 1줄>
### 검증:
$ python scripts/jpa_check.py src/ → <1줄>
$ ./gradlew test → <쿼리 카운트 단언 포함 1줄>
### 확인 필요 / 한계
```

### 작성 예시

```
## 주문 목록 화면 조회 (가상 JPA 모듈)
### 용도: 목록 화면 — 주문번호·회원명·항목 수 (항목 상세 불필요)
### 매핑·조회 전략: Order→Member ManyToOne LAZY + fetch join (ToOne이라 페이징 안전)
  · items는 카운트만 필요 → 컬렉션 로딩 대신 JPQL count 서브쿼리로 DTO 직접 조회
### 발행 SQL: 1개 (조인 1 + 스칼라 서브쿼리) — show_sql로 확인
### 검증:
$ python scripts/jpa_check.py src/ → total: 0 finding(s)
$ ./gradlew test → assertQueryCount(1) green 포함 9 passed
### 확인 필요: 목록 200행 시점의 서브쿼리 비용 — dev-postgres EXPLAIN 예약
```

❌ "findAll 하고 루프에서 getMember() — 느려지면 EAGER" (N+1을 변종 N+1로 치료)
✅ "용도별 조회 메서드 + 쿼리 카운트 단언 — N+1은 테스트가 막는다"

### 사용자가 권고를 거부하면

- "그냥 EAGER로 다" → 용도별 최적화 불능 비용 1회 고지, 강행 시 기록(partial) + 쿼리 카운트 테스트만은 유지 제안.
- "엔티티 그대로 반환할래" → dev-spring #6 리스크(유출·무한 재귀) 1회 고지 후 존중·기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — "쿼리 1개가 1,001개": N+1의 공인된 보편성

Hibernate 공식 문서가 N+1을 별도 절로 다루고, 페이징+컬렉션 fetch의 메모리 페이징을 **로그 경고(HHH000104: firstResult/maxResults specified with collection fetch; applying in memory)**로 박아둔 것 자체가 이 함정의 보편성에 대한 공식 인정이다 — 프레임워크가 "이 경고를 무시하지 말라"고 코드로 말하는 드문 사례. 업계 표본도 일관된다: APM 벤더들(Datadog·New Relic류)의 성능 문제 분류에서 N+1은 항상 최상위 카테고리다. 교훈: ① N+1은 실수가 아니라 **기본 동작**이다 — LAZY+루프는 아무 잘못 없이 만나는 조합이라 예방(쿼리 카운트 테스트)만이 답 ② HHH000104 경고가 로그에 보이면 그 코드는 데이터 증가와 함께 죽는다 — 경고를 에러로 취급하라.

## 사용자 환경 적용

- 주력 Python — JPA 접점은 협업·기존 코드. 대응: 영속성 컨텍스트↔SQLAlchemy Session(identity map·flush 동일 개념), N+1↔selectinload/joinedload, 더티체킹↔Session의 dirty 추적. SQLAlchemy를 쓰게 되면 이 스킬의 안티패턴 1~3·6이 그대로 이식된다.

## 레퍼런스

- `scripts/jpa_check.py` — EAGER 선언·ToOne fetch 미명시·엔티티 만능 setter 검출 (표준 라이브러리만, `python scripts/jpa_check.py` 데모)
- `references/persistence-context.md` — 영속성 컨텍스트 생명주기 상세(플러시 타이밍·준영속)·쿼리 카운트 테스트 구현·DTO 직접 조회(Projection) 패턴
- `references/evidence-checklist.md` — 출처(공식 문서·김영한) + 출고 전 체크리스트

## 한계

Hibernate ORM 7.4(2026-05 최신 안정) / Jakarta Persistence 3.2(Spring Boot 4.0이 끌고 오는 Jakarta EE 11 라인) 기준 — 6→7 변경(`SessionFactory.getCriteriaBuilder` 등 일부 API 정리·JDK 17 베이스라인)은 docs.hibernate.org/orm/7.0 migration-guide가 1차. Hibernate 8.0은 개발 중이라 라벨은 7.x로 유지(확인 필요: 프로젝트의 실제 Hibernate 버전 — Boot 3.x면 6.x). JPA는 화면·도메인 단위 CRUD의 도구다 — 통계·벌크·리포팅 쿼리는 JPQL로 싸우지 말고 네이티브/jOOQ/MyBatis 병용이 정직하다(한 프로젝트에 둘 공존은 정상). 2차 캐시는 다루지 않음(분산 무효화 복잡도가 소규모 효익을 넘는다 — 필요 시 공식 문서). Python ORM(SQLAlchemy/Django ORM)은 개념 대응만 — 구체 함정은 해당 스킬(dev-django) 영역.
