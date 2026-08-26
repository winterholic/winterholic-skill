# biz-experts — 비엔지니어링 직군 전문가 스킬군

제품을 만들고 키우는 데 필요한 **비개발 직군**(제품·디자인·마케팅·사업·운영·세일즈·피플)을 직무 단위로 세분화한 52종(전문가 51 + 라우터 1) 체계.
단일 범용 스킬 대신, 각자 거장/원전 앵커와 안티패턴 카탈로그를 갖춘 전문가를 미리 만들어두고 꺼내 쓴다.

> **설계 근거**: `~/.claude\biz-experts-plan.md` (결정 §0 · 카탈로그 §4 · DoD §6 · 파이프라인 §7 · Phase §8).
> **진행표(SSOT)**: `~/.claude\biz-experts-progress.md`.
> **품질 기준점**: dev-experts(92종)·stock-experts(21종)·life-experts(34종)에서 검증된 제작 공식의 이식.

## 이 폴더의 성격

- **자동 로드되지 않는 전용 폴더**다. 51개 description이 매 세션 컨텍스트를 점유하는 것을 피하기 위함. 글로벌엔 디스패처 1개만 상주.
- 사용하려면: ① 라우터 `biz-chief-strategist/SKILL.md`를 먼저 Read해 어떤 전문가를 부를지 정하고 ② 해당 전문가 `SKILL.md`를 Read해 그 매뉴얼대로 작업한다. (직무가 이미 명확하면 직행)
- **전역 디스패처**: `~/.claude/skills/biz-experts/SKILL.md`가 설치되어 있어, 일반 세션에서 비개발 직군 작업이 나오면 이 폴더로 자동 라우팅된다.
- 본문의 `[[이름]]`은 이 스킬군 내 다른 SKILL/레퍼런스를, `(→ biz-x)`는 해당 전문가로의 위임을 가리킨다. `(→ dev-x)`/`(→ life-x)`/`(→ stock-x)`는 다른 컬렉션 위임.
- 개별 스킬을 자주 쓰게 되면 그 폴더만 글로벌 `skills/`로 승격한다.

## 제1원칙 — 우선순위 사다리 (모든 스킬 적용)

```
프로젝트 CLAUDE.md·프로젝트 스킬 > 이 스킬군의 전문가 > LLM 일반 지식
```

프로젝트별 컨벤션이 전문가 일반론과 충돌하면 **항상 프로젝트 규칙이 이긴다**. 전문가 스킬은 프로젝트 규칙이 침묵하는 영역만 채운다. 충돌이 알려진 안티패턴일 때만 한 줄로 지적(무단 변경 금지).

## 도메인 경계 (다른 컬렉션과)

| biz-experts | 다른 컬렉션 |
|---|---|
| 직무로서 제품을 만들고 파는 일 | 코드 작성·시스템 설계 (→ dev-experts) |
| 사업·제품 의사결정 | 개인 일상 재무·세무·법률 (→ life-experts) |
| 가격·수익화 전략 | 주식 투자 분석·종목 판단 (→ stock-experts) |
| 마케팅 SEO·콘텐츠 전략 | SEO 기술 구현·메타태그·sitemap (→ dev-seo-analytics) |
| UX 라이팅·마이크로카피 | API 문서·기술 문서 (→ dev-tech-writing) |
| 비즈니스 데이터 분석·지표 정의 | pandas·EDA 코드 (→ dev-data-analysis) |

## 공통 규칙 (모든 스킬 적용)

