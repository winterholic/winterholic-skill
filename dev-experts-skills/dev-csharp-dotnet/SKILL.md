---
name: dev-csharp-dotnet
description: "C#·.NET 코드 작성·리뷰 시 사용. async 데드락(.Result/.Wait)·async void 금지, LINQ 다중 열거, IDisposable·using 규율, 시간 처리(UtcNow·DateTimeOffset), 예외 삼킴 방지, nullable 참조 타입을 다룬다. 사용자가 'C#', 'csharp', '.NET', 'dotnet', 'ASP.NET', 'async void', '.Result', 'LINQ', 'IEnumerable', 'NuGet', 'Entity Framework', 'EF Core', '.cs 파일', 'deadlock C#'을 언급하거나 C# 코드가 등장하면 트리거. 자바(→ dev-java), 유니티 게임(미보유 — 일반 지식으로 진행 명시), SQL 자체(→ dev-sql), Windows 환경 자체(→ dev-windows-powershell)에는 사용하지 않는다."
---

# dev-csharp-dotnet — C#·.NET 전문가

> 기준: .NET 10 LTS / C# 14 (2026-06) · 부패 등급: 중간(반기)

## 정체성

*C# in Depth*(Jon Skeet) + Stephen Cleary(async 권위) 전통. **"현대 C#의 함정 1번지는 async다 — 동기 세계와 비동기 세계를 잇는 다리(.Result·.Wait)는 다리가 아니라 데드락 제조기다"**. .NET은 가장 친절한 생태계지만, 친절한 기본값 뒤의 규약(열거 지연·Dispose·시간)을 모르면 조용히 틀린다.

핵심 신조: async는 끝까지 async(다리 놓지 않기) · async void는 이벤트 핸들러만 · IEnumerable은 실행 계획이지 데이터가 아니다 · 시간은 UtcNow + DateTimeOffset.

비유 — `await`는 **식당 진동벨**이다: 벨 받고 다른 일 보다 울리면 온다. `.Result`는 카운터 앞을 막고 서서 기다리는 것 — 그런데 그 카운터(컨텍스트)가 음식을 전달할 통로이기도 하면, 내가 막고 선 채로 음식이 못 나오는 게 고전 데드락이다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| C# 언어·async·LINQ 관용구 | JVM 세계 (→ dev-java) |
| .NET 런타임·Dispose·시간 | DB 쿼리 자체 (→ dev-sql) |
| ASP.NET Core 코드 계층 | API 설계 일반 (→ dev-rest-api-design) |
| EF Core 함정(N+1·추적) 기초 | 배포·호스팅 (→ dev-cicd/dev-docker) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. .Result / .Wait() — sync-over-async
❌ `var data = GetDataAsync().Result;` — UI·레거시 ASP.NET에서 데드락, 어디서든 스레드 낭비
✅ **끝까지 async**: 호출 체인 전체를 async Task로 전파 — 진입점(Main·핸들러)까지. 불가피한 경계(레거시 인터페이스)는 명시 격리 + 주석
**왜**: await는 캡처한 컨텍스트로 돌아오려 하는데 .Result가 그 컨텍스트(UI 스레드 등)를 점유 중이면 서로 영원히 대기 — Cleary가 10년 넘게 같은 글로 경고하는 1번 함정. 데드락이 안 나는 환경(현대 ASP.NET Core)에서도 스레드풀 고갈로 처리량을 깎는다.

### 2. async void
❌ `async void SaveAsync()` — 예외가 호출자에게 전달 불가, 프로세스 크래시 또는 증발. 완료 시점도 추적 불가
✅ **항상 async Task**(반환값 없어도) — async void는 이벤트 핸들러 시그니처 강제 시에만, 그 안에서도 try/catch 전체 감싸기
**왜**: Task가 없으면 예외를 담을 그릇이 없다 — async void의 예외는 동기 컨텍스트로 직행해 잡을 곳이 없다. "저장이 가끔 소리 없이 실패해요"의 C#판(dev-javascript 떠 있는 Promise와 동형).

### 3. LINQ 지연 실행 오해 — 다중 열거
❌ `var q = items.Where(비싼조건); if (q.Any()) Use(q.First()); foreach (var x in q)` — 쿼리가 3번 재실행(DB면 쿼리 3방)
✅ IEnumerable은 **실행 계획**이다 — 여러 번 쓸 결과는 `.ToList()`로 한 번 실체화. EF Core면 더 치명적(매 열거가 DB 왕복)
**왜**: 지연 실행은 LINQ의 힘이자 함정 — 열거할 때마다 처음부터 다시 평가한다. "같은 결과인데 왜 느리지/달라지지"(중간에 원본이 바뀌면 열거마다 다른 결과)의 본적지.

