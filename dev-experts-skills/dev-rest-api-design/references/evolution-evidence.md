# 진화 전략·실증·체크리스트

## 버저닝 전략 비교

| 전략 | 형태 | 평가 |
|---|---|---|
| URL 메이저 | `/v1/...` | **기본값** — 명시적, 라우팅 단순, 캐시 친화 |
| 헤더 버전 | `Accept: ...;version=2` | URL 불변이 장점이나 디버깅·문서·캐시 불편 — 소규모 비추 |
| 계정 고정 + 변환 레이어 | Stripe 방식 — 계정마다 버전 고정, 서버가 구버전 응답으로 변환 | 최상의 소비자 경험, 최대 구현비 — 대형 플랫폼용 |
| 무버전 + 추가만 | 버전 없이 호환 유지 | 내부 API 현실 기본값 — breaking이 정말 필요해질 때 /v1을 그때 도입하면 늦다. **처음부터 /v1을 붙여두는 비용은 0** |

결론: `/v1` 접두를 첫날 붙이고, 추가-만(additive-only) 규율로 v2를 영원히 미루는 것이 소규모의 정답.

## 폐기(deprecation) 절차

1. 신규 필드/엔드포인트 병행 추가 (구버전 유지)
2. 문서 + 응답 헤더 표시: `Deprecation: @<unix-timestamp>`(폐기 시점, RFC 9745 — 값은 boolean이 아니라 Date), `Sunset: <RFC 1123 날짜>`(제거 예정일, RFC 8594). 두 헤더는 짝 — Deprecation은 "언제부터 권장 안 함", Sunset은 "언제 사라짐". (구버전 관례인 `Deprecation: true`는 RFC 9745 이전 드래프트 형식 — 표준은 Date)
3. 사용량 관측 — 구버전 호출이 0이 되거나 예고 기한 도달
4. 제거는 메이저 이벤트로 (CHANGELOG·알림)

소규모(클라이언트가 자기 프론트뿐)의 축약판: 병행 1배포 주기 + 클라 전환 확인 후 제거 — 단계 자체는 같다.

## 실증·출처

- **Stripe "APIs as infrastructure: future-proofing Stripe with versioning" (2017, 공식 블로그, stripe.com/blog/api-versioning)** — 계정 고정 버저닝·변환 레이어·추가-만 규율. SKILL.md 실전 케이스 원 출처. (URL 실확인)
- **Stripe "Designing robust and predictable APIs with idempotency" (2017)** — Idempotency-Key 패턴 원전 (dev-data-engineering evidence와 공유).
- **RFC 9110 (HTTP Semantics)** — 메서드 멱등성 표(GET/PUT/DELETE 멱등, POST 비멱등)·상태코드 의미의 1차 출처.
- **RFC 8594 (The Sunset HTTP Header Field)** — 리소스 제거 예정일을 알리는 헤더 표준.
- **RFC 9745 (The Deprecation HTTP Field, 2025)** — `Deprecation` 헤더의 1차 표준. 값은 구조화 필드 Date(예: `Deprecation: @1688169599`)이며 boolean `true`가 아님. Sunset과 짝으로 권장. (실확인 — rfc-editor.org/rfc/rfc9745)
- **GitHub REST API 문서** — 커서 페이지네이션(`Link` 헤더 방식)·enum 확장 정책("clients must handle unknown values") 실전 예.
- 오픈소스 차용 표기: alirezarezvani api-design-reviewer(REST 린트 접근 참고, 본문 비복사). **역흡수**: breaking 판별표·"기본 limit 변경도 breaking"·하위 액션 3조건 같은 판단 규칙 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (계약 추가·변경 시)

- [ ] 엔드포인트 표가 작성·리뷰됨 (구현 전)
- [ ] URL에 동사 없음 (`api_lint.py` 0건, 하위 액션은 3조건 통과 기록)
- [ ] 모든 목록에 limit 상한 + 봉투(data/next_cursor)
- [ ] 에러가 표준 스키마 + 안정 code (message 매칭 분기 없음)
- [ ] 시각 ISO 8601 UTC / 금액 정수 최소 단위
- [ ] 변경분이 breaking 판별표 통과 (breaking이면 병행 전략 명시)
- [ ] /v1 접두 존재
- [ ] 부수효과 POST에 멱등키 수용 (해당 시)
- [ ] OpenAPI(/docs)와 계약 표 일치 확인
- [ ] 429에 Retry-After (rate limit 있는 경우)

## 점검 주기 (부패 느림 — 연 1회)

- 실 호출 로그로 규약 위반(거대 limit 요청·미지 에러 code 의존) 표본 확인
- ledger의 API 관련 삽질 3회 패턴 → 판별표·체크리스트 반영
