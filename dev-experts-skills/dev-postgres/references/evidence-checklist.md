# evidence + 출고 전 체크리스트

## 실증·출처

- **PostgreSQL 18 Release Notes** (postgresql.org/docs/release/18.0, 18.0 GA **2025-09-25**) — 버전 라벨의 1차 출처. 19는 2026-06 현재 미출시. 신규 사실:
  - **비동기 I/O(AIO)**: `io_method`(기본 `worker`, Linux 5.1+는 `io_uring`, 과거는 `sync`)·`pg_aios` 뷰, seq/bitmap scan·vacuum에서 최대 3배 읽기 향상 → 정량 기준 표 근거.
  - **B-tree skip scan**: 선행 카디널리티 낮고 후행이 `=`면 플래너가 선행 distinct를 건너뜀(자동·`=` 한정, 범위엔 무효) → 안티패턴 2 보강(순서 설계는 여전히 기본).
  - **`uuidv7()` 내장 + pg_upgrade 통계 보존**: 시간순 UUID로 인덱스 지역성↑, 업그레이드 직후 성능 침체 제거.
- **Sentry "Transaction ID Wraparound in Postgres" (2015, 공식 블로그 포스트모템)** — SKILL.md 실전 케이스 원 출처. autovacuum 지연 → XID 고갈 → 쓰기 거부 → single-user 모드 복구의 실제 기록.
- **공식 문서**: "Routine Vacuuming"(wraparound 메커니즘), "Using EXPLAIN" — 노드 해석의 1차 출처. shared_buffers 25% 권고는 공식 "Resource Consumption" 문서.
- **Markus Winand, *Use The Index, Luke*** — 복합 인덱스 순서·함수 감쌈·OFFSET 비용·keyset의 표준 교과서(use-the-index-luke.com 무료 공개).
- **Dimitri Fontaine, *The Art of PostgreSQL*** — "DB가 잘하는 일은 DB에게"(앱에서 루프 돌며 집계하지 말 것) 철학의 출처.
- FK에 자동 인덱스 없음: 공식 문서 "Foreign Keys" — referencing 쪽 인덱스는 명시 생성 필요.
- 오픈소스 차용 표기: alirezarezvani database-designer류(VoltAgent 색인)는 스키마 생성 중심 — **역흡수**: EXPLAIN 기반 처방 루프·연결 예산표·XID 모니터링 같은 운영 규율 부재가 본 스킬 차별점.

## 출고 전 체크리스트 (쿼리·DDL 변경 시)

- [ ] 처방 전후 EXPLAIN (ANALYZE, BUFFERS) 비교가 기록됐다
- [ ] 인덱스 추가 시: 복합 순서가 등호→범위, CONCURRENTLY 사용(운영)
- [ ] 인덱스 추가 시: 한 달 후 idx_scan 확인 일정 인지(안 쓰면 제거)
- [ ] WHERE 절에 컬럼 감싼 함수·캐스트 없음 (`sql_check.py` 0건)
- [ ] 페이지네이션은 keyset (OFFSET이면 명시 사유)
- [ ] 트랜잭션 안에서 외부 I/O 호출 없음
- [ ] 신규 FK에 referencing 인덱스 검토함
- [ ] 대량 DELETE/UPDATE 후 VACUUM (ANALYZE) 실행
- [ ] 연결 예산표가 현실과 일치 (워커·풀 변경 시 갱신)
- [ ] 설정 변경은 1개씩 + 전후 관측

## 점검 주기 (부패 중간 — 반기)

- PG 메이저 버전 vs 라벨 (현 18.x, 19 GA 시점 확인) — release notes의 플래너·vacuum 변경만
- pg_stat_statements 상위 10 쿼리 리뷰 + 안 쓰는 인덱스 정리
- XID age·n_dead_tup 경보가 실제 동작하는지
