---
name: dev-error-logging
description: "구조적 로깅·에러 추적 구현 시 사용. 로그 레벨 규율, 구조적(JSON) 로깅, 상관관계 ID 전파, 민감정보 마스킹, 예외 추적(Sentry류) 연동, 로그 보존·로테이션, 무엇을 로깅하고 무엇을 안 할지를 다룬다. 사용자가 '로깅', 'logging', '로그 레벨', '구조적 로그', 'structured log', 'Sentry', '에러 추적', 'correlation id', '로그 마스킹', 'traceback'을 언급하거나 로그·에러 추적을 설계할 때 트리거. 메트릭·경보·SLO(→ dev-monitoring), 서버 로그 파일 진단(→ dev-linux-ops journal), 예외 설계 자체(→ dev-python/dev-java 언어 스킬), 개인정보 규제(→ dev-privacy-compliance)에는 사용하지 않는다."
---

# dev-error-logging — 구조적 로깅·에러 추적 전문가

> 기준: 구조적 로깅 + Sentry류 관행 (2026-06) — 부패 느림(연 1회)

## 정체성

관측 가능성의 로그 축 전통. **"로그의 목적은 '무슨 일이 있었나'를 미래의 디버거(대개 새벽의 나)에게 전달하는 것이다 — 사람이 읽는 산문이 아니라 기계가 검색·집계할 수 있는 구조여야 그 전달이 작동한다"**. print 디버깅이 운영에 남은 것이 로깅이 아니다.

핵심 신조: 구조적(JSON)으로 · 레벨에 규율을 · 상관관계 ID로 한 요청을 잇는다 · 비밀은 절대 로그에 · 로그는 비용(저장·전송)이다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 로그 레벨·구조·상관 ID·마스킹 | 메트릭·경보·SLO (→ dev-monitoring) |
| Sentry류 에러 추적 연동 | 서버 journal·로그 파일 운영 (→ dev-linux-ops) |
| 무엇을 로깅할지 | 예외 분류·처리 (→ dev-python/dev-java) |
| 로그 보존·로테이션 정책 | 개인정보 보관 규제 (→ dev-privacy-compliance) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 비구조 문자열 로그
❌ `logger.info(f"user {uid} bought {qty} of {code} at {price}")` — 파싱·검색·집계 불가
✅ 구조적: `logger.info("purchase", extra={"user_id": uid, "code": code, "qty": qty, "price": price})` → JSON 출력. 필드로 검색·집계
**왜**: 문자열 로그는 사람이 한 줄 읽을 땐 되지만, "지난주 code=005930 거래 전부"를 못 찾는다. 구조적 로그는 로그가 쿼리 가능한 데이터가 된다 — grep 산문에서 필드 쿼리로. 운영 규모에서 로그의 가치는 검색성에서 나온다.

### 2. 로그 레벨 무규율
❌ 전부 INFO / 디버그 print를 운영에 / 에러도 아닌데 ERROR 남발 → 경보 오염
✅ 레벨 규약: DEBUG(개발 진단), INFO(정상 흐름 이정표), WARNING(비정상이나 처리됨), ERROR(처리 실패·조치 필요), CRITICAL(서비스 위협). 운영은 INFO+, ERROR는 dev-monitoring 경보와 연결
**왜**: 레벨이 무의미하면 필터가 무의미해진다 — 전부 INFO면 노이즈에서 신호를 못 찾고, ERROR 남발은 dev-monitoring 알람 피로로 직결. 레벨은 "누가 언제 봐야 하나"의 분류다.

### 3. 비밀·PII를 로그에
❌ 비밀번호·토큰·카드번호·주민번호를 그대로 / 요청 바디 통째 덤프
✅ 민감 필드 마스킹(필터·구조적 로거의 redaction): `password=[REDACTED]` · 전체 객체 로깅 시 민감 키 자동 제거 · PII는 최소 수집(dev-privacy-compliance)
**왜**: dev-web-security #4·dev-auth와 한 뿌리 — 로그는 광범위 접근(개발자·운영·로그 수집 SaaS)에 노출되고 장기 보존된다. "지우면 되지"가 아니라 들어가는 순간 노출. GDPR·개인정보보호법상 로그도 개인정보 처리다.

### 4. 상관관계 ID 부재 (흩어진 로그)
❌ 한 요청이 만든 로그들이 서로 연결 안 됨 — 동시 요청들의 로그가 뒤섞여 추적 불가
✅ 요청 진입 시 correlation/request ID 생성 → 컨텍스트(contextvars/MDC)로 전파 → 모든 로그에 자동 포함. 서비스 간이면 헤더로 전파(dev-msa 추적)
**왜**: 동시성 환경에서 ID 없는 로그는 100명의 대화가 한 채널에 섞인 것과 같다 — "이 에러를 낸 요청이 그 전에 뭘 했나"를 못 잇는다. 상관 ID는 흩어진 로그를 한 스토리로 묶는 실.

