---
name: senior-loop-developer
description: "senior-review가 만든 리뷰 보고서를 받아 지적들을 자동으로 '처리'하는 후속 스킬. 다중 에이전트로 (배치 판정[오탐/수정/보류] → 수정대상만 파일별 코딩 → 분리된 검증)을 거쳐, 오탐은 근거 달아 패스·실수정은 고치고 검증·영향범위 크거나 애매한 건 사람에게 보류한 뒤, 같은 senior-review 문서에 처리 라운드를 append하고 마지막에 senior-review를 1회 재호출해 2차 리뷰까지 남긴다. 사용자가 'loop-developer', '루프디벨로퍼', '리뷰 처리해줘', '지적 처리해줘', '리뷰 결과 반영해줘', '오탐 거르고 고쳐줘', 'senior-loop-developer'를 언급하거나, 방금 senior-review를 돌린 뒤 '이거 처리해줘'라고 할 때 트리거. 리뷰 자체(문제 탐지)는 /senior-review, 단순 PR 리뷰는 /pr-review가 한다 — 이 스킬은 '이미 나온 리뷰를 사람 대신 1차로 처리'하는 게 목적이다."
model: opus
effort: high
---

# Senior Loop Developer (리뷰 보고서 자동 처리)

## 이 스킬이 존재하는 이유

senior-review는 pr-review보다 꼼꼼하지만 여전히 100% 신뢰는 못 한다 — 여러 번 돌리면 오탐도, 못 잡은 것도 계속 나온다. 그래서 **사람이 리뷰 결과를 2~3번 받아 처리하는 게 필연**이고, 그 처리(오탐 판별 → 고칠 것 고치기 → 검증 → 애매한 건 사람에게 남기기)가 가장 오래 걸린다. 이 스킬은 그 처리 루프의 1차를 자동화한다.

핵심은 **사람이 했을 판단을 그대로 재현하되, 안이하지 않게** 하는 것:
- 오탐은 **근거를 인용**해야만 패스(근거 없으면 보류) — 진짜 버그를 자기합리화로 죽이지 않게.
- 수정은 **코딩한 에이전트가 아닌 별도 에이전트가 검증** — 자기 작업을 안이하게 보는 편향 차단.
- 영향범위가 크거나(공용 유틸·공개 인터페이스·타 기능 영향·PR 스코프 초과) 애매한 건 **자동수정 금지, 사람에게 보류**.

## 비용 설계 (senior-review·lite-research와 동일 원칙 — 에이전트 남발 금지)

1. **findings·코드는 메인 루프가 1회만 수집해 인라인 전달.** 판정·검증 에이전트는 `git`/`grep`/`Read` 재탐색 금지(코딩 에이전트만 예외 — 실제 파일 편집).
2. **판정은 배치 1패스**(지적 >12건이면 2분할 병렬). 건별로 에이전트 안 띄운다.
3. **코딩은 '수정' 분류분만, 파일별로 묶어** 에이전트 1개씩. 오탐·보류는 안 띄운다 → 비용이 실제 수정 파일 수에 비례.
4. **검증도 배치 1패스**(코딩과 분리).
5. **결정적 처리는 JS로**(오탐 근거부족→보류 강등, 영향범위 큰 fix→보류 강등, 집계).
6. **하드캡**: 검증 반려분만 코딩 재시도 1회 → 또 반려면 보류. 전체 루프 1라운드(추가는 사용자가 재호출).

> **모델**: 판정·검증 = opus(정확도 생명), 코딩 = 위험도별(nitpick → sonnet, logic/dangerous → opus). 워크플로우가 `agent({model})`로 고정.

---

## 절대 규칙

