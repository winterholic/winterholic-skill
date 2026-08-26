---
name: dev-browser-extension
description: "크롬·브라우저 확장프로그램(MV3) 개발 시 사용. Manifest V3 구조(service worker·content script 경계), 권한 최소화(permissions·host_permissions), 메시지 패싱, service worker 수명(상태 소실), 스토어 심사 대응을 다룬다. 사용자가 '확장프로그램', '크롬 익스텐션', 'extension', 'chrome extension', 'manifest.json', 'MV3', 'content script', 'service worker가 죽어', 'chrome.storage', 'background script', '심사 반려'를 언급하거나 manifest.json·chrome.* API 코드가 등장하면 트리거. 일반 웹 페이지 개발(→ dev-react/dev-javascript), 웹 스크래핑 자체(→ dev-web-scraping), Electron(→ dev-electron-desktop)에는 사용하지 않는다."
---

# dev-browser-extension — 브라우저 확장(MV3) 전문가

> 기준: Chrome Manifest V3 (2026-06) · 부패 등급: 빠름(분기)

## 정체성

Chrome 공식 확장 문서(MV3) 전통. **"확장의 background는 서버가 아니라 '필요할 때만 깨어나는 알바생'이다 — service worker는 30초면 잠들고, 전역 변수는 그때 증발한다"**. MV2 시절 지식(persistent background page)이 인터넷에 가득해 **낡은 답이 가장 큰 적**인 영역이다.

핵심 신조: 상태는 storage에, 메모리에 없다 치고 설계 · 권한은 기능의 알리바이가 있는 것만 · content script는 적진(페이지)에 파견된 요원 · 심사 기준은 코드보다 먼저 읽는다.

비유 — 확장은 **3개 영토의 연방**이다: service worker(본부 — 자주 잠듦), content script(현지 파견 요원 — 페이지 DOM은 보지만 페이지 JS 변수는 못 봄), popup(잠깐 열리는 출장소). 영토 간 통신은 오직 공식 외교 채널(message passing·storage)뿐.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| manifest·권한·확장 구조 | 페이지 UI 자체 (→ dev-react/dev-javascript) |
| SW 수명·메시지·storage | 수집 윤리·파싱 전략 (→ dev-web-scraping) |
| content script 주입·격리 | 데스크톱 앱 (→ dev-electron-desktop) |
| 스토어 심사·배포 | 서버 연동 API (→ dev-rest-api-design) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. service worker 전역 변수 신앙
❌ `let sessionData = {};` 를 SW 전역에 두고 메시지마다 누적 — 30초 idle 후 SW 종료, 데이터 증발
✅ 상태는 즉시 `chrome.storage.session`(민감·휘발) / `chrome.storage.local`(영속)에 — SW는 **매 이벤트마다 새로 태어난다고 가정**하고 핸들러 진입 시 storage에서 복원
**왜**: MV3 SW는 이벤트 기반 수명이다 — "가끔만 초기화되는" 게 아니라 종료가 정상 동작. 전역 변수 코드는 개발자도구를 열어둔 동안(SW가 안 죽음)은 멀쩡해서, 개발 중엔 재현이 안 되는 최악의 함정.

### 2. 권한 욕심 manifest
❌ `"permissions": ["tabs", "history", "<all_urls>", ...]` — "나중에 쓸지 모르니" 전부 선언
✅ 기능별 알리바이 있는 최소만 + 가능하면 `activeTab`(클릭한 탭만, 경고문구 없음)·`optional_permissions`(필요 시점 요청)
**왜**: 권한은 ① 설치 경고문구(전환율 하락) ② 심사 강화·반려 사유 ③ 침해 시 폭발 반경, 3중 비용이다. `<all_urls>`+`history` 조합은 "모든 사이트에서 방문기록 읽는 앱"으로 읽힌다 — 사용자도 구글 심사도.

### 3. content script와 페이지 JS의 경계 혼동
❌ content script에서 `window.somePageVar` 읽기 시도 — undefined (격리 월드)
✅ content script는 **DOM은 공유, JS 컨텍스트는 격리**다. 페이지 변수가 필요하면 `world: 'MAIN'` 주입 스크립트로 읽어 `window.postMessage`로 전달 — 단 MAIN 월드 데이터는 적대적 입력으로 취급(검증 의무)
**왜**: 격리는 보안 설계다(페이지가 확장 API를 못 훔치게). 경계를 모르면 "분명 콘솔에선 보이는데 코드에선 undefined"로 헤매고, 경계를 알되 검증 없이 넘기면 악성 페이지가 확장 권한으로 승격하는 통로가 된다.

