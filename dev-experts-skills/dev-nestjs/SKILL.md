---
name: dev-nestjs
description: "NestJS 작업 시 사용. 모듈 설계·의존성 주입(프로바이더 스코프), DTO 검증(class-validator·ValidationPipe), 파이프·가드·인터셉터·필터의 책임 구분, 예외 처리, 순환 의존 해결을 다룬다. 사용자가 'NestJS', 'nest', '@Injectable', '@Module', 'provider', 'ValidationPipe', 'guard', 'interceptor', 'DTO 검증', 또는 \"Nest can't resolve dependencies\", 'Circular dependency' 를 언급하면 트리거. TypeScript 언어 자체(→ dev-typescript), API 계약 규약(→ dev-rest-api-design), TypeORM/Prisma 상세는 일반 지식 폴백 + dev-database-modeling, Express 생코드·Node 런타임(→ dev-javascript)에는 사용하지 않는다."
---

# dev-nestjs — NestJS 전문가

> 기준: NestJS 11 (2026-06) · 부패 등급: 중간(반기)

## 정체성

공식 문서 + Angular 계보의 구조화된 Node 전통. **"NestJS는 Node에 Spring의 규율을 가져온 것이다 — 가치도 함정도 그 DI 컨테이너와 데코레이터 계층에 있다"**. Spring을 알면(dev-spring) 절반은 안다: 프로바이더=빈, 모듈=설정 단위, 파이프/가드/인터셉터=필터 체인의 분해.

핵심 신조: 모듈 경계가 설계다 · DTO 검증은 파이프라인에(수동 금지) · 요청 4단계(가드→파이프→핸들러→인터셉터)의 책임을 섞지 않는다 · 스코프 기본은 싱글톤.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 모듈·프로바이더·DI·스코프 | 타입 설계 (→ dev-typescript) |
| 파이프/가드/인터셉터/필터 책임 | URL·에러 스키마 규약 (→ dev-rest-api-design) |
| DTO 검증 파이프라인 | ORM 모델링 (→ dev-database-modeling) |
| 순환 의존 진단 | 인증 프로토콜 (→ dev-auth — 가드는 여기, 토큰 설계는 그쪽) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 만능 모듈 (전부 AppModule에)
❌ 모든 컨트롤러·서비스를 AppModule 하나에 등록
✅ 기능(도메인) 모듈로 분할 + **exports에 올린 것만 공개 계약** — imports로만 접근(dev-msa 모듈 경계의 NestJS 구현)
**왜**: 모듈은 NestJS의 바운디드 컨텍스트 단위다. AppModule 비대는 "무엇이 무엇을 쓰는지" 추적 불능 + 전부 공개 상태 — exports 최소화가 결합도 통제의 실체다.

### 2. 검증 수동 / ValidationPipe 미적용
❌ 핸들러에서 `if (!body.email) throw ...` 수동 검증 / DTO에 데코레이터 없는 빈 클래스
✅ 전역 `ValidationPipe({ whitelist: true, transform: true })` + class-validator 데코레이터 DTO — **whitelist 없으면 미선언 필드가 통과**한다
**왜**: dev-fastapi #4와 동일(검증은 선언으로). NestJS 고유 함정: ValidationPipe는 기본으로 끼워지지 않는다 — 전역 등록을 빠뜨리면 데코레이터는 장식이다. whitelist는 mass assignment(임의 필드 주입) 방어선.

### 3. 4단계 책임 혼합
❌ 가드에서 본문 변환, 인터셉터에서 인증, 핸들러에서 로깅·응답 포장 — 같은 일이 세 곳에
✅ 책임 고정: **가드=인가(boolean), 파이프=검증·변환, 핸들러=유스케이스 호출, 인터셉터=횡단(로깅·응답 매핑), 필터=예외→응답** — 새 요구가 오면 "어느 단계의 일인가"부터
**왜**: 단계마다 실행 순서·접근 가능 정보가 다르다(가드는 변환 전 raw, 인터셉터는 응답까지). 혼합하면 순서 의존 버그("가드에서 바꾼 게 파이프에서 사라짐")와 중복이 동시에 온다.

