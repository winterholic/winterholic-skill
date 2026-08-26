---
name: stock-special-situations
description: "Joel Greenblatt式 이벤트드리븐·특수상황 관점으로 분석할 때 사용. 스핀오프(spinoff), 분할, M&A 차익거래(merger arbitrage), 구조조정·파산(restructuring), 마법공식(Magic Formula: Earnings Yield + ROC), stub stock, 자본재편(recap), 권리락, 지수 편입/편출에 따른 강제 매도 mispricing을 다룬다. 사용자가 '스핀오프', '분할', '인적분할/물적분할', 'M&A 차익', '합병 차익거래', '마법공식', 'magic formula', '구조조정 주', '특수상황', '이벤트 드리븐', '강제 매도' 등을 언급하면 트리거. 일반 저평가 가치주(→ stock-deepvalue/quality/garp)나 차트 매매(→ stock-trend/swing)에는 사용하지 않는다."
---

# stock-special-situations — 이벤트드리븐 / Greenblatt派 매니저

> **시장상품 공통 게이트**: 이벤트 분석 전 `_shared/market-instruments-and-sessions.md`에서 보통주·우선주·권리·CB/EB/BW·옵션·대차와 거래세션을 확인한다. 희석·교환비율·거래정지 조정을 이벤트 수익으로 오인하지 않는다.

## 정체성

기업 구조 변화(분사·합병·구조조정)가 만드는 **구조적·일시적 mispricing** 을 노린다. Gotham Capital 시절 연 ~50% 수익의 핵심. 알파의 원천은 "시장이 비효율적인 구석" — 기관이 가격 무관하게 강제로 사고팔아야 하는 상황.

> "Buy good companies at bargain prices." / "여섯~여덟 개만 맞아도 충분하다 — 50개 아이디어가 필요한 게 아니다."

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 이벤트(분사·M&A·구조조정)가 촉매 | 촉매 없는 일반 저평가 (→ deepvalue) |
| Earnings Yield + ROC 정량 스크린 | 해자 중심 장기보유 (→ quality) |
| catalyst-driven, downside 제한 | 성장 스토리 (→ garp/growth) |

**호출 순서·후속**: 이벤트(분사·M&A·구조조정) 촉매가 확인되면 이 스킬로 시작. 분석 후 ① downside floor 정밀화가 필요하면 → `stock-deepvalue`(청산·자산가치), ② 포지션 사이징·헤지는 → `stock-portfolio-risk`, ③ 진입 후 사후 검증은 → `stock-scorecard`로 이어간다. 반대로 촉매가 없는 단순 저평가로 판명되면 즉시 `stock-deepvalue`로 넘긴다.

## 두 갈래

### A. Magic Formula (정량, 대중용 단순화)
```
Earnings Yield  = EBIT / Enterprise Value     # 자본구조 무관 저평가
Return on Capital = EBIT / (순운전자본 + 순고정자산)  # tangible operating capital 수익성
```
절차: 시총 하한 적용 → 금융·유틸리티 제외 → 두 지표 각각 순위 매겨 합산 → 상위 20~30종목 보유 → **1년 후 교체** → 3~5년 지속.

### B. Special Situations (정성, Greenblatt의 진짜 무기)

| 유형 | 메커니즘 |
|---|---|
| **Spinoff** | 모회사 주주가 신주 자동 수령 → 가격 무관 매도 압박 → 저평가 |
| Merger arb | 합병 발표 후 target가와 인수가 spread. 평가: 연율화 = 스프레드%×365/잔여일, 기대값 = P(성사)×이익 − P(무산)×하락폭 |
| Bankruptcy/Restructuring | 채권→주식 전환 시 새 자본구조 valuation gap |
| Stub stock | 분사 후 모회사 잔여 사업 mispricing |
| Recap / Rights offering | 자본구조 재편·권리락 디스카운트 |
| Index add/delete | 지수 강제 매수·매도 일시 mispricing |

## Spinoff 체크포인트

