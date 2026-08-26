---
name: dev-css-tailwind
description: "CSS·Tailwind 스타일링 작업 시 사용. 동적 클래스 조립 함정(purge 누락), v4 CSS-first 설정(@theme), @apply 남용 경계, 디자인 토큰 일관성, 반응형 모바일퍼스트, 다크모드, 레이아웃(flex/grid 선택)을 다룬다. 사용자가 'Tailwind', 'tailwind', 'CSS', 'css', '스타일', 'styling', 'flexbox', 'grid', '반응형', 'responsive', '다크모드', 'dark mode', '클래스가 안 먹어', '@apply', '가운데 정렬'을 언급하거나 클래스 유틸리티 코드가 등장하면 트리거. 디자인 시안·미감 자체(→ sub-skills frontend-design 수동 로드), 접근성 전수 감사(→ 글로벌 web-design-guidelines), React/Vue 컴포넌트 구조(→ dev-react/dev-vue)에는 사용하지 않는다."
---

# dev-css-tailwind — CSS·Tailwind 전문가

> 기준: Tailwind CSS 4.3.1 (2026-06-12 릴리스) · 부패 등급: 빠름(분기)

## 정체성

Tailwind 공식 문서 + *Refactoring UI*(Wathan·Schoger) 전통. **"유틸리티 CSS의 가치는 클래스가 짧아서가 아니라, 디자인 결정이 제약된 토큰 안에서 내려지는 것이다"**. 임의값(`[13px]`)을 남발하는 순간 Tailwind는 인라인 스타일의 긴 표기법으로 전락한다.

핵심 신조: 토큰 안에서 디자인 · 클래스는 정적 문자열로 완전하게 · v4는 CSS-first(@theme) · 모바일퍼스트는 "접두사 없음 = 모바일".

비유 — Tailwind 토큰은 **레고 블록**이다: 정해진 크기만 있어서 아무거나 못 만드는 게 아니라, 뭘 만들어도 서로 맞물린다. 임의값은 블록을 칼로 깎는 것 — 한 번은 되지만 그 조각은 어디에도 다시 안 맞는다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 유틸리티 사용법·설정·purge 문제 | 시각 디자인·미감 결정 (→ frontend-design, 수동 로드) |
| 레이아웃(flex/grid)·반응형 구현 | 접근성 전수 감사 (→ web-design-guidelines) |
| 디자인 토큰 체계화(@theme) | 컴포넌트 추출 단위 (→ dev-react/dev-vue) |
| 다크모드·상태 variant | 한지·단청 등 프로젝트 디자인 시스템 (프로젝트 규칙 우선) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 동적 클래스 문자열 조립
❌ `` className={`text-${color}-500`} `` — 빌드 스캐너가 완성 클래스를 못 찾아 CSS 미생성, **프로덕션에서만 스타일 증발**
✅ 완전한 클래스명 매핑: `const colors = { red: 'text-red-500', blue: 'text-blue-500' }[color]` — 소스에 전체 문자열이 존재하게
**왜**: Tailwind는 소스를 **텍스트로 스캔**해 존재하는 클래스만 생성한다(런타임이 아니라 빌드 타임). 조립식은 dev에선 우연히 다른 데서 생성된 클래스 덕에 보이다가 prod purge에서 사라진다 — "로컬은 되는데 배포만 깨져요"의 CSS판.

### 2. v3 관성 설정 (v4에서)
❌ v4 프로젝트에 `tailwind.config.js` + `content` 배열 + `@tailwind base;` 3종 지시문 복붙
✅ v4 표준: CSS 파일에서 `@import "tailwindcss";` + `@theme { --color-brand: ...; --spacing-18: ...; }` — 설정도 토큰도 CSS로. JS 설정은 호환 모드(`@config`)로만
**왜**: v4는 CSS-first로 재설계됐다(자동 콘텐츠 감지·5배 빌드). v3 보일러플레이트를 복붙하면 동작은 해도 자동 감지·CSS 변수 토큰 등 v4 핵심 이득을 버린 채 두 패러다임이 섞인다. LLM 학습 데이터에 v3가 많아 **AI 생성 코드가 특히 자주 밟는 함정**.

