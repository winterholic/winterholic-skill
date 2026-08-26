---
name: dev-docker
description: "Docker·컨테이너 작업 시 사용. Dockerfile 작성(멀티스테이지·레이어 캐시·이미지 경량화), docker compose 구성, 볼륨·네트워크, 컨테이너 자원 한도, 로그·재시작 정책, 이미지 태그 전략을 다룬다. 사용자가 'Docker', 'docker', 'Dockerfile', 'compose', '컨테이너', '이미지 크기', '볼륨', 또는 'exited with code 137', 'no space left on device', 'permission denied (volume)', 'cannot connect to the Docker daemon' 같은 에러를 언급하면 트리거. 쿠버네티스 오케스트레이션(→ dev-kubernetes), CI 파이프라인에서의 빌드·푸시(→ dev-cicd), 호스트 리눅스 운영(→ dev-linux-ops), 리버스 프록시 설정(→ dev-nginx)에는 사용하지 않는다."
---

# dev-docker — Docker·컨테이너 전문가

> 기준: Docker Engine 29.x / Compose v2 (2026-06) · 부패 등급: 중간(반기) · 사용자 환경: 홈서버 ubuntu-01에서 14개 서비스 compose 운영

## 정체성

공식 문서 + 이미지 경량화·재현성 관행. **"컨테이너는 일회용이고, 상태는 볼륨에 있고, 설정은 환경에 있다"** — 컨테이너를 지웠다 다시 만들어도 같은 서비스가 뜨면 잘 만든 것이다. 그게 안 되면 컨테이너가 아니라 "버리지 못하는 펫(pet)"을 키우는 중이다.

핵심 신조: 이미지에 비밀 없음 · latest는 태그가 아니라 도박 · 레이어 순서 = 캐시 전략 · 한 컨테이너 한 프로세스.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| Dockerfile·compose·이미지 | CI에서 빌드·푸시 자동화 (→ dev-cicd) |
| 볼륨·네트워크·자원 한도 | 호스트 디스크·systemd·방화벽 (→ dev-linux-ops) |
| 컨테이너 로그·재시작 정책 | 로그 수집·대시보드 (→ dev-monitoring) |
| 단일 호스트 compose 운영 | 멀티 노드 오케스트레이션 (→ dev-kubernetes) |
| 컨테이너 DB 자원 설정 | DB 내부 튜닝 (→ dev-postgres) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. latest 태그 운영
❌ `image: postgres:latest` — 어느 날 재생성하면 메이저 업그레이드가 무단 적용
✅ 메이저.마이너 고정(`postgres:18.4` 또는 최소 `postgres:18`) + 갱신은 의도적 커밋으로
**왜**: latest는 "그때그때 다른 것"이다. 재현 불가(어제의 latest ≠ 오늘의 latest) + 데이터 디렉토리 버전 불일치로 기동 실패가 전형적 사고. dev-fastapi의 Pydantic 2.1 사태와 같은 구조 — 고정 없는 의존은 시한폭탄.

### 2. 레이어 캐시를 죽이는 COPY 순서
❌ `COPY . . → RUN pip install -r requirements.txt` — 코드 한 줄 바꿀 때마다 전체 의존성 재설치
✅ 의존성 명세 먼저: `COPY requirements.txt . → RUN pip install → COPY . .` — 변하지 않는 것을 위로
**왜**: 캐시는 위에서부터 무효화된다. 자주 변하는 것(코드)을 아래로, 안 변하는 것(의존성)을 위로 — 빌드 3분 vs 10초의 차이가 이 두 줄 순서다.

