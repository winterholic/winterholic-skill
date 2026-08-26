# biz-marketing-analytics — 모델 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30~07-01 웹 검증. 1단계 참조. 실무 심화 파일: `attribution-models.md`, `incrementality-testing.md`.

## 1. 어트리뷰션 모델 (Google 폐지 — 중요)
⚠️ **Google Ads/GA4는 first/linear/time-decay/position 모델을 폐지(2023-04 발표, ~2023-09~10 완전 제거). 현재 last-click + data-driven(DDA)만 남음.** https://support.google.com/google-ads/answer/6259715 · 발표 https://ads-developers.googleblog.com/2023/04/first-click-linear-time-decay-and.html
- scripts/attribution.py의 4모델은 **개념 학습용**(모델 민감도 시연) — Google 도구에서 직접 못 쓰는 것 인지. DDA는 계정별(보편 알고리즘 아님).
- 6모델 편향·용도·한계 상세 비교표는 → `attribution-models.md`.

## 2. DDA 작동 원리·데이터 요건 (검증)
DDA는 전환 경로 데이터로 **각 터치포인트의 한계 기여를 알고리즘이 학습**(Shapley value 계열 반사실 비교 — Google은 알고리즘 세부를 공개하지 않으므로 "Shapley 계열"은 업계 이해, 공식 확정 아님·확인 필요).
- **데이터 요건 변화(검증)**: 과거 임계값 = 30일 내 **전환 300건 + 지원 네트워크 광고 상호작용 3,000건**. 이 요건은 **2021-09-27 제거**되어 모든 전환 액션에 DDA 사용 가능. 다만 Google은 품질을 위해 **30일 내 전환 ~200건·상호작용 ~2,000건** 권장. https://support.google.com/google-ads/answer/6394265 · https://blog.google/products/ads-commerce/data-driven-attribution-new-default/
- 함의: DDA도 **관찰(클릭/노출 경로) 기반** — 추적 안 되는 오프라인·크로스디바이스·뷰스루 손실분은 못 봄. 여전히 상관·기여이지 인과 아님.

## 3. 삼각측량 — MTA vs MMM vs 증분성 실험
세 방법은 대체재가 아니라 **삼각측량(triangulation)** — 각각 다른 편향을 가지므로 교차검증. 결정 프레임·비교표 → `attribution-models.md`, `incrementality-testing.md`.
- **MTA(멀티터치 어트리뷰션)**: 유저 경로 단위·정밀·전술적(캠페인/키워드 배분). 한계 = 쿠키/ATT로 경로 붕괴, 관찰 기반이라 인과 아님.
- **MMM(미디어 믹스 모델)**: 집계·시계열·프라이버시 안전·오프라인+온라인 통합·장기 전략 배분. 한계 = 상관, 다중공선성(채널 동시집행), 저빈도 데이터.
- **증분성 실험(지오/홀드아웃)**: 유일한 **인과**. 한계 = 비용·시간·특정 채널만 격리 가능.

## 4. 증분성 (인과 — 학술)
- **Johnson, Lewis, Nubbemeyer(2017), "Ghost Ads: A Revolution in Measuring Ad Effectiveness," *JMR* 54(6):867–884**, DOI 10.1509/jmr.15.0297. https://journals.sagepub.com/doi/10.1509/jmr.15.0297 (※ SSRN 워킹페이퍼 제목은 "...Improving the Economics of..."; 게재본 부제는 "A Revolution in...". 2017 Paul E. Green Award 수상.) ghost ad = 노출됐을 광고를 실제 미노출하되 식별만 해 완벽 대조군 구성 → PSA 플라시보보다 비용·편향 우월.
- **Vaver & Koehler(2011), "Measuring Ad Effectiveness Using Geo Experiments," Google.** https://research.google/pubs/measuring-ad-effectiveness-using-geo-experiments/
- ghost ads가 PSA 플라시보를 대체. 지오는 프라이버시 안전.
- 방법 비교표(지오홀드아웃·유저스플릿·PSA·ghost ads)·설계 절차·검정력·표본 → `incrementality-testing.md`.

