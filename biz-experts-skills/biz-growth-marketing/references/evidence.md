# biz-growth-marketing — 프레임 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 최초 웹 검증, 2026-07-01 실전 심화 2차 확장(aha moment 상관≠인과 명시·사이클타임 지수효과·바이럴소진·성장루프 4유형·ICE vs PIE vs RICE 출처 확정·실험 벤치마크 보강). 1단계 참조.
> 부패 등급: 중간. 벤치마크 수치는 **시점 라벨** 필수 — 벤더/연도 없는 수치는 인용 금지.

---

## 1. Hacking Growth (정전)
Sean Ellis & Morgan Brown, *Hacking Growth*(Currency, 2017). 교차기능·고템포 실험, PMF·aha 게이트. https://www.penguinrandomhouse.ca/books/545936/

## 2. Sean Ellis PMF 40% test
"The Startup Pyramid"(2009). "더 못 쓰면 어떨까?" → ≥40% "매우 실망" = PMF 가능성(~100개 스타트업 도출). 이름은 사후 명명, 40%는 휴리스틱(통계 법칙 아님). 운영화: Superhuman/First Round(22%→33%→58%). https://review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit/

**실무 심화**:
- **표본·세그먼트 규칙(운영판)**: Superhuman 방식은 "실망" 응답자만 따로 떼어 그들의 공통 특성으로 ICP를 재정의하고, "약간 실망"층 중 ICP와 겹치는 사람을 40%로 끌어올리는 로드맵을 짠다. 단순 40% 통과/실패 이분법이 아니라 **세그먼트별 PMF 지도**가 실전 산출물. (First Round 리뷰 원문)
- **최소 표본**: Ellis 권고 ~40~100 응답(순수 정성적 신호). n<30이면 신뢰 못 함 — "확인 필요"로 표기. (원 휴리스틱, 엄밀 통계 근거 아님)
- **한계**: 신규 사용자만 대상(생존편향 방지), 이미 이탈한 사람은 설문에 안 잡힘 → 40%가 과대평가될 수 있음. 40% test는 리텐션 곡선(§9)과 **교차검증**해야 함.

## 3. AARRR (McClure, 2007) — 단계·지표 심화
"Startup Metrics for Pirates," Ignite Seattle 2007. 원순서 Acquisition·Activation·Retention·Referral·Revenue. ⚠️ "AAARRR"(Awareness 추가)는 후대 파생. https://www.slideshare.net/slideshow/startup-metrics-for-pirates-long-version/89026

**단계별 대표 지표·측정정의**(상세는 `growth-loops-and-metrics.md`):
| 단계 | 핵심 질문 | 대표 지표 | 실무 기준선 |
|---|---|---|---|
| Acquisition | 어떻게 오는가 | 채널별 방문·CAC·클릭→가입 전환율 | CAC < LTV/3 (업계 일반, 확인 필요) |
| Activation | 첫 만족 경험을 했는가 | 활성화율(aha 행동 도달 %)·TTV(time-to-value) | SaaS 온보딩 완료율 20~40% (확인 필요) |
| Retention | 다시 오는가 | N-day/N-week 리텐션·코호트 곡선·DAU/MAU | 모바일 앱 D30 평균 ~5~10% (2023 Adjust, 확인 필요) |
| Revenue | 돈을 내는가 | 전환율·ARPU·LTV·LTV:CAC | LTV:CAC ≥ 3:1이 SaaS 건강 기준 (확인 필요) |
| Referral | 남을 데려오는가 | 바이럴계수 K·NPS·추천 경유 가입 % | 현실적 K: 0.2~0.8 (확인 필요) |

⚠️ McClure 원 순서는 Retention이 Revenue보다 **앞**(RARRA 재배열은 후대 — 리텐션 우선을 강조하려는 파생, 원전 아님).

**Activation — aha moment 정의법 (실무 절차)**:
- aha moment: 신규 사용자가 "이 제품이 나한테 가치 있다"를 처음 체감하는 행동/순간.
- **찾는 방법**: 잔존(D30+) 코호트 vs. 이탈 코호트 → 신규 등록 후 첫 N일 내 공통 행동 비교 → 로지스틱 회귀·코호트 분할로 리텐션과 상관 높은 행동 식별 → 온보딩을 그 행동으로 유도 → A/B 테스트로 인과 확인.
- **매직넘버 예시**: Facebook **"7친구/10일"** (Chamath Palihapitiya가 공개 인터뷰·강연에서 언급한 수치 — "10친구/14일" 버전이 인터넷에 돌지만 검증된 원문 수치는 7/10). ⚠️ **상관≠인과**: Mode Analytics 분석(2017)에 따르면 이 매직넘버는 통계적 절벽(cliff)이 아니라 분포의 중간값에 가까우며, "7명을 추가하게 강제했더니 리텐션이 올랐다"는 인과는 별도 실험으로 검증해야 한다. 경쟁 제품에 그대로 이식 불가 — 자사 데이터로 독립 검증 필수. 출처: https://mode.com/blog/facebook-aha-moment-simpler-than-you-think/
- Twitter "30팔로워/1달", Slack "팀당 2,000메시지" — 마찬가지로 상관 기반이며 내부 원천 데이터 비공개. 모두 "확인 필요"로 인용.

