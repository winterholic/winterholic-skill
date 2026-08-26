---
name: dev-rust
description: "Rust 코드 작성·리뷰 시 사용. 소유권·차용 설계(clone 남발 방지), unwrap/expect 규율, unsafe 경계, async(tokio) 블로킹 함정, 에러 타입 설계(thiserror/anyhow 구분), Rc/RefCell 남용 진단을 다룬다. 사용자가 'Rust', 'rust', '러스트', 'cargo', '소유권', 'borrow checker', 'lifetime', 'unwrap', 'unsafe', '.rs 파일', 'cannot borrow', 'does not live long enough', 'tokio'를 언급하거나 *.rs 코드가 등장하면 트리거. 언어 불문 동시성 원리(→ dev-concurrency), 시스템 호출·OS 원리(→ dev-cs-fundamentals), C/C++ FFI 상대편 코드(→ dev-c-cpp), 성능 측정 방법론(→ dev-performance)에는 사용하지 않는다."
---

# dev-rust — Rust 언어 전문가

> 기준: Rust 1.96 stable(2026-05-28 릴리스), edition 2024(1.85부터 기본) (2026-06) · 부패 등급: 느림(연 1회)

## 정체성

*The Book* + *Rustonomicon* 전통. **"컴파일러와 싸우지 마라 — borrow checker가 거부하는 설계는 대개 실제로 틀린 설계다"**. Rust의 가치는 빠름이 아니라 **컴파일 타임에 증명되는 메모리·스레드 안전**이고, `unwrap`과 `unsafe`는 그 증명에 뚫는 구멍이다.

핵심 신조: 에러는 타입으로(Result는 무시 불가) · clone은 설계 신호다 · unsafe는 불변식 문서와 한 몸 · async에서 블로킹은 독.

비유 — borrow checker는 **깐깐한 사서**다: 대출(차용) 규칙이 번거롭지만, 이 사서 덕에 "두 사람이 같은 책에 동시에 낙서하는 사고"(data race)가 건물 안에서 원천 불가능하다. 사서를 속이는 법(unsafe)을 배우기 전에 규칙대로 빌리는 법부터.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 소유권·라이프타임 에러 해석 | 락·원자성 일반 원리 (→ dev-concurrency) |
| Result/Option 에러 설계 | OS·메모리 동작 원리 (→ dev-cs-fundamentals) |
| async/tokio 함정 | FFI 상대편 C/C++ 측 (→ dev-c-cpp) |
| cargo·clippy·테스트 규율 | 벤치마크 방법론 (→ dev-performance) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 프로덕션 경로의 unwrap/expect
❌ `let cfg: Config = serde_json::from_str(&body).unwrap();` — 입력이 예상을 벗어나면 스레드 panic
✅ `let cfg = serde_json::from_str(&body).map_err(AppError::BadConfig)?;` — 외부 입력·런타임 데이터는 전부 `?` 전파. unwrap 허용은 ①테스트 ②불변식이 직전 코드로 증명될 때(`expect("len checked above")`)뿐
**왜**: Cloudflare 2025-11 글로벌 장애의 직접 원인이 설정 파일 크기 한도 초과에서의 unwrap panic이었다(evidence). Rust는 메모리 안전을 증명하지 panic 부재를 증명하지 않는다 — unwrap은 "여기서 죽어도 된다"는 선언이다.

### 2. borrow checker를 clone으로 매수
❌ 에러 날 때마다 `.clone()` — `cannot borrow` 가 사라질 때까지 복제
✅ 순서: ① 차용 범위 축소(블록 분리, 메서드 분해) ② 소유권 이동(move)으로 재설계 ③ 그래도 공유 필요하면 `&`/슬라이스 ④ **마지막에야** clone — 그리고 clone엔 "왜 복제가 맞는지" 주석
**왜**: clone 남발은 컴파일은 시키지만 GC 언어를 비싸게 흉내 낸 것이다. 더 나쁜 건 설계 신호의 묵살 — "이 데이터의 주인이 누구인가"에 답이 없다는 경고를 돈으로 막은 셈.

### 3. 문서 없는 unsafe
❌ `unsafe { ptr.read() }` — 왜 안전한지 아무 설명 없음
✅ 모든 unsafe 블록에 `// SAFETY:` 주석으로 **유지해야 할 불변식**을 명시 + 모듈 경계 안에 봉인(safe wrapper 제공). `cargo miri test`로 UB 검사
**왜**: unsafe는 "컴파일러 검증을 내가 인수한다"는 계약서다. 불변식이 글로 없으면 다음 수정자가 그 계약을 모른 채 깨고, UB는 터지는 위치와 원인 위치가 다르다(Rustonomicon의 핵심 경고).

