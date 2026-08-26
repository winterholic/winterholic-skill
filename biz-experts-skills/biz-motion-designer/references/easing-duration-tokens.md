# 이징·듀레이션 토큰 & 접근성 실무 사양 (실전)

> 근거: Material Design Motion(M1/M3) · Apple HIG Motion · WCAG 2.1 · web.dev/MDN 애니메이션 성능. 값의 최종 출처는 플랫폼 공식 가이드.

## 1. 듀레이션 토큰

### Material 3 명명 토큰 (Flutter Durations API로 확정)
| 토큰 | 값 | 용도 |
|------|-----|------|
| short1–4 | 50 / 100 / 150 / 200ms | 아이콘·셀렉션·작은 상태 변화 |
| medium1–4 | 250 / 300 / 350 / 400ms | 컴포넌트 진입/퇴장·확장 |
| long1–4 | 450 / 500 / 550 / 600ms | 큰 표면 전환·풀스크린 |
| extralong1–4 | 700 / 800 / 900 / 1000ms | 대형·강조 연출(드묾) |

⚠️ **"375ms"는 M3 토큰에 없음** — 인용 금지.

### 실무 경험칙 (플랫폼 무관)
- **작을수록 빠르게, 클수록 길게**: 토글/체크 ~100ms, 버튼 상태 ~150ms, 카드/모달 진입 ~250~300ms, 페이지 전환 ~300~400ms.
- **퇴장 < 진입**: 나가는 건 더 빠르게(사용자는 이미 다음으로 이동 중). Material: 진입 225 / 퇴장 195ms.
- **>400ms 지양**: UI 전환이 400ms 넘으면 "느리다" 체감. 대형 연출만 예외.
- 데스크톱은 모바일보다 짧게(~150~200ms) — 마우스는 빠른 피드백 기대.

## 2. 이징 곡선 (cubic-bezier)

| 상황 | 곡선 | 이유 |
|------|------|------|
| 진입(enter) | ease-out `(0,0,0.2,1)` | 빠르게 들어와 부드럽게 정착 |
| 퇴장(exit) | ease-in `(0.4,0,1,1)` | 천천히 시작해 빠르게 사라짐 |
| 강조/영구/이동 | standard/ease-in-out `(0.4,0,0.2,1)` | 화면 내 이동 |
| 스피너·무한 진행 | **linear** | 등속이 자연스러운 **유일** 정당 용례 |

- **linear를 UI 전환에 쓰지 말 것** — 기계적·죽은 느낌. 현실 물체는 가속·감속.
- 오버슈트/바운스: `cubic-bezier(0.34,1.56,0.64,1)` 류(제어점 y>1). 재미 요소이나 과하면 산만 — UI는 미묘하게.

## 3. 성능 사양 (매끄러움의 물리)

### 프레임 예산
- 60fps = **16.66ms/프레임**. 이 안에 layout+paint+composite 완료. 넘으면 프레임 드롭(jank).

### 애니메이트할 속성 (비용 순)
- ✅ **저렴(compositor only)**: `transform`(translate/scale/rotate), `opacity` — GPU가 처리, 레이아웃/페인트 없음.
- ⚠️ **중간(paint)**: `color`, `background`, `box-shadow`, `border-radius` — 매 프레임 리페인트.
- ❌ **비쌈(layout/reflow)**: `width`, `height`, `top`, `left`, `margin`, `padding`, `font-size` — 매 프레임 레이아웃 재계산. **애니메이트 금지**, `transform`으로 대체(예: `left` 대신 `translateX`).

### 레이어 승격
- `will-change: transform` 또는 `transform: translateZ(0)`로 GPU 레이어 강제. **GPU 메모리 소비** → 애니 직전 켜고 끝나면 해제, 상시 남발 금지.

## 4. 스태거 (순차 등장)
- 목록/그리드 요소를 40~80ms 오프셋으로 순차 등장 → 생동감·시선 유도.
- **~8~10개에서 캡**: 그 이상은 마지막 요소가 너무 늦게 나와 답답. 큰 목록은 첫 화면 보이는 것만 스태거.

## 5. 접근성 (필수, 선택 아님)

### prefers-reduced-motion
```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important; }
}
```
- "reduce" = **비필수 모션 최소화/대체**(전부 제거 아님). 상태 변화 자체는 즉시 전환(fade 정도)로 유지.
- 시차(parallax)·큰 이동·회전·확대 같은 **전정계 트리거** 모션을 우선 제거.

### WCAG 준수
- **SC 2.2.2 (A)**: 5초+ 자동 재생/이동/깜빡임 콘텐츠는 정지·일시정지 수단 제공.
- **SC 2.3.3 (AAA)**: 상호작용으로 유발되는 모션은 비활성화 가능하게.
- **정보를 모션에만 의존 금지**: 모션 끈 사용자·저사양 기기도 같은 정보를 아이콘·텍스트·상태색으로 받아야.
- **깜빡임**: 초당 3회 이상 번쩍임 금지(광과민성 발작, SC 2.3.1).

## 6. 산출 포맷 (Lottie/영상/코드)
- **Lottie(.json)**: 벡터 기반 경량, 해상도 독립, 색·속도 런타임 제어. AE→Bodymovin/LottieFiles. 복잡 셰이더·마스크는 미지원 주의.
- **영상(.mp4/webm)**: 사실적·복잡 연출. 파일 크고 색/속도 고정.
- **코드(CSS/JS/Rive)**: 인터랙티브·상태 반응. 구현은 → dev-css-tailwind/dev-react.
- 명명: `{컴포넌트}_{상태}.{ext}` (예: `button_press.json`, `toast_enter.json`, `spinner_loop.json`).
