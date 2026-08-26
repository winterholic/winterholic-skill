# evidence + 출고 전 체크리스트

## 실증·출처

- **로그 무제한 기본값**: Docker 공식 문서 "Configure logging drivers"(https://docs.docker.com/engine/logging/configure/) — 기본 드라이버 json-file은 로테이션 미설정 시 무제한 증식, `max-size`/`max-file`을 직접 줘야 함을 명시. Engine 28.x·29.x 모두 동일(확인됨 2026-06: 29.x에서도 기본 로테이션 미도입). 공식은 로테이션이 기본 내장된 `local` 드라이버를 권장 — Docker 공식 문서 "Local file logging driver"(https://docs.docker.com/engine/logging/drivers/local/), 기본 max-size 20m × max-file 5.
- **shell form vs exec form 시그널**: Docker 공식 문서 "Dockerfile reference - CMD" — shell form은 `/bin/sh -c`의 자식으로 실행되어 시그널을 못 받음 명시. graceful shutdown 실패의 1차 원인.
- **exit 137 = OOM**: 128 + SIGKILL(9). `docker inspect --format '{{.State.OOMKilled}}'`의 플래그가 확정 근거 — 추측 디버깅 금지의 사례. 주의: OOMKilled는 **컨테이너 cgroup 메모리 한도 초과** 시에만 true. 호스트 전체 메모리 고갈로 커널 OOM killer가 죽인 경우엔 false로 나오므로 `dmesg | grep -i oom`(또는 `journalctl -k`)로 커널 로그 교차확인 필요(커뮤니티 다발 사례: docker forums "exited with code 137 but OOMKilled is false").
- **태그 고정의 근거 구조**: dev-fastapi 실전 케이스(Pydantic 2.1 사태)와 동형 — 상한 없는 의존은 남의 릴리스가 내 장애가 되는 구조. 이미지 태그도 의존성이다.
- **BuildKit 캐시·시크릿 마운트**: Docker 공식 문서 "Build secrets"·"Cache mounts" — 레이어에 남지 않는 메커니즘의 1차 출처.
- **alpine(musl) vs slim(glibc) — 파이썬 기본값이 slim인 근거**: Python 패키지는 glibc 기반 manylinux 휠로 배포되어 musl(alpine)에선 매칭 휠이 없으면 소스 컴파일로 폴백 → 빌드 급격히 느려짐(pythonspeed "Using Alpine can make Python Docker builds 50× slower", https://pythonspeed.com/articles/alpine-docker-python/ — 실측: pandas류 1분 vs 20분 수준). 추가로 musl는 DNS-over-TCP 미지원·작은 스레드 스택 등 런타임 함정. PEP 656(musllinux 휠 표준) 이후 numpy·pandas·matplotlib 등은 musl 휠을 제공해 상황이 개선됐으나 모든 패키지가 빌드하진 않음 → **파이썬/루비/PHP는 slim이 안전한 기본값, Go/Rust(정적 바이너리)는 alpine이 자연스러움**. (Python.org Discussions "Wheels for musl (Alpine)" 교차확인.)
- 오픈소스 차용 표기: 컨테이너 베스트프랙티스류 스킬(VoltAgent 색인) 다수 존재 — **역흡수**: 상태 분류 표 선행·down/up 일회용 테스트·연결된 백업 목록(dev-backup-dr 연계) 같은 운영 규율 부재가 본 스킬 차별점.

## 출고 전 체크리스트 (Dockerfile·compose 변경 시)

- [ ] FROM·image: 태그가 메이저.마이너 고정 (`docker_check.py` 0건)
- [ ] 의존성 명세 COPY가 코드 COPY보다 위
- [ ] .dockerignore에 .git·.env*·venv/node_modules
- [ ] 이미지에 비밀 없음 (`docker history`로 1회 확인)
- [ ] 비root 유저 + exec form CMD
- [ ] 상태 분류 표 작성 — 모든 상태가 볼륨에
- [ ] 6종 세트: 태그/볼륨/env/한도/로그/재시작
- [ ] 상태 서비스에 healthcheck + depends_on condition
- [ ] `docker compose config -q` 통과
- [ ] down/up 일회용 테스트 통과 (데이터·기능 보존)
- [ ] 빌드 후 이미지 크기 확인 — 직전 대비 급증 시 history로 원인
- [ ] 호스트 포트 노출이 최소인지 (DB 포트 외부 노출 없음)

## 점검 주기 (부패 중간 — 반기)

- Engine 메이저 버전 vs 라벨 (현 29.x) — release notes의 기본값 변화(containerd store, 로그)만
- `docker system df` + 안 쓰는 볼륨·이미지 정리
- 메모리 한도 vs `docker stats` 실측 재정렬
- 예제의 베이스 이미지 버전 라벨(현 2026-06: Python 3.14.6/3.13.14 stable, Node 24 LTS·26 Current, Postgres 18.x). 예제는 `python:3.12-slim`을 쓰지만 3.12는 2028-10까지 지원이라 유효 — 신규 프로젝트는 3.13/3.14 권장. 태그 고정 원칙은 버전 무관 불변.
