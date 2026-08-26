---
name: html-report
description: "마크다운 대신 가독성과 시각적 밀도가 높은 단일 HTML 문서를 만들 때 사용. 결정·보고 문서 6종(작업 계획서, 인프라 전환·리아키텍처 등 큰그림 분석 보고서, 라이브러리/툴 기술 검토 RFC, 시스템 설계, 회고, 장애 postmortem) + 지식 문서 3종(개념·기술 해설 explainer, 지표 산출·산식·알고리즘 방법론 명세, 절차 실행 가이드/runbook) + 증거 문서 2종(감사·점검 audit, 백테스트·벤치마크·실험 결과 results)을 모두 커버. 사용자가 'HTML 보고서', '보고서 만들어줘', '작업 계획서', '큰그림 그려줘', '분석 보고서', 'RFC', '기술 검토', '설계 문서', '회고서', '장애 회고', 'postmortem', '인시던트 리포트', '방법론 문서', '산출 방식 정리', '수식 정리', '개념 설명 문서', '해설 문서', 'X가 뭔지 정리해줘', 'tech overview', '가이드 문서', 'how-to', 'runbook', '온보딩 문서', '절차 문서', '점검 보고서', '감사', 'audit', '백테스트 결과', '벤치마크 결과', '실험 결과 정리', '측정 결과' 등을 언급하거나, 받은 업무·예정된 작업에 대한 정리·구상을 요청하면 트리거. 단순 코드 변경 설명·간단한 답변·README 작성에는 사용하지 않음. PR 리뷰 보고서는 별도 pr-review 스킬 사용."
---

# HTML Report — 보고서 작성 스킬

마크다운으로 만들면 너무 산만하거나 빈약해지는 기획·분석·검토·회고·해설·방법론·가이드·점검·실험결과 문서를, **단일 HTML 파일** 로 출력한다. 자체 디자인 시스템 + 컴포넌트 카탈로그 + 11가지 타입별 골격을 갖춰 두었으니, **콘텐츠 채우기에만 집중**한다. "디자인하지 말고, 콘텐츠를 슬롯에 매핑하라"는 철학을 그대로 따른다.

> **약어 빠른 풀이** — TL;DR = "Too Long; Didn't Read", 보고서 맨 위 1~2문장 요약. RFC = "Request for Comments", 설계 제안 문서. AS-IS / TO-BE = "현재 모습 / 목표 모습", 인프라·시스템 변경 시 격차를 보여주는 대비 구조. kicker = 헤더 제목 위에 작게 들어가는 보고서 분류 라벨 (예: "Analysis Report").

## Quick Start — 5분 만에 한 장 (긴급용)

급한 경우 아래 네 줄로 골격까지 도달:

```bash
TYPE=plan            # plan|analysis|invest|design|retro|incident|explain|method|guide|audit|results 중 택1
SLUG=foo             # 케밥 케이스 영문
OUT=~/.claude\reports\$(date +%Y-%m-%d)-$TYPE-$SLUG.html
cp ~/.claude\skills\html-report\templates\base.html "$OUT"
```

이후 `templates/{TYPE}.html` 본문을 `$OUT` 의 `<main class="content">` 안쪽에 붙이고 `{{...}}` 슬롯을 채운다. 자세한 절차는 아래 "워크플로우" 섹션 참조. 정상 케이스는 항상 워크플로우 전체를 따른다.

## 출력 결과물

