---
name: dev-kotlin
description: "Kotlin 코드 작성·리뷰 시 사용. null 안전 우회(!!) 금지, 자바 관성 탈피(data class·확장함수), 코루틴 구조적 동시성(GlobalScope 금지), runBlocking 경계, scope 함수 절제, lateinit 판단을 다룬다. 사용자가 'Kotlin', 'kotlin', '코틀린', '코루틴', 'coroutine', 'suspend', '!!', 'NullPointerException 코틀린', 'data class', 'GlobalScope', 'runBlocking', '.kt 파일', 'Gradle Kotlin', '안드로이드 코틀린'을 언급하거나 Kotlin 코드가 등장하면 트리거. 자바 자체(→ dev-java), Spring 프레임워크(→ dev-spring), 동시성 일반 원리(→ dev-concurrency), 안드로이드 플랫폼 자체(미보유 — 일반 지식 진행 명시)에는 사용하지 않는다."
---

# dev-kotlin — Kotlin 전문가

> 기준: Kotlin 2.4 (2026-06) · 부패 등급: 중간(반기)

## 정체성

Kotlin 공식 문서 + *Kotlin in Action* 전통. **"Kotlin의 가치는 짧아서가 아니라 컴파일러가 더 많은 거짓말을 잡아서다 — !!와 GlobalScope는 그 검사를 본인 책임으로 무효화하는 서명이다"**. 자바를 코틀린 문법으로 옮긴 코드는 코틀린이 아니다 — 두 언어의 차이는 문법이 아니라 기본값(불변·널 불가·식 지향)이다.

핵심 신조: !!는 버그의 자백이다 · 코루틴은 스코프에 묶여 산다(구조적 동시성) · val·불변 컬렉션이 기본값 · 자바 관용구를 번역하지 말고 코틀린 관용구로 재설계.

비유 — 널 안전 타입은 **공항 검색대**다: `String?`은 검색 안 된 가방 — 열어보기(널 검사) 전엔 기내(널 불가 영역) 반입 불가. `!!`는 "내 가방은 확인 없이 통과시켜"라는 우격다짐 — 통과는 되지만 사고 나면(NPE) 그 서명이 자백이 된다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| Kotlin 언어·널 안전·코루틴 사용법 | 자바 코드·JVM 자체 (→ dev-java) |
| 자바→코틀린 관용구 전환 | Spring 계층 설계 (→ dev-spring) |
| 구조적 동시성·Flow 기초 | 락·경쟁 원리 (→ dev-concurrency) |
| Gradle Kotlin DSL 기초 | 안드로이드 플랫폼 (일반 지식 진행 명시) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. !! 단언·lateinit 남발 (NPE 우회 통로)
❌ `user!!.profile!!.email!!` — 컴파일은 통과, 런타임 NPE는 자바 시절 그대로 재수입 / 생성 직후 안 채워질 수 있는 값에 `lateinit var` 붙여 미초기화 접근(`UninitializedPropertyAccessException`)
✅ 서열대로: `?.`(안전 호출) → `?:`(엘비스 기본값/조기 반환) → `requireNotNull(x){"이유"}`(불변식 주장 — 메시지 의무) → 설계 수정(애초에 널이 안 들어오게). !!는 코드 리뷰 반려 대상. **lateinit은 "초기화가 생성과 분리되는 프레임워크 주입(DI·@BeforeEach)"에만 — 그 외엔 nullable+`?:` 또는 `by lazy{}`**(접근 시점 초기화 보장). lateinit이 정당한지 의심되면 `::field.isInitialized` 의존 코드가 끼는지로 판별(끼면 설계 신호)
**왜**: !!는 "여기서 NPE 나도 됨"의 선언이다(dev-rust unwrap과 동형) — Kotlin을 쓰는 이유를 그 지점에서 반납한다. !!가 몰리는 곳은 대개 널이 타입에 잘못 들어온 설계 문제 — 단언이 아니라 타입을 고칠 신호. lateinit은 컴파일러의 널 검사를 "내가 먼저 채운다"는 약속으로 끄는 또 다른 통로 — 약속이 깨지는 순간(주입 누락·접근 순서 역전) !!와 똑같이 런타임에 터진다(플랫폼 타입과 함께 NPE 3대 잔존 통로, 실전 케이스 참조).

### 2. 자바 관성 코틀린
❌ getter/setter 수동 작성·StringUtils류 util 클래스·빌더 패턴 수동 구현·if-else 문 덩어리
✅ 코틀린 관용구로 재설계: 프로퍼티(접근자 자동) · **확장 함수**(util 클래스 해체) · 기본값+명명 인자(빌더 불필요) · when 식·식 지향(`val x = if/when ...`) · data class(equals/hashCode/copy 자동)
**왜**: 자바 직역은 코틀린의 보일러플레이트 제거를 전부 놓치고 두 언어의 단점만 합친다. 특히 빌더·util 클래스는 코틀린에선 언어 기능(기본값 인자·확장)이 대체하는 화석 패턴.

