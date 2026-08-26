# 레퍼런스 — Markowitz · Kelly · VaR

> 원저작: Markowitz(1952), Kelly(1956), John Hull *Risk Management*.
> vault 소스: `sources/stock-investing/markowitz-kelly-portfolio-risk.md`. 스킬 실행용 가공본.

## 1. 정체성

"얼마나·어떻게 섞을까". 시그널을 위험조정 후 비중으로 변환(사이징 레이어).

## 2. MPT (Markowitz 1952)

자산=μ·σ²·상관(ρ). 상관 낮은 결합으로 위험↓. 효율적 투자선=주어진 위험서 수익 최대. 무위험 추가→CML, 접점=Tangency(시장) 포트→CAPM 연결.

## 3. Kelly Criterion

```
f* = edge/odds = (bp−q)/b        # 베팅형
f* ≈ (μ−r)/σ²                    # 투자형(Merton)
```
- Thorp가 *Beat the Dealer/Market*에서 적용·대중화.
- Fractional/Half-Kelly: 풀켈리 변동성 과다 → 1/2 켈리("수익 ~3/4, 변동성 절반"). 추정오차 안전마진.

## 4. VaR & CVaR

VaR=신뢰수준·기간 내 예상 최대손실(분산-공분산/역사적/몬테카를로). CVaR(ES)=VaR 초과 손실 기대값(꼬리 측정). Hull=실무 교과서.

## 5. 추가 도구

Risk Parity(위험기여 균등) · 변동성 타게팅 · MDD·리스크 버짓팅 · Black-Litterman(추정오차 보완).

## 6. KRX 적용

위기 시 외국인 동반매도로 상관 급등(분산 증발)→스트레스 상관 재점검. 원화만으론 분산 약→미국주식·달러·금. 공매도 제약→long-only 비중·현금으로 조절.

## 6.5 심화 — SKILL.md 비중복

- **추정오차의 서열(Chopra-Ziemba)**: 기대수익 추정오차가 분산 오차보다 ~11배, 공분산 오차보다 ~21배 해롭다(확인 필요: 정확 배수) — 함의: μ 추정에 자신 없으면 **μ를 아예 안 쓰는 방법**(risk parity·최소분산·동일비중)이 최적화보다 낫다.
- **Shrinkage(Ledoit-Wolf)**: 표본 공분산을 구조화된 타깃으로 수축시켜 추정 노이즈 축소 — 종목 수가 표본 기간 대비 많을 때 필수. '추정오차 대응 3종': shrinkage(공분산), Black-Litterman(기대수익), fractional Kelly(사이징).
- **풀켈리의 드로다운 분포**: 풀켈리 베팅은 자본이 현재의 x배율까지 떨어질 확률이 대략 x — 즉 **절반까지 드로다운 확률 ~50%**(확인 필요: 연속 근사 가정). 수학적 최적이 심리적으로 운용 불가능한 이유의 정량화 → ½켈리가 실무 표준.
- **Portfolio heat**: 모든 포지션의 '손절까지 거리×비중' 합계 = 동시 최악 손실 — 종목당 1~2% 룰이 있어도 heat 합계가 10%를 넘으면 상관 급등 시 한 번에 −10%. 포지션별이 아니라 **합계로 관리**.
- **Risk of ruin**: 승률 p·손익비 b·베팅비율 f가 고정일 때 파산확률은 f에 지수적으로 민감 — 같은 전략도 f 2배면 파산확률은 제곱이 아니라 그 이상으로 뛴다. '조금 더 크게'의 비선형 대가.

## 7. 비판과 한계

MPT 정규분포·안정상관 가정→위기 상관 1·두꺼운 꼬리. 입력 추정오차 극민감(error maximization). 풀 Kelly 드로다운·파산 위험→fractional. VaR은 초과손실 크기 침묵→[[stock-tail-risk]] 보강.