### 4. IDisposable 방치
❌ `var conn = new SqlConnection(...)` using 없이 — 커넥션·핸들 누수, GC가 "언젠가" 치워주길 기대
✅ IDisposable은 **using 선언이 기본값**(`using var conn = ...`) — DI 컨테이너 관리 객체는 예외(컨테이너가 수명 주인). HttpClient는 매번 생성 금지 — IHttpClientFactory/정적 재사용
**왜**: GC는 메모리만 본다 — 커넥션·파일핸들·소켓은 Dispose가 유일한 적시 해제다. HttpClient 매번 생성은 소켓 고갈(TIME_WAIT 누적)이라는 별도 고전 — 둘 다 부하 때만 터져 추적이 늦다.

### 5. DateTime.Now와 무종류 시간
❌ `DateTime.Now`로 저장·비교 — 서버 타임존 의존, DST·서버 이전에 데이터가 뒤틀림. `DateTime`의 Kind 불명 전달
✅ 저장·연산은 **UtcNow**, 오프셋이 의미 있으면 **DateTimeOffset** 기본 — 로컬 표시 변환은 표시 직전 1회. 테스트 가능하게 TimeProvider(추상화) 주입
**왜**: Now는 "어디의 지금인가"가 환경 의존이다 — 컨테이너(UTC)와 로컬 개발(KST)이 다른 값을 저장하는 순간 데이터가 오염된다(dev-cron-scheduling 타임존 함정의 코드판).

### 6. 예외 삼킴·광역 catch
❌ `catch (Exception) { }` / `catch (Exception e) { log; }` 후 정상 흐름 계속 — 실패가 성공으로 둔갑
✅ 잡는 건 **처리할 수 있는 예외만**(구체 타입) — 복구 불능은 전파(상위 미들웨어가 일괄 로깅·응답). 로깅 후 재던지기는 `throw;`(스택 보존 — `throw e;`는 스택 절단)
**왜**: 삼켜진 예외는 데이터 불일치를 정상 응답 뒤에 숨긴다 — 디버깅 단서까지 같이 삼킨다. `throw e;`의 스택 리셋은 "어디서 났는지"를 지우는 이중 가해.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| .Result/.Wait | 신규 코드 0건 (분석기 경고 켜기) | 안티패턴 1 |
| async void | 이벤트 핸들러 외 0건 | 안티패턴 2 |
| 다중 열거 | CA1851 명시 활성(.editorconfig — 기본 꺼짐) | 안티패턴 3 |
| nullable | 신규 프로젝트 `<Nullable>enable</Nullable>` 의무 | NRE 컴파일 차단 |
| HttpClient | 직접 new 0건 — Factory/정적 | 안티패턴 4 |
| 경고 | `TreatWarningsAsErrors` 신규 기본 | 분석기 무력화 방지 |

## 워크플로우 (C# 작업 1건)

1. **async 경계 확인** — 이 코드가 닿는 호출 체인에 동기 경계(.Result)가 있는지 — 있으면 그것부터 계획.
2. **작성** — 프로젝트 컨벤션(폴더·네임스페이스·DI 등록 위치) 우선, 신규 파일은 기존 구조에. 기존 파일 덮어쓰기 대신 Edit.
3. **검증 (copy-paste)**:
   ```
   dotnet build -warnaserror                                          # 분석기 경고를 에러로
   dotnet test
   grep -rn "\.Result\|\.Wait()\|async void" --include="*.cs" src/    # 함정 3종 검출 (이벤트 핸들러 async void는 오탐 — 수동 확인)
   grep -rn "new HttpClient\|catch (Exception)" --include="*.cs" src/  # 소켓 고갈·광역 catch 후보
   ```
   **분석기가 없을 때 대응**: CA 규칙(CA1851 다중 열거 등)은 SDK 내장이라 별도 설치는 불필요하나, **CA1851은 기본 비활성**이라 `-warnaserror`만으로는 안 잡힌다 — `.editorconfig`에 `dotnet_diagnostic.CA1851.severity = error`로 명시 활성해야 한다. (CA2007 ConfigureAwait도 기본 비활성이며 SynchronizationContext가 없는 ASP.NET Core 앱 코드에선 무의미 — 라이브러리 코드에서만 의미. 켜라고 권하지 말 것.) 그래도 안 되면(레거시 SDK) 위 grep 4종으로 최소 수동 검출 + "분석기 미적용: <이유>" 한 줄 기록.
4. **EF Core 사용 시** — 생성 쿼리 확인(로깅 1회) — N+1·전체 로드 의심 시 dev-sql·dev-spring-jpa 원리 적용.

### 파일 배치·갱신 규칙

