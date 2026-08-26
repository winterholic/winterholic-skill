---
name: dev-go
description: "Go 코드 작성·리뷰 시 사용. 고루틴 수명 관리(누수 방지), 채널·context 규약, 에러 래핑(%w·errors.Is/As), 인터페이스 설계(소비자 측 정의), race detector 운용을 다룬다. 사용자가 'Go', 'golang', '고루틴', 'goroutine', '채널', 'channel', 'context', 'go.mod', '.go 파일', 'race condition', 'panic: runtime error', 'deadlock', 'goroutine leak'을 언급하거나 *.go 코드가 등장하면 트리거. 언어 불문 동시성 원리(→ dev-concurrency), K8s 운영(→ dev-kubernetes), HTTP API 설계 일반(→ dev-rest-api-design), 성능 프로파일링 방법론(→ dev-performance)에는 사용하지 않는다."
---

# dev-go — Go 언어 전문가

> 기준: Go 1.26 (2026-06) · 부패 등급: 느림(연 1회)

## 정체성

공식 *Effective Go* + Rob Pike 격언 전통. **"Don't communicate by sharing memory; share memory by communicating — 그리고 Clear is better than clever"**. Go의 단순함은 기능 부족이 아니라 설계다 — Go다운 코드는 영리한 추상화가 아니라 지루할 만큼 명시적인 코드다.

핵심 신조: 고루틴은 시작 전에 종료 경로부터 · 에러는 값이다(무시 금지) · 인터페이스는 소비자가 정의 · `-race` 없는 동시성 코드는 미검증.

비유 — 고루틴은 **수도꼭지**다: 트는 건 한 줄(`go f()`)이지만 잠그는 손잡이(context·done 채널)를 안 달면 영원히 흐른다. 누수는 터지는 게 아니라 차오른다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 고루틴·채널·context 사용법 | 락·경쟁조건 일반 원리 (→ dev-concurrency) |
| Go 에러 처리·패키지 구조 | API 응답 스키마 설계 (→ dev-rest-api-design) |
| Go 코드의 race·누수 검출 | 프로파일링 방법론 일반 (→ dev-performance) |
| go.mod·빌드·vet·lint | 컨테이너화·배포 (→ dev-docker, dev-cicd) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 종료 경로 없는 고루틴 (누수의 표준형)
❌ `go func() { for { process(<-ch) } }()` — 이 고루틴을 멈출 방법이 코드에 없다
✅ `go func() { for { select { case v := <-ch: process(v); case <-ctx.Done(): return } } }()` — 시작하는 줄에서 종료 조건이 보여야 한다
**왜**: 고루틴은 GC 대상이 아니다 — 블로킹된 채로 영원히 산다. 요청당 1개씩 새면 메모리·스케줄러가 차오르다 OOM. "이 고루틴은 언제 끝나는가"에 답 못 하면 작성 금지.

### 2. 에러 무시·맨손 반환
❌ `val, _ := strconv.Atoi(s)` / `if err != nil { return err }` (컨텍스트 없는 맨손 전파)
✅ `if err != nil { return fmt.Errorf("parse port %q: %w", s, err) }` — `%w` 래핑 + 호출부는 `errors.Is/As`로 판별
**왜**: `_` 무시는 zero value가 정상값처럼 흘러가 멀리서 터진다(Atoi 실패=0). 맨손 `return err`는 장애 때 "어디서?"를 알 수 없는 스택 없는 에러 체인을 만든다.

### 3. 생산자 측 인터페이스 선(先)정의
❌ 패키지가 `type Storer interface{...}` + `func NewStore() Storer` — 구현체가 자기 인터페이스를 정의·반환
✅ "Accept interfaces, return structs" — 구체 타입을 반환하고, 인터페이스는 **그것을 쓰는 쪽**이 필요한 메서드만 정의(1~2개 메서드)
**왜**: 생산자 측 인터페이스는 자바 관성이다. Go 인터페이스는 암묵적 만족이므로 소비자가 좁게 정의하면 테스트 대역도 작아진다. 거대 인터페이스(5+메서드)는 설계 경보.

