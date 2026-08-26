# Components — 컴포넌트 카탈로그

`base.html` 의 CSS 가 모든 컴포넌트 스타일을 제공한다. 아래 HTML 스니펫을 그대로 복사해 콘텐츠에 맞게 텍스트만 치환하면 된다.

**원칙**: 자의로 CSS 를 새로 작성하지 말 것. 기존 컴포넌트 조합으로 99%의 보고서가 가능하다. 도저히 필요한 컴포넌트가 없으면 새로 추가하되, `base-css.md` + `base.html` 두 파일을 함께 갱신한다.

---

## Quick Reference

| 컴포넌트 | 클래스 | 용도 |
|---------|--------|------|
| Header | `.report-header` | 보고서 상단 (kicker·제목·메타) |
| TL;DR | `.tldr` | 첫 화면 결론 (좌측 primary bar) |
| Callout | `.callout.{note\|info\|success\|warn\|danger}` + `<use href="#i-...">` | 주의·정보·경고 박스 |
| Badge | `.badge.{primary\|success\|warn\|danger\|info\|muted}` | 인라인 상태 표시 |
| Feature Grid | `.grid.cols-{2,3,4}` + `.card{.outline\|.highlight}?` | 카드 그리드 (특징·옵션) |
| Stat / KPI | `.stat` | 큰 숫자 강조 (sans bold) |
| Pros / Cons | `.proscons > .pros / .cons` | 장단점 좌우 비교 (명시 클래스로 색) |
| Comparison Table | `<table>` | 일반 비교표 |
| Decision Matrix | `<table class="decision">` + `.winner` | 점수 매트릭스 |
| Timeline | `.timeline` | 마일스톤·일정 |
| Step List | `<ol class="steps">` | 1→2→3 단계 |
| AS-IS / TO-BE | `.compare` (+ `.side.danger\|.success\|.primary`) | 전후 비교 좌우 |
| Code Block | `<pre><code>` | 코드 (다크 배경) |
| Progress Bar | `.progress > .bar` | 진행률 |
| Checklist | `.checklist` | 체크리스트 (인터랙티브) |
| Risk Heatmap | `.risk-grid` | 영향×확률 3×3 |
| Q&A Toggle | `<details class="qa">` | FAQ 접힘 |
| Term Hint | `<span class="term" title="...">` | 인라인 용어 힌트 (점선 밑줄) |
| Primer | `<details class="primer">` | 접이식 배경지식 (독자 보조) |
| Glossary | `<dl class="glossary">` | 하단 용어집 |
| Formula | `.formula` + `dl.formula-where` | 수식 블록 + 변수 뜻풀이 (method/explain) |
| Worked Example | `.example` | 숫자 예시·구체 예시 박스 (method/explain) |
| Mermaid Diagram | `.mermaid-wrap > .mermaid` | 다이어그램 |
| Footer | `.report-footer` | 보고서 하단 |

> **아이콘 sprite**: `base.html` 의 상단에 `<svg>` 안에 `<symbol id="i-{note|info|success|warn|danger}">` 5종이 미리 정의되어 있다. callout에서 `<svg class="callout-icon"><use href="#i-success"/></svg>` 형태로 참조한다 — 추가 의존 없음.

---

## 1. Header (보고서 헤더)

```html
<header class="report-header">
  <span class="kicker">Analysis Report</span>
  <h1>인프라 컨테이너화 전환 큰그림</h1>
  <p class="subtitle">VM 직접 배포 → Docker + Watchtower 기반 격리 구조로 이행</p>
  <div class="report-meta">
    <span class="item"><span class="label">작성자</span> <strong>홍길동</strong></span>
    <span class="item"><span class="label">작성일</span> <strong>2026-05-11</strong></span>
    <span class="item"><span class="label">상태</span> <span class="badge info">Draft</span></span>
    <span class="item"><span class="label">대상</span> <strong>인프라팀, CTO</strong></span>
  </div>
</header>
```

---

## 2. TL;DR (첫 화면 결론)

좌측에 4px primary bar가 자동으로 들어가는 surface 카드. gradient 없음, 본문은 `--fz-xl` 큰 단락.

