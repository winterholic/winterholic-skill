# biz-crm-lifecycle — 시퀀스 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 웹 검증(라이프사이클·deliverability·RFM·동의 항목 2026-07-01 추가). 1단계 참조. 실전 운용집은 `playbook.md`.

## 1. 라이프사이클 단계 × 메시지
신규(활성화)·활성화→습관·리텐션·확장·위기(이탈신호)·윈백. 행동 트리거 기반(일괄 아님). 라이프사이클 마케팅은 실무 기원(Infusionsoft/Keap 대중화). https://www.smartinsights.com/ecommerce/web-personalisation/what-is-lifecycle-marketing/

### 1-1. 단계별 시그니처 시퀀스 (실무 컨센서스 — 아래 타이밍은 출발점, 제품·업종별 조정)
- **웰컴/온보딩**: 가입 직후 즉시 첫 통 발송, 이후 **3~5통을 7~14일**에 걸쳐. 신규 사용자는 **첫 3~7일에 이탈 위험이 가장 큼** → time-to-value 단축이 핵심. 각 통의 목적은 "다음 한 행동" 유도(전체 기능 소개 아님). https://userpilot.com/blog/onboarding-email-sequence/
- **활성화(aha moment)**: 온보딩의 목표는 "제품이 내 문제를 푼다"를 깨닫는 첫 순간(aha)으로 데려가는 것. **가치를 증명하는 단일 핵심 행동 하나**를 정해 모두를 그리로 먼저 보낸다. https://customer.io/learn/lifecycle-marketing/essential-lifecycle-marketing-campaigns
- **리텐션(이탈 위험, at-risk)**: 사용 감소·미접속 신호에 선제 개입. 실무 예: **미접속 14일 → "we miss you" 발송 → 3일 대기 → 여전히 비활성이면 도움·미사용 기능 하이라이트 → 1주 더 뒤 CS 개인 아웃리치**(임계는 제품 사용주기에 맞춰 조정). https://customer.io/learn/lifecycle-marketing/essential-lifecycle-marketing-campaigns
- **확장(업셀/크로스셀)**: 활성·만족 세그먼트에만. 신뢰가 쌓인 뒤 관련 상위 플랜·보완 상품 제안(가치 먼저).
- **윈백(lapsed)**: 장기 미구매·휴면 고객 대상. 재활성화 캠페인 후 무반응이면 sunset(아래 §5).
- **멀티채널**: 이메일 무시 시 인앱 배너·푸시가 실제 사용 순간에 포착 — 채널 병행이 단일 채널보다 강함.

## 2. Deliverability 표준 (RFC — 검증)
- **SPF: RFC 7208(2014)** https://datatracker.ietf.org/doc/html/rfc7208
- **DKIM: RFC 6376(2011)** https://datatracker.ietf.org/doc/html/rfc6376
- **DMARC: RFC 7489(2015)** https://datatracker.ietf.org/doc/html/rfc7489 — SPF/DKIM **+ 정렬(alignment)** 필요(SPF만 통과·정렬 실패면 DMARC 실패).
- **Google 대량 발신자 요건(2024-02-01 시행, Gmail에 5,000+/일)**: SPF+DKIM, DMARC p=none 최소, 정렬, 스팸률 <0.30%(목표 <0.10%), 원클릭 수신거부, FCrDNS, TLS. https://support.google.com/a/answer/81126 (Yahoo 동시 시행). 임계는 수신 도메인당·일 기준.
- **Microsoft(Outlook.com) 대량 발신자 요건**: 2025-05-05 시행, 하루 5,000+ 발신 시 SPF+DKIM+DMARC 필수. Google/Yahoo와 정합. https://techcommunity.microsoft.com/blog/exchange/keeping-our-outlook-com-users-safe-updated-sender-requirements/4399730 ("확인 필요" — 시행일·임계는 MS 공지 기준, 세부는 변동 가능)
- **BIMI/VMC(로고 표시)**: BIMI는 인증이 아닌 **브랜드 로고 표시** 규격 — 전제로 **DMARC 시행 수준(p=quarantine 또는 p=reject, pct=100)** 필요. `p=none`으로는 불가. Gmail·Apple 등은 로고 표시에 **VMC(Verified Mark Certificate, 등록상표 기반) 또는 CMC(Common Mark Certificate, 2024~ 비상표 대안)** 를 요구. deliverability를 직접 높이진 않으나 신뢰·인지도·간접 참여 상승 효과. https://bimigroup.org/faqs-for-senders-esps/ · https://knowledge.workspace.google.com/admin/security/set-up-bimi

