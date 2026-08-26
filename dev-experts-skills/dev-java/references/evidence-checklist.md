# evidence + 출고 전 체크리스트

## 실증·출처

- **Bloch, *Effective Java* 3판 (2018)** — equals/hashCode 계약(아이템 10·11)·불변 우선(17)·Optional 반환 전용(55)·상속보다 조합(18)의 원전.
- **Brian Goetz (Optional 설계 의도)** — Stack Overflow 답변(질문 ID 26327957, Java 언어 아키텍트 본인 답변): "라이브러리 메서드 반환 타입을 위한 제한된 메커니즘이지 범용 Maybe 타입이 아니다 — 필드·파라미터로 거의 쓰지 말고, 컬렉션 반환엔 빈 컬렉션을, get()은 절대 호출 말 것" — 안티패턴 4의 1차 근거. https://stackoverflow.com/questions/26327957/should-java-8-getters-return-optional-type
- **JEP 395(record, JDK 16)·409(sealed, JDK 17)·441(패턴 매칭 switch, JDK 21)·444(가상 스레드, JDK 21)·491(synchronized 피닝 해소, JDK 24)** — openjdk.org 공식 명세. 버전 라벨·기능 서술의 1차 출처. (JEP 491은 JDK 24에 정식 인도 — synchronized/Object.wait() 블로킹이 더는 캐리어를 점유하지 않으며, 진단 플래그 `-Djdk.tracePinnedThreads`는 JDK 24에서 제거되고 JFR `jdk.VirtualThreadPinned` 이벤트로 대체. https://openjdk.org/jeps/491 )
- **JEP 506 (Scoped Values, JDK 25 정식)** — ThreadLocal의 가상 스레드 친화 대체재(불변·구조적). 5차 프리뷰를 거쳐 JDK 25에서 final. https://openjdk.org/jeps/506
- **Log4Shell (CVE-2021-44228)**: Apache Log4j 공식 권고·CISA 분석 — SKILL.md 실전 케이스(예상 가능한 동작 원칙·의존성 신뢰 비용).
- 오픈소스 차용 표기: Java 베스트프랙티스류 다수(색인 인지, 본문 비복사). **역흡수**: 8→25 대응표(옛/새 공존 함정 프레임)·가상 스레드 피닝 주의·record-JPA 비호환 명시 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (Java 코드 출고 시)

- [ ] 값 클래스가 record (불가 사유 없는 한)
- [ ] equals 오버라이드에 hashCode 동반 (`java_check.py` 0건)
- [ ] java.util.Date/Calendar 신규 사용 0
- [ ] 닫힌 변형에 sealed + default 없는 switch
- [ ] 예외: printStackTrace 0 · 복구 가능성 기준 분류 · 문맥 더한 재던지기
- [ ] Optional이 반환에만 (필드·파라미터 0)
- [ ] 컬렉션 반환 불변 (copyOf)
- [ ] I/O 동시성에 가상 스레드 (피닝 점검)
- [ ] 빌드+테스트 출력 첨부

## 점검 주기 (부패 느림 — 연 1회)

- ScopedValue(JEP 506)·피닝(JEP 491)은 JDK 25/24에서 각각 정식화 완료 — 차기 LTS(JDK 26 예정, 2026-09)와 신규 final JEP만 확인 → 대응표 갱신
