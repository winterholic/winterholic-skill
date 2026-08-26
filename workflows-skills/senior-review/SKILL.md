---
name: senior-review
description: "빅테크 시니어급 심층 코드 리뷰. 다중 에이전트 오케스트레이션으로 (의도·아키텍처 매핑 → 차원별 독립 병렬 리뷰 → loop-until-dry 완전성 스윕 → 발견마다 회의적 검증 → 보정)을 거쳐 가독성 높은 단일 HTML 리뷰 문서를 만든다. **리뷰 시나리오 4종을 구분해 출력 프레임을 맞춘다**: peer-pr(타인 PR 심사)·pre-submit(PR 올리기 전 자기 점검)·wip(개발 중간 방향 점검)·audit(기존 코드 분석·감사, diff 없음). 사용자가 'senior-review', '시니어급 리뷰', '시니어 리뷰', '꼼꼼하게 리뷰', '제대로 리뷰', '심층 리뷰', '깊게 리뷰', 'deep review', '제대로 봐줘', '대충 말고 제대로 리뷰', '올리기 전에 제대로 점검', '이 코드/프로젝트 깊게 분석'을 언급하거나, 가벼운 /pr-review·/self-review로는 부족하다고 느낄 때 트리거. 단일 패스의 한계(일관성 부족·맥락맹 상태의 사소한 지적 남발·표면적 패턴매칭·의도 미파악)를 구조적으로 해결한다. 가벼운 리뷰는 /pr-review(타인 PR)·/self-review(PR 전 자기점검)를, 보안 전용은 /security-review를 쓴다."
model: sonnet
effort: high
---

# Senior Review (시니어급 심층 코드 리뷰)

## 이 스킬이 존재하는 이유 — 단일 패스의 구조적 한계

`/pr-review`·`/self-review`는 잘 만들어진 **단일 컨텍스트 1회 패스** 리뷰다. 그런데 한 패스는 어텐션이 분산돼 **커버리지가 확률적**이고(같은 코드를 여러 번 돌리면 매번 다른 걸 찾는 이유), 같은 컨텍스트 안에서 자기가 방금 쓴 지적을 스스로 죽이는 자기검열이 약하다(사소한 지적이 계속 남는 이유). 이건 프롬프트를 더 잘 써서 고칠 수 있는 게 아니라 **구조로** 고쳐야 한다.

실증 근거(`references/methodology.md`): 단일 리뷰어의 결함 검출률은 50% 미만이고(Fagan), 다중 독립 리뷰어는 60~90%, 관점 분리 팀은 체크리스트 팀보다 고유 결함을 41% 더 잡는다. 다중 에이전트는 리뷰 일관성을 85.5% 끌어올린다. **그래서 이 스킬은 리뷰를 여러 독립 에이전트로 fan-out하고, 발견을 별도 회의적 검증자가 반증하게 한다.**

이 스킬은 호출되면 **번들된 워크플로우(`workflow.js`)를 다중 에이전트 오케스트레이션으로 실행**하고, 그 결과(검증·보정된 구조화 리뷰)를 받아 **`pr-review`와 동일한 HTML 디자인 시스템**으로 렌더링한다.

> **모델 고정**: 리뷰 에이전트는 전부 **Sonnet**으로 돈다(`workflow.js`의 모든 `agent({model:'sonnet'})`). 리뷰의 힘은 단일 에이전트의 추론력이 아니라 **다중 독립 패스의 커버리지**에서 나오므로, Opus 단일 패스보다 Sonnet 다중 패스가 비용 대비 우월하다. 이 스킬·렌더링도 `model: sonnet`.

---

## 절대 규칙

