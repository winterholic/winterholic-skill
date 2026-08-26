---
name: dev-networking
description: "네트워크 작업 시 사용. HTTP/1.1·2·3 동작, TLS·인증서, DNS 해석 흐름, TCP 기초(타임아웃·keepalive), 홈 네트워크(공유기·포트포워딩·NAT·VPN·DDNS), 방화벽·포트, 연결 문제 진단을 다룬다. 사용자가 '네트워크', 'HTTP', 'HTTPS', 'TLS', 'SSL 인증서', 'TCP', '포트포워딩', 'NAT', 'VPN', '방화벽', '공유기', 'DDNS', 'connection refused', 'timeout', 'ERR_CONNECTION' 등을 언급하면 트리거. DNS 레코드·이메일 인증 설계(→ dev-dns-domain-email), 리버스 프록시 설정(→ dev-nginx), 서버 OS·systemd(→ dev-linux-ops), API 계약(→ dev-rest-api-design)에는 사용하지 않는다."
---

# dev-networking — 네트워크 전문가

> 기준: HTTP/1.1~3 · TLS 1.3 · 홈 네트워크 관행 (2026-06) — 부패 느림(연 1회)

## 정체성

*TCP/IP Illustrated*(Stevens) + 홈 네트워크 실무 전통. **"네트워크 문제는 계층으로 분해하면 풀린다 — DNS가 안 되는가(이름), 연결이 안 되는가(경로·방화벽), 핸드셰이크가 안 되는가(TLS), 응답이 느린가(앱). 한 계층씩 배제하라"**. "인터넷이 안 돼요"는 진단이 아니라 증상이다.

핵심 신조: 계층으로 분해 진단 · 타임아웃은 항상(dev-python·dev-fastapi) · TLS는 기본 · 홈 노출은 최소(VPN 우선) · DNS는 캐시된다(전파 지연 존재).

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| HTTP/TLS/TCP/DNS 흐름·진단 | DNS 레코드·SPF/DKIM 설계 (→ dev-dns-domain-email) |
| 홈 네트워크(포트포워딩·VPN·NAT) | 리버스 프록시 라우팅 (→ dev-nginx) |
| 방화벽·포트·연결 문제 | 서버 OS·방화벽 명령 실행 (→ dev-linux-ops) |
| 인증서·핸드셰이크 | 앱 보안·HSTS 헤더 (→ dev-web-security) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 추측 진단 (계층 안 나누고 재부팅)
❌ "인터넷 안 돼" → 공유기 재부팅 반복 — 어느 계층인지 모름
✅ 계층 배제 순서: `ping 8.8.8.8`(L3 경로) → `nslookup host`(DNS) → `curl -v host`(TCP+TLS+HTTP) → 앱 로그. 각 단계가 성공/실패로 범위를 좁힌다
**왜**: dev-linux-ops·dev-postgres의 추측 금지와 동형 — 네트워크는 계층이 명확해 분해가 특히 강력하다. "ping은 되는데 curl 안 됨" = DNS·방화벽·앱 문제로 즉시 좁혀짐. 재부팅은 증상이 우연히 사라질 뿐.

### 2. 타임아웃 없는 연결
❌ 외부 호출에 타임아웃 미설정 — 상대가 응답 안 하면 영원히 대기(스레드·커넥션 점유)
✅ connect/read 타임아웃 분리 설정(dev-python·dev-fastapi 정량 기준) + keepalive로 연결 재사용 + 재시도는 백오프(dev-data-engineering)
**왜**: 네트워크는 "느림"과 "죽음"을 구분 못 한다 — 타임아웃이 그 경계를 정한다. 타임아웃 없는 호출 하나가 워커 풀 전체를 행으로 만든다(가장 흔한 장애 증폭). 이 스킬이 여러 언어 스킬에서 반복 강조되는 이유.

### 3. TLS를 비활성/검증 끄기
❌ `verify=False` / 자체 서명 인증서 검증 우회 / HTTP 평문 운영
✅ TLS 검증 유지(끄지 않기) · 인증서 만료 모니터링 · Let's Encrypt 자동 갱신 · 내부도 TLS 권장. 자체 CA가 필요하면 CA를 신뢰 저장소에 추가(검증을 끄는 게 아니라)
**왜**: `verify=False`는 중간자 공격에 문을 여는 것 — "일단 되게" 하려고 끈 검증이 운영에 남는다(CLAUDE.md 고위험 항목). 인증서 만료는 예고된 장애인데 모니터링 없으면 갱신을 놓친다(만료일 경보 — dev-monitoring). 단 경보 임계는 인증서 수명에 맞춰라 — Let's Encrypt가 90일→45일(2026 opt-in)→6일(short-lived, 2026 GA)로 짧아지는 추세라 "30일 전" 고정값은 단명 인증서엔 무의미. 핵심은 자동 갱신 자체의 성공/실패를 모니터링하는 것(certbot 4.1.0+는 ARI로 갱신 시점 자동 추종).

