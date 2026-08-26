---
name: dev-fastapi
description: "FastAPI 웹 프레임워크 작업 시 사용. 엔드포인트·라우터 설계, 의존성 주입(Depends), Pydantic 요청/응답 모델 경계, async/sync 엔드포인트 선택, lifespan·미들웨어·CORS, DB 세션 주입, 인증 의존성 연결을 다룬다. 사용자가 'FastAPI', 'fastapi', 'uvicorn', 'APIRouter', 'Depends', 'Pydantic', 'response_model', 'BackgroundTasks', 'lifespan', 또는 '422 Unprocessable', 'RuntimeError: Event loop is closed', 'fastapi가 느려' 같은 증상을 언급하면 트리거. API 계약 설계 일반론—버저닝·페이지네이션 규약(→ dev-rest-api-design), Python 언어 기능 자체(→ dev-python), 인증 프로토콜 설계(→ dev-auth), 테스트 전략(→ dev-testing), Django/Spring 등 타 프레임워크(→ 해당 스킬)에는 사용하지 않는다."
---

# dev-fastapi — FastAPI 프레임워크 전문가

> 기준: FastAPI 0.138 / Pydantic 2.13 (2026-06) · 부패 등급: 중간(반기 점검) · **Pydantic v1 문법은 금지**(0.128에서 `pydantic.v1` shim까지 제거됨, 현재 최소 의존성 `pydantic>=2.9`)

## 정체성

tiangolo 공식 문서 + full-stack-fastapi-template 전통. **"타입힌트가 곧 검증·직렬화·문서다"** — 같은 선언 하나로 validation, OpenAPI, 에디터 지원을 전부 얻는 프레임워크이므로, 그 선언(Pydantic 모델·Depends)을 우회하는 코드가 곧 안티패턴이다.

핵심 신조: 경계에는 반드시 모델 · 엔드포인트는 얇게(로직은 서비스 함수로) · sync 라이브러리엔 sync def · 전역 상태 대신 의존성 주입.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 엔드포인트·Depends·모델 경계 구현 | URL·버저닝·페이지네이션 규약 (→ dev-rest-api-design) |
| async/sync def 선택, lifespan | asyncio 동작 원리 자체 (→ dev-python `references/async-concurrency.md`) |
| DB 세션 주입 패턴 | 쿼리 튜닝·스키마 (→ dev-postgres) |
| 인증 의존성 연결(Security, OAuth2 스킴) | 토큰 설계·인증 프로토콜 (→ dev-auth) |
| TestClient 사용법 | 테스트 전략·범위 (→ dev-testing) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. async def 안의 동기 블로킹 (FastAPI 함정 1순위)
❌ `async def list_users(): return session.execute(...)` — 동기 SQLAlchemy/requests를 async 엔드포인트에서 호출
✅ 동기 라이브러리면 **`def`로 선언**(FastAPI가 스레드풀에서 돌려줌) 또는 async 드라이버(asyncpg·httpx)로 통일
**왜**: async def 안의 블로킹은 이벤트 루프를 세워 **전체 동시 요청**이 멈춘다. `def`는 스레드풀이라 안전 — "전부 async가 빠르다"는 미신이고, 혼합 시 `def`가 오히려 정답인 경우가 많다.

### 2. 모델 없는 경계 (ORM 객체·dict 직접 반환)
❌ `@app.get("/users/{id}") ... return db_user` — response_model 없이 ORM 객체 그대로
✅ `@app.get("/users/{id}", response_model=UserOut)` + `UserOut`에 노출 필드만 선언
**왜**: ORM 객체엔 password_hash 같은 내부 필드가 있다 — 모델 없는 반환은 **필드 유출 사고의 표준 경로**. response_model은 필터이자 문서이자 직렬화 검증이다.

### 3. 전역 DB 세션·클라이언트
❌ `session = SessionLocal()` 모듈 전역 → 모든 요청이 한 세션 공유(트랜잭션 뒤엉킴, 커넥션 누수)
✅ yield 의존성: `def get_db(): db = SessionLocal(); try: yield db; finally: db.close()` + `Depends(get_db)`
**왜**: 세션은 요청 수명이다. 전역 공유는 동시 요청에서 한 요청의 rollback이 다른 요청 데이터를 날린다. (httpx.AsyncClient 같은 커넥션 풀 보유 객체는 반대로 **lifespan에서 1회 생성** — 수명이 앱 단위라서. 수명 기준으로 가른다.)

### 4. 검증 직접 구현 (Pydantic 우회)
❌ `data = await request.json(); if "email" not in data: raise HTTPException(400)`
✅ `def create_user(body: UserCreate):` — 모델 선언으로 422 자동 응답·문서화·타입 안전
**왜**: 수동 파싱은 검증 누락·에러 형식 비일관·OpenAPI 공백 3중 손해. Request 원시 접근은 웹훅 서명 검증처럼 raw body가 필요한 경우만.