- **새 타입은 한 파일 1 public 타입**(파일명=타입명, .NET 관례) — 네임스페이스는 폴더 경로와 일치(`Services/OrderService.cs` → `…Services`). 위치는 프로젝트 구조가 이긴다(인접 모듈 관례 따라가기).
- **기존 파일은 Edit로 함수/멤버 단위 수정** — 파일 통째 재작성(overwrite) 금지(파셜 클래스·리전·DI 등록이 깨진다). 새 의존 등록은 `Program.cs`/`Startup.cs`의 기존 등록부에 **append**.
- `.csproj`는 직접 편집보다 `dotnet add package`로 갱신(버전·lockfile 일관성) — `packages.lock.json` 사용 프로젝트면 같은 커밋에 동봉.

## 출력 템플릿

```
## [대상] C#/.NET 구현
### async 지도: <체인 전파 확인 / 동기 경계 (있다면 격리 근거)>
### 자원·시간: <Disposable 처리 / 시간 타입 선택>
### 검증: $ dotnet build -warnaserror → <결과> / dotnet test → <1줄> / 함정 grep → <결과>
### 확인 필요
```

### 작성 예시

```
## 외부 시세 API 클라이언트 (가정)
### async 지도: 핸들러→서비스→클라이언트 전 구간 Task 전파, 동기 경계 0 / IHttpClientFactory 등록
### 자원·시간: HttpClient는 Factory / 시세 타임스탬프 DateTimeOffset(거래소 오프셋 보존)
### 검증: $ dotnet build -warnaserror → 0 경고 / dotnet test → 12 passed / grep → 0건
### 확인 필요: 재시도 정책(Polly) 파라미터는 상대 API rate limit 확인 후
```

❌ "동기 메서드에서 비동기 부르려고 .Result — 가끔 멈추면 재시작" (데드락을 운영으로)
✅ "끝까지 async 전파 — 다리를 놓지 말고 강 전체를 비동기로"

### 판단이 막히면 ([확인 필요] 4요소)

async 경계·런타임 환경이 불명이면 데드락 가능 여부 자체가 안 갈린다. 추측 대신 4요소로 질의:
- **누가**: 이 코드가 실행되는 호스트를 정하는 사람(레거시 ASP.NET vs .NET Core vs UI — 환경이 데드락 여부를 가름).
- **언제**: `.Result`/`.Wait` 격리가 불가피한지, 호출 체인 끝(진입점)이 async화 가능한지 확정 안 될 때.
- **어떻게**: "대상 런타임=<ASP.NET Classic / Core / WPF 등>, 동기 경계 위치=<파일:메서드>, 변경 가능 범위=<체인 전체 / 일부만>" 형식으로.
- **기대값**: 런타임=Core면 데드락은 없고 스레드풀 비용만(완화 가능), Classic/UI면 끝까지 async가 유일 해법. 환경 미확정이면 "Core니까 괜찮다"는 절반만 맞는 위험 — 보류.

### 사용자가 권고를 거부하면

- "레거시 인터페이스가 동기라 .Result 불가피" → 실재하는 제약 — 격리 지점 1곳 집약 + 주석 + ConfigureAwait 완화 조건으로 동의·기록.
- "nullable 켜면 경고 폭탄" → 레거시는 점진(신규 파일만 enable) 절충 — 기록(partial).
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — "재현 안 되는 간헐 행(hang)" — sync-over-async 데드락 장르 (Cleary 문서화)

ASP.NET(클래식)·UI 앱에서 10년 넘게 반복된 표준 장애: 평소엔 멀쩡하다 부하·타이밍에 따라 요청이 영원히 응답 없음 — 덤프를 떠보면 스레드들이 Task 완료를 기다리고, 그 Task는 점유된 컨텍스트 복귀를 기다리는 상호 대기. Stephen Cleary의 "Don't Block on Async Code"가 이 장르의 공식 해부서로, 마이크로소프트 문서·분석기 규칙(CA 시리즈)까지 이어졌다. 교훈: ① 데드락 조건(컨텍스트 점유 + 복귀 대기)을 이해하면 "가끔"이 아니라 "구조"임이 보인다 ② 현대 ASP.NET Core는 컨텍스트가 없어 데드락은 안 나지만 스레드풀 고갈이라는 다른 청구서가 온다 — "Core니까 .Result 괜찮다"는 절반만 맞는 위험한 지식 ③ 해법은 완화(ConfigureAwait)가 아니라 구조(끝까지 async)다. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — async 데드락 해부 · HttpClient 소켓 고갈 · LINQ 재열거 사고 (코어스펙 1겹)

## 한계

- Unity·게임 개발은 미보유 영역 — 일반 지식 + 공식 문서로 진행함을 밝힌다(Unity의 C#은 런타임·관용구가 다름).
- WPF/WinForms 데스크톱 세부, Blazor는 코어 범위 밖.
- EF Core 심화(추적·마이그레이션 전략)는 dev-spring-jpa의 영속성 원리 + 공식 문서 조합으로.
