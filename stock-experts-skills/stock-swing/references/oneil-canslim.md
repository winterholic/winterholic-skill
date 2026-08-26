# 레퍼런스 — William O'Neil (CAN SLIM)

> 원저작: *How to Make Money in Stocks*(1988~). IBD 창간. 1953–85 최우수 600여 종목 분석.
> vault 소스: `sources/stock-investing/oneil-canslim.md`. 스킬 실행용 가공본.

## 1. 개요

7개 머리글자 종목+시장 체크리스트. 펀더(C·A·N)+수급/기술(S·L·I)+매크로(M). 신고가 부근 주도 성장주.

## 2. 7기준

- **C** Current: 분기 EPS YoY ≥+25%, 매출 +25% 동반, 마진 개선이면 신뢰↑.
- **A** Annual: 3년 EPS 매년 성장 평균 +25%, ROE ≥17%.
- **N** New: 신제품·신경영·신시장·신고가 중 1+. 큰 상승주 95%가 "변화" 동반.
- **S** Supply/Demand: 적은 유통주식, 자사주·경영진 지분, 상승일 거래량>하락일.
- **L** Leader: 산업 1·2위, RS Rating ≥80, 산업군 상위 20%.
- **I** Institutional: 기관 신규매수 증가(over-owned 주의), smart money 가중.
- **M** Market: Confirmed Uptrend에서만 풀 포지션. distribution days 4~5주 5회+ 경고. 단계: Confirmed Uptrend / Under Pressure / In Correction.

## 3. Base 패턴

Cup-with-handle(손잡이 고점+0.10) / Double bottom(중간 고점 돌파) / Flat base(박스 상단) / Ascending base / High-tight flag(드묾·강력). depth 12~33%, 약세장 직후 40%+.

## 4. 매수 규칙

①시장 Uptrend ②7기준 충족 ③base 완성+pivot ④돌파 거래량 평소 +40%↑ ⑤돌파 당일 매수 ⑥진입가 ±5% 내만 추가.

## 5. 매도 규율

- 손절: −7~8% 무조건(가장 중요한 단일 규칙).
- 익절: +20~25% 부분. 단 8주 내 +20% 도달 시 최소 8주 보유.
- 매도 신호: climax top, distribution days, 50일선 거래량 동반 이탈, 3개월 추세선 하향.

## 6. 포트폴리오

4~8종목 집중 + 엄격 손절 = 비대칭 리턴. 손실 작게, 승자 키움.

## 7. IBD 도구

Composite Rating, IBD 50, MarketSmith, The Big Picture(M 코멘트).

## 8. 후대

Minervini *Trade Like a Stock Market Wizard*(SEPA), David Ryan, Dan Zanger. 한국 변형: 강환국·systrader79.

## 9. KRX 적용

거래세 부담→손익비·손절로 보완. RS·기관 데이터는 국내 RS·외국인/기관 순매수로 대용. ±30% 가격제한으로 돌파 양상 상이.
- **RS Rating의 구조적 한계**: IBD RS Rating은 원래 시총가중 벤치마크(SPY) 대비다. 코스피처럼 삼성전자·SK하이닉스 비중이 큰 지수를 그대로 쓰면 메가캡 랠리 국면에서 L(주도주) 기준이 반도체로 편중되거나 전멸한다(2023–2024 미국 Magnificent 7 실증). 동일가중/ex-메가캡 벤치마크 병행 산출 필요 — `references/benchmark-guardrails.md`.
- 2026-05-27 국내 삼성전자·SK하이닉스 단일종목 레버리지 ETF/ETN 18종 상장으로 이 두 종목의 변동성·수급 쏠림이 더 커질 수 있음(확인 필요: 실제 유동성·베이시스 영향).

## 9.5 심화 — SKILL.md 비중복

- **Base 카운팅**: 강세장 시작 후 **1~2번째 base가 성공률 최고**, 3번째부터는 'late-stage base'로 실패율 급증(이미 다 아는 주도주 = over-owned). 몇 번째 base인지 세는 습관이 추격 매수를 거른다.
- **Shakeout 재진입**: −7~8% 손절은 재진입 금지가 아니다 — 손절 후 종목이 다시 base를 만들고 재돌파하면 신규 셋업으로 취급(O'Neil 본인도 같은 종목 2~3회 재진입). 손절의 비용은 보험료.
- **Climax top 정량 신호**: 장기 상승 말기에 **2~3주에 +25~50% 급등**, 상장 후 최대 일간 상승, exhaustion gap, 최대 거래량 — 가장 좋아 보이는 날이 파는 날(확인 필요: 임계 수치).
- **50일선 운용**: 기관의 방어선 — 첫 50일선 터치는 추가매수 기회, **거래량 동반 이탈**은 기관 이탈 신호로 매도. '터치'와 '이탈'을 거래량으로 구분.
- **물타기 절대 금지 / 불타기만**: 평균 단가는 올리는 방향으로만(상승 중 ±5% 내 피라미딩). 내려가는 종목에 추가하는 순간 CANSLIM이 아니다.

## 10. 비판과 한계

추세장 강·횡보장 false breakout. 신고가 매수=항상 비싸 보임. 거래 빈도·세금. M 후행성.

## 11. 작성 예시 전문 (가상 종목)

```
## (가상) H성장주 CAN SLIM 분석
### 시장 M: Confirmed Uptrend
### 7기준: C +32% / A 3년 +28% / N 신고가+신제품 / S 상승일 거래량 우위 / L RS 88·산업 상위 / I 기관 신규매수 ✅
### Base 패턴: cup-with-handle / pivot 45,200 / 돌파 거래량 +52%
### 한 줄 결론: 매수
### 진입 45,300 / 손절 41,800(−7.7%) / 익절: +20~25% 부분, 8주 내 +20%면 보유 연장
### 확인 필요: ㉠RS Rating 국내 대용(시장 대비 수익률 순위) → L 확정
```

SKILL.md 출력 템플릿(§"출력 템플릿")을 이 예시대로 채우면 된다. 위 값은 전부 가상이며 실데이터로 대체할 것.
