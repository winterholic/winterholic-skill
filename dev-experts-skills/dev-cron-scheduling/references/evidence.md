# dev-cron-scheduling evidence — 장애·실증 사례

## 1. GitLab (2017-01-31) — 백업 5중 침묵 실패 (공식 포스트모템·생중계 복구)

- **무슨 일**: 레플리카 지연 대응 중 피로 상태의 엔지니어가 프라이머리 호스트에서 데이터 디렉토리 삭제. 복구 시도에서 발견된 것: ① 정기 pg_dump — PostgreSQL 메이저 버전 불일치로 **수개월간 빈 파일 생성**(실패 알림은 메일 설정 오류로 미발송) ② S3 백업 — 비어 있음 ③ LVM 스냅샷 — 우연히 6시간 전 수동본만 유효 ④⑤ 기타 메커니즘도 각각 구멍. 6시간 데이터 유실로 복구.
- **이 스킬과의 연결**: "돌고 있다"와 "작동한다"는 다르다 —
  1. **산출물 검증**: 백업 크기·복원 가능성을 주기 자동 검증(0바이트 덤프가 수개월 통과한 이유는 아무도 산출물을 안 봐서)
  2. **dead man's switch**: 실패 메일(발송 실패 가능)이 아니라 성공 핑 부재 감지 — 알림 경로 자체의 실패까지 흡수
  3. **리허설**: 복구를 해본 적 없는 백업 체계는 전부 미검증 가설이다.

## 2. "터미널에선 되는데 cron에선 안 돼요" — 실행 환경 함정 (운영 표준 사고)

- **무슨 일**: cron 작업의 표준 신규 실패 — PATH 최소(`/usr/bin:/bin`)·환경변수 부재·HOME 다름·셸이 sh. `python`이 시스템 파이썬을 가리켜 가상환경 패키지 없음, `aws`·`node` 못 찾음 등. 에러 출력은 메일 스풀로 가서 아무도 안 본다.
- **방어**: ① 래퍼 스크립트에서 절대경로·환경 명시(`/app/venv/bin/python`) ② 래퍼 첫 줄에 `set -euo pipefail` + 로그 파일 리다이렉트 ③ 신규 등록 직후 **1회 강제 실행 검증**(`run-parts --test` 또는 시각을 1분 뒤로 임시 등록) — "다음 새벽에 확인"은 검증이 아니다.
- **systemd timer 우위**: 실행 환경이 unit 파일에 선언적(Environment=)·journal 로그 통합·`Persistent=true`로 꺼진 동안 누락 보정 — 신규 작업의 기본 권장 근거.

## 3. 시각 의존 연쇄 — "선행이 늦자 후속이 빈 데이터로 돌았다" (암묵 의존 실증)

- **무슨 일**: 03:00 수집 → 04:00 집계 → 05:00 리포트 발송 — 평소엔 정상. 데이터 증가로 수집이 70분 걸린 날, 집계가 미완료 데이터로 실행 → 리포트가 "급감"을 보고 → 새벽 대응 소동. 시각 차이는 의존 선언이 아니라 희망이었다.
- **방어 사다리**: ① 후속 작업 시작 시 선행 완료 검증(완료 마커 파일·DB 워터마크 — 없으면 대기/중단+알림) ② 선행이 후속을 직접 트리거(체이닝) ③ 규모가 커지면 DAG 오케스트레이터(Airflow류)로 의존을 1급 객체화.
- **이 스킬과의 연결**: 안티패턴 6. "몇 시면 끝나있겠지"의 수명은 데이터 증가 속도와 같다 — 의존은 시각이 아니라 신호로.

## 출처 (2026-06 웹 검증 완료)

- **GitLab 공식 포스트모템**: https://about.gitlab.com/blog/postmortem-of-database-outage-of-january-31/ — 1차 사고 당사자가 직접 작성한 공식 포스트모템(복구 과정 유튜브 생중계). 위 1번 사례의 모든 디테일(pg_dump 9.2 vs DB 9.6 메이저 불일치로 인한 빈 덤프·침묵 실패, S3 비어 있음, LVM 스냅샷이 유일하게 유효, ~6시간 데이터 유실)의 직접 근거. 검증 확인.
- **healthchecks.io 공식 문서**: https://healthchecks.io/docs/ · https://healthchecks.io/docs/monitoring_cron_jobs/ — dead man's switch(heartbeat 모니터링)의 표준 구현체 공식 docs. "성공 핑 부재 시 알림"이라는 안티패턴 4의 메커니즘, Period+Grace Time 설정, `https://hc-ping.com/<uuid>` 핑 URL, 머신 다운·cron 미설정·비정상 종료·과실행 등 무실행 계열 실패를 모두 잡는다는 근거. BSD-3 오픈소스로 자체 호스팅 가능(소스: github.com/healthchecks/healthchecks). 검증 확인.
- **systemd.timer 공식 매뉴얼**: https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html — `Persistent=true`가 시스템이 꺼져 있던 동안 놓친 OnCalendar 실행을 부팅 후 따라잡는다(anacron 대체)는 안티패턴 2·5의 근거. journal 로그 통합·`Environment=` 선언적 환경도 동일 출처. 검증 확인.
- **APScheduler 3.x 공식 문서**: https://apscheduler.readthedocs.io/en/3.x/ — `max_instances`(동시 실행 상한)·`coalesce`(밀린 실행 합치기)·`misfire_grace_time`(누락 허용 시간) API의 1차 근거. 2026-06 기준 3.x가 여전히 안정 프로덕션 브랜치(최신 3.11.x), 4.0은 아직 알파(`max_instances`→`max_running_jobs` 등 API 변경 예정 — 4.0 채택 시 재확인 필요). 검증 확인.

> 위 4개 출처는 2026-06 WebSearch로 존재·정확성 확인. cron 실행 환경 함정(2번)·시각 의존 연쇄(3번)는 단일 1차 출처가 아닌 운영 표준 사고 패턴의 집적이라 URL 미부여.
