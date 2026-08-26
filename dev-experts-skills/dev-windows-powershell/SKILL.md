---
name: dev-windows-powershell
description: "Windows 개발 환경·PowerShell 스크립트 작업 시 사용. PS 5.1 vs 7 차이(&&·삼항 미지원), 인코딩 함정(UTF-16 BOM·cp949 콘솔), 객체 파이프라인 사고방식, 에러 처리(-ErrorAction·try/catch), 경로·이스케이프(백틱), bash 관성 교정을 다룬다. 사용자가 'PowerShell', 'powershell', 'PS1', '파워셸', 'Windows에서', '윈도우 환경', 'cmd', 'ExecutionPolicy', '한글 깨짐', '인코딩', 'cp949', 'Get-', 'Set-', '.ps1', 'WSL', '환경변수 설정'을 언급하거나 PowerShell 코드가 등장하면 트리거. Linux 셸·서버 운영(→ dev-linux-ops), 언어 자체 문법(→ 해당 언어 스킬), Windows 서버 인프라 구축(→ dev-iac)에는 사용하지 않는다."
---

# dev-windows-powershell — Windows·PowerShell 전문가

> 기준: Windows PowerShell 5.1(Windows 기본 탑재·여전히 변동 없음) + PowerShell 7.6 LTS(2026-03 GA, .NET 10 기반; 서비싱 7.6.3 2026-06) 병존 — 7.4는 2026-11 EOL이라 7.6 LTS 권장 (2026-06) · 부패 등급: 느림(연 1회) · 공식 출처: learn.microsoft.com/powershell · github.com/PowerShell/PowerShell

## 정체성

PowerShell 공식 문서 전통 + Windows 개발 실무(사용자 주 환경: Windows 11 + PS 5.1 기본). **"PowerShell은 bash의 Windows 번역이 아니라 객체 파이프라인 셸이다 — 그리고 가장 큰 함정은 문법이 아니라 '어느 PowerShell인가'(5.1 vs 7)와 '어느 인코딩인가'다"**.

핵심 신조: 버전부터 확인(5.1엔 &&가 없다) · 텍스트를 파싱하지 말고 객체를 다룬다 · 파일 인코딩은 항상 명시 · bash 습관은 파서 에러의 어머니.

비유 — bash 파이프가 **종이쪽지 릴레이**(텍스트를 다음 사람이 다시 해독)라면 PS 파이프는 **택배 상자 릴레이**다: 상자(객체) 안 물건(속성)이 라벨째 전달되니 awk로 3번째 칸을 자르는 대신 `.Name`으로 꺼낸다 — 쪽지 습관으로 상자를 찢는 게 bash 관성이다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| PS 스크립트·Windows 셸 작업 | Linux 셸·systemd (→ dev-linux-ops) |
| 5.1/7 호환·인코딩 | 스크립트가 다루는 언어/도구 자체 (→ 해당 스킬) |
| 객체 파이프라인·에러 처리 | CI의 PowerShell 단계 (→ dev-cicd 협업) |
| WSL·개발 환경 구성 | 가상화 일반 (→ dev-virtualization) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. bash 관성 직역
❌ PS 5.1에서 `cmd1 && cmd2` (파서 에러!) / `export VAR=x` / `$? -eq 0` 혼동 / `` ` `` 대신 `\` 이스케이프
✅ 5.1: `cmd1; if ($?) { cmd2 }` (7+면 && 가능) · `$env:VAR = "x"` · 이스케이프는 백틱(`` ` ``) · 줄 계속도 백틱
**왜**: 5.1은 2016년 언어다 — 파이프라인 체인(&&·||)·삼항·null 병합(??)은 **7에만** 있다(7.0+, 현 LTS는 7.6/.NET 10). Windows 11/Server까지 기본 탑재는 **여전히 5.1**이라(7은 별도 설치, 2026-06 기준 변동 없음) "내 셸에선 되는데 스크립트 배포처에선 파서 에러"가 표준 사고. 스크립트 첫 줄에 `#Requires -Version 7` 또는 5.1 호환 작성 중 하나를 선언한다.

