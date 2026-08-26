# 자료구조 선택표·rate limit·메모리 진단 (SKILL.md 비중복)

## 자료구조 선택표 (용도 → 구조)

| 용도 | 구조 | 핵심 명령 | 함정 |
|---|---|---|---|
| 단순 캐시 값 | string (JSON) | SET ex= / GET | 부분 갱신 불가 — 자주 부분 갱신이면 hash |
| 객체 필드 캐시 | hash | HSET / HGET | hash 전체 TTL만 가능(필드별 불가) |
| 랭킹·리더보드 | zset | ZADD / ZREVRANGE / ZRANK | 동점 처리(score 동일 시 사전순) 명시 |
| 최근 N개 목록 | list | LPUSH + LTRIM | LTRIM 누락 = 무한 성장 |
| 고유 집합·태그 | set | SADD / SISMEMBER | SMEMBERS 거대 셋 금지(SSCAN) |
| 카운터 | string INCR | INCR / INCRBY | 원자적 — 앱에서 읽고-더하기 금지 |
| 이벤트 스트림·경량 큐 | stream | XADD / XREADGROUP | 본격 운영은 dev-messaging-queue |
| 존재 추정(대규모) | bloom (Redis 8 GA부터 코어 내장 — 별도 모듈 설치 불필요) | BF.ADD / BF.EXISTS | 위양성 허용 용도만 |

## rate limit 패턴 (고정 윈도우 → 슬라이딩)

```python
# 고정 윈도우 (단순 - 경계 순간 2배 버스트 허용이 한계)
key = f"rl:{user}:{minute}"
n = r.incr(key)
if n == 1: r.expire(key, 60)
allow = n <= LIMIT

# 슬라이딩 (zset - 정확, 비용 약간)
now = time_ms()
r.zremrangebyscore(key, 0, now - 60_000)
r.zadd(key, {f"{now}": now}); r.expire(key, 60)
allow = r.zcard(key) <= LIMIT
```

- 고정 윈도우로 시작(YAGNI) — 경계 버스트가 실제 문제일 때 슬라이딩 승격.
- 429 응답·Retry-After는 dev-rest-api-design 상태코드 트리와 합류.

## 재계산 락 (stampede 방어 1단) 표준형

```python
val = r.get(key)
if val is not None:
    return val
if r.set(key + ":lock", "1", nx=True, ex=10):     # 10s: 재계산 최대 예상 시간 x2
    try:
        val = compute()
        r.set(key, val, ex=ttl_with_jitter())
    finally:
        r.delete(key + ":lock")
    return val
return stale_or_wait()    # 락 못 잡은 쪽: 직전 stale 반환(보관해뒀다면) 또는 짧은 재시도
```

stale 보관 트릭: 본 키 TTL보다 긴 `key:stale`을 SET해 두면 "잠깐 낡은 응답"이 항상 가능 — 2번 거짓말(miss 폭주)을 1번 거짓말(허용된 stale)로 바꾸는 거래.

## 메모리·상태 진단 명령 (copy-paste)

```
redis-cli INFO memory | grep -E "used_memory_human|maxmemory_human|evicted"
redis-cli INFO stats | grep -E "keyspace_(hits|misses)"     # 적중률 - 0.8 미만이면 키 설계 재검
redis-cli --bigkeys                                          # 거대 키 색출 (SCAN 기반 - 안전)
redis-cli SLOWLOG GET 10                                     # 느린 명령 (KEYS 범인 색출)
redis-cli DEBUG SLEEP 0                                      # (쓰지 말 것 - 예시) 블로킹 명령의 위험 시연용
```

- 적중률(hits/(hits+misses))이 낮으면: TTL이 너무 짧거나, 키가 너무 세분화됐거나, 캐시할 가치가 없는 데이터다 — 도입 근거 재검토.
- evicted_keys 증가 = maxmemory 도달 중 — TTL 설계나 용량 재검토(증설이 1순위가 아니다).
