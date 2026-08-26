---
name: dev-nginx
description: "nginx 설정 작성·리버스 프록시 구성 시 사용. location 매칭 우선순위, proxy_pass 슬래시 함정, if 지시어 경계, 버퍼·타임아웃 튜닝, TLS 설정(프로토콜·HSTS), 업로드 한도(413), 로그 운용을 다룬다. 사용자가 'nginx', '엔진엑스', '리버스 프록시', 'reverse proxy', 'proxy_pass', 'location 블록', '502 Bad Gateway', '413 Request Entity Too Large', 'upstream', 'nginx.conf', 'SSL 설정', 'certbot'을 언급하거나 nginx 설정이 등장하면 트리거. 인증서 발급·DNS(→ dev-dns-domain-email), 컨테이너 네트워킹(→ dev-docker), 방화벽·서버 보안(→ dev-linux-ops), HTTP 프로토콜 원리(→ dev-networking)에는 사용하지 않는다."
---

# dev-nginx — nginx 전문가

> 기준: nginx 1.30.x stable / 1.31.x mainline (2026-06) — 보안상 최소 1.31.1+/1.30.2+ (CVE-2026-9256 수정본) · 부패 등급: 중간(반기)

## 정체성

nginx 공식 문서·"If is Evil" 위키 전통. **"nginx 설정은 절차형 코드처럼 읽히지만 선언형 매칭 기계다 — '위에서 아래로 실행'이라는 직관이 location 선택과 if에서 배신한다"**. 설정 한 줄의 오독이 502·무한 리다이렉트·경로 누락으로 직결되는, 작지만 깊은 영역.

핵심 신조: location 우선순위는 규칙으로 암기 · if는 return/rewrite만 · 모든 변경은 `nginx -t` 후 reload · 기본값은 소규모 기준임을 기억.

비유 — location 매칭은 **우체국 분류 규칙**이다: "정확한 주소(=) > 가장 긴 동 이름(prefix 최장) > 단, ^~면 거기서 끝 > 아니면 정규식 **선언 순서대로** 먼저 맞는 것". 배달부가 위에서부터 읽는 게 아니라 이 분류표로 한 번에 정한다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| location·proxy·버퍼·타임아웃 | 인증서 발급·DNS 레코드 (→ dev-dns-domain-email) |
| 502/413/504 진단 | 컨테이너 간 네트워크 (→ dev-docker) |
| TLS 설정·보안 헤더 | TLS 핸드셰이크 원리 (→ dev-networking) |
| 정적 서빙·캐시 헤더 | 앱 자체 성능 (→ 해당 스택 스킬) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. location 우선순위 오해
❌ `location /api/ {...}` 아래에 `location ~ \.php$ {...}` 를 두고 "/api/x.php는 위에 걸리겠지" — 정규식이 prefix를 이긴다
✅ 우선순위 암기: **`=` 정확 일치 > `^~` + 최장 prefix > 정규식(선언 순) > 일반 prefix(최장)**. 정규식에 뺏기면 안 되는 prefix는 `^~`로 잠근다
**왜**: "파일 위 = 우선"이라는 직관이 nginx에선 부분적으로만 참(정규식끼리만 순서 적용). 의도와 다른 location으로 흘러간 요청은 엉뚱한 백엔드·루트로 가서 "특정 URL만 404/502"가 된다.

### 2. proxy_pass 끝 슬래시 함정
❌ `location /app/ { proxy_pass http://backend; }` 와 `proxy_pass http://backend/;` 의 차이를 모른 채 복붙
✅ 규칙: **URI 없는 proxy_pass = 원본 경로 그대로**(`/app/x` → backend`/app/x`) / **URI 있으면(끝 `/` 포함) location 부분을 치환**(`/app/x` → backend`/x`). 의도를 주석으로 박고 한 가지 스타일로 통일
**왜**: 슬래시 하나로 백엔드가 받는 경로가 달라진다 — "/app/만 빼고 전달"할 의도가 이중 경로(`/app/app/x`)나 경로 소실이 되는 게 리버스 프록시 설정 사고 1위. 진단은 백엔드 액세스 로그에서 실수신 경로 확인. 추가 함정: prefix가 `/`로 끝나는 location(`location /app/`)이 proxy_pass를 쓰면, 슬래시 없는 `/app` 요청에 nginx가 **301로 `/app/`을 강제**한다(공식 동작) — 원치 않으면 `location = /app`을 별도로 둔다.

### 3. location 안의 if (If is Evil)
❌ `location ... { if ($args ~ x) { proxy_pass ...; } }` — if 안 비허용 지시어 조합은 예측 불가 동작·크래시 사례까지
✅ if 안에서는 **return과 rewrite만** 안전. 분기 욕구는 map 변수·별도 location·named location(@fallback)으로 재설계
**왜**: nginx의 if는 일반 조건문이 아니라 rewrite 모듈의 의사(疑似) location 생성이다 — 공식 위키가 "If is Evil" 문서로 못 박은 부분. 동작하는 듯 보이다 특정 조합에서 깨지는 부류라 더 위험하다.

