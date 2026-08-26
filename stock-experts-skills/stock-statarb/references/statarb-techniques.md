# 레퍼런스(심화) — 통계차익 기법 (Johansen·OU·Kalman·Hurst·Bollinger·Copula)

> 목적: Chan 기본편을 넘어 **공적분 추정·동적 헤지·레짐 판별**의 정량 기법.
> 웹 출처: jonathankinlay(Kalman/cointegration), Meucci(OU review), macrosynergy·quantinsti(Hurst), arxiv(Bollinger 30년·copula).

## 1. 표준 워크플로우 (Meucci/Chan)

1. **Johansen 절차**로 다변량 공적분 추정(2개 이상 자산).
2. 스프레드를 **Ornstein-Uhlenbeck(OU)** 로 모델링 → **half-life**(평균회귀 속도) 산출.
3. 스프레드 **z-score**에 비례한 포지션. ±임계 진입, 0 청산.

## 2. Kalman Filter (동적 헤지비율)

- 정적 회귀 β의 한계 보완 — **시간가변 β**를 베이지안 갱신으로 추정.
- 관계가 서서히 변하는 페어에 강건. 스프레드·z-score를 실시간 정제.

## 3. Hurst Exponent (레짐 판별)

- **H<0.5 평균회귀 / ≈0.5 random walk / >0.5 추세**. 페어 적합성의 사전 진단.
- 실시간 레짐 측정 → 평균회귀 전략을 켤지/끌지 판단(추세 레짐에서 평균회귀는 손실).

## 4. 진입 신호: Bollinger vs Z-score

- Bollinger Bands(이동평균±kσ)는 z-score 대비 더 효과적이라는 연구도(테스트 기간 의존).
- 임계는 **거래비용 초과 폭** 으로(net positive 보장).

## 5. Copula 기반 (비선형 의존)

- 선형 공적분의 한계 보완 — 조건부확률로 비선형·비대칭 의존 포착. 공적분이 깨지는 구간에 대안.

## 6. Regime Switching

- 시장은 추세↔횡보 레짐을 전환 → 레짐 판별(Hurst·HMM) 후 전략 on/off. 잘못된 레짐 적용이 손실 원천.

## 7. 정보 활용

- 경제적 동질성(같은 산업·대체재·우선주/보통주)으로 페어 후보 선별 — 통계적 우연 회피.
- 차입공매도 가능성·비용(실행 제약, → [[harris-kissell-execution]]).

## 8. KRX 적용

- 우선주-보통주, 지주-자회사, 동일산업 대형 페어. 공매도 제약 → ETF·선물·우선주 long 대체.
- 우선주 괴리는 구조적으로 지속될 수 있어 손절(z 한도) 필수.

## 9. 비판과 한계

공적분은 과거 통계 성질 — **구조 변화 시 발산**(decoupling). 추정(β·half-life)은 표본 의존. 고빈도일수록 거래비용·지연이 우위 잠식. 과적합 위험 → CPCV/DSR 검증([[backtesting-methodology]] 차용).
