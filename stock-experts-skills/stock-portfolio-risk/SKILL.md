---
name: stock-portfolio-risk
description: "Markowitz·Kelly·VaR式 포트폴리오 구성과 리스크 관리 관점으로 분석할 때 사용. 현대포트폴리오이론(MPT)·효율적 투자선, 상관·분산, Kelly criterion 포지션 사이징(f*=edge/odds, fractional/half-Kelly), Value at Risk·CVaR, 변동성 타게팅, 최대낙폭(MDD)·리스크 버짓팅, Black-Litterman을 다룬다. 사용자가 '포지션 사이징', 'position sizing', '켈리', 'Kelly', '비중 얼마', 'VaR', '효율적 투자선', '포트폴리오 최적화', 'MPT', '리스크 관리', '상관관계 분산', '최대낙폭' 등을 언급하거나 '얼마나 살까/어떻게 섞을까'를 물으면 트리거. 무엇을 살지(→ 가치·기술·퀀트 시그널 스킬), 꼬리위험 헤지(→ stock-tail-risk), 주문 체결(→ stock-execution)에는 사용하지 않는다."
---

# stock-portfolio-risk — 포트폴리오 / 리스크 매니저

> **시장상품 공통 게이트**: 배분·헤지 전 `_shared/market-instruments-and-sessions.md`에서 현물·채권·선물·옵션·ETP의 계약, 세션, 증거금과 유동성을 확인한다. 명목 익스포저와 실제 청산위험을 분리한다.

## 정체성

"무엇을 살까"가 아니라 **"얼마나·어떻게 섞을까"** 를 전담한다. 시그널 전문가들의 아이디어를 받아 위험조정 후 실제 비중으로 변환하는, 자동매매 체인의 **사이징 레이어**.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 비중·분산·리스크 한도 | 무엇을 살지 (→ 시그널 스킬) |
| MPT·Kelly·VaR | 꼬리위험 헤지 (→ tail-risk) |
| 포트 최적화 | 주문 체결 (→ execution) |

## 1) MPT (Markowitz)

자산을 기대수익(μ)·분산(σ²)·**상관(ρ)** 으로 평가. 상관 낮은 자산 결합 시 같은 수익에서 위험↓. **효율적 투자선** = 주어진 위험에서 수익 최대(또는 위험 최소) 집합. 무위험자산 추가 → Capital Market Line, 접점=Tangency(시장) 포트.

## 2) Kelly Criterion (사이징)

장기 복리(log wealth) 최대화 베팅 비율 f*:
```
베팅형:  f* = edge/odds = (bp − q)/b      # b=odds, p=승률, q=1−p
투자형:  f* ≈ (μ − r)/σ²                  # 초과수익/분산 (Merton 비율과 동형)
```
- **Fractional / Half-Kelly**: 풀켈리는 변동성 과해 실무에선 1/2 켈리 — "수익 ~3/4를 변동성 절반으로". 추정오차에 대한 안전마진.

## 3) VaR & 그 너머

- **VaR**: 신뢰수준·기간 내 예상 최대손실(분산-공분산/역사적/몬테카를로). 모수적(정규): VaR = −(μ + z_α·σ)×V — 꼬리 과소평가하므로 '최소 위험'으로만 읽는다.
- **CVaR(Expected Shortfall)**: VaR 초과 손실의 기대값 — 꼬리 측정, VaR 약점 보완. 정규 근사: CVaR = −(μ − σ·φ(z_α)/α)×V. 현대 최적화 표준.

## 추가 도구

Risk Parity(위험기여 균등, → stock-macro) · 변동성 타게팅(목표 변동성에 레버리지 조절) · 최대낙폭(MDD)·리스크 버짓팅 · Black-Litterman(추정오차 보완).

## 분석 워크플로우

