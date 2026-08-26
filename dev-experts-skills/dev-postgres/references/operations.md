# 운영 — autovacuum 조율·연결 예산·관측 쿼리 (SKILL.md 비중복)

## 연결 예산표 양식 (안티패턴 5의 실행 도구)

| 소비자 | 인스턴스 | 풀 크기 | 소계 |
|---|---|---|---|
| API 서버 (uvicorn) | 2 워커 | 5+5 overflow | 20 |
| collector 배치 | 1 | 5 | 5 |
| 수동 psql·관리 | - | - | 5 |
| **합계** | | | **30** / max_connections 100 |

- 합계가 max_connections의 70%를 넘으면: 풀 줄이기 → 그래도 부족하면 pgbouncer(transaction 모드) 도입 검토 — max_connections 상향은 마지막 수단(연결당 메모리 비용).
- 예산표는 README·compose 옆에 파일로 — "누가 연결을 먹는가"를 코드로 답하지 않게.

## autovacuum 조율 (끄지 말고 맞추기)

```sql
-- 거대·고변경 테이블만 테이블 단위로 민감하게
ALTER TABLE candles SET (
  autovacuum_vacuum_scale_factor = 0.02,   -- 기본 0.2(20%) -> 2%: 4천만 행이면 80만 dead에서 발동
  autovacuum_analyze_scale_factor = 0.01
);
```

- 기본 scale_factor 0.2는 소형 테이블용 기본값이다 — 행수에 비례해 방치 구간이 커진다(Sentry 케이스의 기술적 핵심).
- 대량 DELETE/UPDATE 직후엔 기다리지 말고 `VACUUM (ANALYZE) <table>` 수동 1회.
- 모니터링 최소 2종:
  ```sql
  -- dead tuple 비대화
  SELECT relname, n_live_tup, n_dead_tup FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;
  -- XID wraparound 거리 (10억 넘으면 경보 - 2^31의 절반)
  SELECT datname, age(datfrozenxid) FROM pg_database ORDER BY 2 DESC;
  ```

## 관측 쿼리 모음 (copy-paste)

```sql
-- 느린 쿼리 상위 (pg_stat_statements 확장 필요 - shared_preload_libraries)
SELECT calls, mean_exec_time::int AS ms, query
FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

-- 안 쓰는 인덱스 (제거 후보 - 한 달 이상 관측 후)
SELECT schemaname, relname, indexrelname, idx_scan,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes WHERE idx_scan = 0 ORDER BY pg_relation_size(indexrelid) DESC;

-- 테이블·인덱스 크기
SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) AS total
FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 10;

-- 캐시 적중률 (0.99 미만 지속이면 shared_buffers/쿼리 패턴 점검)
SELECT sum(blks_hit)::float / nullif(sum(blks_hit) + sum(blks_read), 0) FROM pg_stat_database;

-- 현재 활동·오래 걸리는 쿼리
SELECT pid, now() - query_start AS dur, state, left(query, 60)
FROM pg_stat_activity WHERE state != 'idle' ORDER BY dur DESC;
```

## 설정 기본값 (홈서버 컨테이너 규모)

| 설정 | 출발점 | 메모 |
|---|---|---|
| shared_buffers | 컨테이너 메모리의 25% | 호스트 RAM 아님(SKILL.md 사용자 환경) |
| work_mem | 16MB | 세션·정렬 노드마다 곱해진다 — 큰 값 전역 설정 금지, 배치 세션만 `SET work_mem` |
| maintenance_work_mem | 256MB | VACUUM·CREATE INDEX 가속 |
| effective_cache_size | 컨테이너 메모리의 50~75% | 할당 아님 — 플래너 힌트일 뿐 |
| wal_level / 백업 | dev-backup-dr 소관 | 여기선 건드리지 않음 |

설정 변경은 한 번에 1개 + 변경 전후 관측(캐시 적중률·느린 쿼리) — 튜닝 워크플로우와 같은 규율.
