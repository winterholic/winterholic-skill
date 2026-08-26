# Design System — html-report

**원칙: 디자인하지 말고, 콘텐츠를 컴포넌트에 매핑한다.**

이 디자인 시스템은 토스(Toss) 모바일 앱의 시각 언어 — 단단한 primary blue, 중립 zinc gray, 큰 여백, 평면 surface 위계, 톤다운된 시멘틱 컬러 — 에서 영감을 받아 **웹 보고서 전용**으로 재구성한 토큰 체계다. 토스의 코드·에셋·컴포넌트 prop 명을 직접 복제하지 않고, 디자인 결정의 원리만 차용한다.

CSS 구현 정본은 `base-css.md`. 이 문서는 *왜 이렇게 정해졌는지* 와 *언제 어떤 토큰을 쓰는지* 를 다룬다. 토큰을 외워 쓰지 말고, 의미 단위로 골라 쓴다.

---

## 0. 디자인 원칙 (모든 결정의 상위 규칙)

1. **단일 강조색** — primary blue 하나만 강조에 쓴다. 보라·주황·분홍을 새로 들이지 않는다. 위계는 색이 아니라 **surface 단계·여백·weight**로 만든다.
2. **자동 색 코딩 금지** — `.compare`(AS-IS/TO-BE), `.proscons`는 기본 중립. "AS-IS가 항상 나쁜 것"은 아니다. 의도가 명확할 때만 `.variant-improvement` 같은 명시 클래스로 색을 입힌다.
3. **그림자 거의 없음** — surface tint 1~2단계 차이로 elevation을 표현한다. 그림자는 modal·floating CTA 같은 진짜 떠 있는 요소에만.
4. **숫자가 정렬되어야 할 때만 mono** — 표 안 수치·코드·기술 식별자만 monospace. KPI 큰 숫자는 sans bold (가독·임팩트 우선).
5. **한글 본문 13px 미만 금지·italic 금지** — Pretendard는 italic이 없어 시스템 폰트로 fallback되며 깨진다. 강조는 weight 또는 색으로.
6. **다크 모드는 단순 반전이 아니다** — 명도 대비 4.5:1 이상, base는 순흑 아닌 zinc-950. primary와 시멘틱은 light/dark에서 hue는 같지만 lightness만 미세 조정.

---

## 1. 색상 팔레트

### 1.1 Brand · Primary (Calm Pro · blue 라인)

`#3B82F6` 한 색만 강조에 쓴다. 링크·CTA·kicker·TOC active·progress bar·번호 step·timeline 활성 dot — 전부 같은 색.

| 토큰 | Light | Dark | 용도 |
|------|-------|------|------|
| `--color-primary` | `#3B82F6` | `oklch(72% 0.15 248)` | 강조의 기준점. CTA, 링크, kicker, accent bar |
| `--color-primary-hover` | `#1D4ED8` | `oklch(80% 0.13 248)` | hover · focus |
| `--color-primary-pressed` | `#1E40AF` | `oklch(86% 0.10 248)` | active 클릭 순간 |
| `--color-primary-soft` | `#EFF6FF` | `var(--color-surface)` ← 다크는 hue tint 폐기, surface 단색 | 배경 (TL;DR bar 영역, kicker pill 등) |
| `--color-primary-fg` | `#FFFFFF` | `#0A1F3D` | primary 색이 *배경*일 때 그 위 텍스트 |

> 다크의 primary가 light보다 *더 밝다*: 어두운 배경에서 명도 대비를 확보하려면 hue는 유지하되 lightness를 끌어올린다. `#3182F6`을 다크에 그대로 쓰면 침침해진다.

### 1.2 Neutral (zinc · pure neutral gray)

푸르스름·따뜻함 없는 순 중립 gray. primary blue와 충돌하지 않고 어떤 시멘틱 색과도 조화된다.

**Light**

