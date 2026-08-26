# biz-chief-strategist — 라우팅 매트릭스 & eval

> 전문가 51종 색인 + 상호 호출 관계 + 라우팅 평가(eval). 라우팅이 애매할 때, 새 작업 유형이 들어올 때 grep. 1단계 참조.

## 전문가 51종 색인 (작업 키워드 → 전문가)

### A. 프로덕트·기획
- 기능 우선순위·로드맵·output/outcome → biz-product-manager
- 사용자 문제 발견·인터뷰·기회트리 → biz-product-discovery
- 제품 비전·전략·집중 → biz-product-strategy
- 제품 주도 성장·성장모델·PLG → biz-growth-pm
- 화면설계서·정책정의서·IA(한국형) → biz-service-planner
- PRD·스펙·유저스토리·PR/FAQ → biz-prd-writing
- 제품 지표·퍼널·코호트·HEART → biz-product-analytics
- B2B SaaS 제품(구매자≠사용자) → biz-b2b-saas-pm
- AI/LLM 제품·eval·환각UX → biz-ai-product-pm

### B. 디자인
- UX 플로우·사용성·휴리스틱 → biz-ux-designer
- UI 비주얼·위계·타이포·간격 → biz-ui-designer
- 사용자 리서치·방법·편향 → biz-ux-researcher
- end-to-end 제품 디자인·리디자인 → biz-product-designer
- 디자인 시스템·토큰·아토믹 → biz-design-system
- 서비스 여정·블루프린트 → biz-service-designer
- 로고·브랜드 아이덴티티 → biz-brand-designer
- 포스터·배너·편집·키비주얼 → biz-graphic-designer
- 모션·마이크로인터랙션·Lottie → biz-motion-designer
- 3D 제품·환경·PBR·렌더 → biz-3d-designer
- 3D 캐릭터·토폴로지·리깅 → biz-3d-character-artist
- 일러스트·마스코트(2D)·스타일 → biz-illustrator
- 버튼/에러/빈상태 문구·마이크로카피 → biz-ux-writer

### C. 마케팅·그로스
- 그로스 실험·AARRR·바이럴 → biz-growth-marketing
- 유료 광고·ROAS·퍼포먼스 → biz-performance-marketing
- 콘텐츠 전략·블로그·깔때기 → biz-content-marketing
- SEO 의도·키워드·E-E-A-T(마케팅) → biz-seo-marketing
- 브랜드 전략·도달·정신적 가용성 → biz-brand-marketing
- 포지셔닝·메시징·런칭(PMM) → biz-product-marketing
- SNS·채널·커뮤니티 마케팅 → biz-social-media
- CRM·라이프사이클·이메일 → biz-crm-lifecycle
- 카피·헤드라인·랜딩 문구 → biz-copywriter
- PR·언론·위기관리 → biz-pr-comms
- 어트리뷰션·증분성·MMM → biz-marketing-analytics
- 앱스토어 최적화 → biz-aso

### D. 사업·전략·경영
- 기술 조직 전략·build vs buy(비코딩) → biz-cto
- 창업·PMF·피벗 → biz-ceo-founder
- 산업 구조·경쟁·해자 → biz-business-strategy
- 투자 유치·피치덱·텀시트 → biz-fundraising
- 단위경제·번레이트·런웨이 → biz-finance-fpa
- 가격·요금제·수익화 → biz-pricing-monetization
- 제휴·파트너십·채널 → biz-business-development
- OKR·목표 설정 → biz-okr-goals
- 1:1·피드백·조직 매니지먼트 → biz-management
- 시장 진입 모션·PLG/SLG → biz-go-to-market

### E. 운영·고객·세일즈·피플
- B2B/SaaS 세일즈·SPIN/MEDDIC → biz-sales
- 고객 성공·갱신·NRR → biz-customer-success
- 고객 지원·티켓·SLA → biz-customer-support
- 커뮤니티 빌딩·SPACES → biz-community
- 채용·온보딩·조직설계 → biz-people-hr
- 프로세스·RevOps·툴스택 → biz-business-ops
- 비즈 데이터·지표·대시보드 → biz-data-analyst

## 자주 묶이는 조합 (multi-expert)

