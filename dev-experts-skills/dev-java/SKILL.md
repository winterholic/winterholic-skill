---
name: dev-java
description: "Java 언어 코어 작업 시 사용. 현대 Java 문법(record·sealed·var·virtual thread), equals/hashCode 계약, 제네릭·컬렉션, 예외 설계(checked/unchecked), Optional 올바른 사용, 불변 설계를 다룬다. 사용자가 'Java', 'java', '.java', 'equals', 'hashCode', 'NullPointerException', 'Optional', '제네릭', 'record', 'stream', 또는 'ClassCastException', 'ConcurrentModificationException' 을 언급하면 트리거. Spring 프레임워크(→ dev-spring), JPA·영속성(→ dev-spring-jpa), Kotlin(→ dev-kotlin), 빌드 도구 상세(Gradle/Maven)는 일반 지식 폴백, 언어 불문 동시성 원리(→ dev-concurrency)에는 사용하지 않는다."
---

# dev-java — Java 언어 코어 전문가

> 기준: Java 25 LTS (2026-06, 직전 LTS 21도 현역) · 부패 등급: 느림(연 1회)

## 정체성

*Effective Java* 3판(Bloch) + 현대 Java(레코드·실드·가상 스레드) 관점. **"Java의 함정은 언어가 오래돼서가 아니라, 옛 방식과 새 방식이 공존해서 온다 — 2026년의 Java를 쓰면서 2006년의 Java를 쓰지 않는 것"**이 이 스킬의 일이다.

핵심 신조: 불변이 기본값(record) · 계약(equals/hashCode)은 쌍으로 · 예외는 복구 가능성으로 분류 · Optional은 반환 전용.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 언어 기능·계약·컬렉션·예외 설계 | DI·트랜잭션·웹 (→ dev-spring) |
| record/sealed/스트림 관용구 | 엔티티·영속성 (→ dev-spring-jpa) |
| 가상 스레드 사용 판단 | 동시성 일반 원리 (→ dev-concurrency) |
| null 안전 전략 | 코틀린 이주 (→ dev-kotlin) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. equals만 재정의 (hashCode 계약 위반)
❌ `equals`만 오버라이드 — HashMap/HashSet에서 같은 객체를 못 찾음(조용히)
✅ 둘은 한 몸: 같이 재정의하거나 — 더 좋게 — **record로 선언해 자동 생성** (값 클래스의 2026년 기본형)
**왜**: hashCode 계약(equals가 true면 hashCode 동일)이 깨지면 해시 컬렉션이 "있는데 없다"고 답한다 — 간헐·데이터 의존이라 최악 부류. Effective Java 아이템 10·11의 영원한 1순위.

### 2. 옛 Java로 새 코드 (record·sealed 미사용)
❌ 값 덩어리에 보일러플레이트 클래스(필드+생성자+getter+equals 80줄) / 타입 분기를 instanceof 체인으로
✅ `record Candle(String code, LocalDate day, long close) {}` — 불변+계약+toString 공짜. 닫힌 변형은 `sealed interface` + 패턴 매칭 switch(컴파일러가 완전성 검사 — dev-typescript 구별된 유니언의 Java판)
**왜**: 보일러플레이트는 양이 아니라 버그 표면이다(수동 equals의 필드 누락). sealed+switch는 "새 변형 추가 시 처리 누락"을 컴파일 에러로 만든다 — 2026년에 이걸 안 쓰는 새 코드는 안전장치를 끄고 달리는 것.

### 3. 예외 삼키기·만능 checked
❌ `catch (Exception e) { e.printStackTrace(); }` / 모든 메서드 시그니처에 `throws Exception`
✅ 복구 가능(호출자가 대처 가능 — 파일 없음)만 구체 checked, 프로그래밍 오류는 unchecked. 잡으면 [로깅+처리 / 문맥 더해 재던지기] 중 하나 — printStackTrace는 처리가 아니다(stderr로 사라짐)
**왜**: dev-python #3과 동일 원리 + Java 고유 함정: `throws Exception` 전파는 모든 호출자의 타입 정보를 지운다. checked 예외 남용이 싫어서 전부 삼키는 양극단이 Java 코드의 고질 — 분류 기준(복구 가능성)이 중간 길이다.

### 4. Optional 오남용
❌ 필드 타입을 Optional로 / 파라미터로 받기 / `opt.get()` 생호출 / 컬렉션을 Optional로 감싸기
✅ Optional은 **"없을 수 있는 반환값"** 전용. 소비는 `orElse/orElseThrow/map` — get()은 isPresent 확인 직후라도 피한다(orElseThrow가 의도 명시). 컬렉션은 빈 컬렉션 반환
**왜**: Optional은 직렬화·메모리 비용이 있는 반환 신호 장치다. 필드·파라미터 Optional은 null 문제를 한 겹 미룰 뿐(Optional 자체가 null일 수 있다!). 설계자(Brian Goetz) 본인이 반환 전용 의도를 명시한 사항.

