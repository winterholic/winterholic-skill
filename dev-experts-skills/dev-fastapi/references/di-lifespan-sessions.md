# 의존성 주입 심화 — yield 의존성·수명 판단·lifespan·테스트 오버라이드 (SKILL.md 비중복)

## 수명 판단표 (어디서 만들 것인가 — 이 표가 안티패턴 3·6의 일반형)

| 자원 | 수명 | 생성 위치 |
|---|---|---|
| DB 세션·트랜잭션 | 요청 | yield 의존성 (`Depends(get_db)`) |
| DB 엔진·커넥션 풀 | 앱 | lifespan (yield 앞 생성, 뒤 정리) |
| httpx.AsyncClient | 앱 | lifespan — 요청마다 만들면 커넥션 풀 이점 소멸 |
| 설정(BaseSettings) | 앱 | lifespan 또는 `@lru_cache` 팩토리 — 환경변수 1회 평가 |
| 현재 사용자(인증) | 요청 | Depends 체인 (`get_current_user`) |
| 요청 ID·로깅 컨텍스트 | 요청 | 미들웨어 또는 의존성 |

판단이 애매하면: "두 요청이 이걸 공유해도 되는가?" — 아니오면 요청 수명.

## yield 의존성의 실제 동작 (오해 잦은 지점)

```python
def get_db():
    db = SessionLocal()
    try:
        yield db          # <- 여기서 엔드포인트 실행
        db.commit()       # 엔드포인트가 예외 없이 끝났을 때만
    except Exception:
        db.rollback()
        raise             # 삼키면 500 대신 침묵 — dev-python 안티패턴 #3
    finally:
        db.close()
```

- **yield 뒤 코드는 응답 전송 후에 실행될 수 있다**(버전에 따라 응답 직전/직후 차이 있음 — 확인 필요: 사용 버전 release notes). 응답 내용에 반영돼야 하는 작업을 yield 뒤에 두지 말 것.
- 의존성은 같은 요청 안에서 **캐시된다** — `Depends(get_db)`를 여러 곳에 써도 세션은 1개. 캐시를 끄려면 `Depends(get_db, use_cache=False)` (드묾).
- 의존성 체인은 합성이 정답: `get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db))` — 인증이 자동으로 DB를 같이 받는다.

## lifespan 표준형

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await create_pool(settings.dsn)     # 시작
    app.state.pool = pool
    yield                                       # 서비스 중
    await pool.close()                          # 종료(배포·재시작 시 정리 보장)

app = FastAPI(lifespan=lifespan)
```

- 접근은 `request.app.state.pool` 또는 이를 감싼 의존성으로 — 모듈 전역 변수로 빼돌리면 안티패턴 3으로 회귀.
- 테스트에서 lifespan 실행이 필요하면 `with TestClient(app):` 컨텍스트 형태로 (with 없이 호출하면 lifespan이 안 돈다 — 조용한 함정).

## 테스트 오버라이드 (TestClient에서 진짜 DB 안 붙기)

```python
app.dependency_overrides[get_db] = lambda: iter([fake_session])  # 또는 제너레이터 함수
client = TestClient(app)
...
app.dependency_overrides.clear()   # 테스트 간 누수 방지 — fixture teardown에서
```

- 오버라이드 대상은 **함수 객체 그 자체**가 키다 — 같은 로직의 다른 함수로는 안 걸린다.
- clear() 누락이 "혼자 돌면 통과, 전체 돌면 실패" 플레이키의 단골 원인.

## Depends 과용 경계 (정직한 한계)

- 2~3단 체인까지가 가독 한계 — 그 이상이면 서비스 객체로 묶어 1개 의존성으로.
- 비즈니스 로직을 의존성 안에 넣지 말 것 — 의존성은 자원·컨텍스트 공급자다. 로직이 들어가면 테스트가 프레임워크에 묶인다.
