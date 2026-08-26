---
name: senior-detail-reviewer
description: "senior-review가 만든 리뷰 보고서를 받아 각 지적이 오탐인지 유효한지 read-only로 2차 판정만 하는 스킬(코드 수정·git 없음). 독립 판정자 2명(opus)이 전체 지적을 배치로 판정하고, 오탐은 근거 인용이 만장일치일 때만 확정 — 갈리거나 근거 부족이면 유효/사람확인으로 보수 처리(진짜 버그를 오탐으로 죽이지 않음). 결과를 같은 senior-review 문서에 '정밀 판정 라운드'로 append한다. 사용자가 'detail-reviewer', '디테일 리뷰어', '오탐인지 봐줘', '이 리뷰 믿어도 되나', '리뷰 판정만', '오탐 걸러줘', 'senior-detail-reviewer'를 언급하거나, senior-review 결과의 신뢰도만 확인하고 싶을 때 트리거. 지적을 실제로 고치는 처리는 /senior-loop-developer, 리뷰 자체는 /senior-review가 한다 — 이 스킬은 '고치지 않고 오탐/유효 판정만' 하는 순수 리뷰어용이다."
model: opus
effort: high
---

# Senior Detail Reviewer (리뷰 오탐/유효 read-only 판정)

## 이 스킬이 존재하는 이유

senior-review는 꼼꼼하지만 오탐이 섞인다. 순수 리뷰어(코드를 고칠 입장이 아닌 사람) 입장에선 **"이 리뷰의 어느 지적을 믿어야 하나"**만 알면 된다 — 고치는 건 작성자 몫이다. 이 스킬은 senior-review 결과를 받아 각 지적을 **오탐/유효/사람확인**으로 2차 판정만 하고(코드·git 손 안 댐), 그 판정을 보고서에 남긴다.

`senior-loop-developer`가 이 판정을 내부 1단계로 쓰되 거기에 "수정"까지 붙인 것이라면, 이 스킬은 **판정에서 멈추는 read-only 버전**이다.

핵심은 **오탐 판정에 안이하지 않은 것**: 오탐 확정은 판정자 2명이 **모두, 근거를 인용해** 동의할 때만. 한 명이라도 유효라고 보거나 근거가 부실하면 유효 또는 사람확인으로 남긴다(진짜 버그를 오탐으로 죽이는 게 최악의 실패라서).

## 비용 설계 (senior-review·senior-loop-developer와 동일 원칙)

1. **findings·코드는 메인 루프가 1회만 수집해 인라인 전달.** 판정 에이전트는 `git`/`grep`/`Read` 재탐색 금지.
2. **판정은 배치** — 지적 N개여도 판정자는 2명(건별로 안 띄움). 각자 전체 리스트를 한 번에 판정.
3. **합의는 JS로 결정적 처리**(오탐은 만장일치+근거일 때만, 아니면 보수적으로 유효/사람확인).
4. read-only라 코딩·검증·재시도·루프가 없다 — 이 스킬은 senior-loop-developer보다 훨씬 가볍다.

> **모델**: 판정자 2명 모두 opus(정확도가 유일한 산출물이라). 워크플로우가 `agent({model:'opus'})`로 고정.

---

## 절대 규칙

