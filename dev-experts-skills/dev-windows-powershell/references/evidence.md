# dev-windows-powershell evidence — 실증 사례

## 1. 5.1/7 이중 세계 — 파서 에러는 실행 전에 죽는다 (구조 실증)

- **무슨 일**: PS 7 전용 문법(`&&`·`||`·삼항 `?:`·`??`·`?.`)이 든 스크립트를 5.1이 로드하면 **한 줄도 실행되기 전에** 파서 에러 — try/catch도 로깅도 소용없다(파싱 단계라). 작업 스케줄러·구형 CI·타인 환경의 기본이 5.1인 한 반복되는 사고.
- **분기 사실표**: Windows 기본 탑재 = 5.1(powershell.exe, .NET Framework) / 7.x = 별도 설치(pwsh.exe, 최신 .NET) — 명령도 모듈 호환도 다르다. 스케줄러·호출 측이 어느 exe를 부르는지가 전부.
- **방어**: ① 스크립트 서두 `#Requires -Version 7` (5.1이 열면 즉시 명확한 에러 — 침묵 오동작 방지) 또는 5.1 호환 작성 ② 배포 전 `powershell.exe -NoProfile -File` 1회 실검증 ③ 스케줄 등록 시 실행 파일 경로를 pwsh.exe로 명시(7 전용일 때).

## 2. 인코딩 3중주 — 파일·도구·콘솔이 제각각 (한글 환경 표준 사고)

- **무슨 일**: ① 5.1 `Out-File`/`>` 기본 = UTF-16 LE BOM → git이 바이너리 취급·리눅스 도구 깨짐 ② 7 기본 = BOM 없는 UTF-8 → 같은 스크립트가 버전 따라 다른 산출물 ③ 한국 Windows 콘솔 = cp949 → UTF-8 출력 한글이 화면에서만 깨짐(파일은 정상) — 세 겹이 조합되며 "어디서 깨졌는지"가 미궁이 된다.
- **진단 절차**: 파일 자체(`Format-Hex file | Select -First 1` — BOM 확인: FF FE=UTF-16, EF BB BF=UTF-8 BOM) → 읽는 쪽의 가정 → 콘솔(`chcp`) 순서로 3지점 분리.
- **방어 표준**: 쓰기 100% 인코딩 명시 + 도구 간 교환 파일은 BOM 없는 UTF-8(`[IO.File]::WriteAllText` — 5.1에서도 BOM 없이 가능) + 스크립트 메시지는 ASCII 안전 우선. 본 스킬군의 "scripts 출력 ASCII만" 규율의 근거.

## 3. 비종결 에러 — "catch가 있는데 안 잡혔다" (에러 모델 실증)

- **무슨 일**: `try { Get-Item C:\없는파일 } catch { "잡힘" }` — 안 잡힌다. cmdlet 기본 에러는 비종결(파이프라인 계속 진행)이라 catch는 종결 에러만 잡는다. "에러 메시지는 빨갛게 떴는데 스크립트는 성공 종료" — 백업 검증·배포 스크립트에서 치명적 침묵 통과.
- **이중 채널 함정**: cmdlet 성패는 `$?`, 외부 exe는 `$LASTEXITCODE` — `robocopy`(성공도 1~7 반환)나 `git`(stderr 출력이 에러가 아님) 같은 exe별 관례까지 겹치면 성공 판정 로직 자체가 도메인 지식이다.
- **방어 표준**: 서두 `$ErrorActionPreference = 'Stop'`(전 cmdlet 종결 승격) + 개별 무시는 명시 `-ErrorAction SilentlyContinue` + exe 호출마다 `if ($LASTEXITCODE -ne 0) { throw ... }` 래퍼 — "기본이 침묵 진행"임을 전제로 한 방어.

> 출처: PowerShell 공식 문서(about_Parsing·about_Preference_Variables·인코딩) · Windows 한글 환경 실무 집적. 2026-06, PS 5.1/7.x 병존 기준.
