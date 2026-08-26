# biz-motion-designer — 원칙 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30/07-01 웹 검증. 1단계 참조. 실무 파일: `easing-duration-tokens.md`.

## 1. 디즈니 12원칙 (정전)
Frank Thomas & Ollie Johnston, *The Illusion of Life: Disney Animation*(초판 1981, Abbeville Press; 1995 Disney Editions/Hyperion 재판). 순서: Squash&Stretch·Anticipation·Staging·Straight Ahead/Pose to Pose·Follow Through&Overlapping·Slow In/Out·Arc·Secondary Action·Timing·Exaggeration·Solid Drawing·Appeal.

## 2. 접근성 (WCAG — w3.org 직접 확인) ⚠️ 레벨 교정
- **SC 2.2.2 Pause, Stop, Hide = Level A**(5초+ 자동 이동 콘텐츠 정지 가능). https://www.w3.org/WAI/WCAG21/Understanding/pause-stop-hide.html
- **SC 2.3.3 Animation from Interactions = Level AAA**. https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html
- (2차 출처가 레벨을 자주 오기 — A/AAA 정확히.)
- `prefers-reduced-motion`(MDN, 2020 Baseline) — "reduce"=비필수 모션 최소화/대체(전부 제거 아님). https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion

## 3. 이징·타이밍 (Material — 검증)
표준 곡선 `cubic-bezier(0.4,0,0.2,1)`, decelerate `(0,0,0.2,1)`, accelerate `(0.4,0,1,1)`. 진입 ease-out, 퇴장 ease-in. 모바일 ~300ms 기준(진입 225/퇴장 195), 데스크톱 ~150~200ms, >400ms는 느리게 느껴짐. https://m1.material.io/motion/duration-easing.html
- ✅ **M3 명명 duration 토큰 확정**(Flutter `Durations` API로 교차 검증, https://api.flutter.dev/flutter/material/Durations-class.html): short1–4 = **50/100/150/200ms**, medium1–4 = **250/300/350/400ms**, long1–4 = **450/500/550/600ms**, extralong1–4 = **700/800/900/1000ms**. ⚠️ **"375ms"는 M3 토큰에 존재하지 않음**(이전판 오기) — 인용 금지. 토큰 페이지 https://m3.material.io/styles/motion/easing-and-duration/tokens-specs 는 JS 렌더라 WebFetch 빈 본문 → Flutter API 값으로 확정.
- Apple HIG Motion https://developer.apple.com/design/human-interface-guidelines/motion

## 4. 성능·구현 접점 (실무 확장) ✅ 검증
- **프레임 예산 = 16.66ms/프레임**(60fps). 이 안에 레이아웃+페인트+컴포짓 완료해야 매끄러움. 저사양·120fps면 예산 더 빠듯.
- **컴포짓 전용 속성만 애니메이트**: `transform`·`opacity`는 GPU 컴포짓 단계라 저렴. `width/height/top/left/margin/padding/font-size`는 매 프레임 **리플로우**(layout+paint) → jank. 색·그림자는 paint 유발(중간).
- `will-change` / `transform: translateZ(0)`로 레이어 승격 가능하나 **GPU 메모리 소비** — 남발 금지, 애니 직전 켜고 후 해제.
- **스태거(stagger)**: 목록 요소를 오프셋으로 순차 등장 → 생동감. 단 **~8~10개에서 캡** — 그 이상은 마지막이 너무 늦어 답답.
- 스프링/오버슈트: `cubic-bezier`로 바운스 근사 가능하나 과하면 산만. UI는 미묘하게. 구현은 → dev.

## 5. 실무 모션 패턴 (맥락별)
상세 토큰·패턴은 `easing-duration-tokens.md`. 요지: 진입=ease-out+짧게, 퇴장=ease-in+더 짧게, 강조/영구=ease-in-out, 스피너/진행바=linear(유일한 linear 정당 용례).

## 6. 교정
2.2.2=A, 2.3.3=AAA(혼동 빈번). 선형 이징은 부자연 — 스피너/진행에만. 12원칙은 UI 모션에 *응용*되는 것(원래 캐릭터 애니). 성능=transform/opacity만 애니. 375ms는 M3에 없음.

## 7. 출처
- Thomas & Johnston, *The Illusion of Life*(1981). · WCAG 2.1(W3C). · Material Design Motion. · Apple HIG. · Flutter `Durations` API(M3 토큰 교차검증). · web.dev/MDN 애니메이션 성능.
