# Base CSS — html-report 디자인 시스템

**v2.0 기준 — CSS 정본은 `templates/base.html` 의 `<style>` 인라인 블록이다.** 이 markdown은 더 이상 별도 정본을 두지 않는다 (sync 부담 회피).

## 왜 stub인가?

- v1에서는 markdown에 전체 CSS를 복사해 정본 역할을 했지만, 토큰 체계가 v2(Toss-inspired)로 전면 개편되면서 두 파일을 매번 동기화하는 부담이 컸다.
- 단일 진실 원천(single source of truth)은 `templates/base.html`. 새 보고서는 base.html을 복제해서 시작하면 된다.

## CSS를 보고 싶다면

```bash
# Style 블록 전체
sed -n '/^<style>/,/^<\/style>/p' ~/.claude\skills\html-report\templates\base.html
```

또는 에디터에서 `templates/base.html` 을 열고 `<style>` 블록을 참조 (줄 범위는 버전에 따라 다르므로 마커로 찾을 것).

## CSS 수정 절차

1. `templates/base.html` 의 `<style>` 블록만 수정 (정본)
2. 토큰 의미·정책이 바뀌었으면 `references/design-system.md` 갱신
3. 새 컴포넌트 추가했으면 `references/components.md` 에 HTML 스니펫 + Quick Reference 표 갱신
4. 시각 확인은 `examples/_design-catalog.html` 을 브라우저로 열어 검토 (또는 새 컴포넌트를 카탈로그에 추가)

## CSS 구조 개요 (정본 base.html 의 섹션 인덱스)

| 섹션 | 내용 |
|------|------|
| 1 | DESIGN TOKENS (Light) — Brand·Neutral·Semantic·Typography·Spacing·Radius·Layout·Motion |
| 2 | DESIGN TOKENS (Dark override) |
| 3 | BASE — html, body, ::selection, reduced motion |
| 4 | LAYOUT — `.page`, `.toc`, `.content`, 반응형 |
| 5 | TYPOGRAPHY — h1~h4, p, a, strong, code, ul/ol, blockquote |
| 6 | REPORT HEADER — `.report-header`, `.kicker`, `.subtitle`, `.report-meta` |
| 7 | BADGE — `.badge.{primary\|success\|warn\|danger\|info\|muted}` |
| 8 | CALLOUT — `.callout.{note\|info\|success\|warn\|danger}` + SVG sprite icon |
| 9 | TL;DR — 좌측 4px primary bar + surface card |
| 10 | GRID & CARD — `.grid.cols-{2,3,4}`, `.card.{outline\|highlight}` |
| 11 | STAT / KPI — sans bold (mono 폐기) |
| 12 | PROSCONS — 중립화 기본, `.pros`/`.cons` 명시 클래스로 색 옵트인 |
| 13 | TABLE — 일반·`.decision.winner` |
| 14 | TIMELINE — dot 14px, `.item.{done\|active\|warn\|danger}` |
| 15 | STEPS — grid 2칸(32px 번호 + 1fr), title·desc는 grid-column:2 고정, absolute 폐기 |
| 16 | COMPARE — `.side.{danger\|success\|primary}` 옵트인, 모바일 arrow 숨김 |
| 17 | CODE BLOCK — 다크 배경 고정 |
| 18 | PROGRESS — primary/success/warn/danger |
| 19 | CHECKLIST — 인터랙티브 |
| 20 | RISK HEATMAP — 3×3, axis cell 가독성 개선 |
| 21 | Q&A TOGGLE — chevron 아이콘 회전 |
| 21.5 | 독자 보조 레이어 — `.term`(인라인 점선 힌트), `details.primer`(접이식 배경지식, 좌측 primary bar), `dl.glossary`(하단 용어집 grid) |
| 21.7 | FORMULA & WORKED EXAMPLE — `.formula`(mono 수식 블록 + `.fx-comment`/`.fx-hl`), `dl.formula-where`(변수 legend), `.example`(숫자 예시 박스) |
| 22 | MERMAID WRAP |
| 23 | FOOTER |
| 24 | THEME TOGGLE |
| 25 | UTILITIES |
| 26 | PRINT (@media print) |

## 토큰 명세

`references/design-system.md` 참조. 이 파일은 CSS 코드의 위치 안내, design-system.md 는 토큰·원칙의 명세.