- **포맷**: 단일 `.html` 파일 (CSS·JS 모두 인라인, 외부 의존은 Pretendard 폰트 CDN + Mermaid CDN 두 개뿐)
- **출력 디렉토리**: `~/.claude\reports\`
- **파일명 컨벤션**: `YYYY-MM-DD-{type}-{slug}.html` (type 약어와 슬러그 규칙은 `references/report-types.md` 참조)
- **특성**: 라이트/다크 모드 토글, 자동 TOC, 인쇄(A4) 친화, 한글 가독 최적화, **다이어그램·도표 클릭 확대**(라이트박스 + 휠 줌 + 드래그 팬)

## 워크플로우 (반드시 순서대로)

### 1단계 — 타입 결정

보고서 타입 11개 중 하나를 먼저 정한다. 본문 골격이 달라지므로 이 단계를 건너뛰면 안 된다. 사용자 발화로 명확하면 바로 결정, 모호하면 한 줄로 요약시켜 동사로 판별한다 (`references/report-types.md` 의 판단 플로우 참조).

**결정·보고 문서 6종** — "무엇을 할지/골랐는지/겪었는지"가 본문:

| 타입 | 약어 | 언제 | kicker |
|------|------|------|--------|
| Task Plan | `plan` | 받은 업무를 어떻게 할지 구상 결과 공유 | `Task Plan` |
| Analysis / Big-Picture | `analysis` | 방대한 작업 착수 전 전체 그림 (예: 인프라 전환) | `Analysis Report` |
| Tech Investigation | `invest` | 라이브러리·툴 옵션 비교·선정 | `Tech Investigation` |
| System Design / RFC | `design` | 새 기능·시스템 설계 제안 | `System Design` |
| Retrospective | `retro` | 작업 완료 후·스프린트·프로젝트 회고 | `Retrospective` |
| Incident Postmortem | `incident` | 운영 장애 회고 (blameless) | `Incident Postmortem` |

**지식 문서 3종** — "독자를 이해시키거나 따라 하게" 하는 게 본문. 두고두고 다시 찾아보는 정본(reference) 성격:

| 타입 | 약어 | 언제 | kicker |
|------|------|------|--------|
| Explainer | `explain` | 개념·기술·시스템을 독자 눈높이로 해설 ("X가 뭔지", tech overview) | `Explainer` |
| Methodology | `method` | 지표 산출·점수 산식·알고리즘 등 계산 방식의 정본 명세 | `Methodology` |
| Guide | `guide` | 설치·설정·운영 절차 how-to, runbook, 온보딩 | `Guide` |

**증거 문서 2종** — "검사/실험했더니 무엇이 나왔다"가 본문. 판정 기준·조건을 결과보다 먼저 고정:

| 타입 | 약어 | 언제 | kicker |
|------|------|------|--------|
| Audit | `audit` | 현재 상태를 기준에 대고 검사한 결과 (마이그레이션 잔재·설정·정합성 점검) | `Audit Report` |
| Results | `results` | 백테스트·벤치마크·A/B 실험·측정 결과 보고 | `Results Report` |

계열 간 경계 판단(섞인 요청 처리 포함)은 `references/report-types.md` 판단 플로우 참조.

### 1.5단계 — 독자 이해도 추론 (절대 건너뛰지 말 것)

**같은 보고서라도 독자의 배경지식에 따라 "좋은 보고서"가 갈린다.** 어떤 독자에겐 자명한 용어가 다른 독자에겐 보고서 자체를 이해 못 하게 만드는 벽이 된다. 그래서 콘텐츠를 채우기 전에 **"이 보고서를 누가 읽고, 그 독자가 무엇을 모를 가능성이 높은가"** 를 먼저 추론한다.

**질문하지 않는다.** 대화 맥락(사용자의 역할·요청 어투·주제)으로 추론해 기본값을 잡고 바로 진행한다. 과하거나 부족하면 사용자가 명시적으로 수정 요청한다. 완벽한 추론은 불가능하므로, 애매할 때는 **"덜 풀어서 못 알아듣는 것"보다 "조금 더 풀어서 보조 레이어에 담는 것"** 쪽으로 기운다 (보조 레이어는 접혀 있어 전문가를 방해하지 않으므로 비용이 낮다).

**무엇을 풀어쓸지 판단하는 휴리스틱** (예시일 뿐, 그대로 베끼지 말고 원리를 적용):

| 축 | 풀이 거의 불필요 | 풀이 권장 (보조 레이어) |
|----|----------------|----------------------|
| **특수 도메인** (주식·금융·의료·법률 등) | 독자가 그 도메인 종사자임이 분명할 때만 | 기본적으로 풀이. 비종사자가 섞일 여지가 조금이라도 있으면 배당락·증거금·T+2 같은 용어는 term/glossary |
| **기술 — 보편성** | 그 분야 실무자면 거의 다 아는 것: Docker, Git, REST, SQL JOIN, 환경변수 | 같은 분야라도 덜 보편적·고급: AWS Lambda/ElasticSearch, CQRS, eventual consistency, Raft, sidecar, 사가 패턴 |
| **아키텍처·인프라 구조** | 단순 CRUD·웹서버 구성 | 분산 트랜잭션, 메시지 큐 백프레셔, 멱등성 처리, 네트워크 토폴로지 — 다이어그램 + primer 병행 |
| **인접 분야 독자** | 독자가 그 코드/시스템의 주 담당일 때 | 백엔드 설계서를 프론트·기획·경영진이 읽을 가능성 → 핵심 개념은 primer 로 풀이 |

예: "AWS EC2/S3 기반 구성" 은 대부분 인프라 독자가 알지만, 같은 보고서의 "Lambda 콜드스타트", "OpenSearch 샤딩 전략" 은 모를 여지가 크다 → 후자만 골라서 보조 레이어로. **전부 풀거나 전부 안 푸는 게 아니라, 항목별로 선별한다.**

추론한 수준은 헤더 메타의 `대상` 필드(예: "인프라팀", "비개발 경영진")에 반영하면 독자에게도 보고서의 눈높이가 전달된다.

> **과잉 설명 경계** — 독자가 전문가임이 분명한데 기초까지 다 풀면 유치하고 장황해진다. 그래서 "본문에 다 풀어쓰기"가 아니라 **3단계의 보조 레이어(term/primer/glossary)로 분리**하는 것이 핵심이다. 본문 자체는 늘 간결하게 유지하고, 깊이는 접힌 레이어에 담는다.

### 2단계 — 베이스 + 골격 합치기

1. `templates/base.html` 를 출력 경로로 복사
2. 1단계에서 정한 타입의 `templates/{type}.html` 본문을 읽음 (이 파일들은 `<main class="content">` 안쪽에 들어갈 파편이다)
3. 복사한 base 안의 `<!-- ... 본문 시작 ... -->` 주석부터 `</main>` 직전까지 영역을, 골격 파편의 내용으로 교체 (줄 번호는 버전에 따라 다르므로 마커 주석을 Grep 으로 찾을 것). 단, base 의 `report-header`·`report-footer` 는 유지하고 그 사이의 자리표시 섹션(`#tldr`, `#context` 등)만 골격의 섹션들로 갈아 끼움
4. `<title>`, `<header class="report-header">` 의 kicker·제목·메타데이터 채움

