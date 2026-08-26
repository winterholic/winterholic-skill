# evidence + 출고 전 체크리스트

## 실증·출처

- **Twitter (2018)·Facebook (2019) 평문 비밀번호 로그 사건** — 양사 공식 발표(침해 아닌 로깅 실수, 전 사용자 재설정/통지 권고). SKILL.md 실전 케이스. 전체 객체 로깅·마스킹 누락의 실증. (웹 확인 2026-06: Krebs on Security 등 다수 1차 보도. Twitter는 해싱 전 평문이 내부 로그에 기록된 버그, Facebook은 Facebook Lite 앱이 비밀번호를 암호화 전 로그에 기록한 것이 근본 원인 — 둘 다 "로깅 경로"의 누출.)
  - https://krebsonsecurity.com/2018/05/twitter-to-all-users-change-your-password-now/ — Twitter 사건 1차 보도
  - https://krebsonsecurity.com/2019/03/facebook-stored-hundreds-of-millions-of-user-passwords-in-plain-text-for-years/ — Facebook 사건 1차 보도
- **12-Factor App XI. Logs** (https://12factor.net/logs) — "로그는 이벤트 스트림, 앱은 stdout로 쓰고 라우팅은 환경에" 원칙(파일 직접 관리 안 함의 근거). 원문 공식 사이트, 웹 확인 2026-06.
- **Python logging 공식 문서 — `Logger.exception` / structured logging** + **structlog 문서** — 구현의 1차 출처. 웹 확인 2026-06.
  - https://docs.python.org/3/library/logging.html — `Logger.exception`(stack 자동 포함), `extra=`
  - https://docs.python.org/3/library/contextvars.html — 상관 ID 전파에 쓰는 contextvars(3.7+, async·스레드 격리)
  - https://www.structlog.org/en/stable/exceptions.html — structlog 예외/traceback 처리. JSON 트레이스백은 `dict_tracebacks` 프로세서(현 stable 26.x). 직접 JsonFormatter가 과하면 권장.
- **OWASP Logging Cheat Sheet** (https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) — 무엇을 로깅하고 무엇을 안 할지(비밀번호·세션 ID·민감 PII·액세스 토큰 등 제외)의 표준. 웹 확인 2026-06. (별도의 "Logging Vocabulary Cheat Sheet"와 혼동 주의 — 이쪽이 본 스킬이 가리키는 문서.) 상위 맥락은 OWASP Top 10 **A09**(2021 "Security Logging and Monitoring Failures" → 2025판 "Security Logging and Alerting Failures"로 개명).
- **Sentry — 민감정보 스크러빙** (https://docs.sentry.io/platforms/python/data-management/sensitive-data/) — 웹 확인 2026-06. `before_send` 수동 스크러빙에 더해, 기본 활성화된 `EventScrubber`가 비밀번호·인증·세션·쿠키 등 denylist를 자동 제거하고 `send_default_pii=False`(기본)면 PII denylist까지 적용 — 마스킹 2차선의 근거.
- 오픈소스 차용 표기: 로깅 가이드 다수(색인 인지, 본문 비복사). **역흡수**: 전체 객체 로깅 금지의 검출화·상관 ID를 run_id와 통합·3축 분업(로그 vs 메트릭) 명시·레벨 판정 질문 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (로깅 출고 시)

- [ ] 운영 로그가 구조적(JSON) + 공통 필드
- [ ] 비밀·PII 마스킹 (전체 객체 로깅 0) — `log_scan.py` 0건
- [ ] 모든 로그에 correlation_id (요청·배치 단위)
- [ ] 에러는 logger.exception(스택) + 도메인 필드
- [ ] 레벨 규약 준수 (WARNING/ERROR 경계 합의)
- [ ] f-string 메시지 대신 구조적 필드
- [ ] 핫패스 루프 개별 로깅 0 (집계/샘플)
- [ ] stdout 출력 + 로테이션은 인프라 위임
- [ ] 샘플 로그 1건 실제 확인 (JSON·ID·마스킹 동작)
- [ ] (Sentry 시) before_send PII 스크러빙

## 점검 주기 (부패 느림 — 연 1회)

- 로그에 PII 누출 표본 점검(grep 민감 패턴)
- 로그량·보존 비용 추이 / 레벨 분포(ERROR 남발 여부)
