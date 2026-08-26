# dev-rust evidence — 장애·실증 사례

## 1. Cloudflare 글로벌 장애 — Bot Management unwrap panic (2025-11-18)

- **무슨 일**: 2025-11-18 11:20 UTC 시작, 약 6시간(2019년 이래 최장) Cloudflare 코어 프록시가 광범위 5xx 반환 — 인터넷 트래픽의 상당 비율이 영향. 출처: Cloudflare 공식 포스트모템 https://blog.cloudflare.com/18-november-2025-outage/ (2026-06 웹 확인).
- **근본 원인 체인**: ClickHouse 권한 변경(explicit grant 점진 롤아웃) → 11:05 이후 메타데이터 쿼리가 r0 스키마 중복 행 반환 → Bot Management feature 파일 행 수 2배↑ → ML feature 한도(런타임 **200개**, 평소 사용 ~60개) 초과 → **신규 FL2 프록시(Rust)** 코드가 에러를 처리 않고 체이닝하다 `.unwrap()` → panic → 5xx 반복.
- **공식 패닉 메시지(원문 인용)**: `thread fl2_worker_thread panicked: called Result::unwrap() on an Err value` — 포스트모템에 그대로 실림. (구형 FL 프록시는 이 경로를 깔끔히 처리해 panic은 없었으나 bot score가 0으로 떨어져 별도 피해 발생 — 같은 데이터, 다른 실패 모드.)
- **5분 플래핑**: feature 파일이 5분마다 재생성되는데, 쿼리가 업데이트된 클러스터 노드에 닿을 때만 불량 파일 생성 → 정상/불량이 번갈아 전파되어 회복·재실패 반복, 원인 추적을 어렵게 함. 전 노드 업데이트 후 완전 실패로 고정.
- **이 스킬과의 연결**: 안티패턴 1의 결정판. 주목할 점 3가지:
  1. 입력은 외부 사용자 데이터가 아니라 **자사 파이프라인이 만든 설정 파일** — "우리가 만드니 신뢰"가 무너진 사례. 신뢰 경계는 조직도가 아니라 프로세스 경계다.
  2. 올바른 실패 모드는 "새 파일 거부 + 직전 정상본 유지(fail-open to last-known-good)"였다 — panic은 가장 나쁜 선택지였다.
  3. Rust였기에 메모리는 안전했다 — 그러나 가용성은 별개 축이다. "Rust = 안 죽는다"는 범주 착오.
- **검출 가능했나**: `clippy::unwrap_used`는 **allow-by-default인 restriction 군**이라 평범한 `cargo clippy -- -D warnings`로는 안 잡힌다 — `[lints.clippy] unwrap_used="deny"`(또는 `#![deny(clippy::unwrap_used)]`)로 명시 opt-in해야 컴파일 단계에서 강제 검토된다. 코어 경로 crate에 이 lint를 켜는 것이 본 스킬 권고. (Clippy 공식: restriction 군은 통째로 켜지 말고 cherry-pick 하라고 명시.)

## 2. RefCell 런타임 panic — "컴파일은 됐는데 already borrowed" (반복 실증 패턴)

- **무슨 일**: `Rc<RefCell<T>>`로 차용 검사를 런타임에 미룬 코드가 콜백·재진입 경로에서 `BorrowMutError: already borrowed` panic. GUI·게임루프·이벤트 핸들러에서 반복 보고되는 패턴(Rust 포럼·이슈 트래커에 다수).
- **메커니즘**: A가 `borrow_mut()` 보유 중 콜백이 같은 셀을 다시 `borrow()` — 컴파일러였다면 거부했을 코드가 런타임 폭탄이 된 것.
- **이 스킬과의 연결**: 안티패턴 4. RefCell 도입 시점에 "재진입 경로가 없는가"를 물어야 하며, 답을 모르면 소유 구조 재설계가 정답.

## 3. tokio 블로킹 — "async인데 p99만 튄다" (tokio 공식 경고)

- **무슨 일**: tokio 메인테이너 Alice Ryhl의 표준 해설("Async: What is blocking?", https://ryhl.io/blog/async-what-is-blocking/)이 명시하는 사고: async는 **협력적 스케줄링**이라 한 태스크가 `.await` 없이 오래 점유하면 같은 스레드의 다른 태스크가 못 돈다 → "특정 기능이 아니라 전체 p99 악화"로 나타나 추적이 어렵다.
- **수치 기준(웹 확인 2026-06)**: Ryhl 권고는 "`.await` 사이 **10~100µs**"가 경험칙(테일 레이턴시 최적화 기준). spawn_blocking 전용 풀은 상한 **~500스레드**라 블로킹 IO(파일시스템·diesel 같은 동기 DB)에 적합하지만, 코어 수보다 스레드가 많아 **무거운 CPU-bound 계산엔 부적합** → 그쪽은 **rayon**이나 별도 런타임 권고. (정확 임계는 워크로드 의존.)
- **이 스킬과의 연결**: 안티패턴 5. 진단 명령: `tokio-console`로 태스크별 poll 시간 관찰, 또는 의심 지점에 `tracing` span.

> 출처(2026-06 웹 확인): Cloudflare 공식 포스트모템 https://blog.cloudflare.com/18-november-2025-outage/ · Alice Ryhl "Async: What is blocking?" https://ryhl.io/blog/async-what-is-blocking/ · Clippy 공식 lints 문서(restriction 군 allow-by-default) https://doc.rust-lang.org/stable/clippy/lints.html · Rust 커뮤니티 이슈 집적.