```html
<div class="tldr">
  <span class="label">TL;DR</span>
  <p>VM 직접 배포 구조를 Docker + GCP Artifact Registry + Watchtower pull 모델로 전환해 <strong>블라스트 반경을 조직 전체에서 프로젝트 단위로 축소</strong>한다. 4주 안에 staging 환경 검증, 8주차에 prod 단계 이행.</p>
</div>
```

3~5개 요점을 리스트로 쓸 수도 있다:

```html
<div class="tldr">
  <span class="label">TL;DR</span>
  <ul>
    <li>VM 직접 배포 → 컨테이너 + 이미지 레지스트리로 전환</li>
    <li>SA 권한을 프로젝트별로 분리해 최소권한 원칙 준수</li>
    <li>Watchtower pull 모델 채택 (인바운드 포트 개방 불가 환경 대응)</li>
  </ul>
</div>
```

---

## 3. Callout (주의·정보 박스)

5종: note, info, success, warn, danger. 아이콘은 `base.html` 의 SVG sprite를 `<use>` 로 참조한다 (외부 의존 0).

```html
<div class="callout note">
  <svg class="callout-icon"><use href="#i-note"/></svg>
  <div class="body">
    <span class="title">참고</span>
    <p>이 보고서는 Draft 단계이며, 4월 30일 인프라팀 리뷰 후 v1 로 확정 예정.</p>
  </div>
</div>

<div class="callout info">
  <svg class="callout-icon"><use href="#i-info"/></svg>
  <div class="body">
    <span class="title">의사결정 배경</span>
    <p>GHCR 대신 GCP AR을 선택한 이유는 GitHub App Installation Token이 GHCR pull을 지원하지 않아 최소권한 원칙을 위반하기 때문이다.</p>
  </div>
</div>

<div class="callout success">
  <svg class="callout-icon"><use href="#i-success"/></svg>
  <div class="body">
    <span class="title">개선 효과</span>
    <p>VM 1대 탈취 시 소스코드 + Secrets 유출이 사라진다. 이미지에만 접근 가능, Secrets는 빌드 타임 주입 후 환경변수로만 존재.</p>
  </div>
</div>

<div class="callout warn">
  <svg class="callout-icon"><use href="#i-warn"/></svg>
  <div class="body">
    <span class="title">주의</span>
    <p>example-svc는 데몬·cron 간 코드 의존이 있어 컨테이너 경계 정의 전 의존 관계 명확화 필요.</p>
  </div>
</div>

<div class="callout danger">
  <svg class="callout-icon"><use href="#i-danger"/></svg>
  <div class="body">
    <span class="title">차단 요인</span>
    <p>온프레미스 환경에서 인바운드 포트 개방 불가 → SSH push 방식은 사용 불가.</p>
  </div>
</div>
```

> 아이콘 추가가 필요하면 `base.html` 의 `<defs>` 안에 새 `<symbol id="i-xxx">` 를 추가하고 본문에서 `<use href="#i-xxx"/>` 로 참조한다. `viewBox="0 0 24 24"`, stroke 1.75px, lineicons/lucide 스타일로 일관 유지.

---

## 4. Badge (인라인 상태)

```html
<span class="badge primary">강조</span>
<span class="badge success">완료</span>
<span class="badge warn">진행 중</span>
<span class="badge danger">차단</span>
<span class="badge info">검토 중</span>
<span class="badge muted">대기</span>
<span class="badge">v0.5</span>
```

표 안에서 상태 컬럼에 자주 쓴다.

---

## 5. Feature Grid (카드 그리드)

2/3/4 열 지원. 모바일에서 1열로 자동 전환.

```html
<div class="grid cols-3">
  <div class="card">
    <div class="card-kicker">Container</div>
    <h4>Docker</h4>
    <p>레이어 캐시 + Dockerfile 표준화로 빌드 재현성 확보.</p>
  </div>
  <div class="card">
    <div class="card-kicker">Registry</div>
    <h4>GCP Artifact Registry</h4>
    <p>SA 단위 IAM 으로 repo 격리. <code>asia-northeast3</code> 리전 사용.</p>
  </div>
  <div class="card">
    <div class="card-kicker">Delivery</div>
    <h4>Watchtower</h4>
    <p>아웃바운드 polling. 인바운드 포트 개방 불필요.</p>
  </div>
</div>
```

