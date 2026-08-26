# dev-sql evidence — 장애·실증 사례

## 1. Basecamp 3 — int PK 고갈 (2018-11-08)

- **무슨 일**: 약 5시간 동안 Basecamp 3 쓰기 전면 실패. 출처: Basecamp 공식 포스트모템(DHH 사과문 포함).
- **근본 원인**: events 테이블 `id`가 32-bit signed INT — 2,147,483,647 도달 순간 시퀀스 발급 불가, 모든 INSERT 에러. 사전 경보 없었음.
- **복구**: 장애 중 BIGINT로 ALTER — 대형 테이블 ALTER는 그 자체로 장시간 잠금이라 복구가 오래 걸렸다.
- **이 스킬과의 연결**: 안티패턴 7. 점검 쿼리(PostgreSQL):
  ```sql
  SELECT relname, last_value, 2147483647 - last_value AS remaining
  FROM pg_sequences s JOIN pg_class c ON c.relname = s.sequencename
  WHERE s.max_value <= 2147483647;
  ```
  (MySQL은 information_schema.tables의 AUTO_INCREMENT 대조 — 정확 쿼리 확인 필요)

## 2. NOT IN + NULL — "조건에 맞는 행이 분명 있는데 0건" (3치 논리 실증)

- **무슨 일**: `WHERE id NOT IN (SELECT ref_id FROM t2)` — t2.ref_id에 NULL이 단 1개라도 있으면 **전체 결과가 공집합**. 모든 SQL 엔진 공통 명세 동작이라 버그 리포트조차 안 된다.
- **메커니즘**: `id NOT IN (1, NULL)` = `id != 1 AND id != NULL` = `... AND UNKNOWN` — 어떤 행도 TRUE가 못 된다.
- **해법**: `NOT EXISTS (SELECT 1 FROM t2 WHERE t2.ref_id = t1.id)` — NULL에 면역이고 플랜도 대개 동등 이상.
- **이 스킬과의 연결**: 안티패턴 5. 집계·정산 쿼리에서 이 패턴이 나오면 "원래 NULL이 없던 컬럼에 NULL이 생기는 날" 숫자가 조용히 틀어진다 — 데이터 사고 중 가장 늦게 발견되는 유형.

## 3. 깊은 OFFSET — 크롤러가 만든 자초 DoS (반복 실증 패턴)

- **무슨 일**: 공개 목록 API에 `?page=50000` 요청(검색엔진 크롤러·스크레이퍼가 기계적으로 순회) → `LIMIT 20 OFFSET 999980` → 페이지당 100만 행 읽기 → DB CPU 포화. 다수 서비스가 동일 패턴으로 보고(Winand가 *Use The Index, Luke*에서 표준 사례로 정리).
- **수치 감각**: OFFSET N의 비용은 O(N) — 1페이지 5ms였던 쿼리가 5만 페이지에선 수 초. 인덱스가 있어도 "읽고 버리기"는 못 피한다.
- **해법**: keyset 페이지네이션 + (공개 API라면) 최대 페이지 깊이 제한. keyset은 `(정렬키, 고유키)` 복합 인덱스가 전제 — 동률 처리를 위해 고유키를 정렬에 반드시 포함.
- **이 스킬과의 연결**: 안티패턴 4. API 설계 단계에서 커서 방식을 계약으로 — 출시 후 OFFSET→커서 전환은 클라이언트 호환성 작업이 따라붙는다(→ dev-rest-api-design).

> 출처: Basecamp 공식 포스트모템(2018) · ISO SQL 3치 논리 명세 · Use The Index, Luke(Winand). 2026-06 기준.