- **선행 조건**: senior-review가 먼저 실행돼 HTML 보고서가 있어야 한다(`~/.claude\reports\senior-review\SR-*.html`). 없으면 사용자에게 "먼저 /senior-review를 돌려라"라고 안내하고 멈춘다.
- **수정은 git 브랜치에서**: 코드를 직접 고치므로 반드시 작업 브랜치에서. push는 절대 안 한다(글로벌 룰). 커밋은 처리 후 의미 단위로(아래 5단계).
- **보류는 손대지 않는다**: 영향범위 크거나 애매한 건 코드를 건드리지 않고 보고서에만 남긴다.
- **오탐 패스는 근거 필수**: 근거 없는 오탐 주장은 워크플로우가 보류로 강등한다(신뢰하고 의존).
- **append 대상**: 새 HTML을 만들지 않는다 — senior-review가 만든 **그 파일에** 처리 라운드를 append(senior-review의 라운드 골격 규칙을 그대로 따른다).

---

## 실행 흐름

### 1단계 — 보고서·대상 확정 + findings·코드 수집 (메인 루프가 직접)

**① 보고서 찾기**: 사용자가 경로를 주면 그걸, 아니면 `~/.claude\reports\senior-review\`에서 가장 최근(또는 대상 슬러그 일치) `SR-*.html`을 쓴다. 어느 보고서인지 모호하면 한 번 묻는다.

**② findings 파싱**: 보고서 HTML을 Read해서 각 `<details class="review-point …">` 카드를 구조화한다. 카드당:
- `fid`: 0부터 일련번호
- `file`, `line`: `.breadcrumb`에서
- `severityClass`: `severity-tag {critical|medium|minor|info|good|check}`에서
- `label`: `[issue]`/`[suggestion]`/`[nitpick]`/`[question]`/`[thought]`/`[praise]`/`[FYI]`
- `blocking`: required/blocking 표기 여부
- `title`, `problem`(문제 섹션), `recommendation`(권장 조치 섹션)
- **append된 이전 라운드에서 이미 resolved 처리된 카드는 제외**(중복 처리 방지). 미해결·신규 지적만.

> **실측 DOM (SR-6 e2e, senior-detail-reviewer와 공통)**: 여는 태그는 `<details class="review-point minor" id="rp-1">` 형태 — **class 뒤에 id 속성이 있다.** regex는 `<details class="review-point ([\w-]+)"[^>]*>`처럼 `[^>]*>`로 닫아야 한다(`"`+`>` 직결 가정 시 0건 매치). severityClass는 class 두 번째 토큰, title·label은 `<summary>` 텍스트, file·line은 `.breadcrumb`(`커밋 N › path › L17` — `L` 접두 제거).

**③ scenario 확정**: 보고서 헤더 kicker(`PEER PR REVIEW`/`PRE-SUBMIT CHECK`/…)에서 `peer-pr`/`pre-submit`/`wip`/`audit`를 읽어 승계.

**④ 코드 수집** (1회만, 인라인용):
```bash
cd <projectRoot>
git diff <base>..HEAD            # → diffText
# findings가 가리키는 파일들만 전체 내용 (라인번호 포함)
for f in <finding 파일 목록>; do git show HEAD:"$f" | cat -n; done   # → files[].content
```
base가 불명확하면 `origin/main`(없으면 `master`) 가정하고 그 사실을 처리 라운드에 한 줄 명시.

**⑤ 작업 브랜치 확보**: 이미 작업 브랜치면 그대로. main/master 위라면 `/git-workflow` 규칙대로 브랜치를 만든 뒤 진행(타입은 `fix`/`refactor` 등 4종). 브랜치명을 `args.branch`로.

수집한 걸로 `args`를 만든다:
```json
{
  "reportPath": "~/.claude\reports\senior-review\SR-N-slug.html",
  "projectRoot": "<프로젝트 루트>/repo",
  "branch": "fix/review-followup",
  "base": "<base ref>",
  "scenario": "pre-submit",
  "findings": [
    {"fid":0,"file":"backend/app/x.py","line":"42","severityClass":"critical","label":"issue","blocking":true,"title":"...","problem":"...","recommendation":"..."}
  ],
  "diffText": "<git diff 전체>",
  "files": [{"path":"backend/app/x.py","content":"<cat -n 전체>"}]
}
```

