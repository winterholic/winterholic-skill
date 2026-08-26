# biz-design-system — 구조 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 웹 검증. 1단계 참조.

## 1. 아토믹 디자인 (Brad Frost)
원자→분자→유기체→템플릿→페이지. ⚠️ **폴더구조·순차 파이프라인이 아니라 멘탈 모델**(Frost 본인 명시). 무료 전문: https://atomicdesign.bradfrost.com/

## 2. 토큰 계층
원시(global/primitive/reference) → 시맨틱(alias/system) → 컴포넌트. 사용처는 시맨틱/컴포넌트만 참조(리브랜딩·다크모드 시 시맨틱만 변경). ⚠️ 계층 용어는 벤더마다 상이 — 개념만 합의. MD3는 `md.ref.*`→`md.sys.*`→`md.comp.*`로 명시. **3계층 실제 설계·네이밍 분류(Curtis)·DTCG 포맷 구조·다크/멀티브랜드 전략 상세 → `token-naming.md`.**

## 3. 토큰 표준 (정확한 지위)
**Design Tokens Format Module** — 첫 안정판 2025.10(2025-10-28 발표, DTCG). ⚠️ **정식 W3C 표준 아님**: 스펙 본문 명시 — "This is not a W3C Standard nor is it on the W3C Standards Track"(W3C **Community Group** 산출물). `$` 접두 규약(`$value` 필수 · `$type`/`$description`/`$deprecated`/`$extensions` 선택), 그룹 `$type` 상속, `{group.token}` alias, composite type(typography·shadow·border 등). 스펙: https://www.designtokens.org/tr/drafts/format/ · 발표: https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/

## 4. 거버넌스 (Nathan Curtis / EightShapes)
팀 모델 3종 — **Solitary**(자기 제품 우선, 남는 것 공유) / **Centralized**(전담팀 배포, 자기 제품 없음, "Overlords don't scale") / **Federated**(제품팀 대표 공동결정 + 중앙 문서화 필수). 소유·기여 절차·버전(semver, 토큰 이름 변경=MAJOR)·deprecation(병행 유예+마이그레이션 가이드)·채택 지표(커버리지·하드코딩 수·우회 컴포넌트). 채택 안 되면 팀이 자기 컴포넌트 양산 → 드리프트. Sparkbox 조사: 지표 추적 16%·거버넌스 보유 44%. **팀 모델·기여 워크플로우·semver·성숙도·성숙DS 비교(MD3/Carbon/Polaris) 상세 → `ds-playbook.md`.** https://medium.com/eightshapes-llc/team-models-for-scaling-a-design-system-2cf9d03be6a0

## 5. 접근성 내장
포커스 가시성(WCAG 2.4.7)·키보드 조작(2.1.1)·대비(1.4.3 텍스트/1.4.11 비텍스트)·모션 감소(2.3.3 + `prefers-reduced-motion`)·이름·역할·값(4.1.2, WAI-ARIA). 컴포넌트에 기본 탑재 → 사용처가 자동 준수. ARIA 1차: https://www.w3.org/TR/wai-aria-1.2/ · **ARIA 제1규칙**: "네이티브 HTML로 가능하면 ARIA를 쓰지 말라"(WAI-ARIA Authoring Practices).

## 6. 실무 심화 파일
- `token-naming.md` — 3계층 아키텍처, Curtis 네이밍 분류(base/modifier/object/namespace), DTCG 포맷 구조 상세, 다크/멀티브랜드 토큰 전략, 단일 소스 파이프라인.
- `ds-playbook.md` — 팀·거버넌스 3모델, 기여 워크플로우, semver·deprecation, 성숙DS 비교(MD3·Carbon·Polaris·Atlassian), 성숙도·채택 지표, 실전 체크리스트.

## 7. 출처
- Brad Frost, *Atomic Design*(2016) — https://atomicdesign.bradfrost.com/ · Alla Kholmatova, *Design Systems*(Smashing). · Nathan Curtis(EightShapes, 팀모델·네이밍·기여). · W3C DTCG *Format Module 2025.10*(Community Group, 정식 표준 아님). · Material Design 3(m3.material.io). · IBM Carbon(carbondesignsystem.com). · Sparkbox Design Systems Survey(성숙도·채택 지표).
