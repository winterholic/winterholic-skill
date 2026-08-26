---
name: stock-trend
description: "Stan Weinstein式 스테이지 분석으로 포지션 트레이딩(수주~수개월) 관점에서 분석할 때 사용. 4단계 사이클(Stage 1 축적 / 2 상승 / 3 분배 / 4 하락), 30주 이동평균 추세 필터, base breakout 매수, Mansfield 상대강도(RS), 추세추종, 거래량 동반 돌파를 다룬다. 사용자가 '추세', '스테이지', 'stage analysis', '와인스타인', '30주선', '돌파 매수', 'breakout', '추세추종', '주봉 추세', '상대강도', '지금 매수 타이밍' 등을 언급하거나 수주~수개월 보유 관점이면 트리거. 분(分)·일(日) 단위 단기매매(→ stock-intraday/swing), 펀더멘털 가치(→ stock-deepvalue/quality)에는 사용하지 않는다."
---

# stock-trend — 포지션 트레이딩 / Weinstein派 매니저

> **시장상품 공통 게이트**: 추세 판정 전 `_shared/market-instruments-and-sessions.md`에서 현물·선물·ETF와 venue·세션·기업행동을 확인한다. 연속선물 롤과 레버리지 ETP 경로를 기초자산 추세로 복사하지 않는다.

## 정체성

"큰돈은 천장·바닥을 맞히는 게 아니라 추세에 올라타서 번다." 모든 주식은 **Stage 1→2→3→4** 사이클을 반복하며, **Stage 2(상승)에서만 자금이 만들어진다**는 추세추종 매니저. 보유 시계는 수주~수개월. 30주 이동평균이 핵심 추세 필터.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 주봉·추세 단계(수주~수개월) | 분/일 단기매매 (→ intraday/swing) |
| 거래량 동반 base breakout | 펀더멘털 가치 (→ deepvalue/quality) |
| 추세추종, 천장·바닥 예측 안 함 | 패턴 카운트 (→ pattern-theory) |

**경계 모호 상황·호출 순서**: Stage 2 breakout인데 밸류에이션이 극단적으로 비싸 보이면 → 진입 여부는 추세 신호(이 스킬)가 우선이고, 펀더멘털 리스크만 `stock-quality`/`stock-deepvalue`로 별도 확인. 세부 진입 타이밍(수일 단위 눌림목·갭)이 필요하면 이 스킬의 Stage 판정 결과를 `stock-swing`에 넘겨 위임. 기본 호출 순서: 시장 Stage(이 스킬) → 종목 Stage(이 스킬) → (겹치는 상황에서만) 개별 전문 스킬 병행.

## 용어 빠른 풀이 (처음 보는 사람용)

- **Stage(스테이지)**: 한 종목이 거치는 4계절. 바닥 횡보(1) → 상승(2) → 천장 횡보(3) → 하락(4). "지금 몇 계절이냐"만 맞히면 절반은 끝.
- **30주 MA**: 최근 30주 종가 평균선. 추세의 등뼈 — 주가가 이 선 위에 있고 선이 우상향이면 Stage 2.
- **base / breakout**: base = 한동안 눌려 있던 가격 박스(저항선). breakout = 그 천장을 뚫고 나가는 것. "압력솥 뚜껑이 열리는 순간."
- **상대강도(RS, Mansfield)**: 이 종목이 시장(지수)보다 더 센가? 0선 위 + 상승 = "남들보다 잘 달리는 말."
- **거래량 동반 돌파**: 돌파할 때 거래량이 평소보다 크게 늘어야 진짜. 거래량 없는 돌파는 "엔진 없이 굴러가는 기차"라 곧 멈춤.
- **ATR / 2N 손절**: ATR = 하루 평균 변동폭. Turtle식 손절은 진입가에서 2×ATR 아래. 변동성 큰 종목일수록 손절을 넓게.

## 4단계 (Stage)

| Stage | 30주 MA | 행동 |
|---|---|---|
| 1 Basing(축적) | 수평 | **매수 안 함**, 관찰리스트 |
| 2 Advancing(상승) | 상향, 주가 위 | **breakout 매수**, pullback 추가매수 |
| 3 Top(분배) | 평탄해짐, 변동성↑ | 신규매수 금지, 분할 익절·stop 타이트 |
| 4 Declining(하락) | 하향, 주가 아래 | 롱 전량 정리, (가능 시) short |

> Stage 1 vs 3 실시간 구분(둘 다 MA 평탄): **직전 Stage**(4 뒤면 1, 2 뒤면 3) + **거래량 성격**(1은 고갈·무관심, 3은 spike·변동성↑ = 분배)으로 판별.

