---
name: web-browse
description: "WebFetch가 빈 껍데기만 가져오는 JS 렌더링 페이지(SPA, React/Vue/Next CSR 앱, 대시보드, 동적 문서 사이트 등)의 실제 본문을 헤드리스 Chromium으로 렌더링해 가져온다. 사용자가 '이 페이지 내용 봐줘', '여기 명세 좀 읽어줘', '문서 fetch', '본문 추출', 'WebFetch가 내용이 없어', 'JS 렌더링', 'SPA 페이지', 'browse', '브라우저로 열어서' 등을 언급하거나, WebFetch 결과가 빈 div/스켈레톤만 돌아오거나, fetch한 페이지에서 기대한 텍스트가 안 보일 때 트리거. 봇 차단(Cloudflare 챌린지, reCAPTCHA)이나 로그인이 필요한 페이지에는 한계가 있어 그쪽은 WebSearch 폴백 → 안 되면 사용자에게 보고. 검색 결과 목록이 필요할 땐 내장 WebSearch를 먼저 쓰고, 그 결과 링크의 본문 추출 단계에서만 이 스킬을 쓴다."
---

# web-browse — JS 렌더링 페이지 fetch

## 언제 쓰는가

내장 `WebFetch`는 정적 HTML만 가져온다. React/Vue/Svelte/Next(CSR) 같은 SPA는 `<div id="root"></div>`만 받아오고 실제 콘텐츠는 빈 상태로 돌아온다. 이때 이 스킬을 사용해 헤드리스 브라우저로 페이지를 실제 렌더링한 뒤 본문을 추출한다.

**기본 브라우저는 실제 설치된 Google Chrome다 (적극 권장).** `fetch.py`는 `--channel chrome`이 기본값이라 번들 Chromium이 아니라 사용자가 실제로 쓰는 Chrome 바이너리로 렌더링한다. 실제 Chrome은 봇 차단·렌더링 차이가 사용자 환경과 가장 가깝고, 번들 Chromium보다 우회 탐지에 덜 걸린다. Chrome이 설치돼 있지 않으면 자동으로 번들 Chromium으로 폴백한다(stderr에 `[web-browse] channel 'chrome' unavailable; falling back...` 경고). 번들 Chromium을 강제하려면 `--channel chromium`.

**전형적인 신호:**
- WebFetch 결과에 본문 텍스트가 거의 없고 `<script>` 태그만 잔뜩 보임
- 사이트가 Vercel/Netlify/Cloudflare Pages에서 호스팅되는 최신 문서 사이트
- 대시보드, 콘솔, 어드민 UI 같은 클라이언트 라우팅 SPA
- 페이지 소스에는 없는데 브라우저에서는 보이는 텍스트를 찾아야 할 때

**쓰지 말아야 할 때:**
- 정적 HTML/마크다운 문서, GitHub README, MDN 같이 WebFetch로 충분한 경우 (속도 차이가 10배 이상)
- 검색 결과 자체가 필요할 때 → 내장 `WebSearch` 사용. 그 결과의 링크 본문 추출에만 이 스킬을 합쳐 쓴다.
- 로그인이 필요한 페이지, Cloudflare/Akamai 챌린지가 떠 있는 페이지 → 한계 있음. 시도는 가능하나 막히면 사용자에게 알리고 다른 방법(공식 API, RSS, 사용자가 직접 복붙) 제안.

## 실행 방법

`scripts/fetch.py`를 Bash로 호출한다. Python(시스템 python3) + playwright + chromium은 이미 설치돼 있다.

**기본 사용:**
```bash
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL"
```

기본 동작: networkidle까지 대기 → `<body>` 전체의 `inner_text`를 stdout으로 출력. 사용자에게 직접 노출되지 않게 충분히 크면 `--max-chars`로 자른다.

**전체 옵션 일람은** `references/cheatsheet.md` 참고. SKILL.md엔 자주 쓰는 것만 둔다.

## 미설치 환경 설치

`ModuleNotFoundError: No module named 'playwright'` 또는 chromium 캐시(`~/Library/Caches/ms-playwright/chromium-*`) 부재 시:

```bash
python3 -m pip install playwright   # 또는 pipx, uv 환경에 맞춰
python3 -m playwright install chromium
```

신규 머신·새 venv에서 한 번만 실행하면 된다. 시스템 Python에 설치하기 싫으면 venv 만들고 같은 두 줄을 그 venv에서 실행한 뒤, SKILL.md 명령의 `python3`을 해당 venv 인터프리터 경로로 바꿔도 동작한다.

## 출력 규약

호출자(나 또는 다른 스킬)가 결과를 안정적으로 파싱하려면 다음 규약을 알아야 한다.

| 채널 | 내용 |
|------|------|
| **stdout** | 추출된 본문 (text/html/title). 마지막은 항상 줄바꿈 1개. |
| **stderr** | 진단 메시지. 모두 `[web-browse]` prefix. 예: `[web-browse] networkidle timed out; continuing with current DOM`, `[web-browse] screenshot saved: <path>`. 본문 없음. |
| **exit 0** | 정상 (네비게이션 타임아웃은 stderr 경고로 흘리고 0 반환 — DOM이 조금이라도 잡혔으면 성공으로 본다). |
| **exit 2** | 치명적 네비게이션 에러 (DNS 실패, net::ERR_*, invalid URL 등). stdout 비어 있음. |