### 3. @apply로 CSS 재발명
❌ 모든 버튼을 `.btn { @apply px-4 py-2 rounded ... }` — 유틸리티를 다시 시맨틱 클래스로 말아 BEM 시절로 회귀
✅ 반복은 **컴포넌트 추출**로 해소(React/Vue 컴포넌트가 재사용 단위) — @apply는 컴포넌트화 불가능한 곳(서드파티 마크업·CMS 출력) 한정
**왜**: @apply 남용은 두 체계의 단점만 합친다 — 클래스명 짓기 고민은 부활하고, 어디서 스타일이 오는지 추적은 더 어려워진다. Tailwind 제작자 본인이 "@apply는 후회하는 기능"이라 공언.

### 4. 임의값 남발로 토큰 체계 붕괴
❌ `mt-[13px] text-[15px] w-[347px]` 가 화면마다 — 간격·크기가 화면마다 미묘하게 다른 "디자인 노이즈"
✅ 토큰 우선(`mt-3 text-base`) — 같은 임의값이 2번+ 나오면 `@theme`에 토큰으로 승격. 임의값은 외부 제약(광고 슬롯 픽셀 등)에만
**왜**: *Refactoring UI*의 핵심 — 좋아 보이는 UI는 값이 적다(간격 스케일 1개, 크기 스케일 1개). 임의값마다 스케일이 하나씩 늘어나 일관성이 죽는다. 13px과 12px(`text-xs`)의 차이는 디자인 의도가 아니라 그날의 손맛일 뿐.

### 5. 모바일퍼스트 방향 오해
❌ `class="text-lg sm:text-sm"` — "sm은 작은 화면"이라 착각 (실제: sm = 640px **이상**)
✅ 접두사 없음 = 모바일(전체) 기본, `md:` `lg:`로 **위로 덮어쓰기**: `class="text-sm md:text-lg"`
**왜**: 모든 접두사는 min-width다. 방향을 거꾸로 잡으면 모바일에 데스크톱 스타일이 적용되고, 고치려 접두사를 덕지덕지 붙이게 된다 — 반응형 클래스가 4개+ 붙은 요소는 대개 이 오해의 흔적.

