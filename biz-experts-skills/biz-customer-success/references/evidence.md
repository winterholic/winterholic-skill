# biz-customer-success — 프레임 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 웹 검증(2026-07-01 심화). 1단계 참조.
> 실무 절차·플레이북·계산식은 `playbook.md`로 분리. 이 문서는 출처·검증사실.

## 1. 정전 소스
- **Mehta·Steinman·Murphy, *Customer Success*(Wiley, 2016)** — CS를 하나의 학문·기능으로 정립. "10 laws of customer success"(예: sell to right customer / customer is on a journey / relentlessly proactive / obsessively improve time-to-value 등). https://www.wiley.com/
- **Desired Outcome = Required Outcome + Appropriate Experience** — Lincoln Murphy(Sixteen Ventures). "고객이 원하는 결과(RO)를 그들이 원하는 방식(AE)으로 얻어야 성공"이라는 정의. https://sixteenventures.com/customer-success-definition
- **Tien Tzuo, *Subscribed*(2018, Zuora CEO)** — 소유→구독 전환, 매출 대부분이 기존 고객 갱신·확장에서 나오는 경제 구조.
- **Gainsight(Nick Mehta)** — CS 소프트웨어 카테고리 정립자. 헬스스코어·플레이북·QBR·세그멘테이션(하이/테크/디지털터치)의 실무 표준 상당수가 Gainsight 자료로 유통됨(벤더 자료임을 유의 — 방법론 참고용). https://www.gainsight.com/customer-success/

## 2. 지표 (NRR/GRR) — 1차 우선

### 정의(불변)
- **GRR(Gross Revenue Retention)**: 확장 제외, 이탈·다운그레이드만 반영 → **이론상 ≤100%**.
- **NRR/NDR(Net Revenue Retention/Dollar-based Net Retention)**: 확장(업셀·크로스셀) 포함 → **>100% 가능**.
- ⚠️ **NRR ≠ 이탈 지표**: 고 NRR이 큰 logo churn을 가릴 수 있음 → NRR·GRR **둘 다** 봐야 함(불변).

### 벤치마크 (출처별 — 수치 편차 큼, 맥락 필수)
- **Stripe**: 중앙값 NRR ~102% · GRR ~91%. https://stripe.com/resources/more/net-revenue-retention-vs-gross-revenue-retention
- **ChartMogul SaaS Retention Report(1차, N=2,100+ SaaS 익명·집계 데이터)** — 사기업 B2B SaaS 2024 기준 **중앙값 NRR ~101%, 중앙값 GRR ~88%(2022 ~90%에서 하락)**. ARR 규모가 클수록 상위분위 NRR 상승(예: $15–30M ARR 세그 상위분위 105%+). https://chartmogul.com/reports/saas-retention-report/ · 2023 PDF https://chartmogul.com/reports/saas-retention-report/saas-retention-report-2023.pdf
  - ⚠️ ChartMogul "중앙값 NRR 82%"류 수치는 **특정 코호트(AI-native/신생 등) 또는 특정 리포트판** 값으로, 전체 사기업 SaaS 중앙값(~101%)과 혼동 금지. 인용 시 어느 리포트·어느 코호트인지 명시.
- **세그먼트별(ACV 기준)** — 흔히 인용: Enterprise(ACV>$100K) ~118% · Mid-market($25K–100K) ~108% · SMB(<$25K) ~97%. ⚠️ **이 세그먼트 수치의 1차 출처는 확인 필요**(Optifai N=939 등 2차 종합 블로그에서 유통 — Optifai/digitalapplied는 1차 아님). 방향성(대형>중형>SMB, SMB는 100% 미만으로 축소 경향)은 여러 소스가 일치하나 정확 수치는 보수적으로 다룰 것.

### 스냅샷 케이스(1차 확정 — 불변)
✅ **Snowflake Form S-1(SEC, 2020)**: **NRR(NDR) 169%**(FY2020, 2020-01-31 종료 회계연도) / **158%**(2020-07-31 기준, 상장 직전 H1). 기존 메모의 "FY22 158%"는 연도 오기 → S-1 수치로 확정. https://www.sec.gov/Archives/edgar/data/1640147/000162828020013010/snowflakes-1.htm

## 3. 헬스스코어 (표준 공식 없음 — 불변)
- **표준 공식 없는 실무 구성물**(불변). 회사·제품·세그먼트마다 다르게 설계. "남의 공식 복사"는 실패 — 자사 가치 동인 기반이어야. https://www.gainsight.com/blog/customer-health-scores/
- 실무 관행: 보통 **4~6개 신호**를 가중합, 0–100 또는 R/Y/G로 시각화. 예시 가중치(Gainsight 블로그 예시) — 사용 40% / 지원 추세 25% / 감정(sentiment) 20% / 임원 참여 15%. ⚠️ **예시일 뿐 정답 아님**.
- **첫 헬스스코어 = 가설**이다. 이탈/확장 예측력을 주기적으로 검증하고 반복(iterate)해야. CSM 정성 입력(수동 오버라이드·감정 가중)도 결합 가능. https://www.gainsight.com/blog/choosing-your-customer-health-score-model/
- 신호 예: 제품 사용(폭·깊이·빈도), 성과 달성, 관계(챔피언·멀티스레딩), 지원(티켓 심각도·추세), 결제(연체), NPS/감정, 계약 단계.

## 4. QBR (Quarterly Business Review)
- 목적: **가치 리뷰 + desired outcome 재정렬 + 다음 분기 계획** — 제품 시연장이 아니라 고객 사업 목표 정렬 자리.
- 표준 아젠다: 지난 분기 성과·win·블로커 → 고객 사업 지표(도입률·기능 활용·time-to-value·정량 효익) → 현재 목표 재확인(목표는 시간이 지나며 이동) → 다음 분기 우선순위·측정가능 목표 → **소유자·기한 있는 액션 아이템**으로 마감. https://www.gainsight.com/essential-guide/quarterly-business-reviews-qbrs/
- 준비: 아젠다 사전 배포, 사용 지표·피드백·지원 이력 사전 수집. ⚠️ QBR이 "모든 고객·매분기 필수"는 아님(테크터치·소액 세그는 비효율일 수 있음 — 세그먼트에 맞춰).

## 5. 교정 (오류 방지)
⚠️ **NRR≠GRR** — NRR을 churn 지표로 쓰는 게 최빈 오류. 둘 다 보고.
⚠️ **헬스스코어 = 표준 공식 없음** — 벤더 예시 가중치를 정답처럼 인용 금지. 자사 데이터로 예측력 검증·반복.
⚠️ CS ≠ 반응형 support/account management — 선제·outcome 지향(만족 ≠ 성공).
⚠️ 갱신은 갱신일이 아니라 첫날부터 만들어짐 — 막판 할인은 원인 미해결 시 다음 해 재이탈.
⚠️ NRR 벤치마크는 산업·규모·세그·리포트판별 편차 큼 — 단일 수치 단정 금지("확인 필요").

## 6. 출처
- Mehta et al.(2016). · Murphy(Sixteen Ventures). · Tzuo(2018). · Stripe(NRR/GRR). · ChartMogul SaaS Retention Report(1차, N=2,100+). · Snowflake S-1(SEC 2020). · Gainsight(헬스스코어·QBR — 벤더 방법론).
