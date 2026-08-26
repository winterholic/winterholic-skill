# EXPLAIN 읽기·인덱스 유형 선택·keyset 상세 (SKILL.md 비중복)

## EXPLAIN 노드 빠른 해석표

| 노드 | 뜻 | 문제 신호 |
|---|---|---|
| Seq Scan | 전체 읽기 | 대형 테이블 + Filter에서 대부분 제거 → 인덱스 후보 |
| Index Scan | 인덱스로 행 위치 찾아 테이블 접근 | rows 많으면 랜덤 I/O 폭증 — 차라리 Seq가 빠를 수도(플래너가 보통 옳다) |
| Index Only Scan | 테이블 안 감(인덱스만으로 응답) | 최상 — SELECT 컬럼이 인덱스에 다 있을 때. `Heap Fetches` 크면 vacuum 부족 |
| Bitmap Heap Scan | 인덱스로 후보 모아 한 번에 테이블 접근 | 중간 선택도에서 정상 — 이상 아님 |
| Nested Loop | 바깥 행마다 안쪽 반복 | 바깥 rows 추정이 틀려 실제 수만 번 돌면 재앙 — 통계 문제 |
| Hash Join / Merge Join | 대량 조인 표준 | work_mem 부족 시 디스크 spill (`Batches > 1`) |
| Sort | 정렬 | `Sort Method: external merge Disk` = work_mem 부족 또는 인덱스로 정렬 대체 검토 |

읽는 우선순위(SKILL.md 워크플로우 2의 상세): **추정 rows vs actual rows가 10배+ 어긋나면** 다른 모든 분석보다 `ANALYZE <table>` 먼저 — 플래너가 장님인 상태의 계획은 논할 가치가 없다.

## 인덱스 유형 선택

| 유형 | 맞는 곳 | 메모 |
|---|---|---|
| B-tree (기본) | =, <, >, BETWEEN, ORDER BY | 90%는 이것. 복합 순서는 SKILL.md #2 |
| 부분 인덱스 | `WHERE deleted_at IS NULL` 같은 고정 조건 | 작고 빠름 — "활성 행만 조회" 패턴에 최적 |
| 표현식 인덱스 | `ON (lower(email))` | 쿼리도 똑같은 표현식이어야 탄다 |
| GIN | JSONB 포함 검색, 배열, pg_trgm(부분 문자열) | 쓰기 비용 큼 — 검색 패턴 확정 후 |
| BRIN | 물리 순서와 상관 높은 컬럼(시계열 append) | 초소형 인덱스 — 거대 시계열 테이블의 base_date에 검토 가치 |
| covering (`INCLUDE`) | Index Only Scan 만들기 | 키엔 안 쓰지만 SELECT에 필요한 컬럼 동봉 |

- `CREATE INDEX CONCURRENTLY`가 운영 기본(쓰기 락 없음, 대신 2배 느리고 실패 시 INVALID 잔재 — `\d`로 확인 후 재시도).
- FK 컬럼은 자동 인덱스가 **없다** — JOIN·CASCADE 삭제 느림의 단골 원인. FK 만들면 인덱스 검토가 세트.

## keyset 페이지네이션 구현 상세

```sql
-- 첫 페이지
SELECT code, base_date, close FROM candles
WHERE code = :code
ORDER BY base_date DESC LIMIT 50;

-- 다음 페이지 (커서 = 마지막 행의 base_date)
SELECT code, base_date, close FROM candles
WHERE code = :code AND base_date < :last_date
ORDER BY base_date DESC LIMIT 51;   -- +1행 트릭: 51개 오면 다음 페이지 존재
```

- 정렬 키가 유일하지 않으면 타이브레이커 추가: `ORDER BY base_date DESC, id DESC` + 행 비교 `(base_date, id) < (:d, :id)` — PG의 행 비교 문법이 이걸 한 줄로 만든다.
- 커서 인코딩(API 노출용)은 dev-rest-api-design 소관 — 여기선 키 값 자체가 커서.
- 제약: 임의 페이지 점프 불가(1→7페이지) — 그 요구가 진짜면 OFFSET+상한(예: 최대 100페이지)으로 명시 절충.

## 락·격리 빠른 진단

```sql
-- 지금 누가 누구를 막나
SELECT blocked.pid AS blocked_pid, blocking.pid AS blocking_pid,
       blocked.query AS blocked_query, blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid AND NOT bl.granted
JOIN pg_locks gl ON gl.locktype = bl.locktype AND gl.relation = bl.relation AND gl.granted
JOIN pg_stat_activity blocking ON blocking.pid = gl.pid;
```

- deadlock detected: PG가 한쪽을 죽여서 해소해준 것 — 로그의 두 쿼리를 보고 **락 획득 순서를 통일**(항상 작은 id 먼저)이 근본 처방.
- 기본 격리 Read Committed에서 "읽고 계산해서 쓰기"는 경합 시 갱신 유실 — `SELECT ... FOR UPDATE` 또는 원자 UPDATE(`SET v = v + 1`)로.