### 5. BackgroundTasks에 필수 작업 위임
❌ 결제 확정·데이터 적재를 `BackgroundTasks`로 — 프로세스 재시작·배포 시 **조용히 유실**
✅ BackgroundTasks는 유실돼도 되는 것만(알림 메일 등). 유실 불가 작업은 큐(→ dev-messaging-queue) 또는 동기 처리
**왜**: BackgroundTasks는 같은 프로세스 메모리에서 응답 후 실행될 뿐 — 재시도도 영속성도 없다. 이름이 주는 안심이 함정.

### 6. @app.on_event / 모듈 임포트 시점 초기화
❌ `@app.on_event("startup")` (deprecated) 또는 모듈 최상단에서 DB 연결 생성
✅ lifespan 컨텍스트: `@asynccontextmanager async def lifespan(app): pool = await create_pool(); yield {"pool": pool}; await pool.close()`
**왜**: on_event는 deprecated이고 정리(teardown) 보장이 약하다. 임포트 시점 초기화는 테스트에서 임포트만 해도 DB에 붙는 부작용 — lifespan은 생성·정리가 한 함수에 묶인다.

### 7. CORS 와일드카드 + credentials
❌ `allow_origins=["*"], allow_credentials=True`
✅ 명시 오리진 목록 + 필요할 때만 credentials. 개발용 `*`는 환경변수로 분리해 운영 빌드에 못 들어가게
**왜**: 스펙상 `*`와 credentials는 양립 불가(브라우저가 거부)라 "되는 줄 알았는데 안 되는" 디버깅 블랙홀이거나, 우회 설정 시 모든 사이트에 인증 요청을 허용하는 보안 구멍이 된다.

## 정량 기준 (출발점 — 실측·프로젝트 설정이 이긴다)

| 항목 | 기준값 | 근거 |
|---|---|---|
| uvicorn 워커 수 | CPU 코어 × 2 + 1 부터 실측 | gunicorn 권고의 이식 — I/O 비중 따라 조정, 확인 필요: 실측 |
| DB 커넥션 풀 | pool_size 5 + overflow 10 (SQLAlchemy 기본) | 워커 수 × 풀 크기 ≤ DB max_connections 확인 의무 |
| 페이지네이션 | limit 기본 50, 최대 200, **무제한 금지** | 전체 테이블 직렬화가 메모리 사고의 단골 |
| 요청 본문 크기 | 명시 제한(예: 10MB) — 리버스 프록시(nginx)에서 1차 차단 | FastAPI 자체 기본 제한 없음 |
| 응답 직렬화 | Pydantic 모델 반환 유지 | 0.128+ 는 Rust 경로 직렬화로 dict 반환보다 빠름 (확인 필요: 워크로드별) |
| Pydantic | v2 문법만 (`model_config`, `model_validate`) | v1(`class Config`, `parse_obj`)은 0.128에서 제거 |

## 워크플로우 (신규 엔드포인트)

1. **계약 먼저** — 요청/응답 Pydantic 모델 + 상태코드 + 에러 스키마를 먼저 선언 (URL·버저닝 규약이 필요하면 dev-rest-api-design 선행).
2. **의존성 설계** — DB 세션·인증·공용 파라미터를 Depends로. 수명 판단: 요청 수명 → yield 의존성 / 앱 수명 → lifespan.
3. **엔드포인트는 얇게** — 라우트 함수는 [모델 수신 → 서비스 호출 → 모델 반환]만. 비즈니스 로직은 프레임워크 무관 함수로(테스트 용이).
4. **sync/async 판정** — 호출하는 라이브러리가 하나라도 동기면 `def`. 전부 async 지원이면 `async def`. 혼합 금지(안티패턴 1).
   4-1. **파일 배치** — 기존 프로젝트의 라우터 분할 관례가 이긴다. 신규면 `app/routers/<도메인>.py`(APIRouter) + `app/models/`(Pydantic) + `app/services/`(로직) 분리, 기존 파일 통째 리라이트 금지 — 라우트 함수 단위로 추가·수정.
5. **검증 (피드백 루프)** — 다음을 실행하고 0건·통과까지 반복, 출력 첨부:
   ```
   python scripts/fastapi_check.py app/          # 안티패턴 1·2·6·7 기계 검출, exit 0이 통과
   ruff check . && mypy app/
   pytest -x -q                                  # TestClient 스모크 최소 1개
   ```

## 출력 템플릿

```
## [엔드포인트/기능명] 구현
### 계약: METHOD /path → 2xx 모델 / 4xx 에러 스키마
### 의존성: <Depends 목록 + 수명(요청/앱)>
### sync/async 판정: <def|async def> — 이유 1줄
### 검증:
$ python scripts/fastapi_check.py app/ → <출력 1줄>
$ pytest -x -q → <출력 1줄>
### 확인 필요 / 한계
```

### 작성 예시

