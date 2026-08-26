# 레퍼런스 — Taleb & Spitznagel (Tail Risk Hedging)

> 원저작: Taleb *The Black Swan*(2007)·*Antifragile*(2012); Spitznagel *Safe Haven*(2021).
> vault 소스: `sources/stock-investing/taleb-spitznagel-tail-risk.md`. 스킬 실행용 가공본.

## 1. 정체성

평균·분산이 놓치는 fat tail을 다룸. 정상 구간 소폭 손해 + 블랙스완 폭발 보상의 비대칭(convex) 설계.

## 2. Black Swan & Extremistan

블랙스완=예측불가+막대충격+사후합리화. Extremistan=두꺼운 꼬리(power law)→가우시안 VaR/MPT 과소평가.

## 3. Antifragile

취약/강건/반취약(충격에서 이득). 변동성에서 이익 보는 포지션(볼록성).

## 4. Barbell

~90% 극안전(국채/현금) + ~10% 극공격·볼록(OTM 옵션·VC, 손실 투입액 한정). 하방 막힘+상방 열림.

## 5. Tail Hedging (Spitznagel)

지수 깊은 OTM 풋 상시 보유→평시 소액 출혈, 20%+ 급락 시 기하급수. *Safe Haven*: 좋은 헤지는 비용이 아니라 기하평균(복리)을 높임(큰 손실 방지). cost-effective 안전자산만 진짜.

## 6. Volatility Tax

기하 ≈ 산술 − σ²/2. 드로다운 방지가 장기 부의 핵심.

## 7. Taleb vs Spitznagel

사상 공유(Empirica 공동설립). Spitznagel(Universa)=실증·복리 강조, Taleb=인식론·철학.

## 8. KRX 적용

KOSPI200 풋(OTM)·인버스 ETF·달러·미국채. 원화 약세 동조→달러가 자연 헤지(우선 검토). 공매도 금지 국면→풋·인버스·현금. ±30%·서킷브레이커로 급락 분산(익절 타이밍).

## 8.5 심화 — SKILL.md 비중복

- **Deep OTM 풋의 수익 구조**: 급락 시 수익의 큰 몫은 내재가치가 아니라 **IV 폭등(베가)** 에서 온다 — 그래서 급락 '직후 IV 정점'이 익절 적기(기다리면 IV 수축으로 반납). 감마·베가 롱 / 세타 숏 구조임을 알고 보유.
- **Put vs Put-spread vs Collar**: 스프레드는 보험료를 줄이지만 **볼록성(폭발적 보상)을 상한으로 자른다** — 테일 헤지 목적엔 plain put이 정통, 스프레드는 '중간 규모 하락' 헤지용. Collar는 상방까지 팔아 비용 0에 가깝게 하나 강세장 수익 포기.
- **롤오버 실무**: 만기 2~3개월짜리를 보유하다 만기 ~1개월 전 롤(세타 가속 구간 회피)이 일반적(확인 필요: Universa 실제 규칙은 비공개). 행사가는 지수 대비 20~30% OTM대 — 더 깊으면 싸지만 '중간 폭락'에 안 깨어난다.
- **VIX 콜 vs 지수 풋**: VIX 콜은 변동성에 직접 베팅하나 **선물 term structure 롤비용**(콘탱고)이 상시 누수 — 지수 풋보다 carry가 비쌀 수 있다. 수단별 비용 구조 비교가 cost-effectiveness의 실체.
- **'안전자산'은 레짐 의존**: 2022년엔 국채도 주식과 동반 하락(인플레 레짐) — 디플레형 폭락(2008·2020)의 안전자산(국채)과 인플레형(2022)의 안전자산(원자재·달러·단기물)이 다르다. 헤지 포트폴리오도 단일 수단이 아니라 레짐별 조합.

## 9. 비판과 한계

평시 보험료 출혈(블랙스완 지연 시 누적 손실)·롤오버 비용. 성과 측정·심리 유지 곤란. crowding 시 IV↑로 기대수익 훼손.