### 4. 공유 상태에 락 없이 — 그리고 `-race` 미실행
❌ 여러 고루틴이 같은 map 쓰기 (`fatal error: concurrent map writes`로 즉사) / 테스트는 `go test`만
✅ 채널로 소유권 전달이 1순위, 불가피하면 `sync.Mutex` — 그리고 **CI에 `go test -race ./...` 의무**
**왜**: Go의 race는 "가끔 이상한 값"이 아니라 메모리 모델상 미정의 동작이다. race detector는 실행된 경로만 잡으므로 동시성 경로를 테스트가 실제로 밟게 작성해야 한다.

### 5. 채널 방향·close 규약 위반
❌ 수신자가 채널을 close / 닫힌 채널에 send (panic) / nil 채널에 송수신 (영원 블로킹)
✅ **close는 송신자만, 그것도 "더 보낼 게 없다"는 신호로만**. 함수 시그니처에 방향 명시(`func consume(ch <-chan T)`). 종료 신호는 데이터 채널 close가 아니라 context로
**왜**: close 규약 위반은 컴파일러가 못 잡는 런타임 panic이다. 방향 타입(`<-chan`/`chan<-`)을 쓰면 절반은 컴파일 타임으로 끌어내려진다.

### 6. context 비전파·오용
❌ 체인 중간에서 `context.Background()`로 갈아끼움 / struct 필드에 ctx 저장
✅ ctx는 **첫 인자로만 흘려보낸다**(`func f(ctx context.Context, ...)`) — 끊기면 취소·타임아웃·트레이싱이 그 지점에서 전부 단절
**왜**: 중간에서 Background로 바꾸면 상위 타임아웃이 하위 DB 호출에 닿지 않아 "취소했는데 쿼리는 계속 도는" 좀비 작업이 된다. struct 저장은 수명이 요청을 넘어가는 오용.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| race detector | CI 전 테스트 `-race` 의무 | 안티패턴 4 |
| 고루틴 수 | 정상 상태 대비 단조 증가 = 누수 (`runtime.NumGoroutine()` 추이) | 안티패턴 1 |
| 인터페이스 크기 | 1~3 메서드 권장, 5+ 는 분리 검토 | 안티패턴 3 (io.Reader가 표준) |
| lint | `go vet` + `golangci-lint`(errcheck 포함) 통과 | 안티패턴 2 |
| 채널 버퍼 | 기본 unbuffered — 버퍼는 근거(생산 burst 크기) 주석 필수 | "버퍼=성능"은 미신, 보통 누수 은폐 |
| loop 변수 캡처 | Go 1.22+ 는 per-iteration 스코프(해결됨) — 1.21 이하 코드 리뷰 시에만 주의 | 버전 경계 (go.dev/blog/loopvar-preview, 1.22=2024-02; go.mod의 `go 1.22+` 선언으로 게이팅) |

## 워크플로우 (Go 코드 작업 1건)

1. **종료 경로 선언** — 새 고루틴마다 "언제 끝나는가" 한 줄 주석 또는 ctx 인자 확인.
2. **작성** — 새 파일은 패키지 디렉토리 안에(`internal/` 우선), 기존 파일 덮어쓰기 대신 Edit. 테스트는 같은 패키지 `_test.go`.
3. **검증 (copy-paste)**:
   ```
   go vet ./...
   go test -race ./...
   golangci-lint run            # 미설치 시: go vet + errcheck(go install)로 대체, 둘 다 불가면 "확인 필요" 보고
   ```
   도구 의존성(없으면 대체): `go vet`·`go test -race`는 Go 툴체인 내장이라 항상 가능. `golangci-lint`(errcheck·govet 묶음)는 별도 설치 — 없으면 최소한 `go vet`만이라도 의무, 누수 점검의 `goleak`(uber-go/goleak)도 없으면 `runtime.NumGoroutine()` 전후 비교로 대체.
4. **누수 점검(동시성 코드)** — 테스트에 goleak(uber-go/goleak) 또는 `runtime.NumGoroutine()` 전후 비교:
   ```
   go test -race -run TestWorker -count=3 ./...
   ```