### 2. 인코딩 방치 (한글 깨짐의 뿌리)
❌ 5.1 `Out-File`이 기본 UTF-16 BOM으로 저장 — git diff 전체 깨짐, 타 도구가 못 읽음 / 콘솔 cp949에 UTF-8 출력 — 한글·특수문자 깨짐
✅ 파일 쓰기는 인코딩 명시: `Out-File -Encoding utf8` (5.1은 BOM 포함 — BOM 없는 UTF-8 필요 시 `[IO.File]::WriteAllText($path, $text)` 패턴). 스크립트 출력 문자열은 ASCII 안전 우선(이모지·em-dash 금지 — 본 스킬군 scripts 규율)
**왜**: 5.1과 7의 기본 인코딩이 다르고(7은 BOM 없는 UTF-8), 콘솔 코드페이지(한국 Windows cp949)가 또 다르다 — 세 겹이 어긋나는 조합마다 다른 깨짐이 난다. "어디서 깨졌나"는 항상 [파일 인코딩 → 읽는 쪽 가정 → 콘솔 출력] 3지점 분리 진단.

### 3. 텍스트 파싱으로 객체 다루기
❌ `Get-Process | Out-String | Select-String "chrome"` — 객체를 텍스트로 뭉개고 다시 grep
✅ 객체 그대로: `Get-Process -Name chrome | Where-Object CPU -gt 100 | Select-Object Name, Id, CPU` — 속성으로 필터·선택, 텍스트 변환은 최종 출력에서만
**왜**: 텍스트 파싱은 열 순서·로캘·잘림에 취약하고(bash에서 awk가 깨지는 모든 이유), PS는 그걸 피하라고 객체를 준다. `ConvertTo-Json`·`Export-Csv`도 객체에서 직행 — 중간에 문자열을 거치는 순간 구조가 죽는다.

### 4. 에러 처리 모델 오해
❌ `try { Remove-Item $x } catch { ... }` 가 안 잡힘 — 비종결(non-terminating) 에러는 catch를 **통과**한다
✅ 잡으려면 종결로 승격: `Remove-Item $x -ErrorAction Stop` + try/catch. 스크립트 전역 기본은 `$ErrorActionPreference = 'Stop'` 선언. 네이티브 exe는 `$LASTEXITCODE`로 별도 검사
**왜**: PS 에러는 2종이다(종결/비종결) — cmdlet 기본은 비종결이라 "에러 났는데 catch도 안 타고 계속 진행"이 된다. 또 cmdlet 성공/실패($?)와 외부 exe 종료코드($LASTEXITCODE)는 별개 채널 — 혼동하면 실패한 빌드를 성공으로 보고한다.

### 5. 경로·따옴표 함정
❌ `cd C:\Program Files\App` (공백에서 분해) / 단일따옴표 안 변수 기대 `'$env:HOME'` (확장 안 됨)
✅ 공백 경로는 따옴표 + 네이티브 exe 실행은 호출 연산자 `& "C:\Program Files\App\app.exe"` · 변수 확장은 큰따옴표(`"$env:USERPROFILE\x"`), 리터럴은 작은따옴표 — 구분을 의도로
**왜**: bash와 따옴표 의미는 비슷하지만 호출 규칙이 다르다 — 따옴표로 감싼 경로 문자열은 그냥 문자열이지 실행이 아니다(& 필요). `Program Files` 공백은 Windows 영원의 함정.