**실행 예시 (Task Plan 보고서를 만들 때):**

```bash
# 1) 변수 설정
TYPE=plan
SLUG=payment-pg-migration
OUT=~/.claude\reports\$(date +%Y-%m-%d)-$TYPE-$SLUG.html

# 2) base 복사
cp ~/.claude\skills\html-report\templates\base.html "$OUT"

# 3) Claude Edit 도구로 OUT 의 본문 마커 자리에 templates/$TYPE.html 의 내용을 삽입
#    (수동 편집 시 base.html 안의 마커 주석을 찾아 그 줄을 골격 내용으로 교체)

# 4) Claude Edit 도구로 <title>·kicker·제목·메타데이터 채움

# 5) 슬롯({{...}}) 을 실제 콘텐츠로 교체

# 6) 브라우저로 확인
open "$OUT"
# 또는 헬퍼 스크립트
bash ~/.claude\skills\html-report\scripts\open_report.sh
```

> **주의**: 위 sed 같은 자동 합치기보다 Claude 의 Edit 도구로 단계별 수정하는 편이 안전. `templates/{type}.html` 의 들여쓰기와 줄바꿈을 그대로 보존해야 CSS 선택자가 깨지지 않는다.

### 3단계 — 콘텐츠 채우기

골격의 `{{...}}` 자리표시자를 실제 내용으로 교체. **컴포넌트 클래스를 임의로 바꾸지 않는다.**

> **점진 작성 원칙 (중간에 끊겨도 살아남게)**: 2단계에서 `cp`로 골격 파일이 이미 디스크에 있다. 이제 **섹션 단위로 Edit를 나눠** 채운다 — `#tldr` → `#context` → 다음 섹션 … 한 섹션을 채울 때마다 디스크에 반영된다. **전체 본문을 한 번의 거대한 Edit/Write로 통째 작성하지 않는다.** 보고서가 길거나 다이어그램·표가 많을수록 더 잘게 쪼갠다. 이렇게 하면 도중에 오류로 끊겨도 그때까지 채운 섹션이 파일에 남는다.

새 시각적 요소가 필요하면:

- 먼저 `references/components.md` 에서 적합한 컴포넌트가 있는지 확인
- 없으면 가장 가까운 컴포넌트를 변형 (CSS 변수만 활용, 새 클래스 추가 지양)
- 정말 필요한 경우만 새 스타일 추가 (이유를 주석으로 남김)

