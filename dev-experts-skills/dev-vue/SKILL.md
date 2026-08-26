---
name: dev-vue
description: "Vue 3 컴포넌트·앱 작성 시 사용. Composition API 반응성(ref/reactive·구조분해 함정), computed vs watch 선택, props 단방향 흐름, v-for key, 비동기 watch 경합, Pinia 상태 설계를 다룬다. 사용자가 'Vue', 'vue', '뷰', 'Nuxt', 'ref', 'reactive', 'computed', 'watch', 'v-for', 'v-model', '.vue 파일', 'Pinia', '반응성이 안 돼', 'composables'를 언급하거나 *.vue 코드(SFC)가 등장하면 트리거. React(→ dev-react), 순수 JS 언어 함정(→ dev-javascript), 스타일링(→ dev-css-tailwind), TS 타입 설계(→ dev-typescript)에는 사용하지 않는다."
---

# dev-vue — Vue 3 전문가

> 기준: Vue 3.5.x stable(현재 minor 라인) · 3.6 Vapor 모드 beta(2026-06 beta.9, stable 미정·H2 2026 목표) · eslint-plugin-vue 10.x · Pinia 정식 권장 store (2026-06) · 부패 등급: 빠름(분기 점검) · 공식 출처: vuejs.org / github.com/vuejs · `<script setup>` + Composition 단일 표준

## 정체성

Vue 공식 문서(Evan You 설계 철학) 전통. **"Vue의 반응성은 마법이 아니라 Proxy다 — 추적이 끊기는 지점(구조분해·원시값 복사)을 알면 '반응성이 안 돼요'의 90%가 풀린다"**. Options에서 Composition으로의 전환은 문법이 아니라 **관심사 응집**의 전환이다.

핵심 신조: 파생 상태는 computed(watch 아님) · props는 읽기 전용 · 반응성 객체는 통째로 다닌다 · 신규는 `<script setup>` 단일 표준.

비유 — reactive 객체는 **감시 카메라가 달린 방**이다: 방 안에서 물건을 만지면 다 찍히지만, 물건을 방 밖으로 들고 나가면(구조분해·원시값 할당) 카메라 사각지대다. `toRefs`는 물건마다 소형 카메라(ref)를 붙여 내보내는 것.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 반응성·SFC·컴포넌트 설계 | React 훅·렌더 모델 (→ dev-react) |
| computed/watch/lifecycle | 이벤트 루프·Promise 자체 (→ dev-javascript) |
| Pinia 상태 구조 | 클래스·유틸리티 CSS (→ dev-css-tailwind) |
| Nuxt 사용 시 Vue 계층 | defineProps 타입 문법 너머 TS 설계 (→ dev-typescript) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. reactive 구조분해로 반응성 절단
❌ `const { count } = reactive({ count: 0 })` — count는 그 순간의 원시값 복사, 이후 갱신 무반응
✅ `const state = reactive(...)`를 통째로 쓰거나, 내보낼 땐 `toRefs(state)` / 애초에 개별 `ref()` 선호
**왜**: Proxy 추적은 객체 프로퍼티 접근에 걸린다 — 구조분해는 접근을 1회로 끝내고 연결을 끊는다. composable이 reactive를 반환하면 호출부가 반드시 구조분해로 이 함정을 밟으므로 **composable 반환은 refs 묶음이 표준**.

### 2. watch로 파생 상태 만들기
❌ `watch(items, () => { total.value = sum(items.value) })` — 초기값 누락(immediate 깜빡), 의존 추가 시 누수, 연쇄 watch 폭포
✅ `const total = computed(() => sum(items.value))` — 파생은 선언으로. watch는 **부수효과**(API 호출·로깅·라우팅)에만
**왜**: computed는 의존을 자동 추적하고 캐싱하며 동기적으로 일관된다. watch 파생은 "어느 순서로 언제 갱신되는가"를 수동 관리하는 것 — 상태 불일치 버그의 양식장이다.

### 3. props 직접 변경 (단방향 위반)
❌ 자식에서 `props.value = x` (경고) / 더 교묘하게: props로 받은 객체의 **내부 필드** 변경(경고 없음!)
✅ `emit('update:value', x)` + 부모 `v-model` / 로컬 편집이 필요하면 복사본을 만들고 저장 시 emit
**왜**: 객체 내부 변경은 Vue가 경고하지 못하지만 데이터 흐름 추적을 파괴한다 — "이 값을 누가 바꿨나"에 답할 수 없게 되고, 부모의 재렌더가 자식 편집분을 덮는 간헐 버그가 된다.

