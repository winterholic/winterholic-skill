# evidence + 출고 전 체크리스트

## 실증·출처

- **vuejs.org "Reactivity Fundamentals" / "Reactivity in Depth"** — Proxy 기반 반응성 추적, `reactive` 구조분해 시 추적 단절, `toRefs` 처방의 1차 출처(안티패턴 1).
- **vuejs.org "Computed Properties" / "Watchers"** — 파생값은 computed, 부수효과는 watch라는 공식 구분(안티패턴 2). watch의 `onCleanup`(3.5+에서 `onWatcherCleanup` API도 제공)이 비동기 경합 전용 도구라는 설명(안티패턴 5).
- **vuejs.org "List Rendering — Maintaining State with key"** — v-for key가 정합성 장치(성능 아님)라는 공식 경고(안티패턴 4).
- **vuejs.org "Props — One-Way Data Flow"** — props 직접 변경 금지·`emit('update:x')`/`v-model` 패턴(안티패턴 3).
- **VueUse 설계 관행** (vueuse.org) — composable이 reactive가 아니라 refs 묶음을 평평하게 반환하는 생태계 표준(안티패턴 1·6의 API 설계 근거).
- **Vue 3.6 Vapor 모드 — beta** (github.com/vuejs/core, 2026-06 기준 3.6.0-beta.9) — vDOM 없는 컴파일 렌더 모드, 컴포넌트 단위 opt-in, stable 시점 미정(H2 2026 목표). 정량 기준표·한계의 근거. **확인 필요**: stable 릴리스 시점은 vuejs.org/blog 추적.
- **eslint-plugin-vue 10.x** (github.com/vuejs/eslint-plugin-vue, npm) — ESLint 9 flat config(`eslint.config.js`) 기준, `--ext` 플래그 불필요. 워크플로우 검증 명령의 근거.
- **Pinia** (pinia.vuejs.org) — Vuex를 대체하는 공식 권장 상태 라이브러리. 정량 기준표 "전역 상태" 행의 근거.

## 출고 전 체크리스트 (Vue 컴포넌트/composable 출고 시)

- [ ] reactive를 구조분해해서 쓰지 않았다 (또는 toRefs / 개별 ref)
- [ ] composable 반환이 refs 묶음이다 (reactive 통째 반환 아님)
- [ ] 파생값은 computed, watch는 부수효과 전용 (watch로 상태 동기화 0건)
- [ ] props를 직접·내부 필드까지 변경하지 않았다 (emit/v-model)
- [ ] v-for key가 안정 고유 id (편집 가능 목록에 index key 0건)
- [ ] 비동기 watch에 onCleanup(또는 AbortController) 경합 방어가 있다
- [ ] 책임 3개+ 또는 ~300줄 SFC는 composable/자식으로 분리됐다
- [ ] 신규 파일은 `<script setup>` + Composition (Options 신규 0건)
- [ ] `vue-tsc --noEmit` 0건 + `eslint` 통과 (flat config)
- [ ] 상호작용 1개 이상 실동작 확인 (vitest 또는 수동)

## 점검 주기 (부패 빠름 — 분기)

- Vue minor 버전 추적(현재 3.5.x 라인) → 버전 라벨 갱신.
- **Vapor 모드(3.6) stable 승격 여부** — beta→stable 전환이 가장 중요한 추적 항목(현재 beta.9, H2 2026 목표). stable 시 정량 기준표·한계의 "도입 보류" 문구 갱신.
- eslint-plugin-vue 메이저 변화(현재 10.x — ESLint 9 flat config) 및 Pinia 메이저 변화.
- VueUse 계약(refs 반환)·공식 문서의 key/watch cleanup 권고 재확인.
