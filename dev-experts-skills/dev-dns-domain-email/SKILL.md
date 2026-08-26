---
name: dev-dns-domain-email
description: "DNS·도메인·이메일 인증 작업 시 사용. DNS 레코드(A·AAAA·CNAME·MX·TXT), 전파·TTL, 이메일 인증(SPF·DKIM·DMARC), 도메인 운영, 서브도메인·DDNS, 발신 도메인 평판을 다룬다. 사용자가 'DNS', 'A 레코드', 'CNAME', 'MX', 'SPF', 'DKIM', 'DMARC', '도메인', '이메일 인증', '메일 안 감', '스팸함', 'TXT 레코드', 'DDNS', '네임서버'를 언급하면 트리거. 네트워크 연결·DNS 해석 흐름(→ dev-networking), 메일 발송 시스템·큐(→ dev-notification), 리버스 프록시·TLS(→ dev-nginx), 개인정보(→ dev-privacy-compliance)에는 사용하지 않는다."
---

# dev-dns-domain-email — DNS·도메인·이메일 인증 전문가

> 기준: DNS 표준 + SPF/DKIM/DMARC (2026-06) · 부패 느림(연 1회), 단 만료·인증은 상시 주의

## 정체성

DNS·이메일 인증 실무 전통. **"DNS는 전화번호부고 이메일 인증은 발신자 신원증명이다 — 둘 다 '설정하고 잊으면' 어느 날 조용히 깨진다(전파 지연·만료·평판 추락). 그리고 둘 다 캐시·전파 때문에 '바꿨는데 안 바뀜'이 정상이다"**.

