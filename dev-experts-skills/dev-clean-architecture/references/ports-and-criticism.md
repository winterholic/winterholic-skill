# 포트 설계 상세 + 비판 회계 (SKILL.md 비중복)

## 포트 시그니처 설계 (도메인 어휘 규칙)

```python
# domain/ports.py - 파이썬에선 Protocol(타입 검사용) 또는 그냥 함수 시그니처 합의
from typing import Protocol
from domain.models import RawTick, TradingDay

class TickSource(Protocol):
    def fetch(self, code: str, day: TradingDay) -> list[RawTick]: ...
    # NOT: def fetch(self, url, params) -> requests.Response  <- 어휘 누수
```

- 반환·인자·예외 전부 도메인 타입 — `requests.Response`·ORM 모델·HTTP 코드가 보이면 누수(안티패턴 4).
- 예외 번역: 어댑터가 `requests.Timeout` → `domain.SourceUnavailable`로. 도메인은 "소스가 안 된다"만 알면 되고, 재시도 정책(dev-data-engineering)은 어댑터 일.
- 포트 정의 위치는 **안쪽**(domain) — 바깥이 안의 계약에 맞춘다(이게 의존 역전의 '역전').

## 함수 주입이 클래스 포트보다 먼저 (파이썬 보정)

```python
# 포트가 메서드 1개면 Protocol 클래스 대신 Callable로 충분
FetchFn = Callable[[str, TradingDay], list[RawTick]]

def ingest(day: TradingDay, fetch: FetchFn, save: SaveFn) -> IngestReport: ...
# 테스트: ingest(day, fetch=lambda c, d: [tick1], save=spy)
```

메서드 2~3개부터 Protocol — dev-design-patterns 단순 사다리와 동일 규율.

## 주요 비판 정리 (동비중 원칙 — 알면서 선택하라)

| 비판 | 타당한 부분 | 반론·절충 |
|---|---|---|
| "간접·보일러플레이트가 과하다" | 4층 직역에선 사실 — DTO 변환 4회는 실비용 | 규칙(방향)과 구현(층수) 분리 — 2층 기본형이 절충 |
| "프레임워크 독립은 환상" (어차피 못 바꿈) | DB·웹 프레임워크 교체는 거의 안 일어남 — 맞다 | 효익의 실체는 교체가 아니라 **테스트 더블과 재사용** — 시계·외부API가 매일 증명 |
| "추상층이 막상 교체 때 안 맞음" | 쿼리 의미론·트랜잭션 차이는 인터페이스로 안 가려짐 — 맞다 | 그래서 DB는 정직 결합이 기본(안티패턴 5) — 포트는 좁은 경계에만 |
| "성능 비용" | 핫패스의 변환·간접은 측정 가능한 비용 | 측정으로 예외 결정(dev-performance) — 전면 포기 사유는 아님 |
| "원전이 모호·교조적 수용 양산" | 책의 그림이 처방으로 오독되기 쉬움 — 커뮤니티 현상으로 사실 | 이 스킬의 존재 이유 — 규칙 한 문장만 지키고 나머지는 회계 |

## 헥사고날·어니언과의 관계

셋 다 같은 한 문장(의존은 안쪽으로)의 방언이다 — 헥사고날(2005, Cockburn)이 포트·어댑터 어휘의 원조, 어니언(2008)·클린(2012)이 재서술. **선택 문제가 아니다** — 어휘만 고르면 된다(이 스킬은 헥사고날 어휘 + 클린의 규칙 문장 사용).

## 점진 도입 경로 (기존 진흙 코드에서)

1. 새 순수 함수부터 domain/에 (신규분만 규칙 적용).
2. 기존 코드는 변경할 때만 순수 부분 추출(dev-refactoring 보이스카웃).
3. `dependency_direction.py`를 CI 게이트로 — 신규 역행만 차단(기존분은 백로그).
4. 시계·외부 API 주입 전환을 우선(테스트 효익 즉시) — 리포지토리 추상화는 하지 않는 게 기본.