### 2-1. 워밍업(warmup) — 새 도메인/IP 평판 확립
- 최대 deliverability까지 **4~8주** 소요(목표 볼륨·참여도에 따라). 원리: **적게 시작 → 일/주당 대략 50~100%씩 증량 → 지표 건강할 때만 가속**. https://www.mailgun.com/blog/deliverability/domain-warmup-reputation-stretch-before-you-send/
- 현대 워밍업은 **볼륨 일변도 → 참여 기반(engagement-based)**으로 이동: open·click·reply 같은 실제 참여 신호를 만들어 "봇이 아닌 사람 발신자"임을 Gmail/Microsoft에 증명. https://www.allegrow.co/knowledge-base/how-to-warm-up-email-domain
- 워밍업 중엔 **가장 참여도 높은 세그먼트부터**: 최근 7~14일 오픈자 > 그중에서도 **최근 클릭자**(클릭은 봇으로 위조 어려워 진짜 의도 신호). https://inboxstack.com/blog/email-warmup-guide-2026
- 중단 임계(참고): 어느 단계든 **불만율(complaint) >0.10% 또는 바운스율 >2%면 증량 멈추고 원인 조사**. https://inboxstack.com/blog/email-warmup-guide-2026 ("확인 필요" — 벤더 가이드 값, Gmail 공식 <0.30%와 별개의 보수적 운영 임계)

## 3. Apple MPP (오픈율 무력화)
WWDC 2021-06-07 발표, iOS 15(2021-09-20) 적용. 콘텐츠(추적 픽셀 포함) 선반입 → 실제 열람과 무관히 "오픈" 기록 → **오픈율 신뢰 불가**. https://www.litmus.com/blog/apple-mail-privacy-protection-for-marketers
- **오픈율 인플레이션**: MPP는 배달 시점에 이미지·픽셀을 선반입 → iOS 청중 비중 큰 발신자는 오픈율이 **15~35% 부풀려짐**. 이 "머신 오픈"은 실제 열람과 무관. https://datainnovation.io/en/apple-mpp-email-open-rate-fix/
- **CTOR도 오염됨**: CTOR(클릭÷오픈)은 분모(오픈)가 부풀려지면 인위적으로 하락 → CTOR도 MPP 이후 단독 신뢰 불가. https://www.beehiiv.com/blog/apple-mpp-open-rate
- **MPP가 건드리지 않는 신뢰 지표**: **배달률·바운스·클릭·전환·회신(reply)·수신거부**는 여전히 유효(사람의 의도적 행동 필요). 대체 측정 전략: ① 클릭률(CTR)을 주 참여 지표로 ② 비-Apple 세그먼트(Gmail/Outlook 등)에서만 오픈·CTOR 계산 ③ B2B/관계형은 회신율 ④ 최종 KPI는 전환. 세그먼트/sunset 판정에도 "오픈 유무" 대신 클릭·사이트 방문·구매 등 서버측 확인 가능 행동을 쓴다. https://documentation.bloomreach.com/engagement/docs/working-with-apple-mail-privacy-protection

### 3-1. 행동 트리거 시퀀스 타이밍 (실무 컨센서스 — 출발점, 조정 필수)
- **장바구니 이탈(abandoned cart)**: 보통 2~3통 — 1통 **이탈 후 1시간 내**(신선한 관심 포착) → 2통 **12~24시간 후**(제품 정보·사회적 증거) → 3통 **24~48시간 후**(한정 할인 등 강한 인센티브). 발송 시간대는 오전 6시~오후 9시, 오후 8시경 참여 피크(주장). https://www.klaviyo.com/blog/abandoned-cart-email · https://attribuly.com/blogs/abandoned-cart-timing-cohort-benchmarks-templates/
- **윈백**: 2~4통, **저압(리마인더) → 무반응 시 가치·인센티브로 상승**. 기존 고객 재획득 확률 20~40% 주장(WinBack Labs 인용 — "확인 필요"). https://www.omnisend.com/blog/win-back-email/
- ⚠️ 위 타이밍·전환율 수치는 전부 **마케팅 벤더 벤치마크** — 절대 기준 아님, 자사 데이터로 A/B 검증하며 조정.

## 4. 세그멘테이션 — RFM (검증)
RFM = **Recency(최근성: 마지막 거래 후 경과, 보통 일 단위)·Frequency(빈도: 기간 내 총 거래 수)·Monetary(금액: 기간 내 총 지출)**. 데이터베이스/다이렉트 마케팅 기원. 각 축을 보통 1~5로 점수화(예 555=최상). https://www.optimove.com/resources/learning-center/rfm-segmentation
- **대표 세그먼트(실무 라벨)**: Champions(최근·자주·최다 지출, 예 555) / Loyal(정기 구매) / Potential Loyalist(최근·평균 빈도) / At Risk(과거 우수했으나 recency 하락 → 윈백) / Can't Lose Them(과거 고빈도였으나 오래 이탈) / Hibernating(소액·오래 미방문 → 라스트찬스 재활성화). 세그먼트별 액션은 `playbook.md` §5. https://clevertap.com/blog/rfm-analysis/
- RFM은 **미래 CLV·이탈 예측 지표**로도 유효. 행동 기반 세그먼트(이벤트·기능사용)와 병용.

