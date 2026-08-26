# 아웃박스 구현·사가 표준형·이벤트소싱 판단 (SKILL.md 비중복)

## 아웃박스 구현 상세

```sql
CREATE TABLE outbox (
  id          uuid PRIMARY KEY,
  type        text NOT NULL,            -- 'TickIngested'
  key         text NOT NULL,            -- 파티션/멱등 기준
  payload     jsonb NOT NULL,
  occurred_at timestamptz NOT NULL,
  published_at timestamptz              -- NULL = 미발행
);
```

```python
# 발행 측: 비즈니스 변경과 같은 트랜잭션
with db.tx() as tx:
    tx.save(run)
    tx.insert_outbox(TickIngested(run_id=run.id, ...))   # 원자성은 여기서 끝

# 릴레이 (별도 루프/프로세스): at-least-once
rows = db.fetch("SELECT * FROM outbox WHERE published_at IS NULL ORDER BY occurred_at LIMIT 100")
for r in rows:
    broker.publish(r)              # 여기서 죽으면 -> 다음 루프에 재발행 (중복 = 정상)
    db.execute("UPDATE outbox SET published_at = now() WHERE id = %s", r.id)
```

- 릴레이 단일 인스턴스 보장(또는 SELECT ... FOR UPDATE SKIP LOCKED) — 2중 릴레이는 중복만 늘린다(멱등이라 안전하긴 함).
- 정리: published_at이 보존 기간(예: 30일) 지난 행 삭제 — outbox 비대화가 dev-postgres vacuum 문제로 전이되지 않게.
- CDC(Debezium류)는 폴링이 측정된 병목일 때 — 소규모에서 폴링 1~5s는 충분하다.

## 멱등 소비 표준형

```python
def handle(event):
    with db.tx() as tx:
        try:
            tx.execute("INSERT INTO processed_events (event_id, consumer) VALUES (%s, %s)",
                       event.id, "validator")
        except UniqueViolation:
            return                       # 이미 처리 - 조용히 스킵 (로그 debug 1줄)
        do_work(tx, event)               # 처리와 기록이 같은 트랜잭션 - 부분 처리 없음
```

핵심: **처리 기록과 처리 결과가 같은 트랜잭션** — 기록만 되고 작업이 안 되거나 그 반대가 없도록.

## 사가 오케스트레이션 표준형

```
saga_instances: (saga_id, type, current_step, state, payload, updated_at)

단계 표 (설계 산출물):
| # | 단계 | 보상 | 보상 불가? |
| 1 | 주문 생성 | 주문 취소 | - |
| 2 | 재고 차감 | 재고 복원 | - |
| 3 | 결제 승인 | 결제 취소(환불) | - |
| 4 | 확인 메일 | (없음) | 보상 불가 - 맨 뒤 배치의 이유 |
```

- 오케스트레이터는 단계 결과 이벤트를 받아 다음 단계 커맨드 발행 — 진행 상태가 한 테이블에 보여 디버깅 가능.
- 각 단계·보상도 멱등이어야 한다(재시도 전제) — 보상의 보상은 없다, 보상은 반드시 성공하도록 단순하게(상태 SET 수준).
- 타임아웃: 단계 응답이 N분 없으면 보상 개시 — "영원히 기다리는 사가"가 중간 상태 누적의 주범.
- 코레오그래피(이벤트 연쇄)는 2단계까지만 — 3단계+는 "지금 어디까지 갔나"를 아무도 모르게 된다.

## 이벤트소싱 도입 판단 (별개 결정)

| 신호 | 판정 |
|---|---|
| 감사 이력이 1급 요구사항(규제·금융 원장) | 검토 가치 |
| "그때 상태가 뭐였나" 시간여행 질의 빈번 | 검토 가치 |
| 그냥 이벤트 기반이니까 | ✕ — 이벤트 기반(통신)과 이벤트소싱(저장)은 독립 결정 |
| CRUD + 이력 테이블로 충분 | ✕ — 90%는 이쪽 |

이벤트소싱의 항구 비용: 스키마 진화가 저장 데이터 전체에 적용(업캐스터)·재생 성능·스냅숏 관리 — 도입 전 이 셋의 운영 계획이 없으면 보류.
