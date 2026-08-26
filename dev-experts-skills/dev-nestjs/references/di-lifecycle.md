# DI·생명주기 심화 — 프로바이더 4형·테스트 오버라이드·요청 순서 (SKILL.md 비중복)

## 프로바이더 등록 4형

```typescript
@Module({
  providers: [
    WatchService,                                          // 1. 클래스 (표준)
    { provide: "RATE_LIMIT", useValue: 20 },               // 2. 값 (설정 상수)
    { provide: TickSource, useFactory: (cfg: ConfigService) =>  // 3. 팩토리 (조립 로직)
        cfg.get("env") === "test" ? new FakeSource() : new KiwoomSource(cfg),
      inject: [ConfigService] },
    { provide: AbstractRepo, useClass: PgRepo },           // 4. 별칭 (포트->어댑터 - clean-architecture)
  ],
})
```

- 토큰이 클래스가 아니면(@Inject("RATE_LIMIT")) 문자열보다 `Symbol` 또는 InjectionToken 상수로 — 오타가 컴파일에 잡히게.
- useFactory가 dev-design-patterns의 "조립은 조립 지점에서" — 분기 생성 로직이 서비스 안으로 새지 않게 하는 자리.

## 테스트 오버라이드 표준형

```typescript
const module = await Test.createTestingModule({ imports: [WatchModule] })
  .overrideProvider(TickSource).useValue(fakeSource)       // dev-fastapi dependency_overrides 등가
  .overrideGuard(AuthGuard).useValue({ canActivate: () => true })
  .compile();
```

- e2e는 `module.createNestApplication()` + supertest — **전역 파이프를 테스트 앱에도 등록**해야 한다(main.ts의 등록이 자동 적용 안 됨 — "테스트는 통과인데 운영에서 422" 또는 그 반대의 원인).
- 단위는 그냥 클래스 직접 생성(new Service(fakeRepo)) — TestingModule도 비용이다(dev-testing 층 결정).

## 요청 생명주기 전체 순서 (디버깅 지도)

```
미들웨어 -> 가드(전역->컨트롤러->핸들러) -> 인터셉터(요청측, 같은 순서)
-> 파이프(전역->...->파라미터) -> 핸들러
-> 인터셉터(응답측, 역순) -> 예외 필터(터진 단계 이후 처리)
```

- "내 인터셉터가 가드보다 먼저 돌길 기대" 같은 순서 오해가 책임 혼합(안티패턴 3)의 짝 — 이 지도로 판정.
- 예외 필터는 **터진 지점 이후**만 잡는다 — 미들웨어 예외는 필터 밖(Express 에러 핸들러 영역).

## 생명주기 훅

| 훅 | 용도 |
|---|---|
| onModuleInit | 의존 주입 완료 후 초기화 (생성자에서 async 불가의 우회) |
| onApplicationBootstrap | 전 모듈 준비 후 — 워밍업·구독 시작 |
| onModuleDestroy / beforeApplicationShutdown | 정리 — **enableShutdownHooks() 호출해야 작동** (dev-docker graceful shutdown의 NestJS 끝단; 누락 시 SIGTERM에 정리 없이 죽음) |

## ConfigModule 요점

```typescript
ConfigModule.forRoot({ isGlobal: true, validate: validateEnv })  // zod/class-validator로 기동 시 검증
```

기동 시 환경 검증 실패가 장점(dev-fastapi BaseSettings·dev-spring @ConfigurationProperties와 동일 철학) — validate 없이 쓰면 누락이 첫 요청에서 발견된다.