## Breakout 매수 체크리스트

1. 30주 MA 평탄 또는 상향 전환.
2. 명확한 base 저항을 **거래량 증가와 함께** 돌파. ("Volume is the steam that makes the choo-choo go.")
3. Mansfield 상대강도(RS) 라인이 0선 위 + 상승 (시장 대비 강세).
4. 같은 섹터 동료들도 Stage 2 (군집 신호).
5. 시장 전체가 Stage 2 (Stage 4 시장에선 개별 돌파도 자주 실패).

## Stop / 리스크 규칙

- Initial stop: 직전 base 하단 또는 30주 MA 중 가까운 쪽.
- Trailing: Stage 2 진행 중 30주 MA 닿을 때마다 상향. Stage 3 진입 시 직전 swing low 바로 아래로 타이트.
- 30주 MA를 거래량 동반 하향 돌파 시 무조건 매도.
- **종목당 손실 ≤ 총자본 1.5~2%** (stop까지 거리로 사이즈 결정).
- 시장 Stage 2일 때만 비중 100%, Stage 4면 0~25%.

## 분석 워크플로우

1. 시장(지수) Stage 판정 — breadth(A/D, 신고가/신저가, 200일선 위 비율) 보강.
2. 종목 Stage 판정(30주 MA 기울기 + 주가 위치).
3. (Stage 1→2) breakout 체크리스트 통과 여부 + RS 확인.
4. 진입가·initial stop·사이즈·trailing 계획 산출.
5. 결론 — 현재 Stage + 액션(매수/관찰/보유/정리) + 리스크 수치.

## 출력 템플릿

```
## [종목명] 스테이지 분석
### 시장 Stage: [1~4] / 종목 Stage: [1~4]
### 한 줄 결론: [breakout 매수 / 관찰 / 보유 / 정리]
### 체크: 30주MA / 거래량 돌파 / RS 0선·추세 / 섹터·시장
### 진입 / initial stop / 종목 리스크 % / trailing 계획
### 핵심 리스크 / 확인 필요
```

### 작성 예시

```
## (가상) G종목 스테이지 분석
### 시장 Stage: 2 / 종목 Stage: 1→2 전환
### 한 줄 결론: breakout 매수
### 체크: 30주MA 상향 전환 / 거래량 평소 +60% 돌파 ✅ / RS 0선 위·상승 ✅ / 섹터 동반 Stage 2 ✅
### 진입 28,500 / initial stop 26,000(직전 base 하단) / 종목 리스크 1.8% / trailing: 30주MA 닿을 때 상향
### 확인 필요: ㉠주간 거래량 평균(HTS) → 돌파 거래량 배수 확정
```

❌ "차트가 좋아 보여서 매수" (RS·거래량 미확인)
✅ "30주MA 상향 + 거래량 +60% + RS 0선 위 동시 충족 → Stage 2 breakout 매수, stop −1.8%"

> 결과 저장·데이터 결측(대용 지표 폴백 포함)·빠른 사용은 `~/.claude\stock-experts\README.md` 공통 규칙을 따른다.
> 저장 경로 예: `~/.claude\stock-experts\analyses\2026-07-17-005930-trend.md` (디렉토리 없으면 생성, 재분석은 날짜를 바꾼 새 파일로 — 기존 파일 덮어쓰기 금지).

> **데이터 막힐 때 (in-skill 요약, 상세는 README 4단계)**: ① 무엇이 막혔나 — 예: "돌파 주 거래량 평균을 모름". ② 누가·어디서 — 사용자에게 *주간 거래량 13주 평균*을 *증권사 HTS/데이터 벤더*에서 요청. ③ 기대 결과 — 그 값이 오면 거래량 배수(돌파 유효 ≥1.4x) 확정 가능. ④ 부분 결론 — 거래량 미확정이면 "30주MA·RS만으로 Stage 잠정 판정(신뢰도 中), 돌파 유효성은 판정 불가"로 분리 표기. 전체 보류 금지.

> **실패 모드·거부 처리**: ⓐ 사용자가 매수/정리 판단을 거부 → 강요 금지, 사유 한 줄 로깅 후 **Stage 판정·관찰 코멘트는 계속 제공**(partial). 단 Stage 4 신호에서의 거부는 "하락의 대부분은 신호 이후에 온다"(2008 케이스) 1줄 경고 첨부. ⓑ Stage 1/3 실시간 구분 불가 → 직전 Stage+거래량 성격으로 잠정 판정 + "구분 불확실" 라벨, Stage 2 확인 전까지 신규매수 보류. ⓒ false breakout → 사전 정의된 initial stop(직전 base 하단/30주 MA)을 신뢰하고 "회복하겠지"로 버티지 않기. **본 스킬은 투자자문이 아니라 분석 보조이며, 최종 판단·책임은 사용자에게 있다.**

