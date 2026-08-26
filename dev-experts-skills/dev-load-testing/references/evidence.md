# dev-load-testing evidence — 실증 사례

## 1. 예고된 다운 장르 — 수강신청·티켓팅·재난지원금 (반복 실증)

- **무슨 일**: 시작 시각이 공지된 동시 접속 이벤트의 다운이 연례 반복 — healthcare.gov(2013, 미국 — 의회 청문까지 간 교과서 사례)·국내 재난지원금/백신예약 초기 다운·대학 수강신청·티켓팅. 공통적으로 "부하 테스트는 했다"가 사후 진술에 등장한다.
- **테스트가 놓친 3요소**: ① **스파이크 형상**: 평시 램프업이 아니라 정각 0초에 수직 — 커넥션 수립·TLS 핸드셰이크·세션 생성이 한 점에 ② **여정 경합**: 로그인(세션 스토어)→조회→신청(같은 행 락)의 체인 — 단계별 단독 테스트는 체인 경합을 못 본다 ③ **핫스팟**: 전원이 같은 인기 강의/좌석/재고를 두드림 — 균등 분포 데이터로는 재현 불가(같은 행 락·같은 캐시 키).
- **설계 답안**: 스파이크 모델 전용 시나리오 + 핫스팟 데이터 + (근본적으로) 가상 대기열로 유입 자체를 제어 — 대기열은 패배가 아니라 "부하를 설계 가능량으로 바꾸는" 표준 부품이다(티켓팅 업계 정착).

## 2. Coordinated Omission — 자비로운 측정기의 거짓말 (Gil Tene 경고)

- **메커니즘**: 닫힌 루프 부하 도구(응답을 받아야 다음 요청)는 서버가 1초 멈추면 그동안 요청을 안 보낸다 — 현실의 사용자들은 그 1초에도 계속 도착해 전원이 1초+를 겪는데, 측정기는 "그 구간에 측정 자체가 없음"으로 지연 통계를 낙관 오염시킨다. Gil Tene(Azul)가 명명·전파한 고전 경고로, 도구들의 arrival-rate 모드 도입 배경.
- **체감 규모**: 서버 멈춤이 간헐적일수록 p99 왜곡이 커진다 — 실제 p99가 수 초인 시스템이 닫힌 루프 측정에선 수백 ms로 보고된 사례 시연 다수.
- **실무 처방**: ① 도착률 고정 executor 사용(k6 constant-arrival-rate류) ② 요청 시작 시각 기준 지연 계산인지 도구 동작 확인 ③ 의심되면 독립 관측(서버측 메트릭·실사용자 모니터링)과 교차 — 측정기의 숫자도 검증 대상이다.

## 3. 가상 대기열 — 부하 테스트의 정직한 결론 (업계 정착 패턴)

- **무슨 일**: 티켓팅·한정판 드롭·예약 시스템들이 정착시킨 패턴 — 수십만 동시 유입을 그대로 받는 대신, 대기열 계층(정적·초경량)이 토큰을 발급하고 본 시스템엔 설계된 처리율만 유입. 본 시스템의 부하 테스트 합격선이 곧 대기열 방출 속도가 된다.
- **설계 요점**: ① 대기열 자체는 극단순(정적 페이지+토큰 — 여기가 죽으면 무의미) ② 순서 공정성·새로고침 어뷰징 방지(토큰 바인딩) ③ 이탈 보정(방출했는데 안 들어옴 — 재방출 정책).
- **이 스킬과의 연결**: "목표 부하에서 SLO"라는 명제가 불가능한 수요(순간 수십만)라면, 답은 무한 증설이 아니라 수요 성형(shaping)이다 — 부하 테스트는 그 방출 속도를 정하는 근거 데이터가 된다.

> 출처(웹 확인 2026-06):
> - Gil Tene, "How NOT to Measure Latency" (QCon SF 2015) — coordinated omission 명명·전파의 1차 출처: https://www.infoq.com/presentations/latency-response-time/ (웹 확인 2026-06, URL 라이브 — Azul Systems CTO, HdrHistogram으로 CO 보정/회피 도구화)
> - k6 `constant-arrival-rate` executor 공식문서 — 개방 모델로 응답 지연과 무관하게 고정 도착률 유지(CO 보정 처방의 근거): https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/ (웹 확인 2026-06, URL 라이브 · k6는 2021 Grafana 인수 후 docs가 k6.io→grafana.com/docs/k6로 이전됨)
> - k6 open vs closed model 개념 문서 — 닫힌 루프가 지연을 과소측정하는 메커니즘 설명, 공식문서가 직접 "coordinated omission"으로 명명("slower response times means longer iterations and a lower arrival rate of new iterations"): https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/ (웹 확인 2026-06, URL 라이브)
> - healthcare.gov(2013) — 로그인 단계 병목·캐파 미산정·의회 청문(교과서 사례): https://www.brookings.edu/articles/a-look-back-at-technical-issues-with-healthcare-gov/ , GAO 감사 보도 https://www.washingtonpost.com/national/health-science/hhs-failed-to-heed-many-warnings-that-healthcaregov-was-in-trouble/2016/02/22/dd344e7c-d67e-11e5-9823-02b905009f99_story.html
> - 국내 공공 서비스 초기 다운 보도·티켓팅 업계 대기열 관행 — 1차 URL 미특정(확인 필요).
