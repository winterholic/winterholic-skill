# biz-cto — evidence & 심화

> SKILL.md 안티패턴·프레임의 실증·심화. 1단계 참조. 정량 수치는 통념/원전 인용을 구분 표기, 불확실은 "확인 필요".

## 목차
1. 기술 부채 포트폴리오 모델
2. build vs buy vs partner 판정 프레임
3. IC→매니저 전환 신호 & IC 트랙
4. 단계별 조직 구조 (실패 모드)
5. 엔지니어링 조직 스케일 정량 기준 (Larson)
6. CTO 역할 진화 (단계별)
7. 출처

세부 실무 파일:
- `tech-debt-portfolio.md` — 부채 분류·정량화·상환 전략 (Fowler 4분면 + 이자율 모델 + SQALE 개념)
- `build-buy-partner.md` — 3자 의사결정 프레임 + TCO 계산 + 사례
- `org-scaling.md` — Team Topologies 4팀 유형·상호작용 모드 + Dunbar + span-of-control + Larson 수치
- `adr-guide.md` — Nygard ADR 템플릿·상태 전이·운영 관행

## 1. 기술 부채 포트폴리오
부채는 "갚을 빚"이 아니라 "관리할 포트폴리오". 등급:
- **이자율 = 변경 빈도 × 변경 시 고통**. 자주 건드리고 건드릴 때마다 아픈 코드 = 고이자 → 우선 상환.
- 안 건드리는 모듈의 부채는 이자 0 → 방치 허용(전면 재작성 금지).
- 의도적 부채(빨리 출시하려 일부러 진 빚)는 상환 계획과 함께 진 것이어야 한다(Fowler 4분면: 신중/무모 × 의도/우발).
- 전면 재작성의 위험: Netscape는 코드를 버리고 재작성하다 시장을 IE에 내줬다(Joel Spolsky "Things You Should Never Do"의 고전 사례).
- **자세한 분류·정량화·상환 전략은 `tech-debt-portfolio.md` 참조.**

## 2. build vs buy vs partner
3자 선택으로 확장(buy만이 아니라 partner/제휴도 옵션):
- **buy** 신호: 우리 경쟁 해자가 아니다(인증·결제·이메일·로그·검색 인프라) · 성숙한 SaaS/OSS 존재 · 직접 만들면 온콜 부담 영구.
- **build** 신호: 제품 차별화의 핵심 · 외부 솔루션이 핵심 워크플로를 못 맞춤 · 데이터·지연·규제상 위탁 불가.
- **partner** 신호: 역량은 없지만 전략적 중요 · 시장 진입 속도가 관건 · 리스크 분담 필요(공동개발·화이트라벨·리셀러).
- 경고: build 결정의 진짜 비용은 초기 개발이 아니라 **영구 유지보수**(TCO). 
- **TCO 계산·판정 매트릭스는 `build-buy-partner.md` 참조.**

## 3. IC→매니저 전환 신호 (Fournier *The Manager's Path*)
매니저가 필요해지는 신호: 팀이 12~15명 넘음 · 1:1·조정에 리드 시간의 절반 이상 · 채용/평가가 밀림. 단 최고 IC를 자동 승진시키지 말 것 — IC 트랙(Staff/Principal)을 별도로 두어 기술 깊이로도 성장하게(Larson *Staff Engineer*).

## 4. 단계별 조직 (복붙 실패)
- ~10명: 단일 팀, CTO가 직접 관리, 제너럴리스트.
- 10~30명: 첫 매니저(들), 2~3개 기능팀.
- 30~80명: 매니저 계층 2단, 플랫폼/인프라 분화 시작(고통이 생긴 곳만).
- 80+: 디렉터 계층, SRE/플랫폼 전담.
실패 모드: 30명인데 80명 구조(과분화 관료제) 또는 80명인데 10명 구조(CTO 병목).
- **Team Topologies 관점의 팀 유형·분화 시점은 `org-scaling.md` 참조.**

## 5. 엔지니어링 조직 스케일 정량 기준 (Will Larson, "Sizing engineering teams")
Larson 원전 수치(통념보다 구체적, 1차 출처):
- **매니저 1인당 엔지니어 6~8명** — 코칭·조정·전략 작성에 충분한 시간.
- **직속 4명 미만** → 매니저가 아니라 사실상 **Tech Lead Manager**(설계·구현도 겸함).
- **직속 8~9명 초과** → 매니저가 코치/안전망으로만 기능, 팀에 능동 투자 불가(과부하).
- **매니저-of-매니저는 매니저 4~6명 지원** — 코칭·이해관계자 정렬·조직 투자 균형.
> 근거: https://lethain.com/sizing-engineering-teams/ (An Elegant Puzzle에도 수록). scripts/org_sizing.py는 span 기본 6으로 이 범위 중간값 사용.

## 6. CTO 역할 진화 (단계별)
CTO라는 직함 하나가 단계마다 전혀 다른 일을 뜻한다:
- **창업~PMF 전**: 최고 코더/아키텍트. 직접 짜고 초기 스택 결정. 조직이랄 게 없음.
- **PMF~30명**: 첫 위임. 코딩 비중을 줄이고 채용·매니저 채용·아키텍처 방향으로. **가장 흔한 실패가 여기서** — 계속 코딩하면 병목(안티패턴 1).
- **30~150명**: 순수 리더. 조직 설계·기술 전략·이해관계자 정렬. 코드는 거의 안 봄. 매니저의 매니저.
- **150명+**: 대외 CTO. 기술 비전·채용 브랜드·이사회·전사 전략. 실무는 VP Eng/디렉터가.
> 회사·창업자마다 편차 큼(확인 필요). 핵심은 "같은 직함이라도 단계가 바뀌면 일을 바꿔야 한다" — 못 바꾸면 CTO 교체 사유가 됨(스케일업 통념).

## 7. 출처
- Camille Fournier, *The Manager's Path* (2017).
- Will Larson, *An Elegant Puzzle* (2019) / *Staff Engineer* (2021). https://lethain.com/ · "Sizing engineering teams" https://lethain.com/sizing-engineering-teams/
- Joel Spolsky, "Things You Should Never Do, Part I" (2000) — Netscape 재작성. https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/
- Martin Fowler, "TechnicalDebtQuadrant" (2009) — 신중/무모 × 의도/우발. https://martinfowler.com/bliki/TechnicalDebtQuadrant.html
- Matthew Skelton & Manuel Pais, *Team Topologies* (2019). 4팀 유형·3상호작용 모드. https://teamtopologies.com/key-concepts · https://martinfowler.com/bliki/TeamTopologies.html
- Michael Nygard, "Documenting Architecture Decisions" (2011). https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions · Fowler 요약 https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
- Friendster 확장 실패: https://highscalability.com/friendster-lost-lead-because-of-a-failure-to-scale/
