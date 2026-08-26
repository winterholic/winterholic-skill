# evidence + 출고 전 체크리스트

> 장애·실증 사례 본문은 같은 폴더 `evidence.md`(Basecamp int 고갈 · NOT IN NULL 공집합 · 깊은 OFFSET 폭주). 이 파일은 출처 색인 + 출고 체크 + 점검 주기.

## 실증·출처

- **ISO/IEC 9075:2023 (SQL:2023)** — 표준 SQL의 현행 판. 3치 논리(TRUE/FALSE/UNKNOWN)·NULL 비교 의미·`NOT IN` 공집합 동작의 규범 출처(안티패턴 5, `evidence.md` §2). 모든 엔진 공통 명세라 "버그 아닌 명세"의 근거.
- **PostgreSQL 18 공식 문서** (postgresql.org/docs/18, GA 2025-09) — EXPLAIN/EXPLAIN ANALYZE 출력 형식·실행계획 어휘(Seq Scan·Index Scan·추정 vs 실제 행)의 1차 출처(워크플로우·안티패턴 1). PG 18 신규 `uuidv7()`(시간 정렬 UUID)는 INT PK 고갈/keyset 논의의 현행 대안 — 확인 필요: 채택 시 PG 18+ 전제.
- **MySQL 8.4 LTS 공식 문서** (dev.mysql.com/doc/refman/8.4, LTS 2032-04까지) — 방언·EXPLAIN 형식 비교 기준. **확인됨**: MySQL 8.0은 2026-04 EOL — 신규/유지보수는 8.4 LTS 또는 9.x 혁신 라인 전제. 깊은 OFFSET 비용 O(N)·AUTO_INCREMENT 한도 점검의 엔진별 차이 출처.
- **Basecamp 공식 포스트모템** (2018-11-08, DHH 사과문 포함) — int PK 고갈 5시간 장애의 1차 실증(안티패턴 7, `evidence.md` §1).
- **Markus Winand, *Use The Index, Luke* / *SQL Performance Explained*** (use-the-index-luke.com) — 깊은 OFFSET DoS·인덱스 선두 컬럼·keyset 페이지네이션의 표준 해설(안티패턴 4, `evidence.md` §3).
- 오픈소스 차용 표기: SQL 튜닝 가이드류 다수(색인 인지, 본문 비복사). **역흡수**: "EXPLAIN 없이 추측 금지" 규율의 명시화·NOT IN/NULL 공집합의 기계적 회피(NOT EXISTS 치환)·엔진 불명 시 4요소 질의 절차 — 본 스킬 차별점.

## 출고 전 체크리스트 (SQL/쿼리 출고 시)

- [ ] 느린 쿼리는 EXPLAIN (ANALYZE) 실측 후 진단 — 추측 튜닝 없음
- [ ] `NOT IN (서브쿼리)`에 NULL 가능성 검토 → 의심 시 `NOT EXISTS`로 치환
- [ ] 목록 API는 OFFSET 대신 keyset 페이지네이션 (정렬키 + 고유키 복합 인덱스)
- [ ] 신규 테이블 PK는 BIGINT(또는 PG 18 uuidv7 등) — INT PK 잔존분은 사용률 모니터링
- [ ] 인덱스 선두 컬럼이 술어/조인/정렬과 정합 (선택도·순서 확인)
- [ ] 집계·정산 쿼리에 NULL/3치 논리 함정 점검 (조용히 틀리는 부류)
- [ ] 대상 엔진(PG/MySQL) 방언·플랜 형식 확정 후 작성
- [ ] 트랜잭션 경계·잠금 시간 의식 (장시간 트랜잭션 내 외부 대기 없음)

## 점검 주기 (부패 느림 — 연 1회)

- 엔진 메이저 추적: PostgreSQL 연 1회 메이저(현 18, 19는 2026 후반 예정) · MySQL LTS(현 8.4, 8.0은 2026-04 EOL 완료) — EXPLAIN 출력·신규 함수(uuidv7 등)만 라벨 갱신
- SQL 표준 개정(현 SQL:2023) — 차기 개정 전까지 3치 논리·NULL 의미는 불변(원칙은 버전보다 오래 감)
- `evidence.md`의 장애 사례는 역사적 사실이라 갱신 불요 — 출처 링크 유효성만 연 1회 확인
