# biz-finance-fpa — SaaS 단위경제·벤치마크 실전 (신설)

> evidence.md의 공식·귀속 교정을 "판정선이 있는 벤치마크 표"로 확장. 회계·세무는 전문가. 출처 2026-07 검증, Bessemer/a16z 1차 우선. 벤치는 상수 아님.

---

## 1. 핵심 단위경제 — 공식과 판정선

| 지표 | 공식 | 판정선 | 주의 |
|---|---|---|---|
| **LTV:CAC** | LTV ÷ CAC | >3 양호 (때로 7~8, Skok) | LTV는 **추정**. 3% vs 5% churn이면 LTV ~1.67배 차이 |
| **CAC payback** | CAC ÷ (신규 월 그로스마진 매출) | 5~7개월 최선, >12개월 빈약 (Skok) | "LTV:CAC는 상상, CAC payback은 실재" |
| **Magic Number** | 신규 ARR ÷ 전기 S&M 지출 | 1.0+ 목표(2024 median ~0.90) | S&M 효율. 1 미만이면 획득 비효율 |
| **Burn Multiple** | 순번레이트 ÷ 순신규 ARR | <1.5 양호(A단계), 낮을수록↑ | "얼마 태워 1달러 ARR 만드나" |
| **Rule of 40** | 성장% + 이익% | ≥40 | 스케일(~$50M+ ARR)·EBITDA 기준 |

- **Blended vs Paid CAC**: 투자자는 paid 중시(blended가 paid보다 3~5배 낮아 1.2:1 열위를 가릴 수 있음). — a16z "16 Startup Metrics".

---

## 2. 리텐션 — NRR/GRR (Bessemer)

| 지표 | 정의 | 판정선 |
|---|---|---|
| **NRR** (net revenue retention) | 확장 포함, >100% 가능 | 100% 양호 / 110% 우수 / 120%+ 최선 |
| **GRR** (gross revenue retention) | 확장 제외, ≤100% | 로고 이탈을 NRR이 가리므로 병기 필수 |

- **State of the Cloud 2024(Bessemer)**: 상장 SaaS 톱퍼포머 NRR **~104~106%**대로 하향 안정(과거 130%+ 시대 종료). CAC payback Good 12~18개월 / Better 6~12 / Best 0~6. NRR Good 100 / Better 110 / Best 120+. (요약 출처 benchmarkit·bantrr — bvp 원문과 정합.)
- **밸류 임팩트**: <12개월 payback 기업 ~8.2x ARR vs >18개월 ~5.1x ARR (Bessemer 2024). 밸류 median 2020~21 ~18x → 2024 ~6x(효율 우선 시대).
- **상한 사례(SEC S-1)**: Snowflake S-1(2020) NRR **158%**(⚠️ **24개월 코호트** 기준, 1년 타사와 직접 비교 불가) · Datadog S-1(2019) dollar-based net retention **>130%**(2022까지 유지, 2023 mid-110%대 둔화). evidence.md.

---

## 3. 번레이트·런웨이
- Gross Burn = 총지출, **Net Burn = 매출 − 지출("진짜 측정")**.
- **런웨이 = 현금 ÷ 순번레이트**. (⚠️ 공식 귀속은 Carta 등 일반 — a16z 아님. runway.py 활용.)

---

## 4. Rule of 40 — 귀속 교정
- "성장% + 이익% ≥ 40." **Brad Feld(2015-02-03)**·Fred Wilson(AVC, 2015-02)이 대중화. ⚠️ **Feld는 Wilson을 출처로 들지 않고 무명 후기단계 투자자를 인용** — 원 창시자 무명. 스케일 SaaS·EBITDA 기준.

---

## 5. 음(-) 단위경제 실패 케이스 (1차 SEC·언론 대조 완료 — evidence.md와 동일 확정치)
- **MoviePass**: 음의 그로스마진(매 방문 손실). 모회사 Helios & Matheson **FY2018 순손실 $329.3M**(매출 $232.3M), 2020-01-28 챕터7. (⚠️ "$266.8M" 오기 금지.)
- **Blue Apron**: CAC>LTV, **6개월 72% 이탈**(28% 잔존), 1년 ~18% 잔존.
- **WeWork**: 자본집약 번, **2018 매출 $1.82B vs 순손실 $1.93B**, 2019-09-17 IPO 철회.
- **Groupon(허영지표)**: S-1에서 **ACSOI**로 2010 영업"이익" $60.6M처럼 보이게 함 → 실제 GAAP 영업손실 $420M. SEC Reg-G 우려로 2011-08 제거.

---

## 6. 리텐션의 경제학 (보강, 1차 원전 주의)
- "리텐션 5%p↑ → 이익 25~95%↑"의 **원전은 Reichheld & Sasser "Zero Defections"(HBR 1990)** — 원문은 **"이탈 5%p 감소 → 한 은행 지점망 이익 85%↑"** 같은 산업별 수치. **25~95%는 산업 범위(95%는 최선 산업의 천장, 기대치 아님)**이며 흔히 "5%→25~95%"로 헐겁게 인용됨. verbatim으로 쓸 땐 "확인 필요"로 산업·출처를 명시. https://hbr.org/2014/10/the-value-of-keeping-the-right-customers

---

## 7. 출처
- Skok forEntrepreneurs "SaaS Metrics 2.0" · a16z "16 Startup Metrics" · Bessemer State of the Cloud 2023/2024 https://www.bvp.com/atlas/state-of-the-cloud-2024 · Feld(2015) · Snowflake/Datadog S-1(SEC) · 실패: Groupon/WeWork S-1(SEC)·MoviePass(Variety)·Blue Apron(McCarthy) · Reichheld & Sasser(HBR 1990, "확인 필요"). 벤치는 상수 아님.