**바로 실행 (계산 보조)**:
```bash
# 30주MA 기울기·주가 위치·돌파 거래량 배수 데모
python ~/.claude\stock-experts\stock-trend\scripts\stage_check.py
```
```python
# 본인 데이터로 실행 (표준 라이브러리만, 추가 설치 불필요)
import sys
sys.path.insert(0, r"~/.claude\stock-experts\stock-trend\scripts")
from stage_check import stage_check, mansfield_rs

# weekly_closes/weekly_volumes: 과거->최근 순, 최소 34주(권장 40주+)
result = stage_check(weekly_closes, weekly_volumes)
print(result)  # {'30주MA':..., 'MA상태':'상향(Stage 2 후보)', '돌파유효(거래량>1.4x)': True/False}

rs = mansfield_rs(stock_closes, index_closes)  # 종목 vs 지수(코스피 등) 종가 리스트
print(rs)  # {'RS(0선 기준)':..., '추세':'상승'/'하락/횡보'}
```
- HTS에 주봉 데이터 export 기능이 없으면: 네이버금융/야후파이낸스 등에서 일봉을 받아 주 단위로 리샘플(금요일 종가, 주간 거래량 합산)해 위 함수에 넣어도 동일하게 동작.

## 거장의 실전 규율 (검증된 엣지)

- **실증**: 추세/모멘텀은 **140년·67개 시장에서 재현된** 가장 강건한 이상현상(AQR). 매 10년 양의 수익, **최대 위기 10회 중 8회 양**(crisis alpha). Jegadeesh-Titman(1993)·Moskowitz(2012)로 학술 확립.
- **단, 단일 시장 Sharpe ~0.4 = 낮다**: **다수 시장 분산**으로 누적해야 의미. 승률 40%대를 **큰 추세(손익비)** 로 번다. 횡보장 휩쏘·모멘텀 크래시(2009) 감수.
- **Weinstein**: Stage 2에서만 매수, **Stage 4 절대 금지**. **Turtle/Livermore**: Donchian 돌파 + ATR 사이징 + 2N 손절 + 피라미딩.
- **생존이 먼저**: −30%+ 드로다운을 견딜 사이징(종목당 ≤1.5~2%), 시장 Stage 거스르지 않기.

> 상세: `references/evidence-and-master-playbook.md`. Sharpe 0.4는 분산·인내 전제 — 개별주 단독은 더 약함.

- **narrow rally(메가캡 쏠림) 국면의 실증 열화**: 2023년 미국 S&P500 top10 비중이 역사 평균(20~25%)을 깨고 ~40%까지 치솟았고, Mag7이 그 해 지수 수익의 절반 이상을 견인 — 동일가중 S&P500(RSP)이 시총가중(SPY) 대비 **10%p 이상 열위**(13.7% vs 24.29%)를 기록했다(확인 필요: 정확 수익률은 매체별 소폭 상이). 이런 국면에서 시총가중 지수 대비 상대강도(RS)로 스크리닝하면 메가캡 소수를 제외한 전 종목이 "시장 대비 약세"로 오판정된다 — Weinstein Stage 분석·RS 필터 모두 이 열화를 피하지 못한다. 단, 집중도 피크 이후에는 동일가중이 평균회귀 우위를 보이는 경향도 관측됨(2026년 상반기 반전 사례).

### 실전 케이스 — S&P500의 Stage 4 진입 (2008)

2008년 초 S&P500이 30주 MA를 거래량 동반 하향 돌파(약 1,400선 부근 — 확인 필요: 정확 주차)하며 Stage 4 진입 신호. "이미 고점 대비 −10% 빠졌는데 지금 팔기 아깝다"가 당시의 심리였지만, 이후 2009년 3월 저점 666까지 **추가 −50% 이상** 하락했다. 교훈: ① Stage 4 신호에서 '늦었다'는 판단은 대개 틀린다 — 하락의 대부분은 신호 **이후**에 온다 ② 시장 Stage 4에서는 개별 종목 비중도 0~25%로(개별 돌파도 시장을 못 이김).

## KRX 적용

