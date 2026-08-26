# 흐름·토큰 심화 — 세션 vs JWT·OAuth/OIDC·rotation·RBAC (SKILL.md 비중복)

## 세션 vs JWT 결정표

| 기준 | 세션(서버 상태) | JWT(무상태) |
|---|---|---|
| 즉시 취소(로그아웃·권한변경) | ◎ 서버에서 삭제 | ✕ 만료까지 유효(블랙리스트로 우회 시 무상태 이점 소멸) |
| 수평 확장 | 공유 저장소 필요(Redis) | ◎ 검증만(공유 불요) |
| 모바일·다중 클라이언트 | 쿠키 외엔 불편 | ◎ 헤더로 자연스러움 |
| 페이로드 노출 | 서버에만 | 클라가 디코드 가능(민감정보 금지 — 서명일 뿐 암호화 아님) |
| 구현 단순성 | ◎ (프레임워크 세션) | 토큰·갱신·저장 설계 필요 |

기본 권장: **단일 웹앱·즉시 취소 중요 → 세션** / **다중 클라이언트·확장·API → JWT(짧은 access + refresh)**. "JWT가 현대적"은 선택 근거가 아니다(안티패턴 2).

## OAuth2/OIDC 흐름 (authorization code + PKCE — 현행 표준)

```
1. 앱 -> IdP 로그인 페이지로 리다이렉트 (+ code_challenge=PKCE)
2. 사용자가 IdP에서 인증 (앱은 비밀번호를 절대 안 봄 - 핵심 가치)
3. IdP -> 앱 콜백으로 authorization code
4. 앱(백엔드) -> IdP에 code + code_verifier 교환 -> access/id/refresh token
5. id token(OIDC, JWT)으로 신원 확인, access token으로 자원 접근
```

- **PKCE는 이제 SPA·모바일뿐 아니라 전부에 권장**(OAuth 2.1). implicit flow는 폐기.
- 직접 OAuth **서버** 구현 금지 — IdP(소셜 로그인·Keycloak·Auth0류) 위임. 직접 OAuth **클라이언트**(위 흐름 소비)는 라이브러리로.
- id token(누구인가, OIDC) vs access token(무엇을 할 수 있나, OAuth) 구분 — 혼용이 흔한 오해.

## refresh rotation + 재사용 탐지 (안티패턴 3 상세)

```
저장: refresh_tokens(token_hash, user_id, family_id, used boolean, expires_at)
사용 시:
  1. 받은 refresh가 used=true면 -> 탈취! family_id 전체 무효화 + 경보 (재사용 탐지)
  2. 정상이면 -> 옛 것 used=true + 새 access/refresh 발급(같은 family_id)
```

- family_id: 한 로그인 세션의 갱신 사슬 — 탈취 시 그 사슬만 끊는다(다른 기기 로그인 유지).
- 회전의 동시 요청 race(같은 refresh로 2요청 동시): 짧은 grace window 또는 advisory lock(dev-postgres) — 정상 클라가 재시도 타이밍에 걸리지 않게.
- refresh도 해시 저장(access는 보통 무상태라 저장 안 함, refresh는 취소 위해 저장).

## 비밀번호 저장 표준 (직접 구현 금지의 핵심)

```python
from argon2 import PasswordHasher
ph = PasswordHasher()                    # 솔트·작업계수 내장
hash = ph.hash(password)                 # 저장
ph.verify(hash, password)                # 검증 (틀리면 예외)
if ph.check_needs_rehash(hash): ...      # 작업계수 상향 시 자동 마이그레이션
```

- 솔트·페퍼·반복을 직접 조합하지 않는다 — 라이브러리가 파라미터를 해시 문자열에 담아 관리.
- 비밀번호 정책: 길이(8+ 권장 12+) 우선, 복잡도 강제는 역효과(NIST 800-63B는 복잡도 규칙·강제 주기변경 폐지 권고) — 유출 목록 대조(Pwned Passwords)가 더 효과적.

## RBAC 경량 모델

```
roles: viewer < editor < admin (또는 권한 비트)
permissions: 리소스 x 동작 (candle:read, watchlist:write)
확인: 매 요청 has_permission(user, resource, action) - 인증과 분리(안티패턴 4)
```

- 단순하면 역할 enum 1개로 시작, 세분화는 권한이 역할에 안 맞을 때(YAGNI). 속성 기반(ABAC)은 규모가 정당화할 때.
- 권한 변경 즉시 반영이 필요하면 토큰 클레임이 아니라 서버 조회(JWT #2 트레이드오프와 연결).
