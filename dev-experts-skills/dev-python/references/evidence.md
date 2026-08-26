# evidence — 실증 사례와 출처 (이 스킬 규칙들의 "왜")

> 수치는 각 사의 공개 자료 기준이며 "확인 필요" 표기는 원문 재대조 전임을 뜻한다.

## Instagram — 순환 GC 비활성화 (2017)

- 출처: Instagram Engineering 블로그 "Dismissing Python Garbage Collection at Instagram" (2017).
- 내용: uWSGI prefork 모델에서 마스터→워커 fork 후 copy-on-write로 메모리를 공유하는데, CPython의 순환 GC가 객체 헤더(gc 추적 필드)를 건드리며 공유 페이지를 복사시켜 메모리 이득이 사라짐. `gc.set_threshold(0)`으로 순환 GC를 끄고(참조 카운팅은 그대로) 공유 메모리를 회복, 서버 용량 ~10% 개선(확인 필요: 원문 수치 재대조).
- 이 스킬에의 교훈: ① CPython 메모리 모델 = 참조 카운팅(주) + 순환 GC(보조) — 순환 참조가 없으면 GC 없이도 회수된다 ② 측정(메모리 공유율) → 원리 가설 → 검증의 순서. 측정 없는 모방은 카고컬트 — 일반 서비스에서 GC를 끄면 순환 참조 누수로 역효과.

## Dropbox — 4백만 라인 mypy 점진 도입 (2019)

- 출처: Dropbox 블로그 "Our journey to type checking 4 million lines of Python" (2019). mypy 주 개발사가 Dropbox(귀도 재직기).
- 내용: 일괄 도입이 아니라 수년에 걸쳐 핵심 모듈부터 점진 적용. 가장 효과 본 곳은 "오래되고 아무도 못 건드리는" 코드 — 타입이 곧 문서가 되어 수정 가능해짐.
- 교훈: tooling-packaging.md의 "도입 사다리" 근거. 타입힌트의 1차 가치는 버그 검출보다 **변경 용기**(리팩터링 안전망).

## "한 글자" 클래스의 사고들 — 침묵 예외·기본값 의존이 비싼 이유

- **AWS S3 장애 (2017-02-28)**: 오타 섞인 명령 1줄이 의도보다 많은 서버를 제거 → S3 광역 장애 약 4시간, 의존 서비스 연쇄 다운. (출처: AWS 공개 postmortem "Summary of the Amazon S3 Service Disruption"). Python 사고는 아니지만 이 스킬의 "입력 경계에서 검증·명시"(naive datetime 거부, 인코딩 명시)와 같은 원리 — 암시적 기본값과 무검증 입력은 규모가 커지면 반드시 사고가 된다.
- **GitLab DB 삭제 (2017-01-31)**: 장애 대응 중 프로덕션 DB 디렉토리를 잘못 삭제, 백업 5중 체계가 전부 작동 안 함이 그때 발각. (출처: GitLab 공개 postmortem). 교훈은 dev-backup-dr 소관이지만, "예외를 삼키고 진행"(안티패턴 #3)이 백업 실패를 수개월 침묵시킨 메커니즘과 동형이다 — **실패는 시끄러워야 한다**.

## 마이너 but 재현 빈도 높은 실증

- **requests 기본 타임아웃 없음**: requests 공식 문서가 명시 — "production code should use timeouts in nearly all cases". 타임아웃 없는 외부 호출 1개가 워커 풀 전체를 점유해 행으로 이어진 사례는 흔하나 개별 출처 특정 곤란 — 정량 기준 "타임아웃 항상 명시"의 근거.
- **asyncio 태스크 GC**: 공식 문서(asyncio.create_task)가 직접 경고 — "Save a reference to the result... a task that isn't referenced elsewhere may get garbage collected at any time". async-concurrency.md 함정 2의 출처는 서드파티가 아니라 공식 문서다.

## 오픈소스 스킬 차용 표기

- 조사 대상: wdm0006/python-skills, mcpmarket "Python Code Quality"·"Python Best Practices", jeffallan claude-skills python-pro (2026-06 조사, 본문 비복사 — 주제 구성 참고만).
- 흡수: ruff+mypy를 워크플로우 검증 명령으로 통합하는 구성, "임팩트 등급"(중요 룰 vs 취향 룰 구분) 아이디어 → 본 스킬은 안티패턴(중요)과 관용구 표(취향 교정)로 분리 반영.
- 역흡수(그들이 빠뜨린 것 → 우리 차별점): Windows cp949·인코딩 함정 전무, 실증 사례·출처 전무, 기준 버전 라벨 전무, async 태스크 GC 함정 누락.