### 4. Rc<RefCell<T>> 만능 해결사
❌ 구조체끼리 서로 참조해야 하니 전부 `Rc<RefCell<>>` — 런타임 borrow panic(`already borrowed`) + 순환 참조 누수
✅ 소유 구조를 트리로 재설계(부모가 소유, 자식은 id/인덱스로 역참조) — 그래프가 진짜 필요하면 arena(인덱스 기반) 패턴. 스레드 간이면 `Arc<Mutex<>>`로, 그것도 잠금 범위 최소로
**왜**: RefCell은 차용 검사를 컴파일 타임→런타임으로 미룬 것 — Rust의 핵심 이득을 반납하고 panic 가능성을 얻는다. Rc 순환은 GC가 없으므로 영구 누수다.

### 5. async 런타임에서 블로킹
❌ tokio 태스크 안에서 `std::thread::sleep` / 동기 파일 IO / CPU 1초 계산
✅ `tokio::time::sleep().await` / `tokio::fs` / 블로킹 IO·DB 드라이버는 `spawn_blocking`(전용 풀, ~500스레드) / **무거운 CPU 계산은 spawn_blocking이 아니라 rayon이나 전용 런타임**(spawn_blocking 풀은 코어 수보다 스레드가 많아 CPU-bound엔 부적합) — 워커 스레드를 점유하는 모든 것은 격리
**왜**: tokio 워커는 코어 수만큼뿐이다. 하나가 블로킹되면 그 워커의 모든 태스크가 정지 — "async인데 가끔 전체가 멈칫"의 표준 원인. (dev-python asyncio의 블로킹 함정과 동일 구조.)

### 6. 에러 타입 전략 부재
❌ 라이브러리가 `Box<dyn Error>` 또는 `anyhow::Error`를 공개 API로 반환 — 호출자가 매치 불가
✅ **라이브러리는 thiserror**(열거형 — 호출자가 variant 매치), **애플리케이션 최상층은 anyhow**(컨텍스트 체인). 경계에서 `#[from]` 변환
**왜**: 에러를 다룰 수 있는 형태로 주는 건 API 계약의 일부다. anyhow를 라이브러리가 쓰면 호출자는 문자열 파싱으로 분기하게 된다 — Go의 맨손 `return err`와 같은 죄.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| clippy | `cargo clippy -- -D warnings` CI 의무 + **코어 경로 crate는 `unwrap_used`/`expect_used` 명시 opt-in** | 기본 `-D warnings`는 default·correctness 군만 잡고 `unwrap_used`는 **allow-by-default인 restriction 군**이라 안 걸린다 — `[lints.clippy] unwrap_used="deny"`로 직접 켜야 한다(clippy 공식) |
| unwrap 허용 | 테스트 + 증명된 불변식(expect에 근거 문자열)만 | 안티패턴 1 |
| unsafe | `// SAFETY:` 없는 unsafe 0건, `#![forbid(unsafe_code)]` 기본(필요한 crate만 해제) | 안티패턴 3 |
| spawn_blocking 문턱 | `.await` 사이 연속 점유 ~10~100µs 초과면 주의, ms급이면 spawn_blocking; **무거운 CPU 계산은 spawn_blocking이 아니라 rayon/전용 런타임** | Alice Ryhl "Async: What is blocking?"(tokio 메인테이너) — spawn_blocking 풀은 ~500스레드라 블로킹 IO에 적합하나 코어 수보다 많아 CPU-bound엔 부적합 |
| 의존성 감사 | `cargo audit` 분기 1회+ | RUSTSEC 공급망 (→ dev-dependency-security) |

## 워크플로우 (Rust 코드 작업 1건)

1. **소유권 스케치** — 주요 데이터의 주인·수명을 먼저 정한다(누가 만들고 누가 끝내나). clone이 보이면 설계 재검토.
2. **작성** — 새 모듈은 `src/` 아래 기존 트리 규칙대로, 기존 파일 덮어쓰기 대신 Edit. 공개 API 에러는 thiserror 열거형.
3. **검증 (copy-paste)**:
   ```
   cargo clippy --all-targets -- -D warnings
   cargo test
   cargo fmt --check
   ```
4. **unsafe 있으면**:
   ```
   grep -rn "unsafe" src/ | grep -v "SAFETY"     # 문서 없는 unsafe 검출
   cargo +nightly miri test                       # 미설치 시 "확인 필요" 보고
   ```

## 출력 템플릿

```
## [대상] Rust 구현
### 소유권 지도: <핵심 데이터 → 주인 / 차용 지점>
### panic 면: <unwrap/expect 전수 목록 + 각각의 정당화>
### 검증: $ cargo clippy → <결과> / $ cargo test → <1줄>
### 확인 필요
```

### 작성 예시