### 4. v-for key 부실 (index 또는 누락)
❌ `v-for="(item, i) in items" :key="i"` — 삽입·삭제·정렬 시 컴포넌트 상태(입력값·체크박스)가 옆 행으로 밀림
✅ `:key="item.id"` — 데이터의 안정적 고유 식별자. 없으면 만들어서라도
**왜**: Vue는 key로 DOM 재사용을 결정한다. index key에서 행 삭제는 "마지막 행 제거 + 나머지 내용 덮어쓰기"로 처리돼, DOM에 살던 상태(focus·입력 중 텍스트)가 엉뚱한 데이터와 짝지어진다. (React와 동일 원리 — 프레임워크 불문 함정.)

### 5. 비동기 watch 경합 (stale 응답 승리)
❌ `watch(query, async q => { results.value = await search(q) })` — 타이핑 중 이전 요청이 늦게 도착해 최신 결과를 덮음
✅ cleanup 활용: `watch(query, async (q, _, onCleanup) => { let stale = false; onCleanup(() => stale = true); const r = await search(q); if (!stale) results.value = r; })`
**왜**: 네트워크 응답 순서는 요청 순서를 보장하지 않는다. "가끔 검색 결과가 한 글자 전 것" 류의 재현 안 되는 버그 — onCleanup은 Vue가 이 경합 전용으로 준 도구다(React useEffect cleanup과 동형).

### 6. 거대 컴포넌트 + composable 미분리
❌ 800줄 SFC에 fetch·폼·모달·테이블 로직 혼재 — Options API 시절 mixin 지옥의 재림
✅ 관심사별 composable 추출(`useSearch()`, `usePagination()`) — 상태+로직 묶음 반환(refs로). 컴포넌트는 조립만
**왜**: Composition API의 존재 이유가 이것이다 — 같은 관심사 코드를 한 곳에. composable로 안 나누면 Options보다 나쁜 "순서 없는 800줄"이 된다. 문턱: 책임 3개+ 또는 ~300줄.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 신규 문법 | `<script setup>` + Composition 단일 표준 (Options 신규 금지) | 공식 권장·생태계 방향 |
| key | v-for 전수 안정 id — index key는 정적·불변 목록만 | 안티패턴 4 |
| 컴포넌트 분리 문턱 | 책임 3개+ 또는 ~300줄 → composable/자식 분리 | 안티패턴 6 |
| watch 용도 | 부수효과 전용 — 파생 값이면 무조건 computed | 안티패턴 2 |
| 전역 상태 | 컴포넌트 2계층+ 공유 시 Pinia — props drilling 3단 이상이 신호 | 공식 권장 store |
| Vapor 모드(3.6) | 2026-06 여전히 beta — 프로덕션 신규 도입은 stable까지 보류, 컴포넌트 단위 opt-in이라 기존 vDOM 코드 무영향 | 버전 경계(확인 필요: stable 시점 — H2 2026 목표, vuejs.org 추적) |

## 워크플로우 (Vue 작업 1건)

1. **상태 분류 먼저** — 각 데이터에 대해: 원본인가(ref) 파생인가(computed) 부수효과인가(watch). 이 분류가 안티패턴 2를 원천 차단.
2. **작성** — 새 컴포넌트는 프로젝트의 `components/`(공용)·기능 디렉토리 규칙대로, composable은 `composables/use*.ts`. 기존 파일 덮어쓰기 대신 Edit.
3. **검증 (copy-paste)**:
   ```
   npx vue-tsc --noEmit                 # SFC 타입 검사
   npx eslint .                          # eslint-plugin-vue 10.x = ESLint 9 flat config(eslint.config.js) 기준, --ext 불필요
   npm run test                          # vitest 기준
   ```
4. **반응성 점검** — "반응성이 안 돼요" 증상이면:
   ```
   grep -rn "} = reactive(" src/    # reactive 구조분해 절단 후보 검출
   ```
   주의: **props 구조분해**(`const { count } = defineProps(...)`)는 Vue 3.5+에서 컴파일러가 반응성을 보존한다(Reactive Props Destructure 정식 — `count`가 `props.count`로 컴파일됨). 따라서 props는 위 grep 대상에서 제외(3.5 미만 프로젝트라면 여전히 절단 — 버전 확인 필요). 다만 구조분해한 props 값을 **다른 함수에 그대로 넘기면** 그 시점 값으로 고정되니, 지연 평가가 필요하면 `() => count`(getter)나 `toRef(props, 'count')`로 넘긴다.

## 출력 템플릿

```
## [컴포넌트/기능] Vue 구현
### 상태 지도: <원본 ref / 파생 computed / 부수효과 watch 분류>
### 데이터 흐름: <props 하향 / emit 상향 지점>
### 검증: $ vue-tsc → <결과> / 테스트 <1줄>
### 확인 필요
```