- **신규 기능 런칭**: product-manager(무엇) + product-marketing(포지셔닝) + copywriter(문구) + (가격이면) pricing
- **신제품 기획→출시**: product-discovery(문제) → product-strategy(방향) → prd-writing(스펙) → product-designer(설계) → go-to-market(진입)
- **유입 안 늘어**: growth-marketing(깔때기 진단) → 새는 단계가 활성화면 product-analytics+ux-designer / 획득이면 performance-marketing or seo/content
- **이탈 많아**: product-analytics(코호트) → 원인이 가치면 product-discovery / 온보딩이면 ux+growth-pm / 고객이면 customer-success
- **디자인 전체**: product-designer(전과정) ↔ ux-designer(사용성)·ui-designer(비주얼)·design-system(시스템)·ux-writer(문구)
- **창업 초기**: ceo-founder(집중) + product-discovery(PMF) + finance-fpa(런웨이) + (자금이면) fundraising
- **B2B 제품**: b2b-saas-pm + customer-success + sales + go-to-market

## 다른 컬렉션 위임

- 코드·구현·시스템 설계 → dev-experts
- 주식 투자 분석·종목 판단 → stock-experts
- 개인 일상 재무·세무·법률 → life-experts
- SEO 기술 구현(메타·schema·CWV) → dev-seo-analytics
- API 문서·기술 문서 → dev-tech-writing
- pandas·SQL·파이프라인 → dev-data-analysis/dev-data-engineering
- 협상 기법 일반 → life-negotiation
- 근로 분쟁·계약 법률 → life-legal(변호사·노무사)

## 라우팅 평가 (eval — 새 Phase·수정 시 재실행)

각 문항: 올바른 무게중심 전문가를 1~3명 골랐는가?

1. "이 기능 만들까 말까, 우선순위" → product-manager (✅ RICE·outcome)
2. "사용자가 왜 이탈하는지 모르겠어" → product-discovery/product-analytics (❌ 바로 기능 추가 금지)
3. "랜딩 페이지 문구랑 구조" → copywriter (+ ux-writer/product-marketing) (❌ ui-designer 단독 아님)
4. "온보딩 화면 기획" → service-planner/ux-designer (❌ 코드=dev)
5. "광고 ROAS 좋은데 예산 늘릴까" → performance-marketing (✅ 증분성·단위경제)
6. "가격 얼마로" → pricing-monetization (+ finance-fpa) (❌ 경쟁가 추종 경고)
7. "투자 받는데 밸류 높으면 좋은가" → fundraising (✅ 텀·희석 경고)
8. "3D 캐릭터 만들기" → 3d-character-artist (❌ 3d-designer 아님 — 캐릭터 특화)
9. "팀원 저성과 어떻게" → management (❌ 바로 해고 경고, people-hr 협의)
10. "지표 대시보드" → data-analyst/product-analytics (❌ 결정 질문 먼저)

> 오라우팅이 반복되면 이 색인·조합 표를 수정하고 해당 문항을 갱신한다.

---

## 발화 신호 → 전문가 매핑 (표층어에 속지 않기)

라우팅 오류의 대부분은 **사용자가 쓴 단어**와 **실제 무게중심 직무**가 어긋날 때 난다. 아래는 "겉보기 단어 → 잘못 끌리는 전문가 → 실제 무게중심" 교정표다.

| 사용자 발화 신호 | 순진하게 끌리는 곳 | 실제 무게중심 | 판별 질문 |
|---|---|---|---|
| "랜딩페이지 만들어줘" | ui-designer / service-planner | **의도에 따라 분기**: 문구가 핵심이면 copywriter, 전환구조면 product-marketing, 화면 자체면 ux/ui | "지금 없는 게 카피냐 화면이냐 유입이냐?" |
| "우리 제품 안 팔려" | sales / performance-marketing | **PMF 여부 먼저**: PMF 전이면 product-discovery, PMF 후 유입이면 growth, 딜이 안 닫히면 sales | "쓰던 사람이 재방문하나?(PMF 신호)" |
| "브랜딩 좀 해줘" | brand-designer(로고) | **로고냐 전략이냐**: 시각 아이덴티티=brand-designer, 인지·포지셔닝=brand-marketing/product-marketing | "지금 필요한 게 로고 파일이냐 시장에서의 자리냐?" |
| "데이터 좀 봐줘 / 대시보드" | data-analyst 즉답 | **결정 질문이 먼저**: 무슨 의사결정을 위한 지표인지 없으면 지표부터 정의(product-analytics+okr-goals) | "이 숫자로 뭘 결정하려 하나?" |
| "AI 기능 넣자" | ai-product-pm 즉답 | 맞다. 단 **환각·eval·신뢰 UX**가 핵심이지 모델 선택(=dev-experts) 아님 | "실패했을 때 사용자가 어떻게 아나?" |
| "가격 올리자/내리자" | pricing 즉답 | pricing 맞으나 **되돌리기 어려운 결정**이라 finance-fpa(단위경제)와 항상 동반 | "기존 고객 반응·해지율을 어디서 보나?" |
| "팀이 삐걱거려" | management 즉답 | 1:1·피드백=management, 채용·조직설계·보상=people-hr — **성과 vs 구조** 구분 | "사람 문제냐 구조·롤 문제냐?" |
| "CS가 너무 많아" | customer-support 즉답 | 티켓 처리=support지만 **근본 원인이 제품**이면 product-analytics로 역류시켜야 | "같은 문의가 반복되나(제품 결함 신호)?" |
| "SEO 해줘" | seo-marketing | 콘텐츠·의도·E-E-A-T=seo-marketing / **메타·schema·CWV 기술구현=dev-seo-analytics로 위임** | "글·키워드냐 태그·속도냐?" |
| "협상 자료" | business-development | 사업 제휴 협상=business-development / **개인 근로·계약 협상=life-experts** | "회사 대 회사냐 개인이냐?" |

