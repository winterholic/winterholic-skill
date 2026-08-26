# 멱등 전략 3형·워터마크·백필 (SKILL.md 비중복 심화)

## 멱등 전략 3형 — 선택 기준

| 전략 | 형태 | 맞는 곳 | 함정 |
|---|---|---|---|
| **Upsert** | `INSERT ... ON CONFLICT (자연키) DO UPDATE` | 행 단위 갱신, 키가 명확 (종목+기준일) | 자연키 설계가 틀리면 무의미 — "같은 행"의 정의가 먼저 |
| **파티션 교체** | `DELETE WHERE 기준일=? → INSERT` 한 트랜잭션 | 기준일 단위 통째 재생성 (일배치 표준) | 트랜잭션 밖에서 하면 DELETE 후 죽었을 때 빈 구간 |
| **Append + dedup 뷰** | 수집차수 컬럼 추가 append, 서빙은 최신 차수만 | raw 층 (이력 자체가 가치), 감사 필요 | 서빙 쿼리가 복잡해짐 — raw 전용으로 |

기본값: **raw는 append+차수, 정제·서빙은 upsert 또는 파티션 교체**. 세 전략 모두 "재실행 시 최종 상태 동일"을 만족하는지로 검증(SKILL.md 멱등 스모크).

## 워터마크 설계

```
watermarks 테이블: (pipeline_name, watermark_value, updated_at)
```

- **성공 시에만 전진** — 적재 검증 3종 통과 후 갱신. 검증 실패면 워터마크 유지 → 다음 실행이 같은 구간 재시도(멱등이므로 안전).
- 워터마크 단위는 소스의 제공 단위에 맞춘다: 일 단위 소스면 기준일, 커서 페이징이면 커서.
- **갭 감지**: 워터마크가 "마지막 성공"만 기억하면 중간 구멍을 모른다 — 기준일 연속성 검사(영업일 캘린더 대비 빠진 날짜 쿼리)를 주기 실행 항목에 포함.
- 동시 실행 가드: 같은 파이프라인 2중 기동 방지(락 파일 또는 DB advisory lock) — 스케줄러 재시작 직후 중복 기동이 단골.

## 백필 절차 (운영 중 파이프라인에 과거 구간 채우기)

1. **같은 코드, 기간 인자** — 백필 전용 스크립트를 따로 만들지 않는다(두 코드는 반드시 어긋난다). `--from/--to` 인자가 설계 단계 요구사항.
2. **작은 구간부터 검증** — 1일 → 1주 → 전체. 첫 구간 후 적재 검증 쿼리로 형식 확인.
3. **rate limit 배수 고려** — 백필은 평시의 수십 배 호출. 소스 한도의 50%로 더 보수적으로 + 야간 실행.
4. **워터마크와 분리** — 백필이 워터마크를 건드리면 증분 수집이 꼬인다. 백필은 워터마크 미갱신 모드로.
5. **백필 중 운영 배치와의 충돌** — 같은 기준일을 동시에 쓰지 않도록 구간을 영업시간 밖으로 — upsert라 데이터는 안 깨지지만 락 경합·한도 공유 문제.

## 재시도·백오프 구현 표준형 (stdlib)

```python
def fetch_with_retry(call, max_tries=3, base=1.0):
    # 3 tries / exponential + jitter: most transient failures clear by try 2
    for attempt in range(1, max_tries + 1):
        try:
            return call()
        except TransientError:
            if attempt == max_tries:
                raise
            time.sleep(base * 2 ** (attempt - 1) + random.uniform(0, 0.5))
```

- **재시도 가능 에러를 명시 분류** — 타임아웃·5xx·연결 끊김만. 4xx(401 토큰 만료·400 잘못된 요청)는 재시도가 아니라 다른 처리(재인증/버그 수정). bare except 재시도는 dev-python #3 위반.
- 재시도 로그에 시도 횟수 포함 — "3번 만에 성공"이 잦아지면 소스 상태 신호.

## 단계 분리의 실행 형태

```
python -m collector.extract --date 2026-06-11     # raw만
python -m collector.transform --date 2026-06-11   # raw → 정제
python -m collector.run --date 2026-06-11         # 전체 (위 둘 순차)
```

각 단계가 CLI로 독립 실행 가능하면: 정제 버그 수정 후 transform만 재실행, 소스 장애 후 extract만 재시도 — 운영이 단계 단위가 된다.
