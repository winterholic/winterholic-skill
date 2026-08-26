# 파생상품 계약·수급 메커니즘

> 검증일: 2026-07-31. 계약명은 범주 지식이고, 실제 상장·거래 여부와 명세는 분석일에 재확인한다.

## 1. 계약을 읽는 공통 체크리스트

```text
venue / product / symbol
underlying / contract_month / expiry / last_trade_date
contract_multiplier / tick_size / tick_value
initial_margin / maintenance_margin / daily_mark_to_market
exercise_style / settlement_type / deliverable / CTD
price_limit / session / currency
```

계약승수·틱가치·증거금 없이 레버리지와 손익을 말하지 않는다. 선물은 일일정산되고,
만기에는 현금결제 또는 실물인도가 발생한다. 국채선물은 인도가능채권과 CTD,
전환계수를 확인한다.

- [KRX 선물 결제](https://global.krx.co.kr/contents/GLB/06/0603/0603010802/GLB0603010802.jsp)
- [KRX 증거금 구조](https://global.krx.co.kr/contents/GLB/06/0608/0608030101/GLB0608030101.jsp)

## 2. KRX 주요 계약 레지스트리

| 범주 | 명시적으로 확인할 계약 | 상태 표기 |
|---|---|---|
| 주가지수 | KOSPI200·미니·KOSDAQ150·KRX300 선물, 월물·위클리 옵션 | current 여부를 거래일에 확인 |
| 개별주식·ETF | 개별주식선물·옵션, ETF선물 | 종목별 상장·유동성 확인 |
| 금리 | 3년·5년·10년·30년국채선물, 3개월 KOFR 선물 | current |
| 통화 | 미국달러·엔·유로·위안 선물, 미국달러옵션 | 통화별 선물/옵션을 분리 |
| 변동성·원자재 | V-KOSPI200선물, 금선물, 돈육선물 등 | 거래량과 상장 상태 재확인 |

- [KRX 30년국채선물](https://global.krx.co.kr/contents/GLB/02/0201/0201040506/GLB0201040506.jsp)
- [KRX 3개월 KOFR 선물](https://global.krx.co.kr/contents/GLB/02/0201/0201040505/GLB0201040505.jsp)
- [KRX 통화 파생상품](https://global.krx.co.kr/contents/GLB/96/9600000000/GLB9600000000.jsp)

종합 상품목록과 개별 상품 페이지가 충돌하면 개별 계약 페이지·당일 거래대상
공지가 우선한다. FLEX 등 과거 자료에만 보이는 상품은 `확인 필요`로 둔다.

## 3. 선물곡선·롤

- 콘탱고: 원월물이 근월물보다 비싼 곡선.
- 백워데이션: 근월물이 원월물보다 비싼 곡선.
- 총수익은 현물 변동뿐 아니라 carry·롤수익률·담보수익의 영향을 받는다.
- 연속선물은 단순 연결, 차이조정, 비율조정 방식에 따라 가짜 갭과 장기수익률이 달라진다.

보고할 값:

```text
front / next / spread / annualized_basis
days_to_expiry / roll_window / continuous_adjustment
inventory_or_carry_driver
```

## 4. 가격과 미결제약정

| 가격 | OI | 1차 해석 | 필수 반증 |
|---|---|---|---|
| 상승 | 증가 | 신규 롱 우위 가능 | 숏도 동시에 생성되므로 참여자·베이시스 확인 |
| 상승 | 감소 | 숏커버 가능 | 거래량·만기 롤 확인 |
| 하락 | 증가 | 신규 숏 우위 가능 | 헤지 수요·현물 매도 확인 |
| 하락 | 감소 | 롱 청산 가능 | 만기·강제청산 확인 |

COT·투자자별 포지션은 보고주기와 분류 차이를 명시한다. OI 하나만으로 순방향을
확정하지 않는다.

## 5. 옵션 표면·딜러 포지셔닝

필수 필드:

```text
strike / expiry / call_put / volume / OI
bid / ask / IV / delta / gamma / vega / theta
skew / term_structure / underlying_price
```

- 행사가별 OI와 거래량을 분리한다.
- 딜러 감마는 고객 포지션 방향을 알아야 부호를 추정할 수 있다.
- vanna·charm은 IV·시간 변화에 따른 델타 헤지 경로를 설명할 때만 사용한다.
- 만기 핀·0DTE·위클리 효과는 조건부 시나리오다.
- `max pain`을 확정 목표가격으로 쓰지 않는다.

## 6. 증거금·청산·기업행동

선물·옵션은 증거금률 변화, 일일정산, 강제청산과 포트폴리오 상계 때문에 같은
명목 익스포저라도 위험이 다르다. 교차증거금 여부와 브로커의 추가 증거금을 확인한다.

배당·액면분할·합병·분할·권리락이 있으면 선물 기준가격, 옵션 행사가·승수,
인도대상이 조정될 수 있다. 조정 전후 시계열을 그대로 비교하지 않는다.

