# 정규형 판정·비정규화 동기화·이력 2형·다대다·트리 (SKILL.md 비중복)

## 정규형 빠른 판정 (이론 대신 질문 3개)

1. **1NF**: 한 칸에 값 하나인가? (CSV·배열 컬럼 → 행/연결 테이블) — 안티패턴 1
2. **2NF/3NF 통합 질문**: "이 컬럼은 이 테이블의 키가 아닌 다른 것에 의해 정해지는가?" — 예: candles에 stock_name이 있으면 code가 정하는 값이라 stocks로 — 갱신 시 한 곳만 고치면 되는 상태가 3NF의 실용 정의.
3. 역질문(과정규화 경계): 조인이 4단을 넘고 그 분해로 지키는 갱신 정합이 없으면 — 합쳐도 된다.

## 비정규화 동기화 3패턴 (하기로 했다면 책임 1곳)

| 패턴 | 형태 | 맞는 곳 |
|---|---|---|
| 앱 코드 동기화 | 쓰기 서비스가 파생 컬럼 동시 갱신 | 쓰기 지점이 1곳일 때만 (2곳째부터 누락 시작) |
| DB 트리거 | 원본 변경 시 자동 갱신 | 쓰기 지점 다수·로직 단순 — 단 "보이지 않는 실행"(dev-django 시그널과 동일 주의) 문서화 |
| 배치 재계산 | 주기적으로 원본에서 파생 재생성 | 실시간 불요(일 단위 집계) — **가장 안전**(원본이 진실, 파생은 캐시) |

배치 재계산이 기본값 — 파생 컬럼이 어긋나도 다음 배치가 고친다(자기 치유). dev-data-engineering 서빙 층 재생성과 동일 사상.

## 이력 테이블 2형

### A. 유효기간형 (느리게 변하는 속성 — 등급·정책·요금)
```sql
CREATE TABLE stock_grade_history (
  code text NOT NULL,
  grade text NOT NULL,
  valid_from date NOT NULL,
  valid_to date,                    -- NULL = 현재 (이 NULL은 '값 없음'이 맞아서 허용)
  UNIQUE (code, valid_from)
);
-- 현재값 뷰: WHERE valid_to IS NULL / 당시값: WHERE :d BETWEEN valid_from AND coalesce(valid_to,'9999-12-31')
```
- 갱신 = [현재 행 valid_to 마감 + 새 행] 한 트랜잭션 — 겹침 방지는 PG라면 EXCLUDE 제약(daterange)까지 가능.

### B. 불변 append형 (사건·측정 — 시세·로그·거래)
- UPDATE 자체가 없다 — candles가 이것. "수정"은 정정 행 추가(수집차수) — dev-data-engineering raw 층과 동일.
- 선택 기준: **상태의 변화**(A) vs **사건의 기록**(B) — "바뀌었다"가 아니라 "일어났다"면 B.

## 다대다·트리 표준형

```sql
-- 다대다: 연결 테이블 + 복합 UNIQUE (+ 관계 자체의 속성은 여기에)
CREATE TABLE watchlist_items (
  watchlist_id bigint REFERENCES watchlists(id),
  code text NOT NULL,
  added_at timestamptz NOT NULL,
  PRIMARY KEY (watchlist_id, code)     -- 연결 테이블은 복합 PK가 자연스러운 예외
);
```

트리(카테고리류): 인접 리스트(parent_id) + PG 재귀 CTE가 기본값 — 깊이 고정·조회 폭주 시에만 materialized path 검토. 트리 모델링 4종 비교는 과한 규모의 신호일 때가 많다(카테고리 2단이면 그냥 컬럼 2개).

## 마이그레이션 호환 원칙 (스키마 변경의 시간축)

- 추가는 안전(NULL 허용 또는 DEFAULT), 의미 변경·삭제는 2단계(dev-rest-api-design breaking 판별표의 스키마판): [새 컬럼 추가 → 이중 기록·백필 → 코드 전환 → 옛 컬럼 제거].
- NOT NULL 추가는 [NULL 허용 추가 → 백필 → NOT NULL 제약] 3단 — 대형 테이블 일괄 잠금 회피(dev-postgres 운영 DDL).
- 컬럼 재사용 절대 금지 — dev-data-engineering 스키마 진화 규칙과 동일.