| 토큰 | hex | 용도 |
|------|------|------|
| `--color-bg` | `#FFFFFF` | 페이지 본 배경 |
| `--color-bg-2` | `#FAFAFA` | 페이지 보조 배경 (히어로 외곽, 인쇄 미리보기) |
| `--color-surface` | `#F4F4F5` | 카드·callout 기본 표면 |
| `--color-surface-2` | `#E4E4E7` | thead, inline code, 강조 표면 |
| `--color-border` | `#E4E4E7` | 일반 경계선 |
| `--color-border-strong` | `#D4D4D8` | 강조 경계선, divider |
| `--color-ink` | `#18181B` | 제목, 본문 강조 (zinc-900) |
| `--color-ink-2` | `#27272A` | 본문 (zinc-800) |
| `--color-ink-3` | `#3F3F46` | 보조 본문, 표 셀 (zinc-700) |
| `--color-muted` | `#71717A` | 캡션, 메타, 라벨 (zinc-500) |
| `--color-muted-2` | `#A1A1AA` | 비활성, placeholder (zinc-400) |

**Dark**

| 토큰 | hex | 용도 |
|------|------|------|
| `--color-bg` | `#09090B` | 페이지 본 배경 (zinc-950) |
| `--color-bg-2` | `#0F0F11` | 페이지 보조 |
| `--color-surface` | `#18181B` | 카드·callout 기본 (zinc-900) |
| `--color-surface-2` | `#27272A` | thead, 강조 표면 (zinc-800) |
| `--color-border` | `#27272A` | 일반 경계 |
| `--color-border-strong` | `#3F3F46` | 강조 경계 |
| `--color-ink` | `#FAFAFA` | 제목 |
| `--color-ink-2` | `#E4E4E7` | 본문 |
| `--color-ink-3` | `#D4D4D8` | 보조 본문 |
| `--color-muted` | `#A1A1AA` | 캡션 |
| `--color-muted-2` | `#71717A` | 비활성 |

> 다크 base가 순흑(`#000`)이 아닌 zinc-950 (`#09090B`): 순흑은 OLED에서는 좋지만 일반 모니터에서 border가 안 보이고 눈부심이 심하다.

### 1.3 Semantic (의미 색)

**Calm Pro 팔레트** — Stripe·Linear 풍 모던 SaaS 톤. primary blue와 emerald(success)·amber(warn)·rose(danger)가 색상환에서 떨어져 있지만 모두 명도 50~60% · 채도 60~70% 라인에 모여 통일감을 만든다. 단색으로 보면 vivid한데 함께 놓이면 균형. **텍스트로 직접 쓰는 hex와 배경으로 쓰는 hex가 다르다** — 대비 안전성 때문.

| 의미 | 토큰 | Light hex | Dark hex | 용도 |
|------|------|-----------|----------|------|
| **Success** | `--color-success` | `#0D9F6E` (emerald-600 변형) | `oklch(72% 0.13 158)` | 아이콘·border·badge 강조 |
| | `--color-success-fg` | `#065F46` (emerald-800) | `oklch(85% 0.10 158)` | callout 본문 텍스트 (대비 안전) |
| | `--color-success-soft` | `#D1FAE5` (emerald-100) | `var(--color-surface)` ← 다크 hue tint 폐기 | callout·badge 면 배경 (light 한정) |
| **Warn** | `--color-warn` | `#D97706` (amber-600) | `oklch(75% 0.13 70)` | 아이콘·border |
| | `--color-warn-fg` | `#92400E` (amber-800) | `oklch(87% 0.10 70)` | 본문 텍스트 |
| | `--color-warn-soft` | `#FEF3C7` (amber-100) | `var(--color-surface)` ← 다크 hue tint 폐기 | 면 배경 (light 한정) |
| **Danger** | `--color-danger` | `#E11D48` (rose-600) | `oklch(72% 0.15 18)` | 아이콘·border |
| | `--color-danger-fg` | `#9F1239` (rose-800) | `oklch(85% 0.10 18)` | 본문 텍스트 |
| | `--color-danger-soft` | `#FFE4E6` (rose-100) | `var(--color-surface)` ← 다크 hue tint 폐기 | 면 배경 (light 한정) |
| **Info** | `--color-info*` | (= primary) | (= primary) | 일반 정보 — primary와 동일 토큰 사용 |