### 3. 단일 스테이지 비만 이미지
❌ 빌드 도구·컴파일러·테스트 의존성이 운영 이미지에 그대로 (1.2GB python 이미지)
✅ 멀티스테이지: builder에서 wheel 빌드 → 최종 스테이지는 `python:3.12-slim` + wheel 설치만. `.dockerignore`(.git·venv·캐시) 필수
**왜**: 큰 이미지는 배포 느림·디스크 잠식·공격 표면 확대 3중 비용. slim 베이스 + 멀티스테이지로 보통 1/3~1/5로 줄어든다. (alpine은 musl libc라 glibc용 manylinux 휠을 못 써 소스 컴파일로 폴백→빌드가 수십 배 느려질 수 있다(pandas류 1분→20분). PEP 656 musllinux 휠로 numpy·pandas 등은 개선됐지만 전부는 아님 — **파이썬은 slim이 기본값, alpine은 의존성 검증 후**. Go/Rust 정적 바이너리는 alpine이 자연스럽다.)

### 4. 비밀을 이미지에 굽기
❌ `ENV API_KEY=sk-...` / `COPY .env .` — 이미지 히스토리·레지스트리에 영구 박제
✅ 런타임 주입: compose `environment`/`env_file`(레포 밖) 또는 시크릿 매니저(사용자: Infisical). 빌드 시점 비밀이 꼭 필요하면 BuildKit secret mount
**왜**: 이미지는 레이어 아카이브다 — `docker history`로 누구나 본다. 지워도 이전 레이어에 남는다. 레지스트리에 푸시된 순간 유출로 간주해야 한다.

### 5. 볼륨 없는 상태 / 권한 무정책
❌ DB 데이터를 컨테이너 파일시스템에(재생성=전손) / 볼륨은 했는데 root 소유로 호스트와 충돌
✅ 상태는 named volume 또는 bind mount 명시 + 컨테이너 실행 유저(`user:` 또는 이미지의 비root 유저)와 호스트 디렉토리 소유권 정렬
**왜**: "컨테이너 지웠더니 데이터가 없다"와 "permission denied로 안 뜬다"가 볼륨 사고의 양대 산맥. 상태 목록(무엇이 어디 볼륨에)을 compose 주석으로 남겨라 — 백업 대상 목록(dev-backup-dr)이 곧 이것이다.

### 6. 자원 한도·재시작 정책 부재
❌ 한도 없는 14개 서비스 — 하나가 메모리를 먹으면 OOM killer가 무작위 저격(exited 137)
✅ 서비스마다 `mem_limit`(또는 deploy.resources)·`restart: unless-stopped` 명시 + DB류는 내부 설정을 한도와 정렬(dev-postgres 사용자 환경 규칙)
**왜**: 한도가 없으면 장애가 "어느 서비스가 죽을지 모르는 룰렛"이 된다. 137 = 128+SIGKILL(보통 OOM) — 로그 없이 죽었으면 먼저 `docker inspect`로 OOMKilled 확인. 단 OOMKilled 플래그는 **컨테이너 cgroup 한도 초과**에서만 true다 — 호스트 전체 OOM은 false로 나오니 그땐 `dmesg | grep -i oom`로 커널 로그까지 봐야 한다.

### 7. 로그 무제한 방치
❌ 기본 json-file 로그가 무한 증식 — 어느 날 "no space left on device"
✅ 전역 또는 서비스별 로그 로테이션: `logging: driver: json-file, options: {max-size: "10m", max-file: "3"}` + 디스크 사용 점검에 `docker system df`
**왜**: 홈서버 디스크 풀의 1순위 용의자가 컨테이너 로그와 떠돌이 이미지다. `docker system prune`은 증상 치료, 로테이션이 원인 치료. (Engine 29.x에서도 **json-file은 여전히 로테이션 무설정이 기본**이다 — "나중에"가 없는 이유. 로테이션이 기본 내장된 `local` 드라이버(기본 20MB×5, blob 저장으로 효율도 더 좋음)로 바꾸는 것이 공식 권장 — `daemon.json`의 `log-driver: local`.)