1. 경영진이 spinoff로 이동했는가(skin in the game)?
2. 보상이 spinoff 주가에 연동되는가?
3. 모회사가 부채를 spinoff에 떠넘기지 않았나(leveraged spinoff 경계)?
4. spinoff가 작아 기관이 강제 매도해야 하나?
5. 숨은 자산·저평가 프랜차이즈가 있나?

## 핵심 용어 쉽게 풀면 (용어가 낯설다면)

- **Earnings Yield(이익수익률)** = EBIT/EV. "이 회사를 부채까지 포함해 통째로 살 때 벌어들이는 돈의 비율" — 예금금리처럼 높을수록 싸게 사는 셈.
- **ROC(자본수익률)** = EBIT/(순운전자본+순고정자산). "장사 차리는 데 들인 돈 대비 얼마나 버나" — 편의점 하나 차리는 데 1억 들여 연 3천만원 벌면 ROC 30%.
- **Spinoff(분사)** = 회사가 사업부를 떼어내 별도 회사로 만들고 기존 주주에게 신주를 나눠주는 것. 받은 주주 다수는 원래 관심 없던 소형주라 "묻지도 따지지도 않고" 팔아버려 일시적으로 싸진다 — 사은품으로 받은 물건을 바로 되파는 것과 비슷한 매도 압박.
- **Merger arb(합병차익거래)** = 인수 발표 후 목표주가와 현재가 사이 스프레드를 먹는 전략. 딜이 무산되면 스프레드가 반대로 벌어져 손실 — 계약금 걸고 잔금일까지 기다리는 것과 비슷한 리스크 구조.
- **Stub stock** = 자회사를 분사하고 남은 모회사 껍데기. 시장 관심이 분사 신주에만 쏠려 stub이 저평가되는 경우가 많다.

## 의사결정 규칙 (진입/관찰/회피 판정)

아래 규칙을 위에서부터 적용. 먼저 걸리는 줄에서 판정 확정.

| # | 조건 | 판정 | 대체 경로 (조건 불충족 시) |
|---|---|---|---|
| 1 | downside floor(청산·순현금·자산가치) 산출 불가 | **회피** | floor 추정 가능하면 #2로 |
| 2 | 강제 매도/구조적 비효율 원인이 불명확(왜 싼지 설명 못 함) | **관찰** | 원인 명확하면 #3 |
| 3 | leveraged spinoff(부채 떠넘기기) 정황 | **회피** 또는 재분류 | 저부채 확인 시 #4 |
| 4 | 촉매(catalyst)·시점이 정의 안 됨 | **관찰**(촉매 대기) | 촉매 명확 + 위 통과 시 #5 |
| 5 | merger arb인데 deal break 시 손실폭 > 기대이익 | **회피/축소** | 기대값(+) 이면 진입 후보 |
| 6 | 위 전부 통과 + Magic Formula 상위 | **진입 후보** | — (단 사이징은 아래) |

> 어느 단계든 입력이 비면 위 "판단 불가" 블록으로 질의. 한 규칙이 막혀도 멈추지 말고 대체 경로/관찰 등급으로 진행.

## Position Sizing

집중(5~8종목)이되 **각 포지션의 downside가 명확히 제한**되어야 함(catalyst·헤지 가능). 무제한 손실 가능 포지션은 집중 금지.

## 필요 데이터·의존성

정성 판단만으로도 진행 가능하지만, 아래 데이터가 있어야 진입/관찰/회피 판정의 근거가 선다 — 없으면 반드시 "추정" 라벨을 결론에 병기.

- **EBIT·Enterprise Value(EV)**: Magic Formula 두 지표의 원천. 손익계산서(EBIT)·시가총액+순부채(EV)로 직접 산출, 없으면 대용 지표(영업이익 등)로 폴백.
- **공시(DART 등)**: 분할계획서·합병계약서의 부채 배분 비율·deal terms — leveraged spinoff 판별(체크포인트 3번), merger arb 스프레드 계산의 핵심 입력. 공시 전이면 판정을 "관찰"에 묶어둔다.
- **순부채·이자보상배율**: leveraged spinoff 여부 판별용(스크리너 구현 가드레일 참조).
- 데이터 결측 시 대용 지표 폴백·표기 규칙은 `~/.claude\stock-experts\README.md` 공통 규칙과 `references/greenblatt-special-situations.md` §11(실패 모드)을 따른다.

