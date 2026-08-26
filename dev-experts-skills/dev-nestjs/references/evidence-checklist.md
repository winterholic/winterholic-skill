# evidence + 출고 전 체크리스트

## 실증·출처

- **NestJS 공식 문서 — Injection scopes** (https://docs.nestjs.com/fundamentals/injection-scopes) — "request-scoped providers will have an impact on application performance" 성능 경고 + 스코프 버블링("CatsController가 CatsService 의존이면 같이 REQUEST화") 명시. 안티패턴 4의 1차 출처. (2026-06 웹 확인)
- **NestJS 공식 문서 — Circular dependency** (https://docs.nestjs.com/fundamentals/circular-dependency) — forwardRef는 "instantiation 순서가 비결정적"인 우회책이며, 대안으로 ModuleRef로 한쪽을 지연 조회해 재설계할 것을 명시. 안티패턴 5의 1차 출처. (2026-06 웹 확인 — docs 페이지는 SPA라 본문 직접 fetch는 안 됨, 내용은 검색·Trilon 블로그로 교차확인)
- **Trilon 블로그 — Avoiding Circular Dependencies in NestJS** (https://trilon.io/blog/avoiding-circular-dependencies-in-nestjs) — NestJS 코어팀 운영. "forwardRef는 정말 답이 없을 때의 last resort이며 catch-all로 쓰면 안 됨", 순환은 Nest의 병렬 의존 평가에서 race condition을 유발한다고 경고. 안티패턴 5의 "forwardRef는 1곳만" 근거 강화. (2026-06 웹 확인)
- **NestJS 공식 문서 — Request lifecycle** (https://docs.nestjs.com/faq/request-lifecycle) — 실행 순서: 미들웨어 → 가드 → **인터셉터(전)** → 파이프 → 핸들러 → 인터셉터(후) → 예외 필터. 주의: 인터셉터(전)는 파이프보다 **먼저** 돈다. SKILL.md의 "가드→파이프→핸들러→인터셉터"는 책임 배치용 4단계 추상화이며, 정확한 실행 순서는 `di-lifecycle.md`의 지도를 따른다. 안티패턴 3의 1차 출처. (2026-06 공식 페이지 fetch 확인)
- **GitHub mass assignment 사건 (2012, Egor Homakov)** — Homakov가 `public_key[user_id]` 숨김 필드로 Rails 저장소에 자기 SSH 키를 주입, master에 커밋. GitHub 공동창업자 Tom Preston-Werner가 "incoming form parameters 검증 실패(mass-assignment)" 원인 확인. 이 사건이 Rails 4의 strong_parameters 기본화 계기. SKILL.md 실전 케이스(whitelist의 근거). 출처: Homakov 본인 글(http://homakov.blogspot.com/2012/03/how-to.html), The Hacker News(https://thehackernews.com/2012/03/github-hacked-with-ruby-on-rails-public.html). (2026-06 웹 확인)
- **NestJS 11 발표 (Trilon 공식 블로그)** (https://trilon.io/blog/announcing-nestjs-11-whats-new) — 2025-01 릴리스. 핵심: Express v5 기본 채택(라우트 매칭·쿼리 파서 breaking change), Node.js 20+ 요구(16·18 지원 종료), 종료 라이프사이클 훅 순서 역전, ConsoleLogger JSON 로깅, ParseDatePipe·IntrinsicException 신규. 버전 라벨 출처. (2026-06 웹 확인)
- **NestJS 공식 문서 — Validation** (https://docs.nestjs.com/techniques/validation) — `whitelist: true`는 데코레이터 없는 필드를 **조용히 제거**(strip), `forbidNonWhitelisted: true`(whitelist와 함께)는 미선언 필드 발견 시 **400으로 거부**. "whitelisted = class-validator 데코레이터를 가진 속성". 안티패턴 2·mass assignment 방어의 1차 출처. 보안 민감 입력은 strip보다 forbidNonWhitelisted로 거부가 더 명시적. (2026-06 웹 확인)
- 오픈소스 차용 표기: NestJS 보일러플레이트 다수(색인 인지, 본문 비복사). **역흡수**: 4단계 책임 고정표·REQUEST 스코프 전염 경고의 검출화·테스트 앱 전역 파이프 누락 함정 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (NestJS 코드 출고 시)

- [ ] 전역 ValidationPipe(whitelist·transform) 등록 — 테스트 앱에도
- [ ] 기능 모듈 분할 + exports 최소
- [ ] forwardRef 0 (있으면 경계 재검토 기록) — `nest_check.py` 0건
- [ ] REQUEST 스코프 0 (사유 없는 한)
- [ ] 핸들러 수동 검증 0 (DTO 선언)
- [ ] 예외가 전역 필터에서 표준 스키마로
- [ ] 응답 DTO 분리 (엔티티 비노출)
- [ ] enableShutdownHooks + 정리 훅 (컨테이너 배포 시)
- [ ] 단위는 직접 생성, 통합은 TestingModule, e2e 스모크 1+

## 점검 주기 (부패 중간 — 반기)

- NestJS 메이저 + Express/Fastify 어댑터 기본 변화 확인
- class-validator 유지보수 상태 (대체재 흐름 확인 필요 시점)