`--max-chars`로 잘릴 때 stdout 본문 끝에 `\n\n[truncated at N chars]` 마커가 붙는다. 호출자가 잘림을 감지하려면 이 마커를 찾는다.

## Quick Reference

| 상황 | 옵션 |
|------|------|
| 단순 본문 텍스트 추출 | (기본값) `--format text` |
| 특정 영역만 (예: 메인 문서 본문) | `--selector "main"` 또는 `--selector "article"` |
| DOM 구조까지 필요 (링크/속성 분석) | `--format html` |
| 페이지 타이틀만 필요 | `--format title` |
| 콘텐츠가 늦게 들어오는 SPA | `--wait-for "h1"` 같이 보장되는 요소 대기 |
| 무한 로딩으로 networkidle 안 끝남 | `--wait-state domcontentloaded` |
| 시각적 확인이 필요할 때 | `--screenshot /tmp/page.png` (text 추출과 동시 사용 가능) |
| 출력이 너무 길어 컨텍스트 낭비 우려 | `--max-chars 10000` |
| 디버깅용 실제 브라우저 창 띄우기 | `--headful` |
| 실제 Chrome 대신 번들 Chromium 강제 | `--channel chromium` (기본은 실제 Chrome) |

## 워크플로우

1. **먼저 WebFetch를 시도한다.** 정적이면 그게 훨씬 빠르고 싸다. 본문이 비어 있거나 스크립트뿐이면 이 스킬로 넘어온다.
2. **URL과 추출 목표를 정한다.** 페이지 전체가 필요한지, 특정 섹션(예: API 명세의 `main`)만 필요한지 판단.
3. **첫 시도는 기본 옵션으로.** 결과가 비어 있거나 잘리면 `--wait-for` 또는 `--selector`를 추가.
4. **결과가 길면 `--max-chars`로 컨텍스트 보호.** 사용자가 전체를 원하면 파일로 저장 후 필요 부분만 Read.
5. **막힌 페이지(Cloudflare 챌린지, 403 캡차)는 우회 시도하지 말고 보고.** 봇 우회는 약관 위반·법적 회색지대이므로 사용자에게 옵션(공식 API, 수동 복붙)을 제시한다.

## 증상별 분기 테이블

첫 시도가 빈 결과나 부분 결과면 산문에서 옵션을 뒤지지 말고 이 표를 따른다.

| 증상 | 1차 조치 | 그래도 실패하면 |
|------|---------|----------------|
| 본문이 거의 비어 있음 (text < 200자) | `--wait-for "h1"` 또는 보장되는 핵심 selector 대기 | `--wait-state domcontentloaded --timeout 60000` 로 폴백 |
| 일부 섹션만 나오고 나머지 누락 | `--selector "main"` 등으로 영역 명시 | `--format html` 로 DOM 받아 정확한 selector 재선정 |
| 네비게이션이 networkidle에서 끝나지 않음 (timeout) | `--wait-state domcontentloaded` | `--wait-state load` + `--timeout 60000` |
| 결과가 잘림 (`[truncated at N chars]` 마커 확인) | 더 큰 `--max-chars` 지정 | 파일로 저장 (`> /tmp/page.txt`) 후 `Read`/`grep` |
| 캡차·챌린지·로그인 화면이 추출됨 | 시도 중단 → WebSearch 폴백(아래) | WebSearch도 없으면 사용자에게 공식 API/복붙 제안 |
| `exit 2` 네비게이션 에러 | URL 오타·프로토콜 확인 | 사용자에게 보고. 재시도 1회까지만. |
| 페이지가 사람 눈으로도 이상 | `--screenshot /tmp/debug.png` 로 렌더 결과 확인 | `--headful`로 실제 창 띄워 사용자와 함께 진단 |

## 봇 차단·로그인 시 fallback 순서

본문 추출이 막혔을 때 포기 전에 아래 순서대로 시도한다.

### 1단계 — 메타 정보 회수 (항상 먼저)

1. **타이틀만** — `--format title` 은 챌린지 페이지에서도 페이지 자체 타이틀이 나오는 경우가 많다.
2. **스크린샷** — `--screenshot /tmp/blocked.png` 로 화면 캡처. 챌린지인지 진짜 콘텐츠인지 사용자가 눈으로 확인 가능.
3. **HTML 메타 태그** — `--format html --selector "head"` 로 `<meta>` description·og:* 만 회수. 본문 차단이어도 head는 통과하는 사이트가 많다.

### 2단계 — WebSearch 폴백

봇 차단으로 본문 추출이 불가능하면 **WebSearch로 같은 정보를 검색**한다.