**1.5단계에서 추론한 독자 수준을 여기서 적용한다.** 독자가 모를 여지가 있다고 판단한 용어·개념은 본문을 늘리지 말고 **보조 레이어**로 분리 (스니펫은 `references/components.md` §17.5):

- **`.term`** — 한 번 짚고 넘어갈 짧은 약어·용어. 점선 밑줄 + 툴팁. 정본은 glossary 에도 등재.
- **`details.primer`** — 한두 문장으로 안 끝나는 개념(아키텍처 패턴·도메인 메커니즘). 접이식이라 전문가는 지나치고 초보만 펼침.
- **`dl.glossary`** — footer 직전에 도메인·기술 용어 정의를 모은 정본. 용어가 3개 이상이면 권장.

본문 문장 자체는 항상 간결하게. 깊이는 접힌 레이어에 담아 두 독자(전문가·초보)를 동시에 만족시킨다.

### 4단계 — 시각화 결정

각 보고서에 다이어그램 1~2개가 일반적으로 효과적. 너무 많으면 헷갈리니 **메인 다이어그램은 1개**.

| 표현하려는 것 | Mermaid 타입 |
|--------------|-------------|
| 시스템 구성·데이터 흐름 | `flowchart LR` 또는 `flowchart TD` |
| 데이터 모델 | `erDiagram` |
| 시계열 상호작용 | `sequenceDiagram` |
| 일정·마일스톤 | `gantt` |
| 상태 전이 | `stateDiagram-v2` |

다이어그램이 거의 필요 없는 타입 (Retrospective 등) 은 `base.html` 의 `<script src="...mermaid">` 두 줄을 지워도 됨.

> **클릭 확대 (내장)** — `.mermaid-wrap` 안의 다이어그램은 작아서 안 보일 수 있으므로, `base.html` 에 클릭하면 전체화면으로 확대되는 라이트박스가 내장돼 있다 (휠 줌 · 드래그 팬 · 더블클릭/⟲ 리셋 · ESC·배경 클릭 닫기). 렌더된 다이어그램에는 hover 시 "⤢ 클릭하여 확대" 힌트가 자동으로 뜬다. **별도 작업 불필요** — `.mermaid-wrap` 만 쓰면 자동 적용된다. 일반 `<img>` 나 큰 표 등 다른 요소도 확대 대상으로 만들려면 그 요소를 감싼 컨테이너에 `class="zoomable"` 을 추가하면 된다(내부의 첫 `<svg>`/`<img>` 가 확대됨). 다이어그램·이미지가 전혀 없는 보고서면 `zoom-overlay` div 와 Diagram Zoom 스크립트 블록을 삭제해도 무방.

### 5단계 — 검증

아래 항목을 모두 확인하기 전에는 완료로 표시하지 않는다.

- 모든 `{{...}}` 자리표시자가 제거됐는가?
- TL;DR 이 1~2문장 안에 끝나는가?
  - ❌ 나쁨: "이 보고서는 결제 모듈을 PG2에서 PG3로 옮기는 작업의 큰그림을 다루며, 4주에 걸친 단계 적용을 통해 안정적으로 전환하는 것을 목표로 하고, 다운타임을 최소화하면서…" (3줄 이상)
  - ✅ 좋음: "PG2 → PG3 전환을 4주에 걸쳐 단계 적용. 다운타임 목표 < 5분." (2문장)
- 표·callout·grid 중 종류가 너무 단조롭지 않은가? (3가지 이상 컴포넌트 혼합 권장)
- 메인 다이어그램이 의미 있는 정보를 담는가? (장식용이면 제거)
- **추론한 독자 수준에서 모를 만한 용어·개념이 보조 레이어로 보강됐는가?** (특수 도메인·고급 기술 용어가 풀이 없이 본문에만 등장하지 않는가) — 반대로, 전문가 대상인데 기초까지 과잉 설명하지 않았는가?
- **mermaid 소스에 raw `<` `>` 가 없는가?** (`&lt;` `&gt;` 이스케이프 — components.md §18 규칙. `<<interface>>`, `x < 10`, `List<T>`, `<br/>` 전부 해당). 확인: `grep -n '<' 구간을 눈으로` 또는 `.mermaid` 블록만 추출해 검사
- 남은 `{{` 확인: `grep -c '{{' 출력파일` 이 0인가?
- **브라우저 렌더 스모크 테스트 (다이어그램 있으면 필수)**: `open` 으로 열어 ① 다이어그램이 에러 박스 없이 렌더되는지 ② DevTools 콘솔에 에러 없는지 ③ 테마 토글 1회 눌러 다이어그램이 살아있는지 확인. Playwright 가 있으면 스크린샷 자동화 가능
- 인쇄 미리보기 (`Ctrl+P`) 에서 페이지 깨짐이 없는가?