> "왜 fg와 base를 나눠?" — `--color-success: #0D9F6E` 위에 본문 텍스트로 쓰면 대비가 살짝 마지널하다. callout 본문은 `-fg`(더 어둡게 emerald-800)로, 강조 라벨·아이콘·border는 `-base`로. 다크는 반대로 `-fg`가 더 밝다.
>
> **톤 선정 이력** — (1) 첫 시도: 토스 캔디(`#00C896` mint / `#FFA800` neon / `#F04452` coral) → 발랄·놀이공원 톤. (2) Deep & bordered (emerald-700 / amber-700 / red-700) → 차이 인지 약함·hue 관계 없음. (3) **Calm Pro 채택** — Stripe/Linear 라인의 명도·채도 통일 팔레트로 색상 간 *조화* 확보.

### 1.4 금기

- primary 외 새 강조색 추가 금지 (보라·주황·분홍 등) — 위계는 surface·여백·weight로
- 한 페이지에 success/warn/danger 셋 다 등장하는 경우 callout 3개 연속 배치 금지 — 시각 노이즈. 위계로 분리
- 임의 hex (`style="color:#ff0000"` 등) 금지 — 토큰만 사용
- 주식·금융 데이터 한정: **상승 빨강 (`danger`)·하락 파랑 (`primary/info`)** 한국 컨벤션 엄수
- 다크 모드에서 `#000` 순흑 배경 금지

---

## 2. 타이포그래피

### 2.1 폰트 스택

| 용도 | 폰트 | 폴백 |
|------|------|------|
| 본문·제목 (한글 포함) | Pretendard Variable (CDN) | system-ui, -apple-system, Apple SD Gothic Neo, Noto Sans KR |
| 코드·정렬 숫자 | JetBrains Mono | SF Mono, Menlo, Consolas, D2Coding |

CDN 못 받는 환경에서도 시스템 폰트로 폴백된다. **페이지당 폰트 패밀리 2개 한도**.

### 2.2 크기 스케일

`--fz-md`를 없애 결정 트리를 단순화. 8단계로 정리.

| 토큰 | px | line-height | 용도 |
|------|----|-------------|------|
| `--fz-caption` | 12 | 1.4 | 캡션, kicker, 메타 라벨 |
| `--fz-small` | 13 | 1.5 | 표 본문, 보조 텍스트 |
| `--fz-base` | 15 | 1.65 | 본문 기본 |
| `--fz-lg` | 17 | 1.6 | 부제, 카드 헤딩 |
| `--fz-xl` | 20 | 1.45 | H4 |
| `--fz-2xl` | 26 | 1.35 | H3 |
| `--fz-3xl` | 32 | 1.25 | H2 |
| `--fz-4xl` | 40 | 1.2 | H1 (보고서 제목) |
| `--fz-display` | 52 | 1.1 | KPI 큰 숫자, hero 강조 |

**본문은 13px 미만 금지.** 표 안 숫자라도 13px 사수. 반응형 폰트 안 씀 (모바일도 동일 — 가독 우선).

### 2.3 Weight

토스풍 단단함 — heading은 700으로 끌어올림.

| 값 | 이름 | 용도 |
|----|------|------|
| 400 | regular | 본문 |
| 500 | medium | 부제, 강조 라벨, 표 헤드 보조 |
| 600 | semibold | 카드 제목, 표 헤드, 강조 본문 |
| 700 | bold | H1~H4, kicker, KPI 큰 숫자, badge |

