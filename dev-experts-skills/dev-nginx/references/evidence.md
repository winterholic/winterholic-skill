# dev-nginx evidence — 장애·실증 사례

## 1. alias/proxy 경로 traversal — 설정 한 줄의 접근 제어 붕괴 (침투 테스트 고전)

- **무슨 일**: `location /static { alias /app/static/; }` (location 끝 슬래시 없음 + alias 끝 슬래시) 조합에서 `/static../secret.conf` 요청이 `/app/secret.conf`로 해석되는 "alias traversal" — Detectify·PortSwigger 등이 표준 점검 항목으로 문서화했고 실서비스 발견 사례 다수. proxy_pass 경로 치환 오해도 같은 부류의 우회를 만든다.
- **방어**: ① location과 alias의 끝 슬래시를 **쌍으로** 맞춘다(`location /static/ { alias /app/static/; }`) ② 정적 루트는 가급적 root 지시어(치환 없음 — 함정 면적 작음) ③ 출고 전 `curl --path-as-is http://host/static../etc/passwd` 류 1회 점검.
- **이 스킬과의 연결**: 안티패턴 2의 보안 승격판 — 경로 변환 규칙은 편의 기능이 아니라 보안 경계다.

## 2. add_header 전무 상속 — "그 경로만 보안 헤더가 없다" (공식 명세 함정)

- **무슨 일**: 보안 스캔(또는 침투 테스트)에서 특정 경로만 HSTS/CSP 부재 판정 — 원인은 그 location에 추가된 Cache-Control add_header 한 줄이 server 레벨 헤더 전체 상속을 끊은 것. nginx 공식 문서 원문: "These directives are inherited from the previous configuration level **if and only if there are no add_header directives defined on the current level**." 직관과 반대라 반복 사고.
- **방어**: ① 공통 헤더를 `security-headers.conf`로 추출 → add_header를 쓰는 모든 레벨에 `include security-headers.conf;` 명시. ② **nginx 1.29.3+**면 `add_header_inherit merge;`로 상위 헤더 병합 상속을 명시적으로 켜는 게 정공법(on/off/merge 지원, 상속 규칙 자체도 하위로 상속됨). 점검: `curl -sI <각 대표 경로> | grep -i strict-transport` 를 경로 샘플마다.
- **출처**: nginx 공식 ngx_http_headers_module 문서 (https://nginx.org/en/docs/http/ngx_http_headers_module.html — add_header / add_header_inherit 명세, 1차 출처) · NGINX Community Blog "What's New in 1.29.3/1.29.4" (https://blog.nginx.org/blog/nginx-open-source-1-29-3-and-1-29-4 — add_header_inherit 도입 공지).
- **이 스킬과의 연결**: 안티패턴 6. "상속이 끊기는 지시어"(add_header·proxy_set_header 등 배열형 다수)는 nginx 설정 리뷰의 고정 점검 항목.

## 3. 502 Bad Gateway — 4갈래 표준 진단 (운영 절차 실증)

- **무슨 일**: 502는 "nginx는 살아있고 백엔드와의 대화가 실패"라는 뜻 — 원인은 거의 4갈래로 수렴하며 전부 error.log에 단서가 있다:
  1. `connect() failed (111: Connection refused)` → 백엔드 다운·포트 불일치 (컨테이너면 네트워크/이름 해석 — dev-docker)
  2. `upstream prematurely closed` → 백엔드가 처리 중 사망(앱 크래시 — 백엔드 로그로)
  3. `upstream timed out` → proxy_read_timeout < 백엔드 처리시간 (안티패턴 4)
  4. `upstream sent too big header` → 버퍼 부족(proxy_buffer_size 상향 — 거대 쿠키/헤더가 진범인지 먼저 확인)
- **절차**: error.log의 메시지 → 위 표 대조 → 백엔드 측 로그 교차 확인. nginx 재시작은 이 4갈래 중 무엇도 고치지 못한다 — "재시작했더니 잠깐 됐다"는 백엔드 재연결 우연.
- **이 스킬과의 연결**: 워크플로우의 "error.log 먼저" — 502를 추측으로 다루지 않게 하는 고정 분기표.

## 4. CVE-2026-9256 / CVE-2026-42945 — rewrite 모듈 힙 오버플로 2연타 (2026-05, 패치 추종 실증)

- **무슨 일**: 2026-05, ngx_http_rewrite_module에서 별개의 힙 버퍼 오버플로 2건이 연달아 공개·수정. CVE-2026-42945(먼저, 1.31.0/1.30.1에서 수정)와 CVE-2026-9256(9일 뒤, 1.31.1/1.30.2에서 수정). 후자는 redirect/args 컨텍스트에서 중첩·겹치는 PCRE 캡처(`^/((.*))$` 류) + 다중 캡처 참조 replacement(`$1$2`) 조합 시 URI 이스케이프 후 길이를 과소계산해 워커 메모리 풀에 OOB write — 미인증 원격 트리거 가능, ASLR 무력화 환경에선 RCE 경로까지. nginx 자체 등급은 medium, F5 CVSS v4.0 9.2.
- **함정**: CVE-2026-42945 패치(1.31.0/1.30.1)만 적용한 환경은 CVE-2026-9256에 **여전히 취약**. "최근에 업데이트했음"이 알리바이가 안 된다.
- **방어**: ① **패키지 버전이 아니라 실행 바이너리**를 1.31.1+(mainline) / 1.30.2+(stable)로 확인 ② rewrite 지시어의 중첩/겹치는 캡처 그룹 감사, 임시완화로 무명 캡처를 named capture로 치환 + ASLR 활성 확인 ③ 외부 노출 리버스 프록시·API 게이트웨이 우선 패치.
- **이 스킬과의 연결**: SKILL.md 실전 케이스 + 부패 등급(보안 패치 추종)의 구체적 실증.

> 출처: nginx 공식 보안 권고 (https://nginx.org/en/security_advisories.html — CVE-2026-9256 Not vulnerable 1.31.1+/1.30.2+, CVE-2026-42945 Not vulnerable 1.31.0+/1.30.1+, 1차 출처) · nginx 공식 문서·위키(If is Evil, ngx_http_core_module location, ngx_http_headers_module) · oss-security 메일링 (https://www.openwall.com/lists/oss-security/2026/05/22/14) · GitHub Advisory GHSA-h78r-86c6-jgp4 · PortSwigger/Detectify 경로 traversal 연구. 2026-06, nginx 1.30.x stable / 1.31.x mainline 기준.
