# dev-go evidence — 장애·실증 사례

## 1. Discord Read States — Go GC 스파이크로 서비스 이식 (2020)

- **무슨 일**: Read States 서비스(누가 어떤 채널을 어디까지 읽었나 — 초당 수백만 갱신)에서 약 2분 간격의 규칙적 레이턴시 스파이크. 출처: Discord 공식 엔지니어링 블로그 "Why Discord is switching from Go to Rust" (2020).
- **근본 원인**: 수백만 엔트리 LRU 캐시(장수 객체 거대 힙)를 GC가 주기적으로 전체 스캔. 당시 Go GC는 최소 2분마다 강제 사이클. 캐시 축소 → GC 단축but miss 증가로 DB 부하 — 구조적 트레이드오프.
- **해결**: Rust 이식(GC 없음, 소유권 기반 즉시 해제). 스파이크 소멸 + 평균 레이턴시도 개선.
- **이 스킬과의 연결**: 안티패턴이 아니라 **한계 섹션의 실증** — Go 코드가 완벽해도 워크로드-런타임 부정합은 코드로 못 푼다. 절차: ① pprof로 GC 비중 실측(`go tool pprof`, `GODEBUG=gctrace=1`) ② GOGC·GOMEMLIMIT 튜닝 시도 ③ 그래도 안 되면 언어 재검토. 순서를 건너뛴 "Rust 가자"는 카고컬트.
- **시효 주의**: Go 1.26의 Green Tea GC 기본 활성화로 대형 힙 마킹 비용이 크게 개선됨 — 2020년 수치를 현재 Go에 그대로 인용하지 말 것(측정이 이긴다).

## 2. Uber goleak — 고루틴 누수의 산업 표준 검출 (실무 관행)

- **무슨 일**: Uber는 수천 개 Go 서비스 운영 중 고루틴 누수가 반복 장애 원인임을 확인하고 테스트 라이브러리 `uber-go/goleak`을 공개. 테스트 종료 시점에 살아있는 비기대 고루틴이 있으면 실패시킨다.
- **전형적 누수 패턴** (goleak이 잡는 것):
  - 수신자 없는 채널에 send 하고 블로킹된 채로 영원히 대기 (`ch <- result` 후 호출자가 타임아웃으로 떠남)
  - `time.Tick()` 사용 (멈출 수 없음 — `time.NewTicker` + `defer t.Stop()`이 정답)
  - context 취소를 select에 안 넣은 무한 루프 워커
- **사용법**: `defer goleak.VerifyNone(t)` 한 줄을 동시성 테스트에 추가. 패키지 전체는 `TestMain`에서 `goleak.VerifyTestMain(m)`(`t.Parallel()` 케이스가 있으면 미완료 테스트와 누수 구분 불가라 이쪽 권장).
- **이 스킬과의 연결**: 안티패턴 1의 검증 도구. "누수는 코드 리뷰로 못 잡는다 — 테스트 시점 단언으로 잡는다."

## 3. concurrent map writes — 프로덕션 즉사 패턴 (Go 런타임 명세)

- **무슨 일**: 고루틴 2개가 같은 map에 동시 쓰기 → `fatal error: concurrent map writes`. recover 불가능한 런타임 강제 종료(panic이 아님) — 프로세스 전체가 즉사한다.
- **흔한 진입로**: HTTP 핸들러(요청마다 고루틴)가 패키지 레벨 map 캐시에 락 없이 쓰기. 부하 적을 땐 안 터지다가 트래픽 오르면 확률적으로 전 프로세스 다운.
- **이 스킬과의 연결**: 안티패턴 4. `-race`는 이걸 부하 전에 잡는 유일한 망 — "로컬에서 잘 됐는데"가 통하지 않는 대표 사례.

## 출처 (웹 검증 2026-06)

- Discord 엔지니어링 블로그(2020) "Why Discord is switching from Go to Rust" — https://discord.com/blog/why-discord-is-switching-from-go-to-rust (1차 출처: 2분 강제 GC·LRU 캐시 전체 스캔·캐시 축소 시 p99 악화, 본문 서술과 일치 확인)
- uber-go/goleak (MIT) — https://github.com/uber-go/goleak (1차 출처: `defer goleak.VerifyNone(t)` / 패키지 전체는 `TestMain`에서 `goleak.VerifyTestMain(m)`. `t.Parallel()` 테스트는 VerifyTestMain 권장)
- Green Tea GC(거대 힙 마킹 개선) — https://go.dev/blog/greenteagc · https://go.dev/doc/go1.26 (1차 출처: Go 1.25 실험→**1.26 기본 활성화**, 실사용 프로그램에서 GC 오버헤드 10–40% 감소, 마킹이 GC 비용의 ~90%. opt-out=`GOEXPERIMENT=nogreenteagc`, 1.27에서 제거 예정)

수치·동작은 2026-06 기준, GC 세부는 Go 버전 따라 변함.
