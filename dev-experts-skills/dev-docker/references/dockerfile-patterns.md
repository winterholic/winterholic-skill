# Dockerfile 패턴 — 멀티스테이지 표준형·캐시·비root (SKILL.md 비중복)

## Python 멀티스테이지 표준형

```dockerfile
# --- builder: 의존성 빌드만 ---
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
# BuildKit 캐시 마운트: pip 캐시가 레이어에 안 남고 빌드 간 재사용
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --wheel-dir /wheels -r requirements.txt

# --- runtime: 실행에 필요한 것만 ---
FROM python:3.12-slim
RUN useradd --create-home --uid 1000 app
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/* && rm -rf /wheels
COPY --chown=app:app . .
USER app
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "collector.run"]
```

- `PYTHONUNBUFFERED=1`: 로그가 버퍼에 갇혀 죽기 직전 로그가 안 보이는 함정 방지.
- CMD는 exec form(`["...", "..."]`) — shell form은 PID 1이 sh가 되어 SIGTERM이 앱에 안 간다(graceful shutdown 실패 → 강제 kill까지 10초 대기).
- 빌드 시점 비밀이 불가피하면: `RUN --mount=type=secret,id=pip_token pip install ...` — 레이어에 안 남는다.

## Node 표준형 (요지만)

```dockerfile
FROM node:22-slim AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-slim
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
USER node
CMD ["node", "dist/main.js"]
```

`npm install`이 아니라 `npm ci`(lock 그대로, 재현성) — pip의 lock 철학과 동일.

## .dockerignore 기본형

```
.git
.venv
__pycache__
*.pyc
node_modules
.env*
tests/
*.md
```

- `.env*` 제외가 안티패턴 4(비밀 굽기)의 마지막 방어선 — `COPY . .`가 있어도 안 들어간다.
- node_modules 제외는 빌드 컨텍스트 전송 시간 문제이기도 — 컨텍스트가 수백 MB면 build가 시작도 전에 느리다.

## 캐시 동작 정밀 규칙

- COPY/ADD는 **파일 내용 해시**로 캐시 판정, RUN은 **명령 문자열**로만 판정 — `RUN apt-get update`는 어제 결과를 영원히 재사용한다. 갱신이 필요하면 같은 RUN에 묶어라: `RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*`.
- 멀티스테이지에서 최종 이미지 크기는 **마지막 스테이지의 레이어만** 계산 — builder가 아무리 커도 무관.
- `ARG`는 캐시 키에 들어간다 — 매번 변하는 값(빌드 시각)을 ARG로 받으면 캐시 전멸. 버전 라벨은 LABEL로.

## 이미지 크기 진단

```
docker image ls <이름>                 # 최종 크기
docker history <이미지>                # 레이어별 크기 - 비만 레이어 색출
docker system df                       # 전체 디스크 사용 (이미지/컨테이너/볼륨/캐시)
```

크기 줄이기 우선순위: ① .dockerignore ② slim 베이스 ③ 멀티스테이지 ④ apt 캐시 삭제 — distroless·alpine은 그 다음(호환 비용 대비).