핵심 신조: TTL을 알고 변경(전파 지연 존재) · 이메일은 SPF+DKIM+DMARC 3종 세트 · 도메인·인증서 만료는 달력 사건(자동·경보) · DMARC는 모니터링부터(p=none).

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| DNS 레코드·전파·이메일 인증 | DNS 해석 흐름·연결 진단 (→ dev-networking) |
| SPF/DKIM/DMARC 설계 | 메일 발송 큐·도달률 (→ dev-notification) |
| 도메인 운영·DDNS·서브도메인 | TLS·프록시 (→ dev-nginx) |
| 발신 도메인 평판 | 수신 동의·개인정보 (→ dev-privacy-compliance) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. TTL 무시하고 즉시 반영 기대
❌ A 레코드 IP 바꾸고 "왜 옛 서버로 가지" — TTL만큼 캐시됨
✅ 변경 전 TTL을 낮춰두기(예 3600→300, 옛 TTL만큼 기다린 후 변경) → 변경 → 확인 후 TTL 복원. 전파 확인은 여러 리졸버로(`dig @8.8.8.8`, `@1.1.1.1`)
**왜**: DNS는 전 세계 리졸버에 TTL만큼 캐시된다(dev-networking #6) — TTL 3600이면 최대 1시간 옛 값이 산다. "마이그레이션 했는데 절반은 옛 서버"의 정체. 사전 TTL 하향이 전환 시점을 통제하는 유일한 방법.

### 2. 이메일 인증 없이 발송 (스팸함 직행)
❌ SPF/DKIM/DMARC 없이 자체 도메인으로 메일 발송 — 스팸 분류·차단
✅ 3종 세트: SPF(허용 발신 서버 IP) + DKIM(서명으로 위변조 방지) + DMARC(둘 실패 시 정책 + 리포트). 발송 전 필수 설정
**왜**: 현대 메일 수신 서버(Gmail·Outlook)는 인증 없는 메일을 스팸·차단한다(2024 Gmail/Yahoo 발신자 요구사항 강화). SPF만으로 부족 — 전달(forwarding) 시 깨진다. 3종이 세트로 작동해야 "신뢰된 발신자". 인증 없는 도메인은 스푸핑에도 악용된다.

### 3. 도메인·인증서 만료 방치
❌ 도메인 갱신·인증서 갱신을 수동·기억에 의존 — 어느 날 도메인 만료로 전체 서비스 다운
✅ 자동 갱신(도메인 auto-renew + Let's Encrypt — dev-networking) + 만료 경보(도메인 30일·인증서 30일 전 — dev-monitoring). 등록 정보·결제수단 최신 유지
**왜**: 도메인 만료는 가장 비싼 "예고된 장애" — 만료되면 전체 서비스 접근 불가 + 도메인 탈취(드롭캐칭) 위험까지. 인증서 만료(dev-networking 실전 케이스)와 한 부류 — 달력에 적힌 장애는 자동화+경보로 막는다.

### 4. CNAME·MX 오용
❌ 루트 도메인에 CNAME(`example.com CNAME ...` — RFC 위반, MX·기타 레코드와 충돌) / MX를 IP로 지정 / CNAME 체인 과다
✅ 루트는 A/AAAA(또는 ALIAS/ANAME — 제공자 기능), CNAME은 서브도메인만. MX는 **호스트명**을 가리키고 그 호스트가 A 레코드. CNAME 대상도 A로 끝나야
**왜**: 루트 CNAME은 표준 위반이라 MX(메일)·NS와 공존 불가 — 메일이 죽는다. MX에 IP 직접 지정도 무효(호스트명만). CNAME 체인이 길면 해석 지연·실패. 레코드 타입의 규칙을 모르면 "메일만 안 오는" 미스터리.

### 5. DMARC를 강제부터 (p=reject 바로)
❌ DMARC 첫 설정에 `p=reject` — 정당한 메일(서드파티 발송·전달)이 거부되어 누락
✅ 단계적: `p=none`(모니터링만, 리포트 수집) → 정당 발송원 전부 SPF/DKIM 정렬 확인 → `p=quarantine` → `p=reject`. rua= 리포트 주소로 누가 내 도메인으로 보내는지 파악
**왜**: DMARC는 강력해서 위험하다 — 바로 reject면 미처 인증 안 한 정당 발송(뉴스레터 서비스·CRM·전달)이 전부 차단되어 메일 누락. p=none으로 현황 파악(리포트) 후 조이는 게 표준. dev-monitoring·dev-cicd의 "report-only부터" 정신.

### 6. DDNS·동적 IP 무관리 (홈서버)
❌ 변동 공인 IP에 고정 A 레코드 — IP 바뀌면 도메인이 옛 IP 가리킴
✅ DDNS: 공인 IP 변경 시 A 레코드 자동 갱신(공유기 내장 또는 스크립트 + DNS API). CGNAT면 DDNS도 무력(dev-networking) → 터널 대안
**왜**: 가정용 인터넷은 공인 IP가 주기적으로 바뀐다 — 고정 레코드는 어느 날 옛 IP를 가리켜 접속 불가. DDNS가 IP 변경을 추적. 단 ISP가 CGNAT면 공인 IP 자체가 없어 DDNS 무의미(Cloudflare Tunnel 등 필요).

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| TTL | 평상시 3600, 변경 전 300으로 하향 | 안티패턴 1 |
| 이메일 | SPF+DKIM+DMARC 3종 필수 | 안티패턴 2 |
| DMARC 도입 | p=none → quarantine → reject 단계적 | 안티패턴 5 |
| 만료 경보 | 도메인·인증서 30일 전 + auto-renew | 안티패턴 3 |
| 루트 도메인 | A/AAAA 또는 ALIAS (CNAME 금지) | 안티패턴 4 |
| 전파 확인 | 다중 리졸버(dig @8.8.8.8 @1.1.1.1) | 안티패턴 1 |

## 워크플로우 (DNS·이메일 설정)

1. **레코드 설계** — 필요한 레코드(A/AAAA/CNAME/MX/TXT) + 루트는 A 규칙. 변경이면 TTL 사전 하향.
2. **(이메일) 3종 세트** — SPF(발신 IP/서비스) + DKIM(서명 키) + DMARC(p=none 시작 + rua 리포트).
3. **만료·자동화** — 도메인 auto-renew + 인증서 자동 갱신 + 만료 경보.
4. **(홈서버) DDNS** — 동적 IP면 자동 갱신, CGNAT 여부 확인.
5. **검증 (피드백 루프)**:
   ```
   python scripts/dns_check.py <zone 파일 또는 레코드 목록>   # 루트 CNAME·MX IP·SPF/DKIM/DMARC 누락·DMARC reject 즉시 검출, exit 0이 통과
   # 실제 확인: dig로 전파·각 레코드 / mail-tester류로 이메일 인증 점수
   ```

## 출력 템플릿

```
## [도메인] DNS·이메일 설정
### 레코드: <타입별 + TTL + 루트 규칙 준수>
### 이메일: <SPF / DKIM / DMARC 정책 단계>
### 만료·자동화: <도메인 renew·인증서·경보>
### (홈) DDNS: <동적 IP 처리 / CGNAT 여부>
### 검증: $ dns_check → <1줄> / dig·mail-tester 확인
### 확인 필요
```

### 작성 예시

```
## example-domain.com DNS·이메일 (사용자 도메인)
### 레코드: 루트 A → 홈서버/호스팅 IP / www CNAME → 루트 / MX → 메일 호스트(A 보유)
  / 서비스 서브도메인 CNAME / TTL 3600(변경 시 300 선하향)
### 이메일: SPF(메일 발송 서비스 IP) + DKIM(발송 서비스 서명 키 등록) + DMARC p=none 시작
  (rua=dmarc@example-domain.com로 리포트 수집 → 정당 발송원 정렬 확인 후 quarantine)
### 만료·자동화: 도메인 auto-renew on + Let's Encrypt 자동 + 만료 30일 경보(monitoring-discord-bot)
### (홈) DDNS: 홈서버 노출 서브도메인은 DDNS — 단 CGNAT 확인 필요(아니면 Cloudflare Tunnel)
### 검증: $ dns_check zone.txt → 0건 / dig MX 확인 / mail-tester 10/10 목표
### 확인 필요: 메일 발송 주체(자체 서버 vs SendGrid류) — 그에 따라 SPF/DKIM 값 결정(dev-notification)
```

❌ "레코드 바꾸고 바로 됐겠지, 이메일은 그냥 발송, DMARC reject로 강하게" (전파 미반영 + 스팸함 + 정당 메일 차단)
✅ "TTL 선하향 + 3종 인증 + DMARC 단계적 + 만료 자동화 — DNS·이메일은 조용히 깨지니 자동·경보로"

### 판단이 막히면 (확인 필요 4요소)

DNS·이메일 설정은 외부 사실(발송 주체·등록기관·ISP의 CGNAT 여부)에 막힌다 — 추측 값으로 레코드를 쓰면 메일이 조용히 안 가거나 전파가 어긋난다. **누가·언제·어떻게·기대값** 4요소로 질의한다.

- **누가**: 도메인 등록기관 계정·메일 발송 인프라를 아는 사람(운영·계정 소유자) — SPF/DKIM의 정확한 값은 발송 서비스(SES·SendGrid·자체)가 정한다.
- **언제**: ① 발송 주체 불명(자체 메일서버 vs 서드파티 — SPF include 값이 달라짐) ② 기존 정당 발송원 목록 미상(DMARC 조이기 전 필수) ③ 홈서버 ISP의 CGNAT 여부 미확인(DDNS 가능성 판가름).
- **어떻게**: `[확인 필요] <항목> — 현재 가정: <SES 발송>, 근거: <없음/추정>, 다른 답이면 SPF·DKIM 값이 <전부 바뀜>. 실제 발송 경로?` (가정/근거/영향/택일).
- **기대값**: 발송 서비스명·정당 발송원 목록·공인 IP 고정 여부. 답이 오면 레코드 값을 확정한다. 끝내 불명이면 **DMARC p=none(모니터링만)**으로 잠그고 rua 리포트로 실제 발송원을 관측해 역으로 채운다 — 조이기는 현황 파악 후가 보수적이다.

### 사용자가 권고를 거부하면

- "이메일 인증 귀찮아" → 스팸함 직행·스푸핑 악용 1회 고지(현대 메일은 인증 필수) + 최소 SPF만이라도. 거부 시 도달률 리스크 기록.
- "DMARC 바로 reject" → 정당 메일 누락 위험 고지, p=none 리포트로 현황 파악 먼저 강력 권고.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — Gmail/Yahoo 발신자 요구사항 강화 (2024)

2024년 Gmail과 Yahoo는 **대량 발신자(Gmail 수신자에게 하루 5,000통 이상)에게 SPF·DKIM·DMARC를 의무화**했다(2024-02-01 발효, Google "Email sender guidelines") — 인증 안 된 도메인의 메일은 거부·스팸 처리. 더해 **스팸률 <0.30% 유지 + 원클릭 구독취소(RFC 8058 헤더)**까지 요구. 그 전까지 "그냥 보내도 가던" 메일이 일제히 막혔고, 인증 미설정 서비스들이 갑자기 메일 도달률 급락을 겪었다. 더 오래된 교훈으로 **도메인 만료로 인한 대형 서비스 다운**(여러 기업이 도메인 갱신 누락으로 전체 서비스 중단)도 반복된다. 교훈: ① 이메일 인증은 이제 선택이 아니라 발송 전제조건 — 3종 세트가 기본 ② DNS·도메인·인증서는 "예고된 장애"의 집합소(만료일이 정해져 있다) — 자동화+경보가 유일한 방어 ③ "전에 됐으니 되겠지"가 가장 위험(요구사항·만료는 시간이 바꾼다) — dev-networking 인증서 만료와 한 가족.

## 사용자 환경 적용

- 사용자 도메인 example-domain.com(이메일 sun@example-domain.com) 운영 — SPF/DKIM/DMARC가 메일 도달률·신뢰의 전제. 발송 주체(자체 vs SendGrid·SES류)에 따라 레코드 값 결정.
- 홈서버 외부 노출 서브도메인은 DDNS + dev-networking(VPN/터널)·dev-nginx(프록시)와 협업. CGNAT 여부가 DDNS 가능성을 가른다.
- 도메인·인증서 만료 경보를 monitoring-discord-bot(dev-monitoring)에 — "예고된 장애"를 달력이 아니라 시스템이 기억하게.

## 레퍼런스

- `scripts/dns_check.py` — 루트 CNAME·MX IP 지정·SPF/DKIM/DMARC 누락·DMARC p=reject 즉시 적용 검출 (표준 라이브러리만, `python scripts/dns_check.py` 데모)
- `references/records-email-auth.md` — 레코드 타입별 용도·TTL 전략·SPF/DKIM/DMARC 작성·전파 확인·DDNS 설정
- `references/evidence-checklist.md` — 출처(Gmail 2024·DMARC) + 출고 전 체크리스트

## 한계

DNS·도메인·이메일 인증 중심 — 연결 진단·홈 네트워크는 dev-networking, 메일 발송 시스템(큐·재시도·도달률 추적)은 dev-notification, 프록시·TLS는 dev-nginx. DNS 제공자별 UI·API는 상이 — 이 스킬은 레코드 원리, 구체 설정은 제공자(Cloudflare·Route53 등) 문서. 고급 메일 인프라(BIMI·MTA-STS)는 도입 시점 확인.
