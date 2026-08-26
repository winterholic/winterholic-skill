# evidence + 출고 전 체크리스트

## 실증·출처

- **Django 공식 문서** — "Database access optimization"(select/prefetch·exists/count)·QuerySet 평가 의미론(QuerySets are lazy)·`check --deploy` — 안티패턴 1·2·4의 1차 출처. URL: https://docs.djangoproject.com/en/5.2/topics/db/queries/ (평가 시점·캐싱), https://docs.djangoproject.com/en/5.2/topics/db/optimization/ (select/prefetch). 공식 docs로 확인(2026-06, 5.2 기준).
- **Two Scoops of Django** — 설정 분리(base/dev/prod)·앱 구조·매니저 패턴의 실무 표준. 최신판은 **3.x(2020, Django 3.x 대상)** — 설정·매니저·앱 구조 원칙은 5.2에도 유효하나 5.x 신기능은 미반영이므로 신기능은 공식 docs 우선. 확인: https://www.feldroy.com (저자 feldroy, 4.x/5.x 판 미출간).
- **DEBUG 노출 실증**: 운영 `DEBUG=True`는 예외 시 설정·환경변수·스택트레이스를 응답으로 노출하는 정보유출 취약점(**CWE-200**). HackerOne 공개 리포트로 실증 — MTN Group #1434276, Glovo #1561377, Dropcontact #963542(전부 'Django debug mode enabled' 부류, 비인증 경로 접근으로 디버그 페이지 노출). 보안 스캐너(Acunetix·Invicti)도 표준 시그니처로 탐지. SKILL.md 실전 케이스. (HackerOne 검색 2026-06 확인.)
- **Django 5.2 LTS** — 2025-04-02 릴리스, 지원 ~2028-04. 신규 `CompositePrimaryKey`(복합 PK), Python 3.10–3.13 지원, PostgreSQL 14+ 최소. 출처: https://www.djangoproject.com/weblog/2025/apr/02/django-52-released/, https://docs.djangoproject.com/en/5.2/releases/5.2/ — 공식 릴리스노트 확인(2026-06).
- 오픈소스 차용 표기: Django 가이드류 다수(색인 인지, 본문 비복사). **역흡수**: 평가 트리거 전체 목록·Prefetch 무효 함정·FastAPI와의 선택 기준 명문화 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (Django 코드 출고 시)

- [ ] DEBUG·SECRET_KEY가 환경에서 옴 (`django_check.py` 0건)
- [ ] `manage.py check --deploy` 통과 (운영 배포 시)
- [ ] 핵심 뷰에 assertNumQueries 단언
- [ ] 루프 내 관계 접근 없음 (select/prefetch 명시)
- [ ] 존재/개수 확인이 exists()/count()
- [ ] 마이그레이션 sqlmigrate 확인 + 비호환은 2단계
- [ ] `makemigrations --check` CI 게이트
- [ ] 시그널 신규 도입 없음 (있으면 문서화 조건)
- [ ] atomic 블록에 외부 I/O 미포함, 커밋 후 작업은 on_commit

## 점검 주기 (부패 중간 — 반기)

- Django LTS 지원 기간·차기 버전 비동기 성숙도 확인
- 검출기 패턴 유효성