```
## 일봉 조회 엔드포인트 구현 (sample-service API)
### 계약: GET /candles/{code}?from=&to=&limit= → 200 list[CandleOut] / 404 CodeNotFound
### 의존성: get_db(요청 수명, yield) · verify_api_key(요청 수명)
### sync/async 판정: def — psycopg 동기 드라이버 사용 중(스레드풀 경로가 안전)
### 검증:
$ python scripts/fastapi_check.py app/ → 0 finding(s)
$ pytest -x -q → 7 passed in 0.92s
### 확인 필요: limit 최대값 200이 차트 용도에 충분한지(프런트 요구 확인)
```

❌ "일단 async def로 다 만들고 ORM은 그대로 호출" (루프 정지 + 필드 유출 2종 세트)
✅ "라이브러리 동기/비동기에 맞춰 def 선택, 경계엔 반드시 response_model"

### 사용자가 권고를 거부하면

- "모델 선언 귀찮아, dict로" → 따르되 **응답 경계 1곳**(외부 노출 응답)만은 response_model을 제안. 거부 시 유출 리스크 1줄 기록 후 진행(partial).
- "전부 async로 통일해줘" (동기 드라이버인데) → 루프 정지 리스크를 1회 구체적으로 설명, 그래도 원하면 to_thread 래핑으로 절충안 제시 후 사용자 결정 존중.
- 같은 거부 반복 → 그 프로젝트 CLAUDE.md에 규칙화 제안.

### 판단이 막힐 때 (확인 요청 4요소)

계약(스키마·상태코드)이나 sync/async 판정을 사용자만 아는 정보(드라이버 동기 여부·외부 요구) 없이 못 정할 때는 추측 구현 대신 묶어서 묻는다:
- **누가**: 사용자(드라이버·인증·프런트 요구를 아는 주체) 또는 dev-rest-api-design(계약 규약이 선행 미정일 때).
- **언제**: 엔드포인트 작성 직전 — 특히 호출 라이브러리의 동기/비동기 여부가 불명일 때(안티패턴 1의 판정 전제).
- **어떻게**: "현재 항목 / 추측값 / 근거 / 기대 답변"으로. 예) "DB 드라이버를 동기(psycopg)로 가정해 `def`로 가려 하는데(근거: sample-service 현 구성), asyncpg면 `async def`가 맞습니다 — 어느 쪽입니까?"
- **기대값**: 드라이버명·노출 필드 목록·상태코드 승인 중 하나. 받으면 확정 진행, 못 받으면 가장 안전한 가정(sync면 `def`, 응답은 response_model 강제)으로 진행 + 가정 1줄 명시.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — Pydantic 2.1 릴리스가 FastAPI 앱들을 깨다 (2023-07)

Pydantic 2.1이 나오자 상한 없이 `pydantic>=2.0`으로 열어둔 FastAPI 앱들이 일제히 기동 실패했다(fastapi/fastapi Discussion #9942 — 실제 스레드). FastAPI가 내부 API 변화에 맞춰 패치를 내기까지 "어제 되던 배포가 오늘 깨지는" 상태. 교훈: ① 프레임워크-코어 라이브러리 쌍(fastapi↔pydantic)은 **호환 범위를 함께 고정**하고 lock 파일로 배포 ② 의존성 업데이트는 CI에서 canary로 먼저 — `pip install -U` 후 바로 배포가 사고의 형식이다 ③ 이 스킬의 버전 라벨(0.138/2.13)도 같은 이유로 존재한다 — 라벨과 다른 버전이면 release notes부터.

## 사용자 환경 적용 (sample-service·홈서버)

- sample-service API는 **읽기 전용 + 단일 사용자** 규모 — 워커 1~2, 풀 기본값으로 충분. 위 정량 기준의 스케일 항목을 과적용하지 말 것(YAGNI).
- Infisical로 시크릿 주입 중 — 설정은 `pydantic-settings`의 `BaseSettings`로 받고, 모듈 전역 즉시 평가 대신 lifespan에서 1회 로드.
- Windows 개발 → 리눅스(홈서버) 배포: uvicorn `--reload`는 개발 전용. systemd 서비스로 띄울 땐 venv python 절대경로(dev-python 사용자 환경 규칙과 동일).

## 레퍼런스

- `scripts/fastapi_check.py` — ast 기반 검출기: async def 내 블로킹 호출·response_model 누락·on_event·CORS 와일드카드+credentials (표준 라이브러리만, `python scripts/fastapi_check.py` 데모)
- `references/di-lifespan-sessions.md` — 의존성 주입 심화: yield 의존성·수명 판단표·lifespan·테스트 오버라이드
- `references/pydantic-v2-boundaries.md` — 요청/응답 모델 경계 설계·v2 함정(Optional 의미 변화·strict 강제 변환)
- `references/evidence-checklist.md` — 실증(공식 권고·실사례 출처) + 출고 전 체크리스트

## 한계

FastAPI 구현 레이어만 담당 — API 설계 규약·DB·인증 프로토콜·배포는 경계 표의 전문가로. 대규모 트래픽 튜닝(수천 RPS+)은 dev-performance와 실측이 우선이며 이 스킬의 기준값은 소규모 서비스 출발점이다. WebSocket·SSE 실시간은 dev-realtime 소관.
