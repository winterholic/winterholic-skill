# evidence + 출고 전 체크리스트

## 실증·출처

- **Pydantic 2.1 호환성 사태 (2023-07)**: fastapi/fastapi Discussion #9942(https://github.com/fastapi/fastapi/discussions/9942, 2026-06-21 실재 확인) — Pydantic 2.1.0 업데이트로 `Annotated`+`Query` 의존성을 쓰던 FastAPI 앱이 import 시점에 기동 실패. SKILL.md 실전 케이스의 원 출처. 교훈: 프레임워크-코어 쌍 버전 고정 + lock 파일.
- **FastAPI 0.126~0.128 (2026)**: Pydantic v1 지원 단계 제거(0.126.0에서 최소 `pydantic>=2.7.0`, 0.128.0에서 `pydantic.v1` shim 제거), Pydantic 반환 타입의 Rust 경로 직렬화로 JSON 응답 성능 개선. **검증(2026-06-21)**: 현재 최신은 0.138.0(2026-06-20 릴리스)이고 최소 의존성은 `pydantic>=2.9.0`로 올라옴 — 출처: FastAPI release notes(https://fastapi.tiangolo.com/release-notes/, 공식 1차) + PyPI `requires_dist`(https://pypi.org/pypi/fastapi/json). SKILL.md 라벨을 0.138로 동기화함. 확인 필요: 사용 시점 최신 버전 재확인.
- **async def 내 동기 호출의 루프 정지**: FastAPI 공식 문서 "Concurrency and async / await" — `def` 엔드포인트는 외부 스레드풀에서 실행됨을 명시. "전부 async가 빠르다"가 미신인 공식 근거.
- **asyncio 태스크 GC·블로킹 검출**: dev-python `references/async-concurrency.md` 참조(중복 방지).
- **BackgroundTasks 비영속**: Starlette/FastAPI 공식 문서 — 응답 후 같은 프로세스에서 실행, 재시도·영속 보장 없음. "무거운 작업은 Celery 등 별도 도구" 권고가 공식 문서에 명시.
- 오픈소스 차용 표기: microsoft/fastapi-router-py(VoltAgent 색인, CRUD+auth 라우터 스캐폴딩 구성 참고), full-stack-fastapi-template(tiangolo 공식 — 모델 3종 세트·디렉토리 구조의 원형). 본문 비복사, 구조 참고만. **역흡수**: 두 소스 모두 sync/async 판정 가이드와 BackgroundTasks 유실 경고 부재 → 본 스킬 안티패턴 1·5의 차별점.

## 출고 전 체크리스트 (엔드포인트 추가·수정 시)

코드 리뷰·셀프 점검용. 전 항목 Y 또는 "해당 없음"이어야 출고.

- [ ] 모든 라우트에 response_model 또는 명시적 `response_model=None` (의도 표명)
- [ ] 입력·출력 모델 분리 (한 모델 겸용이면 사유 1줄)
- [ ] async def 엔드포인트 안에 동기 I/O 없음 (`fastapi_check.py` 0건)
- [ ] DB 세션은 yield 의존성, 풀·클라이언트는 lifespan (전역 없음)
- [ ] 외부 호출 전부 타임아웃 명시
- [ ] 목록 응답에 limit 상한 (무제한 조회 불가)
- [ ] 422 외 도메인 에러가 핸들러로 일관 형식
- [ ] 시크릿은 SecretStr — 로그에 원문 노출 경로 없음
- [ ] CORS 오리진 명시 목록 (운영 빌드에 `*` 불가)
- [ ] deprecated 패턴 없음: on_event·class Config·parse_obj·@validator
- [ ] TestClient 스모크 테스트 최소 1개 (정상 1 + 검증 실패 1 권장)
- [ ] OpenAPI(/docs) 열어서 신규 엔드포인트 스키마 눈 확인

## 점검 주기 (부패 중간 등급 — 반기)

- FastAPI·Pydantic 현재 버전 vs SKILL.md 라벨 비교 → release notes의 breaking 항목만 훑기
- `fastapi_check.py`의 검출 룰이 여전히 유효한지 (deprecated 목록 갱신)
- 체크리스트에 ledger발 신규 항목 있는지 (3회 룰)
