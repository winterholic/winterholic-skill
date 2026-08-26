# biz-ui-designer — 규칙 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 웹 검증. 1단계 참조.

## 1. 위계 (Refactoring UI)
강조 = 크기+굵기+명도/색의 약한 조합. "약화"로 위계(덜 중요한 건 회색·작게). 주요 액션 1개. https://www.refactoringui.com/

## 2. 타이포·스케일
제한된 모듈러 스케일, 굵기 2~3. 본문 줄 길이 **45~75자(66 이상적)** — Bringhurst *The Elements of Typographic Style*. http://webtypography.net/2.1.2

## 3. 색·대비 (WCAG, W3C 직접 확인)
- **1.4.3 텍스트 대비**(레벨 AA): 일반 ≥4.5:1, **큰 텍스트 ≥3:1**. 큰 텍스트 정의(W3C 1차) = **18pt(≈24px) 이상, 또는 14pt(≈18.66px) 볼드 이상**. https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
- **1.4.11 비텍스트 대비**: UI/의미 그래픽 ≥3:1. https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html
- 대비 비율 반올림 금지(2.999는 3:1 미달).

## 4. 게슈탈트 (검증)
근접·유사·폐쇄·연속·전경/배경(Wertheimer, Köhler·Koffka, ~1923). "common region"은 Palmer(1992) 후대 추가. 학술: https://pmc.ncbi.nlm.nih.gov/articles/PMC3482144/

## 5. 간격 시스템
8dp(Material) 등은 **표준이 아니라 관례**(Shopify Polaris는 4px 단위). 일관성이 핵심이지 특정 숫자가 법은 아님.

## 6. 터치 타깃 (근거 명확 — 헷갈림 교정)
- **WCAG 2.5.8 Target Size (Minimum) = 24×24 CSS px, 레벨 AA**(최소). https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- **WCAG 2.5.5 Target Size (Enhanced) = 44×44 CSS px, 레벨 AAA.** https://www.w3.org/WAI/WCAG21/Understanding/target-size.html
- **Apple HIG 최소 44×44 pt** https://developer.apple.com/design/tips/ · **Material 최소 48×48 dp** https://m3.material.io/foundations/designing/structure
- **교정**: "44px가 WCAG AA"는 오류 — 그건 AAA(2.5.5). AA 하한은 24px. 모바일 실무 권장은 44~48px(Apple/Material 근거).

## 7. 교정 (미신·과장 제거)
- **황금비 미신**: 파르테논·인체미 주장은 근거 없음(Markowsky 1992). UI 비례 정당화에 황금비 인용 금지.
- **8pt 그리드는 표준 아님**(관례). **60-30-10 색 규칙**은 **권위 있는 1차 출처 없음(인테리어 디자인 관례)** — 웹 검증 결과 개인·publication 귀속 근거 발견 못함. "법칙"으로 인용 금지, 출발 가이드로만.

## 8. 실무 상세 레퍼런스 (신설)
- `references/type-color-scale.md` — 타입 스케일(모듈러 비율·px 스텝)·라인하이트·measure·WCAG 대비 실무표·색 시스템·상태색·8pt.
- `references/ui-checklist.md` — 시각 위계 5수단·타이포·색대비·간격/그리드·컴포넌트 상태 매트릭스·터치 타깃·깊이·종합 진단 순서(A~H 체크리스트).

## 출처
- Adam Wathan & Steve Schoger, *Refactoring UI*(2018). · Robert Bringhurst, *The Elements of Typographic Style*. · WCAG 2.1(W3C). · Material(8dp)·Apple HIG·IBM Carbon 토큰.