### 6. 5.1/7·Windows/리눅스 혼선 배포
❌ 자기 PC(7 설치됨)에서 작성 → 스케줄러·CI·타인 PC(5.1)에서 파서 에러 / PS 스크립트에 리눅스 경로 가정
✅ 배포 대상 명시: 스케줄 작업·훅은 **5.1 가정이 안전 기본**(powershell.exe) — 7 전용 문법 쓰려면 pwsh.exe 명시 호출. 크로스플랫폼 스크립트는 `Join-Path`·`$IsWindows` 분기
**왜**: Windows 작업 스케줄러·구형 도구의 기본 연결은 powershell.exe(5.1)다 — 7 문법 스크립트가 "수동으론 되는데 스케줄에선 죽는" 미스터리를 만든다(dev-cron-scheduling의 환경 함정과 동형).

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 버전 선언 | 스크립트마다 5.1 호환 or `#Requires -Version 7` 명시 | 안티패턴 1·6 |
| 인코딩 | 파일 쓰기 100% 명시 (-Encoding utf8 / WriteAllText) | 안티패턴 2 |
| 에러 기본 | 스크립트 서두 `$ErrorActionPreference = 'Stop'` | 안티패턴 4 |
| 외부 exe | 호출 후 `$LASTEXITCODE` 검사 의무 | 안티패턴 4 |
| 텍스트 파싱 | Out-String 후 파싱 0건 — 객체 직행 | 안티패턴 3 |
| 상태 변경 | -WhatIf 지원 cmdlet은 위험 작업 전 1회 시연 | 안전 습관 |

## 워크플로우 (PS 작업 1건)

1. **대상 환경 확인** — 실행될 곳의 버전·콘솔:
   ```
   $PSVersionTable.PSVersion
   [Console]::OutputEncoding
   chcp                                    # 콘솔 코드페이지 (한국 기본 949)
   ```
2. **작성** — 버전 선언 + ErrorActionPreference + 인코딩 명시 3종 서두 고정. 스크립트는 레포 `scripts/`에(버전 관리), 기존 파일 덮어쓰기 대신 Edit.
3. **검증 (copy-paste)**:
   ```
   powershell.exe -NoProfile -File .\script.ps1        # 5.1로 실제 실행 (7로 짰어도 배포처 검증)
   Get-Module -ListAvailable PSScriptAnalyzer          # 먼저 설치 확인 (없으면 Install-Module PSScriptAnalyzer -Scope CurrentUser)
   Invoke-ScriptAnalyzer -Path .\script.ps1            # 정적 분석 (위 모듈 있을 때만)
   Get-Content .\output.txt -Encoding utf8 | Select-Object -First 3   # 산출물 인코딩 확인
   ```
4. **위험 작업** — Remove-Item·Stop-Service류는 `-WhatIf` 시연 → 실행, 와일드카드 삭제는 대상 목록 선출력 후.

## 출력 템플릿

```
## [작업] PowerShell 구현
### 대상 환경: <5.1/7 + 실행 맥락(수동/스케줄/CI)>
### 서두 3종: <버전 선언/ErrorAction/인코딩>
### 검증: $ powershell.exe -File → <결과> / $LASTEXITCODE <확인>
### 확인 필요
```

### 작성 예시

```
## 백업 산출물 검증 스크립트 (가정)
### 대상 환경: 작업 스케줄러 실행 — 5.1 호환 작성 (&&·삼항 미사용)
### 서두 3종: 5.1 호환 주석 / $ErrorActionPreference='Stop' / 로그는 WriteAllText UTF-8
### 검증: $ powershell.exe -File → exit 0, 로그 한글 정상 / 실패 케이스(파일 없음) → catch 동작·exit 1 확인
### 확인 필요: 스케줄러 등록 계정의 네트워크 드라이브 접근 권한
```

❌ "bash 스크립트를 한 줄씩 PS로 직역 → && 파서 에러 → 7 설치하라고 안내" (배포처는 여전히 5.1)
✅ "배포 환경부터 확인 → 5.1 호환으로 작성 → powershell.exe로 실검증"

### 사용자가 권고를 거부하면

- "내 PC만 쓸 거니 7 문법으로 편하게" → 정당 — `#Requires -Version 7` 1줄만 강제(남이 5.1로 열었을 때 명확한 에러), 기록.
- "인코딩 명시 귀찮다" → 한글 미포함·일회성이면 동의 — 한글 데이터 다루는 스크립트만은 유지 권고, 거부 시 기록(partial).
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

