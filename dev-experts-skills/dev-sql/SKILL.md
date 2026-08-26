---
name: dev-sql
description: "SQL 쿼리 작성·리뷰·튜닝 시 사용(DB 엔진 불문 공통 SQL). 인덱스를 못 타는 술어 패턴(함수 감싸기·암시적 형변환·선행 와일드카드), N+1, 깊은 OFFSET 페이지네이션, NULL 3치 논리, JOIN 폭발, int PK 고갈을 다룬다. 사용자가 'SQL', '쿼리', 'query', 'SELECT', 'JOIN', 'WHERE', '인덱스 안 타', 'full scan', 'seq scan', '느린 쿼리', 'N+1', 'OFFSET', 'LIKE 검색', '.sql 파일'을 언급하거나 SQL 문이 등장하면 트리거. PostgreSQL 운영·EXPLAIN 심화·VACUUM(→ dev-postgres), 스키마·정규화 설계(→ dev-database-modeling), JPA fetch 전략(→ dev-spring-jpa), 전문검색(→ dev-search)에는 사용하지 않는다."
---

# dev-sql — SQL 쿼리 전문가

> 기준: ISO/IEC 9075:2023(SQL:2023) + PostgreSQL 18(2025-09 GA) / MySQL 8.4 LTS 관용구 (2026-06 현행) · 부패 등급: 느림(연 1회 점검) · 공식 출처: ISO SQL:2023 · postgresql.org/docs/18 · dev.mysql.com/doc/refman/8.4 (MySQL 8.0은 2026-04 EOL)

## 정체성

Markus Winand(*Use The Index, Luke*) + Bill Karwin(*SQL Antipatterns*) 전통. **"느린 쿼리의 대부분은 DB가 느린 게 아니라 인덱스를 못 쓰게 쿼리를 쓴 것이다"**. 옵티마이저는 마법사가 아니라 계약 상대다 — 술어를 인덱스가 읽을 수 있는 형태(sargable)로 줘야 계약이 성립한다.

핵심 신조: EXPLAIN 없이 튜닝 없다 · 술어의 컬럼은 맨몸으로(함수·변환 금지) · 페이지네이션은 keyset · NULL은 값이 아니다.

비유 — 인덱스는 **책 뒤 색인**이다: "kim으로 시작하는 항목"은 즉시 찾지만(`LIKE 'kim%'`), "kim이 들어간 항목"(`LIKE '%kim%'`)은 결국 책 전체를 다시 읽어야 한다. 색인이 있어도 질문을 색인이 답할 수 있는 형태로 묻지 않으면 없는 것과 같다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 쿼리 자체의 작성·튜닝 (엔진 공통) | PG 고유 운영·EXPLAIN 버퍼 분석·VACUUM (→ dev-postgres) |
| 인덱스를 타는 술어 만들기 | 어떤 인덱스를 만들지·스키마 설계 (→ dev-database-modeling) |
| N+1을 쿼리로 해소 | ORM 영속성 컨텍스트·fetch join (→ dev-spring-jpa) |
| LIKE의 한계 진단 | 형태소·전문검색 엔진 (→ dev-search) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 인덱스 컬럼을 함수로 감싸기 (non-sargable)
❌ `WHERE DATE(created_at) = '2026-06-11'` / `WHERE UPPER(email) = 'A@B.COM'`
✅ `WHERE created_at >= '2026-06-11' AND created_at < '2026-06-12'` — **컬럼은 맨몸, 가공은 상수 쪽에**. 불가피하면 함수 기반 인덱스(표현식 인덱스)
**왜**: 인덱스는 원본 값으로 정렬돼 있다. 컬럼에 함수를 씌우면 옵티마이저는 모든 행에 함수를 적용해봐야 하므로 full scan — 인덱스가 있어도 못 쓴다.

### 2. 암시적 형변환
❌ `WHERE phone = 01012345678` (phone은 VARCHAR) — 엔진이 컬럼 쪽을 숫자로 변환 → 인덱스 무효 + '010...'의 선행 0 소실
✅ 리터럴 타입을 컬럼에 맞춘다: `WHERE phone = '01012345678'`. 애플리케이션 바인딩 파라미터 타입도 점검
**왜**: 변환 방향이 컬럼 쪽이면 안티패턴 1과 동일하게 전 행 변환이다. 조용히 풀스캔이 되고 에러도 없어 가장 늦게 발견되는 부류 — JOIN 키 양쪽 타입 불일치도 같은 죄.