## 분석 워크플로우

정책·공시·뉴스에서 새 특수상황 후보를 발굴하는 단계라면 먼저 `_shared/event-discovery-contract.md`를 적용해 관측 가능 시각, 개체 연결, 인과 사슬을 검증한다. 사후 급등 설명이나 법인 연결이 불명확한 테마는 본 분석으로 넘기지 않는다.

1. 이벤트 식별·유형 분류(spinoff/arb/restructuring…).
2. 매도 압박/강제 매도의 구조적 원인 확인(왜 비효율인가).
3. 촉매(catalyst)와 그 시점, downside 한계 정의.
4. (해당 시) Magic Formula 정량 스크린 병행.
5. 결론 — 기대 이벤트 경로 + 진입가 + downside + 촉매 타임라인.

## 출력 템플릿

```
## [종목/이벤트] 특수상황 분석
### 유형: [spinoff 등] / 한 줄 결론: [진입/관찰/회피]
### Mispricing 원인(강제·비효율 구조)
### 촉매 & 타임라인 / downside 한계
### (선택) Magic Formula: EarningsYield / ROC / 종합순위
### 핵심 리스크 / 확인 필요
```

### 작성 예시

```
## (가상) E지주 인적분할 특수상황 분석
### 유형: spinoff(인적분할) / 한 줄 결론: 진입 후보
### Mispricing 원인: 분할 신주가 지수 제외·소형 → 기관 가격무관 매도 예상
### 촉매 & 타임라인: 재상장 후 1~3개월 매도 압박 소진 → 재평가
### downside 한계: 분할 사업 순현금 비중 높아 하방 제한
### (선택) Magic Formula: EV/EBIT 5.2(EarningsYield 19%) / ROC 28% → 종합 상위
### 확인 필요: ㉠분할 시 부채 배분 비율(분할계획서 공시) → leveraged spinoff 여부
```

❌ "분할하면 무조건 오른다"
✅ "인적분할 + 기관 강제매도 + 저부채 = 전형적 저평가. 단 부채 떠넘기기면 가정 붕괴 → 분할계획서 확인 필수"

> 결과 저장·데이터 결측(대용 지표 폴백 포함)·빠른 사용은 `~/.claude\stock-experts\README.md` 공통 규칙을 따른다.

### 결과 파일 저장 / 판단 불가 시 질의 절차

파일명 규칙(`special-sit_<종목>_<날짜>.md`, overwrite 금지·append 규칙)과 데이터 막힘 시 `[확인 필요]` 4요소 질의 절차(누가/언제·어떻게·해석·대체 경로)는 `references/greenblatt-special-situations.md` §11~13 참조.

## 거장의 실전 규율 (검증된 엣지)

- **실증**: Greenblatt의 Gotham Capital은 1985–1994 연 **50%**(순 30%, $1→$52). Magic Formula 원서는 연 30.8% vs S&P 12.4%(1988–2004)나 **출판 후(2006~) 알파 소멸**(value trap 선택↑·3~5년 drawdown). Spinoff +10%(Penn State), 합병차익 6~9.6%.
- **2016–2025 후속 검증**: 유로존 백테스트(마법공식+6개월 모멘텀)는 연 +11.3%(가격 기준) vs STOXX Europe 600 +5.3%이나 **2018·2019·2022–2024는 벤치마크 하회**(quant-investing.com, 2026 update) — 알파는 소멸이 아니라 변동성 확대·지속 하회 구간 증가. 반면 **스핀오프는 최근에도 견고**: Bloomberg Spin-Off Index가 2024 YTD +38%로 S&P500 대비 +26%p, 2020년 이후 누적 +38%p(Forbes, 2024). 정량 스크린(마법공식)보다 정성 이벤트(spinoff)가 여전히 우위 — Greenblatt 본인의 "진짜 무기는 특수상황" 명제와 부합(상세: `references/greenblatt-special-situations.md` §10).
- **진짜 엣지는 집중 특수상황**: Gotham 50%는 **소수(5~8개)·촉매·제한된 downside**의 spinoff·구조조정에서 나왔다. Magic Formula는 "쉽게 만든 대중용 버전" — 둘은 다른 게임.
- **"한 해 6~8개면 충분"**: 50개 아이디어가 아니라 명확한 소수에 집중.
- **강제 매도(구조적 비효율)를 노린다**: 가격 무관 매도(spinoff·지수 편출)가 알파의 원천.
- **downside부터**: 자산·현금·청산가치로 floor 확인 후 진입. 무제한 손실 포지션 집중 금지. merger arb은 급락기 동반 손실(보험매도형) → 분산.

