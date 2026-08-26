# Pythonic 코어 — 데이터 모델·이터레이터·컨텍스트매니저·데코레이터 (SKILL.md 비중복 심화)

> 앵커: *Fluent Python* 2e(Ramalho), *Effective Python* 2e(Slatkin). 페이지 대신 개념 단위 인용.

## 데이터 모델 = 프로토콜을 구현하면 언어가 일해준다

- `__repr__`은 디버깅용(개발자), `__str__`은 표시용(사용자). **`__repr__`만은 항상 구현** — 로그에 `<object at 0x...>`가 찍히는 순간 디버깅 비용이 커진다. dataclass는 공짜로 준다.
- `__eq__`를 구현하면 `__hash__`가 None이 된다(dict 키로 못 씀) — 불변 객체면 `@dataclass(frozen=True)`로 둘 다 해결.
- 컨테이너처럼 굴 객체는 `__len__`/`__getitem__`/`__contains__`만 구현해도 `for`/`in`/슬라이싱이 작동한다 — 상속이 아니라 프로토콜.
- `bool(x)`는 `__bool__` → `__len__` 순서로 본다. "값이 없으면 falsy"를 원하면 `__len__`으로 충분.

## 이터레이터·제너레이터 — 메모리와 조합성의 핵심

- **리스트를 만들 필요가 없으면 만들지 않는다**: `sum(x*x for x in nums)` (제너레이터식) vs `sum([x*x for x in nums])` — 후자는 중간 리스트를 통째로 메모리에 올린다. 수백만 행 시세 데이터에서 차이가 난다.
- 제너레이터는 **1회용**이다. 두 번 순회하면 두 번째는 조용히 빈 결과 — 재사용하려면 list로 굳히거나 매번 새로 만든다(흔한 침묵 버그).
- `yield from`은 단순 위임 + 중첩 제너레이터의 return 값 전달. 깊은 자료구조 평탄화에 관용적.
- 파이프라인 관용구: `lines → parsed → filtered → aggregated`를 각각 제너레이터 함수로 — 각 단계가 독립 테스트 가능해지고 메모리는 상수.
- `itertools` 먼저: `chain`(이어붙임), `islice`(머리만), `groupby`(**정렬된 입력 전제** — 안 지키면 그룹이 쪼개지는 함정), `pairwise`(3.10+).

## 컨텍스트 매니저 — 자원과 임시 상태의 단일 관용구

- `with`의 본질: **예외가 나도 `__exit__`은 실행된다**. 파일·락·DB 커넥션·임시 디렉토리 전부 이걸로.
- 직접 만들 땐 클래스보다 `@contextlib.contextmanager` + try/finally가 짧고 명확:
  ```python
  @contextmanager
  def db_tx(conn):
      try:
          yield conn
          conn.commit()
      except Exception:
          conn.rollback()
          raise          # 삼키지 않는다 — 안티패턴 #3과 동일 원칙
  ```
- `contextlib.suppress(FileNotFoundError)`는 "이 예외는 정말 무시가 정답"일 때의 **명시적** 침묵 — bare except와 의도 표현이 다르다.
- 여러 자원은 3.10+ 괄호 문법: `with (open(a) as f, open(b) as g):`.

## 데코레이터 — 시그니처를 보존하라

- 최소형은 `functools.wraps` 필수 — 없으면 `__name__`/`__doc__`/help()가 wrapper로 바뀌어 디버깅·문서·일부 프레임워크 라우팅이 깨진다.
- 인자 받는 데코레이터(3겹 중첩)는 읽기 어렵다 — 대안: `functools.partial` 또는 클래스 기반(`__call__`). 3겹을 쓸 땐 바깥부터 "설정 → 데코레이터 → wrapper" 주석 한 줄씩.
- `functools.lru_cache`/`cache`: 인자가 hashable이어야 하고, **인스턴스 메서드에 붙이면 self가 캐시 키에 들어가 객체가 영원히 살아남는다**(메모리 누수) — 모듈 함수나 `cached_property`로.

## 흔한 관용구 교정 (빠른 표)

| 비관용 | 관용 | 이유 |
|---|---|---|
| `if len(x) > 0:` | `if x:` | falsy 프로토콜 |
| `for i in range(len(xs)): xs[i]` | `for x in xs:` / `enumerate(xs)` | 인덱스 버그 차단 |
| `d.keys()`로 in 검사 | `if k in d:` | 동일 의미, O(1) |
| `dict 수동 누적` | `collections.Counter`/`defaultdict` | 의도가 이름에 |
| `os.path.join(...)` 문자열 | `pathlib.Path` 연산 | OS 차이 흡수(Windows!) |
| 임시 변수 swap | `a, b = b, a` | 튜플 언패킹 |
| getter/setter 메서드 | `@property` (필요해질 때만) | 자바 관성 탈피 |

## 타입힌트 심화 (SKILL.md 정량 기준의 연장)

- 입력은 너그럽게, 출력은 구체적으로: 매개변수 `Iterable[str]`/`Sequence[str]`, 반환 `list[str]`.
- `Optional[X]`보다 `X | None`(3.10+). None 반환은 "없음이 정상 흐름"일 때만 — 비정상이면 예외를 던진다.
- `TypedDict`는 외부 JSON 경계용, 내부 도메인 객체는 dataclass — 경계에서 변환해 들어온다.
- `Any`는 전염된다: 한 번 Any면 그 하류 전부 무검사. 어쩔 수 없는 곳엔 `cast()` + 이유 주석.