> 이전 디자인은 heading을 600에 두었다. 700으로 끌어올리면 한글 Pretendard 특유의 단단함이 살아난다.

### 2.4 Letter-spacing

| 대상 | 값 |
|------|-----|
| Display, H1 | `-0.025em` |
| H2, H3 | `-0.015em` |
| H4 이하 본문 | `0` (Pretendard 기본) |
| Kicker, 라벨, uppercase | `0.08em` |

### 2.5 숫자 표기

- `body`에 전역 `font-variant-numeric: tabular-nums` (자릿수 정렬)
- KPI 큰 숫자: `font-family: var(--font-sans)`, `font-weight: 700` (mono 아님 — 임팩트 우선)
- 표 안 숫자 정렬: `td.num` → `font-family: var(--font-mono); text-align: right`

한글에 italic 금지. 강조는 weight 600 또는 색상으로.

---

## 3. 스페이싱

4의 배수. 9단계.

| 토큰 | px | 사용 예 |
|------|----|---------|
| `--s-1` | 4 | 인라인 간격, badge 안 |
| `--s-2` | 8 | tight gap, 작은 padding |
| `--s-3` | 12 | 컴포넌트 안 padding |
| `--s-4` | 16 | 일반 padding, grid gap |
| `--s-5` | 24 | 카드 padding, 컴포넌트 간격 |
| `--s-6` | 32 | 큰 컴포넌트 padding |
| `--s-7` | 48 | 섹션 안 위·아래 여백 |
| `--s-8` | 64 | H2 섹션 시작 여백 |
| `--s-9` | 96 | 페이지·푸터 위 여백 |

임의 값 (`padding: 18px`) 사용 금지. 4의 배수만.

---

## 4. Radius

| 토큰 | px | 용도 |
|------|----|------|
| `--r-xs` | 4 | inline code, 작은 badge |
| `--r-sm` | 8 | callout, table wrap |
| `--r-md` | 12 | card, TL;DR, mermaid wrap |
| `--r-lg` | 16 | hero, 큰 카드 |
| `--r-full` | 999 | badge pill, progress, toggle |

---

## 5. Elevation (그림자 정책)

**그림자는 거의 안 쓴다.** 카드·callout·표는 surface tint + border로만 위계 표현. 인쇄 친화적이고 다크 모드에서 깔끔.

| 토큰 | 값 | 용도 |
|------|----|------|
| `--shadow-none` | `none` | 기본 |
| `--shadow-overlay` | `0 8px 24px rgba(15,23,42,.08), 0 2px 6px rgba(15,23,42,.04)` | modal, popover, floating CTA에만 |
| `--shadow-overlay-dark` | `0 8px 24px rgba(0,0,0,.5), 0 2px 6px rgba(0,0,0,.3)` | 다크 모드 overlay |

카드는 `background: var(--color-surface)` + 필요 시 `border: 1px solid var(--color-border)` 조합으로 위계를 만든다. surface 단계가 부족하면 `surface` → `surface-2`로 바꿔서 한 단 더 끌어올린다.

---

## 6. 레이아웃

- 본문 콘텐츠: `max-width: 820px` (가독·인쇄 최적)
- TOC 사이드바: `240px` sticky
- 페이지 좌우 패딩: `--s-5` (24px)
- 980px 미만: TOC 위로 빠지고 1단 흐름
- 720px 미만: grid 컴포넌트 모두 1열

### 6.1 그리드 시스템

`.grid.cols-{2,3,4}`만 사용. 임의 column 비율 금지. 더 복잡한 레이아웃이 필요하면 컴포넌트 조합으로 해결.

---

## 7. Motion

거의 안 쓴다. 보고서는 정적 문서다.

| 토큰 | 값 | 용도 |
|------|----|------|
| `--ease-out` | `cubic-bezier(0.22, 1, 0.36, 1)` | 일반 전환 |
| `--dur-fast` | `150ms` | hover, focus |
| `--dur-base` | `200ms` | 테마 토글, details 펼침 |