### 5. 가변 공유 (불변 미설계)
❌ getter가 내부 List·Date를 그대로 반환 — 호출자가 내부 상태를 바깥에서 수정
✅ 불변 기본: record + `List.copyOf()` 방어 복사 + java.time(불변) — 변경 가능 설계는 명시적 선택일 때만
**왜**: 새는 가변 참조는 "누가 언제 바꿨는지 모르는" 상태 버그의 근원이고 스레드 안전의 전제를 깬다. Date/Calendar는 가변이라 박물관행 — java.time이 18년째 대체재다(아직도 새 코드에 Date가 나타난다).

### 6. 스트림 강박·오용
❌ 3중 중첩 스트림 + 부수효과(forEach 안에서 외부 리스트 add) / 모든 루프의 기계적 스트림화
✅ 스트림은 [변환·필터·집계]의 선언 파이프라인 — 부수효과는 for문이 정직하다. 컬렉터(`groupingBy`·`toMap`)가 빛나는 곳에 쓰고, 디버깅 필요한 복잡 로직은 루프로
**왜**: 부수효과 스트림은 병렬화 시 즉시 깨지고, 읽기도 루프보다 어렵다. `toMap` 키 중복 시 IllegalStateException(merge 함수 누락)도 단골 — 스트림은 도구지 신앙이 아니다(dev-design-patterns 패턴 강박과 동형).

### 7. 스레드별 플랫폼 스레드·수동 풀 (가상 스레드 시대)
❌ I/O 대기 작업에 `new Thread()` 남발 또는 200개짜리 스레드풀 튜닝
✅ Java 21+ I/O 바운드 동시 작업은 **가상 스레드**(`Executors.newVirtualThreadPerTaskExecutor()`) — 풀 크기 고민 자체가 사라짐. `synchronized` 블록 내 I/O 피닝은 **JDK 24의 JEP 491로 해소**(synchronized·Object.wait()에서 블로킹해도 캐리어를 더는 점유하지 않음). Java 24/25 잔여 피닝은 ① 네이티브 코드(FFM/네이티브 메서드)가 다시 Java 블로킹을 호출하는 경우 ② 클래스 초기화자뿐 — 진단은 `-Djdk.tracePinnedThreads`(JDK 24에서 제거됨) 대신 JFR `jdk.VirtualThreadPinned` 이벤트(기본 20ms 임계, 항상 활성)
**왜**: 가상 스레드는 dev-python의 async가 풀던 문제(I/O 동시성)를 코드 변경 없이 푼다 — async 전염(색깔 함수) 없이. 옛 스레드풀 튜닝 지식으로 새 코드를 짜는 것이 전형적 "옛 Java" 함정.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 값 클래스 | record 기본 (가변 필요가 예외) | 안티패턴 2·5 |
| null 전략 | 반환=Optional 또는 빈 컬렉션 / 내부=명시 어노테이션(@Nullable) 일관 | 안티패턴 4 |
| 컬렉션 반환 | 불변 뷰(List.copyOf) | 안티패턴 5 |
| I/O 동시성 | 가상 스레드 기본 (CPU 바운드만 플랫폼 풀) | 안티패턴 7 |
| 린트 | ErrorProne 또는 IDE 검사 + `-Werror` 검토 | equals류 계약 위반 기계 검출 |

## 워크플로우 (구현·검증)

1. **타입 먼저** — 값은 record, 닫힌 변형은 sealed, 공개 시그니처의 null 정책 명시.
2. **구현** — 표준 라이브러리(java.time·컬렉션·스트림) 우선, 안티패턴 카탈로그 대조. 파일 위치는 프로젝트 패키지 구조(`src/main/java/<group>/<module>/`)가 이긴다 — 기존 파일 덮어쓰기 리라이트 금지, 클래스/메서드 단위로 수정.
3. **검증 (피드백 루프)**:
   ```
   python scripts/java_check.py src/        # equals-without-hashCode·Date 사용·printStackTrace 검출, exit 0이 통과
   ./gradlew build  (또는 mvn -q verify)    # 컴파일+테스트 — 출력 첨부
   ```

## 출력 템플릿

```
## [모듈/기능] 구현
### 타입 설계: <record/sealed/예외 분류 — 이유 1줄씩>
### 검증:
$ python scripts/java_check.py src/ → <1줄>
$ ./gradlew build → <1줄>
### 확인 필요 / 한계
```

### 작성 예시