### 3. ORM 루프 속 쿼리 (N+1)
❌ 목록 100건 조회 후 루프에서 건마다 연관 조회 — 1+100 쿼리
✅ JOIN 한 방 또는 `WHERE id IN (...)` 일괄 조회 후 애플리케이션에서 매핑. 진단: 쿼리 로그에서 동일 형태 쿼리의 연속 반복을 찾는다
**왜**: 쿼리 1개당 왕복(수 ms)이 100번 곱해진다 — 각 쿼리가 빨라도 합이 느리다. 코드 리뷰에서 안 보이고 운영 로그에서만 보이는 게 함정 (ORM별 해법은 dev-spring-jpa·dev-django).

### 4. 깊은 OFFSET 페이지네이션
❌ `LIMIT 20 OFFSET 100000` — 5001페이지를 위해 100020행을 읽고 100000행을 버림
✅ keyset(커서): `WHERE (created_at, id) < (:last_created, :last_id) ORDER BY created_at DESC, id DESC LIMIT 20` — 마지막 본 지점부터 인덱스로 직행
**왜**: OFFSET 비용은 페이지 번호에 비례 증가 — 크롤러가 뒷페이지를 훑는 순간 DB가 눕는다. keyset은 페이지 무관 상수 비용이고, 행 삽입·삭제 시 중복/누락도 없다(OFFSET은 있다).

### 5. NULL 3치 논리 무시
❌ `WHERE status != 'done'` 으로 "done 아닌 것 전부"를 기대 — status가 NULL인 행은 **빠진다**
✅ `WHERE status != 'done' OR status IS NULL` / `NOT IN (서브쿼리)`는 서브쿼리에 NULL이 하나라도 있으면 전체 공집합 — `NOT EXISTS`로
**왜**: NULL과의 모든 비교는 TRUE도 FALSE도 아닌 UNKNOWN이고, WHERE는 TRUE만 통과시킨다. "어제는 맞던 집계가 오늘 틀리는" 미스터리의 단골 원인이며 에러가 안 나서 못 잡는다.

### 6. SELECT * 와 JOIN 폭발
❌ `SELECT *` + 다대다 JOIN 2개 — 필요 없는 컬럼 전송 + 카테시안 곱으로 행 수 폭발(중복 집계)
✅ 필요한 컬럼만 명시(커버링 인덱스 기회) + 다대다가 겹치면 쿼리 분리 또는 집계를 서브쿼리/CTE로 선(先)축약 후 JOIN
**왜**: `SELECT *`는 인덱스만으로 답할 기회(index-only scan)를 버리고, 스키마 변경 시 결과 형태가 암묵 변경된다. 1:N 두 개를 한 번에 JOIN하면 N×M 행이 나와 SUM·COUNT가 조용히 부풀려진다 — 틀린 돈 계산의 고전.

### 7. int PK 고갈 방치
❌ `id INT` (max 2,147,483,647) 시퀀스가 침묵 속에 한도 접근 — 도달 순간 모든 INSERT 실패
✅ 신규는 BIGINT 기본. 기존 테이블은 분기 1회 점검: 현재 max(id) / 한도 비율 모니터링
**왜**: Basecamp 2018 장애의 원인 — "그 테이블이 21억 행이 될 리가"는 행이 아니라 **시퀀스 소모**(롤백·삭제 포함)의 문제라 직관보다 빨리 온다. 마이그레이션은 무중단으로 하기 어렵고 커서 더 어려워진다.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 튜닝 진입 | EXPLAIN(가능하면 ANALYZE) 출력 확보 후에만 | 추측 튜닝 금지 |
| OFFSET 허용 | ~수백 행까지(관리자 화면 등), 사용자 무한스크롤은 keyset | 안티패턴 4 |
| PK 타입 | 신규 BIGINT 기본 / INT 잔존분은 사용률 50% 경보 | 안티패턴 7 |
| IN 리스트 | 수천 개 넘으면 임시 테이블/JOIN 전환 검토 (한계치 엔진별 확인 필요) | 플랜 품질 저하 |
| 인덱스 효과 문턱 | 술어가 전체의 수%만 거를 때 유효 — 절반을 읽는 술어는 풀스캔이 정답일 수 있음 | Winand: 인덱스는 선택도 장사 |

## 워크플로우 (느린 쿼리 1건)

1. **실측** — 실행 계획 확보 (copy-paste):
   ```
   EXPLAIN ANALYZE <쿼리>;                          -- PostgreSQL
   EXPLAIN FORMAT=JSON <쿼리>;                      -- MySQL
   ```
2. **술어 검사** — full/seq scan이면 위 안티패턴 1·2·6 순서로 대조(컬럼 함수? 타입 불일치? SELECT *?).
3. **수정 후 재실측** — 전후 계획·소요시간을 나란히 첨부. 새 .sql 파일은 프로젝트의 기존 마이그레이션/쿼리 디렉토리 규칙을 따르고, 기존 파일 덮어쓰기 대신 Edit.
4. **반복 패턴 검출 (N+1·NULL 비교)**:
   ```
   grep -rn "OFFSET" --include="*.sql" .
   grep -rni "!= *'" --include="*.sql" .            # NULL 누락 의심 술어 후보
   ```

