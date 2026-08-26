# token-naming — 토큰 계층·네이밍 실무 (검증판)

> evidence.md의 §2·§3 확장. 3계층 실제 설계, 네이밍 규칙, DTCG 포맷 구조 상세. 출처 2026-07 웹 검증. 1차/공식 우선.

---

## 1. 3계층 토큰 아키텍처 (실제 설계)

성숙한 시스템은 예외 없이 **3계층 참조 체인**을 쓴다. 사용처(컴포넌트 CSS)는 절대 원시 값을 직접 참조하지 않는다.

```
원시(Primitive/Global/Reference)  →  시맨틱(Semantic/Alias/System)  →  컴포넌트(Component)
color.blue.500 = #3B82F6              action.primary = {color.blue.500}   button.bg = {action.primary}
```

| 계층 | 별칭(벤더별) | 담는 것 | 참조 규칙 |
|---|---|---|---|
| **Tier 1 원시** | Global / Primitive / **Reference**(MD3 `md.ref.*`) | 순수 값(hex, px, ms). 의미 없음. 플랫폼 무관. | 정적 값 또는 다른 원시만 참조 |
| **Tier 2 시맨틱** | Alias / Semantic / **System**(MD3 `md.sys.*`) | 역할·의도(`action`, `surface`, `text`, `border`). 다크/브랜드 분기 지점. | 원시를 참조 |
| **Tier 3 컴포넌트** | Component(MD3 `md.comp.*`) | 특정 컴포넌트 부위(`button.primary.bg`, `card.padding`). | **시맨틱을 참조**(원시 직접참조 금지) |

