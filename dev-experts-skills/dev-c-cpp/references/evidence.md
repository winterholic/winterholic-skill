# dev-c-cpp evidence — 장애·실증 사례

## 1. Heartbleed (CVE-2014-0160) — 길이 검증 한 줄 (공개 분석)

- **무슨 일**: OpenSSL heartbeat 확장 — 클라이언트가 [페이로드 + 길이 선언]을 보내면 서버가 같은 길이를 에코. 구현이 선언 길이와 실제 페이로드 길이를 대조하지 않고 memcpy → 선언 64KB·실제 1B면 힙 인접 64KB가 유출(개인키·세션·비밀번호). 2012 도입~2014 발견, 전 세계 노출.
- **구조 교훈**: ① 네트워크에서 온 길이 값은 적대적 입력 — "프로토콜대로 보냈겠지"는 방어가 아니다 ② C의 무경계 memcpy 위에선 한 줄 실수가 메모리 열람권 — `span`·길이 동반 타입이 실수를 컴파일 구조로 차단 ③ 사후 대응이 생태계 교훈: Core Infrastructure 펀딩·OSS-Fuzz 상시 퍼징 — 새니타이저+퍼저가 이 부류의 표준 그물.

## 2. UB 최적화가 보안 검사를 지웠다 — "코드는 있는데 바이너리엔 없다" (공개 사례)

- **무슨 일**: 고전 실사고 패턴 — `if (ptr + len < ptr)` 식 오버플로 검사(포인터 오버플로는 UB)·`memset` 후 최적화 제거(죽은 저장 제거로 비밀번호 클리어가 사라짐)·널 검사 제거(앞서 역참조했으므로 "널일 리 없다"고 컴파일러가 추론 — 리눅스 커널 CVE 사례). 코드 리뷰는 통과하는데 바이너리에서 검사가 증발한다.
- **메커니즘**: UB는 "일어나지 않는다"가 컴파일러의 합법적 가정 — 그 가정 위에서 검사·저장이 불필요 코드로 제거된다. "동작 확인"이 무의미한 이유: 다음 컴파일러 버전·다음 최적화 레벨이 다른 선택을 한다.
- **방어**: 검사는 UB 없는 형태로(오버플로는 무부호 연산·표준 함수로) + 비밀 클리어는 `memset_s`/`explicit_bzero` + UBSan을 CI에 — "의심되면 cppreference"가 룰인 근거.

## 3. use-after-free — 브라우저 보안의 최다 장르 (공개 통계)

- **무슨 일**: Chrome 보안팀 공개 통계 — 심각 보안 버그의 약 70%가 메모리 안전 문제이고 그중 use-after-free가 최대 비중. 객체 해제 후 잔존 포인터로 접근 — 그 메모리를 공격자가 재할당으로 장악하면 임의 코드 실행으로 승격된다.
- **발생 골격**: 소유권 불명(안티패턴 3) + 수동 수명 관리(안티패턴 1)의 곱 — 콜백·캐시·옵저버에 남은 포인터가 전형적 잔존 경로.
- **방어 서열**: ① 소유권을 타입으로(unique_ptr — 댕글링을 만들 손이 없어짐) ② 비소유 참조의 수명 계약 명시(주석+리뷰) ③ ASan이 use-after-free를 직접 잡는다 — 테스트 커버리지가 닿는 한. Chrome의 결론이 MiraclePtr·Rust 도입이라는 점이 "규율보다 구조" 원칙의 업계 실증.

> 출처(전부 1차/공식, 2026-06 응답 확인):
> - Heartbleed: <https://heartbleed.com/> (Codenomicon 공식 공개 페이지) · <https://nvd.nist.gov/vuln/detail/CVE-2014-0160> (NIST NVD 공식 CVE 기록 — 2012 도입~2014-04-07 패치, memcpy 전 길이 미검증 확인).
> - UB와 최적화의 상호작용: <https://en.cppreference.com/w/cpp/language/ub> (cppreference 표준 정리 — "UB 없는 프로그램 가정 위에서 최적화가 예상 밖 결과 생성" 명시; signed overflow·OOB·UAF·strict aliasing 위반을 UB 예시로 열거).
> - 메모리 안전 통계: <https://www.chromium.org/Home/chromium-security/memory-safety/> (Chrome 보안팀 공식 — 심각 버그 약 70%가 메모리 안전, UAF 최다 비중, MiraclePtr·Rust 도입 결론).
> - 새니타이저 vs valgrind 속도: <https://github.com/google/sanitizers/wiki/AddressSanitizerComparisonOfMemoryTools> (Google 공식 비교표 — ASan 2x slowdown vs Valgrind/Memcheck 20x, 약 10배 빠름).
> - 컴파일러 UB 문헌: John Regehr "A Guide to Undefined Behavior in C and C++" (블로그 3부작, UB 제거 최적화 사례).
> - 소유권/RAII 관용구 근거: C++ Core Guidelines <https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines> (R.20/R.21 unique_ptr 우선, F.26/F.27 스마트 포인터, P.8 자원 누수 금지 — Stroustrup·Sutter).
