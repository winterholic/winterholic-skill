# 레퍼런스 — Joel Greenblatt (Magic Formula & Special Situations)

> 원저작: *You Can Be a Stock Market Genius*(1997), *The Little Book That Beats the Market*(2005/2010). Gotham 1985–94 연 ~50%.
> vault 소스: `sources/stock-investing/greenblatt-magic-formula-spinoffs.md`. 스킬 실행용 가공본.

## 1. Magic Formula

```
Earnings Yield    = EBIT / Enterprise Value
Return on Capital = EBIT / (순운전자본 + 순고정자산)
```
- EV/EBIT을 쓰는 이유: 부채·세금·이자 무관 비교. ROC는 tangible operating capital만 보고 quality 측정.
- 절차: 시총 하한 → 금융·유틸 제외 → 두 지표 순위 합산 → 상위 20~30 보유 → 1년 후 교체 → 3~5년 지속.

## 2. 백테스트 (원서, in-sample)

- 1988–2004 미국: Magic Formula 연 30.8% vs S&P 12.4%. 대형(상위1000)만 추려도 22.9%.
- 주의: in-sample. 출판 후(2005~) 알파 축소 후속연구 다수.

## 3. Special Situations 유형

| 유형 | 메커니즘 |
|---|---|
| Spinoff | 주주 자동수령 신주 → 가격무관 매도 → 저평가 |
| Merger arb | target가 vs 인수가 spread |
| Bankruptcy/Restructuring | 채권→주식 전환 valuation gap |
| Stub stock | 분사 후 잔여 사업 mispricing |
| Recap / Rights | 자본재편·권리락 디스카운트 |
| Index add/delete | 강제 매수·매도 일시 mispricing |

## 4. Spinoff 체크포인트

① 경영진 이동(skin in game) ② 보상의 주가 연동 ③ 부채 떠넘기기(leveraged spinoff) 경계 ④ 작아서 기관 강제매도 ⑤ 숨은 자산.
- Penn State 연구(1988–95): spinoff 평균 시장 대비 연 +10%.

## 5. Position Sizing

집중(5~8종목 80%), 단 각 포지션 downside가 명확히 제한(catalyst·헤지).

## 6. Quality+Value 정량화 비교

| 학파 | Quality | Value |
|---|---|---|
| Graham | (청산가치) | NCAV, P/B |
| Buffett | Moat+ROIC | Owner's earnings/EV |
| Greenblatt | ROC(EBIT/op.capital) | Earnings yield(EBIT/EV) |

## 7. Acquirer's Multiple (Tobias Carlisle)

Magic Formula에서 ROC를 빼고 EV/EBIT 단독. 비슷하거나 더 나음 → quality가 이미 가격에 반영됐을 가능성, 순수 cheapness가 알파 원천일 수 있음.

## 8. KRX 적용

- 인적분할 vs 물적분할(쪼개기 상장) — 미국 spinoff와 가치이전 방향 다름, 반드시 모·자 가치 점검.
- 지주사 디스카운트·자사주 분할합병 가치이전.
- 국내 변형: 강환국 등 EV/EBIT+GP/A. 금융·지주·시클리컬 제외·정상화 신중.

## 8.5 심화 — SKILL.md 비중복

- **Spinoff 진입 타이밍**: 수익은 분리 직후가 아니라 **기관 강제매도 소화 후**에 집중 — 학술 연구(Cusatis 등)는 초과수익이 1~3년차에 분포한다고 봄(확인 필요: 연차별 분해). 재상장 첫 주 추격보다 매도 압박 소진(거래량 안정) 확인 후 진입.
- **Parent vs Spinoff 선택**: 보통 작고 미운 쪽(spinoff)이 기회지만, 반대로 **부실을 spinoff에 떠넘기고 가벼워진 모회사**가 기회인 경우도 — 부채·연금·소송이 어느 쪽에 실렸는지가 선택 기준.
- **Merger securities**: 합병 대가로 받는 비주식 증권(워런트·우선주·채권)은 받는 쪽 누구도 원치 않아 기계적 투매 — spinoff와 동일한 구조적 비효율. 한국에선 합병 반대매수청구권 가격과 시가 괴리가 유사 기회.
- **옵션/LEAPS 활용**: 이벤트 시점이 특정되는 특수상황은 장기 콜옵션으로 downside 한정 + 레버리지 — 단 이벤트 지연이 옵션 만기를 넘기는 리스크가 본질적 비용.
- **마법공식 운용 디테일**: 연 1회 교체 시 **손실 종목은 1년 미만, 이익 종목은 1년 초과 보유 후 매도**(미국 세제 기준 — 한국은 대주주 요건 외 양도세 없어 무관). 한 번에 전체가 아니라 분기별 1/4씩 진입해 타이밍 리스크 분산.

## 9. 비판과 한계

출판 후 알파 감소(in-sample). 특수상황 개별 난도 높음. 이벤트 무산·구조조정 실패 시 큰 손실.

