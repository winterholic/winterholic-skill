# evidence + 출고 전 체크리스트

## 실증·출처

- **Stevens, *TCP/IP Illustrated* Vol.1** — TCP·핸드셰이크·계층 모델의 표준 교과서.
- **TLS 인증서 만료 광역 장애** — 통신사·SaaS의 반복 사례(공개 보도 다수). SKILL.md 실전 케이스. 자동 갱신·만료 경보의 근거.
- **Let's Encrypt 문서 + certbot** — 자동 갱신 표준. 현재 인증서 유효기간 90일(권장 갱신: 60일째). 2026 동향: 6일짜리 short-lived 인증서 GA(2026-01), 45일 프로파일 opt-in 예정(2026-05-13), 이후 기본 프로파일도 단계적으로 단축 예정(구체 일정·일수 확인 필요). certbot 4.1.0+는 ARI(ACME Renewal Information)로 만료기간을 자동 추종 — 갱신 주기를 하드코딩하면 깨진다. 1차 출처: https://letsencrypt.org/docs/faq/ , https://letsencrypt.org/2025/12/02/from-90-to-45 (응답 확인). [신뢰: Let's Encrypt 공식 블로그·FAQ]
- **HTTP/2 = RFC 9113, HTTP/3 = RFC 9114, QUIC = RFC 9000(전송)·9001(TLS)·9002(손실복구)** — 멀티플렉싱·HoL 해결의 1차 출처. rfc-editor.org에서 번호·매핑 확인. [신뢰: IETF RFC Editor 1차]
- **TLS 1.3 = 1-RTT(0-RTT 재개 가능), TLS 1.2 = 2-RTT 핸드셰이크** — RFC 8446(TLS 1.3). 연결 재사용의 정량 근거. [신뢰: IETF RFC 1차]
- **WireGuard 문서** — 경량 VPN의 표준(홈 외부 접근 권장 방식). https://www.wireguard.com (확인 필요: 본 감사에서 미재확인).
- 오픈소스 차용 표기: 네트워크 가이드 다수(색인 인지, 본문 비복사). **역흡수**: 계층 배제 진단 절차·CGNAT 함정·VPN 우선 원칙·verify=False 검출 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (네트워크 설정·연결 코드)

- [ ] 외부 호출 전부 타임아웃(connect/read) — `net_check.py` 0건
- [ ] TLS 검증 유지(verify=False 0) + https
- [ ] 인증서 자동 갱신 + 만료 30일 경보
- [ ] 홈 외부 접근은 VPN 우선, 노출은 443 프록시 1개 + 인증
- [ ] DB·SSH·관리 포트 인터넷 직접 노출 0
- [ ] 연결 풀·keepalive 사용
- [ ] DNS 변경 시 TTL 사전 하향
- [ ] 연결 문제는 계층 배제 진단으로(추측 재부팅 0)
- [ ] (홈) CGNAT 여부 확인 / UPnP 자동 개방 off

## 점검 주기 (부패 느림 — 연 1회)

- 인증서 자동 갱신 동작 확인 + 열린 포트 재점검(불필요 노출 색출)
- ledger의 연결 삽질 3회 패턴 → 진단표 보강
