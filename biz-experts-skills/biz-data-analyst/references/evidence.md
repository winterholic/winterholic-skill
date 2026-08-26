# biz-data-analyst — 프레임 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 웹 검증, 2026-07-01 심화 재검증. 1단계 참조.
> 실무 절차·템플릿은 `playbook.md` 참조.

## 1. 정전 소스

- **Cole Nussbaumer Knaflic, *Storytelling with Data*(Wiley, 2015)** — 데이터 시각화는 장식 아닌 커뮤니케이션. 6단계: (1) 맥락 이해 (2) 적절한 시각 선택 (3) clutter 제거 (4) 주의 집중(preattentive attributes) (5) 디자이너처럼 사고 (6) 스토리로 전달. https://www.storytellingwithdata.com/books
  - **Gestalt 6원리**(decluttering 근거): proximity·similarity·enclosure·closure·continuity·connection. https://www.oreilly.com/library/view/storytelling-with-data/9781119621492/c03.xhtml
  - **Preattentive attributes**: 의식적 노력 없이 즉각 인지되는 속성(색·크기·위치·방향). 주의를 핵심 요소로 유도하는 도구.
- **Croll & Yoskovitz, *Lean Analytics*(O'Reilly, 2013)** — 단계별 **OMTM(One Metric That Matters)**, vanity metric 회피. 5단계(Empathy→Stickiness→Virality→Revenue→Scale), 단계마다 다른 OMTM.
- **Tyler Vigen, *Spurious Correlations*(Hachette, 2015)** — 상관≠인과 반례집(예: 니콜라스 케이지 영화 출연 수 vs 수영장 익사자). https://www.tylervigen.com/spurious-correlations
- (엄밀 인과) **Judea Pearl & Dana Mackenzie, *The Book of Why*(2018)** — 인과의 사다리(association→intervention→counterfactual). do-calculus, 상관에서 인과로 가려면 개입/구조가 필요.

## 2. 프레임

- **"좋은 지표" 4기준(Lean Analytics)**: Comparative(비교 가능)·Understandable(이해 가능)·Ratio/Rate(비율·비율은 절대량보다 행동적)·**Behavior-changing(행동을 바꾸는가 — 가장 중요)**.
- **North Star Metric**: ⚠️ **용어=Sean Ellis(growth hacking 창안자, ~2010, OMTM 개념) / 프레임 정형화=Amplitude·John Cutler(North Star Playbook, 2017)** — 혼동 빈번. NSM = 고객이 얻는 핵심 가치의 대리지표(예: Airbnb "예약된 숙박 밤 수"). https://amplitude.com/resources/north-star-playbook
  - 검증: 용어는 Ellis가 growth 커뮤니티에서 대중화, 체계적 플레이북(입력 동인 분해)은 Amplitude 2017. 둘을 한쪽에 몰아 귀속하는 것이 최빈 오류.
- **Metric tree(지표 트리)**: 노스스타 → 입력 동인(input metrics) → 서브지표. 노스스타는 후행(lagging), 입력 동인은 팀이 직접 움직일 수 있는 선행(leading). playbook.md §1 참조.
- **AARRR(해적 지표, Dave McClure)**: Acquisition·Activation·Retention·Referral·Revenue — 퍼널 뼈대. playbook.md §2.

## 3. 교정 (최빈 오류)

- **North Star 용어=Ellis / 프레임=Amplitude·Cutler.** (§2 참조)
- **Vanity metric 오용**: "총량은 항상 vanity"가 아님 — **행동을 못 바꾸거나 비교 불가일 때만** vanity. 누적 가입자 수는 보통 vanity(늘 우상향, 결정 못 바꿈)지만, 동일 수치도 맥락 따라 유효할 수 있음.
- **"상관은 무의미" 과잉정정 오류** — 상관은 **인과의 필요조건이자 가설 생성기**. 문제는 통제실험·메커니즘·식별전략 없이 상관→인과로 **단정**하는 것. 상관 자체를 버리라는 게 아님. (Vigen의 반례는 "상관만으로 인과 단정 금지"의 예시이지 "상관 무용"의 예시가 아님.)
- **"Storytelling with Data=예쁘게 만들기" 오해** — 정반대. clutter 제거·data-ink 극대화가 핵심. 3D·파이 남용·이중축·불필요한 색은 안티패턴. (Tufte의 data-ink ratio와 통함.)
- **심슨의 역설(Simpson's paradox)** — 집계 데이터의 방향이 하위 그룹별 방향과 **반대**로 나올 수 있음. 교란변수 때문. ✅ **UC Berkeley 1973 대학원 입학 1차 검증**: 전체로는 남성 합격률 44% > 여성 35%(성차별 소송)였으나, **학과별로 쪼개면 6개 중 4개 학과에서 여성 합격률이 더 높았음** — 여성이 경쟁률 높은(합격률 낮은) 학과에 더 많이 지원한 것이 교란(학과=lurking variable). 집계 지표를 볼 때 세그먼트 분해가 필수인 이유. https://www.refsmmat.com/posts/2016-05-08-simpsons-paradox-berkeley.html
  - ⚠️ 정확성: "6개 학과 중 4개" 수치는 원 논문(Bickel et al., *Science* 1975)이 다룬 상위 6개 학과 기준. 세부 수치는 인용마다 편차 있어 "약 44% vs 35%, 학과 분해 시 역전"으로 보수 표기.

## 4. 출처

- Knaflic, *Storytelling with Data*(2015) + Gestalt/preattentive(O'Reilly 챕터3).
- Croll & Yoskovitz, *Lean Analytics*(2013, OMTM/좋은 지표 4기준).
- Amplitude/Cutler, *North Star Playbook*(2017) + Sean Ellis(용어 기원).
- Vigen, *Spurious Correlations*(2015). · Pearl & Mackenzie, *The Book of Why*(2018).
- 심슨의 역설: Bickel et al.(*Science* 1975) / refsmmat 해설(1차 데이터 재현).
- 리텐션 정의: Amplitude Docs(N-day/unbounded/bracket). https://amplitude.com/docs/analytics/charts/retention-analysis/retention-analysis-interpret