---

## 6. Stat / KPI (큰 숫자)

```html
<div class="grid cols-3">
  <div class="stat">
    <div class="label">감소된 블라스트 반경</div>
    <div class="value">1/12</div>
    <div class="note">조직 전체 → 프로젝트 단위</div>
  </div>
  <div class="stat">
    <div class="label">예상 전환 기간</div>
    <div class="value">8w</div>
    <div class="note">staging 4w + prod 4w</div>
  </div>
  <div class="stat">
    <div class="label">컨테이너화 대상</div>
    <div class="value">7</div>
    <div class="note">프로젝트 수</div>
  </div>
</div>
```

증감 표시:

```html
<div class="stat">
  <div class="label">월간 인시던트</div>
  <div class="value">42</div>
  <span class="delta up">▲ 5건 (전월 대비)</span>
</div>
```

> **상승 ▲ 빨강 / 하락 ▼ 파랑** — 한국 주식 컨벤션. KPI 가 "더 적은 게 좋은" 지표(인시던트, 에러율)면 down=파랑이 개선이라는 의미가 자연스럽다. KPI 의 방향성에 맞게 색 의미를 해석.

---

## 7. Pros / Cons

`.proscons` 컨테이너의 자식에 `.pros` / `.cons` 를 명시해야 색이 입혀진다 (기본은 중립 surface). 양쪽이 의미상 우열이 없는 단순 좌우 비교라면 클래스 없이 두 칸 모두 중립으로 둔다.

```html
<div class="proscons">
  <div class="pros">
    <h4>Pros — Watchtower 채택 시</h4>
    <ul>
      <li>인바운드 포트 개방 불필요 (온프레미스 친화)</li>
      <li>서버 측 자체 polling → CI/CD 와 디커플링</li>
      <li>설정 단순 (Docker label 1줄)</li>
    </ul>
  </div>
  <div class="cons">
    <h4>Cons</h4>
    <ul>
      <li>롤백 자동화 부재 (수동 이전 태그 복원 필요)</li>
      <li>polling 지연 (기본 5분, 즉시 반영 불가)</li>
      <li>다중 인스턴스 동시 배포 보장 안 됨</li>
    </ul>
  </div>
</div>
```

---

## 8. Comparison Table (일반 비교표)

```html
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>옵션</th>
        <th>비용</th>
        <th class="num">속도</th>
        <th>보안</th>
        <th>상태</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>GCP Artifact Registry</strong></td>
        <td>$0.1/GB-월</td>
        <td class="num">빠름</td>
        <td>SA IAM</td>
        <td><span class="badge success">채택</span></td>
      </tr>
      <tr>
        <td>GHCR</td>
        <td>무료 (public)</td>
        <td class="num">중간</td>
        <td>PAT 의존</td>
        <td><span class="badge danger">탈락</span></td>
      </tr>
      <tr>
        <td>Docker Hub</td>
        <td>유료 (private)</td>
        <td class="num">중간</td>
        <td>토큰</td>
        <td><span class="badge muted">미검토</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

---

## 9. Decision Matrix (가중치 점수표)

```html
<div class="table-wrap">
  <table class="decision">
    <thead>
      <tr>
        <th>옵션</th>
        <th class="num">보안 (×3)</th>
        <th class="num">운영 비용 (×2)</th>
        <th class="num">학습 곡선 (×1)</th>
        <th class="num">합계</th>
        <th>판정</th>
      </tr>
    </thead>
    <tbody>
      <tr class="winner">
        <td><strong>GCP AR + Watchtower</strong></td>
        <td class="score">5 (15)</td>
        <td class="score">4 (8)</td>
        <td class="score">3 (3)</td>
        <td class="score">26</td>
        <td><span class="badge success">채택</span></td>
      </tr>
      <tr>
        <td>GHCR + SSH push</td>
        <td class="score">2 (6)</td>
        <td class="score">5 (10)</td>
        <td class="score">4 (4)</td>
        <td class="score">20</td>
        <td><span class="badge danger">탈락</span></td>
      </tr>
      <tr>
        <td>Self-hosted Registry</td>
        <td class="score">4 (12)</td>
        <td class="score">2 (4)</td>
        <td class="score">2 (2)</td>
        <td class="score">18</td>
        <td><span class="badge muted">보류</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