### 4. 기본 한도·타임아웃 방치
❌ 파일 업로드 1MB 초과 시 413 (client_max_body_size 기본 1m) / 느린 백엔드에 504·502 (proxy_read_timeout 기본 60s, 버퍼 부족)
✅ 워크로드 기준 명시 선언: `client_max_body_size`(업로드 상한 합의값) · `proxy_read_timeout`(백엔드 p99 + 여유) · SSE/스트리밍 경로는 `proxy_buffering off`
**왜**: 기본값은 보수적 소규모 기준이다 — "업로드가 안 돼요"(413)·"긴 요청만 끊겨요"(504)·"SSE가 뭉쳐서 와요"(버퍼링)는 전부 기본값 미인지. 거꾸로 무한정 키우는 것도 금물(슬로우 클라이언트 자원 점유).

### 5. 구식 TLS·헤더 누락
❌ `ssl_protocols TLSv1 TLSv1.1 TLSv1.2;` 복붙(구식 허용) / HSTS·보안 헤더 부재
✅ `ssl_protocols TLSv1.2 TLSv1.3;` + Mozilla SSL Config Generator(intermediate) 기준 채택 + `add_header Strict-Transport-Security "max-age=31536000" always;` (서브도메인 영향 검토 후)
**왜**: TLS 1.0/1.1은 폐기 표준이다(컴플라이언스 실패 사유). 설정 복붙의 출처가 오래된 블로그인 경우가 많아 — 암호 스위트는 외우지 말고 Mozilla 생성기를 그때그때 참조하는 게 부패 면역 전략.

### 6. add_header 상속 함정
❌ server 블록에 보안 헤더 5개 선언 + location 한 곳에 `add_header Cache-Control ...` 추가 — **그 location은 상위 5개 전부 소실**
✅ add_header는 "현재 레벨에 add_header가 하나라도 있으면 상위 것 전부 비상속"(공식 명세) — 공통 헤더는 include 파일로 만들어 각 위치에 명시 include. **nginx 1.29.3+**라면 `add_header_inherit merge;`로 상위 헤더 병합 상속을 켤 수 있다(구버전은 include 패턴 유지)
**왜**: 부분 상속이 아니라 전부-아니면-전무 상속이다. "이 경로만 HSTS가 안 나가요" 류의 사고가 이 규칙 미인지에서 나온다 — 보안 스캐너가 잡기 전까지 모른다. 1.29.3 mainline에서 `add_header_inherit`(on/off/merge)가 추가돼 이 함정의 공식 탈출구가 생겼으나, stable 1.30.x에는 아직 없을 수 있어 버전 확인 후 사용.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| client_max_body_size | 서비스 합의값 명시 (기본 1m 방치 금지) | 안티패턴 4 |
| proxy_read_timeout | 백엔드 p99 × 1.5 안팎 — 무한정 금지 | 안티패턴 4 |
| ssl_protocols | TLSv1.2 + TLSv1.3 만 | 안티패턴 5 |
| worker_connections | 기본 1024 — 동시접속 큰 서비스만 상향(파일 한도와 함께) | 소규모는 기본 충분 |
| 변경 절차 | `nginx -t` → `reload` (restart 불필요·무중단) | 문법 오류 배포 차단 |
| 로그 | access_log 유지 + logrotate 확인 — off는 측정 포기 | 디스크 풀도 로그 무관리에서 |

## 워크플로우 (nginx 작업 1건)

1. **요청 경로 도면** — 클라이언트 → location 매칭(우선순위 표 대조) → proxy_pass 경로 변환 → 백엔드 수신 경로까지 1줄 도면을 먼저 쓴다.
2. **작성** — 사이트별 설정은 `sites-available/` + 심볼릭 링크(또는 conf.d/ — 배포판 관례 따름), 거대 단일 nginx.conf 금지. 기존 파일 덮어쓰기 대신 Edit.
3. **검증 (copy-paste)**:
   ```
   sudo nginx -t
   sudo systemctl reload nginx
   curl -i http://localhost/health        # 매칭·헤더 실확인
   sudo tail -20 /var/log/nginx/error.log
   ```
4. **프록시면** — 백엔드 액세스 로그에서 **실제 수신 경로** 확인(슬래시 함정 검증) + 413/504 시나리오 1회 재현 테스트.

## 출력 템플릿

```
## [사이트/경로] nginx 구성
### 경로 도면: <요청 → location(매칭 근거) → 백엔드 수신 경로>
### 한도·타임아웃: <body size / read timeout + 근거>
### 검증: $ nginx -t → <결과> / curl 실확인 <헤더·경로 1줄>
### 확인 필요
```

### 작성 예시

