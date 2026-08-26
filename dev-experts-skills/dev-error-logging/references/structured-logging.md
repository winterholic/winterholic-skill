# 구조적 로깅 구현 — JSON 로거·상관 ID·마스킹·Sentry (SKILL.md 비중복)

## 파이썬 구조적 로거 설정

```python
import logging, json, contextvars
request_id_var = contextvars.ContextVar("request_id", default="-")

class JsonFormatter(logging.Formatter):
    SENSITIVE = {"password", "token", "secret", "api_key", "card", "ssn"}
    def format(self, record):
        base = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "service": "collector",
            "correlation_id": request_id_var.get(),
            "msg": record.getMessage(),
        }
        # record.extra 필드 병합 + 민감 키 마스킹
        for k, v in getattr(record, "fields", {}).items():
            base[k] = "[REDACTED]" if k.lower() in self.SENSITIVE else v
        if record.exc_info:
            base["exc"] = self.formatException(record.exc_info)
        return json.dumps(base, ensure_ascii=False, default=str)
```

- 표준 `extra=`는 record 속성으로 들어가므로 커스텀 키(`fields=`) 또는 structlog/loguru 같은 라이브러리가 더 깔끔 — 직접 구현이 과하면 structlog 권장.
- stdout으로만 출력 → 수집·로테이션은 인프라(journald/docker — dev-linux-ops/dev-docker). 앱이 파일·로테이션을 직접 관리하지 않는다.
- 개발은 사람이 읽는 포맷, 운영은 JSON — 환경변수로 포매터 분기(dev-django 설정 분리와 동일).

## 상관관계 ID 전파

```python
# 미들웨어/진입점에서 1회 생성·설정
import uuid  # 주의: 워크플로 스크립트가 아닌 실제 앱에서는 OK
def middleware(request, call_next):
    rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex  # 외부 ID 있으면 이어받기
    token = request_id_var.set(rid)
    try:
        response = call_next(request)
        response.headers["X-Request-ID"] = rid  # 응답에 반영(클라 디버깅)
        return response
    finally:
        request_id_var.reset(token)
```

- contextvars는 async·스레드 안전(threadlocal의 현대판) — 동시 요청이 서로의 ID를 안 본다.
- 서비스 간(dev-msa): X-Request-ID 헤더로 전파 → 분산 추적의 경량 버전. 배치(collector)는 run_id를 correlation_id로(dev-data-engineering 연결).
- Java/Spring은 MDC(`MDC.put("correlationId", ...)`)가 등가물.

## 마스킹 전략

| 방식 | 적용 |
|---|---|
| 키 기반 redaction | 민감 키 이름 목록(위 SENSITIVE) — 가장 단순·견고 |
| 화이트리스트 | 로깅할 필드만 명시(전체 객체 로깅 금지) — 가장 안전 |
| 정규식 마스킹 | 카드번호·주민번호 패턴 — 값 기반(키 모를 때) |

- 1순위는 **전체 객체 로깅 안 하기**(화이트리스트) — Twitter/FB 사건의 원인이 객체 통째 로깅. `log(user)` 대신 `log("...", extra={"user_id": user.id})`.
- 로깅 라이브러리·Sentry 모두 `before_send`/processor 훅으로 전역 마스킹 한 겹 더 — 누락 대비 안전망.

## 레벨 규약 (WARNING vs ERROR 경계 — 가장 흔한 혼동)

| 레벨 | 기준 | 예 |
|---|---|---|
| DEBUG | 개발 진단, 운영 off | 변수 값·분기 추적 |
| INFO | 정상 흐름 이정표 | "수집 완료 2431행" |
| WARNING | 비정상이나 **자동 처리됨**, 지금 행동 불요 | 결측 발견→플래그, 재시도 1회 후 성공 |
| ERROR | 처리 실패, **조치 필요** | 적재 실패, 검증 위반 |
| CRITICAL | 서비스 위협 | DB 연결 전면 실패 |

판정 질문: "이걸로 사람이 지금 뭔가 해야 하나?" 예=ERROR(→ dev-monitoring 경보), 아니오=WARNING 이하. ERROR 남발이 알람 피로의 로그 측 원천.

## Sentry류 에러 추적 연동

- ERROR+ 자동 캡처 + 스택·컨텍스트·영향 사용자 수 그룹핑 — "같은 에러 100명 50번"을 보여줘 우선순위(dev-monitoring 영향도).
- `before_send`로 PII 스크러빙(SDK 기본 `EventScrubber`가 비밀번호·인증·쿠키 등 denylist 자동 제거 + `send_default_pii=False`가 기본이나, 도메인 필드는 직접 추가) — 마스킹 2차선. (Sentry Python 공식 docs, 확인 2026-06)
- 릴리스·환경 태그로 "어느 배포부터 이 에러"(dev-cicd 배포 식별자 연결).
- 소규모(단일 사용자)는 구조적 로그 + 알림으로 충분 — Sentry는 사용자·서비스 규모가 생길 때.
