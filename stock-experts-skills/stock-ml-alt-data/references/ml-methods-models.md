# 레퍼런스(심화) — ML 모델·피처 엔지니어링 (실전)

> 목적: López de Prado 방법론 위에 **어떤 모델·피처가 실제로 통하는가**. 금융 시계열의 특수성 반영.
> 웹 출처: dtsystems(XGBoost vs LSTM), Stefan Jansen(GBM for trading), arxiv(ML multi-factor), mdpi(LSTM+RF).

## 1. 핵심 교훈 — 피처가 알파, 모델은 그릇

- 금융 시계열은 신호대잡음이 낮고 비정상 → **피처 엔지니어링이 진짜 알파의 원천**(원시 가격 학습 아님).
- 일간 정형(tabular) 데이터에선 **Gradient Boosting(XGBoost·LightGBM)이 LSTM·Transformer를 대체로 능가**(딥러닝 대비 1~3%p 내, 튜닝·연산은 훨씬 적음).
- 딥러닝(LSTM/Transformer)은 고빈도·텍스트·대용량 비정형에서 우위.

## 2. 피처 엔지니어링

- **Fractional Differentiation**(López de Prado): 정상성 확보 + 기억(memory) 최대 보존(단순 수익률 변환의 정보 손실 회피).
- 기술적 피처: 이동평균·모멘텀·변동성(ATR)·RSI/MACD, 거래량·유동성, 캘린더·계절성.
- 펀더/대안 피처: 밸류·퀄리티 팩터, 수급(외국인·기관), 센티먼트(→ [[alt-data-nlp-sentiment]]).
- 구조적 변화(structural break)·레짐 피처.

## 3. 모델 계열

| 모델 | 적합 |
|---|---|
| Random Forest / GBM(XGBoost·LightGBM) | 정형·일간, 비선형·상호작용, 특성중요도 |
| LSTM/GRU | 순차 의존·고빈도 |
| Transformer | 장기 의존·멀티모달(텍스트+가격) |
| 앙상블(트리+LSTM) | 강건성·분산 |

## 4. 검증 (필수)

- **walk-forward 5+ folds 최소**, purge+embargo / CPCV, DSR·PBO(→ [[lopez-de-prado-ml]], [[backtesting-methodology]] 차용).
- 시계열 무작위 분할·look-ahead 금지. 하이퍼파라미터 튜닝도 과적합원 → 시도 횟수 보정.

## 5. 라벨·타깃

- triple-barrier·meta-labeling(방향+크기), 분류 vs 회귀 선택, 클래스 불균형 처리.

## 6. 정보 활용

- 대안데이터·센티먼트를 피처로 결합([[alt-data-nlp-sentiment]]). 펀더·기술·수급의 다중 정보 융합이 ML의 강점.

## 7. KRX 적용

- 샘플(종목·기간) 작아 과적합 위험↑ → 트리 모델 + 강한 정규화·CPCV 보수적. 딥러닝은 데이터 부족으로 불리한 경우 많음.
- 외국인/기관 순매수·공시·뉴스가 국내 핵심 피처. 레짐 단절(IMF·코로나·공매도 금지) 혼입 주의.

## 8. 비판과 한계

낮은 신호대잡음에서 ML 알파 보장 없음. 복잡 모델일수록 과적합·해석 곤란(블랙박스). 일간 데이터에 딥러닝은 과잉(트리가 더 빠르고 강건). 모든 성과는 비용 차감·아웃샘플로만 검증.
