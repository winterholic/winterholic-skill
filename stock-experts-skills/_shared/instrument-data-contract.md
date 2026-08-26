# 시장상품 데이터 가용성·출력 계약

## 1. 상품 레지스트리

상품을 근거로 사용하려면 다음 메타데이터를 유지한다.

```text
instrument_id:
venue:
product_family:
underlying:
status: current | planned | suspended | delisted | 확인 필요
official_source:
verified_at:
contract_spec_verified_at:
```

거래소 종합 목록과 개별 페이지가 충돌하면 `확인 필요`로 낮추고 당일 거래대상
조회로 해결한다. 개별 티커를 정적 문서에 전수 저장하지 않는다.

## 2. 데이터 가용성

```text
source:
collector:
table_or_endpoint:
availability: realtime | delayed | end_of_day | manual | unavailable
freshness:
observed_at:
ingested_at:
timezone:
session:
fields_available:
fields_missing:
quality_flags:
```

`availability`가 unavailable이거나 `freshness` 기준을 넘으면 중립이 아니라 `미관측`이다.
가격만 있고 거래량·OI·기초자산 괴리가 없으면 `price_only` 품질 플래그를 붙인다.

## 3. 분석 최소 필드

```text
instrument / venue / session
observed_at / quote_age / currency
contract_or_maturity / expiry
price / reference_price / price_change
volume / open_interest
basis_or_nav_gap / bid_ask_spread
signal_interpretation / counterevidence
availability / data_gaps
```

필수값이 없을 때:

1. 같은 경제변수를 나타내는 공식 대체상품을 찾는다.
2. 대체상품의 세션·기초자산 차이를 명시한다.
3. 대체도 없으면 방향 판정을 보류한다.
4. 브리핑에는 “영향 없음” 대신 어떤 필드가 미관측인지 적는다.

## 4. 브리핑 신선도

- `observed_at`이 브리핑 생성시각보다 미래면 폐기한다.
- 일봉을 실시간 야간 시세로 표시하지 않는다.
- 현물 종가와 현재 선물 가격을 비교할 때 공통 기준시각을 기록한다.
- 휴장·DST·조기폐장·롤오버면 `quality_flags`에 남긴다.
- 동일 사건·동일 가격상태를 반복할 때는 `no_new_edge`로 제외한다.

## 5. 현재 sample-service 배선 점검표

| 데이터 | 기대 필드 | 미지원 시 판정 |
|---|---|---|
| KRX 야간 지수선물 | 현월·차월, 가격, 거래량, OI, 베이시스 | 야간 방향 판정 보류 |
| 미국 지수선물 | 지연 5분 가격·직전 일봉 대비 수익률 수집, OI·베이시스 미지원 | `price_only`로 제한하고 신규 포지션 방향은 단정 금지 |
| KRX 옵션 | 행사가·만기별 가격, IV, OI, 거래량 | 풋콜·감마 판정 보류 |
| NXT | venue별 체결·거래대금·호가 | 08:00~20:00 국내 반응 미관측 |
| ETF | NAV/iNAV, 괴리, 설정·환매 | 수급 원인을 ETF 매수로 단정 금지 |