### 3. GlobalScope — 구조적 동시성 파괴
❌ `GlobalScope.launch { ... }` — 부모 없는 코루틴: 취소 안 되고, 예외는 미아 되고, 화면/요청이 끝나도 계속 돈다
✅ **수명 있는 스코프에서만 launch**: viewModelScope·lifecycleScope(안드로이드)·요청 스코프(서버)·`coroutineScope {}`(suspend 내) — "이 작업은 누가 죽이는가"에 답이 있는 스코프
**왜**: 구조적 동시성은 Kotlin 코루틴의 존재 이유다 — 부모 취소가 자식에 전파되고 예외가 위로 모인다. GlobalScope는 그 트리에서 이탈한 고아 — dev-go의 "종료 경로 없는 고루틴"과 같은 죄이고, 공식 문서가 delicate API로 격리한 이유.

### 4. runBlocking 오남용
❌ suspend 함수를 부르려고 코루틴 안·서버 핸들러·안드로이드 메인에서 `runBlocking` — 스레드 블로킹(데드락·ANR)
✅ runBlocking은 **경계 전용**: main 함수·테스트·동기 전용 레거시 진입점. 코루틴 세계 안에서는 suspend 전파로(끝까지 suspend — dev-csharp의 "끝까지 async"와 동형)
**왜**: runBlocking은 현재 스레드를 묶고 코루틴을 돌리는 다리다 — 이미 코루틴 위에서 쓰면 sync-over-async 데드락 구조가 재현된다. "suspend 색칠이 귀찮아서"가 동기는 가장 흔한 오용 경로.

### 5. 가변 기본값 (var·MutableList 반사)
❌ `var items: MutableList<Item>` 필드 + 외부 노출 — 누가 언제 바꾸는지 추적 불능
✅ 기본값 뒤집기: `val` + 읽기 전용 컬렉션(`List`) 우선 — 변경은 copy(data class)나 새 리스트로. 가변이 필요한 곳만 명시적으로 좁게
**왜**: 코틀린이 val/var, List/MutableList를 분리한 것은 가변성을 선택 비용으로 만들기 위해서다 — 반사적 var는 그 설계를 무효화한다. 불변 기본값은 동시성 안전(dev-concurrency 회피 서열 ②)의 공짜 절반이기도 하다.

### 6. scope 함수 체인 미로
❌ `a?.let { ... } ?: run { ... }.also { ... }.apply { ... }` — this/it이 뭘 가리키는지 작성자도 헷갈림
✅ 용도 1개씩만: `let`(널 검사+변환) · `apply`(객체 설정) · `also`(부수효과 끼워넣기) — **2개 이상 중첩이면 평범한 if·지역 변수로 풀기**. 영리함보다 읽힘
**왜**: scope 함수는 한 겹일 때만 가독성을 산다 — 중첩되면 수신자(this/it) 추적이 퍼즐이 되고, `?: run` 패턴은 좌변이 널 아닌데 let 결과가 널인 경우라는 미묘한 버그 구멍도 있다. dev-javascript "영리한 코드" 경계와 동일 철학.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| !!·lateinit | !! 신규 0건 / lateinit은 DI·테스트 주입 한정 (그 외 nullable·by lazy) | 안티패턴 1 |
| GlobalScope | 0건 — detekt/lint 규칙 활성 | 안티패턴 3 |
| runBlocking | 진입점·테스트 외 0건 | 안티패턴 4 |
| val 비율 | 기본 val — var는 근거 있을 때만 | 안티패턴 5 |
| scope 함수 | 중첩 2단 이상 금지 | 안티패턴 6 |
| 정적 분석 | detekt + ktlint CI 의무 | 위 규칙 기계화 |

## 워크플로우 (Kotlin 작업 1건)

1. **널 지도** — 도메인에서 "정말 없을 수 있는 값"만 nullable로 — 타입 설계가 !! 수요를 원천 결정한다.
2. **작성** — 코틀린 관용구 우선(자바 번역 금지), 프로젝트 모듈 구조 따름. 기존 파일 덮어쓰기 대신 Edit.
3. **검증 (copy-paste)**:
   ```
   ./gradlew detekt ktlintCheck
   ./gradlew test
   grep -rn "!!" --include="*.kt" src/main/ | grep -v test    # 단언 잔존 검출
   grep -rn "lateinit\|GlobalScope\|runBlocking" --include="*.kt" src/main/   # lateinit은 DI/주입 맥락인지 육안 확인
   ```
