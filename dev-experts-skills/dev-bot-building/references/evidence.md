# dev-bot-building evidence — 실증 사례

## 1. 봇 토큰 유출 — "내 봇이 서버를 부쉈다" (커뮤니티 반복 실증)

- **무슨 일**: 토큰을 공개 레포·스크린샷·로그로 유출 → 자동 스캐너가 수집 → 공격자가 봇 계정으로 행동. Administrator 봇이면 채널 삭제·전원 추방·@everyone 스팸·웹훅 생성까지 — 피해 서버는 "그 봇 개발자"를 책임자로 본다. 디스코드 개발자 커뮤니티의 장르적 반복 사고로, 디스코드도 GitHub와 토큰 스캔 협력(노출 시 자동 무효화)을 운영.
- **대응 순서**: ① 개발자 포털에서 토큰 즉시 재발급 ② 봇 활동 감사(무엇이 실행됐나) ③ 유출 경로 차단(이력 청소·스캔 훅) — 재발급 전의 어떤 조치도 무의미.
- **설계 교훈**: 권한 최소 초대는 사고 시 보험 — "관리 편하라고 Admin"의 비용은 유출일에 일시불 청구된다.

## 2. 블로킹 핸들러 — "봇이 5초씩 죽은 척" (이벤트 루프 실증)

- **무슨 일**: async 봇 핸들러에 동기 HTTP(requests)·동기 DB 호출 — 호출 동안 이벤트 루프 정지로 모든 명령·이벤트 무응답. 심하면 게이트웨이 하트비트가 밀려 라이브러리가 연결 끊김으로 판단 → 재연결 루프 → "봇이 자꾸 나갔다 들어와요".
- **진단**: 증상이 "특정 명령 직후 전체 무응답"이면 그 핸들러의 동기 호출부터 — `grep -rn "requests\.\|time\.sleep\|\.execute(" handlers/`. asyncio 디버그 모드(`PYTHONASYNCIODEBUG=1`)는 느린 콜백을 직접 경고해준다.
- **패턴 처방**: 외부 IO는 async 클라이언트 / 동기 강제 라이브러리는 `asyncio.to_thread` / CPU 작업은 ProcessPool — dev-python asyncio 규율의 봇 적용판.

## 3. "죽은 줄 몰랐던 2주" — 알림 봇의 침묵 사망 (운영 구조 실증)

- **무슨 일**: 장애 알림 봇이 토큰 만료·서버 재부팅 후 미기동·예외로 조용히 사망 — 알림이 없길래 "장애가 없구나" 했는데 실은 알리는 쪽이 죽어 있었다. 모니터링 체계의 고전적 자기모순(누가 감시자를 감시하나)으로, 알림 의존이 클수록 발견이 늦다.
- **방어 3겹**: ① systemd `Restart=always` + 기동 시 채널에 자가 보고("재시작됨 — 사유 추정") ② 주기 하트비트를 외부 dead man's switch(healthchecks류)로 — **신호 없음이 곧 알림**이 되게(→ dev-cron-scheduling 동일 패턴) ③ 주 1회 수동 `/ping` 습관(사람 쪽 점검 루프).
- **원칙**: 알림 경로의 가용성은 감시 대상보다 한 단계 높아야 한다 — 봇과 감시 대상이 같은 서버에 있으면 같이 죽는다(분리 배치).

> 출처(2026-06 기준, 1차 출처 우선):
> - 디스코드 메시지 한도·API 스펙 — 공식 개발자 문서 https://discord.com/developers/docs/resources/message (일반 2000자, Nitro 4000자, 웹훅 한도 별도). 봇 토큰=봇 계정 전체 권한 전제도 동일 문서의 인증 모델 근거.
> - GitHub × Discord 시크릿 스캔 파트너십(노출 토큰 자동 무효화) — 공식 문서 https://docs.github.com/code-security/secret-scanning/secret-scanning-partnership-program/secret-scanning-partner-program · 디스코드 토큰 유효성 검사 지원 변경로그 https://github.blog/changelog/2023-10-13-secret-scanning-supports-validity-checks-for-discord-tokens/ (스캐너 이름: discord_api_token_v2, discord_bot_token).
> - asyncio 블로킹 진단 — CPython 공식: 디버그 모드 환경변수 PYTHONASYNCIODEBUG(느린 콜백 경고) https://docs.python.org/3/library/asyncio-dev.html · 동기 호출 오프로딩 asyncio.to_thread()(3.9+) https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread .
> - 라이브러리 현행 버전 — discord.py 2.7.1(2026-03, https://pypi.org/project/discord.py/) · python-telegram-bot 22.8(2026-06, Python 3.10+, https://pypi.org/project/python-telegram-bot/).
> - 운영 패턴(침묵 사망 방어·이중 화이트리스트) — 사용자 monitoring-discord-bot 실운영 경험 + 디스코드 개발자 커뮤니티 반복 사고 집적.