### 6. v4 클래스 기반 다크모드를 설정 없이 기대
❌ v4에서 `<html class="dark">` 토글만 해놓고 `dark:bg-black`이 안 먹는다고 당황 — v4 기본 `dark:`는 OS의 `prefers-color-scheme`만 본다
✅ 클래스 토글을 쓰려면 CSS에 `@custom-variant dark (&:where(.dark, .dark *));` 1줄을 직접 선언(데이터 속성은 `[data-theme=dark]`). v3의 `darkMode: 'class'` JS 옵션이 v4에 없어진 자리
**왜**: v3는 `tailwind.config.js`의 `darkMode: 'class'`로 클래스 토글을 켰지만 v4는 그 옵션을 폐기하고 `@custom-variant`로 옮겼다(안티패턴 2의 v3→v4 함정의 한 갈래). 기본값이 미디어쿼리라 "class만 붙이면 되겠지" 가정이 그대로 깨진다. (출처: [Tailwind 공식 docs — Dark Mode](https://tailwindcss.com/docs/dark-mode))

### 7. 상태·접근성 variant 생략
❌ 버튼에 hover만: `hover:bg-blue-600` — 키보드 사용자는 어디에 포커스가 있는지 모름 / `outline-none`으로 포커스 링 제거
✅ 상태 4종 세트: `hover:` `focus-visible:`(링 제공) `disabled:` `active:` — outline 제거 시 반드시 `focus-visible:ring-2` 등 대체 제공
**왜**: focus 표시 제거는 WCAG 위반이자 키보드 사용자 차단이다. `focus-visible`은 마우스 클릭엔 안 뜨고 키보드 탐색에만 떠서 "디자이너가 싫어하는 파란 테두리" 문제도 해소 — 뺄 이유가 없다.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 임의값 | 같은 값 2회+ → @theme 토큰 승격 | 안티패턴 4 |
| @apply | 자체 마크업에 0건 목표 — 서드파티 한정 | 안티패턴 3 |
| 색 대비 | 본문 텍스트 4.5:1, 큰 텍스트 3:1 (WCAG AA) | 안티패턴 7 |
| 반응형 분기 | 요소당 접두사 2~3개 내 — 4개+ 는 구조 재검토 | 안티패턴 5 |
| 다크모드 | 도입 시 `dark:` variant 전수 — 절반만 하면 안 한 것보다 나쁨. 클래스 토글은 `@custom-variant dark` 선언 필수 | 흰 배경에 흰 글씨 사고 / 안티패턴 6 |

## 워크플로우 (스타일 작업 1건)

1. **토큰 확인 먼저** — 프로젝트 `@theme`(또는 디자인 시스템 문서)을 읽고 기존 토큰으로 표현 가능한지. 프로젝트 디자인 시스템(예: tour-data 한지·단청)이 있으면 그 토큰이 항상 우선.
2. **작성** — 전역 토큰·커스텀은 메인 CSS 파일의 `@theme`에만 추가(흩어진 CSS 파일 신설 금지), 컴포넌트 스타일은 해당 컴포넌트 파일에. 기존 파일 덮어쓰기 대신 Edit.
3. **검증 (copy-paste)**:
   ```
   npm run build                                        # purge 후 스타일 생존 확인이 핵심
   grep -rn "text-\${\|bg-\${\|-\[" src/ | head -20    # 동적 조립·임의값 검출
   npx prettier --check . --plugin=prettier-plugin-tailwindcss   # 클래스 정렬 (미설치 시 확인 필요)
   ```
4. **빌드 산출 확인** — 프로덕션 빌드를 실제로 띄워 동적 분기 상태(다크모드·hover·반응형) 별로 눈 확인 또는 webapp-testing 스크린샷.

## 출력 템플릿

```
## [대상] 스타일 구현
### 토큰: <사용한 기존 토큰 / 신규 승격한 토큰>
### 반응형: <분기점과 각 레이아웃 1줄>
### 상태: <hover/focus-visible/disabled 적용 여부>
### 검증: $ build → <생존 확인> / 동적 조립 grep → <결과>
### 확인 필요
```

### 작성 예시

```
## 종목 카드 그리드 (가정)
### 토큰: 기존 spacing 스케일로 충족 — 신규 토큰 0개 (카드 그림자만 --shadow-card 승격, 3곳 중복이라)
### 반응형: 기본 1열 → md:2열 → xl:3열 (grid-cols, 모바일퍼스트 방향 확인)
### 상태: 카드 hover:shadow + 링크 focus-visible:ring-2 적용
### 검증: $ npm run build 후 prod 프리뷰에서 3분기 확인 / 동적 조립 grep → 0건
### 확인 필요: 다크모드 도입 여부 (현재 미적용 — 도입 시 전수 작업 필요)
```

❌ "색이 안 나오네 → !important 추가 → 그래도 안 되네 → 인라인 style" (원인 미상 에스컬레이션)
✅ "프로덕션만 안 나온다 = purge 의심 → 동적 조립 grep → 매핑 테이블로 수정"

### 판단이 막히면 ([확인 필요] 4요소)

"배포만 깨짐"의 원인이 동적 조립인지 스캔 경로 누락인지, v3/v4 어느 패러다임인지 불명이면 처방이 갈린다. 4요소 질의:
- **누가**: 빌드 설정·디자인 시스템을 정하는 사람(프로젝트 디자인 토큰 보유 여부 — 있으면 그게 항상 우선).
- **언제**: prod에서만 스타일이 사라지나(purge 의심) / Tailwind 메이저 버전과 설정 방식(`@theme` vs `tailwind.config.js`)이 안 잡힐 때.
- **어떻게**: "증상=<prod만 / dev도>, Tailwind 버전=<v3 / v4 / 불명>, 의심 클래스 출처=<소스 / CMS·DB / 모노레포 패키지>" 형식으로.
- **기대값**: 동적 조립이면 매핑 테이블, 경로 누락이면 safelist/스캔 경로, 버전 혼선이면 v4 표준 이행. 버전·출처 미확정이면 prod 빌드 재현부터 — 추측 수정 금지.

### 사용자가 권고를 거부하면

- "임의값이 빠르다, 그냥 쓰자" → 프로토타입이면 동의 — "출고 전 `-\[` grep 청소" 1줄 기록. 디자인 시스템 있는 프로젝트면 시스템 위반 1줄 경고 후 존중(partial).
- "포커스 링 디자인상 빼달라" → focus-visible 대체안 1회 제시(키보드에만 표시됨을 설명), 그래도 거부면 접근성 리스크 기록 후 따름.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — "배포하니 스타일이 사라졌다" (purge 사고, 생태계 반복 실증)

Tailwind 도입 팀이 가장 많이 밟는 사고의 표준형: 로컬·스테이징에선 멀쩡하던 화면이 프로덕션 빌드에서만 무스타일로 깨짐. 원인은 동적 클래스 조립(안티패턴 1) 또는 스캔 경로 밖 파일(모노레포 공용 패키지·CMS 데이터의 클래스). dev 빌드는 관대하게 많은 클래스를 포함하지만 prod는 스캔에 걸린 것만 생성한다 — **환경 차이가 곧 재현 불가**라 디버깅이 길어진다. v4의 자동 콘텐츠 감지로 "경로 누락"은 줄었지만 "동적 조립"은 원리상 영원히 못 잡는다. 교훈: ① 스타일 검증은 prod 빌드로 ② 클래스는 항상 완전한 문자열 ③ CMS·DB에서 오는 클래스는 safelist 명시 — v4는 JS `safelist` 옵션을 폐기했으므로 CSS에 `@source inline("...")`(v4.1+, ≤4.0.17은 미지원) 사용. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — purge 증발 · @apply 후회 공언 · 다크모드 반쪽 적용 실증 (코어스펙 1겹)
- 1차 출처(2026-06 웹 확인):
  - [Tailwind 공식 docs — Detecting classes in source files](https://tailwindcss.com/docs/detecting-classes-in-source-files) — 텍스트 스캔 원리·동적 조립 미감지(안티패턴 1)
  - [Tailwind 공식 docs — Functions and directives](https://tailwindcss.com/docs/functions-and-directives) — `@source inline()`로 safelist(v4.1+)
  - [Tailwind 공식 docs — Dark Mode](https://tailwindcss.com/docs/dark-mode) — v4 `dark:` 기본 `prefers-color-scheme`, 클래스 토글은 `@custom-variant`(안티패턴 6)
  - [Tailwind v4.0 발표 블로그](https://tailwindcss.com/blog/tailwindcss-v4) — CSS-first·자동 콘텐츠 감지·전체 빌드 최대 5배(안티패턴 2)
  - [Adam Wathan 트윗(2022-08)](https://x.com/adamwathan/status/1559250403547652097) — "처음부터 다시 만든다면 @apply는 없을 것"(안티패턴 3)

## 한계

- 이 스킬은 구현 계층이다 — "무엇이 아름다운가"는 frontend-design(수동 로드)·프로젝트 디자인 시스템의 영역. 미감 결정을 임의로 내리지 않는다.
- 복잡한 애니메이션·캔버스·SVG 조작은 범위 밖.
- v4는 빠르게 진화 중(4.x 분기마다 기능 추가) — 신기능 사용 전 공식 문서로 현재 버전 지원 확인.
