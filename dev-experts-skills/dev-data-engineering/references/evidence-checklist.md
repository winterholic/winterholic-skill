# evidence + 출고 전 체크리스트

## 실증·출처

- **Kleppmann, *Designing Data-Intensive Applications* (O'Reilly, 2017)** Ch.10 Batch Processing (Part III "Derived Data") — "입력 불변 + 출력 재생성 가능"이 배치의 황금률(이 스킬의 raw 보존·멱등 원칙의 원전). 인간 실수 복구 가능성(human fault tolerance)을 파이프라인 설계 기준으로 둔 것도 DDIA. (1차 출처 — 챕터 구성·발행연도 웹 확인: oreilly.com/library/view/designing-data-intensive-applications/9781491903063/ch10.html)
- **GitLab DB 사고 (2017-01-31)**: 공개 postmortem — 백업 5중 체계가 전부 침묵 실패 상태였음이 사고 때 발각. "검증 없는 성공 신호"(안티패턴 5)의 가장 유명한 실증 — 백업이든 적재든 **결과를 쿼리로 확인하지 않은 성공은 성공이 아니다**. (공개 사고 보고 — 웹 확인: about.gitlab.com/blog/2017/02/01/gitlab-dot-com-database-incident/)
- **idempotency 일반론**: Stripe 엔지니어링 블로그 "Designing robust and predictable APIs with idempotency" — 결제 영역 멱등키 설계의 표준 문서(파이프라인 upsert 키와 동형 개념, dev-payments와 공유). (1차 출처 — 웹 확인: stripe.com/blog/idempotency)
- 재시도·지터: AWS Architecture Blog "Exponential Backoff And Jitter" (Marc Brooker) — 무지터 백오프의 동시 재돌진(thundering herd) 실측. 정량 기준 "지수 백오프+지터"의 출처. (1차 출처 — 웹 확인: aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- 오픈소스 차용 표기: 본 스킬은 dagster/airflow 등 오케스트레이터 문서의 개념(자산·파티션·백필)을 도구 중립 원칙으로 번역(본문 비복사). **역흡수**: 도구 문서들은 "도구 없이 cron+python 규모"의 설계(이 스킬의 주 사용처)를 다루지 않음 — 워터마크 테이블·1행 로그 같은 경량 패턴이 차별점.

## 출고 전 체크리스트 (파이프라인 신설·수정 시)

- [ ] 같은 기준일 2회 실행 → 최종 상태 동일 (멱등 스모크 실측)
- [ ] 중간에 죽이고 재실행 → 정상 수렴 (단계 중단 내성)
- [ ] raw 층이 있고, 정제는 raw에서 재생성 가능
- [ ] 워터마크는 검증 통과 후에만 전진
- [ ] 결측·이상치 정책 표가 문서로 존재하고 사용자와 합의됨
- [ ] 적재 검증 3종(행수·NULL·중복) 자동 실행 + 실패 시 알림
- [ ] 거른 데이터(rejected)가 사유와 함께 남는다
- [ ] 백필이 같은 코드 + 기간 인자로 가능
- [ ] 기준일이 벽시계가 아니라 캘린더/인자에서 온다 (`pipeline_check.py` 0건)
- [ ] 실행 1행 로그(runs)가 남는다
- [ ] 재시도는 일시 에러만, 401류는 별도 처리
- [ ] rate limit이 소스 문서 기준으로 기록돼 있다 (불명이면 "확인 필요")

## 점검 주기 (부패 느림 — 연 1회)

- 갭 감지 쿼리 주기 실행이 실제로 돌고 있는지
- ledger의 파이프라인 삽질 3회 패턴 → 정책 표·체크리스트 반영
