# dev-kotlin evidence — 실증 사례

## 1. 플랫폼 타입 NPE — "널 안전 언어의 널 구멍" (상호운용 경계 실증)

- **무슨 일**: 자바 메서드 반환값은 Kotlin에서 플랫폼 타입(`String!`) — 널 검사를 강제하지 않고 개발자 신뢰로 통과시킨다. 어노테이션 없는 자바 라이브러리·레거시 코드 경계에서 널이 흘러들어 깊숙한 곳에서 NPE — "Kotlin인데 왜"의 1순위 원인. 크래시 리포트 분석 글들이 반복 확인하는 패턴.
- **방어**: ① 자바 경계 수신 즉시 널 계약 확정(`?: error("api X returned null")` 또는 nullable로 받기) ② `@Nullable/@NotNull` 어노테이션 있는 라이브러리 우선(컴파일러가 인식) ③ 경계 모듈을 얇게 분리해 검증 지점 집약.
- **교훈**: 널 안전은 Kotlin 코드 안에서만 완결된다 — 경계는 입국 심사대처럼 다룬다(dev-web-scraping 적재 검증과 동형 원리).

## 2. GlobalScope 누수 — "화면은 닫혔는데 작업은 계속" (구조적 동시성 부재 실증)

- **무슨 일**: 안드로이드·서버 공통 반복 사고 — GlobalScope.launch로 시작한 네트워크 폴링·업로드가 화면 이탈/요청 종료 후에도 계속 실행: 배터리·메모리 소모, 죽은 UI 참조 접근 크래시, 서버에선 응답 없는 요청의 작업이 자원 점유. 예외는 핸들러 없이 증발해 "가끔 안 되는데 로그가 없어요".
- **공식 대응**: Kotlin 팀이 GlobalScope를 `@DelicateCoroutinesApi`로 격리(opt-in 강제)한 것 자체가 사고 빈도의 증거다.
- **올바른 골격**: 수명 주인이 스코프를 소유(`val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)`) + 종료 시 `scope.cancel()` — "이 코루틴을 누가 죽이나"에 항상 답이 있게. 안드로이드는 viewModelScope/lifecycleScope가 그 답의 기성품.

## 3. runBlocking ANR·데드락 — sync-over-async의 코틀린판 (반복 실증)

- **무슨 일**: ① 안드로이드 메인 스레드에서 runBlocking { 네트워크 } → 5초 초과 시 ANR(Application Not Responding) 다이얼로그 ② 코루틴 안에서 runBlocking + 같은 디스패처 대기 → 데드락(제한된 스레드풀에서 자기 완료를 기다리는 구조) — dev-csharp .Result 데드락과 동일 골격의 코틀린 변형.
- **runBlocking의 합법 영역**: main 함수·@Test(또는 runTest)·동기 전용 레거시 인터페이스 구현의 최후 경계 — 그 외에서 보이면 suspend 전파를 회피한 신호다.
- **탐지**: `grep -rn "runBlocking" src/main/` — main 진입점 외 검출분은 전수 리뷰. 안드로이드는 StrictMode가 메인 스레드 IO를 잡아준다.

> 출처(2026-06, Kotlin 2.4 기준 — 웹 확인 완료):
> - 플랫폼 타입·널 안전: Kotlin 공식 문서 https://kotlinlang.org/docs/null-safety.html (자바 상호운용 시 `Type!` 플랫폼 타입 정의를 명시한 1차 출처)
> - GlobalScope = `@DelicateCoroutinesApi`: API 레퍼런스 https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-global-scope/ + https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-delicate-coroutines-api/ (opt-in 강제·취소/예외 핸들러 부재를 공식 명시. Coroutines 1.5.0(2021-05)부터 delicate 표기)
> - 구조적 동시성·예외 처리: https://kotlinlang.org/docs/coroutines-basics.html · https://kotlinlang.org/docs/exception-handling.html
> - 안드로이드 ANR(메인 스레드 5초 초과 시 ANR): https://developer.android.com/topic/performance/vitals/anr · 진단 https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs
> - 커뮤니티 크래시 분석은 패턴 빈도의 보조 근거(1차 아님).