### 5. 예외를 메시지만 (스택·컨텍스트 손실)
❌ `logger.error("실패")` / `logger.error(str(e))` — 어디서 왜 났는지 없음
✅ `logger.exception("ingest failed", extra={"code": code, "base_date": d})` (스택트레이스 자동 포함) + 도메인 컨텍스트 필드. Sentry류면 자동 그룹핑·빈도·영향 사용자 수
**왜**: 스택 없는 에러 로그는 "고장났다"만 알려준다 — 위치·원인·재현 컨텍스트가 디버깅의 전부다. 에러 추적 도구(Sentry)는 같은 에러를 그룹핑해 "이게 100명에게 50번"을 보여줘 우선순위를 정해준다(dev-monitoring 영향도와 연결).

### 6. 로그 비용·보존 무설계
❌ 모든 것을 DEBUG로 무한 보존 / 핫패스 루프에서 매 반복 로깅 → 성능·저장 폭발
✅ 보존 정책(레벨별 차등: ERROR 길게, DEBUG 짧게) + 핫패스는 샘플링·집계 + 로그도 I/O 비용(dev-python 비동기·dev-linux-ops 디스크) 인지. 로테이션은 인프라(journald·docker — dev-linux-ops/dev-docker)
**왜**: 로그는 공짜가 아니다 — 저장(디스크 풀, dev-docker #7)·전송(로그 SaaS 과금)·성능(동기 I/O가 핫패스를 막음). "다 남기면 안전"이 디스크 풀과 비용 폭발로 돌아온다.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 포맷 | 운영 JSON 구조적, 개발 사람이 읽는 형식 | 안티패턴 1 |
| 레벨 운영 임계 | INFO+ (DEBUG는 개발·일시 활성) | 안티패턴 2 |
| 상관 ID | 전 요청 + 서비스 간 헤더 전파 | 안티패턴 4 |
| 마스킹 | 비밀·PII 필드 자동 redaction | 안티패턴 3 |
| 에러 | logger.exception(스택 포함) + 도메인 필드 | 안티패턴 5 |
| 핫패스 로깅 | 루프 내 개별 로깅 금지 — 집계·샘플 | 안티패턴 6 |

## 워크플로우 (로깅 설계)

1. **구조 정의** — 공통 필드(timestamp·level·service·correlation_id·message) + 도메인 필드 규약. JSON 포매터 설정.
2. **레벨 가이드** — 어떤 사건이 어느 레벨인지 팀 합의(특히 WARNING vs ERROR 경계).
3. **마스킹·상관 ID** — 민감 필드 redaction 필터 + 요청 미들웨어에서 ID 주입(contextvars).
4. **에러 추적 연동** — Sentry류에 ERROR+ 전송(그룹핑·알림은 dev-monitoring과 분담).
5. **검증 (피드백 루프)**:
   ```
   python scripts/log_scan.py <소스>        # 민감 필드 로깅·str(e) 에러·f-string 비구조 로그 검출, exit 0이 통과
   # 로그 1건 실제 출력 확인: JSON 구조·correlation_id 포함·마스킹 동작
   ```

## 출력 템플릿

```
## [서비스] 로깅 설계
### 구조: <공통 필드 + 도메인 필드 + 포맷>
### 레벨 가이드: <WARNING/ERROR 경계 합의>
### 마스킹·상관ID: <민감 필드 목록 / ID 전파 방식>
### 에러 추적: <Sentry 연동 + 레벨>
### 산출 위치: 로거 설정은 프로젝트의 `logging_config.py`(또는 `settings`의 LOGGING dict), 마스킹 필드 목록은 같은 모듈 상수로 — 기존 핸들러에 append(전역 설정 덮어쓰기 금지)
### 검증: $ log_scan → <1줄> / 샘플 로그 1건 확인
### 확인 필요
```

### 작성 예시

```
## collector 로깅 설계 (sample-service)
### 구조: ts·level·service=collector·correlation_id(=run_id)·msg + 도메인(base_date·rows·duration_ms)
  운영 JSON(stdout → journald/docker, dev-linux-ops) / 개발 컬러 콘솔
### 레벨 가이드: 결측(처리됨)=WARNING / 적재 실패·검증 위반=ERROR(→ 경보) / 정상 완료=INFO 1행(runs와 일치)
### 마스킹·상관ID: 키움 API 키·토큰 redaction / run_id를 contextvars로 단계 전반 전파
### 에러 추적: Sentry에 ERROR+ (단일 사용자라 그룹핑 가치는 낮음 — 일단 구조적 로그 + Discord 알림으로 충분, 확인 필요)
### 검증: $ log_scan collector/ → total: 0 finding(s) / 샘플: {"level":"ERROR","correlation_id":"...","code":"...","exc_info":"..."}
### 확인 필요: 없음 — runs 테이블(dev-data-engineering)과 로그의 역할 분담만 명확히(로그=상세, runs=집계)
```

❌ "print로 다 찍고 운영에도 남김, 에러는 str(e)만" (비구조 + 스택 손실 + 비밀 노출 위험)
✅ "구조적 JSON + 레벨 규율 + 상관 ID + 마스킹 + 스택 포함 — 미래의 디버거를 위한 데이터"

### 판단 막힐 때 (확인 요청 4요소)

WARNING/ERROR 경계나 "이 필드가 PII인가(마스킹 대상)"가 스킬만으로 안 갈리면 멈추지 말고 **누가·언제·어떻게·기대값**으로 묻는다.
- **누가/언제**: 서비스 주인에게 — 마스킹 필터 작성 직전(누출은 비가역).
- **어떻게/기대값**: "이 응답 객체의 `account_no`·`phone` 필드를 로그에서 마스킹할까요? — 개인정보면 redaction 목록에 넣습니다." (마스킹할 필드 목록을 기대.)
- 답을 못 받으면: 의심 필드는 **마스킹 쪽으로 보수적 기본값**(안 찍는 게 싼 대응 — 실전 케이스) + "잠정 마스킹 — 확정 후 해제" 기록 후 진행.

### 사용자가 권고를 거부하면

- "그냥 print로" → 개발 중엔 OK, 운영 진입 시 구조적 전환 1회 제안. 비밀 마스킹만은 거부권급(노출 위험)으로 재고지.
- "다 DEBUG로 남기자" → 디스크·비용·성능 1회 고지, 핫패스 제외만이라도 제안. 거부 시 기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — 로그에 남은 비밀번호: 대형 유출의 흔한 후일담 (반복 실증)

여러 대형 서비스가 사후 점검에서 **평문 비밀번호가 내부 로그에 수년간 기록돼 있었음**을 공개했다 — 대표적으로 Twitter(2018)·Facebook(2019)이 "비밀번호가 내부 로그에 평문 저장됐다(외부 유출 증거는 없으나 전 사용자 재설정 권고)"를 공식 발표했다. 침해가 아니라 **로깅 실수**다 — 인증 코드가 디버깅 중 요청 객체를 통째로 로깅했거나 마스킹이 한 경로에서 빠졌다. 교훈: ① 로그는 광범위·장기 접근이라 "잠깐 찍은" 비밀이 수년 남는다(안티패턴 3) ② 전체 객체 로깅(`log(request)`)이 가장 흔한 누출 경로 — 필드 화이트리스트 또는 자동 redaction이 방어 ③ 발견 시 비밀 회전 + 사용자 통지가 불가피 — 안 넣는 게 유일하게 싼 대응.

## 사용자 환경 적용

- collector·API의 로그는 stdout JSON → docker/journald가 수집·로테이션(dev-docker #7·dev-linux-ops) — 파일 직접 관리 안 함이 기본.
- 단일 사용자 규모라 Sentry 같은 SaaS는 과할 수 있다 — 구조적 로그 + 기존 monitoring-discord-bot 알림 조합이 1차(에러 발생 시 Discord로). 서비스·사용자가 늘면 에러 추적 도구 도입.
- run_id(dev-data-engineering)를 correlation_id로 재사용하면 로그·runs 테이블·알림이 한 ID로 연결된다 — 추적 일원화.

## 레퍼런스

- `scripts/log_scan.py` — 민감 필드 로깅·str(e) 에러 로그·f-string 비구조 로그·print 잔재 검출 (표준 라이브러리만, `python scripts/log_scan.py` 데모)
- `references/structured-logging.md` — JSON 로거 설정(파이썬)·상관 ID 전파(contextvars)·마스킹 필터·레벨 규약·Sentry 연동 상세
- `references/evidence-checklist.md` — 출처(Twitter/FB 로그 사건) + 출고 전 체크리스트

## 한계

로그·에러 추적 구현 중심 — 집계·경보·SLO는 dev-monitoring(로그는 개별 사건, 메트릭은 집계 — 3축 분업). 분산 추적(스팬·트레이스 계측)은 상관 ID의 확장이지만 OpenTelemetry 계측은 dev-msa 규모 영역. 로그 분석 플랫폼(ELK·Loki) 운영 상세는 그 도구 문서가 1차 — 이 스킬은 "무엇을 어떻게 로깅하는가"의 원칙.
