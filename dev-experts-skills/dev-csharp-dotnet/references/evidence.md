# dev-csharp-dotnet evidence — 실증 사례

## 1. sync-over-async 데드락 — 장르의 해부 (Cleary·MS 공식 문서화)

- **메커니즘 재현**: UI/클래식 ASP.NET 컨텍스트는 "한 번에 한 코드"만 실행 — ① 동기 메서드가 `GetAsync().Result`로 블로킹(컨텍스트 점유) ② GetAsync 내부의 await 완료 후 **그 컨텍스트로 복귀하려 대기** ③ 컨텍스트는 .Result가 점유 중 — 상호 영원 대기. 부하·타이밍 따라 발현해 "간헐 행"으로 보고된다.
- **세대별 양상**: 클래식 ASP.NET/UI = 데드락 / ASP.NET Core(컨텍스트 없음) = 데드락은 없지만 블로킹 스레드만큼 스레드풀 고갈 → 부하 시 처리량 절벽·요청 적체. "Core라서 안전"은 증상이 바뀐 것뿐.
- **탐지·방어**: 분석기 규칙 활성 + `grep "\.Result\|\.Wait()"` 정기 + 덤프 분석 시 "Task 대기 중 스레드 다수"가 서명. 구조 해법은 진입점까지 async 전파 — 다리 자체를 없앤다.

## 2. HttpClient 매 요청 new — 소켓 고갈 (MS 공식 안내로 승격된 사고)

- **무슨 일**: `using (var client = new HttpClient())` 매 요청 패턴 — Dispose해도 소켓은 TIME_WAIT(기본 수 분)로 잔존, 고트래픽에서 포트 고갈 → `SocketException`. "올바르게 Dispose했는데" 일어나는 사고라 혼란이 컸고, MS가 공식 문서로 IHttpClientFactory를 만든 배경.
- **올바른 패턴**: ① ASP.NET Core = IHttpClientFactory(핸들러 풀링·수명 관리·DNS 갱신까지) ② 단순 앱 = 정적 단일 인스턴스 + `SocketsHttpHandler.PooledConnectionLifetime` 설정(DNS 변경 대응).
- **교훈**: "IDisposable이니 짧게 쓰고 버린다"는 일반 규칙의 예외가 문서화된 사례 — 자원의 실체(소켓 풀)가 객체 수명과 다를 때는 타입 관례보다 공식 가이드가 이긴다.

## 3. LINQ 재열거 — "조회가 3배로 나가요" (EF Core 운영 반복 사고)

- **무슨 일**: `IQueryable`/`IEnumerable`을 변수에 담아 Any()→First()→foreach — EF Core면 **각각이 별도 SQL 실행**(3왕복). 모니터링에서 "같은 쿼리가 N배"로 발견되거나, 사이에 데이터가 바뀌어 Any는 참인데 First가 빈 시퀀스 예외를 던지는 경합형 버그로 나타난다.
- **탐지**: EF Core 로깅 1회 켜고 화면당 쿼리 수 세기(dev-spring-jpa N+1 진단과 동일 절차) + 분석기 CA1851(다중 열거 경고). 단 **CA1851은 기본 비활성**(`isEnabledByDefault: false`)이라 `-warnaserror`만으로는 안 잡힌다 — `.editorconfig`에 `dotnet_diagnostic.CA1851.severity = error`로 명시 활성해야 효력.
- **규칙 도출**: "두 번 이상 쓰면 ToList" — 단 전체 로드 비용과의 교환이므로, DB 측에서 끝낼 수 있는 건 쿼리로 끝내고(Count·Any를 DB로) 실체화는 최종 결과만.

## 출처 (웹 검증 2026-06)

- **Stephen Cleary, "Don't Block on Async Code"** — https://blog.stephencleary.com/2012/07/dont-block-on-async-code.html — async 데드락(SynchronizationContext 점유 + 복귀 대기)을 처음 해부한 정전(canonical) 글. async 권위자의 1차 출처, 안티패턴 1·실전 케이스의 근거.
- **MS Learn, "Guidelines for using HttpClient"** — https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/http/httpclient-guidelines — 매 요청 new로 인한 소켓 고갈과 정적 인스턴스+`PooledConnectionLifetime`/IHttpClientFactory 처방의 공식 가이드(안티패턴 4·실증 2의 근거).
- **MS Learn, "IHttpClientFactory with .NET"** — https://learn.microsoft.com/en-us/dotnet/core/extensions/httpclient-factory — 핸들러 풀링·수명 관리·DNS 갱신을 IHttpClientFactory가 맡는다는 공식 설명.
- **MS Learn, "CA1851: Possible multiple enumerations"** — https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca1851 — 다중 열거 분석기 규칙 공식 문서. **기본 비활성**임을 명시(`.editorconfig` 활성 필요).
- **MS Learn, "CA2007: Do not directly await a Task"** — https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2007 — ConfigureAwait 규칙. **기본 비활성**이며 SynchronizationContext가 없는 ASP.NET Core에서는 사실상 무의미(라이브러리에서만 권장)임을 명시 — "CA2007 켜라"는 ASP.NET Core 앱 코드에는 적용 안 됨.
- **MS Learn, "What's new in .NET 10 / C# 14"** — https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/overview — .NET 10은 2025-11-11 출시 LTS(지원 종료 2028-11-10), C# 14 동반. 스킬 버전 라벨의 근거.

> EF Core 재열거 사고는 위 CA1851 + dev-spring-jpa N+1 진단 절차의 조합으로 다룬다(별도 단일 출처보다 운영 패턴 집적). 2026-06, .NET 10 기준.
