# 현대 Java — record/sealed/패턴 매칭/가상 스레드·8→25 대응표 (SKILL.md 비중복)

## 8→25 관용구 대응표 (옛 코드를 읽고 새 코드를 쓰기)

| Java 8 시절 | Java 21~25 |
|---|---|
| POJO + getter/equals 수동 | `record` |
| 타입별 instanceof + 캐스팅 체인 | `sealed` + 패턴 매칭 `switch (e) { case Tick t -> ...; case Halt h -> ... }` (default 없이 완전성 검사) |
| 익명 클래스 콜백 | 람다·메서드 참조 (8부터지만 여전히 혼재) |
| `new Thread()`/풀 튜닝 (I/O) | 가상 스레드 executor |
| null 체크 사다리 | `Optional` 반환 + `Objects.requireNonNull(x, "msg")` 진입 검증 |
| 문자열 연결 SQL/JSON | 텍스트 블록 `"""` |
| 명시 타입 장황 선언 | `var` (지역, 우변이 자명할 때만 — 가독성 우선) |
| 외부 라이브러리 HTTP | `java.net.http.HttpClient` (11+, 타임아웃 명시 의무는 동일) |

## record 심화

```java
record Candle(String code, LocalDate day, long close) {
    Candle {                                  // compact constructor - 검증 지점
        Objects.requireNonNull(code);
        if (close < 0) throw new IllegalArgumentException("close < 0: " + close);
    }
    long won() { return close; }              // 파생 메서드 자유
}
```

- 검증은 compact constructor에 — 생성 즉시 불변+유효(dev-ddd 값 객체의 Java 구현).
- 컬렉션 필드는 생성자에서 `List.copyOf(items)` — record여도 참조 필드의 가변성은 직접 막아야 한다.
- JPA 엔티티로는 못 쓴다(기본 생성자·프록시 요구) — DTO·도메인 값에 쓰고 엔티티는 dev-spring-jpa 규칙.

## sealed + 패턴 매칭 표준형

```java
sealed interface MarketEvent permits Tick, Halt, Resume {}

String describe(MarketEvent e) {
    return switch (e) {
        case Tick t -> "tick " + t.code();
        case Halt h -> "halted " + h.code();
        case Resume r -> "resumed " + r.code();
    };  // 새 변형 추가 -> 여기 컴파일 에러 = 처리 누락 불가능
}
```

default를 넣는 순간 완전성 검사가 꺼진다 — 정말 "나머지 전부 동일 처리"일 때만.

## 가상 스레드 사용 규칙 (21+)

```java
try (var ex = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<Quote>> fs = codes.stream().map(c -> ex.submit(() -> fetch(c))).toList();
    ...
}
```

- **풀링하지 않는다** — 가상 스레드는 1작업 1스레드가 설계 의도(만들고 버린다).
- 피닝: `synchronized` 블록 안 블로킹 I/O는 캐리어 스레드를 묶는다 → `ReentrantLock`으로 교체(확인 필요: 25에서 synchronized 피닝 완화 적용 여부 — JEP 491). 진단: `-Djdk.tracePinnedThreads=full`.
- CPU 바운드엔 이득 없음 — 거기는 여전히 플랫폼 풀(코어 수 크기).
- ThreadLocal 남용 코드와 궁합 나쁨(수백만 스레드 × ThreadLocal) — ScopedValue(25 시점 상태 확인 필요)가 후속.

## 스트림 컬렉터 레시피

```java
Map<String, List<Candle>> byCode = candles.stream().collect(groupingBy(Candle::code));
Map<String, Long> lastClose = candles.stream()
    .collect(toMap(Candle::code, Candle::close, (a, b) -> b));   // merge 함수 - 키 중복 IllegalState 방지
double avg = candles.stream().mapToLong(Candle::close).average().orElse(0);
```

- `toMap`은 merge 함수 3번째 인자 습관화 — 중복 키 예외가 운영에서 터지는 단골.
- 스트림 안 검사 예외는 시그니처 지옥 — 그 지점만 루프로 풀거나 언체크 래핑 헬퍼.