`tr.winner` 클래스로 채택 안을 시각 강조.

---

## 10. Timeline (마일스톤)

```html
<ol class="timeline">
  <li class="item done">
    <div class="when">Week 1 · 완료</div>
    <div class="title">GCP 프로젝트·SA 셋업</div>
    <div class="desc">staging/prod SA 4종 발급, IAM 정책 검토 통과.</div>
  </li>
  <li class="item done">
    <div class="when">Week 2 · 완료</div>
    <div class="title">파일럿 프로젝트 (web-app) 컨테이너화</div>
    <div class="desc">Dockerfile 작성, multi-stage 빌드 적용. 이미지 사이즈 380MB.</div>
  </li>
  <li class="item">
    <div class="when">Week 3 · 진행 중</div>
    <div class="title">GitHub Actions 워크플로우 작성</div>
    <div class="desc">deploy-staging.yml, Infisical 연동.</div>
  </li>
  <li class="item warn">
    <div class="when">Week 4 · 미착수</div>
    <div class="title">example-svc 의존 관계 매핑</div>
    <div class="desc">컨테이너 경계 결정 전 데몬·cron 의존 그래프 명시 필요.</div>
  </li>
  <li class="item danger">
    <div class="when">Week 6 · 차단</div>
    <div class="title">prod 환경 사전 검증</div>
    <div class="desc">대표님 합의 + 다운타임 윈도우 확보 필요.</div>
  </li>
</ol>
```

상태: 기본 (대기) · `.done` (완료, 채움) · `.warn` · `.danger`.

---

## 11. Step List (번호 단계)

```html
<ol class="steps">
  <li>
    <div class="title">사전 분석</div>
    <div class="desc">현재 VM 배포 흐름 문서화, Secrets 인벤토리 작성.</div>
  </li>
  <li>
    <div class="title">파일럿 컨테이너화</div>
    <div class="desc">web-app 1개 프로젝트 선정, Dockerfile + GHA 워크플로우 작성.</div>
  </li>
  <li>
    <div class="title">검증 환경 구축</div>
    <div class="desc">staging VM에 Watchtower 배포, 자동 pull → 재시작 검증.</div>
  </li>
  <li>
    <div class="title">롤아웃</div>
    <div class="desc">나머지 6개 프로젝트 순차 전환, 주당 1~2개 페이스 유지.</div>
  </li>
</ol>
```

---

## 12. AS-IS / TO-BE 좌우 비교

기본은 양쪽 다 중립 surface. AS-IS가 *문제 상황* 이고 TO-BE가 *개선* 일 때만 `.side.danger` / `.side.success` 를 옵트인. 단순한 전후·옵션 A/B 비교라면 색 없이 둔다. 화살표 칸은 모바일에서 자동 숨김.

```html
<!-- 1) 의도가 명확한 경우: 문제 → 개선 -->
<div class="compare">
  <div class="side danger">
    <span class="side-label">AS-IS</span>
    <h4>직접 VM 배포</h4>
    <ul>
      <li>VM 에서 직접 <code>git pull</code></li>
      <li>모든 프로젝트가 같은 파일시스템·환경변수 공유</li>
      <li>Secrets 가 VM 평문 <code>.env</code> 에 존재</li>
      <li>VM 1대 탈취 = 조직 전체 유출</li>
    </ul>
  </div>
  <div class="arrow">→</div>
  <div class="side success">
    <span class="side-label">TO-BE</span>
    <h4>컨테이너 + 격리</h4>
    <ul>
      <li>VM 에 소스 없음, 이미지 pull 만</li>
      <li>컨테이너 간 파일시스템·환경변수 격리</li>
      <li>Secrets 는 빌드 타임 Infisical 주입</li>
      <li>SA 단위 IAM → 프로젝트 1개 영향 한정</li>
    </ul>
  </div>
</div>

<!-- 2) 단순 비교 (의미상 우열 없음) -->
<div class="compare">
  <div class="side">
    <span class="side-label">Option A</span>
    <h4>monorepo</h4>
    <ul><li>...</li></ul>
  </div>
  <div class="arrow">vs</div>
  <div class="side">
    <span class="side-label">Option B</span>
    <h4>polyrepo</h4>
    <ul><li>...</li></ul>
  </div>
</div>
```

