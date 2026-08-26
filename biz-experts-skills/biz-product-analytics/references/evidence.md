# biz-product-analytics — 프레임 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 웹 검증. 1단계 참조.

## 1. HEART (Google, 2010)
Happiness·Engagement·Adoption·Retention·Task success. 각 차원을 **Goals→Signals→Metrics(GSM)**로 구체화.
> 저자 = **Rodden, Hutchinson, Fu**(3인 공저), "Measuring the User Experience on a Large Scale," CHI 2010(ACM). Rodden 단독 아님. https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/ · 저자 해설 https://kerryrodden.com/heart/

## 2. AARRR (Dave McClure, 2007)
Acquisition·Activation·Retention·Revenue·Referral. "Startup Metrics for Pirates," Ignite Seattle **2007**(2012 덱은 재업로드). https://www.slideshare.net/slideshow/startup-metrics-for-pirates-long-version/89026

## 3. 좋은 지표 (Lean Analytics, 2013)
Croll & Yoskovitz. 비교가능·이해가능·비율(rate)·**행동 유발**. OMTM(One Metric That Matters). https://www.oreilly.com/library/view/lean-analytics/9781449335687/

## 4. North Star
용어=Sean Ellis(~2010), 프레임 정형화=Amplitude/John Cutler(North Star Playbook, 2017). https://amplitude.com/resources/north-star-playbook

## 5. 통계 함정 (학술 앵커)
- **Simpson's paradox**: Bickel, Hammel, O'Connell, "Sex Bias in Graduate Admissions: Data from Berkeley," *Science* 187(4175):398–404, **1975**(데이터는 1973 가을). https://www.science.org/doi/10.1126/science.187.4175.398
- **생존자 편향**: Abraham Wald(통계연구그룹, WWII 항공기 장갑, 1943).
- **상관≠인과**: Tyler Vigen *Spurious Correlations*(대중) https://www.tylervigen.com/spurious-correlations · 엄밀 앵커 Judea Pearl & Dana Mackenzie, *The Book of Why*(Basic Books, 2018).
- **온라인 A/B 실험 권위 앵커**: Kohavi, Tang & Xu, *Trustworthy Online Controlled Experiments*(Cambridge Univ. Press, 2020) — Microsoft/Amazon/Google 실험 플랫폼 1차 정리(피킹·다중비교·SRM(sample ratio mismatch) 등 함정 포함). https://experimentguide.com/

## 6. 이벤트 택소노미 (Amplitude·Mixpanel 1차, 검증)
- **Object-Action 프레임**: Amplitude·Mixpanel 공통 권장. Object=명사(사용자가 상호작용하는 대상), Action=동사(과거형). 예: `Form Submitted`, `Button Clicked`, `Page Viewed`. https://amplitude.com/explore/data/event-taxonomy · https://growthmethod.com/object-action-framework/
- **동사 과거형** 권장 — 이미 성공적으로 일어난 기록임을 명확히("Played", "Completed").
- **케이싱**: Mixpanel=데이터웨어하우스 익스포트 고려 시 `snake_case` 권장 / Amplitude 기본 이벤트=Title Case(`[Noun] + [Past-tense Verb]`). 사내 하나로 통일이 핵심.
- **Tracking Plan(추적 계획)** = 살아있는 SSOT 문서: 이벤트명·정의·기대 속성·수집 이유·**담당 오너**를 명시, 분기별로 중복·폐기·모호 이벤트 점검. https://amplitude.com/docs/data/data-planning-playbook
> 교정: 이벤트 이름 자유 방임 → 나중에 중복·해석 불일치로 분석 붕괴. 코드 붙이기 전에 택소노미 합의(SKILL 안티패턴 5). 구현(SDK·SQL)은 → dev-data-analysis.

## 7. 교정
- HEART = 3인 공저(Rodden 단독 아님). AARRR = 2007. NSM = Amplitude가 정형화(발명 아님). Simpson 사례는 "Bickel et al. 1975"로 인용하되 데이터는 1973.