### 6단계 — 출력

`~/.claude\reports\YYYY-MM-DD-{type}-{slug}.html` 로 저장. slug 는 케밥 케이스 영문(필요시 숫자 포함). 한글 슬러그 금지 (파일 시스템 호환성).

저장 후 사용자에게 파일 경로를 알리고, `open` 명령으로 브라우저에서 열 수 있음을 안내. (스크립트가 있으면 `scripts/open_report.sh` 안내)

## 참조 문서 로딩 가이드

토큰 절약을 위해 필요한 것만 읽는다. **단, 보고서 작성을 시작하기 전에 `references/design-system.md` 의 §0(디자인 원칙)·§12(토큰 cheat sheet) 만큼은 반드시 훑는다** — 토큰 이름·자동 색 코딩 금지 같은 상위 규칙을 모르고 시작하면 결과물이 깨진다.

| 상황 | 읽을 파일 |
|------|----------|
| **모든 보고서 시작 전 (필수)** | `references/design-system.md` §0·§12 |
| 타입 판단·골격 섹션 | `references/report-types.md` |
| 컴포넌트 클래스·HTML 스니펫 | `references/components.md` |
| 토큰 전체·시멘틱·다크 모드 상세 | `references/design-system.md` 전체 |
| 베이스 CSS 전체 보기 | `references/base-css.md` |
| 토큰·컴포넌트 시각 카탈로그 | `examples/_design-catalog.html` (브라우저로 열어 시각 확인) |

대부분의 보고서는 `design-system.md` §0·§12 + `report-types.md` + `components.md` 세 파일이면 충분.

## 핵심 원칙

### 1) 콘텐츠가 부족하면 보고서를 만들지 마라

골격을 채울 만한 정보가 없으면, 정보 수집부터 한다. 빈 칸을 "TBD" 로 채운 보고서는 마크다운보다 못하다. 사용자가 작업 컨텍스트를 충분히 주지 않은 경우, 골격을 먼저 보여주고 빠진 부분에 대해 질문 한 차례 받는 것이 낫다.

**사용자가 정보 보충을 거부하거나 "그냥 만들어" 라고 할 때 (fallback):**

1. **최소 골격 모드**: TL;DR + 접근 1안 + 미해결 질문 섹션만 채운다. 나머지 슬롯은 `<!-- TBD: <무엇이 빠졌는지> -->` HTML 주석으로 명시 (사용자가 나중에 보충 가능)
2. **확인 필요 항목 섹션**: 보고서 끝(footer 직전) 에 `.callout.warn` 으로 "확인 필요 항목" 섹션을 자동 추가. 누락된 결정 사항·근거를 불릿으로 열거
3. **한 차례 더 확인**: "이 상태로 출력해도 되는가? 핵심 옵션 비교 없이는 가치가 낮을 수 있다" 라고 한 번 더 묻고, 그래도 진행하면 파일 저장 후 사용자에게 "TBD 항목 N개 남음" 명시 보고

옵션 1개로 진행하는 Task Plan·Tech Investigation 처럼 원칙(아래 3번) 과 충돌하는 경우, 충돌 사실을 명시한 뒤 사용자 의사를 한 번 더 확인한다.

### 2) AS-IS / TO-BE 의 격차를 명시하라

Analysis·Tech Investigation·System Design 모두 **"무엇이 바뀌어 무엇이 해결되는지"** 를 1:1 매핑해야 한다. 단순 비교가 아니라 **격차(Gap)** 가 보여야 한다. `.compare` 컴포넌트가 이를 시각적으로 강조하니 적극 활용.

### 3) 옵션이 1개면 보고서 가치가 낮다 (결정 문서 한정)

특히 Tech Investigation·Task Plan 에서. 옵션 1개 = 결정 아닌 통보. 최소 2~3 옵션을 비교하고 선택 근거를 적는다. 옵션이 정말 1개뿐이라면 "다른 옵션을 왜 배제했는지" 명시.

**지식 문서 3종(explain·method·guide)에는 적용하지 않는다** — 이해시키고 따라 하게 하는 문서에 옵션 비교를 강요하면 문서가 산으로 간다. 단 Methodology 의 변형(variant) 비교는 이 원칙의 해당 타입 버전이다.

