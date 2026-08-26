# dev-electron-desktop evidence — 장애·실증 사례

## 1. Discord·Slack RCE 체인 — XSS의 등급 승격 (2019~2020 버그바운티 공개)

- **무슨 일**: 보안 연구자들이 Electron 메신저에서 "메시지/임베드 → XSS → Node 권한 도달 → RCE" 전체 체인을 시연하고 보상받은 공개 사례들.
  - **Discord (CVE-2020-15174, 2020-10)**: Masato Kinugawa 보고. 3D 모델 임베드의 iframe이 `contextIsolation` 미적용이라 Node 접근 잔존 → XSS+CSP 우회+iframe 체인으로 RCE. 보상 $5,000(RCE) + $300(XSS). 상세: https://mksben.l0.cm/2020/10/discord-desktop-rce.html
  - **Slack (HackerOne #783877, 2020)**: Oskars Vegeris 보고. files.slack.com 저장 XSS → CSP 인젝션 → 데스크톱 앱 RCE. 4.4.0에서 패치. 보상 $1,750(논란 있음). 리포트: https://hackerone.com/reports/783877
- **구조적 교훈**: 체인의 각 고리는 개별로는 '중간' 심각도 — 조합되면 '치명'. 방어도 체인으로: CSP·새니타이즈(1차) → contextIsolation·sandbox(2차) → IPC 좁은 계약(3차). 한 겹 신앙은 금물.
- **이 스킬과의 연결**: 안티패턴 1·2. 점검은 grep(보안 3종 위반)+공식 체크리스트(https://www.electronjs.org/docs/latest/tutorial/security) 대조. 과거 표준이던 정적 스캐너 `electronegativity`(Doyensec, https://github.com/doyensec/electronegativity)는 **유지보수 중단**(최신 Electron에서 깨짐, 공식 문서 권장 목록 제외) — 신규 도입 비권장, 후속은 상용 ElectroNG.

## 2. 메인 프로세스 블로킹 — "모든 창이 동시에 빳빳" (구조 실증)

- **무슨 일**: 트레이 상주형 앱이 주기 작업(대용량 로그 동기 읽기·동기 압축)을 메인에서 수행 → 작업 순간마다 전 창의 입력·드래그·메뉴가 일제히 정지. 렌더러 프로파일링으론 아무것도 안 나와("렌더러는 무죄") 원인 추적이 길어지는 패턴.
- **메커니즘**: 창 이동·메뉴·IPC 라우팅이 전부 메인 이벤트 루프를 경유한다 — 메인의 1초 블로킹은 OS 수준에서 앱 전체 무응답으로 보인다(Windows "응답 없음" 등).
- **방어**: 메인 작업의 상한을 "ms 단위 중개"로 — 그 이상은 utilityProcess/worker. 진단은 메인에 `setInterval`로 이벤트 루프 지연 측정 1줄(`const t = Date.now(); setTimeout(() => lag = Date.now() - t, 0)` 패턴).

## 3. 수제 자동 업데이터 — 업데이트 채널이 공격 채널로 (공급망 실증)

- **무슨 일**: 서명 검증 없는 자체 업데이트(HTTP/zip 교체)를 쓰던 앱들이 ① 중간자(공용 와이파이·사내 프록시)에서 바이너리 치환 ② 업데이트 서버 탈취 시 전 사용자 동시 감염이라는 두 경로로 보안 권고 대상이 된 반복 사례. eslint-scope(2018)·3CX(2023) 등 공급망 사고들이 "배포 채널 장악 = 전 사용자 장악"을 실증.
- **방어**: electron-updater + 서명 검증(공개키 고정)·HTTPS·단계적 롤아웃. 서명 키는 CI 시크릿이 아니라 HSM/클라우드 서명 서비스(DigiCert KeyLocker 등) 수준으로 — 키 유출이 곧 채널 장악이므로. macOS는 Squirrel.Mac 자동업데이트가 서명을 강제(미서명 시 갱신 자체 불가).
- **이 스킬과의 연결**: 안티패턴 6. "업데이트 기능"은 편의 기능이 아니라 원격 코드 실행 인프라로 분류하고 설계한다.

> 출처 (웹 확인 2026-06):
> - Discord RCE 상세 — https://mksben.l0.cm/2020/10/discord-desktop-rce.html (CVE-2020-15174)
> - Slack RCE 리포트 — https://hackerone.com/reports/783877
> - Electron 공식 Security 체크리스트 — https://www.electronjs.org/docs/latest/tutorial/security
> - Electron Code Signing — https://www.electronjs.org/docs/latest/tutorial/code-signing
> - 안전한 Electron 자동업데이터 설계(Doyensec, 2026-02) — https://blog.doyensec.com/2026/02/16/electron-safe-updater.html
