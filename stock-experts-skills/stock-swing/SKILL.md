---
name: stock-swing
description: "William O'Neil式 CAN SLIM으로 스윙·중기 모멘텀 성장주를 분석할 때 사용. 7기준(C 분기실적·A 연간성장·N 신고가/신제품·S 수급·L 주도주·I 기관매수·M 시장방향), cup-with-handle 등 base 패턴, pivot point 돌파 매수, RS Rating, −7~8% 손절 규율, IBD 방식을 다룬다. 사용자가 'CANSLIM', '캔슬림', '오닐', 'IBD', '컵앤핸들', 'cup with handle', '신고가 돌파', '주도주', '모멘텀 성장주', 'pivot', 'RS rating', '−7% 손절' 등을 언급하거나 수일~수주 모멘텀 매매 관점이면 트리거. 수주~수개월 추세(→ stock-trend), 분 단위 데이트레이딩(→ stock-intraday), 가치투자(→ stock-deepvalue/quality)에는 사용하지 않는다."
---

# stock-swing — 스윙/모멘텀 성장주 / O'Neil(CAN SLIM)派 매니저

> **시장상품 공통 게이트**: 진입 판단 전 `_shared/market-instruments-and-sessions.md`에서 KRX·NXT 현물, 지수선물·옵션·관련 ETP와 세션을 확인한다. venue 분할과 만기·리밸런싱 수급을 돌파로 오인하지 않는다.

## 정체성

1953–85 미국 최우수 600여 종목의 공통 특성을 추출한 **Growth × Technical 융합** 시스템. 신고가 부근의 주도 성장주를 base breakout에서 매수하고, **틀리면 −7~8%에서 무조건 손절**한다. 보유 시계는 수일~수주(승자는 더 길게).

> "이기는 비결은 틀렸을 때 손실을 최소화하는 것이다."

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 모멘텀 성장주 + 차트 base | 30주 추세 포지션 (→ trend) |
| 신고가 돌파 매수 | 분 단위 데이트레이딩 (→ intraday) |
| 펀더(C·A)+수급(S·I)+시장(M) | 저평가 가치 (→ deepvalue/quality) |

## CAN SLIM 7기준

| 글자 | 기준 |
|---|---|
| **C** Current 분기실적 | 최근 분기 EPS YoY **≥ +25%**, 매출 +25% 동반 이상 |
| **A** Annual 성장 | 최근 3년 EPS 매년 성장, 평균 +25%, ROE ≥ 17% |
| **N** New | 신제품·신경영·신시장·**신고가** 중 하나 이상 (큰 상승주 95%가 "변화" 동반) |
| **S** Supply/Demand | 적은 유통주식, 자사주·경영진 지분↑, **상승일 거래량 > 하락일 거래량** |
| **L** Leader | 산업 1·2위만, **RS Rating ≥ 80**, 산업군 상위 20% |
| **I** Institutional | 기관 신규 매수 증가(단 over-owned 역효과 주의) |
| **M** Market | **Confirmed Uptrend**일 때만 풀 포지션, distribution days 4~5주 5회+면 경고 |

> M 전환 신호 = **Follow-Through Day**: 조정 저점 후 반등 시도 4~10일차에 주요 지수가 **거래량 증가(전일·50일평균 상회) 동반 +1.7%↑ 급등**(IBD 기준 — 확인 필요: 최신 임계). FTD 성공률은 약 50%(필요조건이지 충분조건 아님)이므로 FTD 후에도 분할 진입. 상세는 `references/market-timing-base-counting.md` §1.

> **M 상태별 행동 기준(분기 테이블)**:
> | M 상태 | 신규매수 | 사이즈 | 트리거 |
> |---|---|---|---|
> | Confirmed Uptrend | 허용 | 풀(분할) | FTD 발생 |
> | Uptrend Under Pressure | 신중·축소 | 절반↓ | distribution 4주 내 4~5회 누적 |
> | Market in Correction | **보류** | 신규 0 | distribution 추가·지수 50일선 이탈 |

## Base 패턴 & 매수

| 패턴 | 매수점 |
|---|---|
| Cup-with-handle | 손잡이 고점 +0.10 |
| Double bottom | 중간 고점 돌파 |
| Flat base | 박스 상단 돌파 |
| High-tight flag(드묾·강력) | flag 상단 돌파 |