- **완전 read-only**: 코드 수정·`git`·`gh` **절대 금지**. 산출물은 보고서 append뿐. (유일한 예외: 판정이 인라인에 없는 미표시 파일 — 호출처/피호출처 — 에 걸리면 판정자가 그 파일 **1개만 Read** 가능. 그래도 수정은 절대 없음.)
- **용어**: `tier`(adjustedTier T1/T2/T3) = T1(관측 가능한 실패: 크래시·데이터 손실·보안·계약 파괴) / T2(확립된 패턴 위반 + 구체적 유지비용) / T3(작지만 실재: 가독성·일관성·실수 유발), senior-review와 동일 체계. · `disputed`(판정 갈림) = 판정자 한 명은 오탐, 한 명은 유효로 본 상태 → 유효로 두되 "사람 최종 확인" 표기. · 이 스킬의 판정은 **병원 재진(second opinion)** 과 같다 — 원 진단(senior-review)을 다른 의사 2명이 다시 봐서 오진(오탐)을 걸러주되, 애매하면 "정밀검사(사람 확인) 필요"로 넘긴다.
- **선행 조건**: senior-review HTML 보고서가 있어야 한다(`~/.claude\reports\senior-review\SR-*.html`). 없으면 "먼저 /senior-review를 돌려라" 안내 후 멈춘다.
- **오탐 확정 기준**: 판정자 2명 만장일치 + 양쪽 다 근거 인용. 이 요건은 워크플로우 JS가 강제한다(신뢰하고 의존).
- **append 대상**: 새 HTML을 만들지 않고 senior-review가 만든 그 파일에 '정밀 판정 라운드'를 append(senior-review 라운드 골격 규칙 준수).

---

## 실행 흐름

### 1단계 — 보고서·findings·코드 수집 (메인 루프가 직접)

**① 보고서 찾기**: 경로를 받으면 그걸, 아니면 `~/.claude\reports\senior-review\`에서 최근/대상 슬러그 일치 `SR-*.html`. 모호하면 한 번 묻는다.

**② findings 파싱**: HTML의 각 `<details class="review-point …">` 카드를 구조화 — `fid`(0부터), `file`·`line`(breadcrumb), `severityClass`, `label`, `blocking`, `title`, `problem`, `recommendation`. **이미 이전 라운드에서 판정·해결된 카드는 제외.**

> **실측 DOM (SR-6 e2e)**: 여는 태그는 `<details class="review-point minor" id="rp-1">` 형태 — **class 뒤에 id 속성이 있다.** regex는 `<details class="review-point ([\w-]+)"[^>]*>`처럼 `[^>]*>`로 닫아야 한다(`"`+`>` 직결 가정 시 0건 매치). severityClass는 class 두 번째 토큰, title·label은 `<summary>` 텍스트(`칭찬 [praise] …`/`경미 [nitpick] … (non-blocking)`), file·line은 `.breadcrumb`(`커밋 N › path › L17` — `L` 접두 제거).

**③ scenario 승계**: 헤더 kicker에서 `peer-pr`/`pre-submit`/`wip`/`audit`.

**④ 코드 수집** (1회, 인라인용):
```bash
cd <projectRoot>
git diff <base>..HEAD            # → diffText
for f in <finding 파일 목록>; do git show HEAD:"$f" | cat -n; done   # → files[].content
```
base 불명확하면 `origin/main`(없으면 `master`) 가정하고 판정 라운드에 한 줄 명시. (read-only라 브랜치는 필요 없다.)

`args` 구성:
```json
{
  "reportPath": "~/.claude\reports\senior-review\SR-N-slug.html",
  "projectRoot": "<프로젝트 루트>/repo",
  "base": "<base ref>",
  "scenario": "peer-pr",
  "findings": [{"fid":0,"file":"...","line":"42","severityClass":"critical","label":"issue","blocking":true,"title":"...","problem":"...","recommendation":"..."}],
  "diffText": "<git diff 전체>",
  "files": [{"path":"...","content":"<cat -n 전체>"}]
}
```

### 2단계 — 판정 워크플로우 실행

```
Workflow({
  scriptPath: "~/.claude\skills\senior-detail-reviewer\workflow.js",
  args: { ...1단계 객체... }
})
```

워크플로우: **Judge**(독립 판정자 2명 opus 병렬, 배치, 서로 안 봄 — 오탐/유효/사람확인) → JS 합의(오탐은 만장일치+근거일 때만, 갈리면 유효로 두되 "판정 갈림" 표기, 근거 부실 오탐은 사람확인).

반환값:
```
{ reportPath, readOnly:true, scenario,
  falsePositives: [{fid,title,file,line,reason,evidence,agreement}],
  valid:          [{fid,title,file,line,adjustedTier,note,disputed}],
  needsHuman:     [{fid,title,file,line,why}],
  skipped:        [{fid,title,label}],   // praise/FYI
  stats }
```

