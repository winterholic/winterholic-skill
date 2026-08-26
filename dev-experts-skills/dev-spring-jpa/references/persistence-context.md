# 영속성 컨텍스트 생명주기·쿼리 카운트 테스트·DTO 직접 조회 (SKILL.md 비중복)

## 컨텍스트 생명주기와 4대 동작

```
트랜잭션 시작 -> 컨텍스트 열림 (보통 트랜잭션 = 컨텍스트 수명)
├─ em.find/JPQL -> 1차 캐시 확인 -> 없으면 SELECT 후 장부 등록 (스냅숏 보관)
│    같은 id 재조회 = 캐시 적중 = SQL 없음 ("쿼리가 안 나가요"의 정체)
├─ 엔티티 필드 변경 -> 장부에만 기록 (SQL 아직 없음)
├─ flush (커밋 직전 / JPQL 실행 직전 자동) -> 스냅숏 대비 변경분 UPDATE 발행
└─ 커밋 -> 컨텍스트 종료 -> 모든 엔티티 준영속(detached)
       └─ 이후 LAZY 접근 = LazyInitializationException
```

- **JPQL은 1차 캐시를 우회해 DB로 직행**한다(단 결과 등록 시 이미 장부에 있는 id는 장부 것 유지) — "방금 바꿨는데 JPQL엔 반영"이 flush-before-query 덕분이고, 벌크 연산은 그 반대로 장부를 모른 채 DB만 바꾼다(clearAutomatically 필요 이유).
- 준영속 엔티티의 변경은 아무 일도 안 일으킨다 — "save 했는데 안 바뀌어요"는 보통 merge 의미론 혼동: Spring Data `save()`는 id 존재 시 merge(SELECT 후 복사)다 — 변경은 영속 상태에서 의도 메서드로 하는 것이 정도.

## 쿼리 카운트 단언 구현 (N+1 예방의 기계화)

```java
// Hibernate Statistics 활용 - 테스트 전용 설정에서
// spring.jpa.properties.hibernate.generate_statistics=true
@Autowired EntityManagerFactory emf;

long queryCount() {
    return emf.unwrap(SessionFactory.class).getStatistics().getPrepareStatementCount();
}

@Test void order_list_is_one_query() {
    var before = queryCount();
    orderService.getOrderList(PageRequest.of(0, 20));
    assertThat(queryCount() - before).isLessThanOrEqualTo(2);  // 본문 1 + count 1
}
```

핵심 조회 메서드마다 이 단언 1개 — 연관 추가·리팩터링이 N+1을 다시 들여오는 회귀를 컴파일 다음으로 싸게 잡는다(dev-testing "버그 났던 곳" 휴리스틱의 JPA판).

## DTO 직접 조회 (Projection) — 엔티티 우회가 정답인 곳

```java
// 화면 전용 조회: 엔티티 그래프가 아니라 필요한 컬럼만
@Query("""
    select new com.app.dto.OrderRow(o.id, m.name, size(o.items))
    from Order o join o.member m
    """)
Page<OrderRow> findOrderRows(Pageable pageable);
```

- 읽기 전용 화면은 DTO 직접 조회가 [N+1 원천 차단 + 영속성 컨텍스트 비용 0 + 필요한 컬럼만] 3승 — 변경이 필요한 조회만 엔티티로.
- 기준: **변경하려고 읽으면 엔티티, 보여주려고 읽으면 DTO** — CQRS-lite(dev-ddd 전술 사전)와 같은 결.
- 인터페이스 프로젝션(getter만 선언)은 간단하지만 중첩·계산에 약함 — record 생성자 프로젝션이 기본값.

## 연관관계 편의 메서드 표준형 (양방향을 쓰기로 했다면)

```java
// Order(주인 아님, mappedBy) <-> OrderItem(주인, FK 보유)
public void addItem(OrderItem item) {
    items.add(item);        // 객체 그래프
    item.setOrder(this);    // FK 반영되는 쪽 (주인) - 이게 빠지면 DB에 안 들어감
}
```

한쪽에만 두고(보통 부모), 생성자/팩토리에서만 호출되게 — 산발 호출은 동기화 누락의 원천.

## flush 타이밍이 무는 함정 모음

- JPQL 직전 자동 flush → "조회했더니 UPDATE가 나갔어요"(정상 — 장부 정리).
- ID 전략 IDENTITY는 persist 즉시 INSERT(id가 필요해서) → 쓰기 지연·batch 무효(안티패턴 6과 연결) — 대량 삽입 설계 시 SEQUENCE 고려.
- `saveAndFlush`는 디버깅·제약 위반 조기 확인용 — 상습 사용은 쓰기 지연 이점 포기.