핵심: "blue-400 대신 `color-background-interactive` 같은 시맨틱 토큰을 만든다. 밑단 hex를 한 번 바꾸면 그 원시를 가리키는 모든 alias가 함께 갱신된다."([design.dev](https://design.dev/guides/design-systems/), [oboe.com Token Architecture](https://oboe.com/learn/advanced-design-engineering-and-systems-architecture-2hulw5/design-token-architecture-0))

⚠️ **계층 개수는 상황 종속**(과설계 금지). 단일 앱은 원시→시맨틱 2계층으로 충분 — 컴포넌트 토큰은 부위별 오버라이드가 실제로 필요할 때만. 멀티브랜드/화이트라벨은 시맨틱 위에 브랜드 alias 레이어를 더한다.

---

## 2. Nathan Curtis 네이밍 분류 체계 (권위 출처)

Curtis는 토큰 이름을 4개 그룹의 조합으로 정의한다. 출처: [Naming Tokens in Design Systems (EightShapes)](https://medium.com/eightshapes-llc/naming-tokens-in-design-systems-9e86c7444676)

**① Base(뼈대)** — 이름의 핵심 축
- Category: `color`, `font`, `space`, `size`
- Property: `text`, `background`, `border`
- Concept: `feedback`, `action`, `heading`

**② Modifier(수식자)** — base에 덧붙임
- Variant: `primary`, `secondary`, `success`, `error`
- State: `hover`, `focus`, `disabled`, `active`
- Scale: enumerated(`1`,`2`,`3`) / ordered(`50`,`100`…`900`) / t-shirt(`sm`,`md`,`lg`)
- Mode: `light`, `dark`

**③ Object(컴포넌트)** — 컴포넌트 스코프
- Component group(`forms`) → Component(`input`) → Nested element(`left-icon`)

**④ Namespace(스코프)** — 최상위 접두
- 시스템 약칭(`esds`, `slds`), 테마(`ocean`), 도메인(`consumer`, `retail`)

**순서 규칙**: "네임스페이스가 맨 앞에 붙고 … 수식자는 맨 뒤에 붙는다."
**예시 조합**: `$esds-color-feedback-background-error`(namespace-category-concept-property-variant)

⚠️ 정확성: 이 글에서 Curtis는 "primitive/semantic/decision token"이라는 용어를 쓰지 **않는다**. 대신 **generic**(`$esds-space-2-x` = 32px)과 **purposeful**(맥락·의도를 담은) 토큰을 구분한다. "시맨틱 토큰"은 커뮤니티 통용어이지 Curtis의 원어가 아니다 — 개념은 동일.

### 실무 네이밍 규칙 (체크)
- **일관된 순서 고정**: `[namespace].[object].[base].[modifier]` 한 패턴을 팀 전체가 준수 → 토큰이 검색 가능·예측 가능·자기설명적이 된다.([netguru](https://www.netguru.com/blog/design-token-naming-best-practices))
- **원시엔 의미 금지**: `color.blue.500`은 OK, `color.brand.500`은 원시 계층에선 안티(브랜드 바뀌면 이름이 거짓말이 됨).
- **시맨틱엔 값 금지**: `action.primary`는 "무엇을 하는가"만, "무슨 색인가"는 참조로 위임.
- **약어 남발 금지**: `bg`·`fg`는 팀 합의 시만. 자기설명 우선.

---

## 3. DTCG 포맷 모듈 구조 상세 (Design Tokens Format Module 2025.10)

출처(1차): [designtokens.org/tr/drafts/format](https://www.designtokens.org/tr/drafts/format/)

### 3.1 지위 (불변 사실)
스펙 본문 원문 그대로: **"This is not a W3C Standard nor is it on the W3C Standards Track."** → W3C **Community Group** 산출물(정식 표준 아님). 2025.10이 첫 안정판(2025-10-28 발표).

### 3.2 토큰 객체 구조
```jsonc
{
  "token-name": {
    "$value": "#3B82F6",        // 필수 — 실제 값
    "$type": "color",            // 선택 — 카테고리(생략 시 그룹에서 상속)
    "$description": "…",         // 선택 — 목적 설명(plain text)
    "$deprecated": true,         // 선택 — 폐기 표시(문자열로 사유·대체 안내 가능)
    "$extensions": { … }         // 선택 — 벤더/팀 독자 데이터 (툴이 MAY 추가)
  }
}
```
- **필수**: `$value` + 토큰 이름(부모 객체 키)
- **선택**: `$type`, `$description`, `$extensions`, `$deprecated`
- `$` 접두: DTCG 예약어. 접두 없는 키는 그룹/토큰 이름.

### 3.3 그룹과 `$type` 상속
그룹은 토큰을 계층으로 묶는다. 그룹의 `$type`은 자식 토큰의 **기본값**이 된다.
- `$extends`: JSON Schema 방식 그룹 상속
- `$description`, `$deprecated`: 그룹 단위로도 적용
- **타입 해석 순서**: 토큰의 명시 `$type` → 상속된 그룹 `$type` → 상위 그룹 `$type` → 없으면 invalid

### 3.4 별칭(Alias) — DTCG의 핵심 가치
"DTCG가 중요한 가장 큰 이유는 alias다."([tasteprofile](https://tasteprofile.io/blog/w3c-dtcg-design-tokens-practical-guide))
- 중괄호 경로: `{group.token}` → 참조 토큰의 `$value` 전체로 해석
- 속성 단위 접근: JSON Pointer `$ref: "#/path"`(고급)

### 3.5 Composite Type(복합 토큰)
여러 하위 값을 묶는 구조 토큰:
| 타입 | 하위 필드 |
|---|---|
| `typography` | fontFamily, fontSize, fontWeight, lineHeight |
| `shadow` | color, offsetX, offsetY, blur, spread (단일 또는 배열=다중 그림자) |
| `gradient` | color stops + 방향 |
| `border` | color, width, style |
| `transition` | duration, delay, timingFunction |
| `strokeStyle` | dashArray, lineCap |

### 3.6 완성 예시
```jsonc
{
  "color": {
    "$type": "color",                                  // 그룹 기본 타입
    "blue": { "500": { "$value": "#3B82F6" } },        // 원시(타입 상속)
    "action": {
      "primary":   { "$value": "{color.blue.500}", "$description": "주 액션 배경" },
      "primary-old": { "$value": "{color.blue.500}", "$deprecated": "action.primary로 이관" }
    }
  },
  "space": {
    "4": { "$value": "16px", "$type": "dimension" }
  },
  "typography": {
    "heading": { "$type": "typography", "$value": {
      "fontFamily": "Inter", "fontSize": "24px", "fontWeight": 700, "lineHeight": 1.3
    }}
  }
}
```

---

## 4. 다크모드·멀티브랜드 토큰 전략 (시맨틱에서만 분기)

**철칙: 원시는 고정, 분기는 시맨틱에서만.** 컴포넌트·원시는 무수정.

- **다크모드**: `md.ref.*`(원시)는 그대로, `md.sys.color.surface`(시맨틱)가 light/dark 각각 다른 원시를 참조. "컴포넌트 토큰이 리터럴 원시가 아니라 시맨틱 시스템 토큰을 가리키므로 UI 전체가 자동 갱신."([MD3 overview](https://m3.material.io/foundations/design-tokens/overview))
  - 구현: `md` 모드 축 또는 CSS `:root` / `[data-theme=dark]` 스코프 오버라이드 + `prefers-color-scheme`.
  - ⚠️ 다크는 밝기 반전이 아니라 **의미 재매핑** — surface/on-surface 대비를 다크에서 별도 검증(대비는 evidence.md §5).
- **멀티브랜드**: 시맨틱 위에 브랜드 alias 레이어. 브랜드 교체 = alias 한 곳. 브랜드 2개면 CSS 변수 오버라이드로 축약, 다수면 빌드타임 테마 산출.
- **Carbon 방식**(참고): 동일 시맨틱 토큰 이름(`text-primary`, `layer-01`, `background`)이 테마(White/Gray 10/Gray 90/Gray 100)별로 다른 값에 매핑 — 컴포넌트는 이름만 참조. (정확한 v11 토큰명 목록은 [carbondesignsystem.com/elements/color/tokens](https://carbondesignsystem.com/elements/color/tokens/) 확인 필요)

---

## 5. 단일 소스 파이프라인 (디자인↔코드 정합)

- **원천 하나**(`tokens.json`, DTCG 포맷) → 빌드로 플랫폼별 산출: CSS custom property, iOS/Android, JS/TS.
- 대표 툴: **Style Dictionary**(Amazon 오픈소스, DTCG 지원), Tokens Studio(Figma↔코드). (툴명 사실, 버전·기능 상세는 확인 필요)
- 규칙: 디자인·코드 토큰 이름 **1:1**. 파이프라인 도입 전이라도 이름 규칙만 먼저 통일.
- 자동화 흐름: Figma 변수 → export → 변환 → 빌드 배포.([dev.to token ecosystem](https://dev.to/timges/building-a-design-token-ecosystem-from-source-of-truth-to-automated-distribution-gpg))

---

## 출처
- Nathan Curtis, *Naming Tokens in Design Systems* — https://medium.com/eightshapes-llc/naming-tokens-in-design-systems-9e86c7444676
- Design Tokens Format Module 2025.10 (DTCG, W3C Community Group — 정식 표준 아님) — https://www.designtokens.org/tr/drafts/format/
- Material Design 3, *Design tokens overview* — https://m3.material.io/foundations/design-tokens/overview
- Carbon Design System, *Color tokens* — https://carbondesignsystem.com/elements/color/tokens/
- 보조: tasteprofile.io, design.dev, netguru, dev.to (실무 해설, 1차 아님)