## 5. MMM 실무 (Meridian 검증)
**Google Meridian**(오픈소스 베이지안 MMM, 2025-01-29 공개) — 증분성 실험을 prior로. https://developers.google.com/meridian · https://github.com/google/meridian . MMM(집계·프라이버시안전·장기) ≠ MTA(유저경로·쿠키). 회귀 MMM은 실험 보정 없으면 상관.
- **입력변수**: 미디어 지출/노출(채널별), 매출/전환(KPI), 통제변수(가격·프로모·계절성·경쟁·거시).
- **adstock(광고 잔존효과)**: 지출 효과는 즉시가 아니라 **시간에 걸쳐 누적·감쇠** — 기하 감쇠 커널로 모델링. 잔존 기간(반감기) 추정.
- **포화곡선(saturation)**: 지출↔매출은 선형이 아니라 **체감(diminishing return)** — Meridian은 **Hill 함수**로 포화, reach는 선형·frequency는 Hill 통과 후 곱해 adstock 전개(검증: Meridian 공식·2차 다수 일치). 한계효율=포화곡선 기울기 → 예산 배분 최적점.
- **왜 실험 보정 필요**: 순수 회귀 MMM은 채널 동시집행(다중공선성)·역인과로 계수가 불안정 → **증분성 실험 결과를 베이지안 prior로 주입(calibration)**해 인과에 근접. Meridian GeoX 지오실험 결과를 prior로 변환 가능(검증). MMM+실험이 현대 측정 스택의 핵심.

## 6. eBay 유료검색 실험 (인과 정전)
**Blake, Nosko, Tadelis(2015), "Consumer Heterogeneity and Paid Search Effectiveness," *Econometrica* 83(1):155–174**, DOI 10.3982/ECTA12423. https://www.nber.org/papers/w20171 — **브랜드 키워드 광고는 단기 측정 가능 효익 없음**(어차피 올 사용자), 비브랜드는 신규/저빈도에만 양(+). 관찰 ROI는 선택편향으로 상향.
- 보강: **Lewis & Rao(2015), "The Unfavorable Economics of Measuring the Returns to Advertising," *QJE* 130(4):1941–1973** — 거대 실험(수백만 노출)도 광고 ROI 신뢰구간이 매우 넓어(리턴 대비 매출 변동성이 커) 개인수준 정밀 측정 종종 불가능. 함의: 증분성 실험도 **충분한 검정력(표본)** 없으면 결론 못 냄.

## 7. 퍼널·코호트·리텐션 분석 (정의 — 실무)
> 마케팅 애널리스트가 기여 외에 자주 쓰는 3대 렌즈. 제품 행동 깊이는 → biz-product-analytics.
- **퍼널(funnel)**: 순차 단계 전환율(노출→클릭→가입→구매). 최대 이탈 단계가 개선 레버. ⚠️ 단계 정의·기간 창(window)을 고정해야 비교 가능.
- **코호트(cohort)**: 가입 시점(주/월) 등 공통 기준으로 묶은 집단을 **시간축으로 추적** — 획득 시점별 품질·리텐션 변화를 봄. 전체 평균이 숨기는 신규 유입 품질 저하를 드러냄.
- **리텐션(retention)**: 일정 기간 후 활성 유지 비율. **N-day(정확히 D+N 활성)** vs **unbounded/rolling(D+N 이후 언젠가 활성)** vs **range(구간 내 활성)** — 정의에 따라 수치가 크게 달라짐(반드시 정의 명시). 리텐션 곡선이 **평탄화(flatten)**되면 PMF 신호.

## 8. 교정
Google 4모델 폐지(2023). 마지막 클릭은 브랜드검색/직접에 과다 공로 → 상단 채널 말소. DDA는 계정별·관찰 기반(인과 아님). 플랫폼 전환 ≠ 증분. 리텐션·퍼널은 정의(창·N-day)에 따라 값이 달라짐.

## 9. 출처
- Google Ads/GA4 공식(어트리뷰션·DDA). · Johnson·Lewis·Nubbemeyer(2017) JMR. · Vaver·Koehler(2011). · Blake·Nosko·Tadelis(2015) Econometrica. · Lewis·Rao(2015) QJE. · Google Meridian(2025-01-29)·GitHub.