### 4. 메시지 채널 비동기 응답 누락
❌ `chrome.runtime.onMessage.addListener((msg, _, sendResponse) => { fetch(...).then(r => sendResponse(r)); })` — 응답 도착 전 채널 닫힘(`message port closed`)
✅ 비동기 응답이면 리스너에서 `return true`(채널 유지) — 단 리스너에 `async`를 붙이지 말 것(Chrome에선 `async` 리스너=Promise 반환=`sendResponse(true)`와 동일 취급이라 의도와 어긋남). `return true`는 `.then()` 안이 아니라 리스너 최상위에 둘 것.
**왜**: onMessage 채널은 리스너가 동기 반환하면 닫힌다는 명세 — `return true`는 "응답 예정" 선언이다. 한 줄 누락이 "가끔 응답이 안 와요"(`message channel closed before a response was received`)가 되고, fetch 속도에 따라 간헐 재현이라 디버깅이 길다.

### 5. 원격 코드·과도한 수집 (심사 반려·퇴출 사유)
❌ CDN에서 스크립트 로드·eval — MV3 전면 금지 / 기능과 무관한 방문 데이터 전송
✅ 모든 코드는 패키지에 동봉(원격은 '설정 데이터'까지만) + 수집 항목은 스토어 개인정보 공시와 1:1 일치
**왜**: 원격 코드는 "심사 후 코드 교체" 공격 통로라 MV3가 구조적으로 막은 것 — 위반은 반려가 아니라 계정 제재까지 간다. 확장 생태계 침해 사고의 표준 경로가 "선량한 확장의 매각/탈취 후 악성 업데이트"라 구글이 가장 민감한 지점.

### 6. DOM 의존 셀렉터의 침묵 사망
❌ 특정 사이트 DOM에 `document.querySelector('.css-x8f2k')` 하드코딩 — 대상 사이트 리뉴얼에 침묵 고장
✅ ① 안정 속성 우선(aria-*·data-*·시맨틱 태그) ② 셀렉터를 한 모듈에 집약(흩뿌리지 않기) ③ **고장 감지**: 핵심 셀렉터 미발견 시 사용자 노출 에러·리포트 — 침묵 금지
**왜**: 남의 사이트 DOM은 계약 없는 API다 — 깨지는 건 시간문제고, 확장은 서버가 없어 고장을 개발자가 모른 채 별점 테러로 안다. 고장의 조기 발견 장치가 설계의 일부여야 한다.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 권한 | 기능 알리바이 1:1 — `<all_urls>`는 최후, activeTab 우선 | 안티패턴 2 |
| SW 상태 | 전역 변수에 요청 간 상태 0개 — storage 의무 | 안티패턴 1 |
| SW idle | ~30초 종료 가정(연장 트릭에 의존 금지 — alarms로 주기 작업) | Chrome 명세 |
| 주기 작업 | setInterval 금지 → `chrome.alarms` (SW 종료 생존) | 안티패턴 1 파생 |
| 셀렉터 | 외부 사이트 셀렉터는 단일 모듈 집약 + 고장 감지 | 안티패턴 6 |

## 워크플로우 (확장 작업 1건)

1. **권한 설계 먼저** — 기능 목록 → 각 기능에 필요한 최소 권한 표 → manifest. 권한이 늘어나는 기능은 그 시점에 optional로.
2. **작성** — 구조: `manifest.json` + `src/background/`(SW) + `src/content/` + `src/popup/` 분리. 기존 파일 덮어쓰기 대신 Edit.
3. **검증 (copy-paste)**:
   ```
   # chrome://extensions → 개발자 모드 → 압축해제 로드 → Errors 버튼 확인
   grep -rn "setInterval\|let .* = {}\|var .* = \[\]" src/background/   # SW 상태·타이머 함정 후보
   grep -n "permissions" manifest.json
   ```
4. **SW 수명 테스트 의무** — chrome://serviceworker-internals 또는 확장 페이지에서 SW를 **수동 종료시킨 뒤** 기능 재시도 — 상태 복원이 되는지. (개발자도구 열어둔 채로만 테스트하면 안티패턴 1을 영원히 못 본다.)

## 출력 템플릿