### 3단계 — 정밀 판정 라운드를 보고서에 append (메인 루프)

`reportPath` HTML의 `<!-- ROUND-INSERT-MARKER -->` 위에 판정 라운드 1개를 삽입한다. **senior-review SKILL.md 4단계의 "라운드 골격 복붙" 규칙을 그대로 따른다**(기억으로 재구성 금지 — `template.html` 하단 골격 주석 복사).

**라운드 번호·삽입 위치 (자기완결)**:
```bash
# 라운드 N = 문서의 기존 라운드 수 + 2 (1차 = 본편 리뷰. senior-review 처리/판정 라운드와 통합 카운트 → 번호 충돌 없음)
# ⚠️ 반드시 id="round- 까지 포함해 grep — 'class="round-divider"'나 '<section class="round-divider"'만 세면
#    ROUND-INSERT-MARKER 안내 주석 원문까지 카운트돼 N이 어긋난다(SR-6 e2e 실측 2회 — 주석에 태그 예시가 그대로 있음)
N=$(( $(grep -c 'section class="round-divider" id="round-' "$reportPath") + 2 ))
# template.html 하단 '라운드 골격 · COPY-PASTE TEMPLATE' 주석의 <section class="round-divider" id="round-【N】">를
# 통째 복사해 <!-- ROUND-INSERT-MARKER --> 바로 위에 삽입하고 【N】 등 placeholder만 채운다.
```
**자기방어 (형제 스킬 부재 시)**: `senior-review/SKILL.md`나 `template.html`을 읽을 수 없으면(이동·삭제) `reportPath` HTML **자체의 기존 `.round-divider` 한 개를 복사**해 구조 템플릿으로 쓴다(같은 문서라 디자인 시스템이 self-contained). 그 뒤 아래 `verify.sh`로 정합을 강제 확인하고, 골격 출처가 불확실했음을 완료 보고에 1줄 남긴다. (즉 senior-review는 편의 참조이지 단일 실패점이 아니다.)

**재실행(overwrite) 규칙**: 같은 findings 대상 정밀 판정 라운드가 **이미 있는 문서에 다시 돌릴 때**는 새 라운드를 누적 삽입하지 말고 — `grep`이 라운드만 계속 늘린다 — 사용자에게 "기존 판정 라운드를 대체할지, 새 라운드로 추가할지" 한 번 묻는다. (판정은 read-only 재현이라 같은 입력이면 결과가 거의 같아, 무한 누적은 노이즈다.)

라운드 내용:

- 라운드 헤더: "정밀 판정 라운드 N — senior-detail-reviewer (read-only)", `.round-meta`에 판정 일시·요약 카운트(오탐 X·유효 Y·사람확인 Z).
- **오탐**(`falsePositives`): 원 카드에 `.status`(예: 오탐 표기) + **반드시 근거(evidence) 인용**. 원 카드는 삭제하지 않고 보존.
- **유효**(`valid`): 실제 문제로 확인됨 + `adjustedTier`(원 severity와 다르면 조정 의견 명시). `disputed`면 "판정 갈림 — 사람 최종 확인" 눈에 띄게.
- **사람확인**(`needsHuman`): `.status pending` + 무엇을 확인해야 하는지(교차파일·비즈니스 로직·런타임). **사용자가 직접 봐야 할 목록**.
- `#toc`에도 이 라운드 항목 추가.

**오탐 근거(evidence) 작성 — 좋음/나쁨 대비**:
- ❌ 나쁜 예(추정): `"아마 의도된 듯", "별 문제 없어 보임"` — 출처 인용 없음(애초에 워크플로우가 사람확인으로 돌림).
- ✅ 좋은 예(출처 인용): `"runner.py:42의 == 비교는 의도적 — 커밋 abc123 'allow loose eq for null check'에 명시. null/undefined 동시 처리 목적."` (코드 라인/커밋·PR/문서/컨벤션 중 무엇이 근거인지 보여야 함.)

