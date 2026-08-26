# 레퍼런스 — Graham 딥밸류 (안전마진 · NCAV · Graham Number)

> 원저작: *Security Analysis* (Graham & Dodd, 1934), *The Intelligent Investor* (Graham, 1949).
> vault 소스: `sources/stock-investing/graham-margin-of-safety.md`, `graham-ncav-korean.md`.
> 이 문서는 스킬 실행용으로 가공된 요약이다. 임계값은 출발점이며 실데이터로 검증한다.

## 1. 안전마진 (Margin of Safety)

> "The function of the margin of safety is, in essence, that of rendering unnecessary an accurate estimate of the future." — *The Intelligent Investor*, Ch.20

- `MOS% = ((내재가치 − 시장가격) / 내재가치) × 100`
- 미래 추정의 부정확성과 시장 변동으로부터 원금을 지키는 완충재.
- 대공황(1929–32) 손실 경험에서 정립.
- 실무: 딥밸류는 보통 **MOS 33~50% 이상**을 요구(자산형일수록 크게).

## 2. Net-Net (NCAV) 정밀 정의

- NCAV = 유동자산 − 총부채 (장기자산을 0으로 간주하는 초보수적 청산가치).
- 매수: 시총 < NCAV × 2/3. 청산해도 유동자산만으로 부채 갚고 남는 잉여 > 시총.
- 변형: **NNWC(Net Net Working Capital)** — 자산 항목별 회수율 차등(현금 100%, 매출채권 75%, 재고 50%)으로 더 보수적.
- 출현 위치: 소외된 소형주, 일시적 악재 종목.

## 3. Graham Number

```
Graham Number = √(22.5 × EPS × BVPS)
22.5 = PER 15 × PBR 1.5 (Graham이 제시한 두 상한의 곱)
```
- 적용 조건: EPS > 0, 자기자본 양(+). 적자·자본잠식 기업엔 무의미.
- 단순 1차 필터일 뿐 — 자산 질·이익 지속성으로 보강.

## 4. Defensive vs Enterprising Investor

| | Defensive | Enterprising |
|---|---|---|
| 목표 | 큰 손실 회피 + 무난한 수익 | 평균 이상 수익 |
| 종목 | 대형·재무건전·배당지속 | 저평가·특수상황·net-net |
| 대상 | 대다수 일반 투자자 | 전업·시간 투입 가능자 |

### Defensive Investor 7 기준 (*Intelligent Investor* Ch.14)
적정 규모 · 유동비율 ≥ 2 · 10년 연속 흑자 · 20년 배당 이력 · 10년 EPS ≥ +33%(CAGR~3%) · PER ≤ 15(3년평균) · PBR ≤ 1.5 (또는 PER×PBR ≤ 22.5)

## 5. 한국시장(KRX) 적용 메모

- 한국은 **자산재평가·계열사 교차보유**로 장부가와 실질가 괴리가 큼 → 유동자산 회수율을 더 깎아본다.
- **코리아 디스카운트**: 저PBR이 거버넌스(낮은 배당·소액주주 경시)에서 기인하면 value trap. 밸류업 정책·행동주의 펀드 개입이 촉매가 될 수 있음(종목별 확인).
- net-net 후보 대다수가 소형주 → 관리종목·상장폐지·감사의견 거절 리스크를 정량스크린 전에 1차 배제.

## 6. 후대 영향

- Buffett: Graham에게 수학 → 초기 net-net → Munger 영향으로 quality compounder 진화(→ stock-quality).
- Seth Klarman *Margin of Safety*(1991), Walter Schloss, Tweedy Browne: net-net 계보 유지.

## 6.5 심화 — SKILL.md 비중복

- **Mr. Market 우화의 운용 의미**: 매일 호가를 제시하는 조울증 동업자 — 그의 가격은 *정보*가 아니라 *기회*다. 호가에 응할 의무가 없다는 것 자체가 개인투자자의 구조적 우위.
- **Graham-Rea 단순 기준(1976, 만년의 Graham)**: ① 이익수익률(E/P) ≥ AAA 회사채 수익률 × 2 ② 배당수익률 ≥ AAA 수익률 × 2/3 ③ 가격 ≤ 유형자산가치 2/3 (확인 필요: 원문 10기준 중 발췌). 금리 연동형 밸류에이션의 원형 — 저금리기엔 기준이 후해지는 함정도 같이 인지.
- **분산 규칙**: Graham 권고 10~30종목. 넷넷은 종목당 균등 비중(스토리 확신에 따른 차등 금지 — 통계 게임이므로).
- **청산가치 회수율 현실**: 실제 청산은 NCAV보다도 박하다(소송·청산비용·자산 헐값 처분). NCAV 2/3 룰은 그 마찰비용까지 흡수하는 장치 — 기준 완화는 안전마진 본질 훼손.
- **Enterprising 승격 조건**: Defensive→Enterprising은 수익 욕심이 아니라 **투입 시간**(주당 수 시간 이상 리서치)으로 결정. 시간 없이 Enterprising 종목(net-net·특수상황)을 사는 게 최악 조합.

## 7. 비판과 한계

- 무형자산 중심 현대 기업에 NCAV 부적용.
- **Value trap** — 싼 데는 이유(구조적 쇠퇴·부실경영)가 있을 수 있음.
- 촉매 부재 시 저평가가 장기 지속 → 분산·인내 필수.
- 회계기준·청산가능성이 다른 시장엔 그대로 적용 불가.
