# evidence + 출고 전 체크리스트

## 실증·출처

- **OAuth 2.1 (IETF 드래프트 통합, 2026-03 기준 draft-15 — RFC 미확정이나 주요 IdP 채택) + OIDC Core** — PKCE 전 클라이언트 의무화·implicit/ROPC 제거·refresh rotation 기대의 표준 출처. https://oauth.net/2.1/
- **OWASP Authentication·Session Management Cheat Sheet** — 로그인 보안·세션 쿠키 속성·rate limit의 1차 처방. https://cheatsheetseries.owasp.org/
- **OWASP Password Storage Cheat Sheet** — argon2id 우선(m=19MiB,t=2,p=1 등)·bcrypt는 레거시 한정(work≥10, 입력 72바이트 한계). 체크리스트 비밀번호 해시 항목의 1차 근거. https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- **NIST SP 800-63B-4 (Digital Identity Guidelines, Rev 4, 2025-07-31 최종 확정 — 2024는 2차 공개 드래프트)** — 비밀번호 길이 우선(검증자 최소 8 허용·단일인자 권장 15·최소 64까지 지원 의무)·복잡도 구성 규칙 부과 금지·강제 주기변경 금지(침해 증거 시에만)·유출 목록 대조 권고. 안티패턴 1·5의 근거. (공식 1차 출처, 2026-06 본문 확인) https://pages.nist.gov/800-63-4/sp800-63b.html
- **JWT alg:none·알고리즘 혼동 취약점 (2015-03 Tim McLean 최초 공론화, CVE-2015-9235는 RS256→HS256 confusion 변종)** — alg 헤더 신뢰·옵션 오용의 위험. 표준 처방은 RFC 8725(JWT BCP)가 "허용 알고리즘 명시 검증"으로 정리. SKILL.md 실전 케이스. (블로그 헤더 표기일은 2020 재게시, 원 공론화는 2015-03 / 2026-06 확인) https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/
- **RFC 8725 (JSON Web Token Best Current Practices, 2020-02 발행)** — alg:none·알고리즘 혼동의 표준 1차 대응 출처: 기대 알고리즘 명시 검증·`none` 회피·키 용도 분리. SKILL.md alg:none 처방의 IETF 근거. (공식 RFC, 2026-06 확인) https://datatracker.ietf.org/doc/html/rfc8725
- **타이밍 공격·hmac.compare_digest** — Python 공식 문서가 비밀 비교에 명시 권고(상수시간 비교, OpenSSL CRYPTO_memcmp 기반). A1b의 근거. (2026-06 확인) https://docs.python.org/3/library/hmac.html#hmac.compare_digest
- 오픈소스 차용 표기: 인증 가이드·IdP 문서(색인 인지, 본문 비복사). **역흡수**: 세션 vs JWT 트레이드오프 표·"직접 구현 금지선" 명문화·refresh 재사용 탐지·거부 시 등급 분리 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (인증 기능 출고 시)

- [ ] 비밀번호 argon2id/bcrypt (자작 해시 0) — `auth_scan.py` 0건
- [ ] 세션/JWT 선택이 트레이드오프 근거와 함께 기록
- [ ] access token 짧음(분) + refresh rotation + 재사용 탐지(JWT 시)
- [ ] 인증과 인가 분리, 매 요청 권한 확인
- [ ] JWT alg 명시 검증(none 거부) + 서명 키 시크릿 관리
- [ ] 로그인 rate limit + 균일 응답(사용자 열거 방지)
- [ ] 쿠키 HttpOnly+Secure+SameSite / 토큰 localStorage 회피
- [ ] 비밀 비교 상수시간(compare_digest)
- [ ] 외부 로그인은 IdP 위임(직접 OAuth 서버 0)
- [ ] [심각] 거부 결정은 리스크와 함께 기록

## 점검 주기 (부패 중간 — 반기)

- OAuth/OIDC 권장 변화·패스키(WebAuthn) 표준 진척 확인
- 의존 인증 라이브러리 CVE 점검