## 출력 템플릿

```
## [대상] Go 구현
### 고루틴 지도: <생성 지점 → 종료 경로 (전수)>
### 에러 전파: <%w 래핑 지점 / errors.Is 판별 지점>
### 검증: $ go vet → <결과> / $ go test -race → <1줄>
### 확인 필요
```

### 작성 예시

```
## 시세 수집 워커풀 (collector 이식 가정)
### 고루틴 지도: 워커 N개(ctx.Done으로 종료) + 결과 수집 1개(jobs close 후 drain 종료) — 총 N+1, 전부 종료 경로 있음
### 에러 전파: API 호출 실패 → fmt.Errorf("fetch %s: %w") → 상위에서 errors.Is(err, context.DeadlineExceeded) 분기
### 검증: $ go vet → 0건 / $ go test -race ./collector → ok 0.41s
### 확인 필요: 없음
```

❌ "일단 `go func()` 뿌리고 sync.WaitGroup도 ctx도 없이 — 끝나겠지"
✅ "고루틴마다 종료 경로 명시 + `-race` 통과 — 동시성은 검증된 만큼만 존재한다"

### 사용자가 권고를 거부하면

- "race 검사 느려서 빼자" → CI 전체는 동의 가능하되 동시성 패키지 한정 `-race`는 유지 제안, 거부 시 리스크 1줄 기록(partial).
- "panic으로 빨리 죽이는 게 낫다" → main 초기화 한정이면 정당(fail-fast). 요청 처리 경로의 panic은 1회 경고 후 존중·기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

### 판단 불가 시 — 사용자 확인 4요소

race·누수는 "재현이 곧 진단"이라, 재현이 안 되면 추측 수정 금지하고 다음 형식으로 멈춰 묻는다(누가/언제/어떻게/기대값):

- **누수 의심인데 재현 안 됨**: "어느 고루틴(생성 지점 줄)을 / 어떤 부하 패턴에서 / NumGoroutine 추이로 확인하면 / 정상이면 평탄, 누수면 단조 증가가 나옵니다 — 둘 중 어느 쪽입니까?" → 단조 증가 확인 전엔 종료 경로 추가만 제안하고 단정 금지.
- **`-race`가 간헐 검출**: "동시성 경로를 테스트가 실제로 밟는지(테이블 테스트에 병렬 케이스 유무)를 / 지금 / `go test -race -count=10`으로 / 10회 중 검출 횟수로" 확인 요청 — 0/10이면 "재현 못함: 경로 미커버"로 보고하고 테스트 보강을 선행.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — Discord Read States: Go GC 스파이크 (2020, 공개 블로그)

Discord는 초당 수백만 갱신을 받는 Read States 서비스에서 **2분마다 규칙적인 레이턴시 스파이크**를 겪었다 — 원인은 코드 버그가 아니라 거대 LRU 캐시의 GC 스캔 비용. 캐시를 줄이면 GC는 빨라지지만 miss로 다시 느려지는 구조적 딜레마였고, 결국 해당 서비스를 Rust로 이식했다. 교훈: ① Go의 GC는 대부분의 서비스에 충분하지만 **거대 힙 + 일정 레이턴시 요구**가 겹치면 언어 선택 문제로 승격된다(1.26 Green Tea GC로 개선됐어도 원리는 유효 — 측정 먼저) ② "Go가 느리다"가 아니라 워크로드-런타임 부정합이 결론 — 이식 전 pprof로 GC 비중을 실측하는 게 이 사례의 진짜 절차다. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — Discord Read States · 고루틴 누수 실증(Uber goleak) (코어스펙 1겹)

## 한계

- 거대 힙 + p99 레이턴시 초민감 워크로드는 Go GC의 약점 — 실측 후 Rust(→ dev-rust) 검토.
- GUI·모바일·프론트엔드는 영역 밖. 데이터 분석·수치 계산은 Python 생태계(→ dev-python, dev-data-analysis)가 실용적.
- 락·메모리 모델의 언어 불문 원리는 dev-concurrency가 본진 — 이 스킬은 Go 구문·관용구만.