`@media (prefers-reduced-motion: reduce)`에서 모든 transition을 0으로.

---

## 8. 다크 모드

- 트리거: `<html data-theme="light|dark">`
- 초기 로드: `localStorage` → 없으면 `prefers-color-scheme`
- 우측 상단 toggle 버튼 (`.theme-toggle`)
- Mermaid는 토글 시 자동 재초기화 (`theme: dark|default`)

토큰은 단일 이름 (`--color-bg`, `--color-ink` 등) — light/dark 값은 `:root`와 `[data-theme=dark]`에서 각각 재정의. 컴포넌트 CSS는 토큰 이름만 참조하므로 분기 코드가 없다.

### 8.1 다크 시멘틱 설계 원리 (OKLCH perceptual uniformity)

다크는 light hex를 그대로 쓸 수 없다(배경이 어두워 mid-tone base가 사라지고, deep fg는 안 보임). 그래서 다크 전용으로 다시 잡되, **sRGB의 hex/HSL을 쓰면 hue마다 시각 밝기가 달라져 카니발 색감이 된다** — yellow는 같은 명도값(L*)에서도 인간 눈에 가장 밝게 인식되는 등 hue별 perceptual bias가 있기 때문.

해결: **OKLCH 색공간** 사용. L(perceptual lightness)·C(chroma)·H(hue) 분리. 같은 L+C에 두고 H만 바꾸면 4 hue가 *시각적으로 같은 밝기*로 보임. coolors.co식 진짜 조화는 이 원리.

| 차원 | 값 | 설명 |
|------|----|------|
| **L (명도)** | `72%` (base) / `85%` (fg) | 다크 배경(zinc-900)에서 잘 보이는 mid-bright |
| **C (채도)** | `0.13~0.15` (base) / `0.10` (fg) | vivid도 무채색도 아닌 sweet spot |
| **H (hue)** | primary `248` blue / success `158` emerald / warn `70` amber / danger `18` rose | 4 hue가 색상환에서 떨어져 있지만 L+C는 동일 |
| **soft** | **폐기** (다크는 `var(--color-surface)` 매핑) | 다크에서 hue tint 면 배경 자체 안 씀 — §8.2 참조 |

브라우저 지원: Chrome 111+ · Safari 15.4+ · Firefox 113+ (2026년 기준 점유율 95%+). 미지원 환경에서는 색이 무시되어 transparent가 되므로 시각이 깨지는데, 이 스킬은 모던 환경 대상이라 채택.

### 8.2 다크에서 hue 사용 원칙 (형광 텍스트 회피)

**다크 배경(`zinc-900`) 위에 vivid hue 텍스트(emerald-fg, rose-fg, amber-fg 등)는 무조건 형광처럼 떠보인다.** OKLCH로 명도·채도를 통일해도 *색 자체*가 어두운 배경과의 대비를 강하게 만들기 때문. 라이트는 흰 배경 위 어두운 hue text라 그라데이션이 부드러운데, 다크는 정반대.

해결책 — **다크에서 박스 hue tint 배경은 전부 제거. 의미는 좌측 4px accent bar + 아이콘 + (badge는 hue text)로만 전달**:

| 요소 | Light | Dark |
|------|-------|------|
| Callout 배경 | `-soft` (옅은 hue tint) | **`--color-surface` 무채색 + `border-left: 4px solid <hue>`** |
| Proscons (.pros/.cons) 배경 | `-soft` | **surface + 좌측 4px hue bar** |
| Compare side 배경 | `-soft` | **surface + 좌측 4px hue bar** |
| Badge 배경 | `-soft` | **surface-2 + border + hue text** |
| Decision winner row | `success-soft` | **surface-2 + ink (강조는 surface 단계로)** |
| Risk-grid cell 배경 | `success/warn/danger-soft` | **`--color-bg` 무채색** (위험도는 axis 위치로) |
| Risk-grid item card | surface + cell hue border-left | surface + cell hue border-left |
| 아이콘 (callout-icon, badge text) | `-base` (mid hue) | `-base` (밝은 hue, OK — 면적 작음) |
| **h4 · title · side-label** | `-fg` (deep hue text) | **`--color-ink` (흰색 무채색)** |
| 본문 li · p | inherit (ink-3) | inherit (ink-2) |

