# biz-graphic-designer — 원칙 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30/07-01 웹 검증. 1단계 참조. 실무 파일: `grid-type-color-spec.md`.

## 1. 정전 소스
- **Josef Müller-Brockmann, *Grid Systems in Graphic Design / Raster systeme für die visuelle Gestaltung*** — ✅ 확정: 이 책(독·영 이중언어판, ISBN 3721201450)의 **초판은 1981년 Niggli(Niederteufen)**. 흔히 인용되는 "1961"은 이 책이 아니라 그의 그리드 이론이 강연·축약 저작(*Gestaltungsprobleme des Grafikers*, 1961)으로 등장한 시점 — 책 *Grid Systems* 자체의 연도로 1961을 쓰면 오류. 스위스(국제 타이포그래피) 그리드. https://www.amazon.com/dp/3721201450
- **Jan Tschichold, *Die neue Typographie*(1928)** — 모더니즘 선언(비대칭·산세리프·기능적 위계). ⚠️ Tschichold가 후일 그 교조성을 철회 — "최종 입장"으로 인용 금지.
- **Robert Bringhurst, *The Elements of Typographic Style*(1992)** — measure/leading/모듈러 스케일; "45~75자/줄, 66 이상적." http://webtypography.net/2.1.2

## 2. 게슈탈트 (검증)
Wertheimer(+Köhler·Koffka, ~1923): 근접·유사·폐쇄·연속·전경/배경. "전체는 부분의 합과 다르다." 학술: https://pmc.ncbi.nlm.nih.gov/articles/PMC3482144/

## 3. 매체별 제작 (교정)
- **RGB(가산)가 CMYK(감산)보다 색역 넓음** — 채도 높은/네온 색은 인쇄 시 칙칙해짐. CMYK/소프트프루프로 디자인.
- **PPI(픽셀/인치, 화면 ~72 레거시/인쇄 300 목표) vs DPI(프린터 잉크점 밀도)** — 흔히 혼동.
- 인쇄 표준: **재단여백(bleed) 3mm + 안전여백 3~5mm.**

## 4. 위계·스위스 스타일
Helvetica(1957, Max Miedinger·Eduard Hoffmann; 원명 Neue Haas Grotesk, 1960 개명). Ernst Keller(취리히 공예학교, 1918~)=교육적 뿌리. 취리히(그리드+Helvetica) vs 바젤(Univers/Frutiger) 축.

## 5. 실무 사양 (실전 확장)
- **모듈러 스케일(음악 비율 기반)** ✅ 검증: Minor Second 1.067 · Major Second 1.125 · Minor Third 1.2 · **Major Third 1.25**(가장 흔함) · Perfect Fourth 1.333 · Perfect Fifth 1.5 · **Golden 1.618**. base(예: 16px)에 비율을 곱/나눠 조화로운 크기 세트를 생성. https://alistapart.com/article/more-meaningful-typography/ 상세는 `grid-type-color-spec.md`.
- **베이스라인 그리드·수직 리듬**: 행간을 기준 단위(예: 8px)의 배수로 정렬 → 요소가 공통 그리드에 앉아 "정돈된" 느낌. 8-point grid가 UI 사실상 표준.
- **측정(measure)**: Bringhurst 45~75자/줄(다단은 40~50자). 너무 길면 다음 줄 찾기 어렵고, 너무 짧으면 리듬이 끊김.
- **행간(leading)**: 본문 행간 = 폰트 크기 × 1.4~1.6(웹 관행 line-height 1.5). 긴 줄일수록 행간 크게.

## 6. 그리드 유형 (실무)
- **Manuscript(단일 블록)**: 책 본문·장문.
- **Column(다단)**: 잡지·신문·웹. 웹은 **12컬럼**이 사실상 표준(2·3·4·6 분할 유연).
- **Modular(모듈)**: 갤러리·대시보드·카드 레이아웃(행+열 격자).
- **Baseline**: 수직 리듬 정렬.
- 구성요소: margin(외곽)·column(단)·gutter(단 사이 여백, 웹 관행 16~24px)·module.

## 7. 교정
Müller-Brockmann(Niggli, 1981). Tschichold(1928, 후일 철회). Bringhurst(1992). RGB>CMYK 색역. PPI≠DPI. 모듈러 스케일=음악 비율 유래(임의 숫자 아님).

## 8. 출처
- Müller-Brockmann(Niggli, 1981). · Tschichold(1928). · Bringhurst(1992). · A List Apart, "More Meaningful Typography." · 스위스 연방 문화 https://www.aboutswitzerland.eda.admin.ch/en/swiss-style-forever-the-story-of-a-graphic-design-tradition