### 4) 리스크·미해결 질문은 필수 (타입별 등가물로)

장밋빛 보고서는 신뢰를 잃는다. 모든 타입에 **리스크 또는 그 등가물 섹션을 포함**한다.

- Analysis → `.risk-grid` (3×3 영향×확률 매트릭스)
- System Design → Open Questions (`<details class="qa">`) 최소 1개
- Incident Postmortem → 5 Whys 또는 기여 요인
- Explainer → "흔한 오해" + "한계" 섹션 (이 둘이 없으면 홍보 자료)
- Methodology → 경계 조건(수식이 깨지는 입력) + 결정 필요 사항
- Guide → 트러블슈팅 + 되돌리기 (복구 불가 단계 명시)
- Audit → "점검하지 않은 것" 명시 (검사 안 함 ≠ 이상 없음)
- Results → 해석·한계 (과최적화·표본 편향·미반영 비용 자기 지적)

### 5) Blameless 원칙 (Incident 한정)

장애 회고에서 **사람 이름·역할 비판 금지**. "X가 잘못된 명령을 실행했다" → "프로덕션 명령에 dry-run 단계가 없었다". 시스템·프로세스 관점으로만 기술.

### 6) 독자 이해도에 보고서를 맞춰라

보고서의 가치는 **독자가 이해하는 만큼**이다. 작성자에게 자명한 용어가 독자에겐 벽일 수 있다. 1.5단계에서 독자 수준을 추론하고, 모를 여지가 있는 용어·개념은 보조 레이어(term/primer/glossary)로 보강한다. **단 "전부 풀어쓰기"는 금지** — 그건 전문가 독자에게 장황·유치하다. 항목별로 선별하고, 깊이는 본문이 아니라 접힌 레이어에 담는다. 핵심은 *한 보고서가 전문가와 초보 둘 다에게 좋은 보고서가 되게* 하는 것.

### 7) 한글 가독성을 해치는 패턴 금지

- 한글 본문에 italic 사용 금지 (서체가 깨짐)
- 본문 글자 13px 미만 금지
- 다크 모드 배경에 순수 검정 `#000` 금지 (눈부심)
- 임의 색상 사용 금지 — `design-system.md` 의 토큰만 사용

## 단계별 복잡도 가이드

작업 양에 따라 처리 방식 분기:

| 복잡도 | 기준 | 처리 |
|--------|------|------|
| 간단 | 단일 타입, 정보 충분, 다이어그램 1개 이하 | 바로 작성, 사용자 확인 없이 출력 |
| 중간 | 정보 일부 부족 또는 다이어그램 2개 이상 | 골격 보여주고 빈 부분만 질문 |
| 복잡 | 타입 결정 모호 또는 여러 보고서 동시 | 타입 후보 제시·합의 후 진행 |

## 예시 — 빠른 입출력 매핑

각 타입이 실제로 어떻게 채워지는지 짧은 walkthrough.

### 예시 1. Analysis (큰그림)

**입력**: "결제 모듈을 PG2에서 PG3로 옮기는 작업 큰그림 좀 그려봐"

**판단**: "큰그림" → Analysis (`analysis`)
**파일명**: `2026-05-11-analysis-payment-pg-migration.html`
**채울 슬롯**:
- TL;DR: "PG2 → PG3 전환을 4주에 걸쳐 단계 적용"
- AS-IS/TO-BE: 현재 PG2 흐름 vs 목표 PG3 흐름 (`.compare`)
- KPI 3개: 월 결제 건수·다운타임 허용치·롤백 윈도우 (`.stat`)
- 아키텍처: Mermaid `flowchart LR` 1개
- 전환 단계 4개 (`.steps`) + 리스크 매트릭스 (`.risk-grid`) + Open Questions

### 예시 2. Incident Postmortem (장애 회고)

**입력**: "어제 02:00 결제 API 5분 다운 — postmortem 작성해줘"