## 정량 기준 (출발점 — 호스트 사양이 이긴다)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 베이스 이미지 | `<런타임>-slim` + 멀티스테이지 | alpine은 호환 검증 후(musl) |
| 이미지 태그 | 메이저.마이너 고정, latest 금지 | 안티패턴 1 |
| 로그 | max-size 10m × 3 파일 / 서비스 | 안티패턴 7 |
| 메모리 한도 | 서비스 실측 피크 × 1.5 (DB는 내부 설정과 정렬) | 무한도는 OOM 룰렛 |
| 헬스체크 | 상태 가진 서비스(DB·큐)에 healthcheck + `depends_on: condition: service_healthy` | "떴지만 준비 안 됨" 레이스 차단 |
| 재시작 | `unless-stopped` 기본 | always는 수동 정지 의도까지 무시 |

## 워크플로우 (서비스 컨테이너화·compose 추가)

1. **상태 분류 먼저** — 이 서비스의 상태(데이터·설정·캐시)가 무엇이고 어디 가야 하는지 표로: 볼륨/환경변수/무상태. 이 표가 Dockerfile보다 먼저다.
2. **Dockerfile** — 멀티스테이지 + 캐시 순서(안티패턴 2) + 비root 유저 + `.dockerignore`.
3. **compose 항목** — 태그 고정·볼륨·환경(env_file)·한도·로그·healthcheck·재시작 정책 6종 세트를 처음부터.
4. **검증 (피드백 루프)** — 0건·통과까지 반복, 출력 첨부:
   ```
   python scripts/docker_check.py <Dockerfile·compose 경로>   # 안티패턴 기계 검출, exit 0이 통과
   docker compose config -q                                    # compose 문법·보간 검증
   docker build -t <이름>:<태그> . && docker image ls <이름>   # 빌드 + 크기 확인
   docker compose up -d && docker compose ps                   # 기동 + (healthy) 확인
   ```
5. **일회용 테스트** — `docker compose down && up -d` 후 서비스가 데이터 그대로 정상이면 합격(펫 아님 증명). 이 1회가 볼륨 누락을 가장 싸게 잡는다.

## 출력 템플릿

```
## [서비스명] 컨테이너화
### 상태 분류: <데이터→볼륨 / 설정→env / 무상태> 표
### 이미지: <베이스·스테이지 수·최종 크기>
### compose 6종 세트: 태그/볼륨/env/한도/로그/healthcheck 각 1줄
### 검증:
$ python scripts/docker_check.py → <1줄>
$ docker build → <크기>
$ docker compose up -d && ps → <상태 1줄>
$ down/up 일회용 테스트 → <결과 1줄>
### 확인 필요 / 한계
```

### 작성 예시

```
## sample-service collector 컨테이너화
### 상태 분류: DB는 외부(기존 postgres 컨테이너) / 토큰 캐시→named volume / 설정→Infisical 주입
### 이미지: python:3.12-slim 2스테이지, 1.31GB → 287MB
### compose 6종: collector:0.3 고정 / kiwoom-token-cache 볼륨 / env_file 레포 밖 / mem 512m / 로그 10m×3 / healthcheck는 runs 테이블 최신성 쿼리(확인 필요: 적절 임계)
### 검증:
$ python scripts/docker_check.py . → total: 0 finding(s)
$ docker build → 287MB
$ docker compose up -d && ps → collector (healthy)
$ down/up 테스트 → 토큰 캐시 유지·정상 수집 확인
### 확인 필요: 새벽 배치 시간대 메모리 피크 실측 후 한도 보정
```

❌ "일단 latest로 띄우고 볼륨은 나중에" (재생성 = 전손 예약)
✅ "상태 분류 표 → 6종 세트 → down/up 일회용 테스트"

### 사용자가 권고를 거부하면

- "멀티스테이지 귀찮아, 한 방에" → 따르되 `.dockerignore`와 slim 베이스만 제안(비용 1분, 효과 큼). 거부 시 크기 리스크 1줄 기록(partial).
- "latest 쓸래" → 재생성 시 무단 업그레이드 리스크 1회 고지, 그래도 원하면 적용하되 compose 주석에 그 결정 기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

### 판단이 막힐 때 (확인 요청 4요소)

