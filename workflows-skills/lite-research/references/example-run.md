# external std 실전 사례 — 2026-06-10 스모크 테스트 (실측 원문 발췌)

> 실제 Workflow 실행 결과다(가상 아님). 3 에이전트(공식 서처 + 현장 헌터 + 배치 검증자), 123,926 서브에이전트 토큰, 290초, 도구 호출 31회.
> 용도: 수집자 claim의 밀도·sourceType 사용법·gaps 정직 표기·배치 검증의 판정 모양에 대한 실물 anchor.

## 입력 (메인이 1회 수집해 넘긴 args)

- **question**: FastAPI `@app.on_event`는 어떤 deprecated 상태이고 lifespan 전환이 필수인가? 전환 시 알려진 함정은?
- **kind/depth**: external / std (버전·날짜 민감한 의사결정 입력 → 검증 포함)
- **context**: 운영 중 FastAPI 백엔드(Python 3.11+, uvicorn)가 on_event 사용 중. 알고 싶은 것 ①제거 예정 여부(버전 명시) ②공식 권장 전환 방식 ③실사용 함정(테스트·미들웨어·mount)

## 공식 서처 claim (발췌 — 이 밀도가 기준)

- `[high/code]` 최신 0.136.3(2026-05-23) 기준 소스에 on_event 잔존 + `@deprecated` 데코레이터만 부착 — *src: raw.githubusercontent.com .../routing.py + releases/latest API* ← **소스를 직접 읽어 행 번호까지 특정**
- `[medium/inference]` 제거 일정은 소스·문서 어디에서도 미발견 — "**증거를 못 찾음이지 제거 계획 없음의 확증이 아님**" ← 부재 증명의 한계를 스스로 명시
- `[high/official]` lifespan 제공 시 on_event 핸들러 무음 미실행 — "It's all lifespan or all events, not both" *src: fastapi.tiangolo.com/advanced/events/*
- gaps 4건 정직 표기: Starlette 쪽 일정 미확인, 0.93.0 정확 릴리스일 fetch 생략 사유, maintainer 직접 발언 미발견, 멀티워커 동작 미조사

## 현장 헌터 claim (발췌 — 공식이 안 말하는 것)

- `[high/community]` 무음 스킵이 "디버깅 정말 어렵다" 보고 다수 (Discussion #9604, maintainer가 Starlette 책임으로 정리)
- `[medium/community]` 서드파티 조합 위험 실증: fastapi-mqtt #87, langserve #441, fastapi-users #1312 — 라이브러리가 on_event 훅을 쓰면 앱의 lifespan 전환이 그 훅을 조용히 죽임
- `[high/official+community]` TestClient를 `with` 없이 쓰면 lifespan 미실행 → 404류 비직관 실패 (#14198); httpx AsyncClient+ASGITransport도 lifespan 무시 → asgi-lifespan 필요 (#2003)

## 배치 검증 결과 (검증자 1명, 1패스)

- 19 claims → **17 confirmed · 2 unverifiable · 0 refuted · conflicts 0**
- unverifiable 2건은 모두 inference형 — "그럴듯하지만 직접 증거 없음"을 이유와 함께 명시 (검증된 척 안 함)
- conflicts 0 → 에스컬레이션 불필요로 종결

## 이 사례에서 배울 것

1. **sourceType이 곧 가중치다** — 종합에서 official/code가 기둥, community는 함정 발굴, inference는 할인. 두 수집자가 독립적으로 같은 결론에 수렴하면(여기선 "deprecated, 제거 일정 없음") 신뢰도가 한 단계 오른다.
2. **현장 헌터의 가치는 공식 문서의 행간** — "혼용 시 무음 스킵"은 공식 문서도 말하지만, *서드파티 라이브러리의 훅까지 죽는다*는 실전 파급은 이슈 트래커에서만 나왔다.
3. **gaps는 답의 일부다** — "멀티워커 동작 미조사"를 숨겼다면 운영 전환 결정에서 구멍이 됐다.
4. **예산 내 깊이 우선이 동작한다** — 도구 호출 31회로 소스 코드 직독 + 이슈 5개 교차 확인까지 도달. 넓게 훑는 대신 유력 리드를 팠다.
