# evidence + 체크리스트

## 실증·출처

- **Google eng-practices (github.com/google/eng-practices)** — "코드 건강의 확실한 개선이면 승인"·속도 장·코멘트 작법의 원전. 공개 문서라 직접 대조 가능.
- **SmartBear/Cisco 코드 리뷰 연구 ("Best Kept Secrets of Peer Code Review" / Cisco 케이스 스터디, ~2,500 리뷰·320만 줄 실측)** — 1회 리뷰 200~400줄 초과 시 결함 검출 효과 급락, 검토 속도 시간당 400~500줄 초과 시 결함 밀도 발견율 저하. 400줄 예산의 1차 출처(static0.smartbear.co/support/media/resources/cc/book/code-review-cisco-case-study.pdf — 공개 PDF, 직접 대조 가능).
- **Apple goto fail (CVE-2014-1266)** — 공개 소스로 검증 가능한 줄 수준 리뷰 실패 사례. SKILL.md 실전 케이스.
- **Microsoft 리뷰 연구 (Bacchelli & Bird, "Expectations, Outcomes, and Challenges of Modern Code Review", ICSE 2013)** — 리뷰의 실효익에서 결함 검출보다 지식 전파·코드 이해가 상위로 보고됨. "지식 전파 장치" 신조의 학술 출처.
- 오픈소스 차용 표기: alirezarezvani pr-review-expert(색인 인지 — blast radius 관점 참고, 본문 비복사). **역흡수**: 등급 라벨 규약·받는 자세·갈등 사다리·1인 셀프 리뷰 절차 부재 — 본 스킬 차별점.

## 리뷰어 체크리스트

- [ ] PR 설명·맥락 먼저 읽음 (없으면 그게 1번 코멘트)
- [ ] 1차 pass(필요성·위치·계약·테스트) 후 2차(줄)
- [ ] 규모 400줄 초과면 분할 요청 (`pr_size_gate.py`)
- [ ] 모든 코멘트에 등급 라벨 + 3요소
- [ ] 스타일 코멘트 0 (도구 소관)
- [ ] 잘한 점 1개+
- [ ] 판정(승인/코멘트 후 승인/변경 요청) 명시
- [ ] 첫 응답 1영업일 내

## 작성자 체크리스트

- [ ] 셀프 리뷰 1회 (diff 뷰 통독)
- [ ] PR 설명: 무엇을·왜·테스트 방법
- [ ] 리팩터/기능 커밋 분리
- [ ] 검출기·린트 결과 첨부
- [ ] 모든 코멘트에 응답 (수용/반론/질문)

## 점검 주기 (부패 느림 — 연 1회)

- 자주 반복되는 코멘트 → 검출기/린트 룰/CLAUDE.md로 승격 (사람 리뷰에서 제거)