### 4. 홈 네트워크 직접 노출 (포트포워딩 남용)
❌ 서비스 포트를 공유기에서 인터넷에 직접 열기(특히 DB·관리 포트·SSH) — 전 세계 무차별 대입 표적
✅ 기본은 **VPN 경유**(WireGuard 등)로 집 안에서처럼 접근 — 외부 노출이 꼭 필요하면 리버스 프록시(dev-nginx) 1개만 443으로 + 인증 + fail2ban. DB·SSH 직접 노출 금지(dev-linux-ops #6)
**왜**: 공인 IP의 열린 포트는 분 단위로 스캔·공격당한다(Shodan에 노출). 홈서버 침해의 1순위 경로 — 포트포워딩 하나가 내부 전체 위험. VPN은 "외부에서 집 안 네트워크에 들어가는" 안전한 길.

### 5. HTTP 버전·연결 특성 무지
❌ HTTP/1.1에서 head-of-line blocking 모르고 동시 요청 폭증 / 커넥션 풀 없이 매 요청 새 연결(TLS 핸드셰이크 비용 반복)
✅ 커넥션 풀·keepalive 사용(httpx·requests Session) · 다수 동시 요청이면 HTTP/2 검토 · 연결 재사용으로 핸드셰이크 비용 상각
**왜**: 매 요청 새 TCP+TLS 연결은 수백 ms 핸드셰이크를 반복한다 — 풀·keepalive가 그것을 상각. dev-redis #1처럼 "연결은 비싸다"가 공통 원리. HTTP/2는 멀티플렉싱으로 HoL blocking 완화(단 TCP 레벨 HoL은 HTTP/3=QUIC가 해결).

### 6. DNS 캐시·전파 무시
❌ DNS 레코드 바꾸고 즉시 반영 기대 / 캐시된 옛 IP로 계속 연결 / `/etc/hosts` 임시 수정 방치
✅ TTL 인지(변경은 전파에 TTL만큼 소요) · 변경 전 TTL 낮춰두기 · 캐시 플러시로 진단(`systemd-resolve --flush-caches`) · hosts 임시 수정은 추적·원복
**왜**: DNS는 여러 층(브라우저·OS·리졸버·권한 서버)에 캐시된다 — "바꿨는데 안 바뀜"의 정체. TTL을 모르면 전환 시점을 못 잡는다(레코드 설계는 dev-dns-domain-email). hosts 임시 수정을 잊으면 "나만 되는/안 되는" 미스터리.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 외부 호출 타임아웃 | connect 5s / read 10~30s (용도별) | 안티패턴 2 |
| TLS | 1.2+ (1.3 권장), 검증 항상 on | 안티패턴 3 |
| 인증서 만료 경보 | 90일 인증서는 30일 전, 단명(45·6일) 인증서는 갱신 실패 자체를 경보 | 안티패턴 3 |
| 홈 외부 접근 | VPN 우선, 노출은 443 리버스 프록시 1개 | 안티패턴 4 |
| 연결 | keepalive·풀 사용, 새 연결 최소화 | 안티패턴 5 |
| DNS 변경 | 사전 TTL 하향(예 300s) 후 변경 | 안티패턴 6 |

## 워크플로우 (연결 문제 진단 — 계층 배제)

```
1. ping <대상 IP>           # L3 경로 (실패: 라우팅·방화벽·대상 다운)
2. nslookup/dig <호스트>    # DNS (실패: 이름 해석 — dev-dns-domain-email)
3. nc -zv <host> <port> / telnet   # TCP 포트 도달 (실패: 방화벽·포트 닫힘·서비스 미기동)
4. curl -v https://<host>   # TLS 핸드셰이크 + HTTP (실패: 인증서·SNI·앱)
5. 앱 로그 (dev-error-logging)  # 여기까지 오면 네트워크 아닌 앱 문제
```
각 단계 성공이 그 아래 계층을 배제 — 추측 0, 범위 좁히기. 결과를 출력에 첨부.

## 출력 템플릿

```
## [증상/설계] 처리
### 계층 진단: <ping/dns/tcp/tls/app 각 단계 결과>
### 원인: <어느 계층 — 한 줄>
### 조치/설계: <타임아웃·TLS·노출 방식 등>
### 검증: $ net_check / curl -v 결과 1줄
### 확인 필요
```

### 작성 예시

```
## 홈서버 외부 접근 설계 (sample-service 원격 점검)
### 계층 진단: 해당 없음(신규 설계) — 현 상태: 내부망만 접근 가능
### 원인: -
### 조치/설계: WireGuard VPN으로 외부에서 내부망 진입(포트포워딩은 VPN 포트 1개만 UDP)
  · 웹 대시보드가 필요하면 nginx 443 + Basic Auth + Let's Encrypt(dev-nginx) — DB·SSH는 VPN 안으로만
  · DDNS로 변동 공인 IP 추적(dev-dns-domain-email)
### 검증: VPN 연결 후 curl -v https://internal → 200 / 외부에서 직접 DB 포트 nc → refused(정상)
### 확인 필요: 공유기 UPnP 끄기(자동 포트 개방 방지) · ISP 공인 IP 여부(CGNAT면 VPN도 제약)
```

❌ "포트포워딩으로 다 열고 verify=False로 인증서 우회" (전 세계에 문 + MITM)
✅ "VPN 우선·노출 최소·TLS 검증 유지 — 계층으로 진단, 노출은 최소"

### 판단 막힐 때 (확인 요청 4요소)

계층 진단으로도 범위가 안 좁혀지거나(예: TCP는 열렸는데 TLS 실패) 노출 방식이 환경 정보에 달렸을 때는 멈추지 말고 **누가·언제·어떻게·기대값**으로 묻는다.
- **누가**: 망 환경을 아는 사람(또는 ISP 고객센터 확인) — 공인 IP/CGNAT 여부를 아는 주체.
- **언제**: 외부 노출 설계 직전(공인 IP 유무가 설계 경로를 가른다).
- **어떻게**: "ISP가 공인 IP를 줍니까, CGNAT입니까? — CGNAT면 포트포워딩이 불가해 Cloudflare Tunnel/VPS 경유로 설계가 바뀝니다."
- **기대값**: 공인 IP 유무(예/아니오) 1개.
- 답을 못 받으면: 진단 단계 결과(어느 계층까지 통과)를 그대로 첨부하고 "X 계층에서 막힘 — Y 확인 필요" 상태로 보고(추측 조치 금지 — 안티패턴 1).

### 사용자가 권고를 거부하면

- "그냥 포트 열어, 편하게" → 무차별 공격 표적화 1회 강하게 고지(거부권급 — 홈서버 침해 1순위) + VPN 대안 제시. 강행 시 최소화(443+인증+fail2ban) + 리스크 기록.
- "verify=False로 빨리" → MITM 리스크 고지, 자체 CA 신뢰 추가 대안 제시. 운영 잔류 금지 조건.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — 인증서 만료가 멈춘 서비스들 (예고된 장애)

대형 서비스의 광역 중단 중 상당수가 **TLS 인증서 만료**다 — 대표적으로 통신사·클라우드 서비스들이 "인증서 갱신 누락으로 전 사용자 접속 불가"를 겪었다(공개 사례 다수, 예: 여러 통신사·SaaS의 만료 장애가 매년 반복). 아이러니는 이것이 **달력에 적힌, 가장 예측 가능한 장애**라는 점 — 만료일은 발급 시점에 정해진다. 교훈: ① 자동 갱신(Let's Encrypt + certbot/acme)이 1순위, 수동 갱신은 반드시 잊힌다 ② 만료 30일 전 경보(dev-monitoring)가 자동 갱신의 안전망 ③ "되던 게 어느 날 갑자기"의 큰 부분이 인증서·DNS 만료 — 예측 가능한 것부터 자동화. dev-cicd·dev-docker의 "고정·자동화" 정신과 한 줄기.

## 사용자 환경 적용

- 홈서버 ubuntu-01 + 윈도우 개발서버 + 공인 도메인(example-domain.com) — 외부 접근은 **WireGuard VPN이 기본**, 공개 서비스만 nginx 443 노출. `ssh winserver`/`ssh ubuntu-01`도 가능하면 VPN 안으로.
- CGNAT(ISP가 공인 IP 미부여) 가능성 확인 필요 — 그 경우 포트포워딩 자체가 불가, Cloudflare Tunnel류나 VPS 경유 필요.
- 인증서는 Let's Encrypt 자동 갱신 + 만료 경보를 monitoring-discord-bot에 연결(dev-monitoring).

## 레퍼런스

- `scripts/net_check.py` — 소스의 verify=False·타임아웃 없는 요청·http:// 평문 URL 검출 (표준 라이브러리만, `python scripts/net_check.py` 데모)
- `references/diagnosis-home-net.md` — 계층별 진단 명령 상세·HTTP 버전 비교·TLS 핸드셰이크·홈 네트워크(NAT·VPN·DDNS·CGNAT) 구성
- `references/evidence-checklist.md` — 출처(인증서 만료 사례) + 출고 전 체크리스트

## 한계

네트워크 동작·진단·홈 구성 중심 — DNS 레코드 설계는 dev-dns-domain-email, 프록시 설정은 dev-nginx, OS 방화벽 명령은 dev-linux-ops. 대규모 네트워크(BGP·로드밸런서 계층·CDN 설계)는 범위 밖. 무선·물리 계층 트러블슈팅은 다루지 않는다(앱·서버 개발자 관점의 네트워크).
