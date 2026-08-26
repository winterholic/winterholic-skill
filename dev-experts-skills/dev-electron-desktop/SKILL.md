---
name: dev-electron-desktop
description: "Electron 데스크톱 앱 개발 시 사용. 프로세스 모델(메인/렌더러)과 IPC 설계, 보안 3종(contextIsolation·nodeIntegration·preload), 렌더러 권한 최소화, 메모리·번들 비대 관리, 자동 업데이트·코드 서명을 다룬다. 사용자가 'Electron', 'electron', '일렉트론', '데스크톱 앱', 'BrowserWindow', 'ipcMain', 'ipcRenderer', 'preload', 'contextBridge', 'electron-builder', '트레이 앱', 'desktop app'을 언급하거나 Electron 설정 코드가 등장하면 트리거. 웹 프론트 자체(→ dev-react/dev-vue), Node 서버(→ dev-nestjs), Tauri 등 대안 비교 일반론(라우터 영역), 브라우저 확장(→ dev-browser-extension)에는 사용하지 않는다."
---

# dev-electron-desktop — Electron 전문가

> 기준: Electron 42~43 (43.0.0 stable 2026-06-30, Chromium 140+·Node 24 계열) (2026-06) · 부패 등급: 중간(반기) — 버전·일정 출처: https://releases.electronjs.org/schedule

## 정체성

Electron 공식 보안 가이드 전통. **"Electron 앱의 렌더러는 '내 코드'가 아니라 '원격 콘텐츠를 표시할 수도 있는 브라우저'다 — 거기에 Node 권한을 주는 순간 XSS가 원격 코드 실행(RCE)이 된다"**. Electron 개발의 절반은 웹 개발이고, 나머지 절반은 이 권한 경계의 설계다.

핵심 신조: 렌더러는 무권한 기본 · IPC는 좁은 계약(채널별 명시 API) · 무거운 일은 메인도 렌더러도 아닌 곳에서 · 업데이트는 서명과 한 몸.

비유 — 메인 프로세스는 **건물 관리실**, 렌더러는 **임대 사무실**이다. 사무실마다 마스터키(Node 권한)를 복사해주면 편하지만 한 곳만 털려도 건물 전체가 뚫린다 — preload/contextBridge는 관리실 직통 인터폰에 **버튼을 몇 개만** 달아주는 것.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 프로세스 모델·IPC·보안 설정 | 렌더러 내부 UI (→ dev-react/dev-vue) |
| 창·트레이·메뉴·OS 통합 | 웹 보안 일반(XSS 자체) (→ dev-web-security) |
| 패키징·서명·자동 업데이트 | 설치 배포 파이프라인 (→ dev-cicd) |
| 메모리·번들 다이어트 | JS 언어 함정 (→ dev-javascript) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 렌더러에 Node 권한 (보안 3종 해제)
❌ `new BrowserWindow({ webPreferences: { nodeIntegration: true, contextIsolation: false } })` — 옛 튜토리얼의 표준 복붙
✅ 기본값 유지(`contextIsolation: true`, `nodeIntegration: false`, `sandbox: true`) + 필요한 기능만 preload에서 `contextBridge.exposeInMainWorld`로 노출
**왜**: 렌더러의 XSS 한 방이 `require('child_process')`로 직결 — 웹이면 세션 탈취로 끝날 사고가 데스크톱에선 사용자 PC 장악이 된다. Slack·Discord 등 주요 앱들의 버그바운티 RCE 보고가 대부분 이 경계 설정 결함이었다.

### 2. IPC 만능 통로
❌ `ipcMain.handle('invoke', (e, fnName, args) => services[fnName](...args))` — 렌더러가 메인의 아무 함수나 호출하는 범용 게이트
✅ **채널별 좁은 계약**: `ipcMain.handle('file:save', validated handler)` 식으로 기능 단위 등록 + preload에서 그 채널만 함수로 노출 + 인자 검증(렌더러 입력은 불신)
**왜**: 범용 게이트는 안티패턴 1을 우회 복원한 것이다 — contextIsolation을 켜도 IPC가 만능이면 공격면은 그대로. 채널 목록이 곧 렌더러의 권한 명세서가 되게 설계한다.

### 3. 메인 프로세스 블로킹
❌ 메인에서 동기 IO(`fs.readFileSync` 대용량)·CPU 계산·`dialog.showMessageBoxSync` 남용
✅ 메인은 **창 관리·OS 통합·IPC 중개만**. 무거운 작업은 `utilityProcess`(또는 worker_threads)로, IO는 async로
**왜**: 메인 프로세스가 막히면 모든 창의 입력·메뉴·창 이동까지 전부 정지한다(렌더러가 멀쩡해도). "앱 전체가 가끔 빳빳해짐"의 표준 원인 — 단일 관리실에 줄 세우는 구조라 증폭된다.

