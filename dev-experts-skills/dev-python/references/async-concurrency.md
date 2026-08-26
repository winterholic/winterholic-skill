# async·동시성 — 모델 선택 기준과 asyncio 함정 (SKILL.md 비중복 심화)

## 동시성 모델 선택 (먼저 이 표 — 모델을 잘못 고르면 이후 전부 헛수고)

| 작업 성격 | 선택 | 이유 |
|---|---|---|
| I/O 대기 다수 + 연결 수천 (API 폴링, 웹소켓) | asyncio | 스레드 수천 개는 메모리·스케줄링 비용, 코루틴은 싸다 |
| I/O 대기 소수 (~수십) + 기존 동기 코드베이스 | `ThreadPoolExecutor` | async 전염(아래) 없이 충분히 빠름 |
| CPU 바운드 (파싱·수치 계산) | `ProcessPoolExecutor` | GIL 때문에 스레드·async로는 코어 1개만 쓴다 |
| 단순 순차로 충분 | 동시성 없이 | 동시성은 공짜가 아니다 — 디버깅 난도가 비용 |

- **GIL의 실제 의미**: "한 시점에 바이트코드를 실행하는 스레드는 1개". I/O 대기 중엔 GIL을 놓으므로 **I/O 바운드 스레딩은 유효**하다. "파이썬 스레드는 무용"은 오해 — CPU 바운드에서만 무용.
- 3.13+ free-threaded 빌드는 실험 단계 취급(확인 필요: 사용 시점의 안정화 여부). 설계를 그것에 걸지 않는다.

## async 전염성 — 도입 전 알아야 할 비용

`await`는 `async def` 안에서만 가능 → async를 한 곳에 도입하면 **호출 경로 전체**가 async가 되거나 경계가 필요하다.

- 동기 → 비동기 경계: `asyncio.run(main())` (진입점 1곳).
- 비동기 → 동기(블로킹) 경계: `await asyncio.to_thread(blocking_fn, arg)` (3.9+) — requests·무거운 파일 I/O·sleep을 루프 밖으로.
- 비동기 → CPU 작업: `loop.run_in_executor(ProcessPoolExecutor(), fn)`.
- 부분 도입이 어중간하면 차라리 전부 동기 + 스레드풀이 단순하다 — 수집기 규모(~수십 동시 요청)에선 보통 그쪽이 정답.

## asyncio 함정 카탈로그 (SKILL.md #2의 각론)

1. **await 누락** — `fetch()`만 쓰고 `await fetch()`를 안 쓰면 코루틴 객체만 만들어지고 실행 안 됨. `RuntimeWarning: coroutine 'fetch' was never awaited`가 그 신호 — 경고를 에러로 승격해 잡는다: `python -W error::RuntimeWarning`.
2. **태스크 가비지 컬렉션** — `asyncio.create_task(job())` 결과를 변수에 안 잡으면 **실행 중 GC로 사라질 수 있다**(공식 문서 명시). 태스크 집합에 보관 + done 콜백으로 제거가 관용구.
3. **fire-and-forget 예외 증발** — 태스크 안 예외는 await/결과 조회 전까지 조용하다. `task.add_done_callback`에서 `task.exception()` 로깅, 또는 `asyncio.TaskGroup`(3.11+)으로 구조화 — 하나 실패 시 전체 취소 + 예외 전파.
4. **타임아웃 없는 await** — 외부 I/O는 `asyncio.wait_for(op(), timeout=10)` (3.11+은 `asyncio.timeout`). HTTP 타임아웃 의무(SKILL.md 정량 기준)의 async 판.
5. **세마포어 없는 무한 동시** — `gather(*[fetch(u) for u in urls_10000])`는 동시 1만 연결 = 상대 서버 공격 + 로컬 소켓 고갈. `asyncio.Semaphore(20)` 게이트가 관용구 (20은 출발점 — 상대 API rate limit 문서가 이긴다).
6. **이벤트 루프에서 디버깅 어려움** — 개발 중엔 `asyncio.run(main(), debug=True)`: 블로킹 100ms+ 콜백·미await 코루틴을 로그로 찍어준다 (100ms는 asyncio 기본 임계 — `loop.slow_callback_duration`으로 조정).

## 스레드 공유 상태 최소 규칙

- 큐(`queue.Queue`)로 소유권을 넘기는 설계가 락보다 먼저다 — "공유하지 말고 전달하라".
- 락이 불가피하면 `with lock:` (컨텍스트 매니저)만 — acquire/release 수동 호출은 예외 시 데드락.
- `threading.local()`은 요청 컨텍스트 보관용이지 전역 상태 정당화 수단이 아니다.

## 검증 명령

```
python -W error::RuntimeWarning -m pytest -x -q     # 미await 코루틴을 실패로
python -X dev <entry.py>                            # dev 모드: asyncio debug 포함 각종 경고 활성
```