선택지: 기본(중립) · `.side.danger` · `.side.success` · `.side.primary`.

---

## 13. Code Block

기본 `<pre><code>` 는 다크 배경. 옵션 토큰으로 syntax highlight 흉내:

```html
<pre><span class="label">deploy-staging.yml</span><code><span class="c-comment"># GitHub Actions 워크플로우</span>
<span class="c-keyword">name</span>: <span class="c-string">deploy-staging</span>
<span class="c-keyword">on</span>:
  <span class="c-keyword">workflow_dispatch</span>:
    <span class="c-keyword">inputs</span>:
      <span class="c-keyword">branch</span>:
        <span class="c-keyword">required</span>: <span class="c-number">true</span>
</code></pre>
```

라벨 없는 단순 코드:

```html
<pre><code>docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower</code></pre>
```

---

## 14. Progress Bar

```html
<div>
  <div class="u-small u-muted">전체 진행률 (4 / 7 프로젝트)</div>
  <div class="progress"><div class="bar" style="width: 57%"></div></div>
</div>

<div>
  <div class="u-small u-muted">Secrets 인벤토리 작성</div>
  <div class="progress warn"><div class="bar" style="width: 30%"></div></div>
</div>
```

색상: 기본(accent) · `.success` · `.warn` · `.danger`.

---

## 15. Checklist (인터랙티브)

```html
<ul class="checklist">
  <li><input type="checkbox" checked id="c1"><span>SA 발급 (sa-web-app-staging-pusher/puller)</span></li>
  <li><input type="checkbox" checked id="c2"><span>Dockerfile 작성 (multi-stage)</span></li>
  <li><input type="checkbox" id="c3"><span>Infisical workspace 생성 + Secrets 이관</span></li>
  <li><input type="checkbox" id="c4"><span>Watchtower 배포 + 동작 검증</span></li>
  <li><input type="checkbox" id="c5"><span>롤백 절차 문서화</span></li>
</ul>
```

체크 시 자동으로 취소선 적용 (base.html의 JS).

---

## 16. Risk Heatmap (3×3 영향 × 확률)

```html
<div class="risk-grid">
  <div class="axis"></div>
  <div class="axis">확률 ↓</div>
  <div class="axis">확률 ↔</div>
  <div class="axis">확률 ↑</div>

  <div class="axis">영향 ↑</div>
  <div class="cell mid">
    <span class="item">Watchtower 다운</span>
  </div>
  <div class="cell high">
    <span class="item">Secrets 누락으로 prod 다운</span>
    <span class="item">의존 그래프 잘못</span>
  </div>
  <div class="cell high">
    <span class="item">롤백 절차 부재</span>
  </div>

  <div class="axis">영향 ↔</div>
  <div class="cell low">
    <span class="item">이미지 사이즈 비대</span>
  </div>
  <div class="cell mid">
    <span class="item">CI 빌드 시간 증가</span>
  </div>
  <div class="cell mid">
    <span class="item">개발자 학습 비용</span>
  </div>

  <div class="axis">영향 ↓</div>
  <div class="cell low">
    <span class="item">로그 포맷 변경</span>
  </div>
  <div class="cell low">
    <span class="item">컨테이너 이름 충돌</span>
  </div>
  <div class="cell mid"></div>
</div>
```

색: `.low` 녹 · `.mid` 황 · `.high` 적.

---

## 17. Q&A Toggle (FAQ 접힘)

