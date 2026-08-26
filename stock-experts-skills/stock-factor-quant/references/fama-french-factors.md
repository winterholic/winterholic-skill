# 레퍼런스 — Fama-French Factor Models

> 원논문: FF(1992, 1993, 2015), Carhart(1997).
> vault 소스: `sources/stock-investing/fama-french-factors.md`. 스킬 실행용 가공본.

## 1. CAPM 한계

`E(Ri)−Rf = βi(E(Rm)−Rf)` — 시장 1팩터. 분산 포트 수익의 ~70%만 설명. anomaly: 소형주(Banz 81), 가치(Basu 77), 모멘텀(Jegadeesh-Titman 93).

## 2. FF 3-factor (1993)

`Ri−Rf = α + βmkt(Rm−Rf) + βsmb·SMB + βhml·HML + ε`
- SMB = 소형 long − 대형 short(규모). HML = 고B/M long − 저B/M short(가치, B/M=1÷PBR).
- 설명력 ~90%(in-sample).

## 3. Carhart 4-factor (1997)

+ MOM(UMD) = 12-1개월 상위 long − 하위 short. 펀드 알파 평가 표준. 모멘텀은 위험 기반 설명 어려움(behavioral 우세).

## 4. FF 5-factor (2015)

+ RMW(수익성: 고영업이익률 long−저 short) + CMA(투자: 저자산성장 long−고 short).
- 5팩터 도입 후 HML이 중복(redundant)화. 모멘텀 미포함이 약점.
- 미국 1963–2013: SMB·HML·RMW·CMA 각 월 +0.3~0.4% 수준(확인 필요: 정확 수치).

## 5. q-factor (Hou-Xue-Zhang 2015)

MKT·SIZE·I/A·ROE 4개로 5팩터급 설명, 모멘텀 일부 흡수.

## 6. 팩터 zoo

Value·Size·Momentum·Quality(ROE·GP/A·accruals·F-score)·Low-Vol/BAB·Investment·Profitability·Liquidity(Amihud).

## 7. 운용 흐름

시그널→점수→다중팩터 합성(EW/IC/최적화)→포트 최적화(Markowitz·RP·BL)→거래비용·세금·임팩트 차감 net alpha→리밸런싱.

## 8. 알파 vs 베타

팩터 수익=스마트베타(알파 아님). 진짜 α=잔차. 4~5팩터 회귀로 α 분해, α의 t-stat 유의해야 실력.

## 9. KRX 연구

HML·MOM 한국 유효(IMF 전후 구조 변화). 가치+퀄리티 안정. 데이터 FnGuide·WiseFn. 강환국 PER+GP/A 우위. 소형주 거래비용·공매도 제약 → long-only tilt.

## 10. 데이터 리소스

Kenneth French Data Library, AQR Data Library, WRDS. Python `pandas-datareader.famafrench`, `linearmodels`.

## 10.5 심화 — SKILL.md 비중복

- **팩터 구성 절차(원전)**: 매년 6월 말 리밸런스, size(중앙값 2분할) × B/M(30/70 분위 3분할) **2×3 정렬** → 6개 포트의 가중평균 차이로 SMB·HML 산출. 직접 한국판 팩터를 만들 때 이 절차를 따라야 문헌과 비교 가능.
- **가치-모멘텀 음(−)상관**: 두 팩터는 역사적으로 약한 음의 상관 — 합성 시 분산효과가 커서 'value+momentum 50:50'이 단일 팩터보다 샤프가 높다(AQR *Value and Momentum Everywhere*). 다중팩터의 1차 근거.
- **BAB의 경제 논리(Frazzini-Pedersen)**: 차입 제약이 있는 투자자가 고베타로 레버리지를 '대신'하므로 고베타가 과대평가 → 저베타 매수·고베타 공매도가 프리미엄. 논리가 있는 팩터(차입제약)와 데이터마이닝 팩터를 구분하는 예시.
- **거래비용 후 생존**: 모멘텀은 회전율이 높아 net 프리미엄이 가장 많이 깎인다 — 소형주 SMB도 마찬가지. **저회전 구현**(리밸런스 완화·밴드 리밸런싱)이 팩터 실현의 절반.
- **팩터 타이밍 논쟁**: Arnott(밸류에이션 기반 타이밍 가능) vs Asness(타이밍은 또 하나의 액티브 베팅, 상시 분산 우위). 이 스킬은 Asness 편 — 단 팩터 스프레드가 역사적 극단(예: 가치 스프레드 99퍼센타일)일 때 틸트 강화 정도는 허용.

## 11. 비판과 한계

in-sample 과적합. 팩터 zoo 300+(Harvey-Liu-Zhu 2016, t-stat hacking). 프리미엄 수년 부진 가능. 군집화로 감소.