**유효(valid) 판정 — severity 조정 예시**: 유효로 두되 원 severity가 과대/과소면 `adjustedTier`로 조정하고 근거를 명시한다.
- ✅ `"유효하나 원 critical은 과대 — sync()가 재시작 시 idempotent(오프셋 재실행 가드 :88 확인)라 데이터 손실 없음. at-least-once 재처리 비용만 → T2로 하향."` (조정 안 하면 원 tier 유지, 이유 불필요.)

**사람확인(needs-human) 판정 — 4요소(누가·무엇·어떻게·기대결과)**: 코드만으로 오탐/유효를 못 가릴 때. **무엇을 확인하면 어떤 판단이 서는지(기대결과)까지** 적어야 사용자가 바로 행동한다.
- ❌ 나쁜 예(막연): `"교차파일 확인 필요"` — 뭘, 어디서, 확인하면 뭐가 결정되는지 없음.
- ✅ 좋은 예: `"sync()가 외부 큐 상태에 의존 — 큐가 at-most-once인지 인프라 설정(<파일/대시보드>)을 사용자가 확인해야 함. at-most-once면 이 지적은 유효(중복 유실 위험), at-least-once면 오탐."` (누가=사용자 / 무엇=큐 delivery 보장 / 어떻게=인프라 설정 확인 / 기대결과=유효·오탐 분기)

**HTML 안전성 (senior-review SKILL.md 4단계·SR-8 실측과 동일)**: codebox는 골격 구조 그대로(bare `<pre>` 금지), 색 모디파이어 클래스는 정의된 모디파이어 동반, `<`·`>`·`&` 이스케이프, 블록 요소를 `<p>`에 넣지 않기.

작성 후 검증:
```bash
bash ~/.claude\skills\senior-review\scripts\verify.sh <reportPath>
```
**FAIL이면 완료 보고 금지** — 골격 이탈이니 `template.html` 하단 골격을 다시 복사해 재작성하고 재검증. 검증 출력 1~3줄을 완료 보고에 첨부.

### 4단계 — 완료 보고

사용자에게: 오탐 X건(각 근거 한 줄), 유효 Y건(severity 조정분 있으면 명시), **사람확인 Z건(직접 봐야 할 것 — 가장 눈에 띄게)**. 이 스킬은 아무것도 고치지 않았음을 명확히 — 고치려면 `/senior-loop-developer`.

---

## 검증 이력

- **2026-07-02 e2e 통주행 (SR-6, 실제 PR 1건)**: 파싱(카드 4: praise 1+nitpick 3) → Workflow(판정자 2·opus·56k토큰·47초) → append(2차 판정 라운드) → `verify.sh` 전부 통과 exit 0. 오탐 게이트 실증 — RUNBOOK 순서 지적을 만장일치+HEAD/crontab 대조 인용으로 오탐 확정(PR이 이미 재정렬), 유효 2건(T3)·needsHuman 0·praise 스킵 정상. 이 실측에서 파싱 regex(id 속성)와 라운드 N grep(주석 오카운트) 함정을 잡아 본문에 반영함.

## 다른 스킬과의 경계

- `/senior-review` — 리뷰(문제 탐지) 자체. 이 스킬의 **입력을 만든다**.
- **`/senior-detail-reviewer` (이 스킬)** — 그 리뷰 결과를 **read-only로 오탐/유효 판정만**. 순수 리뷰어가 "이 리뷰 믿어도 되나"를 걸러낼 때. 코드는 안 고친다.
- `/senior-loop-developer` — 판정에 더해 **실제 수정·검증·2차 리뷰까지** 하는 처리 스킬. 이 스킬의 판정 로직을 내부 1단계로 포함하되 read-only가 아니다. 고칠 거면 이걸 쓴다.
- `/pr-review`·`/self-review` — 가벼운 단일 패스 리뷰.
