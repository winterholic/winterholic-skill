# 레퍼런스(심화) — 오더플로우·볼륨 프로파일 도구 모음

> 목적: Al Brooks 프라이스액션을 **거래량 구조·오더플로우** 로 보강. 데이트레이딩의 핵심은 "어디에 매물이 쌓였나(가격)"와 "지금 누가 공격적인가(주문)".
> 웹 출처: orderflowlabs·tradingview(volume/footprint), trader-dale(VWAP+VP), quantvps(footprint vs VP).

## 1. Volume Profile (가격대별 거래량)

세로축 가격대별 누적 거래량 → 매물 분포 파악.
- **POC (Point of Control)**: 최대 거래량 가격 = 시장이 가장 동의한 "공정가". 자석처럼 가격을 끌어당김.
- **VAH / VAL (Value Area High/Low)**: 거래량 70%가 집중된 구간의 상·하단 = "수용된 가격 범위".
- **HVN/LVN**(High/Low Volume Node): 두꺼운 노드=지지/저항, 얇은 노드=빠른 통과 구간.
- 종류: Session VP, Visible Range VP, Fixed Range VP(특정 구간).

## 2. Market Profile (TPO) & 80% Rule

- TPO(Time Price Opportunity): 시간대별 가격 분포로 시장 균형/불균형 판단.
- **80% Rule**: 가격이 전일 Value Area 밖에서 출발 후 다시 VA 안으로 복귀하면, 약 80% 확률로 VA 전체를 관통.
- 균형(balance, 횡보) vs 불균형(imbalance, 추세) 판별 → Brooks의 추세/횡보 모드와 직접 연결.

## 3. VWAP (거래량가중평균가)

- 기관 체결 벤치마크. 일중 평균 단가 기준선.
- **VWAP 밴드**(±1·2σ): 평균회귀(밴드 끝 페이드) vs 추세(밴드 타고 상승) 판단.
- VWAP 위=매수 우위, 아래=매도 우위. 되돌림 진입의 기준선.

## 4. Order Flow & Footprint (주문 단위)

- **Footprint 차트**: 각 봉의 가격대별 매수/매도 체결량 표시.
- **Imbalance(불균형)**: 한쪽(매수 또는 매도)이 압도 → 공격적 주문 방향.
- **Absorption(흡수)**: 대량 매도가 나오는데 가격이 안 빠짐 = 큰손 매수 흡수(반전 신호).
- **Delta**: 매수체결−매도체결 누적. 가격과 델타의 다이버전스 = 동력 약화.

## 5. Confluence "Combo" (정보 결합)

여러 독립 근거가 한 가격에 겹칠 때 신뢰도↑: 예) VWAP + VP의 HVN + 전일 고점 + Brooks 신호봉이 같은 가격 → 고확률 진입 구간. 단일 지표보다 **다중 confluence**가 핵심.

## 6. 인트라데이 셋업 (프라이스액션 + 볼륨)

- **Opening Range Breakout(ORB)**: 장 시작 N분 고/저 돌파 + 거래량 확인.
- POC/VAL 지지 매수, VAH 저항 매도(횡보장). 돌파+리테스트(VA 가장자리)에서 진입.

## 7. 정보 활용

- 호가창(L2)·체결 테이프(time&sales)로 실시간 공격성 읽기(전통 tape reading의 현대판).
- 프로그램매매·외국인 순매수 흐름을 일중 방향 보조 증거로.

## 8. KRX 적용

- VWAP·Volume Profile은 KRX 분봉에 동일 적용. 단 점심(11:30~13:00) 유동성 저하로 VP 왜곡.
- 동시호가(09:00/15:20)·VI 발동이 footprint 연속성을 끊음 → 단일가 구간 제외하고 해석.
- 신용·미수 반대매매 시간대(특정 종목)의 비정상 매물 주의.

## 9. 비판과 한계

오더플로우·VP는 **선물·고유동성**에 강하고 저유동 개별주는 신호 왜곡. 데이터·플랫폼 비용 큼(Bookmap 등). 과도한 화면 정보가 오히려 판단을 흐림 → confluence 2~3개로 압축. 개인 단타 장기 수익률은 구조적으로 낮음.
