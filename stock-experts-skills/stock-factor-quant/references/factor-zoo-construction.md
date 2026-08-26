# 레퍼런스(심화) — 팩터 동물원 & 멀티팩터 구성

> 목적: 6대 팩터의 실전 정의, 다중팩터 합성, **팩터 타이밍·크라우딩·decay** 등 운용 리스크.
> 웹 출처: AQR Funds(multi-factor·momentum·BAB), Research Affiliates(factor timing), arxiv(crowding/alpha decay), PMC(factor zoo).

## 1. 6대 지속 팩터 (60년+ 검증, 수익변동 90%+ 설명)

| 팩터 | 정의 | 대표 시그널 |
|---|---|---|
| Value | 싼 자산이 비싼 자산 능가 | B/M·E/P·FCF yield |
| Size | 소형주 프리미엄 | 시총(SMB) |
| Momentum | 최근 성과 지속 | 12-1개월·52주 신고가 |
| Quality | 우량 기업 능가 | ROE·gross profitability·낮은 부채 |
| Low-Vol/Defensive | 저베타 위험조정 능가 | 변동성·베타(BAB) |
| Yield/Carry | 고수익 자산 능가 | 배당수익률·carry |

## 2. 멀티팩터 구성 (combining)

- **두 방식**: ①Mixing(팩터별 포트 후 합성) ②Integrating(종목별 다중팩터 종합점수 후 선별 — 보통 우월).
- 가중: equal weight / IC(정보계수) weight / 위험 기여 균등 / 최적화.
- 효과: 팩터 간 저상관으로 분산(모멘텀↓일 때 퀄리티·로우볼이 방어).

## 3. 팩터 타이밍 (어렵다)

- Arnott(Research Affiliates): 밸류·최근성과 기반 팩터 타이밍은 **상시 배분보다 나빴음**. 타이밍보다 분산·인내.
- 단 극단적 밸류에이션 스프레드는 약한 신호로 참고 가능(논쟁적).

## 4. 크라우딩 & Alpha Decay

- 스마트베타 $1.6조 규모 → 같은 팩터에 자금 몰리면 프리미엄 압축·역전.
- 연구: 크라우딩 기반 팩터 선택은 알파 실패 + **꼬리위험 예측**(혼잡한 reversal 팩터의 crash 확률 1.7~1.8배).
- 출판·대중화 후 팩터 수익 축소(decay) — 신규 팩터일수록 의심.

## 5. 팩터 순환성 (regime)

- Value는 회복·금리상승기, Momentum은 추세장, Quality·Low-Vol은 침체·하락기에 상대 강세.
- 거시 국면([[dalio-macro]])·섹터([[stovall-sector-rotation]])와 결합 가능하나 타이밍은 신중.

## 6. 정보 활용

- Kenneth French·AQR 데이터로 팩터 시계열, 자체 종목 스코어링.
- 펀드 평가: 4~5팩터 회귀로 α 분해, α의 t-stat 유의성(→ [[fama-french-factors]]).

## 7. KRX 적용

- 한국 Value·Momentum 유효(IMF 전후 구조변화). 소형주 거래비용·공매도 제약 → long-only tilt.
- 가치+퀄리티 결합이 비교적 안정(강환국 PER+GP/A).

## 8. 비판과 한계

팩터 zoo는 300+ 보고(t-stat hacking·데이터 스누핑). 프리미엄 수년 부진(value 2018~2020). 크라우딩으로 감소·crash. **이론적 가설 우선**, 백테스트는 검증용([[backtesting-methodology]]).