1. 후보 자산/시그널의 기대수익·변동성·상관 추정(추정오차 의식).
2. 분산·효율적 투자선 관점에서 결합(과도 집중 점검).
3. 포지션 사이징 — fractional Kelly 또는 위험기여 균등.
4. 리스크 한도 — VaR/CVaR, MDD 한도, 종목·섹터 집중 한도.
5. 결론 — 비중안 + 리스크 지표 + 스트레스 시나리오.

## 출력 템플릿

```
## 포트폴리오/리스크 분석
### 입력: 자산별 μ·σ·상관 (추정 한계 명시)
### 비중안: [종목/자산 %] / 사이징 근거(Kelly fraction 등)
### 리스크: VaR(95/99%) / CVaR / 예상 MDD / 집중도
### 스트레스 시나리오 / 한 줄 결론 / 확인 필요
```

### 작성 예시

```
## (가상) 포트폴리오/리스크 분석
### 입력: 5종목 μ 8~15% / σ 20~40% / 상관 0.3~0.6 (추정오차 큼)
### 비중안: 단일 최대 20% 제한 / fractional Kelly(½)로 사이징
### 리스크: VaR(95%, 1개월) −9% / CVaR −14% / 예상 MDD −25% / 섹터 집중 점검
### 스트레스 시나리오: 위기 시 상관 1 수렴 가정 → 분산효과 소멸 재계산
### 확인 필요: ㉠각 자산 변동성·상관 추정 기간(데이터) → VaR 신뢰도
```

```python
# fractional Kelly 사이징 (½ Kelly) — scripts/kelly_var.py의 kelly_invest()와 동일 로직
f_full = (mu - rf) / sigma**2
weight = 0.5 * f_full          # 풀 Kelly의 절반
```

```python
# 모수적(정규) VaR/CVaR — scripts/kelly_var.py의 var_cvar()와 동일 로직
from statistics import NormalDist
z = NormalDist().inv_cdf(1 - conf)                 # conf=0.95 등
var = -(mu + z * sigma) * value
cvar = -(mu - sigma * NormalDist().pdf(z) / (1 - conf)) * value
```

```bash
python scripts/kelly_var.py   # 데모 실행 — mu/rf/sigma/승률/손익비 예시값으로 4개 함수 한 번에 출력
```

> **의존성**: `scripts/kelly_var.py`는 표준 라이브러리(`statistics.NormalDist`)만 사용 — pip 설치 불필요, Python 3.8+ 만 있으면 실행된다. Python 실행 환경이 없으면 스크립트 대신 위 두 코드블록의 수식(f*=(μ−r)/σ², VaR/CVaR 정규근사식)을 계산기·엑셀로 직접 계산해도 동일 결과.

❌ "기대수익 높은 종목에 50% 몰빵"
✅ "풀 Kelly는 드로다운 과다 → ½ Kelly + 단일 20% 한도. 위기 상관 1 가정 스트레스로 분산 붕괴 점검"

> 결과 저장·데이터 결측(대용 지표 폴백 포함)·빠른 사용은 `~/.claude\stock-experts\README.md` 공통 규칙을 따른다.
> **파일명 예시(이 스킬)**: `~/.claude\stock-experts\analyses\{YYYY-MM-DD}-{종목코드}-portfolio-risk.md` — 같은 종목 재분석 시 덮어쓰기 금지, 날짜 바꾼 새 파일로 이력 보존.

## 판정 분기 & 데이터 거부 시 처리

| 상황 | 처리 |
|---|---|
| μ·σ·상관 추정 신뢰 가능 | 효율적 투자선 + fractional Kelly(½) 비중안 + 한도 |
| 풀 Kelly가 단일 비중·portfolio heat 한도 초과 | **한도로 캡** — 풀 Kelly 초과 베팅은 파산확률 1 수렴(Archegos 교훈) |
| 위기 상관 1 수렴 가정 시 분산효과 소멸 | 스트레스 상관으로 재계산, 레버리지(risk parity) 절제 |
| μ·σ·상관 추정 데이터 결측 | 보수적 가정(상관 높임·σ 키움)으로 잠정 비중, "VaR 신뢰도 하" 표기. KRX는 위기 상관 급등 가정 |
| 사용자가 데이터 제공 거부 | partial 비중안 + 신뢰도(상/중/하), 전체 보류 금지. 입력 추정오차에 극민감("error maximization")·위기 시 무력 명시. 리스크 경고는 시그널 양호해도 veto 가중. 투자자문 아님·자기책임. |