> 상세: `references/evidence-and-master-playbook.md`. Gotham 수치는 소규모·1990년대 산물, Magic Formula는 공개 후 소멸 — 재현 보장 없음.

### 실전 케이스 — Marriott 분할 (1993)

Greenblatt 책(*You Can Be a Stock Market Genius*)의 대표 사례. Marriott이 호텔 '운영'(Marriott International)과 부채 가득한 호텔 '부동산'(Host Marriott)으로 분할 — 시장과 기관은 부채 덩어리 Host를 가격 무관 투매했지만, Greenblatt는 ① 경영진 핵심 인물이 Host로 이동(skin in the game) ② 투매가 펀더가 아닌 구조(지수·사이즈) 때문임을 보고 Host에 진입, 이후 큰 수익(확인 필요: 정확 수익률). 교훈: spinoff 체크포인트 1·4번(경영진 이동 + 강제 매도)이 실제로 작동한 원형 — 단, 한국 물적분할은 가치이전 방향이 반대일 수 있다(KRX 섹션).

## KRX 적용

- **인적분할 vs 물적분할**: 한국 특유 이슈. 물적분할 후 자회사 상장(쪼개기 상장)은 모회사 주주가치 훼손 논란 → spinoff 알파 가정이 미국과 다르게 작동, 모·자회사 가치이전 방향 반드시 점검.
- **2024–2026 제도 개정으로 성격 변화**: 2024.12 자본시장법 개정(물적분할 자회사 상장 시 공모주 20% 모회사 주주 배정, 이사회 주주보호 의무), 2026.7 상장규정 개정(중복상장 시 모회사 주주동의 의무화·최대주주 의결권 3% 제한·특별위원회 심사)으로 물적분할이 "주주가치 훼손 이벤트"에서 "주주동의를 거쳐야 하는 협상 이벤트"로 바뀌는 중 — 공시 시 주주보호방안 실질 여부를 촉매 점검에 추가(상세·출처: `references/greenblatt-special-situations.md` §14).
- **지주사 전환·자사주**: 지주회사 디스카운트, 자사주 활용 분할 합병의 가치 이전 구조 분석.
- **마법공식 국내 변형**: 강환국 등이 EV/EBIT + GP/A 등으로 변형. 한국은 금융·지주·시클리컬 비중 커 업종 제외·정상화 신중.
- M&A 차익은 한국 공개매수·소액주주 보호 제도(2024~ 강화 흐름)와 결합해 spread 재평가(확인 필요: 최신 제도).
- **메가캡 수급 쏠림 국면의 기회**: 삼성전자·SK하이닉스 등으로 자금·거래대금이 쏠리는 국면에서는 촉매(스핀오프·합병·구조조정)가 확실한 중소형 이벤트주도 수급 밖에서 장기 방치되기 쉬움 — downside floor와 촉매 타임라인이 명확하면 오히려 메가캡 쏠림이 진입가를 낮추는 기회로 작용할 수 있다(단, 유동성·거래대금 부족은 별도 리스크). 시장구조 상세는 `~/.claude\stock-experts\_shared\krx-market-structure-2026.md` 참조.

## 레퍼런스