- **읽기 전용**: `gh pr view/diff`, `git log/show/diff`, 파일 `Read`, 확인용 `grep`/`ast`만. **commit/push/파일수정 금지** (리뷰 산출물 HTML 작성 제외).
- **저장 위치**: `~/.claude\reports\senior-review\` (senior-review 산출물 전용 폴더)
- **출력**: **단일 자기완결 HTML**. 인라인 CSS/JS, 외부 의존성 0.
- **파일명**: `SR-{N}-{슬러그}.html`. **`N`은 PR 번호가 아니라 senior-review 산출물의 1부터 매기는 일련번호** — 저장 폴더 내 기존 `SR-{숫자}-…` 중 최대 번호 + 1(없으면 1). 리뷰 대상이 PR이든 내 브랜치든 프로젝트 분석이든 동일. **`슬러그`에 대상 식별 정보**를 담는다: PR이면 `pr{번호}-{브랜치슬러그}`(예: `pr83-admin-telegram-ui`), 브랜치 diff면 브랜치명 슬러그, 경로/프로젝트 분석이면 대상 설명 슬러그(예: `frontend-arch-audit`). (`SR-` = senior-review. pr-review의 `PR-…` 산출물을 덮어쓰지 않게 접두사로 구분.)
- **템플릿**: `~/.claude\skills\senior-review\template.html`을 `cp`로 복사 후 채운다. 디자인 시스템(컬러·뱃지·카드·심각도 클래스)은 **절대 변형 금지**. (이 템플릿은 pr-review와 동일하다.)
- **같은 대상 재리뷰 시 append**: 저장 폴더에 **같은 슬러그**의 `SR-*-{슬러그}.html`가 이미 있으면 새 N으로 새 파일을 만들지 말고 그 기존 파일에 라운드를 append한다 — `<!-- ROUND-INSERT-MARKER -->` 바로 위에 새 라운드 삽입. 마커·종결 섹션·닫는 태그 보존. (다른 대상이면 새 N으로 새 파일.)
- **위치 표기**: 항상 `<프로젝트루트기준경로>:<라인>` 풀 경로 (예: `backend/app/api/users.py:478`). 단축 경로 금지.

---

## 실행 흐름

### 1단계 — 시나리오·대상 확정 + 원시 맥락 수집 (메인 루프가 직접)

**① 시나리오 판별** — "무엇을"과 직교하는 축: **이 리뷰가 누구를 위한 어떤 상황인가**. 출력의 어휘·verdict·헤더·체크리스트가 전부 여기 따라간다. 잘못 고르면 자체점검에 "머지 가능" 판정이 나가는 사고가 난다.

| scenario | 상황 | 발화·정황 신호 | verdict |
|---|---|---|---|
| `peer-pr` | 타인이 올린 PR 심사 | PR 번호/URL 지정, "PR 리뷰해줘" | approve / approve-with-nits / comment / request-changes |
| `pre-submit` | **PR 올리기 전 본인 작업 자기 점검** | "올리기 전에", "자체점검", "내 코드/브랜치 봐줘", 대상이 본인 작업 브랜치(커밋 author=사용자) | ready / ready-with-notes / needs-work |
| `wip` | 개발 중간 방향 점검 (미완성 전제) | "지금 방향 맞나", "중간 점검", "아직 작업 중인데", uncommitted 변경 다수 | on-track / adjust-course / rethink |
| `audit` | 기존 코드 분석·감사 (diff 없음) | "이 프로젝트/모듈 분석해줘", "코드 상태 봐줘", 경로 지정 + 변경 없음 | healthy / healthy-with-debt / needs-attention / at-risk |

기본값: PR 번호 지정 → `peer-pr` (단, 본인이 방금 올린 PR을 "올리고 나서 점검" 맥락이면 `pre-submit` 프레임이 맞을 수 있다 — 발화 우선). 본인 브랜치 diff → `pre-submit`. 경로만 지정 → `audit`. 신호가 충돌하거나 불명확하면 **한 번만** 묻는다. 결정한 값을 `args.scenario`로 전달.

**② 대상 판별** — 워크플로우에 넘길 **사실(facts)**을 모은다:

- **PR**: 사용자가 PR 번호/URL 지정. `gh auth status` 확인(미인증이면 `gh auth login` 안내). 비-GitHub 호스트면 대응 CLI(`glab` 등) 또는 웹 URL 수동 수집으로 폴백.
- **브랜치 diff**: "현재 브랜치 리뷰" 류 → `git diff <base>...HEAD`. base 불명확하면 한 번 묻는다. uncommitted 포함이면(`wip` 흔함) `git diff <base>` + `git status`로 작업트리 상태까지.
- **경로 범위** (`audit` 전형): git 저장소가 아니거나 특정 디렉토리/모듈 지정 시 그 범위. **diff가 없으므로** `diffText` 생략, 범위 내 핵심 파일들을 `files[]`에 `cat -n`으로 담는다(테스트·생성물 제외, 소스 위주). `additions/deletions`도 생략 — 워크플로우가 `files[]` 총 라인수로 모드를 추정한다. 범위가 아주 크면 `mode: "deep"`을 명시하고 핵심 파일만 인라인 + 나머지는 `truncatedFiles`로.

**질의 불응·거부 시 fallback** (질문은 한 번 — 답이 없거나 "알아서 해"면 멈추지 말고 아래로 진행):

- **base 무응답** → `origin/main`(없으면 `origin/master`, 그것도 없으면 기본 브랜치 `git remote show origin`) 가정하고, 보고서 `#background`에 "base는 origin/main으로 추정" 한 줄 명시.
- **gh 인증 거부/불가** → PR 메타(코멘트·리뷰·linked issue) 없이 로컬 diff만으로 진행. `prBody` 등은 생략하고 designValidity에 "PR 맥락 미수집 — 코드만으로 평가" 표기.
- **시나리오 확인 무응답** → 1단계 ①의 기본값 규칙으로 진행하고 보고서 헤더 kicker 옆에 "(시나리오 추정)" 표기.
- **사용자가 발견 판정에 이의 제기** → 해당 발견의 검증 근거(evidence·verdicts)를 제시하고, 사용자 반박이 코드로 확인되면(Read/grep) append 라운드에서 정정 카드를 추가한다 — 원 카드는 삭제하지 않고 `author-reply` 인용으로 경위를 보존. 코드로 확인 불가면 "검증 못함: 사유"를 밝히고 양쪽 관점을 카드에 병기.
- **openQuestion 답변 수신 시** → 그 답을 코드로 재확인(Read/grep)한 뒤: 답이 결함을 확증하면 append 라운드에서 해당 question을 **`issue`/`suggestion`으로 승격**(검증된 tier로 카드 작성), 무해함이 확인되면 **resolved로 닫고** 그 근거를 한 줄 남긴다(드롭이 아니라 경위 보존). 답이 모호해 코드로 가릴 수 없으면 question 그대로 두고 "추가 확인 필요"로 표기.

PR이면 아래를 빠짐없이 수집(`gh`):