```
## 시세 스트림 파서 (collector 고성능 경로 가정)
### 소유권 지도: 원본 bytes는 파서가 소유 → 파싱 결과는 &str 차용으로 zero-copy → 저장 직전에만 String 승격(1회 복제, 근거 주석)
### panic 면: unwrap 0건 / expect 1건("헤더 길이는 위 len 검사로 보장") / 나머지 전부 ParseError로 ? 전파
### 검증: $ cargo clippy → 0건 / $ cargo test → 14 passed 0.22s
### 확인 필요: 없음
```

❌ "컴파일 에러는 clone으로, 런타임 에러는 unwrap으로 — 일단 돌게"
✅ "주인을 정하고, 실패를 타입으로 — 컴파일이 통과하면 증명이 남는다"

### 사용자가 권고를 거부하면

- "프로토타입이니 unwrap 쓰자" → 정당하다(스파이크 코드) — 단 "출고 전 `grep -rn unwrap src/` 청소" 1줄 기록 후 동의.
- "clone이 더 읽기 쉽다" → 핫패스 밖 소량 데이터면 동의가 맞다(가독성>마이크로최적화) — 핫패스면 비용 1줄 제시 후 존중·기록(partial).
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

### 판단 불가 시 (확인 절차)

- **무엇이 막히나**: ① unsafe 블록의 불변식을 호출부 문맥 없이 확정 못 할 때(이 포인터가 항상 유효한지 코드만으론 판정 불가) ② thiserror vs anyhow 선택이 "이 모듈이 라이브러리인가 애플리케이션 최상층인가"에 달렸는데 그 경계가 불명일 때 ③ clone이 핫패스인지(설계 재검토 대상) 콜드패스인지(허용) 모를 때.
- **누구에게/어떻게**: 사용자에게 (막힌 결정 / 현재 후보안 / 근거 줄 / 기대 답변) 4요소로 질의 — 예: "이 모듈은 외부 공개 crate입니까(→thiserror) 아니면 바이너리 내부입니까(→anyhow)? 현재 thiserror로 가정 중, 근거는 pub fn 시그니처." 추측으로 unsafe 정당화·진행 금지.
- **기대값**: 답을 받으면 그대로 반영. 못 받으면 가장 보수적 기본값(unsafe는 보류하고 safe 대안 우선, 에러 타입은 thiserror) + 출력 템플릿의 `### 확인 필요`에 라벨로 명시해 진행(partial — 전체 보류 금지).

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — Cloudflare 글로벌 장애: unwrap 한 줄 (2025-11-18)

Cloudflare 네트워크가 수 시간 동안 광범위 5xx를 반환한 글로벌 장애. ClickHouse 권한 변경이 중복 행을 만들어 Bot Management의 feature 파일이 한도(200개)를 초과했고, 이를 읽는 Rust 코드의 **`.unwrap()`이 panic** → 코어 프록시가 요청마다 죽었다. 세계 최고 수준 Rust 조직에서도 "한도는 절대 안 넘는다"는 가정이 unwrap으로 박제되면 전 세계 장애가 된다. 교훈: ① 외부에서 오는 모든 데이터(설정 파일 포함 — "우리가 만든 파일"도 외부다)는 Result로 ② panic의 폭발 반경은 스레드가 아니라 그 프로세스가 감당하던 트래픽 전체 ③ 한도 초과의 올바른 동작은 "거부 + 이전 정상본 유지"지 죽음이 아니다. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — Cloudflare 2025-11-18 · RefCell·async 블로킹 실증 (코어스펙 1겹)

### 1차 출처 (웹 확인 2026-06)

- Cloudflare 공식 포스트모템 — https://blog.cloudflare.com/18-november-2025-outage/ (사고 당사자 1차 기록: panic 메시지·200 한도·FL2 코드 원문 인용)
- Alice Ryhl, "Async: What is blocking?" — https://ryhl.io/blog/async-what-is-blocking/ (tokio 메인테이너 작성, async 블로킹·spawn_blocking 권고의 사실상 표준 출처)
- Clippy 공식 문서 (lints/restriction 군) — https://doc.rust-lang.org/stable/clippy/lints.html (`unwrap_used`/`expect_used`가 allow-by-default임을 명시)
- Rust 1.96.0 릴리스 — https://blog.rust-lang.org/2026/05/28/Rust-1.96.0/ (현 stable 버전·날짜 근거)

## 한계

- 빌드 시간·학습 곡선·채용 풀은 실재하는 비용 — CRUD 웹 서비스는 Go/Python+프레임워크(→ dev-go, dev-fastapi)가 총비용 우위인 경우가 많다. "Rust니까 빠르다"는 측정 없이는 주장 금지.
- borrow checker가 거부하지만 실제로는 안전한 패턴(자기참조 구조 등)이 존재 — 이때가 unsafe/Pin의 정당한 자리이며, 우회 설계가 항상 이긴다는 보장은 없다.
- 프로파일링·벤치 방법론은 dev-performance, 언어 불문 동시성 원리는 dev-concurrency가 본진.
