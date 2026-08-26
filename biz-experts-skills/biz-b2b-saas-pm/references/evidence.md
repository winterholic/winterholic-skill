# biz-b2b-saas-pm — 프레임 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 웹 검증. 1단계 참조.

## 1. 이해관계자 분리 (Lean B2B)
구매자(economic buyer)·사용자(end user)·관리자(admin)·챔피언. 각각 니즈 따로. Étienne Garbugli, *Lean B2B*(2판 부제 "Learn to Build Products Businesses Want"). https://leanb2bbook.com/

## 2. SaaS 지표
- NRR(확장 포함, >100% 가능) vs GRR(확장 제외, ≤100%). **NRR ≠ GRR ≠ 전체 성장** — 혼동 금지. 고 NRR이 logo churn 가릴 수 있어 둘 다 본다. Stripe 설명: https://stripe.com/resources/more/net-revenue-retention-vs-gross-revenue-retention
- LTV:CAC ≥3:1(Skok). Rule of 40(스케일 단계).
- 캐즘: Geoffrey Moore *Crossing the Chasm*(1991/2014) — 비치헤드 니치 장악 후 확장.

## 3. 엔터프라이즈 게이트 (표준·1차 출처)
- **SAML 2.0**(OASIS, 2005) https://www.oasis-open.org/standard/saml/ — 인증.
- **OIDC Core 1.0**(2014) https://openid.net/specs/openid-connect-core-1_0.html — 인증.
- **SCIM 2.0**(RFC 7643/7644, 2015) https://datatracker.ietf.org/doc/html/rfc7643 — 프로비저닝.
- **RBAC**(NIST, ANSI/INCITS 359) https://csrc.nist.gov/projects/role-based-access-control
- **SOC 2**(AICPA) — **인증(certification)이 아니라 attestation(증명)**. ISO 27001이 인증. SOC 1=재무통제.
> 교정: SAML/OIDC=인증, SCIM=프로비저닝(대체재 아닌 상보재). NRR≠GRR.

## 4. 실전 케이스 (SEC 1차 대조)
- **Snowflake**: NRR **158%**(S-1, 2020-07-31 기준 6개월) — 소비량(consumption) 기반, IPO 시점 최고 수준. SEC EDGAR 원문(S-1, CIK 1640147, accession 000162828020013010) URL은 WebFetch 자동 접근 403(SEC가 봇 User-Agent 차단) → S-1 teardown(Meritech/PublicComps) 2차 교차로 158% 일치 확인. 직접 인용 시 EDGAR에서 수동 열람: https://www.sec.gov/Archives/edgar/data/1640147/000162828020013010/snowflakes-1.htm
- **Datadog**: dollar-based net retention rate(S-1, CIK 1561550, 2019-08-23 제출) **146%**(2018-06-30·2019-06-30 기준), 직전 12-31 기준은 **141%(2017)·151%(2018)**. 이후 다수 분기 130%+ 유지(공식 수치는 미공개 구간 있음). S-1 본문 1차 수치. https://www.sec.gov/Archives/edgar/data/1561550/000119312519227783/d745413ds1.htm
> 주의: "130%/150%" 같은 라운드 인용보다 S-1 원문 수치(Snowflake 158%, Datadog 146%/141%/151%)를 쓴다. MoviePass/Blue Apron/WeWork/Groupon 등 실패 사례를 인용할 때도 SEC 공시(10-K·S-1) 원문을 1차로 대조할 것 — 본 팩에는 미수록.

## 5. 컴플라이언스·조달 게이트 (검증)
- **SOC 2 Type I vs Type II**: Type I=특정 시점의 통제 **설계** 평가 / Type II=**6~12개월 운영 효과성** 평가. 엔터프라이즈·규제 환경은 거의 Type II 요구(설득력 큼). 둘 다 **SSAE 18** 감사기준 하에 수행, **attestation(증명)이지 certification 아님**. https://secureframe.com/blog/soc-2-type-ii
- **Trust Services Criteria(TSC) 5범주**: Security(필수)·Availability·Processing Integrity·Confidentiality·Privacy. Security가 모든 SOC 2의 기반(공통 범주). https://www.schellman.com/blog/soc-examinations/soc-2-trust-services-criteria-with-tsc
- **SIG / 벤더 보안 설문**: 엔터프라이즈 조달은 보안팀·리스크·구매·컴플라이언스가 함께 벤더 실사(SIG 등 표준 설문). SOC 2 Type II 보고서가 이 과정을 크게 단축.
> 교정: SOC 2 = attestation(AICPA), ISO 27001 = certification. SOC 1 = 재무보고 통제(SaaS 보안엔 SOC 2). Type I ≠ Type II(설계 vs 운영효과) — 딜에서 "SOC 2 있음"만으론 부족, Type II·범주 확인.

## 6. 출처·교정
- Garbugli, *Lean B2B*. https://leanb2bbook.com/lean-b2b-build-products-businesses-want-book/
- David Skok, SaaS Metrics 2.0. https://www.forentrepreneurs.com/saas-metrics-2/
- MEDDIC/MEDDPICC — PTC(1996), Dick Dunkel(약어)·Jack Napoli(전파). https://meddicc.com/
- PLG 코인 = OpenView/Blake Bartlett(2016). Rule of 40 = Brad Feld가 대중화(발명 아님, 2015).