**판단**: "postmortem" → Incident (`incident`) · Blameless 원칙 적용
**파일명**: `2026-05-11-incident-payment-api-down.html` (또는 INC 번호 포함)
**채울 슬롯**:
- kicker: `INC-2026-Q2-001` (번호가 있으면)
- TL;DR: "2026-05-10 02:00 ~ 02:05, 결제 API 5분 다운. 원인: DB 커넥션 풀 고갈. 임시 완화: 인스턴스 재시작"
- 심각도·영향: 다운타임 5분·영향 사용자 ~N명·데이터 손실 0 (`.stat` × 3)
- 타임라인: 분 단위 시각 (`.timeline`, 24h 표기)
- 근본 원인: `.callout.danger` 한 줄 + 상세 단락
- 무엇이 잘됐나/못됐나: `.callout.success` / `.callout.warn`
- 액션 아이템: 단/중/장기 분류 표 + 재발 방지 체크리스트
- ⚠️ 사람 이름·역할 비판 금지 (Blameless)

### 예시 3. Tech Investigation (옵션 비교)

**입력**: "Redis vs Memcached 중 뭐 쓸지 검토해줘"

**판단**: "뭐 쓸지" → Tech Investigation (`invest`)
**파일명**: `2026-05-11-invest-cache-redis-vs-memcached.html`
**채울 슬롯**:
- TL;DR: "**Redis** 채택. 이유: 영속화 + 클러스터링 + 자료구조 다양"
- 평가 기준 표: 성능(×3)·운영 부담(×2)·학습 곡선(×1)
- 후보 옵션 카드 3개 (`.grid.cols-3` — Redis/Memcached/KeyDB 등)
- 결정 매트릭스: 점수 × 가중치 합계 + `.winner` 강조
- 채택안 트레이드오프: `.callout.warn` (메모리 비용 증가 등)

### 예시 4. Retrospective (회고)

**입력**: "이번 스프린트 회고 정리"

**판단**: "회고" → Retrospective (`retro`) · 다이어그램 거의 불필요
**파일명**: `2026-05-11-retro-sprint-2026-Q2-W3.html`
**채울 슬롯**:
- 기간·범위 (`.callout.note`) + 한 일 (`.timeline` 또는 `<ul>`)
- 메트릭 3개 (`.stat` — 배포 횟수·인시던트·코드 변경량 등)
- Keep / Problem / Try 3단 (`.callout.success` / `.callout.warn` / `.steps`)
- 액션 아이템 표 (담당·기한·상태)
- 💡 Mermaid 거의 안 씀 → `base.html` 의 mermaid 스크립트 두 줄 삭제 가능

### 예시 5. Methodology (산식 명세)

**입력**: "섹터별 상대강도 지수 산출 방법론 문서로 정리해줘"

**판단**: "산출 방법론" → Methodology (`method`) · 독자가 금융 비전문가면 숫자 예시 비중 ↑
**파일명**: `2026-07-15-method-sector-relative-strength.html`
**채울 슬롯**:
- TL;DR: "섹터 내 종목을 모멘텀 점수로 가중해 섹터 지수를 만드는 산식 정의. 핵심: 리밸런싱 체인 방식"
- 전체 구조: 입력(수정주가) → 점수 → 가중 → 지수 파이프라인 `flowchart LR`
- 기호 표: P_i(t), r_기간, w_i, N 고정
- 계산 단계마다: 말 정의 → `.formula` → `.example` 숫자 예시 → 경계 조건 `.callout.warn` 반복
- 변형 비교: 동일가중/시총가중/모멘텀가중 × 세부 변형 → `.decision` 표 + `.winner`
- 결정 필요 사항: 리밸런싱 주기, K 값 등 `<details class="qa">`

### 예시 6. Explainer (개념 해설)

**입력**: "SQLAlchemy dirty checking 이 뭔지 정리해줘"

**판단**: "뭔지 정리" → Explainer (`explain`)
**파일명**: `2026-07-15-explain-sqlalchemy-dirty-checking.html`
**채울 슬롯**:
- TL;DR: "왜 save() 없이 commit 만으로 UPDATE 가 나가는가 — 세션이 객체 변경을 추적하기 때문"
- 왜 존재하나: 수동 save 의 고통 + 비유 (`.callout.note`, 비유의 성립 경계 명시)
- 멘탈 모델: Session·IdentityMap·UnitOfWork 카드 3개 + mermaid 1개
- 동작 순서: `.steps` + 실제 코드 시나리오 `.example`
- 흔한 오해: `.compare` (오해 → 실제)
- 치트시트 표 + 용어집

> **공통 팁**: 어떤 타입이든 TL;DR 은 **반드시 1~2문장**으로. 길어지면 결론을 못 잡은 것. 처음 만들 때는 TL;DR 부터 채우고 그 다음 골격 순회하면 빠르다.

