# 품질 정책 — 결측·이상치 표 패턴·적재 검증 쿼리·관측 로그 (SKILL.md 비중복)

## 결측·이상치 정책 표 패턴 (설계 단계 합의 문서)

작성 규칙: 케이스는 소스에서 **실제로 본 것 + 도메인상 가능한 것**만(상상 금지). 각 행은 [감지 → 처리 → 흔적]이 한 줄에.

| 케이스 | 감지 | 처리 | 흔적(플래그) |
|---|---|---|---|
| 행 자체 없음(휴장) | 캘린더 대비 | 정상 — 행 없음 유지 | 캘린더가 곧 흔적 |
| 행 없음(영업일) | 캘린더 대비 | **결측 행 기록 + 알림** | missing_dates 테이블 |
| 필드 NULL | 적재 시 | NULL 유지 | quality_flag='missing' |
| 명백한 이상치(음수 가격) | 정제 규칙 | raw 보존, 정제 층 제외 | rejected 테이블 + 사유 |
| 의심 이상치(전일 대비 ±30% 초과) | 정제 규칙 | **적재하되** 플래그 | quality_flag='suspect' |
| 소스 형식 변화(파싱 실패) | 파서 예외 | 파이프라인 실패(시끄럽게) | 에러 로그 + 원문 보존 |

원칙: **확실한 쓰레기만 거르고, 의심은 플래그와 함께 통과** — 정제가 과격하면 진짜 이벤트(상한가·액면분할)를 지운다. 거른 것은 반드시 rejected에 남긴다(거른 게 맞았는지 사후 검증 가능하게).

## 적재 검증 쿼리 모음 (copy-paste 골격)

```sql
-- 1. 행수 하한 (영업일에만 실행)
SELECT count(*) FROM candles WHERE base_date = :d;
-- 기대: >= active_codes * 0.95  (5%는 거래정지 여유 - 확인 필요: 실측 후 조정)

-- 2. 필수 컬럼 NULL 비율
SELECT count(*) FILTER (WHERE close IS NULL)::float / nullif(count(*),0)
FROM candles WHERE base_date = :d;   -- 기대: <= 0.01

-- 3. 키 중복
SELECT code, base_date, count(*) FROM candles
WHERE base_date = :d GROUP BY 1,2 HAVING count(*) > 1;   -- 기대: 0행

-- 4. 갭 감지 (주기 점검용 - 영업일인데 데이터 없는 날)
SELECT cal.d FROM trading_calendar cal
LEFT JOIN (SELECT DISTINCT base_date FROM candles) c ON c.base_date = cal.d
WHERE cal.is_open AND c.base_date IS NULL AND cal.d >= :since;
```

검증 실패 시 동작: 적재 트랜잭션 롤백(가능하면) 또는 quality_flag 일괄 표시 + 워터마크 미전진 + 알림. "일단 두고 내일 보자"가 침묵 오염의 시작이다.

## 관측 — 실행 1행 로그

모든 실행이 남기는 한 행 (테이블 또는 구조적 로그):

```
runs: (pipeline, base_date, started_at, finished_at, status,
       rows_extracted, rows_loaded, rows_rejected, null_ratio, error_msg)
```

- 이 한 행이 대시보드·알림·디버깅의 공통 원천 — "어제 몇 행이었지"를 코드가 아니라 데이터로 답한다.
- 알림 기준: status != ok **또는** rows_loaded가 7일 이동평균의 ±50% 밖 (절대값 임계는 종목 수 변화에 깨진다).
- Discord/텔레그램 알림 연결은 dev-bot-building, 대시보드·경보 규칙 설계는 dev-monitoring.

## 스키마 진화 (소스가 필드를 바꿀 때)

- raw 층이 JSON이면 새 필드는 자동 보존 — 정제 층 컬럼 추가는 `ALTER TABLE ADD COLUMN ... NULL`(기존 행 NULL 허용)로 하위호환.
- 필드 의미 변화(단위 변경 등)가 최악 — 컬럼 재사용 금지, 새 컬럼 + 적용 시점 기록. "어느 날짜부터 새 의미"를 데이터로 남긴다.
- 파서는 **미지 필드에 관대, 기지 필드에 엄격**: 새 필드 등장은 로그만, 기존 필드 형식 변화는 실패.