```html
<details class="qa">
  <summary>왜 GHCR 가 아니라 GCP Artifact Registry 인가?</summary>
  <div>
    <p>GitHub App Installation Token 이 GHCR pull 을 지원하지 않아, 서버에서 이미지를 pull 할 때 개인 PAT 의존이 발생한다. 이는 최소권한 원칙 위배. GCP AR + SA JSON 키 조합은 repo 단위 IAM 격리가 가능해 SA 유출 시 영향 범위를 1개 프로젝트로 제한할 수 있다.</p>
  </div>
</details>

<details class="qa">
  <summary>Watchtower polling 주기는?</summary>
  <div>
    <p>기본 5분. 운영계는 <code>WATCHTOWER_POLL_INTERVAL=300</code> 으로 명시. 즉시 배포가 필요한 경우 컨테이너에 SIGUSR1 시그널로 강제 트리거.</p>
  </div>
</details>
```

---

## 17.5 독자 보조 레이어 (Term · Primer · Glossary)

독자 이해도가 낮을 수 있는 용어·개념을 **본문 흐름을 해치지 않고** 보강하는 3종 세트. 본문은 간결하게 두고, 깊이는 이 레이어로 분리한다 — 전문가는 본문만 빠르게 읽고, 초보는 펼쳐서 깊이를 얻는다. 한 보고서가 두 독자를 동시에 만족시키는 핵심 장치. **언제 쓰는지의 판단 기준은 SKILL.md "독자 이해도 추론" 단계 참조.**

### (a) Term — 인라인 용어 힌트

본문 중 한 번 짚고 넘어가면 되는 용어. 점선 밑줄 + hover 툴팁. 마우스 hover/인쇄에서 툴팁이 안 보일 수 있으니 **정본 정의는 반드시 하단 glossary 에도 등재**한다 (term 은 가벼운 힌트, glossary 가 정본).

```html
<p>주문 체결 후 <span class="term" title="결제일. 거래 성립일로부터 2영업일 뒤 실제 대금·증권이 오가는 날">T+2</span> 에 정산이 일어난다.</p>
```

> 짧은 약어·축약 1~2개에만. 한 문단에 term 이 3개 넘으면 본문이 누더기가 된다 — 그럴 땐 primer 또는 glossary 로.

### (b) Primer — 접이식 배경지식

한두 문장으로 안 끝나는 개념(아키텍처 패턴, 도메인 메커니즘 등)을 **펼침 박스**로. summary 앞에 "배경지식" 배지가 자동으로 붙고 좌측에 primary accent bar. 전문가는 접힌 채 지나가고, 모르는 독자만 펼친다. 본문 흐름 중간에 자연스럽게 삽입.

```html
<details class="primer">
  <summary>동시호가가 무엇이고 왜 별도 처리가 필요한가</summary>
  <div>
    <p>동시호가는 장 시작(08:30~09:00)·장 마감(15:20~15:30) 구간에 주문을 즉시 체결하지 않고 모았다가, 단일 가격으로 한꺼번에 체결하는 방식이다. 일반 연속매매와 체결 로직이 달라 주문 처리 코드에서 분기가 필요하다.</p>
    <ul>
      <li>일반 시간: 들어온 주문을 가격·시간 우선으로 즉시 체결</li>
      <li>동시호가: 주문을 큐에 쌓아두고 구간 종료 시 단일가로 일괄 체결</li>
    </ul>
  </div>
</details>
```

> primer 안에는 `<p>`·`<ul>`·`<pre>` 등 자유롭게. 단 primer 가 본문보다 길어지면 본론과 배경이 뒤집힌 것 — 별도 섹션으로 빼는 걸 고려.

### (c) Glossary — 하단 용어집

보고서에 등장한 도메인·기술 용어를 **footer 직전**에 모아 정의. term 툴팁이 인쇄·정독에서 사라지는 걸 보완하는 정본. `<dl>` 기반 2열 grid (모바일 1열 자동 전환).

