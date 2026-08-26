# evidence + 출고 전 체크리스트

## 실증·출처

- **Google SRE Book (2016) — Ch.6 "Monitoring Distributed Systems"·Ch.11 "Being On-Call"** — 골든 시그널(지연·트래픽·에러·포화, Ch.6)·증상 기반 경보·"모든 페이지는 지능적 행동 요구"·알람 피로 관리의 1차 출처. 무료 공개: https://sre.google/sre-book/monitoring-distributed-systems/ (웹 확인: 골든 시그널 정의·"성공/실패 요청 지연 분리"·"느린 에러가 빠른 에러보다 나쁘다" 원문 일치).
- **Google SRE Workbook — Ch.5 "Alerting on SLOs"** — SLO/에러 예산 산정 + 다중 윈도우·다중 번레이트(multiwindow, multi-burn-rate) 경보의 1차 출처(signals-slo.md의 "SRE 고급 패턴"·에러예산 배포 조절기 근거). 무료 공개: https://sre.google/workbook/alerting-on-slos/ (웹 확인: 6단계 점진 접근의 최종형이 다중윈도우 번레이트, 99.9%/30일 기준 번레이트 1 = 0.1% 에러율, 저트래픽 서비스 한계 명시).
- **Brendan Gregg — USE Method / Tom Wilkie — RED Method** — 자원·요청 측정 방법론 원전.
- **PagerDuty 운영 자료 + 다수 포스트모템** — 알람 피로가 진짜 장애를 묻는 실패 패턴. SKILL.md 실전 케이스.
- **Prometheus 공식 문서 — "Alerting" best practices** (https://prometheus.io/docs/practices/alerting/) — 증상 경보 우선·`for:` 지속(블립 무시)·page/ticket 심각도 분리·고카디널리티 경고의 도구 측 근거 (웹 확인: 4개 권고 항목 모두 본문과 일치).
- 오픈소스 차용 표기: 모니터링 스택 가이드 다수(색인 인지, 본문 비복사). **역흡수**: 증상/원인 경보 분리의 검출화·3축 분업으로 카디널리티 설명·1인 규모 SLO 적용 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (관측 출고 시)

- [ ] SLI/SLO가 사용자 경험으로 정의됨 (+ 에러 예산)
- [ ] 골든 시그널 4축 계측 + 저카디널리티 라벨 (`alert_lint.py` 0건)
- [ ] 경보는 증상(SLO 위반)에만, 원인은 대시보드
- [ ] 지연은 분위수(p95/p99), 평균 경보 0
- [ ] 각 경보에 런북 한 줄 (행동 가능성)
- [ ] 경보에 `for:` 지속 (순간 스파이크 무시)
- [ ] page/ticket 심각도 분리
- [ ] 메트릭에 user_id/request_id 등 고유 식별자 0
- [ ] liveness/readiness 헬스체크 분리
- [ ] 경보 리허설(장애 주입→발화) 1회

## 점검 주기 (부패 느림 — 연 1회)

- 경보별 발화율·행동율 리뷰 → 무행동 경보 제거(알람 피로 관리)
- SLO 달성률 vs 목표 재평가 (너무 빡빡/느슨)