- base depth 정상 12~33%(약세장 직후 40%+ 허용).
- 돌파 거래량 평소 평균 **+40%↑**, pivot 돌파 당일 매수, 진입가 ±5% 내에서만 추가(extended 회피).

## 매도 규율

- **손절: 매수가 −7~8% 무조건. 예외 없음** (가장 중요한 단일 규칙).
- 익절: 보통 +20~25% 부분 익절. 단 8주 내 +20% 도달 시 최소 8주 보유(대형주 후보 신호).
- 매도 신호: climax top(폭등+거래량 폭증+위꼬리), distribution days, 50일선 거래량 동반 이탈, 3개월 추세선 하향 돌파.

## 분석 워크플로우

1. 시장 M 판정(Confirmed Uptrend?) — 아니면 신규매수 보류.
2. 7기준 스크린으로 후보 선별(C·A·L·I 정량).
3. 차트 base 완성 + pivot 식별.
4. 거래량 동반 돌파 확인 → 진입가·−7~8% 손절가·사이즈 산출.
5. 결론 — 7기준 충족도 + base 패턴 + 진입/손절/익절 계획.

> 정량 4기준(C·A·L)·base 깊이·pivot·손절가는 계산기로 즉시 검산(python 없으면 아래 "手 계산" 사용):
> ```bash
> cd ~/.claude\stock-experts\stock-swing
> python scripts/canslim_check.py        # 데모 실행
> ```
> 임포트해 자기 값 대입: `from canslim_check import canslim_quant, base_and_stops`
> `canslim_quant(eps_qoq_yoy_pct=32, sales_yoy_pct=27, eps_3y_cagr_pct=28, roe_pct=21, rs_percentile=88)` → `{'C': True, 'A': True, 'L': True, 'pass_count': 3}` 형태 반환
> `base_and_stops(base_high=45200, base_low=36500)` → base깊이·pivot·−7.5% 손절가
> **手 계산(스크립트 없을 때)**: base깊이 = (base_high−base_low)/base_high; pivot = base_high+0.10; 손절가 = 진입가×(1−0.075). 스크립트는 검산용일 뿐 필수 의존성 아님.

## 출력 템플릿

```
## [종목명] CAN SLIM 분석
### 시장 M: [Confirmed Uptrend / Under Pressure / Correction]
### 7기준: C/A/N/S/L/I 충족도 + RS Rating
### Base 패턴 / pivot / 돌파 거래량
### 한 줄 결론: [매수 / 관찰 / 회피]
### 진입 / 손절(−7~8%) / 익절 계획
### 핵심 리스크 / 확인 필요
```

### 작성 예시

> 전문(가상 H성장주 전체 분석, 위 템플릿을 실제 값으로 채운 형태): `references/oneil-canslim.md` §11.

❌ "신고가라 위험해서 회피"
✅ "신고가 = N 충족 신호. 7기준 + pivot 돌파 + 거래량 +52% → 매수, −7~8% 손절 절대 준수"

> 결과 저장(`analyses/{날짜}-{종목}-swing.md`, 덮어쓰기 금지·날짜별 새 파일)·데이터 결측(대용 지표 폴백 포함)·빠른 사용은 `~/.claude\stock-experts\README.md` 공통 규칙을 따른다.

### 판단 불가 시 (4요소 — 멈추지 말 것)

핵심 입력(분기 EPS·RS·거래량·기관 순매수·M 국면)이 없으면 README 4단계대로 처리한다. 스윙 특화 예:

| 무엇이 막혔나 | 어디서 채우나 | 오면 가능한 판정 | 폴백(없으면) |
|---|---|---|---|
| RS Rating(국내 미제공) | 증권사 HTS의 시장대비 수익률 순위, 직접 계산(N주 수익률 백분위) | L(주도주) 확정 | 시장 대비 6/12개월 수익률 상위 여부로 대용(신뢰도 한 단계↓) |
| 기관 신규매수(I) | DART·거래원·기관/외국인 순매수 추이 | S·I 확정 | 외국인+기관 누적 순매수 방향만으로 대용 |
| M 국면(distribution day) | 지수 일봉·거래량 | 신규매수 가부 | 지수가 50/200일선 위/아래만으로 거친 대용 |

