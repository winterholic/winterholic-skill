# compose 운영 — 6종 세트 표준형·healthcheck·일상 명령 (SKILL.md 비중복)

## 서비스 6종 세트 표준형

```yaml
services:
  api:
    image: sample-service-api:0.3          # 1. 태그 고정
    env_file: ../secrets/api.env      # 2. 설정 — 레포 밖 경로
    volumes:
      - api-cache:/home/app/.cache    # 3. 상태 — named volume
    mem_limit: 512m                   # 4. 자원 한도
    logging:                          # 5. 로그 로테이션 (json-file은 기본 무제한 → 반드시 명시)
      driver: json-file
      options: { max-size: "10m", max-file: "3" }
      # 대안: driver: local (로테이션 기본 내장 20m×5, blob 저장으로 효율↑) — docker logs는 그대로 동작
    restart: unless-stopped           # 6. 재시작 정책
    depends_on:
      db: { condition: service_healthy }
    networks: [backend]

  db:
    image: postgres:18.4
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d stock"]
      interval: 10s
      timeout: 3s
      retries: 5
      start_period: 30s               # 초기 기동 여유 - 이 동안 실패는 미집계
    ...
```

## healthcheck 패턴

| 서비스 | test | 메모 |
|---|---|---|
| PostgreSQL | `pg_isready -U <user> -d <db>` | 접속 가능 ≠ 복구 완료 — start_period로 흡수 |
| Redis | `redis-cli ping` | |
| HTTP 앱 | `curl -fsS http://localhost:8000/health \|\| exit 1` | 이미지에 curl 없으면 wget 또는 파이썬 한 줄 |
| 배치성(웹 없음) | 자체 상태 파일/쿼리 스크립트 | "살아있음"의 정의를 먼저 — 프로세스 생존 ≠ 일하고 있음 |

- `depends_on.condition: service_healthy`는 **기동 순서만** 보장 — 운영 중 DB가 죽었다 살아나는 경우의 재연결은 앱 책임(커넥션 풀의 pre-ping 등, dev-fastapi/dev-postgres).

## 네트워크·노출 최소화

- 기본값: 서비스 간 통신은 내부 네트워크(`networks: [backend]`), **호스트 포트 노출(`ports:`)은 진짜 외부 접근이 필요한 것만**. DB 포트를 호스트에 열어두는 것이 홈서버 보안 구멍의 단골.
- 서비스 간 주소는 컨테이너 이름이 DNS다: `postgres://db:5432/...` — localhost가 아니다(컨테이너의 localhost는 자기 자신).
- 리버스 프록시 1개(nginx 등)만 80/443을 받고 내부로 라우팅하는 구조가 14개 서비스 운영의 표준형(상세 → dev-nginx).

## 일상 운영 명령 (copy-paste)

```
docker compose up -d                       # 적용 (변경된 서비스만 재생성)
docker compose ps                          # 상태 + (healthy)
docker compose logs -f --tail=100 <svc>    # 로그 추적
docker compose config -q                   # 문법 검증 (CI에도)
docker stats --no-stream                   # 자원 사용 스냅숏 - 한도 보정 근거
docker system df                           # 디스크 사용 분해
docker system prune -f                     # 떠돌이 정리 (이미지는 -a 신중히)
docker inspect <ctr> --format '{{.State.OOMKilled}}'   # 137 사인 확인
```

## 갱신 절차 (이미지 버전 올리기)

1. compose의 태그를 새 버전으로 수정(커밋 — 변경 이력이 곧 배포 이력).
2. `docker compose pull <svc>` → `docker compose up -d <svc>` (해당 서비스만 재생성).
3. `ps`로 healthy 확인 + 앱 로그 1분 관찰. DB류는 마이너 버전이라도 release notes의 데이터 디렉토리 호환 확인 먼저(메이저는 dev-backup-dr의 백업 선행이 전제).
4. 문제 시 롤백 = 태그 되돌리고 다시 up — 이게 되려면 볼륨이 구버전과 호환이어야 한다(메이저 업그레이드 직후가 롤백 불가 구간임을 인지).