### 4. 창 닫힘 ≠ 해제 (메모리 누수)
❌ 닫힌 BrowserWindow 참조를 배열에 보관 / 메인에 등록한 이벤트 리스너를 창 수명과 무관하게 누적
✅ `win.on('closed', () => { win = null; 관련 리스너·타이머 해제 })` — 창 수명에 묶인 자원의 대응표 관리. 장수 앱(트레이 상주형)은 주기적 메모리 프로파일
**왜**: Electron 앱은 브라우저 탭과 달리 수 주 단위로 살아있다 — 작은 누수도 복리로 쌓여 "며칠 켜두면 1GB"가 된다. 창 객체는 Chromium 프로세스 전체를 물고 있어 참조 하나가 수십 MB.

### 5. 번들에 전부 동봉
❌ devDependencies까지 포함된 node_modules·소스맵·미사용 로케일을 그대로 패키징 — 300MB 설치본
✅ electron-builder의 `files` 화이트리스트 + 렌더러 코드는 번들러로 빌드(트리셰이킹) + `asar` 기본 — 산출물 목록을 명시 관리
**왜**: 설치본 크기는 다운로드 이탈률·업데이트 트래픽·디스크 평판에 직결. "Electron이라 무겁다"의 상당 부분은 런타임(~100MB)이 아니라 부주의한 동봉분이다.

### 6. 서명·검증 없는 자동 업데이트
❌ 자체 서버에서 zip 받아 교체하는 수제 업데이터 / 코드 서명 생략
✅ electron-updater(서명 검증 내장) + OS별 코드 서명(Windows Authenticode·macOS notarization) — 서명 없으면 업데이트 채널이 곧 악성코드 배포 채널
**왜**: 업데이트는 "원격에서 코드를 받아 실행"하는 기능이다 — TLS만으론 서버 탈취 시 무방비. 서명 검증은 공급망 공격의 마지막 방어선이고, OS 경고창(SmartScreen·Gatekeeper) 회피를 위해서도 필수.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 보안 3종 | contextIsolation:true · nodeIntegration:false · sandbox:true — 예외는 창 단위 근거 문서화 | 안티패턴 1 |
| IPC | 범용 채널 0개 — 기능당 1채널 + 인자 검증 | 안티패턴 2 |
| 원격 콘텐츠 | 외부 URL 로드 창은 preload 최소 + `webSecurity` 유지 + 네비게이션 화이트리스트 | 공식 체크리스트 |
| 설치본 크기 | 런타임 제외 앱 분이 수십 MB 넘으면 동봉 목록 감사 | 안티패턴 5 |
| 상주 메모리 | idle 시 기준선 기록 → 주 단위 증가 추세면 누수 조사 | 안티패턴 4 |

## 워크플로우 (Electron 작업 1건)