1. **버전 라벨 의무**: 모든 스킬은 frontmatter 직하에 `> 기준: <영역> (YYYY-MM)`. 채널·플랫폼 정책·툴은 부패가 빠르다 — 스킬은 **원칙·함정 위주**, 버전/정책 의존 세부는 공식 문서·플랫폼 정책이 이긴다.
2. **안티패턴 우선**: 잘 하는 법은 LLM이 안다. 스킬의 가치 절반은 ❌/✅ 안티패턴 카탈로그(스킬당 5쌍 이상)에 있다.
3. **거장 앵커 의무**: 각 스킬은 그 분야의 원전/거장을 명시(Cagan·Torres·Sharp·Ogilvy·Grove·Norman 등). 일반론이 아니라 그 거장이 실제 가르치는 기준·함정을 박는다.
4. **사후 채점(결정의 검증 가능성)**: biz 결정은 결과가 늦게 온다. 모든 산출물에 **가설 · 성공지표 · 언제 확인할지**를 명시하게 한다(stock-scorecard 철학 이식). 큰 결정은 선택적으로 `decisions-ledger.md`에 복기.
5. **불확실 수치는 "확인 필요"**: 벤치마크·전환율·플랫폼 수수료·정책은 변한다. 확신 없는 값은 추측으로 메우지 않고 "확인 필요" + 출처 경로.
6. **윤리 게이트(거부권급)**: 마케팅(과장·다크패턴), HR(차별), 가격(담합), 투자유치(허위표시), 리서치(유도질문)에는 "하지 말 것"을 명시. 기만적 다크패턴·허위 마케팅은 기능 요구가 급해도 거부권급으로 경고.
7. **경로 표기**: 스킬 내부 참조는 상대 경로 + 슬래시(`references/x.md`, `scripts/calc.py`). 폴더 밖을 가리킬 때만 절대 경로.
8. **참조 깊이 1단계**: SKILL.md → references/*.md 까지만. 100줄 넘는 레퍼런스는 맨 위에 목차.

## 공통: 빠른 사용 (Quick Start)

1. **라우터부터** — `biz-chief-strategist/SKILL.md`를 읽어 작업을 [기능 × 단계 × 산출물 × 지표]로 분해, 전문가 1~3명을 고른다. (직무가 명확하면 직행)
2. **그 전문가 SKILL.md의 "워크플로우 + 안티패턴"** 만 따라 바로 작업한다. 심화는 `references/`로.
3. **막히거나 큰 결정이면** `decisions-ledger.md`를 확인 — 비슷한 결정의 복기가 있을 수 있다.

## 사후 채점 — biz판 "같은 실수 두 번 안 하기"

코드와 달리 마케팅·전략·제품 결정은 결과가 수주~수개월 뒤에 온다. 그래서:

- 되돌리기 어려운 큰 결정(가격 변경·리브랜딩·핵심 기능 방향·캠페인 예산)을 내리면 `decisions-ledger.md`에 1행 추가(append-only):
  `| 날짜 | 영역 | 결정 | 가설 | 성공지표 | 확인 시점 | 결과(나중에) |`
- 확인 시점이 지나면 결과를 채우고, **틀린 가설이 같은 유형으로 반복되면** 해당 스킬의 안티패턴에 추가.

## 시효성 관리 — 부패 속도 3등급

| 등급 | 대상 | 점검 |
|---|---|---|
| **빠름** | performance-marketing, social-media, aso, ai-product-pm | 플랫폼 정책·채널·툴은 항상 공식 문서 우선. 분기 라벨 점검 |
| **중간** | growth-marketing, product-analytics, seo-marketing, fundraising, pricing | 반기 — 벤치마크 수치·프레임 업데이트 |
| **느림** | product-manager, ux-designer, copywriter, brand-marketing, management, business-strategy | 연 1회 — 거장 원칙은 오래 간다 |

## 2계층 스펙

- **풀스펙**: frontmatter 트리거 10+ · 경계 표 3행+ · 안티패턴 5쌍+ · 정량/프레임 기준표 · 워크플로우+출력 템플릿+예시 · 실전 케이스(실제 실패) · scripts 1+(계산 가능시·실행 검증) · references 2~3겹 · 한계/윤리 섹션 · 거부 처리 · skills-estimate 85+.
- **코어스펙**: SKILL.md(안티패턴 5쌍 + 프레임 기준 + 워크플로우 + 출력 템플릿 + 거부 처리) + `references/evidence.md` 1겹. scripts 생략 가능. 실사용 시 풀스펙 승격.

DoD 전문: `biz-experts-plan.md` §6. 제작 템플릿: `_template/SKILL-template.md`.

## 전문가 카탈로그 (51 + 라우터 1)

> 상태: ✅ 제작됨 · ⬜ 미제작. **⬜ 스킬은 Read 시도 금지** — 일반 지식 + 거장 원칙 + 공식 자료로 진행. 진행 상태 원본은 `biz-experts-progress.md`.

### 라우터
| 스킬 | 역할 | 상태 |
|---|---|---|
| biz-chief-strategist | 작업 분해 → 전문가 1~3 조합·조율 (CPO/CMO 겸 트리아지) | ✅ |

### A. 프로덕트 매니지먼트·기획 (9)
| 스킬 | 거장/원전 앵커 | 상태 |
|---|---|---|
| biz-product-manager | Marty Cagan *INSPIRED*·SVPG | ✅ |
| biz-product-discovery | Teresa Torres *Continuous Discovery Habits* | ✅ |
| biz-product-strategy | Cagan *EMPOWERED*·Rumelt *Good Strategy Bad Strategy* | ✅ |
| biz-growth-pm | Reforge·Sean Ellis·Brian Balfour | ✅ |
| biz-service-planner | 한국형 서비스 기획(화면설계서/정책서/IA) | ✅ |
| biz-prd-writing | Cagan·아마존 PR/FAQ·Shape Up | ✅ |
| biz-product-analytics | Amplitude/Mixpanel·HEART·AARRR | ✅ |
| biz-b2b-saas-pm | *Lean B2B*·SaaS 메트릭 | ✅ |
| biz-ai-product-pm | LLM 제품 패턴·eval·HCI | ✅ |

### B. 디자인 (13)
| 스킬 | 앵커 | 상태 |
|---|---|---|
| biz-ux-designer | Don Norman *DOET*·Cooper·니엘슨 휴리스틱 | ✅ |
| biz-ui-designer | *Refactoring UI* | ✅ |
| biz-ux-researcher | Nielsen Norman·*Just Enough Research* | ✅ |
| biz-product-designer | end-to-end 제품 디자인·Figma | ✅ |
| biz-design-system | Brad Frost *Atomic Design*·디자인 토큰 | ✅ |
| biz-service-designer | *This is Service Design*·저니맵/블루프린트 | ✅ |
| biz-brand-designer | 브랜드 아이덴티티·가이드라인 | ✅ |
| biz-graphic-designer | 편집·그리드·키비주얼 | ✅ |
| biz-motion-designer | 모션 원칙·Lottie/AE | ✅ |
| biz-3d-designer | 3D 모델링/렌더링·PBR | ✅ |
| biz-3d-character-artist | 3D 캐릭터(스컬핑/리토폴/리깅) | ✅ |
| biz-illustrator | 일러스트레이션 | ✅ |
| biz-ux-writer | Podmajersky·마이크로카피 | ✅ |

### C. 마케팅·그로스 (12)
| 스킬 | 앵커 | 상태 |
|---|---|---|
| biz-growth-marketing | Sean Ellis *Hacking Growth*·AARRR | ✅ |
| biz-performance-marketing | Meta/Google Ads·ROAS/MER | ✅ |
| biz-content-marketing | *They Ask You Answer* | ✅ |
| biz-seo-marketing | 검색 의도·E-E-A-T (마케팅 측) | ✅ |
| biz-brand-marketing | Byron Sharp *How Brands Grow* | ✅ |
| biz-product-marketing | April Dunford *Obviously Awesome* | ✅ |
| biz-social-media | 채널 알고리즘·커뮤니티 | ✅ |
| biz-crm-lifecycle | 라이프사이클·이메일·세그먼트 | ✅ |
| biz-copywriter | Ogilvy·Eugene Schwartz | ✅ |
| biz-pr-comms | PR·위기관리·보도자료 | ✅ |
| biz-marketing-analytics | 어트리뷰션·MMM·incrementality | ✅ |
| biz-aso | 앱스토어 최적화 | ✅ |

### D. 사업·전략·경영 (10)
| 스킬 | 앵커 | 상태 |
|---|---|---|
| biz-cto | 기술 리더십(비코딩)·조직/전략 | ✅ |
| biz-ceo-founder | Thiel *Zero to One*·Ries *Lean Startup* | ✅ |
| biz-business-strategy | Porter·Rumelt·BCG/McKinsey 프레임 | ✅ |
| biz-fundraising | YC·*Venture Deals* | ✅ |
| biz-finance-fpa | 유닛이코노믹스·번레이트·런웨이 | ✅ |
| biz-pricing-monetization | *Monetizing Innovation* | ✅ |
| biz-business-development | 제휴·파트너십·채널 | ✅ |
| biz-okr-goals | John Doerr *Measure What Matters* | ✅ |
| biz-management | Andy Grove *High Output Management* | ✅ |
| biz-go-to-market | GTM 모션(PLG/SLG) | ✅ |

### E. 운영·고객·세일즈·피플 (7)
| 스킬 | 앵커 | 상태 |
|---|---|---|
| biz-sales | *The Challenger Sale*·SPIN·MEDDIC | ✅ |
| biz-customer-success | *Customer Success*(Mehta)·NRR | ✅ |
| biz-customer-support | 지원 운영·SLA·CSAT | ✅ |
| biz-community | 커뮤니티 빌딩·SPACES | ✅ |
| biz-people-hr | 채용·온보딩·조직설계 | ✅ |
| biz-business-ops | RevOps·프로세스·툴스택 | ✅ |
| biz-data-analyst | 비즈니스 분석·대시보드·지표 정의 | ✅ |