## 4. 성장 루프 (Balfour/Reforge)
"Growth Loops are the New Funnels"(~2018) — 출력이 입력으로 재투입(복리). Four Fits. https://blog.brianbalfour.com/p/the-four-fits-a-growth-framework

**실무 심화**: 깔때기(funnel)는 선형·1회성(위→아래로 새어나감), 루프는 순환·복리(한 사이클 출력이 다음 사이클 입력). Reforge 분류 4유형(바이럴/콘텐츠/유료/세일즈 — "Growth Loops are the New Funnels" 원문에는 3유형으로 제시되며, 세일즈 드리븐은 후속 글에서 추가, 확인 필요):

| 유형 | 입력 | 핵심 행동 | 출력 | 재투입 방식 | 작동 조건 |
|---|---|---|---|---|---|
| **Viral** | 신규 유저 | 초대·임베드·공유 | 초대받은 신규 유저 | 가입 후 다시 초대 | K>0, 사이클 타임 짧을수록 |
| **Content** | 콘텐츠 제작자 | UGC 생성 | SEO 인덱스·검색 유입 | 신규 유저가 또 콘텐츠 생성 | 검색 수요 존재·크롤 가능 |
| **Paid** | 광고비 | 유료 캠페인 | LTV > CAC인 신규 유저 | 수익 → 더 많은 광고 투자 | LTV:CAC > 1 (복리에는 > 3 필요) |
| **Sales-Driven** | 영업 인력 | 엔터프라이즈 계약 | ARR | ARR → 더 많은 영업 채용 | ACV가 영업비용 상회, 갱신율 높음 |

- **대부분의 제품은 복수 루프 병용**: 초기 유료 루프로 데이터 확보 → 콘텐츠·바이럴 루프로 CAC 감소가 일반 경로.
- **루프가 안 돌아가는 이유**: 전환율이 임계치 미달(바이럴), 콘텐츠 SEO 인덱스 불가, LTV<CAC(유료). 루프 선택은 Four Fits(시장·제품·채널·수익모델 정합)가 결정.
- **Four Fits**(Balfour): Market↔Product, Product↔Channel, Channel↔Model, Model↔Market. 하나라도 어긋나면 루프가 안 돌아감. 상세는 `growth-loops-and-metrics.md` 참조.

## 5. 바이럴 k-factor — 심화
David Skok, "Lessons Learned — Viral Marketing": **K = i × conv%**(i = 사용자당 초대 수, conv% = 초대→가입 전환율), K>1 자가성장, 사이클 타임이 지수성장 좌우. https://www.forentrepreneurs.com/lessons-learnt-viral-marketing/ ⚠️ 반론: Andrew Chen — 리텐션 없는 고 K는 무의미. https://andrewchen.com/viral-coefficient-what-it-does-and-does-not-measure/

**실무 심화**:
- **사이클 타임(ct)의 지수 효과**: 누적 사용자 ≈ 초기값 × K^(t/ct). 예: K=0.8, ct=2일 vs. ct=30일 → 20일 후 격차 수십 배. 동일 K에서 ct를 절반으로 줄이면 같은 기간 성장이 제곱에 가까워짐 — 초대 발송~수락까지 마찰 제거(원클릭 공유, 모바일 딥링크 등)가 K 올리기보다 빠른 레버가 될 수 있다. 출처: https://www.alexanderjarvis.com/viral-cycle-time/
- **왜 K>1 지속이 드문가**: (1) **바이럴 소진(viral exhaustion)** — 초기 열성 사용자가 주소록을 소진하면 i가 급락, K는 시간 경과에 따라 1 아래로 수렴. (2) 주소록·네트워크 풀 유한. (3) K>1이 지속되면 수학적으로 전 인류를 며칠 만에 삼켜야 → 현실 불가능. 지속 성장은 K>1이 아니라 **K<1 + 강한 리텐션 + 보완 루프(콘텐츠/유료)**의 조합.
- **리텐션 결합 필수**: Andrew Chen — 리텐션이 낮으면 데려온 사용자가 곧 이탈 → 다음 사이클 초대 기반 붕괴. 실질 성장의 복리 효과는 리텐션 개선이 K 개선보다 큰 경우가 많다(확인 필요: 제품 단계별 상이). https://andrewchen.com/more-retention-more-viral-growth/
- **측정 함정**: K를 "총 가입 중 초대 경유 비율"로 계산하면 시간축 소진이 숨겨짐 — 코호트 기준(특정 시점 가입자군이 30일 내 몇 명을 초대·전환)으로 측정해야 바이럴 소진 여부가 드러남.

