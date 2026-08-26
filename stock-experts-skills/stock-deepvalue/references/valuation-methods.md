# 레퍼런스(심화) — 내재가치 평가법 (DCF·DDM·잔여이익·역DCF·SOTP)

> 목적: NCAV·Graham Number를 넘어 **현금흐름 기반 내재가치** 산정으로 안전마진을 정밀화.
> 웹 출처: CFA Institute(DDM·FCF), footnotesanalyst(RI vs DCF), HBS(DCF), efinancialmodels.

## 1. DCF (현금흐름할인)

- 내재가치 = 미래 잉여현금흐름(FCF)의 현재가치 합.
- `Equity Value = Σ FCF_t/(1+r)^t + TV/(1+r)^n`, TV(말단가치)=FCFn(1+g)/(r−g).
- 할인율 r = WACC(기업가치) 또는 자기자본비용(주주가치).
- 약점: **말단가치 민감도**가 매우 큼(가정 변화에 가치 급변).

## 2. DDM (배당할인) & Gordon Growth

- 성숙·배당 기업에 적합: `P = D1/(r−g)`(고든 성장). 다단계 DDM으로 고성장→안정 전환 반영.
- 무배당 기업엔 부적용 → FCF/RI로 대체. (배당 중심은 [[weiss-dividend-yield]] 연계)

## 3. Residual Income (잔여이익)

- `가치 = 자기자본 장부가 + Σ(ROE−r)×자본의 현재가치`. 초과이익(ROE>자본비용)만 가치 창출.
- **장점**: 말단가치 의존도가 DCF보다 낮아 안정적. 장부가가 가치의 큰 부분.

## 4. 상대가치 (Multiples)

- PER·PBR·EV/EBITDA·EV/EBIT·P/FCF·P/S. 동종·과거·성장률 대비 비교.
- EV/EBITDA는 자본구조·감가상각 무관 비교(Greenblatt EV/EBIT과 연결, [[greenblatt-special-situations]]).
- 시클리컬은 **정상화이익(normalized earnings)** 으로(정점/저점 PER 함정 회피).

## 5. Reverse DCF (역산)

- "현재가가 정당화하려면 시장이 가정한 성장률은?"을 역산 → 그 가정이 현실적인지 판단.
- 딥밸류엔 강력: 시장이 과도하게 비관(낮은 내재 성장)했는지 검증.

## 6. SOTP (Sum-of-the-Parts)

- 사업부·자산별 개별 평가 후 합산 − 순부채. 지주·복합기업·숨은 자산(asset play)에 필수.

## 7. 모델 등가성 & 실무

- DDM·FCF·RI는 이론상 같은 내재가치를 산출해야 함 → **여러 방법 교차검증** + 시나리오(약세/기본/강세)로 범위 제시.
- 단일 점추정 금지 — 안전마진은 내재가치 *범위*의 하단 대비로 본다.

## 8. KRX 적용

- 지주사 SOTP에 지주 디스카운트 반영. 시클리컬(반도체·화학) 정상화이익 필수.
- 낮은 배당성향으로 DDM 적용 제약 → FCF·RI 우선. 밸류업 정책으로 배당 가정 상향 가능(종목별 확인).

## 9. 비판과 한계

DCF는 가정(성장·할인율·말단가치)에 극도로 민감("garbage in, garbage out"). 상대가치는 동종집단이 동반 고평가면 왜곡. 모든 모델은 추정 — 정밀도 착각 경계, 범위·시나리오로.