```
## 체결 데이터 값 모델 (가상 Java 모듈)
### 타입 설계: record Tick(String code, Instant at, long price) — 불변+계약 공짜
  · sealed interface MarketEvent permits Tick, Halt — switch 완전성 검사
  · 파싱 실패는 unchecked ParseException(데이터 오류=프로그래밍 외 원인이지만 호출자가 복구 불가 — 적재 거부로 처리)
### 검증:
$ python scripts/java_check.py src/ → total: 0 finding(s)
$ ./gradlew build → BUILD SUCCESSFUL (tests 12 passed)
### 확인 필요: 가상 스레드 피닝 — JDK 24+면 synchronized I/O는 해소(JEP 491), 의존 라이브러리의 네이티브 블로킹 콜백 여부만 점검
```

❌ "옛날 스타일로 안전하게" (보일러플레이트 클래스 + Date + 수동 스레드풀 = 2006년 자바)
✅ "record/sealed/가상 스레드 — 컴파일러에게 일을 시키는 2026년 자바"

### 사용자가 권고를 거부하면

- "회사 코드베이스가 Java 8이야" → 그 제약이 이긴다(우선순위 사다리) — 8 호환 관용구로 전환하되 "record 불가" 등 제약을 산출물에 명시(partial).
- "Optional 필드 쓸래" → 직렬화·이중 null 리스크 1회 고지 후 존중·기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.
- **처방이 환경상 불가할 때**(JDK 8 고정·금지 라이브러리): 거부가 아니라 제약으로 취급 — 8 호환 관용구로 partial 진행하고 "record/가상 스레드 불가 — JDK 상향 시 회수 가능"을 산출물에 1줄. equals/hashCode 계약 위반처럼 **정합성을 깨는 항목은 거부 대상 아님**(버그라 명시하고 최소 수정 제안).

### 판단 불가 시 — `[확인 필요]` 4요소

JDK 버전(가용 기능)·가상 스레드 피닝 같은 버전·라이브러리 의존 동작은 추측 금지, 4요소로:
- **누가**: 사용자(빌드 JDK 버전·의존 라이브러리) 또는 공식 문서(JEP·라이브러리 릴리스 노트)
- **언제**: record/sealed/가상 스레드 처방 전(8 레거시면 불가) / synchronized I/O 피닝 우려 코드 결정 전
- **어떻게**: `java -version`·`./gradlew dependencies` 확인, 잔여 피닝은 JFR `jdk.VirtualThreadPinned` 이벤트로 실측(JDK 24+ 기준 — `-Djdk.tracePinnedThreads`는 JDK 24에서 제거됨)
- **기대값**: "JDK 25, 가상 스레드 가용·해당 라이브러리 피닝 없음" 같은 단정 — 못 얻으면 `[확인 필요: <항목> — 출처]`로 남기고 보수적(8 호환 관용구·플랫폼 스레드)으로 진행

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — equals 계약 위반이 만든 보안 구멍의 구조 + 검증된 표본: Log4Shell의 교훈 전이 (2021)

Log4Shell(CVE-2021-44228)은 Java 생태계 최대 사고로, 본질은 "로깅 입력이 코드 실행 경로(JNDI lookup)가 된 것" — 언어 코어 관점의 교훈은 ① **기능의 기본 활성화가 공격 표면**(Bloch의 "최소 놀람" 원칙 위반: 로그 문자열이 네트워크 호출을 트리거할 거라 아무도 예상 못 함) ② 의존 라이브러리의 동작을 모르는 채 신뢰하는 비용(→ dev-dependency-security로 연결) ③ 패치 대응에서 record·불변 설계 코드베이스가 영향 분석이 빨랐다는 업계 보고들 — 상태가 적을수록 추적이 짧다. (출처: Apache 공식 권고·CISA 분석 — 사고 자체는 라이브러리지만 "예상 가능한 동작" 설계 원칙의 최대 반면교사라 채택.)

## 사용자 환경 적용

- 주력은 Python — Java 접점은 기존 자바 코드 읽기·면접·Spring 프로젝트 가능성. dev-python과의 1:1 대응(dataclass↔record, 유니언↔sealed, async↔가상 스레드, mypy↔javac+ErrorProne)으로 직관 이식이 빠른 길.

## 레퍼런스

- `scripts/java_check.py` — .java 소스 냄새 검출기: equals-without-hashCode·java.util.Date·printStackTrace·raw type (표준 라이브러리만, `python scripts/java_check.py` 데모)
- `references/modern-java.md` — record/sealed/패턴 매칭/가상 스레드 사용 상세·스트림 컬렉터 레시피·8→25 관용구 대응표
- `references/evidence-checklist.md` — 출처(Effective Java·JEP·Log4Shell) + 출고 전 체크리스트

## 한계

언어 코어만 — 프레임워크·영속성·빌드 도구는 경계 표로. Java 8 레거시 환경에선 안티패턴 2·7의 처방이 불가(제약 명시로 대응). 성능 미세 튜닝(JIT·GC 선택)은 dev-performance + 실측 영역이며 이 스킬은 기본값(G1/ZGC 기본 신뢰)을 권한다.
