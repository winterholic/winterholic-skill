# evidence + 출고 전 체크리스트

## 실증·출처

- **Karwin, *SQL Antipatterns*** — Jaywalking(CSV 컬럼)·EAV·Phantom Files 등 안티패턴 1·3의 표준 카탈로그. 초판 2010(ISBN 9781934356555), 현행 *Volume 1* 2022 개정판(ISBN 9781680508987, PostgreSQL/Python 예제로 갱신) — https://pragprog.com/titles/bksap1/sql-antipatterns-volume-1/ (저자/출판사 공식 페이지, 2026-06 확인).
- **Kleppmann, *Designing Data-Intensive Applications* Ch.2** — 관계형/문서 모델 트레이드오프·스키마 유연성의 실제 비용. 공식 책 사이트 https://dataintensive.net/ (저자 운영, 2026-06 확인).
- **Stripe API 공식 문서 — `amount`** — "positive integer in the smallest currency unit"로 정수 최소 단위 강제. 실전 케이스(float 금지)의 업계 표준 근거. https://docs.stripe.com/api/charges/object (공식 API 레퍼런스, 2026-06 확인). 참고: KRW·JPY는 zero-decimal 통화라 곱셈 없이 그대로 정수 — https://docs.stripe.com/currencies (사용자의 원 단위 bigint 선택과 일치).
- **RFC 9562 (IETF, 2024-05) — UUIDv7** — 안티패턴 2의 "UUIDv7류 — 시간순 정렬 가능" 권고의 1차 출처. 48비트 Unix 밀리초 타임스탬프를 상위에 배치해 생성 시각 순으로 정렬되는 표준 UUID 버전을 정의(랜덤 UUIDv4의 B-tree 인덱스 분산 삽입 문제를 해소). RFC 4122를 대체. https://www.rfc-editor.org/rfc/rfc9562.html (IETF 표준 문서, 2026-06 확인).
- **PostgreSQL 18 릴리스 노트 — 네이티브 `uuidv7()`** — PG 18(2025-09 GA)부터 `uuidv7()` 내장 함수 제공. 위 RFC 9562 권고를 확장 없이 DB 기본값으로 쓸 수 있게 함(이전엔 `gen_random_uuid()`=v4 또는 확장 필요). 타입 표의 `bigint identity / uuid` 선택을 2026년 기준으로 갱신. https://www.postgresql.org/docs/current/release-18.html (E.5.3.4 항목, 공식 릴리스 노트, 2026-06 확인).
- **PostgreSQL 공식 문서** — timestamptz 권고·EXCLUDE 제약·identity 컬럼. 식별자 컬럼은 `GENERATED AS IDENTITY`가 SQL 표준 준수 현행 권고이고 `serial`은 레거시(공식적으로 identity 권장) — https://www.postgresql.org/docs/current/sql-createtable.html (2026-06 확인).
- **RFC 9562 — UUID (2024-05)** — UUIDv7의 시간순 정렬 보장(48bit Unix ms 타임스탬프 + 74bit 랜덤)의 1차 출처. 안티패턴 2의 "UUIDv7류 시간순 정렬" 주장 근거 — https://www.rfc-editor.org/info/rfc9562/ (IETF 표준, 2026-06 확인). PostgreSQL은 18부터 네이티브 `uuidv7()` 제공(그 이전 버전은 확장/앱 생성 필요 — 확인 필요).
- 오픈소스 차용 표기: 스키마 설계 자료 다수(색인 인지, 본문 비복사). **역흡수**: 이력 2형 선택 기준("바뀌었다 vs 일어났다")·비정규화 동기화 책임 1곳 규칙·DDL 기계 검사 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (스키마 출고 시)

- [ ] 컬럼 표 작성 (타입·NULL 사유·제약)
- [ ] 금액 numeric/정수, 시각 timestamptz (`schema_check.py` 0건)
- [ ] 대리 PK + 자연키 UNIQUE 쌍
- [ ] 불변식이 제약으로 번역됨 (UNIQUE/CHECK)
- [ ] 전 FK + referencing 인덱스
- [ ] NULL에 의미 없음 (상태는 명시 컬럼)
- [ ] 이력 판정 기록 (보존/덮어쓰기 + 근거)
- [ ] 비정규화는 측정 근거 + 동기화 책임 1곳
- [ ] 변경이면 호환 단계(추가→전환→제거) 계획

## 점검 주기 (부패 느림 — 연 1회)

- 고아 행·중복 검사 쿼리 1회 실행 (제약 누락분 색출)
- ledger의 스키마 후회 3회 패턴 → 타입 표·판정 질문 보강