```bash
gh pr view <N> --json title,body,author,headRefName,baseRefName,labels,state,additions,deletions,changedFiles,statusCheckRollup,reviewDecision,closingIssuesReferences,commits,files
gh api repos/{owner}/{repo}/pulls/<N>/comments --paginate
gh api repos/{owner}/{repo}/pulls/<N>/reviews --paginate
gh api repos/{owner}/{repo}/issues/<N>/comments --paginate
git fetch origin <N>:pr/<N>   # 로컬에서 코드 읽기용

# ── 코드를 여기서 한 번만 수집한다 (토큰 절감의 핵심) ──
git -C <root> diff <base>..<head>                         # → diffText (전체 통합 diff)
for f in <changedFiles>; do git -C <root> show <head>:"$f" | cat -n; done   # → files[].content (라인번호 포함 전체 내용)
```

> **핵심 — 코드는 메인 루프가 한 번만 수집해 인라인으로 넘긴다.** 이전 버전은 N개 에이전트가 각자 `git`/`Read`/`grep`로 코드를 탐색해서, 매 툴 호출마다 컨텍스트를 재읽어(cache_read) 토큰이 **에이전트수 × 탐색턴수**로 폭증했다(실측: 87 에이전트·1,314턴·cache_read 35M). 이제 diff와 변경 파일 전체 내용을 args에 담아 모든 에이전트가 **재탐색 없이** 본다.

수집한 사실로 **`args` 객체**를 구성한다(워크플로우가 이걸 받는다):

```json
{
  "kind": "pr",
  "scenario": "peer-pr | pre-submit | wip | audit  (①에서 판별 — 필수)",
  "title": "...", "number": 37, "repo": "owner/repo", "prUrl": "...",
  "base": "<base SHA>", "head": "<head SHA>", "headSha": "<SHA>",
  "changedFiles": ["backend/...", "frontend/..."],
  "additions": 235, "deletions": 84,                    // ← 규모 분류(lite/standard/deep)용 — 필수
  "diffText": "<git diff 전체 출력>",                     // ← 인라인 코드 (필수)
  "files": [ {"path":"backend/...", "content":"<cat -n 전체 내용>"} ],  // ← 변경 파일 전체 (필수)
  "truncatedFiles": ["아주 큰 파일은 변경 영역만 담고 여기 명시"],  // 선택
  "prBody": "...", "commits": [{"sha":"...","message":"..."}],
  "existingComments": [{"path":"...","line":0,"body":"...","author":"..."}],
  "linkedIssue": "...(있으면)",
  "projectRoot": "<프로젝트 루트>/repo",
  "mode": "lite | standard | deep (선택 — 미지정 시 diff 크기로 자동)"
}
```

> **규모 자동 스케일**: `additions+deletions ≤ 40 & 파일 ≤ 2`면 `lite`(렌즈 3·스윕 0·검증 1 — **trivial·문서·설정 전용**), `≤ 600 & ≤ 15`면 `standard`(렌즈 5·스윕 1·**검증 2**), 그 이상이면 `deep`(렌즈 6·스윕 2·검증 2). **lite는 격하됨** — 정확성 블로커를 놓칠 만큼 얕아서, 의미 있는 코드 변경은 전부 standard(정확성 리뷰의 바닥)로 간다. `mode`로 강제 가능.
> **변동성 완화**: correctness 렌즈와 sweep critic에 **고위험 결함 분류표**(빈 결과 vs 에러 혼동 / 실패 경로 부작용 / 재시작 원자성 / 경계 가정 어긋남 / 무한 증식 / 동시성)를 명시해, 매 실행이 같은 고위험 클래스를 일관되게 훑도록 한다(실행별로 다른 블로커를 잡던 문제 완화).
> **거대 PR**: 변경 파일이 너무 커서 전부 인라인이 부담이면, 그 파일은 **변경 영역(±50줄)만** content에 담고 `truncatedFiles`에 경로를 넣는다 — 에이전트가 필요 시 그 파일만 추가로 Read한다.

### 2단계 — 다중 에이전트 워크플로우 실행

번들된 스크립트를 `Workflow` 도구로 실행한다. **1단계에서 만든 `args`를 그대로 JSON 값으로 전달**(문자열로 감싸지 말 것):

```
Workflow({
  scriptPath: "~/.claude\skills\senior-review\workflow.js",
  args: { ...1단계에서 만든 객체... }
})
```

워크플로우가 내부적으로 수행하는 것(메인 루프는 결과만 받음. 에이전트는 전부 인라인 코드를 보고 **재탐색 없음**):