## 6. North Star Metric (NSM) — Amplitude/Reforge 프레임
**정의(Amplitude North Star Playbook)**: 고객이 제품에서 얻는 가치를 가장 잘 포착하는 **단일 지표**. 그 지표를 움직이는 **Inputs(입력 지표) 3~5개** — 팀이 일상 업무로 직접 영향을 줄 수 있는 독립 변수 — 를 함께 정의. https://amplitude.com/books/north-star/about-north-star-framework · Playbook PDF https://info.amplitude.com/rs/138-CDN-550/images/Amplitude-The-North-Star-Playbook.pdf

**좋은/나쁜 NSM(Amplitude)**:
- ✅ **가치 교환의 순간**을 담고, 선행성이 있으며(매출은 후행), 팀이 영향 가능. 예: Airbnb "예약된 숙박 밤 수(nights booked)", Spotify "청취 시간", WhatsApp "전송 메시지 수".
- ❌ 매출·가입자수 단독(후행·허영), 너무 광범위해 팀이 못 움직이는 것. https://amplitude.com/blog/good-bad-north-star-metric
- **NSM = Input1 × Input2 × …** 형태로 분해되면 이상적(각 팀이 한 input을 소유). ⚠️ Amplitude는 벤더 — 프레임 자체는 유용하나 "정답 NSM"은 제품마다 다름.

## 7. 실험 우선순위 프레임 — ICE vs PIE vs RICE (출처·한계)
- **ICE (Sean Ellis, ~2015)**: Impact × Confidence × Ease, 각 1~10 스코어. 평균 = ICE Score. GrowthHackers 플랫폼에서 보급됨. 장점: 빠름·직관적·소규모팀에 적합. 한계: **주관적 점수**(같은 아이디어도 사람마다 다른 점수), Reach(도달 규모) 누락. https://growthmethod.com/ice-framework/
- **PIE (Chris Goward, WiderFunnel, ~2011)**: Potential(개선 여지) × Importance(트래픽 가치) × Ease. CRO·랜딩 최적화 특화 — Importance가 페이지 트래픽 가치를 반영해 "어느 페이지부터 테스트할 것인가"에 강함. 출처: Goward, *You Should Test That!*(2013).
- **RICE (Sean McBride, Intercom, 2016)**: **(Reach × Impact × Confidence) / Effort**. Reach=기간 내 영향받는 사용자 수(실측), Impact=Massive 3/High 2/Medium 1/Low 0.5/Minimal 0.25, Confidence=%, Effort=인·월. ICE 대비 Reach를 명시 추가 + Effort를 분모로. https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
- **선택 기준**: 빠른 스크리닝 → ICE; CRO/페이지 최적화 → PIE; 로드맵 정밀 우선순위 → RICE.
- ⚠️ **공통 한계**: 점수 정밀도는 착시 — 1~10 주관 입력이므로 한 요소 과대평가가 전체 순위를 뒤집음. 이질적 목표(전환 개선 vs. 리텐션 개선)를 섞으면 왜곡. 스코어는 토론 출발점이지 결론이 아님.
- 실험 설계 템플릿 + 우선순위 활용 실무는 `references/experiment-backlog.md` 참조.

