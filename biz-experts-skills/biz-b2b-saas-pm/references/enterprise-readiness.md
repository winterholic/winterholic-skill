# enterprise-readiness — 엔터프라이즈 게이트·구매자≠사용자·SaaS 지표 실무판

> B2B SaaS PM이 엔터프라이즈 딜을 막지 않게 준비하는 실무 체크리스트. evidence.md의 검증 사실(Snowflake NRR 158%·Datadog 146%/141%/151%·SAML/OIDC/SCIM/RBAC 표준·SOC 2=attestation) 위에 "그래서 무엇을 언제 만드나"를 얹는다. 수치는 회사별("확인 필요").

---

## 1. 구매자 ≠ 사용자 — 이해관계자 4역할

*Lean B2B*(Garbugli)는 B2B에서 최소 4역할을 분리한다. 한 사람으로 뭉치면 잘못된 결정이 난다.

| 역할 | 관심사 | 제품이 줘야 할 것 | 무시하면 |
|---|---|---|---|
| **Economic Buyer(구매자·예산 결정)** | ROI·리스크·보안·규정 | 가치 증명(대시보드·리포트), 보안 문서, 관리 통제 | 계약 안 됨 |
| **End User(실사용자)** | 일상 사용성·속도 | 낮은 마찰·도입 용이·핵심 워크플로 | 도입 실패→갱신 실패 |
| **Admin(관리자)** | 권한·프로비저닝·통합 운영 | 관리 콘솔·SSO·SCIM·감사로그 | 배포·운영 막힘 |
| **Champion(내부 추진자)** | 자기 성공·조직 설득 | 성공 스토리·확산 도구·ROI 근거 | 내부 확산 정체 |

> 핵심: **구매자가 사도 사용자가 안 쓰면 도입 실패 → 다음 갱신에 해지.** 반대로 사용자가 좋아해도 구매자 ROI/보안 증명 없으면 확산·구매가 막힌다. NRR은 이 둘을 다 설계해야 산다.

---

## 2. 엔터프라이즈 준비도(Enterprise Readiness) 게이트

엔터프라이즈 딜을 자주 막는 "숨은 본체". 화려한 사용자 기능보다 이게 없어서 딜이 죽는다.

### 2-1. 인증·프로비저닝 (표준, 검증)
| 항목 | 표준 | 역할 | 혼동 주의 |
|---|---|---|---|
| **SSO / 페더레이션** | **SAML 2.0**(OASIS, 2005), **OIDC Core 1.0**(2014) | 조직 IdP로 로그인 | 둘 다 **인증** |
| **자동 프로비저닝** | **SCIM 2.0**(RFC 7643/7644, 2015) | 사용자 생성·비활성 자동화(입·퇴사 반영) | SSO의 **대체가 아니라 상보재** |
| **권한 모델** | **RBAC**(NIST, ANSI/INCITS 359) | 역할 기반 접근제어 | ABAC(속성기반)와 구분 |
| **감사로그(Audit Log)** | (표준 없음, 실무 필수) | 누가 언제 무엇을 — 규제·포렌식 | SIEM 연동 요구 흔함 |

> SSO만 있고 SCIM 없으면 대기업은 수백 계정을 수동 관리해야 해 딜이 막힌다. SSO+SCIM은 세트로 본다.

### 2-2. 컴플라이언스·조달 (검증)
- **SOC 2**: SaaS 보안의 사실상 표준. **Type I(설계, 시점)**보다 **Type II(6~12개월 운영효과성)**를 엔터프라이즈가 요구. **attestation**(AICPA, SSAE 18)이지 certification 아님. TSC 5범주 중 **Security 필수**.
- **ISO 27001**: 국제 정보보안 **인증**(certification). 글로벌·유럽 딜에 유리.
- **개인정보 규제**: GDPR(EU)·CCPA(캘리포니아)·(국내) 개인정보보호법 — DPA(데이터처리계약)·SCC 요구. 상세 → dev-privacy-compliance.
- **벤더 보안 설문(SIG 등)**: 조달 단계에서 보안·리스크·구매·컴플라이언스가 합동 실사. SOC 2 Type II 보고서가 이 과정을 크게 단축.

### 2-3. 관리·통제 기능 (Admin이 요구)
- 조직/워크스페이스 계층, 역할·권한 세분화, 도메인 캡처, 세션·비밀번호 정책, 데이터 잔류·삭제·익스포트, IP 허용목록, 사용량·좌석 관리 대시보드.

### 2-4. 배포·통합
- API·웹훅, 주요 툴 통합(Slack·Salesforce 등), 데이터 인/아웃, 온프레·VPC 옵션(고규제 산업).