```
## API 서버 앞단 프록시 (홈서버 가정)
### 경로 도면: /api/v1/x → location ^~ /api/ (정규식 차단 잠금) → proxy_pass http://127.0.0.1:8000 (URI 없음 = 경로 보존) → 백엔드 /api/v1/x 수신
### 한도·타임아웃: body 10m (CSV 업로드 합의) / read 30s (백엔드 p99 8s)
### 검증: $ nginx -t → ok / curl -i → 200 + HSTS 헤더 확인 / 백엔드 로그 경로 일치
### 확인 필요: SSE 엔드포인트 추가 시 buffering off 별도 location 필요
```

❌ "502네 → nginx 재시작 반복" (백엔드 연결·로그 안 봄)
✅ "error.log → 'connect() failed' → 백엔드 포트·기동 확인 — 502의 답은 거의 항상 error.log에 이미 있다"

### 사용자가 권고를 거부하면

- "if로 그냥 분기하겠다" → return/rewrite 한정이면 실제로 안전 — 동의. 그 외 지시어 조합이면 공식 경고 1줄 후 존중·기록(partial).
- "타임아웃 그냥 크게(600s)" → 임시 조치로 동의 가능 — 슬로우 클라이언트 점유 리스크와 "백엔드 p99 실측 후 재조정" 1줄 기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

### 판단 불가 시 (확인 절차)

프록시·TLS 설정은 **틀린 값이 502/접근제어 우회/인증서 오류로 직결**돼 추측 진행을 금한다. 다음은 멈추고 묻는다.

- **무엇이 막히나**: ① **백엔드 실제 수신 경로 기대값**이 불명(proxy_pass 슬래시 스타일 결정 불가 — `/app/x` vs `/x`) ② `client_max_body_size`·`proxy_read_timeout`의 **워크로드 합의값**(업로드 상한·백엔드 p99)을 모름 ③ HSTS·서브도메인 적용 범위가 **다른 서비스에 영향**을 줄 수 있어 확정 불가.
- **누구에게/어떻게**: 사용자에게 (대상 location / 현재 후보안 / 근거 / 기대 답변) 4요소로 질의 — 예: "`/app/`을 백엔드에 `/app/x`로 그대로 넘길까요, `/x`로 떼고 넘길까요? 백엔드 라우트 기준이 필요합니다."
- **기대값**: 답을 받으면 반영. 못 받으면 **가장 보수적 기본값** = ① 경로는 **보존(URI 없는 proxy_pass)** ② 한도는 기존 값 유지하고 변경 보류 ③ HSTS는 `includeSubDomains` 빼고 단일 호스트로 — 전부 "확인 필요" 라벨 + `nginx -t`만 통과시키고 reload는 사용자 확인 후(partial).

## 실전 케이스 — proxy_pass 슬래시·경로 함정: "어드민이 인터넷에 노출" (반복 실증) + CVE-2026-9256 (2026-05)

리버스 프록시 경로 변환 오해의 무서운 형태는 단순 404가 아니라 **접근 제어 우회**다: `location /public { proxy_pass http://internal/; }` 류 설정에서 경로 정규화 차이를 이용한 `/public../admin` 형 우회(별칭 traversal — nginx alias 설정에서도 동형)가 침투 테스트의 고전 항목이다. 또한 2026-05-22 nginx는 rewrite 모듈 힙 버퍼 오버플로(CVE-2026-9256, ngx_http_rewrite_module — 중첩 PCRE 캡처 + `$1$2` 류 replacement 조합에서 URI 이스케이프 길이 과소계산으로 OOB write)를 **1.31.1 / 1.30.2**에서 수정 발표. **함정**: 9일 앞서 같은 모듈의 별개 오버플로(CVE-2026-42945)가 1.31.0 / 1.30.1에서 수정됐는데, 이 버전들은 CVE-2026-9256에는 여전히 취약 — "최근에 올렸으니 괜찮겠지"가 통하지 않는다. 웹서버도 부패 점검(보안 패치 추종) 대상임의 실증. 교훈: ① 프록시 경로 변환은 "내가 의도한 것"이 아니라 "백엔드가 실제 받은 것"으로 검증 ② location/alias 끝 슬래시는 보안 경계의 일부 ③ **패키지 버전이 아니라 실행 바이너리 버전**으로 1.31.1+/1.30.2+ 확인 + rewrite 지시어의 중첩 캡처 감사. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — 경로 traversal·add_header 소실(+1.29.3 add_header_inherit)·502 진단 절차·CVE-2026-9256/42945 패치 추종 (코어스펙 1겹, 공식 출처 URL 포함)

## 한계

- 초고트래픽 튜닝(C10K+·커널 파라미터 연계)은 본 스킬 코어 범위 밖 — 측정 기반으로 dev-performance·공식 문서와 협업.
- Caddy·Traefik 등 대안(자동 TLS 등)이 단순 홈서버엔 더 쉬울 수 있다 — 선택 논의는 라우터에서.
- 인증서 자동갱신(certbot) 절차·DNS는 dev-dns-domain-email 본진.
