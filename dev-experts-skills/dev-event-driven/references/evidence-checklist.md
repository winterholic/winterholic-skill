# evidence + 출고 전 체크리스트

## 실증·출처

- **Kleppmann, *DDIA* (2017) Ch.11(Stream Processing)~12(Future of Data Systems)** — 이벤트 로그·전달 보장·"정확히 한 번은 최소 한 번 + 멱등"의 원리적 근거. (1차 단행본, 분야 표준서)
- **Stripe Webhooks 공식 문서** — `https://docs.stripe.com/webhooks` (2026-06 확인) — 중복 전달 가능성과 event `id` 기록(이미 처리한 id면 스킵)을 공식 명시. 성숙 공급자가 "최소 한 번 + 소비자 멱등"을 계약으로 못 박는 1차 근거. SKILL.md 실전 케이스. (단, 페이지 개편으로 정확한 섹션 제목 문구는 시점에 따라 변동 — 본문 주장은 유효)
- **아웃박스 패턴**: Richardson, microservices.io "Transactional outbox" — `https://microservices.io/patterns/data/transactional-outbox.html` (2026-06 확인) — 패턴 명세의 표준 출처(릴레이 발행은 자매 패턴 transaction-log-tailing 참조). 이중 쓰기 문제 정의 포함.
- **사가**: Garcia-Molina & Salem, "Sagas" — Proc. 1987 ACM SIGMOD, pp.249–259, DOI `10.1145/38713.38742` (`https://dl.acm.org/doi/10.1145/38713.38742`, 2026-06 확인) — 보상 트랜잭션(compensating transaction) 개념의 원전 1차 논문. + Richardson saga 패턴 정리(오케스트레이션/코레오그래피 구분).
- 오픈소스 차용 표기: 이벤트 아키텍처 자료 다수(색인 인지, 본문 비복사). **역흡수**: 대부분 브로커 사용법 중심 — 두 질문 프레임(유실/중복)·인프로세스 경량 등가물(runs 테이블)·이벤트소싱 분리 판단 부재가 본 스킬 차별점.

## 출고 전 체크리스트 (이벤트 흐름 출고 시)

- [ ] 두 질문(유실·중복)의 답이 설계 문서에 명시
- [ ] 발행이 비즈니스 커밋과 원자적 (아웃박스 또는 상태 컬럼) — `event_check.py` 0건
- [ ] 모든 소비자에 멱등 전략 (처리 기록 또는 천연 멱등 명시)
- [ ] 중복 처리 테스트(같은 이벤트 2회 → 상태 동일) green
- [ ] 이벤트 이름이 과거형 사실 (커맨드 위장 없음)
- [ ] 필수 필드 6종 (id·type·occurred_at·key·payload·version)
- [ ] 순서 요구가 키 단위로 좁혀져 있다
- [ ] 다단계 흐름에 사가 표 (보상 불가 단계는 맨 뒤)
- [ ] 재처리 절차 문서화
- [ ] outbox·processed_events 정리(보존 기간) 정책 존재

## 점검 주기 (부패 느림 — 연 1회)

- outbox 미발행 적체·processed_events 크기 점검
- ledger의 유실/중복 삽질 3회 패턴 → 두 질문 프레임 보강