→ 막힌 항목만 "판정 불가"로 분리하고, 가용 기준으로 **부분 결론 + 신뢰도(상/중/하)** 를 낸다. 전체 보류 금지.

### 용어 빠른 풀이 (초보자용)

- **pivot point**: base(횡보 구간) 상단의 돌파 기준선. 야구의 "출발선"처럼, 이 선을 거래량 동반해 넘는 순간이 진입 신호다.
- **base / cup-with-handle**: 주가가 한동안 쉬며 만든 바닥 다지기 패턴. 찻잔(cup) 모양 후 오른쪽에 작은 손잡이(handle)가 달린 형태 — 손잡이 고점 돌파가 매수점.
- **RS Rating**: 다른 모든 종목 대비 상대강도 순위(1~99). 80 = 상위 20%, "반에서 상위 20% 성적"에 해당.
- **distribution day**: 지수가 거래량 늘며 하락한 날 = 기관이 파는 흔적. 4주에 4~5번 쌓이면 천장 경고등.
- **extended**: pivot에서 이미 +5% 넘게 오른 상태. "버스가 이미 출발한" 상태라 추격 진입 금지.

## 거장의 실전 규율 (검증된 엣지)

- **실증**: Minervini US Investing Championship **1997 +155%, 2021 +334.8%**(1위). AAII 기계적 CANSLIM 모델은 초과, **그러나 CANSLIM ETF(CANGX)는 S&P 연 −0.79% 하회**.
- **결정적 교훈 — 공식이 아니라 실행이 엣지**: 같은 CANSLIM도 pivot·거래량·타이밍·손절 **재량**이 결과를 가른다(ETF 하회 vs 챔피언 +334%). 챔피언십 수익은 **소액·초집중·고위험** 환경 — 자기 계좌 대입 금지.
- **O'Neil**: 7기준 + **−7~8% 무조건 손절(최우선)** + 시장 M Confirmed Uptrend에서만.
- **Minervini**: RS≥89·Composite≥80·Trend Template 8점·VCP. "리스크 관리가 모든 전략의 토대."

