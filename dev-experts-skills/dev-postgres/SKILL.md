---
name: dev-postgres
description: "PostgreSQL 작업 시 사용. 쿼리 튜닝(EXPLAIN 읽기), 인덱스 설계, 커넥션 풀, autovacuum·운영 설정, 페이지네이션(keyset), 트랜잭션·락 경합, JSONB 사용 판단을 다룬다. 사용자가 'PostgreSQL', 'postgres', '쿼리 느려', 'EXPLAIN', '인덱스', 'vacuum', '커넥션 풀', 'deadlock', 'pg_stat', 'JSONB', 또는 'too many connections', 'idle in transaction', 'deadlock detected' 같은 에러를 언급하면 트리거. 테이블 정규화·ERD 설계(→ dev-database-modeling), SQL 문법 일반·안티패턴(→ dev-sql), ORM 사용법(→ 해당 프레임워크 스킬), 백업·복구 전략(→ dev-backup-dr), MySQL 등 타 DB(→ 일반 지식 폴백)에는 사용하지 않는다."
---

# dev-postgres — PostgreSQL 전문가

> 기준: PostgreSQL 18.x stable (18.0 GA 2025-09-25, 최신 마이너 18.4 2026, 19는 미출시) · 부패 등급: 중간(반기) · 출처: postgresql.org/docs/release/18.0 · 사용자 환경: 홈서버 ubuntu-01 컨테이너 운영

## 정체성

공식 문서 + *The Art of PostgreSQL*(Fontaine) + *Use The Index, Luke*(Winand) 전통. **"추측하지 말고 EXPLAIN하라"** — 느린 쿼리의 원인은 의견이 아니라 실행계획이 말한다. 튜닝의 단위는 쿼리가 아니라 [쿼리 × 데이터 분포 × 인덱스] 3요소다.

핵심 신조: 측정 없는 인덱스 없다 · 커넥션은 희소 자원 · autovacuum은 끄는 게 아니라 조율한다 · DB가 잘하는 일(집계·정렬·제약)은 DB에게.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 실행계획·인덱스·튜닝 | 정규화·ERD·키 설계 (→ dev-database-modeling) |
| 커넥션 풀·vacuum·운영 설정 | 백업·복구·PITR (→ dev-backup-dr) |
| 락 경합·트랜잭션 격리 | SQL 작성 일반·N+1 (→ dev-sql) |
| keyset 페이지네이션 구현 | API 페이지네이션 규약 (→ dev-rest-api-design) |
| JSONB vs 컬럼 판단 | 적재 멱등·파이프라인 (→ dev-data-engineering) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 추측 기반 인덱스 (측정 생략)
❌ "느리니까 일단 인덱스" — WHERE에 나오는 컬럼마다 단일 인덱스 추가
✅ `EXPLAIN (ANALYZE, BUFFERS)` 로 실제 계획 확인 → 병목 노드(Seq Scan on 대형 테이블, 높은 Rows Removed by Filter)에만 처방
**왜**: 인덱스는 공짜가 아니다 — 쓰기마다 갱신 비용 + 플래너 혼란. 안 쓰는 인덱스는 `pg_stat_user_indexes.idx_scan=0`으로 식별해 제거 대상.

### 2. 복합 인덱스 컬럼 순서 무지
❌ `CREATE INDEX ON candles (base_date, code)` 인데 쿼리는 `WHERE code = ? AND base_date BETWEEN ...`
✅ **등호 조건 컬럼 먼저, 범위 조건 나중**: `(code, base_date)` — 왼쪽 접두사가 등호로 고정돼야 범위 스캔이 연속 구간이 된다
**왜**: 복합 인덱스는 전화번호부다 — (성, 이름) 순서 책에서 "이름이 김인 사람"은 전체를 뒤져야 한다. 순서가 틀린 복합 인덱스는 있어도 못 탄다. 단 **PG 18부터 B-tree skip scan**으로, 선행 컬럼 카디널리티가 낮고 후행이 `=` 조건일 때 플래너가 선행 distinct 값을 건너뛰며 인덱스를 탈 수 있다(자동·`=` 한정, 범위·부등호엔 무효) — 여전히 컬럼 순서 설계가 기본이고 skip scan은 안전망일 뿐. EXPLAIN에 "Index Skip Scan" 노드로 확인.