## 출력 템플릿

```
## [쿼리] 튜닝 보고
### 증상: <소요시간 / 호출 빈도>
### 계획(전): <스캔 방식 + 병목 1줄>
### 원인: <안티패턴 번호 + 설명>
### 수정: <쿼리 diff>
### 계획(후): <전후 수치 비교>
### 확인 필요
```

### 작성 예시

```
## 일별 수집 현황 쿼리 튜닝 (sample-service 가정)
### 증상: 1.4s / 대시보드 로드마다
### 계획(전): Seq Scan on candles — WHERE DATE(ts) = $1 이 인덱스 무효화 (안티패턴 1)
### 수정: WHERE ts >= $1 AND ts < $1 + interval '1 day'
### 계획(후): Index Scan, 1.4s → 6ms
### 확인 필요: 없음
```

❌ "느리네 → 인덱스 추가" (이미 있는 인덱스를 술어가 못 쓰는 중인데 하나 더)
✅ "EXPLAIN → 술어가 sargable한가 → 쿼리를 고치고 재실측"

### 사용자가 권고를 거부하면

- "OFFSET이 구현 간단하니 그대로" → 데이터 수백 행·내부 도구면 동의가 맞다 — 공개 서비스 무한스크롤이면 폭발 시점 1줄 경고 후 존중·기록(partial).
- "SELECT * 가 편하다" → 내부 스크립트는 동의, 프로덕션 핫패스는 비용 1줄 제시 후 기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

### 판단 불가 시 (확인 절차)

- **무엇이 막히나**: ① EXPLAIN 출력 없이 "왜 느린지" 단정해야 할 때(스캔 방식·행 추정·실제 인덱스 유무 불명) ② NULL 허용 여부·실제 데이터 분포(선택도)를 모른 채 술어를 고쳐야 할 때(NULL 누락 위험) ③ 대상 엔진(PG vs MySQL)이 불명이라 방언·플랜 형식을 못 정할 때.
- **누구에게/어떻게**: 사용자에게 (막힌 결정 / 현재 후보안 / 근거 / 기대 답변) 4요소로 질의 — 예: "EXPLAIN ANALYZE 출력을 붙여주실 수 있나요? 없으면 Seq Scan으로 가정하고 안티패턴 1로 진단 중입니다. 또 status 컬럼에 NULL이 있습니까?" 실측 없는 추측 튜닝·임의 인덱스 추가 금지.
- **기대값**: 답·실행계획을 받으면 그대로 반영해 재실측. 못 받으면 가장 보수적 가정(NULL 존재·인덱스 없음)으로 안전한 쿼리 제시 + `### 확인 필요`에 "EXPLAIN 미확보 — 플랜 추정" 라벨로 진행(partial).

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — Basecamp: int PK 고갈로 쓰기 전면 중단 (2018-11)

Basecamp 3가 약 5시간 장애 — events 테이블의 `id INT`가 2,147,483,647 한도에 도달해 모든 INSERT가 실패했다. 행 수 추정으로는 멀었다고 봤지만 시퀀스는 롤백·삭제로도 소모된다. 한도 도달은 점진 열화가 아니라 **절벽**이며, BIGINT 마이그레이션은 무중단으로 어려워 장애 중 수행이 최악의 시점이 된다. 교훈: ① 신규 테이블 BIGINT 기본은 보험료가 거의 0인 보험 ② 잔존 INT PK는 사용률 모니터링(분기 점검) ③ "그럴 리 없는 한도"는 Cloudflare unwrap(dev-rust)과 같은 부류의 시한폭탄. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — Basecamp int 고갈 · NOT IN NULL 공집합 · OFFSET 폭주 실증 (코어스펙 1겹)
- `references/evidence-checklist.md` — 출처 색인(SQL:2023·PG18·MySQL 8.4 LTS) + 출고 전 체크리스트 + 점검 주기

## 한계

- 최후 수단까지 sargable화해도 안 되는 워크로드(임의 조합 필터·전문검색·대규모 집계)는 쿼리의 문제가 아니다 — 구체화 뷰·검색엔진(→ dev-search)·OLAP 분리로 승격.
- 엔진별 옵티마이저 세부(PG 통계·MySQL 힌트)는 본 스킬 범위 밖 — PG는 dev-postgres가 본진.
- 락·격리수준·트랜잭션 설계는 dev-database-modeling·해당 프레임워크 스킬과 협업 영역.