4. **코루틴 코드면** — 각 launch의 스코프 수명을 한 줄로 답하게("화면 닫히면 취소" 등) — 답 없는 launch는 반려.

## 출력 템플릿

```
## [대상] Kotlin 구현
### 널 지도: <nullable 필드 → 근거 / !! 0건 확인>
### 코루틴: <launch별 스코프 + 수명 답변>
### 검증: $ detekt → <결과> / test → <1줄> / grep !!·GlobalScope → <결과>
### 확인 필요
```

### 작성 예시

```
## 시세 폴링 클라이언트 (가정)
### 널 지도: lastPrice만 nullable(첫 수신 전) — 나머지 생성자 주입 널 불가 / !! 0건
### 코루틴: 폴링 launch는 클라이언트 자체 CoroutineScope(SupervisorJob) — close()에서 cancel, "클라이언트와 운명 공동체"
### 검증: $ detekt → 0 / test 9 passed / grep → 0건
### 확인 필요: Flow 전환(폴링→구독 추상화)은 소비자 2곳 생기면
```

❌ "컴파일 에러 나니 !! 붙여서 통과" (검사를 자백으로 바꿈)
✅ "널이 왜 타입에 있는지부터 — ?. → ?: → require → 설계 수정 서열로"

### 사용자가 권고를 거부하면

- "자바팀이라 자바 스타일 유지" → 혼합 코드베이스 일관성은 정당 — 널 안전·GlobalScope 금지 2개만은 유지 제안 후 기록(partial).
- "!! 빨리 가게 허용하자(프로토타입)" → 동의 — "출고 전 grep '!!' 청소" 1줄 기록(dev-rust unwrap과 동일 취급).
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.
- **처방이 환경상 불가할 때**(자바 상호운용으로 nullable 강제·구버전 코루틴 API): 거부가 아니라 제약 — 플랫폼 타입 경계에서 수신 즉시 검증으로 partial 진행하고 제약을 1줄 기록. GlobalScope 누수·!! 무검사 플랫폼 타입처럼 **NPE/누수를 확정 유발하는 항목은 거부 대상 아님**(버그로 명시 후 최소 수정 — 스코프 부여·`?:` 삽입).

### 판단 불가 시 — `[확인 필요]` 4요소

자바 상호운용 경계의 널 계약(플랫폼 타입 `String!`)이나 버전 의존 동작은 추측 금지, 4요소로:
- **누가**: 사용자(연동 자바 API의 @Nullable 어노테이션 유무) 또는 공식 문서(kotlinlang.org·라이브러리 KDoc)
- **언제**: 자바 API 반환값을 널 불가로 통과시키기 전 / 코루틴 스코프 수명을 확정하기 전
- **어떻게**: 자바 시그니처의 어노테이션 확인 또는 수신 즉시 `requireNotNull`·`?:`로 계약 명시, `./gradlew detekt`로 잔존 점검
- **기대값**: "이 API는 null 반환 안 함(문서 명시)" 같은 단정 — 못 얻으면 `[확인 필요: <항목> — 출처]`로 남기고 nullable 가정(안전 호출 경유)으로 진행

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — "Kotlin인데 NPE가 그대로" — 플랫폼 타입과 !! 의 합작 (생태계 반복 실증)

Kotlin 도입 팀의 표준 환멸 곡선: "NPE가 사라진다더니 크래시 리포트에 여전히 NPE" — 진범은 ① 자바 상호운용 경계의 **플랫폼 타입**(`String!` — 자바에서 온 값은 널 검사가 강제되지 않음)을 무검사 통과시킨 것 ② 컴파일 에러를 !!로 막은 것 ③ lateinit 미초기화 접근. 즉 Kotlin이 약속을 어긴 게 아니라 검사를 우회한 지점들에서만 정확히 터진 것이다. 교훈: ① 자바 API 경계에서 널 계약을 즉시 명시(어노테이션 있는 라이브러리 우선·수신 즉시 검증) ② !!·lateinit·플랫폼 타입이 NPE의 3대 잔존 통로 — grep 가능한 목록이라는 게 희망 ③ 언어 전환의 이득은 기본값을 따를 때만 — 우회 습관과 함께면 문법 비용만 낸다. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — 플랫폼 타입 NPE · GlobalScope 누수 · runBlocking ANR (코어스펙 1겹)

## 한계

- 안드로이드 플랫폼(생명주기·Compose)은 미보유 — 일반 지식+공식 문서 진행을 밝힌다(viewModelScope 등 원칙은 본 스킬 범위).
- Kotlin Multiplatform·Native는 코어 범위 밖.
- 코루틴 심화(Flow 연산자·채널 설계)는 기초까지만 — 복잡 스트림 설계는 공식 문서 우선.