- `scripts/magic_formula.py` — EY·ROC 랭킹 + 합병차익 연율화·기대값 계산기, 표준 라이브러리만 사용. `python scripts/magic_formula.py`로 데모 실행(랭킹·연율화·기대값 예시 출력, 실제 실행 결과는 `references/greenblatt-special-situations.md` §15 참조), 실전에서는 `from magic_formula import earnings_yield, roc, magic_rank, arb_annualized, arb_expected`로 임포트해 EBIT·EV·순운전자본·순고정자산 값을 넣는다.
- `references/greenblatt-special-situations.md` — Magic Formula 절차·백테스트, spinoff/arb/restructuring 상세, Acquirer's Multiple, 후대 영향, 2024–2026 최신 실증(§10)·실패모드·저장규칙(§11~13)·한국 물적분할 제도개정(§14).
- `references/merger-arb-event-types.md` — 합병차익 메커니즘(spread·연율화·deal break), 학술 근거, 이벤트 유형별 구조, KRX 제도.
- `references/distressed-sotp.md` — 부실·구조조정(자본구조·fulcrum), SOTP·stub·청산가치, recap, catalyst·downside 규율.
- `references/evidence-and-master-playbook.md` — 실증(Gotham 50%·Magic Formula 소멸·spinoff+10%·합병차익), Greenblatt 플레이북(집중·강제매도·downside), 시니어 체크.

## 실패 모드 / fallback

핵심 4가지(분석 거부·데이터 결측·이벤트 유형 모호·합병무산 시나리오)의 처리 규칙 전문은 `references/greenblatt-special-situations.md` §11 참조. 원칙: 어느 경우든 **투자 권유가 아니라 분석 보조**이며 최종 판단·책임은 사용자에게 있다.

## 스크리너 구현 가드레일

이 철학(마법공식+이벤트드리븐)을 자동 스크리너로 구현할 때 지켜야 할 최소 요건:

- **EY+ROC만으로는 스크리너가 못 된다**: 마법공식 두 지표는 "정량적으로 싸고 수익성 있다"만 말할 뿐 **왜 시장이 이 가격을 방치했는지**(강제 매도·촉매)를 말하지 않는다. 최소 추가 데이터: ①이벤트/촉매 태그(spinoff·M&A·구조조정 여부와 발표일) ②부채구조(leveraged spinoff 여부 판별용 순부채·이자보상배율) ③업종 제외 로직(금융·유틸리티 자동 배제, 원 절차 그대로).
- **정적 지표만 쓸 때 실패 모드**: 촉매 태그 없이 EY+ROC만 매일 재계산하면, 구조적으로 저평가된 채 방치된 지주사·시클리컬 저점주가 "이벤트 없이도" 상위권에 계속 등장한다 — 이는 특수상황이 아니라 그냥 저PER 스크린과 동일해져 deepvalue 스킬과 구분이 사라진다. **방지 필터**: 최근 N개월 내 공시된 이벤트가 없으면 마법공식 상위여도 "특수상황 후보"에서 제외하고 deepvalue로 라우팅, downside floor(청산·순현금) 산출 불가 종목은 자동 배제(SKILL.md 의사결정 규칙 #1), 시총 하한으로 유동성 함정 배제.
- **반복 감지 원칙**: 같은 종목이 촉매 없이 마법공식 상위에 **N일(예: 20영업일) 이상 연속** 등장하면, 이는 매수 신호가 아니라 "이벤트 태그 데이터가 없거나 부실하다"는 신호로 취급 — 스크리너 출력을 그대로 추천하지 말고 이벤트 데이터 보강을 먼저 요구한다.

## 한계

본 스킬은 **투자 분석·판단 보조 도구이지 투자자문이 아니다.** 모든 결론은 참고용이며, 실제 매매 판단과 그 결과에 대한 책임은 전적으로 사용자에게 있다. 과거 성과(Gotham 50% 등)는 미래 수익을 보장하지 않는다.

Magic Formula는 출판 후 알파 감소 보고 다수(in-sample 주의). 특수상황은 개별 분석 난도 높고 정보·실행 우위 필요. 합병 무산·구조조정 실패 시 큰 손실(이벤트 리스크).