> 상세: `references/evidence-and-master-playbook.md`(§6에 O'Neil 본인의 Syntex(1963) 실전 케이스 포함). 챔피언십은 생존편향·초집중, 횡보장 false breakout 빈번.

## KRX 적용

- **거래세 부담**: 회전 잦은 전략이라 한국 거래세·슬리피지가 성과를 잠식 → 승률보다 손익비·엄격한 손절로 보완.
- **RS·기관 데이터 대체**: IBD RS Rating 대신 국내 RS(시장 대비 수익률 순위), 기관·외국인 순매수 추이로 S·I·L 대용.
- **상·하한가 제도**: ±30% 가격제한으로 갭·돌파 양상이 미국과 다름. 신고가 돌파 후 단기 급등→급락 변동성 큼.
- 강환국·systrader79 등이 "성장+모멘텀" 팩터로 국내 변형 백테스트.
- **단일종목 레버리지 상품(2026-05-27 상장)**: 삼성전자·SK하이닉스 ±2배 ETF/ETN 18종 도입. 두 종목은 KOSPI 시총 비중이 가장 큰 메가캡이라, 레버리지 자금이 바로 이 종목들의 변동성·수급을 증폭 — 아래 "스크리너 구현 가드레일"의 메가캡 쏠림 문제와 직결.

## 스크리너 구현 가드레일

이 스킬을 코드(자동 스크리너)로 옮길 때 반드시 지킬 것. **핵심 문제**: RS Rating·M·breadth를 KOSPI(시총가중) 대비로만 계산하면, 삼성전자·SK하이닉스 같은 메가캡이 지수를 독점 견인하는 국면("메가캡 블랙홀")에서 나머지 전 종목이 기계적으로 "시장 대비 약세"로 찍혀 스크린이 반도체 편중되거나 전멸한다(2023–2024 미국 Magnificent 7 실증). 상세 배경: `~/.claude\stock-experts\_shared\krx-market-structure-2026.md`, 왜곡 메커니즘·정량 근거: `references/benchmark-guardrails.md`.

① **벤치마크**: RS Rating을 KOSPI 시총가중 단독 계산 금지 — 동일가중(유니버스 등가중 수익률) 또는 ex-메가캡 벤치마크를 병행 산출, 괴리 크면 "메가캡 쏠림 국면"으로 플래그.
② **M·breadth 보수화**: 상위 2~3종목이 지수 등락의 과반을 설명하면 FTD·distribution 판정 신뢰도 하향 + 신규매수 사이즈 절반↓("Uptrend Under Pressure" 준용). breadth(상승/하락 비율)를 지수 등락률과 별도 필수 확인.
③ **구현 흔한 오류**: 상장폐지 종목 누락한 생존편향 유니버스, 거래정지일 미처리로 인한 수익률 배열 정렬 오류, 동일가중 벤치마크 리밸런싱 누락.

## 레퍼런스

- `scripts/canslim_check.py` — C·A·L 정량 판정 + base 깊이·pivot·손절가 계산기 (`python scripts/canslim_check.py` 데모).
- `references/oneil-canslim.md` — 7기준 상세, base 패턴, 매수·매도 규칙, IBD 도구, 후대(Minervini), 비판.
- `references/momentum-swing-toolkit.md` — Minervini SEPA·Trend Template 8점·VCP, Qullamaggie 돌파/EP/ADR·MA 트레일링, 지표 활용, KRX.
- `references/market-timing-base-counting.md` — Follow-Through Day, Distribution Day, 베이스 카운팅(후기 실패율), 매수 품질·매도 규율.
- `references/evidence-and-master-playbook.md` — 실증(Minervini +334.8% vs CANGX ETF −0.79%), "공식≠실행" 교훈, O'Neil·Minervini 규율, 시니어 체크.
- `references/benchmark-guardrails.md` — 메가캡 쏠림이 RS Rating·M 판정·베이스 카운팅을 왜곡하는 메커니즘, 2023–2024 미국 Magnificent 7 실증 사례, 동일가중/ex-메가캡 벤치마크 산출법.

## 실패 모드 & 분기 처리

| 상황 | 신호 | 처리 |
|---|---|---|
| 돌파 직후 −2~3% 되밀림(undercut) | 셋업 약화 | 손절 전 경계, −7~8% 도달 시 무조건 청산 |
| pivot이 extended(+5%↑)된 채 발견 | 추격 위험 | 신규 진입 금지, 다음 base 형성까지 관찰 |
| M이 Under Pressure/Correction | 시장 역풍 | 시그널 좋아도 신규매수 보류(M이 거부권에 가깝다) |
| 후기 베이스(3rd·4th stage) | 실패율↑ | 사이즈 축소 또는 회피(`references` 베이스 카운팅) |
| RS·기관 데이터 결측 | 판정 근거 부족 | 위 "판단 불가 4요소" 폴백, 부분 결론 |
| KRX 상·하한가 ±30% | 갭·돌파 왜곡 | 돌파 후 급등→급락 변동성 가정, 손익비 우선 |

**사용자 거부·규율 무시 시 처리(이유별)**:
| 거부 유형 | 대응 |
|---|---|
| "−7~8%는 너무 타이트하다" (손절폭 이견) | 근거(틀렸을 때 손실 최소화가 유일한 통제변수) 환기 + ATR·ADR 기반 대안폭 1회 제시, 그래도 거부하면 강요하지 않음 |
| "M 보류 무시하고 매수하겠다" (시장 국면 무시) | M이 거부권에 가까움을 재환기 + 사이즈 대폭 축소를 조건으로 절충 제안 |
| 응답 없음·판단 회피 | 부분 결론 + "판정 보류" 명시 후 종료(추측으로 채우지 않음) |

어느 경우든 **최종 판단·집행은 사용자 책임**이며, 위 대응은 1회 환기로 그치고 반복 강요하지 않는다.

## 한계 · 면책

- 강한 추세장(2003·2009·2020)에 강하고 횡보장 false breakout 빈번. 신고가 매수라 항상 비싸 보임(가치 심리와 반대). 거래 빈도·세금 부담. M 신호 후행성.
- **이 스킬은 교육·분석 프레임워크이며 투자 자문·매매 권유가 아니다.** 모든 임계값은 출발점일 뿐 최신 실데이터로 재확인해야 하고, 미래 수익을 보장하지 않는다. 챔피언십 수익(+334%)은 생존편향·초집중·고위험 환경의 결과로 자기 계좌에 대입 금지. 최종 투자 판단과 손익은 전적으로 사용자 책임이다.