1. **Context** — 공유 의도·아키텍처·컨벤션 맵 1개(front-loaded 제약). epicenter 파일 선정.
2. **Review** — 독립 lens 병렬(서로의 발견을 못 봄). **개수는 모드별**: lite 3(correctness+design / security / intent+convention+roi) · standard 5 · deep 6.
3. **Sweep** — **standard/deep만.** 완전성 비평가가 미검토 영역 지목 → 타깃 finder. 연속 dry까지(standard 최대 1·deep 최대 2라운드). lite는 생략.
4. **Verify** — **배치 검증**(발견마다 에이전트를 띄우지 않는다). 검증자가 **전체 발견 리스트를 한 번에** 받아 vid별로 판정: lite 1명, **standard·deep 2명**(검증자 2명이라야 심각도 과대평가 — 본질적 at-least-once를 critical로 올리는 류 — 를 걸러낸다). **컷 기준은 "사소함"이 아니라 "맥락맹"** — 추적된 맥락·의도에 근거했나(zoom-out), 도달 가능한가, 의도된 무해 트레이드오프인가. 맥락 근거면 사소해도 살림(non-blocking nit), 맥락맹이면 크기 무관 컷. **tier 차등**: T3는 1표 컷, T1/T2는 검증자 2명일 때 만장일치라야 컷(미묘한 버그 보호).
5. **Calibrate** — 모더레이터가 의미 중복 병합, design-blocker·epicenter 우선 정렬, praise 1개 이상, design-validity(ROI) 축 평가. **크기로 거르지 않는다** — linter가 잡을 순수 기계적 스타일·반복 패턴(대표 1건+카운트)만 억제, 맥락 근거 사소 발견은 nitpick/non-blocking으로 **모두 노출**.

반환값:
```
{ target, scenario, context, review: { verdict, summary, blockingCount, nonBlockingCount, designValidity, findings[], praise[], openQuestions[], suppressed[], uiChange }, stats, integrity }
```

> **안정성 가드(조용한 실패 차단 — 품질 비용 0)**: ① 코드 소스(`bundlePath`/`diffText`/`files`)나 사이징 신호가 없으면 시작 시 **시끄럽게 경고**(빈손 리뷰·모드 오판정 방지). ② lane이 null 반환(차원 증발)하면 로그로 표면화하고 **correctness lane은 1회 재시도**. ③ **심각도는 JS가 확정한다(모더레이터가 못 건드림)** — 검증자 2명이 정한 tier→severityClass/blocking을 JS가 계산하고, 모더레이터는 카드마다 `sourceVids`(병합한 원본 발견 id)만 지정한다. 최종 단계에서 JS가 각 카드 severity를 source의 검증된 tier에서 **재계산해 덮어쓰고**, 모더레이터가 누락한 survivor는 **자동 복구**(recovered-*)한다. 즉 모더레이터가 블로커를 강등·드롭해도 구조적으로 무효화된다(deep 실측에서 모더레이터가 T1을 medium으로 강등한 사고를 이 방식으로 fix — prompt 지시만으론 안 지켜졌음, 단위테스트로 검증). ④ **deep 모드는 correctness lane 2중 독립 실행 후 union**(블로커 recall 안정화, +1 에이전트). `integrity{blockerSurvivors, blockingOut, recoveredBlockers, severityAuthority}`로 노출 — `recoveredBlockers>0`이면 모더레이터가 빠뜨린 걸 JS가 살린 것.

> 워크플로우가 **사고(리뷰)**를, 메인 루프가 **렌더링(HTML)**을 맡는다. 분리하는 이유: 1500줄 템플릿을 한 에이전트가 한 방에 채우면 깨지기 쉽다. 검증된 점진 작성은 메인 루프가 한다.

### 3단계 — HTML 렌더링 (메인 루프가 점진 작성)

워크플로우가 돌려준 `review` 객체를 `template.html`에 채운다.

**시나리오별 표면 어휘** — 디자인 시스템(클래스·구조·섹션 ID·번호)은 그대로 두고 **문구만** 아래 표로 치환한다. 템플릿의 `{KICKER}`/`{TARGET_TAG}`/`{BG_TITLE}`/`{INTENT_DOC_TITLE}`/`{ACTION_REQUIRED}`/`{ACTION_RECOMMENDED}`/`{ACTION_PLAN_TITLE}`/`{DOC_TITLE}` placeholder가 이 표를 받는다:

| 위치 | peer-pr | pre-submit | wip | audit |
|---|---|---|---|---|
| `{KICKER}` | `PEER PR REVIEW` | `PRE-SUBMIT CHECK` | `WIP DIRECTION CHECK` | `CODE AUDIT` |
| `{TARGET_TAG}` | `PR #N` | 브랜치명 | `브랜치명 (WIP)` | 대상 경로/모듈명 |
| 헤더 meta | author·diffstat·head→base·CI·GitHub 링크 | diffstat·base 브랜치 (**CI 칩·GitHub 링크 span 삭제**) | pre-submit과 동일 + "uncommitted 포함" 표기 | 파일 수·총 라인 수 (**diffstat·CI·링크 삭제**) |
| `{BG_TITLE}` | PR 배경 | 변경 배경 | 작업 배경 | 분석 대상 개요 |
| `{INTENT_DOC_TITLE}` | PR description 평가 | 의도 가시성 평가 | 의도 가시성 평가 | 문서·README 현행화 평가 |
| `{ACTION_REQUIRED}` / `{ACTION_RECOMMENDED}` | 이번 PR 수정 필수 / 권장 | 올리기 전 수정 필수 / 권장 | 지금 수정 필요 / 마무리 때 반영 | 우선 개선 / 여유 시 개선 |
| `{ACTION_PLAN_TITLE}` | 리뷰 진행 순서 추천 | **PR 올리기 전 체크리스트** (체크박스 형태 권장) | 다음 작업 전 결정 사항 | 개선 우선순위 로드맵 |
| verdict 어휘 | 머지 가능/불가 | 제출 준비 여부 — "머지" 표현 금지 | 방향 유지/수정/재고 | 건강도 — "머지/제출" 표현 금지 |

