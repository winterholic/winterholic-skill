# 프록시·트랜잭션 심화 — 메커니즘·전파 결정표·롤백 규칙 (SKILL.md 비중복)

## 프록시 메커니즘 (모든 미스터리의 해부도)

```
호출자 ──> [프록시] ──(부가기능: tx 시작/commit/rollback)──> [실제 빈]
                                                              │
                            실제 빈 내부의 this.другой() ────┘  <- 프록시 안 거침!
```

- 인터페이스 있으면 JDK 동적 프록시, 없으면 CGLIB 서브클래싱(부트 기본은 CGLIB 강제) — 그래서 **final 클래스/메서드엔 어드바이스 불가**(서브클래싱 못 함, 조용히 무시되거나 기동 에러).
- 어드바이스가 무시되는 4대 조건: ① this 호출 ② private/final ③ 빈이 아님(new) ④ 프록시 모드 한계 — 진단 순서 그대로.
- @Async·@Cacheable·@Retryable 전부 같은 메커니즘 — @Transactional에서 배운 함정이 전부 재적용된다.

## 전파(propagation) 결정표

| 속성 | 의미 | 쓰는 순간 |
|---|---|---|
| REQUIRED (기본) | 있으면 참여, 없으면 생성 | 95% — 기본 유지 |
| REQUIRES_NEW | 항상 새 트랜잭션(기존 일시 중단) | 본 작업 실패와 무관하게 남겨야 하는 기록(감사 로그·실패 이력) |
| NESTED | 세이브포인트 | 부분 롤백 — JPA에선 제약 많아 드묾 |
| SUPPORTS/NOT_SUPPORTED/NEVER/MANDATORY | 참여 정책 세칙 | 거의 안 씀 — 쓰게 되면 경계 설계 재검토 신호 |

- REQUIRES_NEW 주의: **새 커넥션을 추가로 잡는다** — 외부 트랜잭션이 커넥션을 쥔 채 대기하므로 풀 고갈 데드락 가능(풀 크기 < 동시 중첩 수일 때). dev-postgres 연결 예산에 반영.

## 롤백 규칙 전체

```
기본: RuntimeException·Error → 롤백 / checked Exception → 커밋(!)
조정: @Transactional(rollbackFor = OrderFailedException.class)
함정 1: 트랜잭션 안에서 언체크 예외를 catch로 삼킴
  → 프록시는 이미 rollback-only 마크 → 커밋 시도 시 UnexpectedRollbackException
  → 처방: 잡지 말거나, 잡았으면 그 트랜잭션은 끝났다고 취급(재던지기)
함정 2: REQUIRES_NEW 안의 예외를 바깥에서 잡음 → 안쪽만 롤백, 바깥 진행 - 의도면 OK, 모르면 부분 커밋
```

## @Transactional 위치 규율

- 서비스 계층 메서드에만 — 컨트롤러(웹 관심사 혼입)·리포지토리(경계 너무 작음)는 비권장.
- 테스트의 @Transactional은 다른 물건(롤백 격리 — dev-testing fixture와 동일 목적)이지만 **lazy 로딩이 테스트에서만 성공하는 가짜 통과**를 만들 수 있음 — 운영 경로엔 트랜잭션이 없는데 테스트엔 있어서. 통합 테스트 일부는 트랜잭션 없이.

## 빈 수명·스코프 세칙

- 싱글톤 빈이 prototype 빈을 주입받으면 **한 번만 주입**된다(매번 새 것 아님) — ObjectProvider로 매번 요청.
- @PostConstruct에서 무거운 I/O 금지 — 기동 시간 + 실패 시 전체 기동 실패. 지연 초기화 또는 ApplicationRunner.
- 순환 참조: 생성자 주입이면 기동 즉시 BeanCurrentlyInCreation — **에러가 빨리 나는 게 장점**이다. setter/@Lazy로 우회하지 말고 설계를 고친다(보통 둘 중 하나가 треть 빈으로 분리될 책임).

## 설정 바인딩 표준형

```java
@ConfigurationProperties(prefix = "app.kiwoom")
public record KiwoomProps(String baseUrl, Duration timeout, int maxRetry) {}
// application.yml: app.kiwoom.base-url: ... + 환경변수 APP_KIWOOM_BASE_URL 자동 매핑
```

- @Value 산탄총보다 record + @ConfigurationProperties — 타입·검증(@Validated)·테스트 용이. dev-fastapi BaseSettings의 등가물.
