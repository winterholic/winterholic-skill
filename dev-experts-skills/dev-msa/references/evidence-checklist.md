# evidence + 출고 전 체크리스트

## 실증·출처

- **Prime Video Tech Blog (2023-03)** "Scaling up the Prime Video audio/video monitoring service and reducing costs by 90%" — 분산 단계(AWS Step Functions + Lambda) 아키텍처 → 모놀리스 통합. SKILL.md 실전 케이스 원 출처. 1차 출처 URL 웹 확인됨: `https://www.primevideotech.com/video-streaming/scaling-up-the-prime-video-audio-video-monitoring-service-and-reducing-costs-by-90` (원본이 서버리스/오케스트레이션 비용 사례임에 유의 — 고전적 MSA 폐기가 아니라 "분리 비용이 워크로드에 따라 지배적"의 사례).
- **Fowler, "MonolithFirst" (2015)** — "성공한 MSA는 거의 전부 모놀리스에서 출발했고, 처음부터 MSA로 지은 시스템은 심각한 곤경에 빠지곤 했다". 1원칙의 표준 출처. URL 웹 확인됨: `https://martinfowler.com/bliki/MonolithFirst.html` (보완 출처: 같은 저자 "MicroservicePremium" `https://martinfowler.com/bliki/MicroservicePremium.html` — 분산 비용이 진입 프리미엄이라는 근거).
- **Newman, *Building Microservices* 2판 (2021, O'Reilly, ISBN 9781492034025)** — 독립 배포 가능성(independent deployability)을 분리의 정의로·데이터 소유권·분산 모놀리스 경고의 원전. *Monolith to Microservices*(2019, O'Reilly, ISBN 9781492047841)가 점진 분리 절차의 원전. 두 판/연도 웹 확인됨.
- **Fowler, "StranglerFigApplication"** — SKILL.md가 쓰는 "strangler" 점진 분리의 명명 원전(Fowler 2004 최초 게시, 2019-04-29 "Strangler Fig"로 개명). 빅뱅 재작성 대비 위험 감소가 핵심 동기 — Newman의 마이그레이션 절차가 이를 차용. URL 웹 확인됨: `https://martinfowler.com/bliki/StranglerFigApplication.html`.
- **가용성 곱셈**: 동기 체인 N단의 가용성은 각 서비스 가용성의 곱 — 산술 자체가 근거(99.9%를 3단 곱하면 99.7%, 월 ~2시간 추가 다운).
- 오픈소스 차용 표기: MSA 설계류 자료 다수(색인 인지, 본문 비복사). **역흡수**: 대부분 "어떻게 나누나" 중심 — "나누지 않을 근거 검증"·트리거 판단표·1인 규모 보정·경계 보존 기계 검사 부재가 본 스킬 차별점.

## 출고 전 체크리스트 (분리 검토·실행 시)

- [ ] 트리거가 판단표의 ◎/○ 행에 해당 (✕ 행이면 대안 처방으로 종료했다)
- [ ] 경계가 DDD 컨텍스트에서 왔고 데이터 소유권으로 검증됨
- [ ] 비용/효익 표가 작성됨 (분리로 새로 생기는 것 명시)
- [ ] 전제조건 체크리스트(관측·CI·추적) 통과
- [ ] 한 트랜잭션이 경계를 넘지 않는다 (넘으면 경계 재검토했다)
- [ ] 동기 호출 깊이 2 이내, 전 호출 타임아웃
- [ ] strangler 단계 중 현재 위치가 명시됨 (빅뱅 아님 증명)
- [ ] 독립 배포 시연 1회 통과
- [ ] (모놀리스 유지 시) `module_boundary_check.py` 0건 — 경계 보존

## 점검 주기 (부패 느림 — 연 1회)

- 모듈 경계 검사 재실행 + shared/ 비대화 점검
- 트리거 재평가 (팀·트래픽·도메인 변화)