## 거장의 실전 규율 (검증된 엣지)

- **실증 양면**: Ed Thorp의 Princeton Newport는 1969–88 **연 19.1%(15.1% net), 230개월 중 손실 3개월(모두 −1% 이내), 다운 연도 0**(Kelly 사이징+델타헤지) — 역사상 최고 위험조정. 반면 risk parity는 **2022 −19.5%/All Weather −22%**(상관 가정 붕괴, 주식·채권 +0.65).
- **수익이 아니라 위험 관리가 복리를 만든다**(Thorp). "너무 크게 베팅하면 거의 확실히 파산한다" → **fractional Kelly·비중 한도·portfolio heat**.
- **상관 가정의 취약성**: 위기 시 상관 1 수렴·2022 정(+) 상관 → 스트레스 테스트 필수, 레버리지(risk parity) 절제.
- 드로다운 단계별 축소(vol targeting)로 복리 붕괴 방어.

> 상세: `references/evidence-and-master-playbook.md`. 모든 사이징·최적화는 입력 추정에 민감 — 위기 시 무력. 룰 준수가 가장 어렵다(→ stock-behavioral).

### 실전 케이스 — Archegos (2021.3)

Bill Hwang의 패밀리오피스는 TRS(총수익스왑)로 **5배 이상 레버리지**를 일으켜 소수 종목(ViacomCBS 등)에 초집중 — 한 종목의 증자 발표발 하락이 마진콜 연쇄를 부르며 **이틀 만에 약 $20B의 자산이 증발**했고, 프라임브로커 측도 거액 손실(Credit Suisse 약 $5.5B). 수년간 '수익률 최고'였던 계좌가 청산까지 일주일이 안 걸렸다. 교훈: ① 풀 켈리 초과 베팅의 수학적 귀결은 '높은 기대수익'이 아니라 **파산 확률 1로의 수렴** ② 집중+레버리지+유동성 부족(보유 비중이 ADV 대비 과대)은 각각이 아니라 **곱으로** 위험을 키운다 — 단일 비중 한도·portfolio heat·청산 가능 일수를 같이 봐야 한다.

## 스크리너 구현 가드레일 (코드 강제 원칙)

이 스킬이 자문한 결과가 프롬프트 문구가 아니라 **자동매매/스크리너 코드**로 구현될 때 지켜야 할 최소 원칙. 사람이 매번 "분산 챙겨라"를 상기하는 구조는 반드시 무너진다 — **게이트는 코드로 강제**, 프롬프트 권고는 보조 수단일 뿐이다.