### 2단계 — 처리 워크플로우 실행

```
Workflow({
  scriptPath: "~/.claude\skills\senior-loop-developer\workflow.js",
  args: { ...1단계 객체... }
})
```

워크플로우가 내부적으로(메인은 결과만 받음): **Triage**(배치 판정 opus — 오탐/수정/보류, 오탐은 근거 강제·없으면 보류 강등, 영향범위 큰 fix는 보류 강등) → **Code**(수정분류분만 파일별 코딩, 위험도별 모델, 실제 파일 Edit) → **Verify**(배치 검증 opus, 코딩과 분리 — resolved/not-resolved/regression-risk, 반려분 코딩 1회 재시도 후 보류).

반환값:
```
{ reportPath, branch, scenario,
  falsePositives: [{fid,title,file,line,reason,evidence}],
  fixed:          [{fid,title,file,line,riskClass,summary,changedLines}],
  deferred:       [{fid,title,file,line,reason,blocking}],
  skipped:        [{fid,title,label}],          // praise/FYI
  stats }
```

### 3단계 — 처리 라운드를 보고서에 append (메인 루프)

`reportPath` HTML의 `<!-- ROUND-INSERT-MARKER -->` 바로 위에 처리 라운드 1개를 삽입한다. **senior-review SKILL.md 4단계의 "라운드 골격 복붙" 규칙을 그대로 따른다**(골격을 기억으로 재구성 금지 — `template.html` 하단 골격 주석을 복사). 라운드 내용:

- 라운드 헤더(`.round-divider` > `.section-head`): "처리 라운드 N — senior-loop-developer", `.round-meta`에 처리 일시·브랜치·요약 카운트(고침 X·오탐 Y·보류 Z).
- **고친 항목**(`fixed`): 각 원 카드의 해결표(`.status resolved`) + 무엇을 어떻게 고쳤는지(file:line, summary).
- **오탐 패스**(`falsePositives`): `.status`(예: `resolved`/별도 표기) + **반드시 근거(evidence) 인용**해서 "왜 오탐인지". 원 카드는 삭제하지 않고 보존.
- **보류**(`deferred`): `.status pending` + 사유(영향범위/애매/수정실패). blocking이었던 건 눈에 띄게 — **사용자가 직접 판단해야 할 목록**임을 명확히.
- `#toc`에도 이 라운드 항목 추가.

**오탐 근거(evidence) 작성 — 좋음/나쁨 대비** (워크플로우가 근거 부실분은 보류로 강등하지만, 살아남은 오탐도 이 기준으로 쓴다):
- ❌ **나쁜 예** (추정·자기합리화): `"아마 의도된 듯", "별 문제 없어 보임", "작성자가 알고 했을 것"` — 출처 인용 없음. 이런 건 애초에 보류로 갔어야 한다.
- ✅ **좋은 예** (출처 인용): `"runner.py:42의 == 비교는 의도적 — 커밋 abc123 메시지 'allow loose eq for null check'에 명시. null/undefined 동시 처리가 목적이라 === 강제는 오히려 버그."` (코드 라인 / 커밋·PR 텍스트 / 문서 / 컨벤션 중 **무엇을** 근거로 삼았는지가 보여야 한다.)

**HTML 안전성 (senior-review SKILL.md 4단계·SR-8 실측 결함과 동일 — 반드시 준수)**:
- 코드블록은 골격의 `.codebox` 구조(`.rp-content` 래퍼 + 라인 gutter)를 그대로 쓴다. **bare `<pre>`/`<code>`로 즉흥 작성 금지** — append 라운드가 골격에서 이탈해 코드가 안 보이는 게 SR-8 실측 결함이었다.
- 색이 모디파이어에서 나오는 클래스(`severity-tag`·`status`·`action-tag`)는 단독 사용 금지, 정의된 모디파이어를 반드시 동반. `:root`에 정의된 `var(--x)`만 사용.
- 코드 본문의 `<`·`>`·`&`는 `&lt;`·`&gt;`·`&amp;`로 이스케이프. 블록 요소를 `<p>` 안에 넣지 않는다.