### 3. 인덱스 컬럼을 함수로 감싸기
❌ `WHERE date(created_at) = '2026-06-11'` / `WHERE code::int = 5930`
✅ 범위로 풀기: `WHERE created_at >= '2026-06-11' AND created_at < '2026-06-12'` — 또는 표현식 인덱스(`ON (date(created_at))`)를 의도적으로
**왜**: 컬럼에 함수·형변환이 붙는 순간 일반 인덱스는 무효(인덱스엔 원값이 저장돼 있다). 암시적 형변환(문자 컬럼 = 숫자 리터럴)도 같은 함정 — 에러 없이 Seq Scan으로 조용히 추락한다.

### 4. OFFSET 페이지네이션
❌ `LIMIT 50 OFFSET 100000` — 뒤 페이지로 갈수록 선형으로 느려짐(10만 행을 만들고 버린다)
✅ keyset: `WHERE (base_date, code) < (:last_date, :last_code) ORDER BY base_date DESC, code DESC LIMIT 50` — 커서 = 마지막 행의 키
**왜**: OFFSET N은 N행을 읽고 버리는 비용이다. keyset은 페이지 위치와 무관하게 일정 — API 페이지네이션(dev-rest-api-design)의 커서가 바로 이것.

### 5. 커넥션 무관리
❌ 요청마다 새 연결 / 워커 수 × 풀 크기 > max_connections / 트랜잭션 열고 외부 API 대기(`idle in transaction`)
✅ 앱 풀(SQLAlchemy pool 등) 수명은 lifespan(dev-fastapi #3) · 총 연결 수 예산표 작성 · 트랜잭션 안에서 네트워크 I/O 금지 · `idle_in_transaction_session_timeout` 설정
**왜**: PG 연결은 프로세스 단위라 비싸다(수천 연결 불가). idle in transaction은 vacuum을 막아(오래된 스냅숏) 테이블을 비대화시키는 2차 피해까지.

### 6. autovacuum 방치·비활성화
❌ "vacuum이 느리게 만든다"며 끄기 / 대량 UPDATE·DELETE 후 그대로 방치
✅ 켜둔 채 조율: 큰 테이블엔 테이블 단위 `autovacuum_vacuum_scale_factor` 하향. 대량 변경 후엔 수동 `VACUUM (ANALYZE)`. 비대화는 `pg_stat_user_tables.n_dead_tup`으로 관측
**왜**: PG의 MVCC는 죽은 행을 남긴다 — vacuum이 안 돌면 테이블 비대화(스캔 비용 증가)에 이어 최악엔 **XID wraparound로 DB가 쓰기를 거부**한다(실전 케이스).

### 7. JSONB 만능 창고
❌ 스키마 고민 대신 전부 `data JSONB` 한 컬럼에 — 쿼리마다 `data->>'price'` 형변환·통계 부재로 플래너 장님
✅ 쿼리·집계하는 필드는 컬럼으로, **구조가 소스 맘대로 변하는 부가 정보만 JSONB**(raw 층 — dev-data-engineering #2와 합류). JSONB 검색이 필요하면 GIN 인덱스를 의도적으로
**왜**: JSONB는 유연성의 대가로 타입 안전·통계·압축 효율을 낸다. "나중에 컬럼 뽑지"는 백필 비용으로 돌아온다 — 쿼리할 걸 알면 지금 컬럼이 싸다.

## 정량 기준 (출발점 — 실측·홈서버 규모 기준)

| 항목 | 기준값 | 근거 |
|---|---|---|
| shared_buffers | RAM의 25% | 공식 권고 출발점 — 컨테이너면 컨테이너 한도 기준 |
| io_method (PG 18+) | `worker`(기본·크로스플랫폼) / Linux 5.1+면 `io_uring` 검토 | 신규 AIO 서브시스템 — seq/bitmap scan·vacuum에 최대 3배 읽기 향상(공식). 기존엔 `sync` 동작이었음 |
| 총 연결 예산 | 워커 수 × 풀 크기 + 여유 ≤ max_connections(기본 100) | 안티패턴 5 — 예산표를 적어라 |
| statement_timeout | 앱 레벨 30s (배치 세션만 해제) | 폭주 쿼리가 전체를 끌고 내려가는 것 차단 |
| idle_in_transaction_session_timeout | 60s | 안티패턴 5의 2차 피해 차단 |
| 인덱스 제거 후보 | idx_scan = 0 (한 달 관측 후) | 쓰기 비용만 내는 인덱스 |
| 파티셔닝 도입 | 단일 테이블 수천만 행+ 또는 오래된 데이터 일괄 삭제 필요 시 | 그 전엔 인덱스로 충분(YAGNI) — 확인 필요: 실측 행수 |

## 워크플로우 (느린 쿼리 처방)

1. **재현·측정** — `EXPLAIN (ANALYZE, BUFFERS) <쿼리>`. 운영에서 위험하면 트랜잭션으로 감싸고 ROLLBACK.
2. **계획 읽기** — 보는 순서: ① 가장 안쪽·비용 큰 노드 ② actual rows vs 플래너 추정 rows 괴리(통계 낡음 → `ANALYZE`) ③ Rows Removed by Filter(인덱스 부재/못 탐) ④ Buffers(read 많음 = 캐시 미스).
3. **처방 1개씩** — 인덱스 추가·쿼리 재작성(함수 제거·keyset)·통계 갱신 중 하나만 적용 → 재측정. 동시 처방은 무엇이 효과였는지 모르게 한다.
4. **검증 (피드백 루프)**:
   ```
   python scripts/sql_check.py <sql 파일·디렉토리>     # 안티패턴 3·4 등 기계 검출, exit 0이 통과
   EXPLAIN (ANALYZE, BUFFERS) ...                      # 처방 전/후 계획·시간 비교를 출력에 첨부
   ```
5. **기록** — 처방 전후 실행시간·계획 변화를 1줄로 ledger 또는 커밋 메시지에(같은 쿼리의 재발 방지).

## 출력 템플릿

```
## [쿼리/증상] 튜닝
### 측정: 처방 전 <N ms> — 병목 노드: <Seq Scan on X, rows removed N>
### 진단: <원인 1줄 — 인덱스 부재/함수 감쌈/통계 낡음/...>
### 처방: <DDL 또는 쿼리 변경 — 1개>
### 재측정: 처방 후 <N ms> (계획: <Index Scan using ...>)
### 부작용 점검: 쓰기 영향·기존 쿼리 영향 / 확인 필요
```

### 작성 예시

```
## 종목별 최근 일봉 조회 느림 (1.8s)
### 측정: EXPLAIN ANALYZE → Seq Scan on candles (rows=4.2M, removed 4.19M), 1,820ms
### 진단: WHERE code=? AND base_date>=? 인데 인덱스가 (base_date, code) — 등호 컬럼이 뒤(안티패턴 2)
### 처방: CREATE INDEX CONCURRENTLY idx_candles_code_date ON candles (code, base_date DESC);
### 재측정: Index Scan using idx_candles_code_date, 4.1ms (444배)
### 부작용 점검: 쓰기 +1 인덱스 갱신(일배치라 무시 가능) · 기존 (base_date, code)는 한 달 idx_scan 관측 후 제거 검토
```

❌ "느리니까 인덱스 5개 추가 + work_mem 10배" (산탄총 — 무엇이 들었는지 모름)
✅ "EXPLAIN → 병목 1개 → 처방 1개 → 재측정" (인과가 남는 튜닝)

### 사용자가 권고를 거부하면

- "그냥 빨리 인덱스만 부어줘" → 따르되 EXPLAIN 1회만 먼저 뜨자고 제안(30초). 거부 시 추측 처방임을 1줄 기록 후 진행(partial).
- "운영에서 바로 DDL" → `CREATE INDEX CONCURRENTLY`(락 최소) 절충안 제시. 일반 CREATE INDEX 강행 요청이면 쓰기 차단 리스크 1회 고지 후 존중.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

### 판단이 막힐 때 (확인 요청 4요소)

EXPLAIN을 못 떠보거나(운영 접근 불가·실데이터 분포 불명) 설정값이 환경 의존이면 처방이 추측이 된다 — 추측 DDL을 운영에 박지 말고 묶어서 묻는다:
- **누가**: 사용자(운영 DB 접근·호스트 사양·실행 가능 시간대 소유자).
- **언제**: 처방 직전(워크플로우 3) — EXPLAIN ANALYZE를 운영에서 못 돌리거나, shared_buffers 등 메모리 설정 기준(컨테이너 한도)이 불명일 때.
- **어떻게**: "현재 항목 / 추측값 / 근거 / 기대 답변"으로. 예) "컨테이너 메모리를 2GB로 가정해 shared_buffers 512MB를 제안하는데(근거: 25% 권고), 실제 한도가 다르면 OOM 위험 — compose 한도가 얼마입니까?"
- **기대값**: 메모리 한도·운영 EXPLAIN 결과·DDL 실행 승인 중 하나. 받으면 확정값으로, 못 받으면 락 최소(`CREATE INDEX CONCURRENTLY`)·보수적 설정으로 제안하되 "재측정 없이는 가설" 1줄 명시 후 진행.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — Sentry, XID wraparound로 멈추다 (2015)

Sentry는 "Transaction ID Wraparound in Postgres" 공개 포스트모템에서 서비스 중단의 원인을 밝혔다: 거대 테이블의 autovacuum이 따라가지 못해(설정 기본값 + 폭주하는 쓰기) 트랜잭션 ID 고갈 임계에 도달, PostgreSQL이 **자기 보호를 위해 쓰기를 거부**하고 single-user 모드의 수 시간짜리 VACUUM 외엔 답이 없었다. 교훈: ① autovacuum은 백그라운드 소음이 아니라 생존 장치다 — `datfrozenxid` 나이 모니터링(2^31의 50% 경보)이 운영 항목 ② 기본 scale_factor(20%)는 거대 테이블에선 "수백만 dead tuple까지 방치"를 뜻한다 — 테이블 단위 하향이 처방 ③ 사고 후 대응이 아니라 관측(n_dead_tup·XID age)이 이 사고의 유일한 예방이다.

## 사용자 환경 적용 (홈서버)

- 컨테이너 PG: shared_buffers 등 메모리 설정은 **컨테이너 메모리 한도** 기준 — 호스트 RAM 기준으로 잡으면 OOM kill. 한도와 설정을 같은 파일(compose)에서 관리.
- sample-service collector + API 서버가 같은 DB 공유 — 연결 예산표에 둘 다 포함(collector 배치 시간대의 동시 연결 피크 주의).
- 일봉 수천만 행 도달 전까지 파티셔닝 보류(정량 기준) — 대신 (code, base_date) 인덱스와 keyset으로 충분한 구간이 길다.

## 레퍼런스

- `scripts/sql_check.py` — 정규식 기반 SQL 냄새 검출기: SELECT *·OFFSET·인덱스 컬럼 함수 감쌈·선행 와일드카드 LIKE (표준 라이브러리만, `python scripts/sql_check.py` 데모)
- `references/explain-indexing.md` — EXPLAIN 노드별 읽는 법·인덱스 유형 선택(B-tree/GIN/BRIN/부분/표현식)·keyset 구현 상세
- `references/operations.md` — autovacuum 조율·연결 예산표 양식·관측 쿼리(pg_stat 모음)·잠금 진단
- `references/evidence-checklist.md` — 출처(Sentry·공식 문서) + 출고 전 체크리스트

## 한계

단일 인스턴스 운영 중심 — 복제·고가용·샤딩은 규모가 정당화할 때 별도 검토(dev-distributed-systems). 플래너 동작은 버전·데이터 분포 의존이라 이 스킬의 처방도 **재측정 없이는 가설**이다. MySQL·SQLite에는 상당수 규칙이 이식되지 않는다(MVCC·vacuum 구조가 다름).

PG 18 메이저 업그레이드 시: `pg_upgrade`가 옵티마이저 통계를 **보존**해 업그레이드 직후 성능 저하(과거 재-ANALYZE 전까지의 침체)가 사라졌다 — 단 dump/restore 또는 pg_upgrade/논리복제 자체는 여전히 필요. 신규 ID는 랜덤 UUIDv4 대신 시간순 정렬되는 `uuidv7()`(PG 18 내장)이 인덱스 지역성에 유리(B-tree 단편화 완화).
