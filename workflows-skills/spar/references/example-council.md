# Council 실전 사례 — 2026-06-10 스모크 테스트 (실측 원문 발췌)

> 실제 Workflow 실행 결과다(가상 아님). 3 에이전트(judge 포함), 85,857 서브에이전트 토큰, 171초.
> 용도: Council brief가 어떤 밀도여야 하는지, 판정이 어떻게 한쪽에 커밋하는지, 메인 종합이 어떤 모양인지의 실물 anchor.

## 입력 (메인이 1회 수집해 넘긴 args)

- **topic**: 단일 서버 FastAPI 앱의 로그 로테이션 — 시간 기반(daily) vs 크기 기반(100MB)
- **position**: daily 로테이션 (운영자가 날짜로 grep, 디스크는 retention 7일로 방어)
- **alternatives**: 크기 기반 100MB / 하이브리드(daily + 500MB 상한)
- **context**: 온프레미스 단일 VM, 로그 파티션 50GB, 평시 1GB/day·장애 시 20GB/day, 수집기 없이 SSH grep, **과거 사건: 장애 당일 18GB 단일 파일로 grep 분 단위 지연**
- **judge**: true

## 옹호자 brief (발췌 — 이 밀도가 기준)

- verdict: "daily(+compress, 7일)가 조회 패턴·retention 의미론에 부합하며, **과거 18GB grep 지연은 크기 기반으로 가도 해결 안 됨**" (확신도: medium)
- 핵심 논점: grep 시간은 **스캔 총 바이트**에 비례 — 18GB를 100MB×180개로 쪼개도 그날 전체 grep은 똑같이 18GB를 읽는다. 크기 기반 파일명(app.log.1..N)엔 시간 정보가 없어 좁히기가 오히려 어려움. *basis: 인라인 컨텍스트(18GB 사건) + grep 순차 스캔 원리*
- 크기 기반의 함정: 로그량 20배 변동 환경에서 파일 수 retention은 **장애 직전 일주일치를 정확히 그 순간 삭제** — 근본원인 분석에 가장 필요한 로그를 잃음
- 자기 약점 명시: 장애 당일 active 파일은 여전히 20GB까지 자람 — 단 이건 어떤 로테이션도 못 피하는 총량 문제
- falsifiableCheck: `time grep -c 'ERROR' dummy.log`(1GB 더미)로 스캔 처리량 측정 → 20GB÷처리량이 분 단위면 "분할 무용" 확정

## 비판자 brief (발췌)

- verdict: "daily 단독은 **문서화된 실패(18GB 사건)를 로그가 가장 필요한 순간에 재현** + retention 7일도 worst case(20GB×7=140GB>50GB)에서 깨짐 → 하이브리드가 우월" (확신도: high)
- 숨은 가정 공격: "retention 7일이면 안전"은 평시 1GB/day에서만 성립 — 평가는 worst case에서 해야 하는데 position 근거는 평시만 봄
- 자기 대안의 전제 취약성도 인정: maxsize는 logrotate 실행 시점에만 평가 — **daily cron뿐이면 하이브리드도 무력화** (트리거 주기 확인 필요)
- falsifiableCheck: `systemctl list-timers | grep logrotate`로 트리거 주기 확인 + `logrotate -d`로 maxsize dry-run

## 판정 (advocate 승 — "둘 다 일리 있음" 회피가 핵심)

- **decisiveFactor**: 18GB 사건의 원인 귀속 — grep 지연은 파일 구조가 아니라 스캔 총 바이트 문제. 비판자의 주력 논거가 이 반론에 응답하지 못함.
- 비판자의 140GB 산수는 **compress(~10:1) 누락** — 압축 포함 worst case ≈ 32GB < 50GB.
- 하이브리드는 비판자 스스로 전제 취약성(트리거 주기)을 인정했고, "daily로 시작 → 필요 시 maxsize 한 줄 추가"가 **가역적**이라 지금 복잡도를 살 이유 없음(YAGNI).

## 이 사례에서 배울 것

1. **basis 없는 논점은 판정에서 죽는다** — 비판자의 "로그 가치 최고 순간에 daily 최악" 프레임은 수사적으로 강했지만 bytes-scanned 반론을 못 넘어 hand-waving 판정.
2. **양쪽 다 자기 약점을 명시**했다(옹호: active 파일 비대, 비판: 트리거 주기) — 역할 수행과 정직성이 공존하는 모양.
3. **falsifiableCheck가 구체 커맨드**다 — "확인해보면 좋을 듯"이 아니라 복붙 가능한 한 줄.
4. 판정은 **조건부 split 회피** — 커밋하되, 가역성(maxsize 한 줄 추가)을 다음 수로 남김.