> 핵심 원칙: **명사가 아니라 결정(decision)을 라우팅한다.** 사용자가 요청한 산출물 이름(랜딩·대시보드·로고)은 껍데기다. "이걸로 무슨 결정을 내리려 하는가"를 1회 되물으면 무게중심이 드러난다.

## 경계 케이스 처리 (애매할 때의 규칙)

- **단일 직무 명확한데 라우터가 발동됐다** → 즉시 해당 전문가로 직행. 라우터는 조율할 게 없으면 물러난다(과호출·과설계 금지).
- **두 전문가가 같은 강도로 당긴다** → 무게중심 = "실패 시 가장 크게 잃는 쪽". 예: 런칭에서 카피가 어설퍼도 회복 가능하지만 포지셔닝이 틀리면 캠페인 전체가 헛발 → product-marketing이 무게중심, copywriter는 보강.
- **단계가 서로 다른 요구가 충돌** → 충돌 아님. 되돌리기 쉬운 것 먼저(빠르게), 어려운 것(가격·리브랜딩·조직개편)은 검증 후. 단계로 분리해 제시.
- **카탈로그에 없는 영역**(하드웨어 산업디자인, 순수 오프라인 리테일 운영, 법인 세무회계 등) → 폴백 선언(거장 원칙+공식 자료) + 그 사실 1줄 고지. 인접 전문가로 억지 라우팅 금지.
- **경계에 걸친 위임 대상** → 코드=dev-experts / 투자판단=stock-experts / 개인 일상=life-experts. biz는 "무엇을·왜"까지, "어떻게 구현"은 넘긴다.
- **⬜(미제작) 전문가로 라우팅됨** → Read 시도하지 말고 폴백. 상태는 항상 `../README.md`가 원본.

## 조합 사례 — 순서와 핸드오프 (cross-domain 시나리오)

각 조합은 **호출 순서**가 핵심이다(잘못된 순서 = 헛수고). "→"는 산출물 핸드오프.

| 시나리오 | 순서 (무게중심 굵게) | 핸드오프 포인트 · 게이트 |
|---|---|---|
| **신규 유료 기능 런칭** | product-discovery(수요검증) → **product-marketing**(포지셔닝) → pricing-monetization(가격) → copywriter(문구) → go-to-market(채널) | 포지셔닝 확정 전엔 카피 쓰지 말 것. 가격은 finance-fpa로 단위경제 게이트 통과 후 확정 |
| **"유입이 안 늘어"** | **growth-marketing**(AARRR 깔때기 진단) → 병목이 획득이면 performance/seo/content, 활성화면 product-analytics+ux-designer, 재방문이면 crm-lifecycle | 어느 단계가 새는지 진단 전에 채널부터 늘리지 말 것 |
| **"이탈이 심해"** | **product-analytics**(코호트로 언제·누가) → 원인이 가치면 product-discovery, 온보딩이면 ux-designer+growth-pm, 고객관리면 customer-success | "왜 떠나는지" 없이 리텐션 기능부터 만들지 말 것 |
| **시드 투자 준비** | ceo-founder(집중·스토리) → finance-fpa(런웨이·유닛이코노믹스) → **fundraising**(덱·텀시트) → product-marketing(내러티브 정합) | 지표(finance) 없는 덱은 못 만든다. 밸류·희석 경고는 fundraising 거부권급 |
| **B2B SaaS 시장 진입** | b2b-saas-pm(구매자≠사용자 구조) → **go-to-market**(PLG/SLG 모션) → sales(딜 플로우) + customer-success(NRR 설계) | 모션(PLG/SLG) 결정 전에 세일즈 조직부터 짜지 말 것 |
| **리브랜딩** | brand-marketing(포지셔닝·인지 전략) → **brand-designer**(아이덴티티) → design-system(토큰화) → 전 채널 copywriter/ux-writer 정합 | 되돌리기 매우 어려운 결정 — 검증(사용자·시장) 후 착수. 라우터가 속도 제동 |
| **OKR 도입/정렬** | product-strategy or business-strategy(방향) → **okr-goals**(O/KR 작성·정렬) → product-analytics(KR 측정 가능성 검증) | 측정 불가능한 KR은 KR 아님 — analytics가 게이트 |
| **조직 스케일업** | **cto**(기술조직 전략·build vs buy) + people-hr(채용·조직설계) + management(1:1·성과) | 세 축이 병렬. 채용만 늘리고 매니지먼트 체계 없으면 무너짐 |

