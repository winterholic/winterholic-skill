# 레퍼런스(심화) — RRG(상대순환그래프) & 섹터 상대강도

> 목적: 경기국면 판정의 사후성을 **상대강도 시각화(RRG)** 로 보완 — 실제 자금이 어느 섹터로 도는지 실시간 추적.
> 웹 출처: stockcharts ChartSchool·strike.money·relativerotationgraphs.com(Julius de Kempenaer).

## 1. RRG (Relative Rotation Graph)

- 2004~05 Julius de Kempenaer 개발. 여러 종목·섹터를 벤치마크 대비 동시 추적.
- **X축 JdK RS-Ratio**: 상대강도 추세(>100 강세). **Y축 RS-Momentum**: 상대강도 변화 속도. 교차점 100.

## 2. 4사분면 & 시계방향 순환

- **Leading**(우상): 상대강세 + 강한 모멘텀.
- **Weakening**(우하): 강세 유지하나 모멘텀 둔화.
- **Lagging**(좌하): 상대약세 + 약한 모멘텀.
- **Improving**(좌상): 약세이나 모멘텀 회복.
- 보통 **시계방향**: Improving → Leading → Weakening → Lagging → Improving 순환.

## 3. 11 GICS 섹터 적용

- SPY 대비 11개 섹터 ETF의 RRG가 가장 널리 관찰됨.
- Improving 진입 섹터를 선취매, Weakening 진입 시 차익 — 경기국면(Stovall)과 교차검증.

## 4. 상대강도(RS) 기반 로테이션

- 섹터 ETF RS 순위로 오버/언더웨이트. "국면(why, Stovall) + RRG/RS(when)" 결합([[stovall-sector-rotation]]).
- 모멘텀 팩터와 직접 연결([[factor-zoo-construction]]) — 섹터 모멘텀.

## 5. 정보 활용

- 섹터 ETF·업종지수 가격, 자금 흐름(ETF 순유입), 외국인·기관 업종별 순매수.

## 6. KRX 적용

- KRX 업종지수·섹터 ETF(TIGER/KODEX)로 RRG 구성. 단 한국은 IT(반도체)·2차전지 비중 과대 → RRG가 사실상 반도체 사이클 추적이 되기 쉬움.
- 외국인 업종별 순매수가 RS의 실효 동인.

## 7. 비판과 한계

RRG·RS는 **모멘텀 기반 = 후행**(전환점에서 늦음). 시계방향 순환은 자주 깨짐(중간 이탈·역행). 잦은 로테이션은 거래비용·세금 잠식. 좁은 시장(반도체 편중)에선 분산 효과 제한.