```html
<section id="glossary">
  <h2>용어집</h2>
  <dl class="glossary">
    <dt>T+2</dt>
    <dd>결제일(Settlement Date). 거래 성립일(T)로부터 2영업일 뒤, 실제 대금과 증권의 소유권이 이전되는 날. 한국·미국 주식 현물 기준.</dd>
    <dt>동시호가</dt>
    <dd>장 시작·마감 구간에 주문을 모아 단일 가격으로 일괄 체결하는 방식. 연속매매와 체결 로직이 다르다.</dd>
    <dt>증거금</dt>
    <dd>신용·미수 거래 시 예치해야 하는 보증금. 종목별 증거금률에 따라 매수 가능 금액이 정해진다.</dd>
  </dl>
</section>
```

> 용어집은 TOC 에도 자동 등재된다 (`<section id>` + `<h2>` 쌍). **용어 3개 미만이면 term/primer 로만, 3개 이상이면 glossary 섹션** — SKILL.md 3단계 기준과 동일.

---

## 17.7 Formula & Worked Example (수식 · 숫자 예시)

Methodology·Explainer 타입의 핵심 컴포넌트. 외부 수식 렌더러(KaTeX 등) 없이 **mono 선형 표기**로 쓴다 — CDN 의존을 늘리지 않고, 복사-붙여넣기도 된다.

### (a) Formula — 수식 블록

`white-space: pre-wrap` 이므로 수식 안 공백·줄바꿈이 그대로 보존된다. 아래첨자는 `<sub>`, 위첨자는 `<sup>`, 인라인 주석은 `.fx-comment`, 강조 항은 `.fx-hl`.

```html
<div class="formula">지수(오늘) = 지수(직전 리밸런싱일) × Σ [ w<sub>i</sub> × P<sub>i</sub>(오늘) ÷ P<sub>i</sub>(리밸런싱일) ]  <span class="fx-comment">— 체인 방식</span></div>
<dl class="formula-where">
  <dt>w<sub>i</sub></dt><dd>종목 i 의 비중 (합 = 1)</dd>
  <dt>P<sub>i</sub>(t)</dt><dd>종목 i 의 t 시점 수정주가</dd>
</dl>
```

> 그리스 문자·연산 기호는 유니코드 직접 사용: Σ Π √ × ÷ ± ≤ ≥ ≠ ≈ Δ σ μ α β. 분수는 `a ÷ b` 또는 `a / b` 선형 표기 — 세로 분수를 흉내내려 하지 말 것.

### (b) Worked Example — 숫자 예시 박스

추상 정의·수식을 **실제 값으로 한 번 굴려** 보여주는 박스. 독자가 손으로 따라 계산해 같은 답이 나오는 수준으로 쓴다. 라벨 텍스트는 자유 ("숫자 예시", "구체 예시", "따라 해보기" 등).

```html
<div class="example">
  <span class="label">숫자 예시</span>
  <p>종목 3개(비중 0.5 / 0.3 / 0.2), 리밸런싱일 대비 각각 +2%, −1%, +5% 움직였다면:</p>
  <div class="formula">지수 = 100 × (0.5×1.02 + 0.3×0.99 + 0.2×1.05) = 100 × 1.017 = 101.7</div>
  <p class="u-small u-muted">비중이 큰 종목의 등락이 지수에 더 크게 반영된다.</p>
</div>
```

> `.example` 안의 `.formula` 는 배경이 한 단계 밝게 자동 조정된다. Methodology 에서는 **정의 → 수식 → 숫자 예시** 3종 세트로 반복 사용 (report-types.md §8 참조).

---

## 18. Mermaid Diagram

`base.html` 에 mermaid CDN 이 이미 포함되어 있다. 다이어그램은 `.mermaid-wrap > .mermaid` 안에 작성.

```html
<div class="mermaid-wrap">
  <div class="mermaid">
flowchart LR
    A[GitHub Actions] -->|build| B[Docker Image]
    B -->|push| C[GCP Artifact Registry]
    D[VM · Watchtower] -->|poll| C
    C -->|pull| D
    D -->|restart| E[App Container]
  </div>
  <div class="caption">그림 1. 컨테이너 빌드 → 배포 흐름</div>
</div>
```