**시나리오별 구조 적응** (섹션 ID·순서는 유지, 내용 재해석):

- **pre-submit/wip**: 독자는 작성자 본인 — 카드 문체를 "리뷰어가 작성자에게"가 아니라 **"네 코드에서 리뷰어가 이걸 지적할 것"** 톤으로. GitHub 라인 링크는 원격에 브랜치가 있으면 유지, 로컬 전용이면 코드박스 `↗` 링크 삭제.
- **wip**: 미완성 영역(TODO·스텁)은 발견 카드가 아니라 `#background`에 "미완성 전제 범위" 한 줄로 명시.
- **audit**: `#commits` 섹션을 **"검토 범위"**(파일/모듈 표 — SHA 열 대신 경로·라인수)로, `#review`의 commit-block을 **모듈/영역 단위**(`COMMIT 1` 뱃지 → `영역 1`, breadcrumb "커밋 N" → "영역 N")로 재구성. diffstat·GitHub 커밋 링크 삭제.

```bash
DIR=~/.claude\reports\senior-review
mkdir -p "$DIR"
SLUG={슬러그}   # PR이면 pr{번호}-{브랜치슬러그}, 아니면 대상 설명 슬러그

# 같은 슬러그의 기존 산출물 있으면 그 파일에 append (새 N 만들지 않음)
EXISTING=$(ls "$DIR"/SR-*-"$SLUG".html 2>/dev/null | head -1)
if [ -n "$EXISTING" ]; then
  OUT="$EXISTING"   # append 모드 — ROUND-INSERT-MARKER 위에 새 라운드 삽입
else
  # N = 기존 SR-{숫자}- 중 최대 + 1 (없으면 1)
  N=$(( $(ls "$DIR" 2>/dev/null | grep -oE '^SR-[0-9]+' | grep -oE '[0-9]+' | sort -n | tail -1) + 1 ))
  OUT="$DIR/SR-$N-$SLUG.html"
  cp ~/.claude\skills\senior-review\template.html "$OUT"
fi
echo "$OUT"
```

그 다음 placeholder를 채우고 콘텐츠를 **점진적으로**(헤더·요약 → 배경/설계타당성 → 커밋 → 리뷰포인트 한 개씩) Edit로 추가한다. 한 방에 통째 Write 금지(중간에 끊겨도 살아남게).

**구조화 리뷰 → 템플릿 매핑:**

| `review` 필드 | HTML 위치 |
|---|---|
| `summary` + 카운트 | `.summary` (결론 1~3문장 + 심각도 카운트) |
| `context` (problem/architecture/statedIntent) | `#background` 배경 카드 + (큰 변경이면) "이 PR의 맥락" 박스 |
| `designValidity` (axes + conclusion) | `#background` 안 "설계·목적 타당성 평가" 표 + 종합 notice |
| `findings[]` | `#review` 각 항목이 `<details class="review-point {severityClass}">` 카드 1개 |
| `praise[]` | `severity-tag good` 카드 또는 요약의 긍정 항목 (최소 1개 노출) |
| `openQuestions[]` | `severity-tag check` 카드 (누가/언제·무엇/어떻게/기대결과 4요소) |
| `suppressed[]` | `#background` 또는 요약에 "걸러낸 노이즈" 한 줄 (투명성 — 무엇을 안 적었는지 명시) |
| `uiChange: true` | `#frontend-test` 수동 테스트 가이드(체크박스) 작성 |

**각 finding 카드 필수 요소** (pr-review와 동일):
1. `<summary>`: `severity-tag {severityClass}` + `[{label}]` 표기 + 번호·제목 (예: `이슈 1-1. ...` / `제안(non-blocking) ...`)
2. `.breadcrumb`: 커밋 › `file` › `line` + GitHub 라인 직링크
3. `<h4>코드</h4>` + `.codebox`: Mac 헤더 + 라인 gutter + 문제 라인 `.ln.hl` 하이라이트
4. `<h4>문제</h4>`: `problem` (traced evidence). **위반한 원칙(`principle`)을 명시** — "근거: SRP 위반" 식.
5. `<h4>권장 조치 <span class="action-tag {actionTag}">…</span></h4>`: `recommendation` (가능하면 방법 A/B)
6. (선택) `.plain-talk` `plainTalk` / (선택) `.impact` `impact` — 1.5단계 독자 수준 기반 선별. 전문가 독자면 비직관·고영향 항목에만.

**`problem` 작성 품질 기준** — verify.sh는 구조만 검사하므로 내용은 이 대비로 자가 점검:

- ❌ **나쁜 예** (표면 요약 — 추적 없음): `"이 함수는 에러 처리가 없어 위험합니다."`
- ✅ **좋은 예** (traced evidence — 출처→흐름→파괴 지점): `"runner.py:42의 fetch()가 '결과 없음'과 '타임아웃 실패'를 모두 []로 반환한다. 호출자 sync()(:88)는 []를 '데이터 없음'으로 해석해 기존 오프셋을 삭제하므로, 일시 장애가 영구 재수집으로 번진다. (근거: 빈-결과/에러 혼동, fail-safe 원칙 위반)"`

좋은 예의 3요소: **어디서 오는 값이**(출처) → **어떤 경로로**(흐름) → **무엇을 깨뜨리나**(파괴 지점) + 위반 원칙. 이 중 하나라도 못 채우면 `issue`가 아니라 `question`이다.

