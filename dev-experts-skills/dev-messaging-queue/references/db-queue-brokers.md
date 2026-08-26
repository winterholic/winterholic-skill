# DB 큐 표준 구현·브로커 비교·가시성 타임아웃 (SKILL.md 비중복)

## DB 큐 전체 구현 (사다리 1단 — 그대로 사용 가능)

```sql
CREATE TABLE job_queue (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  kind        text NOT NULL,
  payload     jsonb NOT NULL,
  status      text NOT NULL DEFAULT 'pending'
              CHECK (status IN ('pending','running','done','dead')),
  attempts    int NOT NULL DEFAULT 0,
  run_after   timestamptz NOT NULL DEFAULT now(),   -- 백오프·지연 실행
  locked_at   timestamptz,
  last_error  text,
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ON job_queue (status, run_after) WHERE status = 'pending';  -- 부분 인덱스
```

```python
CLAIM = """
UPDATE job_queue SET status='running', locked_at=now(), attempts=attempts+1
WHERE id = (
  SELECT id FROM job_queue
  WHERE status='pending' AND run_after <= now()
  ORDER BY id
  FOR UPDATE SKIP LOCKED        -- 핵심: 경쟁 워커가 서로 안 막힘
  LIMIT 1
) RETURNING id, kind, payload, attempts;
"""

def worker_loop(db):
    while True:
        job = db.fetchone(CLAIM)
        if job is None:
            time.sleep(1.0)        # 폴링 간격 - 지연 허용량의 함수
            continue
        try:
            handle(job)            # 멱등이어야 함 (dev-event-driven #2)
            db.execute("UPDATE job_queue SET status='done' WHERE id=%s", job.id)
        except RetryableError as e:
            backoff = min(60, 2 ** job.attempts)   # 안티패턴 2: 횟수 세고
            if job.attempts >= 3:
                db.execute("UPDATE job_queue SET status='dead', last_error=%s WHERE id=%s",
                           str(e), job.id)         # DLQ = dead 상태 + 경보
            else:
                db.execute("UPDATE job_queue SET status='pending', run_after=now()+%s WHERE id=%s",
                           timedelta(seconds=backoff), job.id)
        except Exception as e:     # 재시도 불가 - 즉시 격리
            db.execute("UPDATE job_queue SET status='dead', last_error=%s WHERE id=%s", str(e), job.id)
```

- **스턱 잡 회수**: running인데 locked_at이 오래된 행(워커 사망) → 주기 잡이 pending으로 환원 — 가시성 타임아웃의 DB 큐 구현.
- lag 지표 = `SELECT count(*) FROM job_queue WHERE status='pending' AND run_after <= now()` — runs 1행 로그(dev-data-engineering)와 같은 관측 사상.

## 브로커 3종 비교표 (사다리 2~4단)

| | Redis Streams | RabbitMQ | Kafka |
|---|---|---|---|
| 모델 | 로그 + 컨슈머 그룹 | 큐 + 라우팅(exchange) | 파티션 로그 |
| 순서 | 스트림 내 | 큐 내(경쟁 시 깨짐) | 파티션 내 |
| 리플레이 | 가능(ID 기반) | 불가(소비=제거) | **본질 기능**(오프셋) |
| DLQ | 직접 구현(XAUTOCLAIM+격리) | 내장(DLX) | 토픽 컨벤션(.dlq) |
| 맞는 곳 | Redis 보유 + 경량 스트림 | 작업 라우팅·우선순위 큐 | 대용량·다중 구독·리플레이 |
| 운영 무게 | 낮음(기존 Redis) | 중간 | 높음 |

선택의 결정 인자는 처리량보다 **리플레이 필요**와 **다중 독립 구독** — 둘 다 없으면 Kafka 근거가 없다.

## 가시성 타임아웃 의미론 (브로커 공통 개념)

```
워커가 메시지를 잡음 -> 타임아웃 T 동안 다른 워커에게 안 보임
├─ T 내 ack -> 완료
├─ T 내 미ack (워커 사망/처리 지연) -> 재배정 (at-least-once의 메커니즘)
└─ 함정: 처리 시간 > T -> 살아있는 워커의 작업이 중복 배정 (재전달 폭풍)
   -> 정량 기준 "처리 < T/3" + 긴 작업은 하트비트 연장 또는 작업 분할
```

- SQS visibility timeout·RabbitMQ consumer timeout·Streams XAUTOCLAIM min-idle·DB 큐 locked_at 회수 — 전부 같은 개념의 방언.
  - XAUTOCLAIM은 Redis 6.2 도입(XPENDING+XCLAIM을 1커맨드로 원자화). Redis 8.4부터는 `XREADGROUP ... CLAIM`이 신규 소비+유휴 재배정을 한 커맨드로 처리하며 공식 벤치에서 XAUTOCLAIM 대비 최대 22.5배 빠름(범위 쿼리화). 6.2~8.2은 여전히 XAUTOCLAIM 권장. (출처: Redis 공식 docs — [XAUTOCLAIM](https://redis.io/docs/latest/commands/xautoclaim/), [Redis 8.4 XREADGROUP CLAIM 블로그](https://redis.io/blog/single-shot-reliable-consumers-with-xreadgroup-claim-in-redis-84/))
- "같은 작업이 두 번 돌았어요"는 보통 버그가 아니라 이 타임아웃과 처리 시간의 경주 — 멱등이 전제인 이유.

## 우선순위·지연 실행

- 우선순위: DB 큐는 priority 컬럼 + ORDER BY가 공짜 / RabbitMQ priority queue 내장 / Kafka는 부적합(토픽 분리로 우회).
- 지연 실행(N분 후): DB 큐 run_after가 가장 자연스럽다 — 브로커들은 지연이 의외로 불편(RabbitMQ 플러그인·SQS 최대 15분). 지연 작업이 주 용도면 DB 큐 가산점.