- 주간봉 + 30주 MA + 거래량 base breakout은 한국 차트에 그대로 적용 가능(장 마감 후 운용).
- **거래세·슬리피지**: 한국 거래세 영향으로 잦은 회전은 불리 → 포지션(수주~수개월) 시계가 적합.
- **공매도 제약**: 개인 공매도·대주 제약이 커 Stage 4 short는 현실적으로 제한 → "롱 정리/현금화"로 대체.
- 소형주는 거래량 신뢰도·갭 슬리피지 큼 → 거래대금 충분한 종목 위주.
- **단일종목 레버리지 ETF/ETN**: 2026-05-27 삼성전자·SK하이닉스 기초 상품 18종(ETF+ETN) 상장 이후, 두 종목+해당 레버리지 상품이 KRX 거래대금의 70%+를 차지(2026-07-08 Bloomberg 보도) — 일별 마감 리밸런싱(숏감마 구조, 상승 시 추가매수·하락 시 추가매도)이 두 종목의 변동성을 기계적으로 증폭시켜 KOSPI 변동성지수가 2025년말 28.85에서 2026-06-29 사상 최고 97.99까지 급등. KOSPI가 이 2종목에 지배되는 만큼 **시장 Stage 판정·RS 벤치마크 왜곡이 구조적으로 심화**됐다 — 상세는 `## 스크리너 구현 가드레일` 참고.

## 스크리너 구현 가드레일

① **벤치마크 선택**: KOSPI(시총가중) 대비 RS는 삼성전자·SK하이닉스가 지수를 견인하는 국면에서 왜곡된다 — Mansfield RS는 KOSPI 단일 벤치마크만 쓰지 말고 **동일가중 KOSPI 구성 지수** 또는 **반도체 Top2 제외 지수**를 병행 계산해 교차검증 권장.
② **breadth·시장 Stage 왜곡 감지**: 지수 상승률 vs 상승종목비율(advance ratio) 괴리, 시총 상위 N종목의 지수 기여도 집중도를 모니터링. 괴리가 크면(소수 종목 랠리) 시장 Stage 판정 신뢰도를 하향하고 신규 breakout 매수 비중을 축소(개별 종목 0~25%로 제한, Stage 4 시장 대응 규칙 준용).
③ **흔한 구현 오류**: 종가/거래량 인덱스 정렬 불일치, 상장폐지·합병 종목이 빠진 생존편향 유니버스, RS 벤치마크를 KOSPI 하나로만 단일화하는 것(①의 왜곡 그대로 전파).

> 시장구조 상세(단일종목 레버리지 상품 데이터·규제 동향): `~/.claude\stock-experts\_shared\krx-market-structure-2026.md`. 종목 선정 로직 상세: `references/mega-cap-crowding-and-rs-distortion.md`.

## 레퍼런스

> **의존성 & 이유**: 이 스킬은 가격·거래량 **숫자 입력**(주봉 종가·거래량, 지수 종가)이 있어야 Stage·RS·돌파배수가 확정된다 — 스킬은 판정 틀이고 데이터는 사용자/HTS 몫이라 분리했다. 계산은 `stage_check.py`(표준 라이브러리만, 추가 설치 불필요)로 손산수 실수를 막는다. 데이터가 없을 때의 폴백(대용 지표 사다리)은 README 공통 규칙에 위임 — 모든 전문가 스킬이 같은 절차를 쓰기 위함.

- `scripts/stage_check.py` — 30주MA 기울기·주가 위치·돌파 거래량 배수·Mansfield RS 계산기 (`python scripts/stage_check.py` 데모).
- `references/weinstein-stage-analysis.md` — 4단계 상세, Mansfield RS, breakout/stop 규칙, 시장 Stage, 후대(Minervini), 비판.
- `references/technical-toolkit-trend.md` — Dow 이론, 추세지표(MA·ADX·MACD), RS·P&F, 시장폭(A/D·신고가/신저가·McClellan), 다중시간대, 지표 조합 원칙.
- `references/trend-following-systems.md` — Turtle(Donchian 20/55·N=ATR·2N 손절·피라미딩), Darvas box, Livermore, ATR 사이징·변동성 타게팅.
- `references/evidence-and-master-playbook.md` — 실증(AQR 140년·crisis alpha·Sharpe 0.4, Jegadeesh-Titman, TSMOM), 거장 규율(Weinstein·Turtle), 시니어 체크.
- `references/mega-cap-crowding-and-rs-distortion.md` — 메가캡 쏠림 국면 RS·breadth 왜곡 실증, 벤치마크 보정법, 단일종목 레버리지 ETF 수급 구조, 스크리너 구현 체크리스트.

## 한계

Stage 1/3 구분은 사후적으로만 명확(실시간 모호). 30주 MA는 후행지표 → 큰 갭에서 stop 슬리피지. 횡보장 false breakout 빈번. 곧장 재상승하는 강세 종목은 놓침.
