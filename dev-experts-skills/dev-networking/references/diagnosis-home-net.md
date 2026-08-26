# 계층 진단·HTTP 버전·TLS·홈 네트워크 (SKILL.md 비중복)

## 계층별 진단 명령 (배제법 상세)

| 계층 | 명령 | 실패가 뜻하는 것 |
|---|---|---|
| L3 경로 | `ping <IP>` / `traceroute <IP>` | 라우팅·방화벽·대상 다운 (ICMP 차단도 있음 — 참고만) |
| DNS | `dig <host>` / `nslookup` / `dig +trace` | 이름 해석 실패 (레코드·리졸버 — dev-dns-domain-email) |
| TCP 포트 | `nc -zv <host> <port>` / `ss -tlnp`(로컬) | 방화벽·포트 닫힘·서비스 미기동 |
| TLS | `openssl s_client -connect host:443` / `curl -v` | 인증서 만료·체인·SNI·프로토콜 불일치 |
| HTTP | `curl -v -w "%{time_total}"` | 앱 응답·상태코드·지연 |
| 앱 | 로그(dev-error-logging) | 네트워크 아닌 앱 문제 |

- 윈도우: `Test-NetConnection host -Port n`(nc 대용), `Resolve-DnsName`(dig 대용) — dev-windows-powershell.
- `curl -v`가 만능 진단기 — DNS 해석 IP·TLS 핸드셰이크·인증서·HTTP 상태를 한 번에 보여준다.

## HTTP 버전 비교 (언제 무엇)

> 스펙 1차 출처: HTTP/2=RFC 9113, HTTP/3=RFC 9114, QUIC=RFC 9000(전송)·9001(TLS)·9002(손실복구). [신뢰: IETF RFC Editor]

| | HTTP/1.1 | HTTP/2 | HTTP/3 (QUIC) |
|---|---|---|---|
| 멀티플렉싱 | ✕ (연결당 1요청, HoL) | ◎ (스트림) | ◎ |
| HoL blocking | 있음 | TCP 레벨 잔존 | 없음(UDP/QUIC) |
| 연결 비용 | TCP+TLS | TCP+TLS(연결 1개 재사용) | QUIC(0-RTT 재연결) |
| 쓰는 곳 | 단순·내부 | 다수 동시 요청·외부 | 모바일·고지연 네트워크 |

- 대부분 리버스 프록시(nginx)·CDN이 버전 협상을 처리 — 앱은 1.1로 받아도 됨. 클라이언트(외부 API 호출)는 라이브러리 기본을 신뢰하되 keepalive·풀만 챙긴다.
- HoL blocking: 1.1에서 한 느린 응답이 같은 연결의 뒤를 막음 → 동시 요청은 연결 여러 개 또는 2/3.

## TLS 핸드셰이크·인증서 빠른 이해

- 핸드셰이크 비용: TLS 1.3은 1-RTT(재개 시 0-RTT 가능), TLS 1.2는 2-RTT — 그래서 연결 재사용이 중요(안티패턴 5). [근거: RFC 8446 TLS 1.3]
- 인증서 체인: 서버 인증서 → 중간 CA → 루트. "체인 불완전"(중간 CA 누락)이 "브라우저는 되는데 curl 안 됨"의 단골(브라우저는 중간 CA 캐시).
- SNI: 한 IP에 여러 도메인일 때 어느 인증서를 줄지 결정 — 프록시 설정 실수 시 엉뚱한 인증서.
- 만료 확인: `openssl s_client -connect host:443 | openssl x509 -noout -dates` 또는 모니터링 자동(만료 30일 경보).
- Let's Encrypt: certbot/acme.sh 자동 갱신(cron/timer — dev-linux-ops) — 수동 갱신은 반드시 잊힌다(실전 케이스).

## 홈 네트워크 구성

```
인터넷 -- [ISP] -- 공유기(NAT, 공인 IP 1개) -- 내부망(192.168.x.x)
                      |- 포트포워딩: 외부 포트 -> 내부 IP:포트 (최소화!)
                      |- VPN 서버(WireGuard): 외부에서 내부망 진입 (권장 접근법)
                      |- DDNS: 변동 공인 IP를 도메인에 자동 갱신
```

- **NAT**: 내부 사설 IP는 외부에서 직접 접근 불가 — 그래서 포트포워딩(위험) 또는 VPN(안전)이 필요.
- **CGNAT 함정**: ISP가 공인 IP를 안 주고 자기들끼리 NAT(공인 IP 공유)하면 포트포워딩·DDNS 무력 — 확인: 공유기 WAN IP vs 외부에서 본 IP 일치 여부. 불일치면 Cloudflare Tunnel·VPS 릴레이·역방향 터널 필요.
- **VPN 우선 원칙**: WireGuard 1포트(UDP)만 열어 내부망 전체를 안전하게 — 서비스마다 포트 여는 것보다 공격 표면이 훨씬 작다(안티패턴 4).
- **DDNS**: home.example.com → 현재 공인 IP 자동 갱신(공유기 내장 또는 스크립트 — dev-dns-domain-email과 협업).

## 연결 문제 빠른 분류표

| 증상 | 1순위 의심 |
|---|---|
| connection refused | 서비스 미기동 또는 포트 닫힘(방화벽) — 즉시 거부 = 도달은 함 |
| connection timeout | 방화벽 drop 또는 라우팅 — 응답조차 없음 |
| DNS 해석 실패(NXDOMAIN) | 레코드 없음·오타·전파 전(dev-dns-domain-email) |
| TLS handshake failed | 인증서·프로토콜·SNI |
| 느림(연결은 됨) | 앱·DNS 지연·MTU — curl time 분해로 |
