# evidence + 출고 전 체크리스트

(상세 실증 사례는 `evidence.md`, 여기서는 출처 색인 + 출고 체크리스트 + 점검 주기)

## 실증·출처

- **PowerShell 5.1 vs 7 분기** (learn.microsoft.com/powershell, "about_Automatic_Variables"·릴리스 노트) — `&&`/`||`·삼항 `?:`·null 병합 `??`·null 조건 `?.`는 **7.0+ 전용**, 5.1은 파서 에러. Windows 11/Server 기본 탑재는 2026-06 기준 여전히 5.1(powershell.exe). 안티패턴 1·6의 1차 근거.
- **PowerShell 7.6 LTS** (devblogs.microsoft.com/powershell "Announcing PowerShell 7.6", 2026-03 GA; 서비싱 7.6.3 2026-06, .NET 10 기반) — 현 권장 LTS. 7.4 LTS는 2026-11 지원 종료 → 7.6 이관 권장. 버전 라벨·한계의 근거. **확인 필요**: 더 최신 7.7 preview 진행 여부는 github.com/PowerShell/PowerShell/releases 확인.
- **인코딩** (learn.microsoft.com "about_Character_Encoding") — 5.1 `Out-File`/`>` 기본 = UTF-16 LE BOM, 7 기본 = BOM 없는 UTF-8. 한국 Windows 콘솔 기본 코드페이지 = cp949(949). 안티패턴 2·`evidence.md` 2번의 근거. BOM 없는 UTF-8 강제는 `[IO.File]::WriteAllText`.
- **에러 모델** (learn.microsoft.com "about_Try_Catch_Finally"·"about_Preference_Variables") — cmdlet 기본 에러는 비종결(non-terminating)이라 catch를 통과. `-ErrorAction Stop` 또는 `$ErrorActionPreference='Stop'`로 종결 승격. cmdlet 성패는 `$?`, 외부 exe는 `$LASTEXITCODE`(별개 채널). 안티패턴 4·`evidence.md` 3번의 근거.
- **객체 파이프라인** (learn.microsoft.com "about_Pipelines") — 텍스트가 아닌 객체 전달, `Where-Object`/`Select-Object`로 속성 필터. 안티패턴 3의 근거.
- **호출 연산자·따옴표** (learn.microsoft.com "about_Operators"·"about_Quoting_Rules") — 네이티브 exe는 `&`, 변수 확장은 큰따옴표·리터럴은 작은따옴표. 안티패턴 5의 근거.

## 출고 전 체크리스트 (PowerShell 스크립트 출고 시)

- [ ] 배포 대상 환경 확인 — 5.1인가 7인가, 수동/스케줄러/CI 중 무엇인가
- [ ] 서두 3종: 버전 선언(`#Requires -Version 7` 또는 5.1 호환) / `$ErrorActionPreference='Stop'` / 인코딩 방침
- [ ] 7 전용 문법(&&·삼항·??)을 5.1 배포처에 쓰지 않았다 (또는 pwsh.exe 명시)
- [ ] 파일 쓰기 100% 인코딩 명시 (-Encoding utf8 / WriteAllText), 교환 파일은 BOM 없는 UTF-8
- [ ] 스크립트 메시지는 ASCII 안전(이모지·em-dash 회피)
- [ ] 외부 exe 호출마다 `$LASTEXITCODE` 검사 (robocopy 1~7 정상 등 exe별 관례 반영)
- [ ] try/catch 대상은 `-ErrorAction Stop`으로 종결 승격됨 (비종결 통과 방어)
- [ ] 텍스트 파싱(Out-String 후 grep) 0건 — 객체 직행
- [ ] 공백 경로는 따옴표 + `&`, 위험 작업은 `-WhatIf` 1회 시연 후 실행
- [ ] **실행 환경(배포처)에서** `powershell.exe -NoProfile -File`로 실검증 (작성 환경 아님)

## 점검 주기 (부패 느림 — 연 1회)

- PowerShell 7 LTS 라인 추적(현재 7.6 LTS/.NET 10; 7.4는 2026-11 EOL) → 버전 라벨 갱신. 단 5.1/7 **이중 세계 구조**는 불변이므로 우선순위는 "배포처가 5.1인가".
- Windows 기본 탑재 버전 변화 확인(2026-06 여전히 5.1 — 이게 바뀌면 본 스킬 전제 갱신).
- 인코딩 기본값·콘솔 코드페이지(cp949) 동작은 안정 — 변동 드묾, 연 1회로 충분.
