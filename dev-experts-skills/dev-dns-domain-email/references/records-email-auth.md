# 레코드·이메일 인증·전파·DDNS (SKILL.md 비중복)

## DNS 레코드 타입별 용도

| 타입 | 용도 | 주의 |
|---|---|---|
| A | 도메인 → IPv4 | 루트에 사용 가능 |
| AAAA | 도메인 → IPv6 | IPv6 지원 시 |
| CNAME | 별칭(다른 이름으로) | **루트 금지**, 서브도메인만, 체인 최소 |
| ALIAS/ANAME | 루트의 CNAME 대용(제공자 기능) | 루트를 다른 도메인에 가리킬 때 |
| MX | 메일 수신 서버(우선순위 + 호스트명) | IP 금지, 호스트는 A 보유 |
| TXT | SPF·DKIM·DMARC·도메인 소유 확인 | 길이·인용 주의 |
| NS | 권한 네임서버 | 위임 |
| CAA | 인증서 발급 가능 CA 제한 | 보안 강화(선택) |
| SRV | 서비스 위치 | 특수 프로토콜 |

## 이메일 인증 3종 세트

### SPF (발신 서버 허용 목록)
```
example.com TXT "v=spf1 include:_spf.google.com ip4:203.0.113.5 -all"
```
- `-all`(엄격, 미허용 거부) vs `~all`(soft, 의심) — 도입은 ~all, 안정 후 -all.
- include로 발송 서비스(메일 호스팅·SendGrid 등) 위임. **10 DNS 조회 한도** 주의(include 중첩 과다 시 실패).
- 한계: 전달(forwarding) 시 발신 IP가 바뀌어 깨짐 → DKIM이 보완.

### DKIM (서명)
```
selector._domainkey.example.com TXT "v=DKIM1; k=rsa; p=<공개키>"
```
- 발송 서버가 개인키로 서명, 수신 서버가 DNS의 공개키로 검증 → 위변조·발신자 확인. 전달에도 살아남음(SPF 보완).
- 셀렉터로 키 회전 가능(여러 키 공존). 키는 발송 서비스가 생성·제공.

### DMARC (정책 + 리포트)
```
_dmarc.example.com TXT "v=DMARC1; p=none; rua=mailto:dmarc@example.com; adkim=s; aspf=s"
```
- SPF·DKIM이 **정렬(alignment)** 됐는지 확인 + 실패 시 정책(none/quarantine/reject) + 리포트(rua).
- 단계: `p=none`(모니터링) → 리포트로 정당 발송원 전부 인증 확인 → `p=quarantine` → `p=reject`.
- rua 리포트가 "누가 내 도메인으로 보내는가"를 알려줌 — 스푸핑·미인증 발송원 발견.

## TTL 전략 (변경 시)

```
1. 변경 며칠 전: TTL을 300(5분)으로 하향
2. 옛 TTL(예 3600)만큼 기다림 (전 세계 캐시가 새 TTL 학습)
3. 실제 레코드 변경 → 5분 내 전파
4. 안정 확인 후 TTL 복원(3600)
```

확인: `dig @8.8.8.8 example.com`, `dig @1.1.1.1` 등 여러 리졸버 — 전파는 균일하지 않다. `dig +trace`로 권한 서버부터 추적.

## DDNS (홈서버 동적 IP)

```
공인 IP 변경 감지 -> DNS 제공자 API로 A 레코드 갱신
```
- 공유기 내장 DDNS(제공자 제한) 또는 스크립트(ddclient·제공자 API) + cron(dev-linux-ops).
- TTL은 낮게(300) — IP가 자주 바뀌므로 빠른 전파 필요.
- **CGNAT 확인**(dev-networking): 공유기 WAN IP ≠ 외부에서 본 IP면 CGNAT → DDNS 무의미, Cloudflare Tunnel·VPS 릴레이 필요.

## 도메인 운영

- auto-renew 켜기 + 결제수단 유효 + 만료 30일 경보(dev-monitoring) — 도메인 만료는 서비스 전체 다운 + 탈취 위험.
- WHOIS 개인정보 보호(privacy protection) 사용.
- CAA 레코드로 인증서 발급 CA 제한(보안 강화) — Let's Encrypt 쓰면 `0 issue "letsencrypt.org"`.
- 네임서버 변경은 전파가 길다(최대 48h) — 이전 시 양쪽 레코드 동기화 후 전환.