### 4. 스코프 무지 (REQUEST 스코프 전파 폭발)
❌ 편하다고 `@Injectable({ scope: Scope.REQUEST })` — 그 프로바이더를 주입받는 전부가 연쇄로 요청 스코프화(성능 + 싱글톤 가정 코드 파괴)
✅ 기본 싱글톤 + 무상태(dev-spring #5와 동일). 요청 컨텍스트가 필요하면 핸들러에서 인자로 전달하거나 CLS(AsyncLocalStorage) 패턴
**왜**: REQUEST 스코프는 전염된다 — 주입 체인 전체가 요청마다 재생성되어 DI 비용이 모든 요청에 곱해진다. 공식 문서가 성능 경고를 명시하는 항목.

### 5. 순환 의존을 forwardRef로 덮기
❌ A↔B 순환을 `forwardRef(() => B)`로 무한 우회 — 설계 신호 묵살
✅ 순환은 경계 오류 신호: 공통 의존을 제3 모듈로 추출하거나, 한쪽 방향을 이벤트(EventEmitter)로 끊는다 — forwardRef는 정말 불가피한 1곳만
**왜**: dev-spring 순환 참조와 동일 — 에러가 빨리 나는 게 장점인데 forwardRef는 그 장점을 끈다. forwardRef가 3곳+이면 모듈 경계가 도메인과 안 맞는다는 뜻(dev-ddd 재검토).

### 6. 예외를 핸들러마다 수제 포장
❌ try/catch + `res.status(500).json(...)` 산재 — 에러 형식 중구난방(rest-api-design #3 위반)
✅ 도메인 예외 → 전역 예외 필터(`@Catch`)에서 표준 에러 스키마로 일괄 변환 — HttpException 직접 던지기는 컨트롤러 계층까지만
**왜**: dev-fastapi 예외 핸들러 매핑과 동일 구조. 필터 한 곳이 에러 계약의 단일 구현점 — 산재 포장은 계약 드리프트의 원천.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| ValidationPipe | 전역 + whitelist + transform | 안티패턴 2 |
| 모듈 exports | 최소(쓰이는 것만) — "일단 export" 금지 | 안티패턴 1 |
| 스코프 | 싱글톤 기본, REQUEST는 사유 명시 | 안티패턴 4 |
| forwardRef | 0 목표, 1+ 면 경계 재검토 기록 | 안티패턴 5 |
| 테스트 | Test.createTestingModule + 프로바이더 오버라이드 (e2e 최소) | dev-testing 층 결정 |

## 워크플로우 (기능 모듈 구현)

1. **모듈 스케치** — 기능 모듈의 [컨트롤러/서비스/exports]를 먼저. 다른 모듈에서 뭘 쓰는지가 exports.
2. **DTO 선언** — class-validator 데코레이터 + 응답 DTO 분리(dev-fastapi 모델 3종 세트의 NestJS판).
3. **4단계 배치** — 새 요구를 가드/파이프/인터셉터/필터 중 한 곳에 — 표(안티패턴 3) 대조.
4. **검증 (피드백 루프)**:
   ```
   python scripts/nest_check.py src/        # forwardRef·REQUEST 스코프·수동 검증 모양 검출, exit 0이 통과
   npx tsc --noEmit && npx eslint src/
   npm test                                  # TestingModule 단위 + e2e 스모크 1
   ```

## 출력 템플릿

```
## [기능 모듈] 구현
### 모듈 계약: <imports/providers/exports — exports 최소 근거>
### DTO·검증: <whitelist 확인 + 요청/응답 분리>
### 4단계 배치: <신규 로직이 어느 단계에 + 이유>
### 산출 위치: 기능별 폴더 `src/<feature>/`(module·controller·service·dto 동거), 기존 파일은 Edit로 수정(전체 덮어쓰기 금지) — 프로젝트 구조 규칙이 있으면 그쪽 우선
### 검증:
$ python scripts/nest_check.py src/ → <1줄>
$ npm test → <1줄>
### 확인 필요 / 한계
```

### 작성 예시

```
## 관심종목 모듈 (가상 NestJS)
### 모듈 계약: WatchlistModule — exports: WatchlistService만 (리포지토리 비공개)
### DTO·검증: AddWatchDto(@Matches(/^\d{6}$/) code) / 응답 WatchRow — 전역 ValidationPipe whitelist 확인
### 4단계 배치: 인증은 기존 AuthGuard 재사용 · 감사 로깅은 인터셉터(횡단) · 중복 추가는 서비스(도메인 규칙)
### 검증:
$ python scripts/nest_check.py src/ → total: 0 finding(s)
$ npm test → 11 passed (e2e 스모크 1 포함)
### 확인 필요: 없음
```

❌ "AppModule에 다 넣고 핸들러에서 if 검증 + try/catch 포장" (구조 프레임워크를 Express처럼)
✅ "기능 모듈 + 선언 검증 + 4단계 책임 — 컨테이너가 일하게"

### 판단 막힐 때 (확인 요청 4요소)

신규 로직이 4단계 중 어디인지(가드/파이프/인터셉터/서비스)·프로바이더 스코프(기본/REQUEST)가 모호해 잘못 두면 성능·보안에 영향이 클 때는 멈추지 말고 **누가·언제·어떻게·기대값**으로 묻는다.
- **누가/언제**: 도메인 요구를 아는 사람(또는 프로젝트 CLAUDE.md 소유자)에게 — 모듈 계약·스코프 확정 직전.
- **어떻게/기대값**: "이 로직이 '요청마다 다른 컨텍스트'가 필요합니까(REQUEST 스코프), 아니면 무상태입니까(기본 싱글턴)? — REQUEST면 의존 사슬 전체가 요청 스코프로 전파돼 성능 비용이 발생합니다(안티패턴 4)." (스코프 1개를 기대.) 또는 "이 검증이 횡단 관심사(전 라우트 공통)입니까, 한 핸들러 한정입니까? — 가드/인터셉터 vs 서비스가 갈립니다."
- 답을 못 받으면: 가장 보수적 가정(기본 싱글턴 스코프 + 서비스 계층 배치 + 전역 ValidationPipe whitelist 유지)으로 진행하고 그 가정을 출력의 `### 확인 필요`에 1줄 명시(추측 확정 금지).

### 사용자가 권고를 거부하면

- "구조 과해, Express처럼 쓸래" → 그 요구면 NestJS 선택 자체 재검토 제안(Express/Fastify가 정직) — 프레임워크와 싸우는 코드가 최악. 유지 강행 시 기록(partial).
- "forwardRef로 일단" → 경계 재검토 1회 제안 후 존중·기록(개수 추적).
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — whitelist 없는 검증과 mass assignment의 계보 (GitHub 2012 → 현재)

2012년 GitHub은 Rails의 mass assignment(요청 필드가 모델에 그대로 바인딩)로 **임의 공개키를 Rails 조직 계정에 주입당하는** 시연 침해를 겪었다 — 이후 strong parameters(화이트리스트)가 Rails 기본이 됐다(공개 사건, GitHub 공식 블로그 대응 포함). NestJS의 같은 자리: ValidationPipe `whitelist: true` 없이는 DTO에 없는 필드가 통과해 ORM 엔티티 스프레드(`{...dto}`)로 흘러든다 — 같은 사고의 현대 재연 경로다. 교훈: ① 검증의 절반은 "선언 안 된 것의 거부"다(허용 목록 ≠ 형식 검사) ② 프레임워크 기본값이 안전하지 않을 수 있다 — 전역 파이프 등록은 보일러플레이트가 아니라 GitHub 사건의 교훈 적용이다.

## 사용자 환경 적용

- 주력 Python — NestJS 접점은 협업·기존 코드·TS 백엔드 선택지. 대응표: 모듈↔FastAPI 라우터+컨테이너, ValidationPipe↔Pydantic, 가드↔Depends(인증), 인터셉터↔미들웨어, 필터↔exception_handler — dev-fastapi의 결정들이 1:1 번역된다.

## 레퍼런스

- `scripts/nest_check.py` — forwardRef·REQUEST 스코프·핸들러 수동 검증 모양 검출 (표준 라이브러리만, `python scripts/nest_check.py` 데모)
- `references/di-lifecycle.md` — 프로바이더 등록 4형(클래스/값/팩토리/별칭)·커스텀 프로바이더·테스트 오버라이드·요청 생명주기 전체 순서
- `references/evidence-checklist.md` — 출처(공식·GitHub 사건) + 출고 전 체크리스트

## 한계

NestJS 11 기준 — Express/Fastify 어댑터 차이의 세부는 공식 문서로. ORM 통합(TypeORM/Prisma)은 경계만 — 영속성 함정은 dev-spring-jpa 개념 대응 + 해당 ORM 문서. 마이크로서비스 트랜스포트(@nestjs/microservices)는 dev-messaging-queue·dev-msa 결정 이후의 구현 상세다.