> 조합에서도 원칙은 같다: **모든 전문가를 부르지 않는다.** 무게중심 1명 + 게이트/핸드오프에 꼭 필요한 1~2명. 순서를 어기면 앞 단계 산출물이 없어 뒤 단계가 공회전한다.

## 라우팅 평가 (eval — 확장판, 새 Phase·수정 시 재실행)

각 문항: 올바른 무게중심 전문가를 1~3명 골랐는가? (기존 1~10 + 확장 11~24)

11. "브랜딩 좀 해줘, 로고부터" → brand-designer(로고) 단, 포지셔닝 없으면 brand-marketing 선행 (❌ 로고만 파고들기)
12. "AI 챗봇 기능 붙이자" → ai-product-pm (❌ 모델 선택은 dev-experts / ✅ 환각·eval·신뢰 UX)
13. "협상 자료 만들어줘 (제휴사랑)" → business-development (❌ life-negotiation은 개인용)
14. "우리 화면설계서/정책정의서" → service-planner (한국형) (❌ prd-writing과 구분: 스펙 서술이 아니라 화면·정책 정의)
15. "리텐션 올릴 방법" → product-analytics로 코호트 먼저 (❌ 바로 crm-lifecycle 기능 아님)
16. "커뮤니티 만들자" → community(SPACES) (❌ social-media와 구분: 채널 운영≠커뮤니티 소속감)
17. "NRR/갱신율 관리" → customer-success (❌ sales와 구분: 신규≠확장·유지)
18. "이 시장 들어갈까(경쟁·해자)" → business-strategy (❌ go-to-market과 구분: 진입 여부≠진입 방법)
19. "PLG로 갈까 세일즈로 갈까" → go-to-market (모션 결정) (+ b2b-saas-pm) (❌ 조직부터 짜지 말 것)
20. "번레이트·런웨이 몇 개월" → finance-fpa (❌ fundraising과 구분: 재무 현황≠자금 조달)
21. "디자인 토큰·컴포넌트 체계" → design-system (❌ ui-designer 단독 아님 — 시스템화가 핵심)
22. "저성과자 PIP 절차" → management(1:1·피드백) + people-hr(절차·법적) (❌ 바로 해고 아님)
23. "빈 상태/에러 메시지 문구" → ux-writer (❌ copywriter와 구분: 제품 내부 마이크로카피≠마케팅 카피)
24. "메타태그·schema·페이지 속도" → dev-seo-analytics로 위임 (❌ seo-marketing은 콘텐츠·의도 담당)

### 자가 점검 루브릭 (라우팅 후 스스로 채점)

- [ ] **무게중심 1명을 명확히 지목**했는가? (전원 소집 금지)
- [ ] 부른 전문가가 3명 이하인가? (초과 시 과호출)
- [ ] 사용자 **명사(산출물)가 아니라 decision**을 라우팅했는가?
- [ ] **되돌리기 어려운 결정**(가격·리브랜딩·조직)에 검증 게이트를 걸었는가?
- [ ] **윤리 축**(다크패턴·과장·차별·허위)을 거부권급으로 유지했는가?
- [ ] ⬜(미제작) 전문가를 Read 시도하지 않고 폴백 선언했는가?
- [ ] 조합이면 **호출 순서·핸드오프**를 명시했는가?
- [ ] 위임 대상(코드/투자/개인)을 biz 안에서 억지 처리하지 않았는가?

> 8개 중 하나라도 ❌면 라우팅을 재검토한다. 오라우팅이 2회+ 반복되는 유형은 위 색인·발화 신호표·조합표를 수정하고 해당 eval 문항을 갱신한다.