**심각도 → 클래스** (template 강제): `critical`/`medium`/`minor`/`info`/`good`/`check`. `[심각]`만 `<details open>`.

**Conventional Comments 라벨을 카드에 노출**: 각 카드 summary에 `[issue]`/`[suggestion]`/`[nitpick]`/`[question]`/`[thought]`/`[praise]`/`[FYI]` 중 하나를 표기하고, blocking 여부를 명시(`required`=blocking, `optional`/non-blocking 등). 이게 작성자가 "뭘 꼭 고쳐야 하는지" 즉시 분류하게 해준다.

**문서 구조**(template 강제 순서, ID·번호 변경 금지): `pr-header` → `.summary` → `#toc` → `#background`(배경+설계타당성) → `#commits` → `#review` → `#frontend-test`(UI 시) → `#summary-table` → `#action-plan` → `<!-- ROUND-INSERT-MARKER -->`.

> HTML 컴포넌트(브레드크럼·codebox·plain-talk·impact·author-reply·notice·abbr 등) 상세 사용법과 append(2차/3차 라운드) 전략은 **`~/.claude\skills\pr-review\SKILL.md`의 6·7단계가 그대로 적용된다**(동일 템플릿). 그 규칙을 따른다 — 여기서 중복 기술하지 않는다.
>
> **자기방어 (pr-review 부재 시)**: 위 pr-review 6·7단계를 읽을 수 없으면(파일 이동·삭제) `template.html` 하단의 `<!-- 라운드 골격 · COPY-PASTE TEMPLATE -->` 주석이 **self-contained 정답 구조**다 — 그 골격을 복사해 쓰면 컴포넌트 사용법 없이도 정합한 카드/라운드를 만들 수 있고, `scripts/verify.sh`가 이탈을 FAIL로 잡아준다. (즉 pr-review는 편의 참조이지 단일 실패점이 아니다.)

**HTML 안전성**:
- 코드 본문의 `<`·`>`·`&`는 반드시 `&lt;`·`&gt;`·`&amp;`로 이스케이프.
- **블록 요소(`.codebox`·`.notice`·`table` 등 `div` 계열)를 `<p>` 안에 넣지 않는다** — 브라우저가 `<p>`를 자동 종료시켜 stray `</p>`가 생기고 DOM이 틀어진다(SR-4 실측 2건). 권장 조치에 코드 예시를 붙일 땐 `<p>설명</p>` 닫은 **뒤에** `.codebox`를 형제로 둔다.
- 코드 한 줄이 아주 길어도 줄을 임의로 쪼개지 말 것 — 가로 스크롤은 `.codebox-body`가 처리한다(템플릿의 `.main > .content { min-width: 0 }`이 전제).
- **codebox 본문은 반드시 `<div class="codebox-code">`에 넣는다 — bare `<pre>` 금지**(SR-8 2차 실측: 코드가 안 보임). `.codebox-body`는 `display:flex`에 자체 텍스트색이 없어, 색·줄바꿈·하이라이트(`.codebox-code .ln`, `.codebox-code .ln.hl`)가 전부 `.codebox-code` 셀렉터에 걸려 있다. `<pre>`를 직접 쓰면 본문이 페이지 다크 텍스트색을 상속해 다크 배경에 묻혀 안 보인다. append 라운드의 codebox는 골격(신규 발견 `<details>` 안 코드 블록)을 복사해 채울 것 — 기억으로 재작성 금지.
- **codebox 두 열 형식 엄수**(SR-15 실측: gutter가 깨짐): `.codebox-gutter`에는 **줄번호를 줄바꿈으로 구분한 순수 숫자만** 넣고 `<span>`으로 감싸지 않는다(감싸면 inline이라 번호가 한 줄로 뭉쳐 코드와 어긋난다). `.codebox-code`에는 **코드 한 줄당 `<span class="ln">…</span>` 하나**를, 문제 줄만 `class="ln hl"`로. 두 열의 줄 개수는 정확히 일치해야 한다.

**출력 언어 — 한국어 강제**(SR-15 실측: `#background`가 영어로 나옴): workflow의 에이전트 프롬프트는 영어지만 산출물은 한국어 문서다. `context`(problem/statedIntent/architecture 등)·`designValidity`·findings 등 **모든 자연어 필드 값을 한국어로** 채운다. 에이전트가 반환한 값이 영어면 그대로 붙여넣지 말고 의미를 한국어로 옮겨 쓴다(코드·식별자·파일경로·enum/라벨 토큰은 원문 유지). `#background` 카드가 특히 이 실수가 잦은 지점.

### 4단계 — 산출물 자체검증 (생략 금지)

작성·append 후 "완료" 보고 전에 번들 스크립트로 검증:

```bash
bash ~/.claude\skills\senior-review\scripts\verify.sh <리뷰_HTML_경로>
# 종료코드 0=FAIL없음, 1=FAIL있음. WARN(placeholder 목록)은 육안 확인.
```