> **PM 판단**: 위 항목은 "언젠가"가 아니라 **타깃 딜 규모에 맞춰** 단계적으로. 첫 6자리 딜 앞에서 SSO/SOC 2가 없으면 그게 로드맵 1순위다. deal-breaker 패턴을 수집해 우선순위화(안티패턴 6).

---

## 3. SaaS 지표 — 제품 결정과 연결

### 3-1. 리텐션 지표 (혼동 금지)
- **GRR(Gross Revenue Retention)**: 확장 **제외**, 이탈·다운그레이드만 반영. **≤100%**. 제품 끈끈함의 순수 지표.
- **NRR(Net Revenue Retention)**: 확장(업셀·시트↑) **포함**. **>100% 가능**. 확장이 이탈을 상쇄·초과하면 100% 넘음.
- **함정**: 높은 NRR이 **로고 이탈(logo churn)**을 가릴 수 있다(소수 대형 고객 확장이 다수 이탈 은폐). **GRR·NRR·로고 이탈을 함께** 본다.
- 검증 벤치마크(IPO 시점 최상위, 베끼기 금지): **Snowflake 158%**(S-1, 소비량 기반), **Datadog 146%/141%/151%**(S-1). (evidence §4)

### 3-2. 단위경제
- **LTV:CAC ≥ 3:1**(Skok 통념, 절대 법칙 아님) · **CAC 회수기간** · **Rule of 40**(성장률+수익률 ≥40%, 스케일 단계) — Brad Feld 대중화.
> 정밀 단위경제 계산·모델링은 → biz-finance-fpa. 이 스킬은 지표를 **제품 결정에 연결**(어느 기능이 NRR·도입을 움직이나)하는 축.

### 3-3. 도입(Adoption) 지표 — PM의 성공 판정
- **활성 좌석(active seats)/구매 좌석** 비율, 핵심 기능 도입률, 조직 내 확산(계정당 활성 사용자 수 = PQA 신호).
- B2B는 좌석 단위 갱신·확장이 매출 → **도입 안 되면 좌석 축소·이탈**. 도입을 CS 몫으로 떠넘기지 말고 제품 지표로(안티패턴 5).

---

## 4. 엔터프라이즈 요구 관리 — 커스텀 폭주 막기

큰 고객의 "이거 없으면 계약 안 함"을 다루는 절차:
1. **문제로 추상화** — 요청(솔루션)이 아니라 **왜 필요한가**(문제)를 캔다. "이 버튼"이 아니라 "감사 요건 충족".
2. **일반화 가능성 판정** — 다른 고객·세그먼트에도 해당하나? → 해당하면 제품화, 1회성이면 설정 옵션·통합·프로페셔널서비스로 격리.
3. **deal-breaker vs nice-to-have 구분** — 진짜 계약 차단인가, 협상 카드인가(영업과 검증).
4. **로드맵 균형** — deal-breaker 패턴 + 장기 비전. 영업 요구만 좇으면 비전 없는 기능 공장, 무시하면 매출 상실(안티패턴 6).
5. **커스텀 부채 관리** — 수용한 1회성은 별도 트랙·기술부채로 추적(누더기화 방지).

---

## 5. B2B PM 딜 리뷰 체크리스트 (신규 딜/기능 판단 시)
- [ ] 요구 출처가 구매자/사용자/관리자/챔피언 중 누구인가, 몇 개 계정인가
- [ ] 일반화 가능한 문제인가 1회성 커스텀인가
- [ ] 엔터프라이즈 게이트(SSO·SCIM·SOC 2·감사) 중 막히는 게 있나
- [ ] 도입 설계(온보딩·관리자 설정)가 있나 — 사용자가 실제 쓸까
- [ ] NRR·GRR·로고이탈·활성좌석에 어떻게 영향
- [ ] deal-breaker인가 vs 비전 훼손인가

---

## 출처
- Garbugli, *Lean B2B*. https://leanb2bbook.com/
- Skok, SaaS Metrics 2.0. https://www.forentrepreneurs.com/saas-metrics-2/
- 표준: SAML https://www.oasis-open.org/standard/saml/ · OIDC https://openid.net/specs/openid-connect-core-1_0.html · SCIM https://datatracker.ietf.org/doc/html/rfc7643 · RBAC https://csrc.nist.gov/projects/role-based-access-control
- SOC 2 Type I/II·TSC: https://secureframe.com/blog/soc-2-type-ii · https://www.schellman.com/blog/soc-examinations/soc-2-trust-services-criteria-with-tsc
- NRR vs GRR: https://stripe.com/resources/more/net-revenue-retention-vs-gross-revenue-retention
- 벤치마크 S-1(수동열람): Snowflake https://www.sec.gov/Archives/edgar/data/1640147/000162828020013010/snowflakes-1.htm · Datadog https://www.sec.gov/Archives/edgar/data/1561550/000119312519227783/d745413ds1.htm