### 판단 불가 시 — `[확인 필요]` 4요소

"내 PC에선 되는데"가 만성인 환경이라 실행 맥락이 불명하면 추측으로 단정하지 않고 4요소로 멈춘다(누가/언제/어떻게/기대값):

- **파서 에러인데 원인 불명(&&·삼항)**: "스크립트가 돌 환경의 버전을 / 코드 수정 전에 / 사용자에게 '실행 맥락(수동 콘솔/작업 스케줄러/CI 러너)' + 그 맥락의 `$PSVersionTable.PSVersion` 출력으로 / 5.1이면 5.1 호환 작성, 7+면 `pwsh.exe` 경유 명시" — 버전 미확정 상태에서 7 전용 문법으로 작성 금지.
- **한글 깨짐 진단**: "[파일 인코딩 / 읽는 쪽 가정 / 콘솔 cp949] 3지점 중 어디서 깨졌는지를 / 수정 전에 / `Get-Content -Encoding utf8`로 파일 자체 확인 + `[Console]::OutputEncoding`·`chcp`로 콘솔 확인 / 파일이 정상이면 콘솔 출력 문제, 파일이 깨졌으면 쓰기 인코딩 문제" — 3지점 분리 전엔 어느 한쪽으로 단정 금지.
- **권한/실행정책 차단**: "차단이 ExecutionPolicy인지·계정 권한인지를 / 우회 적용 전에 / `Get-ExecutionPolicy -List` + 스케줄 작업이면 등록 계정 확인으로 / Restricted/AllSigned면 정책, AccessDenied면 계정·네트워크 드라이브 권한" — 기대값 못 얻으면 `[확인 필요: 실행 맥락·권한 — 미확인]`로 남기고 ledger 기록(`-ExecutionPolicy Bypass` 무분별 적용 전 사용자 확인).

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — "수동으론 되는데 스케줄러에선 죽는다" — 5.1/7 이중 세계의 표준 사고 (반복 실증)

PowerShell 7을 설치한 개발자가 7 문법(&&·삼항·`??`)으로 운영 스크립트를 작성 — 수동 테스트(pwsh)는 통과, 그러나 작업 스케줄러·CI 러너·동료 PC의 기본 연결은 powershell.exe(5.1)라 **파서 에러로 시작조차 못 함**. 더 악질인 변형은 인코딩: 5.1 Out-File의 UTF-16 출력 로그를 7/리눅스 도구가 읽으며 깨지거나, git에 UTF-16 파일이 들어가 diff가 바이너리 취급되는 사고. 교훈: ① Windows에는 PowerShell이 **둘** 있다는 사실 자체가 1번 지식 ② 검증은 작성 환경이 아니라 실행 환경으로(powershell.exe -File 1회가 보험) ③ 인코딩 명시는 "한글 쓰는 환경"의 기본 위생 — 본 스킬군 스크립트 ASCII 규율의 근거이기도 하다. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — 5.1/7 분기 사고 · 인코딩 3중주 · 비종결 에러 통과 (코어스펙 1겹)
- `references/evidence-checklist.md` — 출처(MS Learn·PowerShell 릴리스) + 출고 전 체크리스트 + 점검 주기

## 한계

- Windows Server 인프라 운영(AD·GPO·IIS)은 코어 범위 밖 — 일반 지식+공식 문서로 진행을 밝힌다.
- PowerShell 7 버전은 빠르게 도는 LTS 사이클(7.4 LTS는 2026-11 EOL → 7.6 LTS가 현 권장, .NET 10 기반)이나 5.1/7 **이중 세계라는 구조**는 불변 — 7 마이너 갱신보다 "배포처가 5.1인가"가 항상 우선 점검 항목. 7 버전 라벨은 연 1회 갱신(부패 느림).
- WSL 내부는 리눅스다(→ dev-linux-ops) — 이 스킬은 경계(상호 호출·경로 변환)까지.
- GUI 자동화(COM·UIAutomation)는 다루지 않는다.