스크립트는 마커·anchor·`<p>` 중첩에 더해 **디자인 시스템 정합**(정의 안 된 `var(--x)` 사용·`.review-point`의 `.rp-content` 래퍼 누락·`priority`/`action-tag`/`severity-tag`를 모디파이어 없이 단독 사용)까지 자동으로 잡는다 — append 라운드가 템플릿에서 이탈하는 전형(SR-7 3차 실측)이라 반드시 통과시킨다. 스크립트가 여전히 못 잡는 것(`<`·`>`·`&` 미이스케이프, 색·간격의 미세한 어긋남)은 육안 확인. 검증 출력 1~3줄을 완료 보고에 첨부한다.

**append 라운드는 "복붙 골격"을 복사한다 — 기억으로 재구성 금지**(SR-7 3차 컴포넌트 깨짐의 근본 원인 = 골격 없이 즉흥 재작성). `template.html` 맨 아래 `<!-- ROUND-INSERT-MARKER -->` **바로 위**에 라운드 골격 주석(`라운드 골격 · COPY-PASTE TEMPLATE`)이 박혀 있다. 그 안의 `<section class="round-divider" id="round-【N】"> … </section>`을 **통째로 복사**해 마커 위에 붙이고 `【…】`만 채운다. 골격이 곧 정답 구조다 — 1·2차를 흉내 내거나 새로 짜지 않는다.

골격이 보장하는 불변식(verify.sh가 자동 FAIL로 강제하니 반드시 통과):
- 라운드 헤더 = `.round-divider` > `.section-head`(>`.section-num`+`.section-title`+`.section-sub`) > `.round-meta`(사유·대상·변경). 판정을 재산정할 때만 `.summary-verdict` 한 블록 추가. **임의 inline-style div·`.commit-head` 재사용 금지**(그게 SR-7 2·3차가 제각각이 된 원인).
- 각 finding = `<details class="review-point {severityClass}">` → `<summary>`(`.severity-tag`+`.rp-title`) → **`<div class="rp-content">`로 본문 전체를 감싼다**(이 래퍼가 padding·구분선을 만든다).
- 색이 모디파이어에서 나오는 클래스는 단독 사용 금지: `priority`는 `required/recommended/optional/fyi`, `action-tag`는 `required/recommended/optional/out-of-scope`, `severity-tag`는 `critical/medium/minor/info/good/check` 중 하나를 반드시 동반. 요약표의 issue/nit 같은 분류 칩은 `priority`가 아니라 `severity-tag {색}`을 쓴다.
- 색/여백은 `:root`에 정의된 변수만 사용(`--sub`=muted 회색). `--muted-foreground` 등 임의 변수명 금지.
- 이전 라운드 지적 해결표는 `.status`(resolved/unresolved/partial/pending)로 — 골격에 포함. 라운드 추가 시 `#toc`에도 같은 id 항목 추가.

---

## 시니어 리뷰 원칙 (워크플로우가 강제하는 것 — 사람도 알아야 할 요지)

전체 근거·인용은 `references/methodology.md`.

**용어 미니 사전** (이 스킬·workflow.js 전반에서 쓰는 내부 용어):

| 용어 | 뜻 |
|---|---|
| **tier** (T1/T2/T3) | 발견의 본질 등급. T1=관측 가능한 실패(크래시·데이터 손실·보안·계약 파괴), T2=확립된 패턴 위반 + 구체적 유지비용, T3=작지만 실재(가독성·일관성·실수 유발). 검증자가 확정하며 JS가 못 바꾸게 고정 |
| **severityClass** | tier를 HTML 카드 색으로 변환한 표시 등급 — T1→`critical`, T2→`medium`, T3→`minor` (+`info`/`good`/`check`는 라벨에서 직접) |
| **epicenter** | 논리 변경량이 가장 큰 파일 — 리뷰를 여기서부터 읽도록 정렬 기준이 된다 |
| **zoom-out 테스트** | 발견을 살릴지 결정하는 게이트: "변경 전체 목적·코드베이스 전체 구조로 시야를 넓혀도 이 지적이 유효한가?" 통과 못 하면 맥락맹으로 컷 |
| **vid** | 검증 단계에서 발견마다 붙는 id — 모더레이터 병합·자동 복구의 추적 키 |
| **lane / lens** | 병렬 리뷰 에이전트 1개가 맡는 단일 관점(correctness·security·design 등) — 서로의 발견을 못 본다 |

### 0번 대원칙 — 적은 "사소함"이 아니라 "맥락맹(context-blindness)"이다

**꼼꼼히 사소한 것까지 봐주는 건 좋은 리뷰다.** 이 스킬은 사소한 발견을 억누르지 않는다. 진짜 문제는 **PR 전체 목적·코드 전체 구조·맥락을 고려하지 않은 채** 줄 하나만 떼서 사소한 걸 던지는 것 — 즉 "이 패턴은 위험"이라는 공식 대입(맥락맹)이다. 그래서 모든 발견은 keep 전에 **zoom-out 테스트**를 통과해야 한다: *"이 PR이 통째로 뭘 하려는지, 코드베이스가 어떻게 짜여 있는지로 시야를 넓혀도 이 지적이 여전히 말이 되나, 아니면 그 줄만 노려볼 때만 문제로 보이나?"* 생사는 **크기가 아니라 이 큰그림 근거**로 가른다:

