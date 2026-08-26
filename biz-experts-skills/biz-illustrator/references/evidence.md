# biz-illustrator — 시스템 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30/07-01 웹 검증. 1단계 참조. 실무 파일: `illustration-system.md`.

## 1. 색 (정전 — 두 학파 구분)
- ✅ **Josef Albers, *Interaction of Color*(Yale University Press, 1963)** — 색은 가장 상대적인 매체, 지각은 맥락 의존(relativity).
- ✅ **Johannes Itten, *Kunst der Farbe*(Otto Maier, Ravensburg, 1961; 영역 *The Art of Color*, Van Nostrand Reinhold, 영문 완역판 1973)** — 색 심리·상징, 이텐 색상환, 7대비(harmony). 연도·출판사 확인.
- ⚠️ Albers(상대성) vs Itten(조화/상징)은 **상반된 목적** — 혼동 금지.
- HSB 모델 ⚠️ Alvy Ray Smith(1978).

## 2. 구성·실루엣
- **Appeal(Thomas & Johnston, *Illusion of Life* 1981)** = 명료·가독·매력(귀여움 아님 — 악당도 appeal 가능). 실루엣 명료성.
- 룰 오브 서드 ⚠️ John Thomas Smith(1797) 명명. 시선 흐름·초점·여백.

## 3. 벡터·접근성 (W3C 직접 확인)
- ✅ **SVG 1.1 (Second Edition) = W3C Recommendation, 2011-08-16** 현행 안정 표준(W3C 권고일 확인). https://www.w3.org/TR/SVG11/ · https://www.w3.org/standards/history/SVG11/ (⚠️ SVG 2는 아직 Candidate/Draft — 현행 Rec 아님).
- WCAG: **1.4.3 텍스트 대비 ≥4.5:1**(큰 텍스트 3:1), **1.4.11 비텍스트 ≥3:1**, **1.4.1 색만으로 정보 전달 금지(Level A)**. 본문은 4.5:1(3:1은 큰 텍스트/UI만). 반올림 금지.
- Microsoft Inclusive Design Toolkit(persona spectrum). https://inclusive.microsoft.design/

## 4. 스타일 시스템·재현성 (실무 확장) ✅ 검증
- **일러스트 시스템 = 규칙을 한 번 정하고 반복**(에셋마다 재발명 금지)해야 통일감. 규칙 요소: 선 굵기·팔레트·그리드·모서리 반경·조명 방향·원근·인물 비율. 상세는 `illustration-system.md`.
- **선 굵기(line weight) 규칙** ✅: 한 일러스트 내 **선 굵기 종류 ≤ 4개**(명확히 구별될 때만 혼용). IBM Design Language line-style도 제한된 굵기 세트 + 그리드로 일관성. https://www.ibm.com/design/language/illustration/line-style/design/
- **그리드·모서리 반경**: 아이콘·일러스트를 공통 그리드(예: 24px/48px) + 통일 corner radius로 → 세트가 한 손에서 나온 듯. Airbnb 3D 일러스트는 균일 형태·깊은 그림자·균형 팔레트를 시스템으로 규정.
- **팔레트 제한**: 핵심 색 소수로 제한하고 명도 단계만 확장 → 재현성. 색 수가 많을수록 통일 붕괴.

## 5. 실전 케이스
Airbnb DLS — Karri Saarinen, "Building a Visual Language"(절제 원칙). https://medium.com/airbnb-design/building-a-visual-language-behind-the-scenes-of-our-airbnb-design-system-224748775e4e ⚠️ Slack/Dropbox 일러스트 시스템은 1차 스펙 URL 미확인 — unverified.

## 6. 포맷 (실무)
- **SVG**(벡터, 무한 확대·경량·CSS 제어) = 아이콘·플랫/라인 일러스트·로고. 현행 Rec은 SVG 1.1(2011).
- **PNG**(래스터, 투명) = 복잡 렌더·3D 일러스트 · **WebP/AVIF**(경량 웹). **PDF/AI/EPS**(인쇄·원본).
- 텍스처·회화풍은 래스터(PSD/PNG), 재편집·확대 필요하면 벡터(SVG/AI).

## 7. 교정
Albers≠Itten. Appeal≠귀여움. 본문 4.5:1(3:1은 큰 텍스트/UI 그래픽만). 색만으로 정보 전달은 1.4.1 위반. SVG 1.1(2011)이 현행 Rec(SVG 2 아님). 시스템=규칙 반복(선 굵기 ≤4·팔레트 제한·그리드).

## 8. 출처
- Albers(1963)·Itten(1961/1973). · Thomas & Johnston(1981). · W3C SVG 1.1·WCAG 2.1. · Microsoft Inclusive Design. · IBM Design Language(일러스트 line-style). · Airbnb "Building a Visual Language."