## 10. 2024–2026 최신 실증 업데이트 (SKILL.md에서 이동)

- **마법공식 알파 감소 재확인**: 2003.7–2015.12 미국 백테스트 연 11.4% vs S&P500 8.7%(약 +3%p) — 2007년 이전 연 26%대에서 크게 둔화(quant-investing.com 2026 update). 2010–2021 구간은 alpha가 통계적으로 유의하지 않다는 학술 분석 존재(Reasonable Deviations, 2020; 확인 필요: 표본·방법론 세부). 2016–2025 유로존 백테스트(마법공식+6개월 모멘텀)는 연 +11.3%(가격 기준) vs STOXX Europe 600 +5.3% — 다만 2018·2019·2022–2024는 벤치마크 하회, 2021·2025만 크게 상회(quant-investing.com). **결론: 알파는 소멸이 아니라 "변동성 커지고 지속 하회 구간 잦아짐" — 3~5년 drawdown을 견딜 시계 없으면 원서 그대로 못 씀.**
- **스핀오프 최근 강세**: Bloomberg Spin-Off Index(BNSPIN)가 2024년 YTD +38%로 S&P500 대비 약 +26%p 아웃퍼폼, 2020년 이후 누적으로도 S&P500 대비 +38%p(Forbes, 2024.6). 매수-보유 전략은 재상장 후 6/12/24/36개월 시점에 각각 +9.52%/+43.22%/+82.58%/+139.04% 초과수익 보고(출처 불명확 — 확인 필요: 원 연구 저자·표본기간). 2025년 인도 시장 163건 스핀오프 발표 연구는 발표 전후 누적초과수익 +3.32%(SAGE Journals, 2025). **스핀오프 알파는 마법공식보다 최근에도 견고하게 관측됨 — Greenblatt의 "진짜 무기는 특수상황이지 정량 스크린이 아니다"는 명제와 부합.**
- **출처**: [Magic formula investment strategy back test (2026 update)](https://www.quant-investing.com/blog/magic-formula-investment-strategy-back-test) · [A critical look at Greenblatt's Magic Formula](https://reasonabledeviations.com/2020/06/08/greenblatt-magic-formula/) · [US Spin-Offs Beat S&P 500 (Up 34% YTD)](https://www.forbes.com/sites/joecornell/2024/06/03/us-spin-offs-beat-sp-500-up-34-ytd/) · [Corporate Spin-offs and the Wealth of Shareholders: Evidence from India](https://journals.sagepub.com/doi/10.1177/09721509251321613)

## 11. 실패 모드 / fallback (SKILL.md에서 이동, 원문 보존)

| 상황 | 처리 |
|---|---|
| 사용자가 분석 자체를 거부·중단 | 강요 금지. 사유(정보 부족·관심 없음 등)만 한 줄 로깅하고 종료. 부분 산출(스크린 결과만)이라도 원하면 그 범위만 제공. |
| 데이터 결측(EBIT·EV·spread 등) | 대용 지표 폴백(README 공통 규칙) → 그래도 불가면 해당 지표 "산출 불가" 표기, 나머지로 partial 분석 후 한계 명시. |
| 이벤트 유형 분류가 모호 | 가장 가까운 유형 1개로 잠정 분류 + "유형 불확실" 라벨, 사용자에게 추가 정보 요청. |
| 합병 무산·구조조정 실패 시나리오 | 진입 전 반드시 downside floor(청산·순현금) 먼저 계산. floor 산출 불가 = 진입 근거 부족 → "회피/관찰". |

> 위 어느 경우든 **투자 권유가 아니라 분석 보조**다. 최종 판단·책임은 사용자에게 있다.

## 12. 판단 불가 / 데이터 막힘 시 (누가·언제·어떻게·기대값) (SKILL.md에서 이동, 원문 보존)

분석 중 핵심 입력이 비면 멈추지 말고 `[확인 필요]` 블록으로 사용자에게 질의한다 — 4요소를 한 줄에 명시:

- **누가/언제**: 분할계획서·합병계약서·공시(DART) 미확인으로 부채 배분·deal terms를 모를 때, 분석 중단 시점에 즉시.
- **어떻게**: `[확인 필요] 항목=<분할 시 부채 배분 비율> / 출처=<분할계획서 공시일·DART> / 현재 가정=<순현금 spinoff 전제> / 기대 답변=<부채 떠넘기기 여부 Y/N>`.
- **확인 결과 해석**: 부채 떠넘기기=Y면 leveraged spinoff → 본 분석의 downside 가정 붕괴, "회피"로 재분류. N이면 진입 가정 유지.
- **확인 불가 시 대체 경로**: 공시가 아직 안 나왔으면 "재상장/공시 후 재평가" 관찰 등급으로 보류하고, 추정치 사용 시 반드시 "추정·확인 필요" 라벨을 결론에 병기(추정으로 진입 판단 금지).

## 13. 결과 파일 저장 규칙 (SKILL.md에서 이동, 원문 보존)

- **파일명**: `special-sit_<종목/티커>_<YYYY-MM-DD>.md` (이벤트성이라 날짜 필수 — 같은 종목도 이벤트 진행에 따라 결론이 바뀜).
- **위치**: README가 지정한 stock-experts 공통 출력 경로. 경로 없으면 생성 여부를 사용자에게 확인.
- **append vs overwrite**: 같은 종목·같은 날짜 파일이 이미 있으면 **overwrite 금지** — 기존 분석을 보존하고 `_v2` suffix로 새로 저장하거나, 이벤트 경과 업데이트면 같은 파일 하단에 `## 업데이트 <날짜>` 섹션으로 **append**. 과거 판단 추적이 사후채점(stock-scorecard)에 필요하므로 덮어쓰지 않는다.

## 14. 한국 물적분할·쪼개기 상장 제도 개정 (2024–2026, SKILL.md KRX 섹션 보강분)

- **2024.12 자본시장법 개정**: 합병·분할 시 이사회의 주주이익 보호 의무 신설, 물적분할 후 자회사 상장 시 공모주 20%를 모회사 주주에게 배정하는 조항 포함. 합병가액도 주가·자산가치·수익가치를 종합한 공정가액 기준으로 변경(한국경제, 2024.12.2).
- **2026.7 상장·공시규정 개정("쪼개기 상장" 제동)**: 기존 상장사가 물적분할한 자회사를 중복상장하려면 모회사 주주 동의가 의무화. 최대주주 의결권은 3%로 제한("3%룰", 상법상 감사위원 선임 방식 준용), 출석주주 의결권 과반 + 발행주식총수 1/4 이상 찬성 요건. 모회사 이사회 산하 독립 특별위원회가 주주 보호방안(자회사 지분 배분·자사주 소각 등)을 마련해 동의를 구해야 함(한국일보·파이낸셜뉴스, 2026.7.6).
- **배경**: 최근 5년간 상장사 기업분할 10건 중 8건이 물적분할 — 모회사가 자회사 지분을 독점한 채 상장으로 자금만 조달하고 기존 주주는 자회사 지분을 못 받는 구조가 반복 지적됨(서울신문, 2025.7.3).
- **특수상황 스킬 시사점**: 이 개정으로 향후 물적분할 발표 자체가 "주주가치 훼손 이벤트"에서 "주주동의·특별위원회를 거쳐야 하는 협상 이벤트"로 성격이 바뀔 가능성 — 물적분할 공시 시 ①모회사 주주 동의 요건 충족 여부 ②특별위원회 구성·독립성 ③주주 보호방안(공모주 20% 배정·자사주 소각) 실질 여부를 촉매/downside 점검 항목에 추가할 것. 시행 초기라 실제 사례 축적은 "확인 필요".
- **출처**: [상장사 합병·분할때…소액주주 보호 명시](https://www.hankyung.com/article/2024120289591) · ['쪼개기 상장' 제동…물적분할 자회사 중복상장 땐 주주동의 의무화](https://www.hankookilbo.com/news/article/A2026070616290005102) · ['쪼개기 상장' 제동…정부, 모회사 주주동의 없는 중복상장 원칙적 금지](https://www.fnnews.com/news/202607061154343364) · [기업분할 10건 중 8건 물적분할](https://www.seoul.co.kr/news/plan/ProtectingShareholderValue/2025/07/03/20250703002003)

## 15. `scripts/magic_formula.py` 데모 실행 결과 (SKILL.md 레퍼런스 항목 상세)

`python scripts/magic_formula.py` 실행 시 표준 라이브러리만으로 다음이 출력된다(가상 3종목 데모):

```
== 데모 ==
{'name': '갑', 'EY%': 18.8, 'ROC%': 27.3, '종합순위점수': 3}
{'name': '을', 'EY%': 20.0, 'ROC%': 22.5, '종합순위점수': 3}
{'name': '병', 'EY%': 9.2, 'ROC%': 14.7, '종합순위점수': 6}
합병차익: 스프레드 4% / 90일 -> 연율화 16.2%
기대값: 성사 90% x +4% vs 무산 시 -15% -> +2.10%
```

- 종합순위점수는 EY 순위 + ROC 순위(낮을수록 저평가·고수익성 상위) — 갑·을이 동률 3점으로 공동 1위, 병이 6점으로 최하위.
- 실전 사용 시: `from magic_formula import earnings_yield, roc, magic_rank, arb_annualized, arb_expected`로 임포트 후 실제 종목의 EBIT·EV·순운전자본(nwc)·순고정자산(nfa) 값을 딕셔너리 리스트로 넣어 `magic_rank()` 호출. 합병차익은 `arb_annualized(스프레드%, 잔여일)`과 `arb_expected(이익%, 성사확률, 무산시손실%)`로 별도 계산.
