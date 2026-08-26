# 레퍼런스(심화 2) — 시장 타이밍(M) · 베이스 카운팅 · 매도 규율

> 목적: CANSLIM의 "M(시장 방향)"과 베이스 단계 판정을 IBD 실무 규칙으로 정밀화. 진입보다 **언제 사지 말아야 하는가**가 핵심.
> 웹 출처: traderlion·quantifiableedges(FTD), grokipedia·nasdaq(distribution day), yahoo/IBD(base).

## 1. Follow-Through Day (FTD) — 바닥 확인

- 하락 후 반등 시도의 **4~10일째**, 지수가 **+1.7% 이상 상승 + 전일보다·50일평균보다 큰 거래량**.
- 의미: 기관 자금이 실제로 들어온 신호 = "Confirmed Uptrend" 전환.
- **모든 강세장은 FTD로 시작**했으나, FTD의 성공률은 약 50% → 필요조건이지 충분조건 아님(이후 distribution으로 무효화 가능).

## 2. Distribution Day — 천장 경고

- 지수가 **−0.2% 이상 하락 + 전일보다 큰 거래량**(기관 매도 흔적).
- **4주 내 4~5회 누적** → 시장 약세 경고, 신규매수 축소.
- 1회는 **25거래일 후 만료**(또는 +5% 상승 시 무효).
- M 단계: Confirmed Uptrend → Uptrend Under Pressure → Market in Correction.

## 3. 베이스 카운팅 (Base Count)

- Stage 2 상승 중 형성되는 base를 순번으로 셈(1차·2차·3차…).
- **후기 베이스(3rd·4th stage)는 실패율↑** — 이미 많이 오른 뒤라 기관이 분배. 1~2차 베이스가 안전.
- base 내 **accumulation 단서**: 상승일 거래량 > 하락일, 타이트한 종가, 매물 소화.
- 베이스 리셋: 큰 하락(예 base 저점 이탈)이면 카운트 초기화.

## 4. 매수 품질 점검 (진입 정밀화)

- pivot 돌파 시 거래량 평소 +40~50%↑.
- 진입가 ±5% 내에서만 추가(extended 회피).
- 돌파 후 즉시 −2~3% 되밀림(undercut)이면 셋업 약화 신호.

## 5. 매도 규율 (공격/방어)

- **방어 손절: −7~8% 무조건**(가장 중요).
- 공격 익절: +20~25% 부분, 8주 내 +20% 도달 시 보유 연장.
- 매도 신호: climax top(폭등+거래량 폭증+위꼬리), distribution days 누적, 50일선 거래량 동반 이탈, 추세선 하향.

## 6. 정보 활용

- IBD Composite/RS Rating·산업군 순위로 L·주도주 확정(국내는 시장대비 수익률 순위로 대용).
- 어닝 시즌·가이던스로 베이스 후 촉매 점검.

## 7. KRX 적용

- FTD·distribution day는 코스피·코스닥 지수에 동일 적용(임계 −0.2%/+1.7%는 변동성 보정 검토).
- 외국인·기관 순매수 누적을 distribution/accumulation 보조 지표로.
- ±30% 제한으로 climax top 위꼬리가 상한가에 가려질 수 있음.

## 8. 비판과 한계

M 신호는 후행 — 전환을 미리 못 잡음. FTD 50% 성공률은 단독 신뢰 불가(distribution과 함께 봐야). 잦은 매매로 거래세 부담. 후기 베이스 판정은 사후적으로 명확.
- **메가캡 쏠림 국면 취약성**: 소수 대형주가 지수를 견인하면 FTD가 breadth(상승/하락 종목 비율) 동반 없이도 발생할 수 있어 신뢰도가 추가로 낮아진다. 2023–2024 미국 Magnificent 7처럼 상위종목 비중이 급증하는 국면에서는 지수 등락률과 별도로 breadth를 반드시 병행 확인할 것. 상세는 `references/benchmark-guardrails.md`.
