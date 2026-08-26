# biz-growth-pm — 프레임 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 웹 검증. 1단계 참조.

## 1. 성장 모델 만들기 (Balfour/Reforge)
제품 성장을 입력 변수의 수식으로(예 SaaS: MRR = 신규×활성화×유료전환 + 기존×유지×확장 − 이탈). 모델이 실험 우선순위를 정한다.
- **Four Fits** (Brian Balfour, 2017, 4부작): Market↔Product, Product↔Channel, Channel↔Model, Model↔Market — PMF만으로 스케일 안 됨, 네 적합을 함께 설계. https://brianbalfour.com/four-fits-growth-framework

## 2. 성장 루프 (Balfour/Reforge)
"Growth Loops are the New Funnels" — 루프는 복리, 깔때기는 샌다. 바이럴/콘텐츠/페이드 루프. https://www.reforge.com/blog/growth-loops

## 3. 활성화·PMF
- Sean Ellis 40% test("매우 실망" ≥40%, ~2009). 절대 컷 아닌 휴리스틱.
- a16z AI 리텐션 벤치마크("smiling" 곡선). https://a16z.com/ai-retention-benchmarks/
- Superhuman PMF 엔진(Rahul Vohra, First Round Review): "매우 실망" 22%→(세그먼트 후)33%→세 분기 만에 58%로 거의 2배. 4단계 엔진(supporters 세그먼트→피드백 분석→로드맵 50/50→분기 반복). 1차(First Round Review 원문)·저자 본인 블로그 교차 확인. https://review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit/ · 저자판 https://blog.superhuman.com/how-superhuman-built-an-engine-to-find-product-market-fit/

## 4. PLG / PQL
PQL(Product-Qualified Lead) vs PQA — **Elena Verna**가 정립. 가이드: https://www.lennysnewsletter.com/p/the-ultimate-guide-to-product-led

## 5. 실전 케이스
- 드롭박스 양면 추천(추천인·피추천인 각 500MB, 계정당 상한 16GB): 등록 사용자 **10만→400만, 15개월, 약 3900%**(2008-09 PayPal식 추천 도입, Sean Ellis 데이터 분석으로 시작). 도입 첫 달 **일일 가입의 최대 35%가 추천 유입**, 2010-04 기준 월 280만 초대. 이상 수치는 2차 케이스 다수가 일치 — 단 **k-factor 1.5~2.0**은 2010 Houston/Ellis 원본 덱에서 1차 확인 못함(2차 인용만 존재) → "추정 바이럴 계수, 1차 미확인"으로 표기. https://referralrock.com/blog/dropbox-referral-program/ · https://viral-loops.com/blog/dropbox-grew-3900-simple-referral-program/
- Slack "~2000 메시지" 활성화 임계: **팀 누적 2,000 메시지 도달 시 93%가 잔존(장기 전환)**. 출처는 First Round Review의 Butterfield 인터뷰(2015-01, "From 0 to $1B")이지 **S-1 아님**(흔한 오귀속). 1차 인터뷰 본문 확인. https://review.firstround.com/from-0-to-1b-slacks-founder-shares-their-epic-launch-strategy/

## 6. North Star 프레임 심화 (Amplitude, 검증)
NSM은 **출력(output)**, 그 밑에 **입력 지표(inputs) 3~5개**가 있다 — Amplitude는 이 3~5개를 "가장 직접적으로 NSM에 영향을 주는 상보적 레버"로 정의하고, 흔히 **Breadth(폭: 획득·재활성 사용자 수) · Depth(깊이: 사용자당 세션·행동) · Frequency(빈도: 재방문 주기·stickiness) · Efficiency(효율: 가치 도달 시간·마찰 감소)** 4축으로 배치한다. 팀은 NSM을 직접 못 움직이니 입력 레버를 순서대로 당긴다.
- 검증 예: **Airbnb NSM = nights booked**(게스트·호스트 양면 가치 포착), **Facebook NSM = DAU**. https://amplitude.com/blog/product-north-star-metric · https://amplitude.com/books/north-star/about-north-star-framework
> 교정: NSM은 "허영지표 하나 고르기"가 아니다 — 반드시 **가치 교환을 대표**하고, 입력 지표로 분해 가능해야 한다. 매출 자체는 NSM으로 부적합(후행·조작 유인) — 매출을 낳는 선행 가치 행동을 NSM으로.

## 7. 실험 우선순위 (검증)
- **ICE = Sean Ellis 창안**(LogMeIn·Dropbox 그로스팀에서 실험 순위용). Impact·Confidence·Ease를 각 1~10 점수 → 합/3. 초기·고속 실험(주 다건)에 적합. https://growthmethod.com/ice-framework/
- **RICE = Sean McBride @ Intercom**(ICE의 맹점=도달 인원 무시를 보완). Reach×Impact×Confidence÷Effort. 트래픽 큰 페이지가 정당하게 높은 점수. 스프린트당 20개 초과·세그먼트 상이하면 RICE로. 
> 교정: ICE≠RICE(창안자·공식 다름). 점수는 상대 순위용이지 절대 진리 아님 — Confidence 낮으면 "먼저 싸게 검증"하라는 신호.

## 8. 출처·교정
- Brian Balfour / Reforge. https://brianbalfour.com/essays
- Andrew Chen, *The Cold Start Problem* (2021) — atomic network.
- Sean Ellis & Morgan Brown, *Hacking Growth* (2017) — Ellis가 "growth hacker"·40% test 창안.
- North Star Metric: 용어=Sean Ellis(~2010), 프레임 정형화=Amplitude/John Cutler(North Star Playbook, 2017). https://amplitude.com/resources/north-star-playbook
- ⚠️ 교정: **Elena Verna는 현재 Lovable의 Head of Growth**(과거 Amplitude/Reforge 아님). PLG 코인=OpenView(Blake Bartlett, 2016, OpenView는 2023~24 운영 종료 — 콘텐츠는 역사적 참조).