## 5. 동의(consent)·리스트 위생·Sunset (검증)
- **Single opt-in**: 폼 제출 즉시 리스트 편입(1단계, 빠른 성장·마찰↓). **Double opt-in**: 확인 이메일 링크 클릭까지 요구(2단계) — 스팸 가입↓, 유효·진성 구독자만 남아 리스트 품질↑. https://mailchimp.com/help/single-opt-in-vs-double-opt-in/
- **Suppression list**: 수신거부·하드바운스·불만 신고자를 영구 제외 목록으로 관리(재발송 금지). 동의 철회·수신거부는 즉시 반영(정보통신망법 §50⑥과 정합).
- **Sunset policy**(비활성 자동 정리 규칙): 표준 구현 예 — **90일 무참여(오픈·클릭 없음)에 sunset 시작 → 재참여 캠페인 → 14~30일 내 무반응 시 전체 발송에서 suppress → 총 180일 무활동 시 리스트에서 완전 제거**. 실행 주기: 고빈도 발신자 분기별, 월간 발신자 반기별 감사. https://mailflowauthority.com/list-hygiene/sunset-policies-guide (⚠️ MPP로 오픈이 부정확하므로 sunset 판정은 **클릭·행동 우선**, 오픈 단독 사용 금지)

## 6. 한국 정보통신망법 제50조 (검증)
제50조①영리 광고성 정보=명시적 사전 동의(옵트인). **제50조③ 21시~익일 08시** 전송 별도 동의(전자우편 예외) — 조문번호·시간대 확정(2026-06-30). 제50조④ 전송 시 명칭·연락처+수신거부 방법 등 표기. 수신거부·동의철회 시 전송 금지(제50조⑥). https://www.law.go.kr/법령/정보통신망이용촉진및정보보호등에관한법률/제50조

### 6-1. 표기·야간·수신거부 구체 방식 (KISA 안내서·시행령 — 검증)
KISA "불법스팸 방지를 위한 정보통신망법 안내서"(정보통신망법 2024-01-23 개정 반영, 제6차 개정판)와 시행령 기준:
- **"(광고)" 표기**: 광고성 정보가 **시작되는 부분**에 "(광고)" + 전송자 명칭. 이메일은 **제목이 시작되는 부분**에 "(광고)"를 표시. 본문에 전송자 명칭·연락처(전화·주소, 회신 가능 시 이메일 생략 가능). https://developers.fingerpush.com/assemble/guide/ads · https://www.kisa.or.kr/402/form?postSeq=2382
- **끝부분 수신거부**: 광고성 정보가 **끝나는 부분**에 "곧바로 수신거부/동의철회를 간단히" 할 수 있는 방식([수신거부] 링크 등)을 명시(원클릭 지향).
- **야간 전송(21~08시)**: 별도 사전동의 필요하나 **전자우편은 예외**(수신확인 즉시성이 낮다는 취지). 문자·앱푸시는 야간 별도동의 필요.
- **"무료" 표시**: 시행령 제62조(별표6)에 따라 수신거부에 **비용이 들지 않음("무료")을 함께 안내**. 단 이 무료 표기 의무는 문자/앱푸시 등이 주 대상이며 **전자우편은 예외**로 보는 것이 실무 해석(전자우편 수신거부는 원래 무료). https://developers.fingerpush.com/assemble/guide/ads
- **처리·확인 의무(시행령)**: 제62조의2 — 수신동의·거부·철회 처리 결과를 **14일 이내 통지**. 제62조의3 — 수신동의 여부를 **2년마다 정기 확인**. https://developers.fingerpush.com/assemble/guide/ads
- ⚠️ 시행령 조문번호(제62조·별표6·62조의2·62조의3)와 "무료 표기 전자우편 예외" 해석은 KISA 안내서·ESP(Stibee 등) 실무 해석 기반 — 실제 캠페인 집행 전 **최신 KISA 안내서 원문·법무 확인 필요**(개정 잦음).

## 7. 교정
**오픈율 ≠ 참여**(MPP 후 클릭·전환으로 전환). DMARC=SPF/DKIM+정렬. 5,000/일은 수신 도메인당·일(월 아님). **워밍업·sunset·warmup 중단 임계의 구체 수치는 벤더 가이드**(ISP 공식과 별개) — 운영 출발점으로만 쓰고 "확인 필요". RFM 세그먼트 라벨(Champions·At Risk 등)은 **업계 통용 명칭이며 도구마다 경계 정의가 다름** — 절대 기준 아님.

## 8. 출처
- RFC 7208/6376/7489. · Google/Yahoo 발신자 요건(2024) · Microsoft(2025). · Apple MPP(2021). · 정보통신망법 제50조 + KISA 안내서(제6차) + 시행령 제62조/62조의2/62조의3.
- 라이프사이클 시퀀스: Customer.io · Userpilot. · 트리거 타이밍: Klaviyo · Omnisend · Attribuly. · 워밍업/engagement: Mailgun · Allegrow · InboxStack. · RFM: Optimove · CleverTap · Braze. · 동의/sunset: Mailchimp · Mailflow Authority. · MPP 대체지표: Bloomreach · beehiiv · DataInnovation. · BIMI: BIMI Group · Google Workspace.