다이어그램 종류:
- `flowchart` — 시스템 흐름
- `sequenceDiagram` — 시간순 상호작용
- `gantt` — 일정
- `classDiagram` — 데이터 모델
- `stateDiagram-v2` — 상태 전이
- `erDiagram` — DB ER

**⛔ 다이어그램 소스 작성 규칙 (어기면 "Syntax error in text" 폭탄 박스)**:

1. **`<` `>` 는 반드시 `&lt;` `&gt;` 로 이스케이프.** `.mermaid` 안 소스는 HTML 파서를 먼저 통과하므로 raw `<` 는 태그로 오인돼 소스가 손상된다. classDiagram 의 `<<interface>>`, 라벨 속 `x < 10`, 제네릭 `List<T>` 가 대표적 피해자.
   - ❌ `class Runner { <<interface>> }` → ✅ `class Runner { &lt;&lt;interface&gt;&gt; }`
   - ❌ `A -->|x < 10| B` → ✅ `A -->|x &lt; 10| B`
2. **라벨 안 줄바꿈**도 같은 이유로 `&lt;br/&gt;` 로 쓴다 (raw `<br/>` 는 렌더 전 소멸).
3. **`<details>`(primer·qa) 안에 mermaid 를 넣으면** 접힌 상태에서 크기 0으로 렌더된다. base.html 이 펼칠 때 자동 재렌더하지만, 가능하면 다이어그램은 본문에 배치.
4. 문법 오류 시 페이지에 빨간 에러 박스가 노출된다. **작성 후 브라우저로 한 번은 열어 콘솔까지 확인할 것** (SKILL.md 5단계 검증 항목).

---

## 19. Footer

```html
<footer class="report-footer">
  <span>인프라 컨테이너화 전환 큰그림 · 2026-05-11</span>
  <span>v0.5 · Example Author</span>
</footer>
```

---

## 컴포넌트 조합 패턴 (자주 나오는 형태)

### 결정 보고 패턴 (Tech Investigation)
1. TL;DR (결론)
2. 컨텍스트 (Callout note)
3. 옵션별 Card grid (3개)
4. Decision Matrix (점수)
5. 채택안의 Pros/Cons
6. Callout danger (트레이드오프)

### 큰그림 패턴 (Analysis)
1. TL;DR
2. AS-IS / TO-BE 좌우 비교
3. Stat KPI 3개 (변화 수치)
4. Architecture Mermaid 다이어그램
5. Step List (전환 단계)
6. Risk Heatmap
7. Timeline (마일스톤)

### 작업 계획 패턴 (Task Plan)
1. TL;DR
2. 컨텍스트
3. 접근 옵션 카드
4. 선택안 + 근거 (Callout info)
5. Step List
6. Checklist (작업 항목)
7. Timeline (마일스톤)
8. Risk Heatmap

### 방법론 패턴 (Methodology)
1. TL;DR
2. 전체 파이프라인 Mermaid (`flowchart LR`)
3. 기호 표 (table)
4. **[말 정의 → Formula → Worked Example → Callout warn(경계 조건)] 을 계산 단계 수만큼 반복**
5. 변형 비교 Decision Matrix
6. Glossary

### 해설 패턴 (Explainer)
1. TL;DR (답하는 질문)
2. Callout note (비유)
3. 멘탈 모델 Mermaid + Card grid (구성요소)
4. Step List (동작 순서) + Worked Example
5. Compare (오해 → 실제)
6. 치트시트 table + Glossary

### 가이드 패턴 (Guide)
1. TL;DR (N단계 · M분)
2. Checklist (전제 조건) + 플레이스홀더 table
3. Step List — 단계마다 `<pre><code>` + "예상 결과"
4. Checklist (완료 검증)
5. 트러블슈팅 table

---

## 새 컴포넌트 추가 절차

1. 정말 필요한지 검토 — 기존 컴포넌트 조합으로 안 되는지 확인
2. `base-css.md` 에 CSS 추가 (디자인 토큰 사용, 새 색·임의 px 금지)
3. `base.html` 의 `<style>` 인라인 블록에 같은 CSS 추가
4. 이 파일에 HTML 스니펫 + 사용 시점 추가
5. Quick Reference 표 갱신