**검색어 구성 방법:**
- 사이트 도메인 + 페이지 제목/경로에서 추출한 핵심 키워드
- 예: `site:docs.example.com API reference authentication` 또는 `example.com 페이지제목 기능명`

**WebSearch 폴백의 한계 (명시하고 사용):**
- 공개 검색엔진에 인덱싱된 정보만 회수 가능 — 로그인 후 페이지, 내부 docs, 실시간 대시보드는 여전히 불가
- SPA 동적 콘텐츠는 검색엔진도 못잡는 경우가 많음 (SSR/pre-render된 페이지만 인덱싱됨)
- 검색 결과가 최신 버전 정보가 아닐 수 있음

WebSearch로 충분한 정보를 회수했으면 그걸로 진행하고 "봇 차단으로 직접 접근 불가, 검색 결과 기반으로 답변"임을 명시.

### 3단계 — 사용자에게 넘기기

1·2단계로도 정보가 부족하면 "이만큼은 확보했음"을 보고하고 의사결정(공식 API 사용, 수동 복붙, 포기)을 사용자에게 넘긴다. 본문 우회 시도(쿠키 위조, UA 회전, 프록시 등)는 이 스킬 범위 밖이다.

## 결과 핸들링 패턴

**짧은 페이지(블로그 글, 명세 한 페이지):**
```bash
python3 ~/.claude\skills\web-browse\scripts\fetch.py "https://example.com/spec" --max-chars 20000
```
바로 stdout 받아 분석.

**긴 페이지 / 여러 페이지를 비교해야 할 때:**
```bash
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL" > /tmp/page1.txt
```
파일로 저장 후 `Read` 또는 `grep`으로 필요 부분만 가져온다.

**SPA가 늦게 그려질 때:**
```bash
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL" \
  --wait-for "main article" --timeout 45000
```

## 한계 명시

다음은 이 스킬로 안 되거나 어렵다. 해당 상황이면 시도 전에 사용자에게 알린다.

- **Cloudflare/Akamai/PerimeterX 봇 차단**: 챌린지 페이지만 받아옴. 우회는 지원하지 않는다.
- **로그인 필요 페이지**: 쿠키/세션 수동 주입이 필요. 이 스킬은 기본적으로 익명 세션만 쓴다.
- **reCAPTCHA / hCaptcha**: 풀 수 없다.
- **DRM 콘텐츠 / 결제 페이지**: 동작 보장 안 함.
- **JS가 무한 polling 하는 사이트**: `networkidle`이 끝나지 않을 수 있음 → `--wait-state domcontentloaded`로 우회.

## 디버깅

페이지가 이상하게 추출되면:
1. `--screenshot /tmp/debug.png` 추가해서 실제로 어떻게 렌더됐는지 본다 (Read tool로 PNG 열람 가능).
2. `--format html`로 DOM을 한 번 본 뒤 정확한 selector 잡기.
3. `--headful` 로 실제 창 띄워서 사람 눈으로 확인 (로컬에서만).

## 처음 막혔을 때 5분 walkthrough

신규 시도가 빈 결과로 돌아왔을 때 우왕좌왕 안 하도록 5분 안에 끝낼 경로.

**1분 — 일단 기본으로 한 번:**
```bash
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL" --max-chars 3000
```
결과가 본문이면 끝. 아래는 본문 아닐 때만.

**2분 — 화면 확인:**
```bash
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL" \
  --screenshot /tmp/wb-debug.png --max-chars 3000
```
PNG를 Read 툴로 열어 봄. 셋 중 하나로 분기:
- 정상 화면인데 텍스트만 짧음 → **3분 분기 A**
- 로딩 스피너·스켈레톤 그대로 → **3분 분기 B**
- 챌린지·캡차·로그인 화면 → 더 시도 말고 **3분 분기 C**

**3분 분기 A — 영역 안 잡힘:** `--format html --selector body --max-chars 30000` 으로 DOM 한 번 본 뒤, 정확한 selector(`article`, `main`, `[role=main]`, `#__next main` 등) 찾아서 `--selector` 명시 재시도.

**3분 분기 B — 콘텐츠 아직 안 그려짐:** `--wait-for "<핵심 선택자>"` + `--timeout 60000` 추가. 아직 비면 `--wait-state domcontentloaded` 로 폴백 (networkidle이 long polling으로 안 끝나는 케이스).

**3분 분기 C — 챌린지·봇 차단 확인됨:**
1. title/head/screenshot 회수 (1단계 메타 회수)
2. `WebSearch`로 해당 URL의 도메인 + 핵심 키워드 검색. 결과가 충분하면 그걸로 답하고 "봇 차단으로 직접 접근 불가, 검색 기반 답변" 명시.
3. 로그인 필요 페이지 / 내부 docs / SPA 동적 콘텐츠라면 WebSearch도 무의미 → 바로 사용자에게 넘긴다.

**5분 — 그래도 안 되면 보고:** "X를 시도했고 Y가 막힘. 공식 API / 사용자가 직접 복붙 / 포기 중 어느 쪽 원하는지" 사용자에게 넘긴다. 더 시도하지 않는다.