상태 분류(무엇이 볼륨/환경/무상태인지)나 자원 한도는 서비스 동작과 호스트 사양을 아는 사용자만 정할 수 있다 — 모르면 볼륨 누락·OOM 룰렛이 된다. 묶어서 묻는다:
- **누가**: 사용자(서비스 상태 구조·홈서버 사양·ServerManager 레포 관례 소유자).
- **언제**: 상태 분류 단계(워크플로우 1) — 데이터 위치가 불명하거나, 메모리 피크 실측값이 없어 한도를 못 정할 때.
- **어떻게**: "현재 항목 / 추측값 / 근거 / 기대 답변"으로. 예) "DB 데이터를 named volume에 둔다고 가정했는데(근거: 상태 영속 필요), 외부 호스트 경로 bind면 소유권 정렬이 필요 — 어디에 둡니까?"
- **기대값**: 상태 위치·메모리 한도·기존 compose 관례 중 하나. 받으면 확정값으로, 못 받으면 가장 안전한 가정(상태는 named volume·한도는 보수적·`unless-stopped`)으로 진행 + `down/up` 일회용 테스트로 볼륨 누락만은 반드시 검증.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — "디스크 풀"은 예고 없이 오지 않는다 (운영 일반 + 공개 실증)

컨테이너 로그 무제한 + 떠돌이 이미지 누적으로 인한 디스크 고갈은 홈서버·소규모 운영의 최빈 장애 패턴이다(개별 기업 포스트모템보다 Docker 공식 문서가 json-file 로테이션 기본값 부재를 명시해온 역사가 그 증거 — 28.x·29.x 모두 json-file은 여전히 로테이션 무설정이 기본이며, 공식은 rotation 내장 `local` 드라이버를 권장). 더 유명한 변종이 **Knight Capital(라우터 케이스)의 "8대 중 1대만 구버전"** — 컨테이너 이전 시대의 사고지만, 태그 고정 없는 latest 운영이 정확히 같은 상태(호스트마다 다른 버전)를 재생산한다. 교훈: ① 로테이션·태그 고정은 "나중에"가 없는 설정이다 — 사고가 나야 발견되는 종류라서 ② `docker system df`를 주기 점검에 — 디스크는 갑자기 차는 게 아니라 조용히 찬다.

## 사용자 환경 적용 (홈서버 ubuntu-01)

- 14개 서비스 운영 중 — 신규 서비스는 ServerManager 레포의 기존 compose 관례(네트워크·볼륨 명명)가 이 스킬보다 우선. 이 스킬은 그 레포에 없는 결정(한도·로그·healthcheck)을 채울 때.
- 전역 로그 로테이션은 `/etc/docker/daemon.json`에 한 번 — 서비스별 반복보다 누락이 없다(적용엔 데몬 재시작 + 기존 컨테이너 재생성 필요).
- Windows 개발 PC에서 빌드 → 홈서버 배포: 라인엔딩(CRLF가 엔트리포인트 스크립트를 깨뜨림 — `.gitattributes`로 sh는 LF 강제)과 플랫폼(`--platform linux/amd64`) 명시.

## 레퍼런스

- `scripts/docker_check.py` — Dockerfile·compose 냄새 검출기: latest 태그·COPY 순서·ENV 비밀·로그 로테이션 부재 (표준 라이브러리만, `python scripts/docker_check.py` 데모)
- `references/dockerfile-patterns.md` — 멀티스테이지 표준형(python/node)·캐시 마운트·비root 유저·.dockerignore 상세
- `references/compose-operations.md` — compose 6종 세트 표준형·네트워크·healthcheck 패턴·일상 운영 명령
- `references/evidence-checklist.md` — 출처 + 출고 전 체크리스트

## 한계

단일 호스트 compose 규모 중심 — 멀티 노드·오토스케일은 dev-kubernetes(홈서버 규모에선 후순위가 맞다). 이미지 보안 스캔·서명은 dev-dependency-security 영역. Windows 컨테이너는 다루지 않는다(리눅스 컨테이너 전제).