- **큰그림에 근거한 발견은 사소해도 살린다** → `nitpick`/`suggestion (non-blocking)`으로 명확히 라벨해 노출. (작성자가 "아 이건 진짜 챙겨줬네" 하는 디테일.)
- **맥락맹인 발견은 크든 작든 죽인다** → 줄 하나만 보고 PR 전체 의도·코드 전체를 놓친 지적(예: 설계가 일부러 한 곳에 모아둔 에러처리를 개별 줄마다 요구, 코드베이스 전반과 일관된 네이밍·형태를 트집, PR 목적상 무의미해진 부분을 "개선"), 추적 안 된 표면 패턴매칭, 작성자가 의도한 트레이드오프를 모르고 던진 지적, 도달 불가 시나리오.
- **단, 순수 기계적 노이즈는 별개로 억제**: linter/formatter/type-checker가 잡을 스타일은 발견이 아니다(있으면 "lint 규칙 추가" 한 줄로). 같은 패턴이 여러 곳이면 대표 1건+카운트로 묶는다.

> 즉 **signal ratio 같은 크기 기반 하드컷은 쓰지 않는다.** "맥락 근거 게이트"가 그 자리를 대신한다.

### 핵심 지시문

1. **설계 블로커는 라인 코멘트보다 먼저, 별도로 surface한다.** 설계가 틀렸으면 라인이 깨끗해도 approve 안 함. (잘못된 설계 위에 5개 PR이 더 쌓이는 비용 > 1차 리뷰가 불완전한 비용.)
2. **epicenter 파일**(논리 변경량 최대)을 명시하고 거기서부터 리드.
3. **모든 코멘트에 Conventional Comments 라벨**(issue/suggestion/nitpick/question/thought/praise/FYI) + blocking 여부. 무라벨 코멘트 금지.
4. **모든 발견은 추적된 맥락에 근거**해야 한다. T1/T2는 위반한 엔지니어링 원칙(SRP/YAGNI/DRY 등)을 인용. 근거가 "나라면 다르게"뿐이면 발견이 아니다(컷 또는 `thought`).
5. **사소한 발견도 환영하되 근거를 댄다.** nit이라도 "왜 이게 더 나은지"를 맥락으로 설명 — 취향이 아니라 가독성·일관성·실수 유발 가능성 등 구체 근거. 근거 못 대는 nit만 버린다.
6. **크기로 거르지 않는다.** nit이 많아도 전부 맥락 근거가 있으면 전부 노출(non-blocking으로 라벨해 blocking 신호를 흐리지 않게). blocking과 non-blocking을 명확히 분리하는 게 노이즈 억제보다 우선.
7. **보안/정확성 발견 전 reachability를 결정적으로 확인**(grep/AST/Read). 미확인이면 `issue` 아닌 `question`.
8. **리뷰 세션을 생성 컨텍스트와 분리**. 검증자는 diff+요구사항만 받고 작성자 추론은 안 받는다(자기검토 환각 방지).
9. **아키텍처 제약을 프롬프트 앞에 front-load**(lost-in-the-middle 방지).
10. **억제는 blocklist 아닌 allowlist로**("이 카테고리만 보고하라"). LLM은 부정 지시("X 금지")를 약하게 따른다.
11. **교차파일·비즈니스 로직 발견은 "사람 확인 필요"로 표기**, 모델이 검증 못 하는 정합성을 단정하지 않는다.
12. **개인 취향으로 blocking 금지**. 스타일 가이드 인용 없는 스타일 지적은 의견 → non-blocking(`nitpick`).
13. **리뷰당 최소 1개 `praise`** (비협조적 톤 방지 — 비협상).
14. **실질(blocking) 발견이 ~8개를 넘으면** 개별 나열이 아니라 "이 PR은 너무 크다/체계적 문제가 있다"는 상위 신호로 묶는다. (non-blocking nit 개수에는 이 상한을 적용하지 않는다.)

---

## 다른 리뷰 스킬과의 경계

- `/pr-review` — 타인 PR 가벼운 1패스 HTML 리뷰. 빠르게 훑을 때.
- `/self-review` — PR 올리기 전 작성자 자기 점검(텍스트 보고).
- `/security-review` — 보안 전용.
- `/code-walkthrough` — 코드 한 줄씩 독해(문제 탐지 아님).
- **`/senior-review` (이 스킬)** — 위 1패스의 한계를 다중 에이전트로 넘어선 **심층 HTML 리뷰**. 무겁고 토큰을 많이 쓰는 대신, 일관성·맥락맹·표면성·의도 미파악을 구조적으로 해결. 중요한 PR·놓치면 안 되는 변경에. **시나리오 4종을 모두 커버**: 타인 PR 심사(peer-pr), PR 올리기 전 자기 점검(pre-submit — /self-review의 심층판), 개발 중간 방향 점검(wip), 기존 코드 분석·감사(audit). 같은 파이프라인이지만 verdict·어휘·체크리스트가 시나리오를 따라간다.

기존 `/pr-review`·`/self-review`는 **대체하지 않는다** — 가벼운 용도로 그대로 둔다.

**리뷰 이후 — 후속 처리**: 이 리뷰가 만든 산출물 HTML의 지적들을 사람 대신 1차 처리(오탐 거름 + 수정 + 검증 + 보류 분류)하고 같은 문서에 처리 라운드와 2차 리뷰를 남기려면 **`/senior-loop-developer`**로 이어진다 — 이 스킬의 HTML 산출물을 입력으로 받는다. (리뷰 → 처리 → 재리뷰가 한 흐름.)
