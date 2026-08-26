# ETP·권리·구조화상품 레퍼런스

> 검증일: 2026-07-31. 개별 상품의 투자 가능 여부·과세·교육·기본예탁금은 계좌와 규정에 따라 재확인한다.

## 1. ETF

ETF는 거래소에서 거래되는 가격과 펀드의 NAV가 동시에 존재한다.

```text
market_price / NAV / iNAV / premium_discount
tracking_difference / tracking_error
AP / LP / creation_unit / PDF_basket
creation / redemption / fund_flow
securities_lending_income / fee / FX_hedge
```

AP(지정참가회사)는 CU 단위 설정·환매로 1차시장 바스켓과 ETF를 교환한다.
설정·환매와 LP 호가가 괴리를 좁히지만, 해외 기초자산 휴장·급변·거래중단 때는
괴리가 정보일 수도 있다.

- [KRX ETF 설정·환매](https://global.krx.co.kr/contents/GLB/03/0303/0303090203/GLB0303090203.jsp)
- [KRX ETF 가격결정·LP](https://global.krx.co.kr/contents/GLB/02/0201/0201030203/GLB0201030203T8.jsp)

레버리지·인버스·커버드콜·버퍼·단일종목 ETF는 경로의존, 옵션 매도, 상방 제한,
집중위험을 각각 분리한다. 상품 이름의 `2X`를 장기 누적수익률 배수로 읽지 않는다.

## 2. 합성 ETF·ETN

- 합성 ETF: 스왑 상대방, 담보, 대체바스켓, 거래상대방 한도를 확인한다.
- ETN: 발행사 무담보 신용, 지표가치, 만기, 조기상환·가속상환, LP와 괴리를 확인한다.
- ETF의 별도 신탁재산을 ETN에도 있다고 가정하지 않는다.

## 3. ELW·신주인수권·권리증서

ELW는 옵션형 파생결합증권이고, 신주인수권증권·신주인수권증서는 기업의 신주를
인수할 권리다. 이름이 비슷해도 발행 목적과 희석 경로가 다르다.

권리 분석:

```text
subscription_price / exercise_ratio / expiry
rights_value / theoretical_ex_rights_price
new_shares / diluted_share_count / take_up_rate
market_rules / liquidity
```

KRX 권리시장은 일반 주식과 주문·가격제한 규칙이 다를 수 있다.

- [KRX 신주인수권·권리증서 거래](https://global.krx.co.kr/contents/GLB/06/0602/0602010202/GLB0602010202T7.jsp)

## 4. 채권·유동화·자본성 상품

| 유형 | 주식 분석 연결 |
|---|---|
| CB·EB·BW | 전환·교환·행사, 리픽싱, 잠재 희석, 풋·콜 |
| ABS·MBS | 담보풀, 조기상환, 트랜치, 부동산·소비자 신용 |
| 커버드본드 | 발행사 신용과 커버풀 이중상환 구조 |
| 물가연동국채 | 명목금리와 기대인플레이션·실질금리 분해 |
| 변동금리채 | 기준금리·스프레드·리셋주기 |
| 후순위·신종자본증권 | 콜 미행사, 이자지급 제한, 자본인정과 손실흡수 |

표면금리만 비교하지 말고 YTM·YTC·듀레이션·옵션조정스프레드를 구분한다.

## 5. ELS·DLS·ELB·DLB

- ELS·DLS: 비보장형 손실구조를 포함할 수 있다.
- ELB·DLB: 발행사 기준 원금지급형이지만 예금자보호나 무위험을 뜻하지 않는다.
- 공통: 기초자산, 배리어, knock-in/knock-out, 조기상환, 만기, 쿠폰,
  발행사 신용, 발행잔액과 만기 군집을 확인한다.

발행사의 동적 델타·감마 헤지가 현물·선물·옵션 수급에 미칠 수 있다. 공개 잔액이
없으면 `미관측 구조화 익스포저`로 남긴다.

## 6. CFD·대차·공매도

CFD는 증거금, 명목 익스포저, 반대매매, 상대방과 대량보유 공시를 확인한다.

대차는 다음을 분리한다.

```text
lendable / on_loan / utilization
borrow_fee / rebate / days_to_cover
recall / settlement_fail / short_volume / short_interest
```

대차잔고 증가는 공매도 체결과 같지 않고, 높은 차입수수료는 스퀴즈 연료인 동시에
정보거래자의 강한 약세 의견일 수 있다.

## 7. 펀드·현금관리·계좌 래퍼

- 공모펀드·폐쇄형펀드·BDC·REIT: NAV, 환매구조, 할인·프리미엄, 레버리지를 구분한다.
- MMF·CMA·RP: 대기자금과 단기금리 전달경로를 볼 때 사용하되 주식 방향상품으로 보지 않는다.
- 랩·신탁·ISA·연금계좌: 계좌·운용 래퍼이며 내부 보유상품과 리밸런싱 제약이 실제 익스포저다.
- 사모펀드·PE·VC·인프라·부동산펀드: 평가주기와 유동성 지연 때문에 상장가격과 같은 빈도로 비교하지 않는다.

이들은 개별 종목 추천의 기본 바스켓은 아니지만, 가계·기관의 현금 대기와 자산배분
이동을 설명할 때 조건부로 확인한다.
