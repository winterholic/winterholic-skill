# evidence + 출고 전 체크리스트

## 실증·출처

- **Confluent 공식 블로그 — "Can Your Kafka Consumers Handle a Poison Pill?" (Tim van Baarsen)** — 역직렬화 실패의 크래시 루프·로그 폭주 재현 + ErrorHandlingDeserializer 격리 패턴. SKILL.md 실전 케이스. (https://www.confluent.io/blog/spring-kafka-can-your-kafka-consumers-handle-a-poison-pill/)
- **AWS SQS 공식 문서 — DLQ·visibility timeout·delay queues** — 두 개념을 1급 기능으로 둔 표준 설계의 근거. 지연(DelaySeconds)·메시지 타이머 최대 15분, visibility timeout 최대 12시간 한도도 여기서 확인. (https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html , https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-delay-queues.html)
- **PostgreSQL 공식 문서 — SELECT FOR UPDATE SKIP LOCKED** — DB 큐의 핵심 구문(9.5+ 도입). "DB를 큐로"가 안티패턴이던 시절을 끝낸 기능. (https://www.postgresql.org/docs/current/sql-select.html)
- **"Choose Boring Technology" (Dan McKinley, 2015)** — 사다리(작은 것부터)·"innovation token" 철학의 표준 에세이. (https://mcfunley.com/choose-boring-technology)
- 오픈소스 차용 표기: 브로커 가이드 다수(색인 인지, 본문 비복사). **역흡수**: DB 큐 전체 구현 제공·"리플레이·다중 구독" 결정 인자·가시성 타임아웃의 방언 통합 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (큐 도입·수정 시)

- [ ] dev-event-driven 두 질문(유실·중복) 답 존재
- [ ] 사다리 판정 기록 (①부터 탈락 근거)
- [ ] ack가 처리 후 (`queue_check.py` 0건) + 소비 멱등
- [ ] 재시도 횟수 상한 + 백오프 + DLQ/dead 격리
- [ ] DLQ 1건 경보 + 재투입 절차 문서화
- [ ] 순서 단위(키) 명시 — 경쟁 컨슈머와 충돌 없음
- [ ] lag 지표 + 추세 경보 (dev-monitoring 연결)
- [ ] 한도·폐기 정책 (도메인 결정 기록)
- [ ] 처리 시간 < 가시성 타임아웃/3
- [ ] 리허설 3종 (컨슈머 사망 / poison / 중복) 통과

## 점검 주기 (부패 중간 — 반기)

- dead 누적·lag 추이 리뷰
- 처리량이 사다리 다음 단 임계에 접근하는지
