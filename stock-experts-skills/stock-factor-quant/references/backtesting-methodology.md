# 레퍼런스(심화) — 백테스트 방법론 & 함정

> 목적: 모든 퀀트 전략의 사활 — **과적합·편향을 피하고** 현실적 성과를 추정. "학술 전략 90%+가 실전에서 실패"하는 이유를 막는다.
> 웹 출처: starqube·hedgefundalpha·frontierledger(pitfalls), luxalgo(survivorship), CFA(backtesting), López de Prado(DSR/PBO).

## 1. 3대 편향 (반드시 차단)

- **Overfitting(과적합)**: 파라미터가 많으면 노이즈까지 학습. 인샘플 성과는 아웃샘플을 보장하지 않음.
- **Look-ahead bias**: 실시간에 없던 정보 사용(발표 전 재무·정정 데이터). point-in-time 데이터로 차단.
- **Survivorship bias**: 현존 종목만 테스트 → 상폐·부도 제외로 수익 **연 1~4%p 과대**. 정확한 universe(상폐 포함) 필수.
- 기타: data snooping(다중 시도), 거래비용 누락, 미래 리밸런싱.

## 2. 검증 프레임

- **Train/Validation/Test 분리** + walk-forward(이동창 재최적화) — 시계열은 무작위 분할 금지.
- **Purged + Embargo CV / CPCV**(López de Prado, → [[lopez-de-prado-ml]]): 라벨 누수 차단·다중경로 분포.
- 시도 횟수 기록 → **DSR(Deflated Sharpe)·PBO(과적합 확률)** 로 운(luck) 보정.

## 3. 성과 지표 (단일 지표 금지)

| 지표 | 의미 |
|---|---|
| Sharpe | 초과수익/총변동성 (표준) |
| Sortino | 하방변동성만 (downside) |
| Calmar | 연수익/최대낙폭(MDD) |
| MDD | 최대낙폭(견딜 수 있나) |
| 승률·손익비·turnover | 실현 가능성·비용 |

## 4. 거래비용·실현 가능성

- 수수료+세금+스프레드+**시장충격**(→ [[harris-kissell-execution]]) 차감 후 net으로 판단.
- 용량(capacity): 전략이 키워도 알파 유지되나(소형주 알파는 자금 늘면 소멸).
- turnover↑면 비용·세금이 알파 잠식 → net Sharpe로.

## 5. 가설 우선 원칙

- "많은 백테스트로 찾은 패턴"이 아니라 **이론적 가설 → 검증** 순서. 사후 곡선맞춤 경계.

## 6. 정보 활용

- point-in-time 펀더(재무 정정 반영), 상폐 포함 universe, 실제 체결 가능 가격(호가).

## 7. KRX 적용

- 한국 데이터는 기간·종목 수 작아 과적합 위험↑ → CPCV·DSR 보수적, 거래세(매도) 반드시 포함.
- 상폐·관리종목 포함 universe로 survivorship 차단(FnGuide·WiseFn point-in-time 확인).
- 공매도 제약으로 long-short 백테스트는 실현 불가할 수 있음 → long-only로 재검증.

## 8. 비판과 한계

완벽한 백테스트도 **레짐 변화·구조 단절**(IMF·코로나·공매도 금지)엔 무력. 비용·용량 가정이 낙관적이면 실전 괴리. 결국 아웃샘플·실거래(페이퍼 트레이딩)로만 진짜 검증.
