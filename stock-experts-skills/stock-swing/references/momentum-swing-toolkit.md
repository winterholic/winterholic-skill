# 레퍼런스(심화) — 모멘텀 스윙 도구 모음 (Minervini VCP·Qullamaggie·진입/청산)

> 목적: O'Neil CANSLIM을 현대 스윙 실전으로 확장 — Minervini SEPA/VCP, Qullamaggie 셋업, 정량 진입·청산·리스크 규칙.
> 웹 출처: traderlion·finermarketpoints(VCP), quantstrategy.io(SEPA), qullamaggie.com·chartmill(Qullamaggie), financialtechwiz(Trend Template).

## 1. Minervini SEPA (Specific Entry Point Analysis)

펀더멘털 강도 + 최적 기술 타이밍 결합. 핵심 5요소: Trend(추세) · Fundamentals · Catalyst · Entry Point · Exit. CANSLIM의 진화형.

### Trend Template (8점 — Stage 2 필터)
1. 주가 > 150일 & 200일 MA
2. 150일 MA > 200일 MA
3. 200일 MA 최소 1개월(이상) 상승
4. 50일 MA > 150일 & 200일 MA
5. 주가 > 50일 MA
6. 주가가 52주 저점 대비 **+30% 이상**
7. 주가가 52주 고점의 **−25% 이내**
8. RS Rating ≥ 70 (이상적 80+)
→ 8개 모두 충족해야 매수 후보(나머지는 제외).

## 2. VCP (Volatility Contraction Pattern)

Stage 2 종목이 신고가 직전 만드는 **변동성 수축** 베이스:
- 2~6회 풀백, 각 수축이 직전보다 **작아짐**(예: 25% → 12% → 6%).
- 풀백마다 **거래량 감소**, 마지막 수축에서 거래량 최저(매물 소진).
- 마지막 수축 고점 = pivot. **거래량 급증 동반 돌파** 시 매수.
- "T"(수축 횟수)와 footprint로 매물대 압축 정도 판단.

## 3. Qullamaggie 셋업 (모멘텀 3종)

### Breakout
- 조건: ADR > 4% · 주가 > 10일 & 20일 MA · 최근 1~3개월 **+30~100%** 선행 상승 · 2~8주 횡보(타이트).
- 진입: 횡보 고점 돌파. 손절: **1× ADR 이내**.

### Episodic Pivot (EP)
- 갭업 > 10% + 첫 15분 거래량 평소 2배↑ (실적 서프라이즈·신제품·뉴스 촉매).

### ADR (Average Daily Range)
- `ADR% = 20일 평균((고−저)/종가)`. 변동성·손절폭·목표의 기준.

### 청산
- 3~5일 후 1/3~1/2 익절 → stop 본전 이동 → 잔량은 **10일 또는 20일 MA 트레일링**(MA 이탈 시 종료).
- 트레이드당 리스크 0.25~1%.

## 4. 보조 지표 활용 (스윙 맥락)

- RSI: 돌파 후 과매수(>70)는 추세장에선 "강세 신호"로 재해석(가치투자와 반대).
- 거래량: 돌파일 평소 +40~50%↑ 필수(Bulkowski — 거래량 미확인 돌파 실패율 약 2배).
- 50일선: 추세 추종 종목의 1차 트레일링 지지.

## 5. 정보 활용

- 실적 발표(어닝 서프라이즈)·가이던스를 EP 촉매로. 어닝 캘린더 사전 점검.
- 기관·외국인 신규 매수(분기 변화)로 I(institutional) 보강.

## 6. KRX 적용

- ADR·1× ADR 손절은 한국 변동성에 그대로 적용. 단 ±30% 제한으로 EP 갭이 상한가에 막혀 진입 곤란(상한가 풀린 다음날 추적).
- RS Rating은 국내 시장대비 수익률 순위로 대용. 거래세로 회전 비용↑ → 손익비 관리.

## 7. 비판과 한계

VCP·돌파는 강추세장(2003·2009·2020·2023)에 강하고 횡보장 false breakout 빈번. 신고가 매수라 심리적 저항 큼. 엄격한 손절(−7~8%/1×ADR) 없이는 비대칭 리턴 붕괴.
- Trend Template 8번 항목(RS Rating ≥70)도 시총가중 벤치마크 대비라 메가캡 쏠림 국면에서 왜곡될 수 있음 — `references/benchmark-guardrails.md` 참조.