## 8. 실험 통계 (조기 종료·검정력·MDE·peeking·승률 벤치마크)
안티패턴 7의 근거. A/B 테스트를 "이틀 보고 이김"으로 끝내면 안 되는 이유:
- **유의수준(α)**: 보통 5% — 진짜 차이 없는데 있다고 오판(1종 오류) 허용 확률.
- **검정력(1−β)**: 보통 80% — 진짜 차이가 있을 때 잡아낼 확률. 표본이 작으면 검정력 부족으로 실제 효과를 놓침(2종 오류).
- **MDE(Minimum Detectable Effect, 최소 탐지 가능 효과)**: 사전에 "몇 %P 개선을 잡고 싶은가"를 정해야 표본크기가 나옴. 작은 효과를 잡으려면 표본이 급격히 커짐(대략 표본 ∝ 1/MDE²).
- **표본크기**: α, 검정력, MDE, 기준 전환율로 사전 계산(계산기/공식). 도달 전에 결론 내리지 않는다.
- **peeking(엿보기) 문제**: 결과를 계속 들여다보며 "유의해지면 멈추기"를 하면 **거짓 양성이 눈덩이처럼 증가**(반복 검정 → α가 5%가 아니라 사실상 20~30%로 부풀음). 대응: 사전 확정 표본까지 결과를 안 보거나, **순차 검정(sequential testing)/always-valid p-value** 방법론(벤더별 구현) 사용. ⚠️ 정확한 표본식·순차검정 세부는 도구/통계 자문 필요("확인 필요").
- **실무 규칙**: 최소 1~2 사이클(주간 패턴 흡수 위해 보통 ≥1주, 이상적 2~4주), Novelty effect(신규성으로 초반 과대반응) 흡수 기간 고려.
- **실험 승률(win rate) 벤치마크 (2023~2025 데이터, 확인 필요)**:
  - Optimizely 플랫폼 전체 평균 승률 ~20%; 수익 직결 지표에선 ~10% (Optimizely Evolution of Experimentation Report, 2024).
  - e-커머스 업계 평균 약 12~15% (확인 필요).
  - 일부 보고에서 "실험의 1/3 성공·1/3 무효·1/3 해로움" 구분. (하버드 비즈니스 스쿨 A/B 테스팅 논문 — 출처: HBS Working Paper 2019, 확인 필요).
  - **시사점**: 승률 낮음 = 실패가 아니라 정상. 핵심 지표는 **실험 속도(velocity)** — 연 24회 이상 실험 조직이 10회 미만 조직 대비 누적 개선 3~4배(Optimizely, 2024 기준, 확인 필요). 승률이 10% 미만으로 지속 하락하면 가설 품질 재검토.
- 자세한 실험 설계 및 흔한 실수 → `references/experiment-backlog.md`.

## 9. 코호트 리텐션 곡선 (smile/flat)
**PMF 신호(Andrew Chen)**: 코호트 리텐션 곡선이 **0으로 안 가고 평탄화(flatten)** 되면 끈끈함(stickiness)·durable value의 신호. https://x.com/andrewchen/status/1184170125525577728
- **flattening curve**: D0에서 떨어지다 특정 수준(예 20~40%)에서 수평 → 그 층이 "고정 사용자 기반". 평탄선 높이가 곧 장기 리텐션 상한.
- **"smile" 구분(중요·혼동 주의)**: Chen 원 트윗의 세 번째 지표 "smile"은 **파워유저 곡선(power user curve)** — 사용일수별 사용자 분포 히스토그램이 양끝이 높은 U자(스마일)면 열성 코어가 두껍다는 뜻. **리텐션 곡선 자체가 시간이 갈수록 다시 올라가는 "smiling retention curve"**(이탈했다 복귀하거나 사용 증가로 반등)는 별개 개념으로, 후대(특히 AI 제품 맥락)에서 확장 사용됨 — 두 용법을 섞지 말 것. https://a16z.com/ai-retention-benchmarks/
- Chen "10 magic metrics" 참고치(**2019 시점, 소비자테크 휴리스틱**): DAU/MAU>50%, D1/D7/D30 ≈ 60/30/15%, 바이럴계수>0.5, 유기적 획득>60%, 구독 연간 리텐션>65%. ⚠️ 절대 기준 아님·제품 카테고리별 편차 큼·**2019 소비자앱 기준**이라 B2B SaaS엔 부적합.

## 10. 실전 케이스 — 드롭박스 (수치 확정)
1차: Drew Houston, "Dropbox Startup Lessons Learned"(SLLConf 2010 덱). 양면 500MB(2008-09 런칭). 수치 확정(Houston 2010 덱 = 원천, 다수 2차 재진술 일치): **10만→400만 유저/15개월(=3900% 성장)**, 추천이 **가입 영구 +60%**, **일일 가입의 ~35%가 추천 경유**, 2010-04에만 280만 초대 발송. **누락 맥락(중요)**: SEM 등 유료 획득(CPA가 LTV 초과)이 먼저 실패해서 추천으로 전환 — k-factor만이 아니라 단위경제 실패가 동인. https://www.slideshare.net/slideshow/dropbox-startup-lessons-learned-3836587/3836587

## 11. 출처
- Ellis & Brown, *Hacking Growth*(2017). · Andrew Chen, *The Cold Start Problem*(2021) + 바이럴계수/리텐션 블로그(andrewchen.com). · Balfour/Reforge, growth loops·Four Fits. · Skok 바이럴 (forentrepreneurs.com). · Amplitude North Star Playbook (amplitude.com/books/north-star). · Intercom RICE(McBride, 2016, intercom.com/blog). · GrowthMethod/ProductPlan(ICE 2차 해설). · Mode Analytics, "Facebook's Aha Moment Was Simpler"(2017). · Alexander Jarvis, viral cycle time(alexanderjarvis.com). · Optimizely Evolution of Experimentation Report(2024, 확인 필요). · HBS A/B Testing Paper(2019, 확인 필요).
