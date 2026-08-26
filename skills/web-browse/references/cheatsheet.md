# web-browse — fetch.py 옵션 치트시트

`scripts/fetch.py` 전체 옵션 일람. SKILL.md Quick Reference보다 상세함.

## 위치

`~/.claude\skills\web-browse\scripts\fetch.py`

## 인자 한눈에

| 인자 | 기본값 | 의미 |
|------|--------|------|
| `URL` (위치) | — | 필수. fetch할 페이지. 따옴표 권장. |
| `--format` | `text` | `text` / `html` / `title` |
| `--selector` | (전체 body) | CSS selector로 추출 범위 지정 |
| `--wait-for` | (없음) | 이 selector가 나타날 때까지 추가 대기 |
| `--wait-state` | `networkidle` | `load` / `domcontentloaded` / `networkidle` |
| `--timeout` | `30000` | ms 단위 |
| `--screenshot` | (없음) | PNG 저장 경로. text 추출과 동시 사용 가능 |
| `--user-agent` | Chrome 131 macOS | 커스텀 UA |
| `--channel` | `chrome` | 실제 설치된 Google Chrome로 렌더링(권장). 미설치 시 번들 Chromium 자동 폴백. `chromium`으로 번들 강제 |
| `--headful` | off | 실제 창 띄우기 (디버깅용) |
| `--max-chars` | `0` (무제한) | 출력 잘림. 끝에 `[truncated at N chars]` 마커 |

## 자주 쓰는 조합

```bash
# 1) 가장 단순: 본문 텍스트
python3 ~/.claude\skills\web-browse\scripts\fetch.py "https://example.com"

# 2) 영역 명시 + 컨텍스트 보호
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL" \
  --selector "main" --max-chars 20000

# 3) 늦게 그려지는 SPA
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL" \
  --wait-for "article h1" --timeout 45000

# 4) networkidle 안 끝나는 사이트 (long polling)
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL" \
  --wait-state domcontentloaded

# 5) DOM 구조 분석 (selector 잡기 전 정찰)
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL" \
  --format html --max-chars 30000 > /tmp/dom.html

# 6) 차단·로그인 페이지에서 메타만 회수
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL" --format title
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL" \
  --format html --selector head --max-chars 5000
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL" \
  --screenshot /tmp/blocked.png --max-chars 0

# 7) 시각 디버깅
python3 ~/.claude\skills\web-browse\scripts\fetch.py "URL" \
  --screenshot /tmp/debug.png --headful
```

## exit code

| 코드 | 의미 |
|------|------|
| `0` | 성공 (네비게이션 타임아웃은 stderr 경고로만 흘리고 0) |
| `2` | 치명적 네비게이션 에러 (DNS 실패, net::ERR_*, invalid URL) |

stderr 메시지는 모두 `[web-browse]` prefix. 본문은 stdout만.

## --wait-state 선택 가이드

| 값 | 종료 조건 | 적합한 사이트 |
|----|-----------|--------------|
| `load` | `load` 이벤트 | 거의 안 씀, 가장 빠름 |
| `domcontentloaded` | DOM 파싱 완료 | long polling·WebSocket으로 networkidle 안 끝나는 사이트 |
| `networkidle` (기본) | 500ms 동안 네트워크 idle | 대부분의 SPA, 가장 안전 |

## --format 별 동작

- `text` — `--selector` 영역의 `inner_text()` (CSS `display: none` 텍스트는 제외, 시각적으로 보이는 것만)
- `html` — `--selector` 있으면 그 요소의 `innerHTML`, 없으면 페이지 전체 `content()` (전체 HTML)
- `title` — `<title>` 태그 텍스트 (`--selector` 무시)

## 한계 (재확인)

- Cloudflare 챌린지·reCAPTCHA·hCaptcha → 우회 안 함
- 로그인 페이지 → 익명 세션만 지원. 쿠키 주입은 직접 fetch.py 수정 필요
- DRM·Widevine → 동작 보장 안 함
- 결제 페이지·OS 다이얼로그 → 처리 불가