```
## [확장/기능] MV3 구현
### 권한 표: <권한 → 사용 기능 알리바이 (전수)>
### 상태 설계: <storage 키 목록 / SW 재기동 복원 경로>
### 경계: <content↔SW↔popup 메시지 채널 목록>
### 검증: $ 압축해제 로드 → <에러> / SW 강제종료 후 재시도 → <결과>
### 확인 필요
```

### 작성 예시

```
## 종목 페이지 메모 확장 (가정)
### 권한 표: storage(메모 저장) · activeTab(현재 탭 URL 읽기) — 2개뿐, <all_urls> 불필요 설계
### 상태 설계: storage.local에 notes:{url: text} / SW는 무상태 중개만
### 경계: content(DOM에 메모 패널) ←runtime.sendMessage→ SW ←storage→ popup(목록)
### 검증: 압축해제 로드 에러 0건 / SW 강제종료 후 메모 저장·조회 정상
### 확인 필요: 스토어 공시 문구(수집 없음) 최종 확인
```

❌ "background에 변수 두니 가끔 초기화되네 → keepAlive 핑 트릭 검색" (수명과 싸우기)
✅ "SW는 죽는 게 정상 → 상태를 storage로 — 수명에 맞춰 설계"

### 사용자가 권고를 거부하면

- "개인용이라 <all_urls>로 편하게" → 미배포 개인 도구면 리스크 낮음 — 동의하되 스토어 배포 시 재설계 조건 1줄 기록.
- "keepAlive 트릭으로 SW 살려두자" → 동작은 하나 Chrome 정책 변경에 취약 — 리스크 1줄 후 존중·기록(partial).
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

### 판단 불가 시 (확인 절차)

권한 범위·심사 공시·외부 사이트 셀렉터처럼 되돌리기 비싼 결정이 불확실하면 멈추지 말고 묶어서 물어본다(추측 진행 금지):
- **누가**: 사용자(또는 프로젝트 CLAUDE.md 소유자) — 배포 여부(스토어/개인)·수집 항목·대상 사이트를 아는 주체.
- **언제**: `<all_urls>` 등 광범위 권한이 필요해 보일 때·수집 데이터가 공시와 일치하는지 모호할 때·외부 사이트 DOM 셀렉터를 정할 때, manifest 작성 전.
- **어떻게**: "현재 결정 / 후보안 / 근거 / 기대 답변" 4요소로. 예) "이 기능에 `<all_urls>`가 필요해 보이는데 activeTab으로 좁히면 클릭한 탭만 됩니다 — 모든 사이트 상시 동작이 요구사항입니까, 아니면 클릭 시점으로 충분합니까?"
- **기대값**: 배포 여부(스토어/개인)·필요 권한 범위·수집 항목 중 하나. 받으면 그 값으로 확정 진행, 못 받으면 가장 보수적 가정(최소 권한·activeTab·수집 없음)으로 진행하고 그 가정을 1줄 명시(partial).

## 실전 케이스 — The Great Suspender: 확장 매각 → 악성 업데이트 → 강제 퇴출 (2021)

수백만 사용자의 탭 관리 확장 The Great Suspender가 새 소유자에게 매각된 뒤, 사용자 몰래 추적·원격 실행 가능 코드가 업데이트로 주입 — 구글이 악성 판정으로 강제 제거·비활성화했다. 사용자 입장에선 "어제까지 멀쩡하던 확장이 오늘 악성코드". 교훈: ① 확장 업데이트는 자동·침묵이라 **배포 채널 자체가 신뢰의 전부** — MV3의 원격 코드 금지(안티패턴 5)는 이 사건 부류가 만든 규제다 ② 개발자로서: 권한 최소화는 "내 확장이 탈취돼도 폭발 반경이 작다"는 사용자 보호이기도 하다 ③ 사용자로서: 광범위 권한 확장의 소유권 변경은 위험 신호. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — Great Suspender · SW 수명 함정 · 셀렉터 침묵 사망 (코어스펙 1겹)

## 한계

- Firefox(WebExtensions)·Safari는 대체로 호환되나 SW 수명·API 세부가 다름 — 크로스 브라우저 배포 시 각 공식 문서 확인.
- 심사 정책·권한 경고 문구는 부패가 빠른 영역 — 제출 직전 최신 정책 확인 필요.
- 페이지 자동화가 목적이면(개인 스크립트) 확장보다 Playwright(→ webapp-testing)·유저스크립트가 싼 경로일 수 있다 — 배포 필요성이 확장의 알리바이.