원칙: **다크에서 hue tint 면 배경은 무조건 NO**. 너무 어두우면 칙칙 / 너무 진하면 vibrate / 가운데 톤은 무지개색 카니발. 단색 surface + 좌측 4px hue accent bar가 가장 깔끔.

---

## 9. 인쇄 (Print)

`@media print` 자동 적용:

- A4, 여백 18mm/14mm
- TOC, theme toggle, mermaid 컨테이너 그림자 제거
- 본문 폭 제한 해제
- 카드·표·코드·callout `page-break-inside: avoid`
- 외부 링크는 URL 자동 표기 (`a[href^="http"]::after`)
- 색은 약간 채도 낮춰 토너 절약 (시멘틱 soft 색을 흰색으로 fallback)

Chrome 인쇄 미리보기 → "PDF로 저장"으로 깔끔히 출력된다.

---

## 10. 외부 의존성

CDN 2개만 사용:

1. **Pretendard Variable** (필수, 한글 폰트)
2. **Mermaid.js** (선택, 다이어그램 보고서에만)

오프라인에서도 시스템 폰트 폴백으로 안 깨진다. 다른 CDN (Chart.js, KaTeX 등) 추가 시 반드시 사용자 확인.

아이콘은 인라인 SVG로 base.html에 포함 — 외부 의존 0. 토큰화된 아이콘 목록은 `components.md` §callout 참조.

---

## 11. 보고서 화면 위계

> 청중이 5초 안에 구조를 파악할 수 있어야 한다.

1. **헤더** (kicker · 제목 · 부제 · 메타) — 누가·언제·무엇
2. **TL;DR** — 결론을 먼저
3. **본문 섹션** (H2 단위 5~8개)
4. **푸터** (작성자·버전·날짜)

H2가 10개를 넘으면 보고서가 너무 무거운 신호 — 섹션을 합치거나 별도 문서로.

---

## 12. 토큰 빠른 참조 (Cheat Sheet)

```css
/* Brand */
--color-primary  /* 강조의 단일 색 */
--color-primary-soft  /* 강조 면 배경 */

/* Neutral 위계 (밝음 → 어두움) */
--color-bg → --color-bg-2 → --color-surface → --color-surface-2
--color-border → --color-border-strong
--color-muted-2 → --color-muted → --color-ink-3 → --color-ink-2 → --color-ink

/* Semantic — 텍스트는 fg, 배경은 soft (light 한정), 강조는 base */
/* ⚠ 다크에선 *-soft = surface (hue tint 면 배경 폐기). §8.2 참조 */
--color-success / --color-success-fg / --color-success-soft
--color-warn    / --color-warn-fg    / --color-warn-soft
--color-danger  / --color-danger-fg  / --color-danger-soft

/* Spacing 4의 배수 */
--s-1 (4) ~ --s-9 (96)

/* Radius */
--r-xs (4) → --r-sm (8) → --r-md (12) → --r-lg (16) → --r-full

/* Font size 8단계 */
--fz-caption (12) → --fz-small (13) → --fz-base (15) → --fz-lg (17)
→ --fz-xl (20) → --fz-2xl (26) → --fz-3xl (32) → --fz-4xl (40)
→ --fz-display (52)
```

토큰을 외워 쓰지 말고, 의미(역할)로 골라 쓴다. 예: "이건 본문 안 callout의 배경" → `--color-success-soft`. "이건 H2 위 큰 간격" → `--s-8`.
