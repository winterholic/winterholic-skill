# biz-finance-fpa — 공식 & 출처 (검증판)

> SKILL.md 보강. 회계·세무는 전문가. 출처 2026-06-30 웹 검증. 1단계 참조.

## 1. 단위경제 (David Skok, a16z)
- Skok "SaaS Metrics 2.0": "LTV:CAC >3, 때로 7~8"; CAC 회수 최선 5~7개월·12개월 넘으면 빈약. https://www.forentrepreneurs.com/saas-metrics-2/
- a16z "16 Startup Metrics": CAC=유저당 전체 획득비; LTV=관계 순익의 현재가치. **Blended vs Paid CAC**(투자자는 paid 중시). https://a16z.com/16-startup-metrics/
- ⚠️ LTV는 추정(관측 아님) — 3% vs 5% 이탈이면 LTV ~1.67배 차이. Blended CAC(paid보다 3~5배 낮음)가 1.2:1을 가릴 수 있음. "LTV:CAC는 상상, CAC payback은 실재."

## 2. 번레이트·런웨이
Gross Burn=지출, Net Burn=매출−지출("진짜 측정"). ⚠️ **런웨이=현금÷순번레이트 공식은 a16z 아님 — Carta 등 일반 귀속**. https://carta.com/learn/startups/metrics/burn-rate/

## 3. NRR/GRR (Bessemer)
NRR 100% 양호/110% 우수/120%+ 최선(확장 포함, >100% 가능). GRR(확장 제외, ≤100%). NRR이 logo churn 가릴 수 있어 GRR·로고 리텐션 병기. https://www.bvp.com/atlas/state-of-the-cloud-2023
- **상한 사례(SEC S-1, 1차)**: Snowflake S-1(2020) **net revenue retention 158%** — ⚠️ **24개월(2년) 고정 코호트 기준**이라 1년 기준 타사 NRR과 직접 비교 불가(측정 방식 주의). https://www.sec.gov/Archives/edgar/data/1640147/000162828020013010/snowflakes-1.htm · Datadog S-1(2019) **dollar-based net retention >130%**(2022까지 130%+ 유지, 2023 mid-110%대로 둔화). https://www.sec.gov/Archives/edgar/data/0001561550/000119312519227783/d745413ds1.htm

## 4. Rule of 40 (귀속 교정)
"성장%+이익% ≥40." Brad Feld(2015-02-03) https://feld.com/archives/2015/02/rule-40-healthy-saas-company/ · Fred Wilson(AVC, 2015-02). ⚠️ **Feld는 Fred Wilson을 출처로 들지 않음 — 무명 후기단계 투자자를 인용**; Wilson은 독립 게시. 정확 프레이밍: "2015-02 Feld·Wilson이 대중화, 원 창시자 무명." 스케일 SaaS(~$50M+)·EBITDA 기준.

## 5. 음(-) 단위경제 실패 (1차 SEC·언론 대조 완료)
- **MoviePass**: 음의 그로스 마진(매 방문 손실). 모회사 Helios & Matheson **FY2018 순손실 $329.3M**(매출 $232.3M) — ⚠️ 기존 "$266.8M"은 오기, $329.3M으로 교정(Variety/SEC). 2020-01-28 챕터7 파산. https://variety.com/2020/film/news/moviepass-bankruptcy-parent-helios-and-matheson-1203485327/
- **Blue Apron**: CAC>LTV, **6개월 후 72% 이탈**(28% 잔존), 1년 후 ~18% 잔존. (Daniel McCarthy 단위경제 분석, 2017 S-1 기반.)
- **WeWork**: 자본집약 번, **2018 매출 $1.82B vs 순손실 $1.93B**(S-1), 2019-09-17 IPO(S-1) 철회. https://en.wikipedia.org/wiki/WeWork
- **Groupon(허영지표 사례)**: 2011-06 S-1에서 **ACSOI**(구독자 획득 마케팅 제외)로 2010 영업"이익" $60.6M처럼 보이게 함 → 실제 GAAP **영업손실 $420M**(2011 Q1 ACSOI $81.6M vs 손실 $117.1M). SEC Reg-G 우려로 2011-08 개정 S-1에서 제거. https://www.sec.gov/Archives/edgar/data/0001490281/000104746911005613/a2203913zs-1.htm

## 6. 출처
- Skok forEntrepreneurs. · a16z "16 Startup Metrics". · Bessemer State of the Cloud. · Feld(2015). · Snowflake/Datadog S-1(SEC). · 실패 사례: Groupon S-1·WeWork S-1(SEC), MoviePass(Variety), Blue Apron(McCarthy 분석).
