# evidence + 출고 전 체크리스트

## 실증·출처

- **Spring Framework 공식 문서 "Proxying mechanisms"·"Understanding the Spring Framework's declarative transaction implementation"** — self-invocation 한계의 공식 명시(박스 경고). SKILL.md 실전 케이스의 1차 출처.
- **토비의 스프링 3.1 (이일민)** — 프록시·트랜잭션 추상화를 원리부터 쌓는 한국어 표준 교과서. "왜" 중심 접근의 앵커.
- **김영한 스프링 핵심 원리 (인프런 커리큘럼)** — 생성자 주입 단일 정답론·싱글톤 무상태 규율의 실전 표준.
- **Spring Boot 4.0.0 GA** (spring.io/blog/2025/11/20/spring-boot-4-0-0-available-now, 2025-11-20) · **Spring Framework 7.0 GA** (spring.io/blog/2025/11/13/spring-framework-7-0-general-availability, 2025-11-13) — 버전 라벨 1차 출처. 6→7 베이스라인 변화(Java 17 최소·Jakarta EE 11·JSpecify 널 안전성·내장 HTTP 인터페이스 클라이언트)는 Spring Boot 4.0 Release Notes(github.com/spring-projects/spring-boot/wiki) 참조. 확인 필요: 개별 프로젝트의 실제 boot 버전(3.x 잔존 광범위) — 4.0 전제 답변 전 빌드 파일 확인.
- 오픈소스 차용 표기: Spring 가이드류 다수(색인 인지, 본문 비복사). **역흡수**: 프록시 우회 4대 조건의 진단 절차화·REQUIRES_NEW 커넥션 데드락·테스트 @Transactional의 가짜 통과 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (Spring 코드 출고 시)

- [ ] 필드 주입 0 (`spring_check.py` 0건)
- [ ] 어드바이스 메서드의 this 호출 없음
- [ ] 트랜잭션 경계가 메서드 단위 + 외부 I/O 미포함
- [ ] 조회 메서드 readOnly = true
- [ ] 예외-롤백 정합 (checked 던지며 롤백 기대하는 곳 없음)
- [ ] 빈 인스턴스 필드에 요청 상태 없음
- [ ] 컨트롤러가 엔티티 비반환 (record DTO)
- [ ] 시크릿이 yml에 없음 (환경변수 참조)
- [ ] 테스트: @SpringBootTest 최소, 슬라이스·단위 우선

## 점검 주기 (부패 보통 — 반기)

- 부트 메이저 vs 라벨 (현 4.0.x / FW 7.0.x, 둘 다 2025-11 GA) — release notes의 프록시·트랜잭션·DI 변경만 추적
- 부트 4.0.x 패치 라인 진행 + 3.x EOL 시점 추적(3.x는 2026-06 현재 여전히 다수 운영)
- 검출기 패턴 유효성 (어노테이션 변화)