1. **권한 경계 먼저** — 이 기능이 렌더러에 필요로 하는 OS 능력을 나열 → 각각 IPC 채널 1개로 계약화(범용 통로 금지).
2. **작성** — 메인은 `src/main/`, preload는 `src/preload/`, 렌더러는 `src/renderer/` 식 프로세스별 분리(프로젝트 기존 구조 우선). 기존 파일 덮어쓰기 대신 Edit.
3. **검증 (copy-paste)**:
   ```
   grep -rEn "nodeIntegration\s*:\s*true|contextIsolation\s*:\s*false|sandbox\s*:\s*false" src/   # 1차 방어선: 보안 3종 위반 즉시 검출(공백 변형 포함)
   npm run build && npm start            # 패키징 전 동작 확인
   ```
   - 정적 보안 스캐너 `electronegativity`(Doyensec)는 한때 표준이었으나 **유지보수 중단 상태**(마지막 의미있는 릴리스 2023년경, 최신 Electron 빌드에서 깨짐 보고 다수, 공식 보안 문서 권장 목록에서도 빠짐) — 신규 도입 권장 불가. 후속은 상용 ElectroNG(동일 Doyensec). grep 기반 수동 점검 + 공식 [Security 체크리스트](https://www.electronjs.org/docs/latest/tutorial/security) 대조가 현실적 1차선.
4. **출고 전** — 설치본 크기 확인 + 보안 3종 grep 재확인 + 자동 업데이트 서명 경로 점검.

## 출력 템플릿

```
## [기능] Electron 구현
### 권한 경계: <렌더러에 노출한 IPC 채널 목록 (전수)>
### 프로세스 배치: <메인/유틸리티/렌더러에 둔 것과 이유>
### 검증: $ 보안 grep → <결과> / 동작 확인 <1줄>
### 확인 필요
```

### 작성 예시

```
## 로컬 로그 뷰어 기능 (가정)
### 권한 경계: 채널 2개 — 'log:list'(디렉토리 고정·경로 인자 없음), 'log:read'(파일명 화이트리스트 검증) — 임의 경로 읽기 불가 설계
### 프로세스 배치: 파일 읽기는 메인(async) / 1GB+ 로그 파싱은 utilityProcess / 렌더러는 표시만
### 검증: $ grep 보안 3종 위반 → 0건 / 500MB 로그 열며 창 드래그 → 멈춤 없음 확인
### 확인 필요: 코드 서명 인증서 보유 여부 (배포 전 필수)
```

❌ "fs가 안 불려지네 → nodeIntegration: true 켜기" (검색 1등 답변 복붙 — 2018년 답)
✅ "필요한 건 '저장' 하나 → preload에 saveFile만 노출 — 권한은 기능 단위로"

### 사용자가 권고를 거부하면

- "개인용 도구라 보안 설정 풀고 빠르게" → 외부 콘텐츠를 절대 안 띄우는 로컬 전용이면 리스크가 실제로 낮다 — 그 전제 1줄 기록 후 동의(전제가 깨지는 순간 재논의 조건부).
- "코드 서명 비용 아깝다" → 사내·개인 배포면 존중 + OS 경고 안내, 공개 배포면 신뢰 비용 1줄 경고 후 기록(partial).
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

### 판단 불가 시 (확인 절차)

보안 설정 완화나 배포 경로처럼 되돌리기 비싼 결정이 불확실하면 멈추지 말고 묶어서 물어본다(추측 진행 금지):
- **누가**: 사용자(또는 프로젝트 CLAUDE.md 소유자) — 배포 대상·서명 인증서·외부 콘텐츠 로드 여부를 아는 주체.
- **언제**: 보안 3종을 끄려 할 때·자동 업데이트/서명 경로를 정할 때·렌더러가 외부 URL을 로드할지 모호할 때, 코드 작성 전.
- **어떻게**: "현재 결정 / 후보안 / 근거 / 기대 답변" 4요소로. 예) "이 창이 외부 URL을 로드합니까? 로드하면 preload 최소+네비게이션 화이트리스트가 필수라 IPC 설계가 달라집니다 — 로컬 전용/외부 로드 중 어느 쪽입니까?"
- **기대값**: 배포 대상(개인/사내/공개)·외부 콘텐츠 여부·서명 인증서 보유 중 하나. 받으면 그 값으로 확정 진행, 못 받으면 가장 보수적 가정(보안 3종 유지·외부 로드 가정·서명 필수)으로 진행하고 그 가정을 1줄 명시(partial).

## 실전 케이스 — 메신저 앱들의 XSS→RCE 버그바운티 연쇄 (2019~2020 공개 보고서)

Slack·Discord 등 Electron 기반 메신저들이 버그바운티로 공개한 RCE 체인의 공통 골격: ① 메시지 렌더링의 XSS(웹이면 여기서 끝) ② 렌더러에 잔존한 Node 접근 경로(설정 미흡 또는 IPC 우회) ③ 결과: 메시지 한 통으로 수신자 PC 코드 실행. Discord 사례는 contextIsolation 미적용 + 임베드 iframe 체인으로 RCE까지 도달(보상금 지급·공개). 교훈: ① 데스크톱에서 XSS의 등급은 '치명'으로 승격된다 — 웹 감각으로 심각도를 매기면 틀림 ② 방어는 XSS 차단(dev-web-security)과 **권한 경계(이 스킬)** 의 이중벽 — 한 겹은 뚫린다고 가정 ③ 보안 3종 기본값은 이 역사 위에 강화된 것이니 끄는 쪽이 입증 책임을 진다. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — 메신저 RCE 체인 · 메인 블로킹 · 수제 업데이터 사고 (코어스펙 1겹)

**1차 출처 (공식, 웹 확인 2026-06)**
- Electron 공식 Security 튜토리얼 — https://www.electronjs.org/docs/latest/tutorial/security — 보안 3종 기본값(contextIsolation 12.0+·nodeIntegration off 5.0+·sandbox 20.0+)·17개 체크리스트의 1차 근거
- Electron Process Sandboxing — https://www.electronjs.org/docs/latest/tutorial/sandbox — sandbox:true가 렌더러+preload에 거는 제약의 정확한 범위
- Electron Code Signing — https://www.electronjs.org/docs/latest/tutorial/code-signing — Windows Authenticode·macOS notarization 요건 (안티패턴 6). macOS는 Squirrel.Mac 자동업데이트가 **서명 필수**라 선택이 아님
- Electron 릴리스 일정 — https://releases.electronjs.org/schedule — 버전·번들 Chromium/Node 대조표 (버전 라벨 부패 점검용)

## 한계

- 가벼운 트레이 도구·단일 창 유틸이면 Tauri(웹뷰 공유·수 MB) 등 대안이 합리적일 수 있다 — 선택 논의는 라우터에서, 이 스킬은 Electron 확정 후 매뉴얼.
- macOS notarization·Windows 인증서 발급 절차의 최신 요건은 부패가 빠름 — 배포 직전 공식 문서 확인.
- 렌더러 내부 성능(React 렌더 등)은 웹 스킬들 본진.