작성 후 senior-review의 검증 스크립트로 정합 확인:
```bash
bash ~/.claude\skills\senior-review\scripts\verify.sh <reportPath>
```
**verify.sh가 FAIL이면 완료로 보고하지 않는다** — 십중팔구 골격 이탈이다. `template.html` 하단 라운드 골격 주석을 **다시 복사**해 해당 라운드를 재작성(기억으로 고치지 말 것)하고 재검증한다. WARN(placeholder 목록)은 육안 확인. 검증 출력 1~3줄을 완료 보고에 첨부.

### 4단계 — git 커밋 (수정이 있었다면)

`fixed`가 있으면 `/git-workflow` 규칙대로 의미 단위 커밋. 한 커밋 메시지에 처리한 지적을 요약(예: `fix: senior-review 지적 3건 반영 (오탐 2건 제외)`). **push는 하지 않는다.** 보류·오탐은 커밋하지 않는다(코드 변경 없음).

### 5단계 — 2차 리뷰 재호출 (senior-loop-developer가 마무리로 1회)

수정이 반영됐으니 senior-review를 **1회** 다시 돌려 같은 문서에 2차 리뷰를 남긴다. **senior-review SKILL.md의 1~3단계를 그대로 수행**한다(코드 재수집 → 같은 `args`로 `senior-review/workflow.js` 실행 → 같은 슬러그 파일에 라운드 append). 같은 슬러그라 senior-review가 알아서 append한다.

**재호출 안전장치 (무한·중복·유실 방지)**:
- **이 단계는 `senior-review`만 호출한다 — senior-loop-developer를 (자기 자신을) 재귀 호출하지 않는다.** 자동 처리 루프는 1라운드로 끝. (재귀 트리거가 무한 처리·과수정으로 번지는 걸 구조적으로 차단.)
- **`fixed`가 0건이면 2차 리뷰를 생략**한다 — 코드가 안 바뀌었으니 재리뷰는 토큰 낭비고 같은 결과가 또 나온다. 대신 처리 라운드(오탐·보류만)로 마무리.
- **2차 리뷰(senior-review 재호출)가 실패하면**(워크플로우 에러·중단) 3단계의 처리 라운드는 이미 append돼 보존되므로 유실 없음. 사용자에게 "처리는 완료, 2차 리뷰는 실패 — `/senior-review`를 수동으로 한 번 더 돌려라"라고 보고하고 멈춘다(처리 라운드를 롤백하지 않는다).

> **루프는 여기까지가 디폴트(1라운드 + 2차 리뷰).** 2차 리뷰에서 또 처리할 게 보이면 사용자가 senior-loop-developer를 다시 호출한다 — 2회 이상 자동 반복은 깔지 않는다(비용·과수정 방지).

### 6단계 — 완료 보고

사용자에게: 고친 것 N건(요약), 오탐 패스 M건(근거 한 줄씩), **보류 K건(사용자 판단 필요 — 특히 blocking이었던 것)**, 2차 리뷰 결과 verdict. 보류 목록을 가장 눈에 띄게 — 사용자가 다음에 결정할 것이므로.

---

## 다른 스킬과의 경계

- `/senior-review` — 리뷰(문제 탐지) 자체. 이 스킬의 **입력을 만든다**.
- `/pr-review`·`/self-review` — 가벼운 단일 패스 리뷰.
- **`/senior-loop-developer` (이 스킬)** — 이미 나온 리뷰를 **사람 대신 1차 처리**(오탐 거름 + 수정 + 검증 + 보류 분류)하고 2차 리뷰까지. 리뷰를 새로 하지 않는다.
