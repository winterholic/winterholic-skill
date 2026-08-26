# 레퍼런스(심화) — 합병차익거래 & 이벤트 유형 정량

> 목적: spinoff 외 **merger arbitrage(위험차익)** 의 정량 메커니즘과 이벤트별 수익·리스크 구조.
> 웹 출처: insidearbitrage·wallstreetprep·analystprep(CFA), alphaarchitect(merger spread), Wikipedia(risk arb).

## 1. Merger Arbitrage 메커니즘

- **Spread** = (인수가 − 현재가). 예: 인수가 $55, 현재가 $50 → spread $5 = 10%.
- **연율화 수익** = spread / 잔여기간. 10% spread가 6개월 후 종료 → 연 20%.
- 거래비용·차입·deal 실패 확률 차감 후 **현실적 spread 3~7%**, 레버리지·회전으로 net 연 7~12%(저상관).
- 현금 인수: target 매수. 주식 인수: target 매수 + acquirer 공매도(교환비율 헤지).

## 2. Deal Break Risk (핵심 위험)

- **넓은 spread = 시장이 보는 deal 실패 확률↑**. break 시 target가 급락(때로 −50%+).
- 위험 원천: ①규제·반독점(antitrust) ②자금조달(financing) ③주주 승인 ④실사·MAC 조항 ⑤경쟁 입찰 무산.
- 비대칭: 성공 시 작은 spread, 실패 시 큰 손실 → **분산(여러 deal)** 필수.

## 3. 학술 근거

- Baker & Savasoglu(1981–96, 1,901건): 분산 위험차익 포트 연 초과 +9.6%.
- Mitchell & Pulvino(1963–98, 4,750건): 연 6.2%, 시장 급락기에 손실(보험 매도형 수익 구조).

## 4. 이벤트 유형별 구조

| 유형 | 수익 원천 | 핵심 리스크 |
|---|---|---|
| Merger arb(현금) | 확정 spread 수렴 | deal break |
| Merger arb(주식) | 교환비율 + acquirer 헤지 | 비율 변동·acquirer 하락 |
| Tender offer | 공개매수가 vs 시장가 | 응모율·미달 |
| Spinoff | 강제매도 저평가([[greenblatt-special-situations]]) | 부채 떠넘기기 |
| Rights offering | 권리락 디스카운트 | 청약 불확실 |
| Index add/delete | 강제 매수·매도 | 선반영 |

## 5. 정보 활용

- 공시(합병계약서·증권신고서), 규제 일정(공정위·해외 antitrust), spread 추이(시장의 deal 확률 평가).

## 6. KRX 적용

- 한국 M&A는 **공개매수·소액주주 보호 제도 강화(2024~ 흐름)** 로 spread·의무공개매수 구조 변화 — 최신 제도 확인 필요.
- 합병비율 산정(자산·수익가치 가중)·반대주주 주식매수청구권 가격이 차익 구조의 변수.
- 물적분할·지주 전환의 가치 이전 방향 점검(미국 spinoff와 상이).

## 7. 비판과 한계

위험차익은 **시장 급락기에 동반 손실**(보험 매도형) — "평소 잔돈 줍다 가끔 큰 손실". deal break·규제 변수는 예측 곤란. 개인은 정보·실행·차입 우위 부족 → 분산·downside 한정 필수.
