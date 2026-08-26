# pytest 실전 관행 — fixture·parametrize·patch 위치·conftest (SKILL.md 비중복)

## fixture 설계 규칙

- **scope 판단**: 기본 function(테스트마다 새로). 생성이 비싼 읽기 전용 자원(앱 인스턴스, 스키마 적용된 DB 컨테이너)만 session/module로 올리되, **세션 스코프 + 가변 상태**는 테스트 간 오염의 공식 — 올리려면 불변이어야 한다.
- **yield fixture가 정리의 표준형**:
  ```python
  @pytest.fixture
  def db_session(engine):
      conn = engine.connect()
      tx = conn.begin()
      yield Session(bind=conn)
      tx.rollback()          # 테스트가 뭘 했든 원상복구 - commit 안 함
      conn.close()
  ```
  트랜잭션 롤백 격리는 "테스트마다 고유 데이터" 규칙(SKILL.md 안티패턴 3)의 가장 싼 구현.
- **factory fixture**: 값이 아니라 함수를 반환 — 한 테스트에서 여러 개 만들 때.
  ```python
  @pytest.fixture
  def make_tick(): 
      def _make(price=1000, ts=None): ...
      return _make
  ```
- conftest.py 배치: fixture는 **사용하는 테스트와 가장 가까운** conftest에. 루트 conftest는 전역 설정(마커 등록·플러그인)만 — 루트에 fixture가 쌓이면 안티패턴 6의 거대 conftest.

## parametrize 관용구

```python
@pytest.mark.parametrize("raw, expected", [
    ("1,000", 1000),          # 콤마 한국 포맷
    ("1000.0", 1000),         # 소수점 문자열
    pytest.param("", None, id="empty-string"),   # id로 실패 메시지 가독화
])
def test_parse_price(raw, expected):
    assert parse_price(raw) == expected
```

- 케이스가 5개를 넘으면 id 의무 — `test_parse_price[2]` 실패는 아무 정보가 없다.
- 행동이 다른 입력만 추가(SKILL.md 워크플로우 2) — parametrize는 같은 분기 반복 검증용이 아니라 **분기별 대표** 나열용.

## patch 위치 규칙 (안티패턴 2의 각론)

| 대상 코드의 임포트 형태 | patch 경로 |
|---|---|
| `import requests` 후 `requests.get(...)` | `"myapp.client.requests.get"` |
| `from requests import get` 후 `get(...)` | `"myapp.client.get"` |
| `from myapp.config import TIMEOUT` (상수) | patch 불가 — 이미 값 복사됨. 함수가 settings를 인자/의존성으로 받게 리팩터링 |

- 검증법: patch가 진짜 걸렸는지 의심되면 **일부러 깨뜨려본다** — mock 반환값을 명백히 이상한 값으로 두고 테스트가 그걸 보는지 확인.
- `mocker`(pytest-mock)를 unittest.mock 직접 사용보다 권장 — 테스트 끝나면 자동 원복(수동 stop 누락 = 테스트 간 오염원 하나 제거).
- monkeypatch(내장)는 환경변수·속성 교체용: `monkeypatch.setenv("APP_DSN", ...)` — 외부 라이브러리 함수 교체는 mocker가 명확.

## 자주 쓰는 실행 옵션 (copy-paste)

```
pytest -x -q                      # 첫 실패에서 중단(작업 중 기본)
pytest -k "normalize and not slow"  # 이름 부분 매칭
pytest --lf                       # 직전 실패만 재실행(수리 루프)
pytest -q --durations=10          # 느린 테스트 상위 10 - 10초 규칙 위반자 색출
pytest --cov=pkg --cov-report=term-missing   # 미커버 라인 번호까지
python -W error::RuntimeWarning -m pytest    # 미await 코루틴을 실패로 (async 코드)
```

## async 테스트

- `pytest-asyncio` + `@pytest.mark.asyncio` (또는 asyncio_mode=auto 설정). async 테스트에서 동기 sleep은 이중 죄 — `await asyncio.sleep` 조차 폴링 대기로 대체.
- async fixture도 yield 형태 동일. event loop fixture를 직접 만지는 코드는 플러그인 버전 간 깨짐이 잦다(확인 필요: pytest-asyncio 현재 권장 방식) — 기본 제공을 따른다.