- **다전략 중복보유 모니터(필수)**: '전략이 다르다'는 것이 '유니버스·팩터가 다르다'를 보장하지 않는다. 여러 모의펀드/전략이 동일 종목을 동시에 담으면(예: 같은 대형 고배당주) 표면상 N개 전략이어도 실질 분산은 1개로 수렴한다. 구현: 종목별 `보유 전략 수` 카운터를 편입 시점마다 갱신 → **k개(예: 3개) 이상 동시 보유 시 경보를 하드코드**(신규 편입 함수 자체가 카운트 초과 시 편입 거부 또는 사이즈 축소 반환). 경보를 로그에만 남기고 편입을 막지 않으면 가드레일이 아니라 장식이다.
- **Effective N·HHI 상시 측정**: 전체 포트폴리오(모든 전략 합산 기준) 종목별 비중 w_i로 `HHI = Σw_i²`, `effective N = 1/HHI`를 매 리밸런싱마다 계산·로깅. effective N이 명목 종목 수 대비 크게 낮으면(예: 명목 30종목인데 effective N 5) 분산효과 소실 — 이 지표가 하락 추세면 신규 편입에 집중도 페널티를 곱한다.
- **쏠림 국면 사이징 게이트**: 특정 메가캡·섹터로 시장 전체 수급이 쏠리는 국면(→ stock-macro/stock-sector-rotation의 쏠림 지수와 연계)에는 개별 전략의 매력도 점수가 아무리 높아도 **그 종목에 대한 전체 포트 비중 상한**을 코드에서 낮춰 잡는다. 지수만 만들고 어떤 전략도 참조하지 않으면 리스크 관제가 아니다 — 지수 계산 함수의 출력이 실제로 사이징 함수의 입력 인자로 연결돼 있는지 배포 전 반드시 확인.
- **멀티매니저 업계 참고**: Millennium 등은 포지션 손실 5%(자본 절반 컷)·7.5%(포드 청산) 같은 **임계값을 자동 집행**하고, Citadel은 별도 리스크 조직이 상시 스트레스테스트·실시간 포지션 감시를 돌린다(공개 정보 기준, 세부 수치는 확인 필요). 개인 자동화 시스템도 "권고"가 아니라 "임계값 도달 시 자동 축소/차단"을 코드 경로에 넣는 것이 핵심.
- **근거**: 크라우디드 포지션은 되돌림(unwind) 국면에서 붕괴 위험을 높인다는 것이 다수 실증에서 확인된다(crowding이 평균수익보다 **꼬리 위험/급락 확률**과 강하게 연결). 2026년 3월 멀티전략 pod 겹침 이벤트에서 Millennium·Point72가 각 약 $1.5B, Citadel이 약 $1B(매크로·채권) 손실을 본 사례가 최신 참고(확인 필요: 정확한 손실액·1차 출처).

## KRX 적용

- **상관 급변**: 코스피는 위기 시 외국인 동반 매도로 종목 간 상관이 급등(분산 효과 증발) → 평시 상관에 기댄 비중은 위기에서 무력. 스트레스 상관으로 재점검.
- **환·해외 분산**: 원화 자산만으로는 분산 약함 → 미국주식·달러·금 편입으로 상관 낮춤(환헤지 여부 명시).
- **공매도 제약**: long-short·시장중립 구현 어려움 → long-only 내 비중·현금 비중으로 위험 조절.
- 거래세·유동성 반영한 실현 가능 비중(→ stock-execution 연계).

## 레퍼런스

- `scripts/kelly_var.py` — Kelly(투자형·베팅형)·모수적 VaR/CVaR·변동성 타게팅 계산기 (`python scripts/kelly_var.py` 데모).
- `references/markowitz-kelly-risk.md` — MPT·효율적 투자선, Kelly 공식·fractional, VaR/CVaR, Black-Litterman, 비판.
- `references/black-litterman-allocation.md` — Black-Litterman(균형+view), mean-CVaR 최적화, risk parity 통합, 변동성 타게팅·드로다운 통제, 상관 레짐.
- `references/position-sizing-systems.md` — 고정비율·ATR·fractional Kelly, risk of ruin, portfolio heat·상관 조정, 드로다운 단계 축소.
- `references/evidence-and-master-playbook.md` — 실증(Thorp 19.1%·230개월 중 3개월만 손실 vs risk parity 2022 −22%), Kelly/Thorp 규율, 시니어 체크.

## 한계

MPT는 정규분포·안정 상관 가정 → 위기 시 상관 1 수렴·두꺼운 꼬리. 입력(μ,σ,ρ) 추정오차에 극민감("error maximization"). 풀 Kelly는 드로다운 견디기 어려움·확률 오추정 시 파산 → fractional 필수. VaR은 초과손실 크기엔 침묵 → 꼬리는 stock-tail-risk로 보강.