### 작성 예시

```
## 종목 검색 자동완성 (가정)
### 상태 지도: query(ref 원본) / suggestions(검색 결과 — watch+onCleanup, 안티패턴 5 방어) / hasResults(computed 파생)
### 데이터 흐름: 선택 시 emit('select', item) — 부모가 v-model로 수신
### 검증: $ vue-tsc → 0건 / vitest 5 passed (stale 응답 경합 테스트 포함)
### 확인 필요: 디바운스 간격 300ms는 UX 합의 필요
```

❌ "reactive에서 꺼내 쓰는데 화면이 안 바뀌네 → forceUpdate 검색"
✅ "추적이 끊기는 지점(구조분해)을 규칙으로 알고 toRefs — 원리에서 도출"

### 사용자가 권고를 거부하면

- "Options API가 익숙해서 계속 쓴다" → 기존 코드베이스 일관성이면 정당 — 신규 파일만 Composition 제안, 거부 시 기록(partial).
- "index key로 충분하다" → 정적·추가전용 목록이면 실제로 충분 — 동의가 맞다. 편집 가능 목록이면 밀림 버그 1줄 경고 후 존중·기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

### 판단 불가 시 (확인 절차)

- **무엇이 막히나**: ① 전역 상태로 올릴지 컴포넌트 로컬에 둘지(공유 범위가 코드만으론 안 보일 때) ② 디바운스 간격·페이지 크기 등 UX 수치 ③ Options 잔존 코드베이스에 신규를 Composition으로 섞을지(팀 컨벤션 부재 시) ④ Vapor(3.6) 도입 가부 — 안정화 여부가 외부 사실.
- **누구에게/어떻게**: 사용자에게 (대상 / 현재 후보안 / 근거 / 기대 답변) 4요소로 질의 — 추측으로 전역 store를 만들거나 UX 수치를 박고 진행하지 않는다. 예: "이 검색 상태를 (대상)Pinia store로 올릴지 / (현 후보)컴포넌트 로컬 ref / (근거)현재 한 화면에서만 쓰임 / (기대)다른 화면도 공유합니까?"
- **기대값**: 답을 받으면 그대로 반영. 못 받으면 가장 보수적 기본값(로컬 ref·`<script setup>` Composition·디바운스 300ms)으로 진행하고 해당 줄에 `// 확인 필요:` 라벨을 남긴다(partial — 전체 보류 금지).

## 실전 케이스 — 유럽 공공기관 폼 데이터 뒤섞임 (index key 부류의 반복 실증)

단일 유명 장애보다 **무수히 반복 보고되는 패턴**으로 존재하는 사고: 행 삭제 가능한 동적 폼(신청서 명부 등)에서 index key 사용 → 중간 행 삭제 시 아래 행들의 입력값·체크 상태가 한 칸씩 밀려 **다른 사람의 데이터와 짝지어짐**. 제출된 데이터가 화면과 달라 사후 정정 불가능한 데이터 오염이 된다. Vue 공식 문서가 key를 "필수에 준하는" 강도로 경고하는 이유이며, 테스트로도 잘 안 잡힌다(단건 입력 테스트는 통과, 삭제 후 입력 시나리오에서만 발현). 교훈: ① key는 성능 최적화가 아니라 **정합성 장치** ② "편집 가능한 목록 + index key" 조합은 코드 리뷰 즉시 반려 항목. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — 반응성 절단·index key·stale 응답 실증 (코어스펙 1겹)
- `references/evidence-checklist.md` — 출처(vuejs.org·VueUse) + 출고 전 체크리스트 + 점검 주기

## 한계

- Nuxt(SSR·라우팅·서버 계층)는 본 스킬 범위 밖 — Vue 계층만 담당하고 Nuxt 고유 사항은 공식 문서 우선(부패 빠름).
- 3.6 Vapor 모드는 2026-06 기준 beta(beta.9, stable 미정) — 본 스킬 내용은 vDOM 기준이며 Vapor는 vDOM 없이 컴파일하는 별도 렌더 모드(SolidJS류). 컴포넌트 단위 opt-in이라 본 스킬의 반응성 원칙(ref/computed/구조분해 함정)은 Vapor에서도 동일하게 적용된다 — 세부는 vuejs.org 확인.
- 사용자 주력이 React 생태계라면(기존 프로젝트 다수) 신규 프로젝트 프레임워크 선택 논의는 중립적으로 — 이 스킬은 Vue 선택 이후의 매뉴얼이다.
