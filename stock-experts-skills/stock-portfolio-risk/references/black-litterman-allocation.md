# 레퍼런스(심화) — 자산배분 (Black-Litterman·CVaR·Risk Parity)

> 목적: MPT의 추정오차·코너해 문제를 **Black-Litterman·꼬리위험 최적화**로 보완. 시그널을 안정적 비중으로.
> 웹 출처: MIT/BU(Black-Litterman), PMC/Springer(BL + mean-CVaR), uliege(risk parity+momentum).

## 1. Black-Litterman (BL)

- MPT 단순 최적화의 문제: 입력 민감 → 극단·비분산 비중("error maximization").
- BL: **시장 균형 수익률(역최적화)** 을 prior로 두고, 투자자 **views(전망)** 를 신뢰도와 함께 베이지안 결합 → 안정적·분산된 비중.
- views: 절대("A는 8% 수익") 또는 상대("A가 B를 3%p 상회"), 확신도(불확실성)로 가중.

## 2. 꼬리위험 최적화

- 평균-분산 대신 **mean-CVaR**(꼬리손실 최소화) 최적화 — 비대칭·두꺼운 꼬리 반영.
- BL views를 copula·ARMA-GARCH 기대수익과 결합한 mean-CVaR 프레임(연구).
- 제약: 최대낙폭(MDD), 단일/섹터 비중 한도, 회전율.

## 3. Risk Parity 통합

- 위험기여 균등([[dalio-macro]]) + 모멘텀/BL view로 비중 틸트 → 균형과 전망의 절충.
- 저변동 자산 레버리지로 위험기여 동일화(단 레버리지 리스크).

## 4. 변동성 타게팅 & 드로다운 통제

- **Vol targeting**: 실현변동성에 반비례해 익스포저 조절 → 위기 자동 디레버리징, 평시 레버리지.
- **Drawdown control**: MDD 한도 접근 시 비중 축소(CPPI류). 복리 붕괴 방어([[taleb-spitznagel-tail]] volatility tax).

## 5. 상관 레짐

- 평시 상관에 기댄 분산은 **위기 시 상관 1 수렴**으로 붕괴 → 스트레스 상관·레짐별 공분산으로 재추정.

## 6. 정보 활용

- 시가총액(균형 prior), 시그널 전문가의 view + 확신도, 위기 시나리오 공분산.

## 7. KRX 적용

- 원화 자산만으론 분산 약 → 미국주식·달러·금·국채 결합으로 BL 유니버스 확장.
- 위기 시 외국인 동반매도로 상관 급등 → 스트레스 상관 필수. 공매도 제약으로 long-only BL.

## 8. 비판과 한계

BL도 view·확신도·균형 prior 가정에 의존(쓰레기 입력 시 쓰레기 출력). CVaR 추정은 꼬리 표본 부족에 취약. risk parity는 채권 레버리지 의존(2022 동반 하락). 모든 최적화는 추정오차 — 단순·강건 우선.