## 무엇을 하지 않는가

- **README·일반 문서 생성**: 본 스킬은 보고서 전용. 일반 문서는 마크다운으로.
- **PR 리뷰 결과 문서**: `/pr-review` 스킬 사용.
- **장표·발표 자료**: `/pptx`.
- **임의 디자인 변경**: CSS 토큰을 바꾸지 말 것. 새 컴포넌트 추가는 정말 필요할 때만.
- **시크릿 노출**: 보고서에 API 키·DB 접속 정보·내부 URL 포함 금지.

## 자주 막히는 곳 (Troubleshooting)

| 증상 | 원인 | 대처 |
|------|------|------|
| 다이어그램에 "Syntax error in text" 폭탄 박스 | mermaid 소스 안 raw `<` `>` 가 HTML 파싱에 먹힘 (`<<interface>>`, `x < 10` 등) | `&lt;` `&gt;` 로 이스케이프 (components.md §18 규칙 1) |
| 테마 토글하면 다이어그램이 전부 깨짐 | 구버전 base.html 산출물 (렌더 후 SVG 텍스트를 소스로 오인하는 버그) | 최신 `templates/base.html` 로 재생성. 신규 base 는 렌더 전 소스를 `data-src` 에 보존 |
| `<details>` 안 다이어그램이 펼쳐도 안 보이거나 찌그러짐 | 접힌 상태(크기 0)에서 렌더됨 | 최신 base 는 펼칠 때 자동 재렌더. 가능하면 다이어그램은 본문에 배치 |
| 다크 모드로 인쇄하면 색이 뒤엉킴 | 다크 토큰이 흰 종이 배경과 충돌 | 최신 base 는 인쇄 시 라이트 토큰 강제. 구버전 산출물은 라이트로 토글 후 인쇄 |
| 브라우저에서 다이어그램이 안 보임 | Mermaid CDN 차단 또는 코드 문법 오류 | DevTools Console 확인. CDN 차단이면 오프라인 환경에서 mermaid.min.js 다운로드 후 인라인 |
| 다크 모드로 토글하면 색 깨짐 | 임의 색상 인라인 사용 (`style="color: #ff0000"` 등) | 인라인 색상 제거. `design-system.md` 의 CSS 변수만 사용 |
| 인쇄 시 페이지 중간에 표 잘림 | `page-break-inside: avoid` 클래스 누락 | 큰 표·이미지를 `<div class="avoid-break">` 로 감싸기 |
| 한글이 흐릿하게 보임 | Pretendard CDN 로드 실패 | 네트워크 점검 또는 시스템 폰트 폴백 확인 |
| TOC 가 자동 생성 안 됨 | 본문 섹션에 `id` 또는 `h2` 누락 | 각 `<section>` 에 `id="..."` + 내부 `<h2>` 페어 유지 |
| 컴포넌트가 적용 안 됨 | 클래스명 오타 (`.callout warn` vs `.callout.warn`) | `components.md` 의 정확한 클래스 복사 |

## 파일 구조

```
html-report/
├── SKILL.md                              (이 파일)
├── templates/
│   ├── base.html                         (CSS·JS 다 포함된 베이스)
│   ├── task-plan.html                    (1. 작업 계획서 골격)
│   ├── analysis.html                     (2. 분석 보고서 골격)
│   ├── tech-investigation.html           (3. 기술 검토 골격)
│   ├── system-design.html                (4. 시스템 설계 골격)
│   ├── retrospective.html                (5. 회고 골격)
│   ├── incident-postmortem.html          (6. 장애 회고 골격)
│   ├── explainer.html                    (7. 개념·기술 해설 골격)
│   ├── methodology.html                  (8. 방법론·산식 명세 골격)
│   ├── guide.html                        (9. 절차 실행 가이드 골격)
│   ├── audit.html                        (10. 감사·점검 골격)
│   └── results.html                      (11. 실험·측정 결과 골격)
├── references/
│   ├── report-types.md                   (타입별 골격 상세)
│   ├── components.md                     (컴포넌트 카탈로그)
│   ├── design-system.md                  (디자인 토큰)
│   └── base-css.md                       (베이스 CSS 풀)
├── examples/
│   └── _design-catalog.html              (토큰·컴포넌트 시각 카탈로그)
└── scripts/
    └── open_report.sh                    (macOS 브라우저 열기 헬퍼)
```
