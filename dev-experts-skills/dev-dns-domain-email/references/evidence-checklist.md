# evidence + 출고 전 체크리스트

## 실증·출처

- **Gmail/Yahoo 발신자 요구사항 (2024)** — 대량 발신자(=Gmail 수신자에게 하루 5,000통 이상) SPF·DKIM·DMARC 의무화. **2024-02-01 발효**, 추가로 스팸률 <0.30% 유지 + 원클릭 구독취소(RFC 8058) 요구. 공식: support.google.com/a/answer/81126 (Google "Email sender guidelines"). SKILL.md 실전 케이스, 이메일 인증이 전제조건이 된 근거. 확인일 2026-06.
- **RFC 7208(SPF)·6376(DKIM)·7489(DMARC)** — 이메일 인증 표준의 1차 출처(datatracker.ietf.org/doc/html/rfc7208 등). SPF는 **DNS 조회 10회 한도(§4.6.4)** + 별도로 **void(NXDOMAIN/빈응답) 조회 2회 한도** — 초과 시 PermError(DMARC는 이를 SPF fail로 간주). DKIM TXT는 `selector._domainkey.<도메인>`에 `v=DKIM1; k=rsa; p=<base64 공개키>`(RFC 6376 §3.6.1).
- **RFC 8058(원클릭 구독취소)** — 대량 발신 시 `List-Unsubscribe` + `List-Unsubscribe-Post: List-Unsubscribe=One-Click` 헤더, DKIM 서명 포함 필수. 2024 Gmail/Yahoo 요구사항의 일부. 발송 시스템 측 구현은 dev-notification, 여기서는 인증·요구사항 출처로만.
- **RFC 1034/1035(DNS)·루트 CNAME 금지** — CNAME이 다른 레코드와 공존 불가 규정(D4a 근거).
- **도메인 만료 서비스 다운 사례** — 여러 기업의 갱신 누락 장애(공개 보도 다수). auto-renew·경보의 근거.
- 오픈소스 차용 표기: DNS·이메일 가이드 다수(색인 인지, 본문 비복사). **역흡수**: TTL 선하향 전환 절차·DMARC 단계적 도입·루트 CNAME/MX IP 검출·CGNAT 연계·만료를 "예고된 장애"로 자동화 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (DNS·이메일 설정 시)

- [ ] 루트 CNAME 없음, MX는 호스트명 (`dns_check.py` 0건)
- [ ] 변경 시 TTL 선하향 → 변경 → 다중 리졸버 확인
- [ ] (메일) SPF + DKIM + DMARC 3종
- [ ] DMARC p=none부터 (rua 리포트 수집 후 단계적)
- [ ] SPF include 10조회 한도 내 + void 조회 2회 이하 (둘 다 초과 시 PermError)
- [ ] 도메인 auto-renew + 인증서 자동 + 만료 30일 경보
- [ ] (홈) DDNS 설정 + CGNAT 여부 확인
- [ ] mail-tester류로 이메일 인증 점수 확인
- [ ] CAA 레코드(선택, 보안)

## 점검 주기 (느림 — 연 1회, 단 만료는 상시 경보)

- 도메인·인증서 만료 임박 점검(자동 경보가 1차)
- DMARC 리포트 리뷰(미인증 발송원·스푸핑 시도) → 정책 단계 상향 검토
- 메일 수신자 요구사항 변화 확인(Gmail/Yahoo 정책 갱신)
