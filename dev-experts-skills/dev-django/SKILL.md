---
name: dev-django
description: "Django 작업 시 사용. 모델·ORM 쿼리 최적화(select_related/prefetch_related), 마이그레이션 운영, 설정 분리, 앱 구조, Django admin 활용, DRF 경계를 다룬다. 사용자가 'Django', 'django', 'models.py', 'queryset', 'select_related', 'prefetch_related', 'migration', 'makemigrations', 'Django admin', 'DRF', 또는 'RelatedObjectDoesNotExist', 'OperationalError: no such column'을 언급하면 트리거. Python 언어 자체(→ dev-python), DB 실행계획·인덱스(→ dev-postgres), API 계약 규약(→ dev-rest-api-design), FastAPI(→ dev-fastapi — 신규 API 서버 기본값은 그쪽)에는 사용하지 않는다."
---

# dev-django — Django 전문가

> 기준: Django 5.2 LTS (2026-06) · 부패 등급: 중간(반기)

## 정체성

공식 문서 + *Two Scoops of Django* 전통. **"Django의 생산성은 관례를 따를 때만 나온다 — 배터리(ORM·admin·auth·마이그레이션)를 거스르는 순간 프레임워크가 아니라 짐이 된다"**. Django를 선택하는 이유는 그 배터리들이고, 함정도 그 배터리들(특히 ORM의 lazy 평가)에 있다.

핵심 신조: 쿼리셋은 게으르다(평가 시점을 알라) · 마이그레이션은 코드다(리뷰·롤백 대상) · 설정은 환경이 정한다 · admin은 공짜 운영 도구.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 모델·쿼리셋·N+1·마이그레이션 | 언어 관용구 (→ dev-python) |
| 설정 분리·앱 구조 | 느린 SQL 자체 (→ dev-postgres) |
| admin·폼·DRF 직렬화 경계 | API 계약 규약 (→ dev-rest-api-design) |
| "Django vs FastAPI" 선택 | 라우터 비교 프레임 — 기본값: admin·풀스택이면 Django, API 전용이면 FastAPI |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. N+1 (루프 안 관계 접근) — Django 버전
❌ `for order in Order.objects.all(): order.member.name` — 100건에 101쿼리
✅ ToOne은 `select_related("member")`(JOIN), ToMany는 `prefetch_related("items")`(IN 일괄) — 용도별 쿼리셋 메서드를 매니저/쿼리셋 클래스에 이름 붙여 비치
**왜**: dev-spring-jpa #1과 동일 구조(lazy 기본 + 무심한 루프). Django는 `django.db.connection.queries`·`assertNumQueries`로 카운트 단언이 내장돼 있다 — 예방의 기계화가 더 쉽다.

### 2. 쿼리셋 평가 시점 무지
❌ `qs = Order.objects.filter(...)` 를 if qs / len(qs) / 리스트 변환으로 여러 번 — 매번 또는 예상 밖 시점에 SQL
✅ 평가 트리거(반복·len·bool·list·슬라이스)를 알고 설계: 존재 확인은 `.exists()`, 개수는 `.count()`, 재사용은 명시 `list()` 1회
**왜**: 쿼리셋은 실행 계획서지 결과가 아니다 — `if qs:`는 전체 행을 끌어온다(exists()는 1행). "쿼리가 두 번 나가요"의 정체가 대부분 이 평가 의미론.

### 3. 마이그레이션을 생성만 하고 안 읽기
❌ `makemigrations` 산출물을 안 보고 커밋 — 어느 날 운영에서 테이블 락·데이터 손실 마이그레이션 실행
✅ 마이그레이션 파일은 **리뷰 대상 코드**: 위험 연산(컬럼 삭제·타입 변경·대형 테이블 인덱스) 식별 + 비호환 변경은 2단계(추가→전환→제거 — dev-cicd 마이그레이션 규칙) + `sqlmigrate`로 실제 SQL 확인
**왜**: 자동 생성이 안전 생성은 아니다 — Django는 "그 변경의 SQL"을 만들 뿐 운영 영향(락 시간)을 모른다. 대형 테이블 변경은 dev-postgres CONCURRENTLY 지식과 합류해야 한다.

### 4. settings.py 단일 파일 + 시크릿 하드코딩
❌ SECRET_KEY·DB 비밀번호가 settings.py에, dev/prod 차이는 주석 토글
✅ 설정 모듈 분리(base/dev/prod) 또는 django-environ류로 환경변수화 — `DEBUG=True` 운영 유출이 최악(스택트레이스·설정 노출)
**왜**: dev-spring #7·dev-docker #4와 동일 원리. Django 특유의 추가 위험: DEBUG=True는 디버그 페이지로 설정·쿼리·환경변수를 **응답으로** 보여준다 — 운영 켜짐은 즉시 사고다.

### 5. 비대 뷰 / 로직의 시그널 은닉
❌ 뷰 함수 200줄에 비즈니스 로직 / 핵심 규칙이 post_save 시그널에 숨어 "저장하면 뭔가 더 일어나는" 코드
✅ 뷰는 얇게(요청 해석→서비스/모델 메서드→응답 — dev-fastapi와 동일), 도메인 규칙은 모델 메서드·서비스 모듈에. 시그널은 진짜 횡단 관심(캐시 무효화 등)만 — 핵심 흐름엔 명시 호출
**왜**: 시그널은 호출 추적이 안 되는 암묵 실행이다 — "save 했더니 이메일이 두 번" 류 디버깅 블랙홀. dev-spring 프록시 미스터리와 같은 부류(보이지 않는 실행 경로).

### 6. raw SQL 충동 / ORM 만능 양극단
❌ 조금 복잡하면 바로 raw() / 반대로 집계 리포트를 ORM 체조 7단으로
✅ 사다리: 필드 lookup → `annotate/aggregate`(F·Q·Window까지 ORM은 강하다) → 그래도 안 되면 **이름 있는 raw 함수**로 격리(dev-spring-jpa "병용 정상"과 동일). ORM 결과와 raw의 경계를 한 모듈로
**왜**: ORM 체조는 읽기 불능, raw 산재는 인젝션·스키마 드리프트 위험. F/Q/annotate를 모르면 사다리 중간이 없어 양극단만 남는다 — 중간을 아는 것이 이 스킬의 일.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 쿼리 카운트 | 핵심 뷰에 `assertNumQueries` 단언 | 안티패턴 1 — 내장 도구 |
| DEBUG | 운영 False + ALLOWED_HOSTS 명시 | 안티패턴 4 |
| 마이그레이션 | PR마다 sqlmigrate 확인 흔적, 비호환은 2단계 | 안티패턴 3 |
| 앱 크기 | 한 앱이 모델 ~10개 넘으면 분할 검토 | 앱 = 바운디드 컨텍스트 후보(dev-ddd) |
| 신규 프로젝트 판단 | admin·인증·풀스택 필요 → Django / API 전용 → FastAPI | 경계 표 |

## 워크플로우 (기능 구현)

1. **모델·마이그레이션 먼저** — 모델 변경 → `makemigrations` → **산출물 읽기 + sqlmigrate** → 위험 분류.
2. **쿼리셋 설계** — 용도별 이름 있는 메서드(매니저), select/prefetch 명시.
3. **뷰는 얇게** — 폼/DRF 직렬화기가 검증(수동 파싱 금지 — dev-fastapi #4 동일).
4. **검증 (피드백 루프)**:
   ```
   python scripts/django_check.py <프로젝트>   # DEBUG·시크릿·N+1 모양 검출, exit 0이 통과
   python manage.py makemigrations --check     # 모델-마이그레이션 정합 (CI 게이트)
   pytest -x -q                                 # assertNumQueries 포함
   python manage.py check --deploy              # 운영 설정 점검 내장 도구
   ```

## 출력 템플릿

```
## [기능] 구현
### 모델·마이그레이션: <변경 + sqlmigrate 위험 분류>
### 쿼리 전략: <select/prefetch + 카운트 단언>
### 검증:
$ python scripts/django_check.py → <1줄>
$ manage.py makemigrations --check → <1줄>
$ pytest → <1줄>
### 확인 필요 / 한계
```

### 작성 예시

```
## 관심종목 목록+admin (가상 Django 모듈)
### 모델·마이그레이션: Watchlist(user FK, code) 신규 — sqlmigrate: CREATE TABLE만(위험 없음)
### 쿼리 전략: WatchlistQuerySet.with_user() = select_related("user") / 목록 뷰 assertNumQueries(2)
### 검증:
$ python scripts/django_check.py → total: 0 finding(s)
$ manage.py makemigrations --check → no changes
$ pytest → 6 passed (NumQueries 단언 포함)
### 확인 필요: admin 등록만으로 운영 CRUD 충분한지 (충분하면 별도 화면 생략 — 배터리 활용)
```

❌ "settings에 키 박고 DEBUG로 운영, 마이그레이션은 자동이니 믿고 적용"
✅ "환경 분리 + check --deploy + 마이그레이션 SQL 눈 확인 — 배터리는 쓰되 장부는 읽는다"

### 판단이 막히면 (확인 필요 4요소)

Django 결정은 운영 사실(테이블 규모·기존 스키마 소유권·배포 윈도우)에 막힌다 — 추측으로 마이그레이션을 적용하면 운영 락·손실이 난다. **누가·언제·어떻게·기대값** 4요소로 질의한다.

- **누가**: 운영 DB·배포 절차를 아는 사람 — "이 테이블이 몇 행인가/무중단 배포인가"는 코드가 아니라 운영이 답한다.
- **언제**: ① 변경 대상 테이블의 규모 불명(대형이면 2단계·CONCURRENTLY 필요 — dev-postgres) ② 기존 DB가 Django 외부 소유인지 미상(`managed=False` 판단) ③ read-your-writes 요구가 불명(레플리카 라우팅 가부).
- **어떻게**: `[확인 필요] <항목> — 현재 가정: <소형 테이블·즉시 적용>, 근거: <없음>, 다른 답(대형)이면 <2단계 마이그레이션+CONCURRENTLY>로 바뀜. 행 수?` (가정/근거/영향/택일).
- **기대값**: 테이블 행 수·소유권·배포 방식. 답이 오면 마이그레이션 전략을 확정한다. 끝내 불명이면 **가장 보수적 가정(대형 테이블·무중단)**으로 2단계 전략을 택하고 그 비용을 명시 — 락은 되돌릴 수 없으므로 과보수가 안전하다.

### 사용자가 권고를 거부하면

- "시그널로 깔끔하게 하고 싶어" → 추적 비용 1회 고지, 강행 시 시그널 목록을 README에 문서화하는 조건 제안(암묵을 명시로).
- "마이그레이션 그냥 적용해" → 위험 연산 포함 시에만 1회 경고(락·손실), 아니면 그대로 진행.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — DEBUG=True가 응답으로 내준 것들 (반복 실증)

Django 디버그 페이지는 예외 시 설정·환경변수·쿼리를 응답으로 렌더링한다 — 운영 DEBUG=True 사이트의 시크릿 노출은 보안 스캐너들이 자동 수확하는 표준 수확물(CWE-200, 정보유출)로, 공개 버그바운티 보고서에 반복 등장한다(HackerOne 공개 리포트 — MTN Group #1434276, Glovo #1561377, Dropcontact #963542 등 'Django debug mode enabled' 부류, 비인증 경로 접근만으로 디버그 페이지 노출. 2026-06 확인). Django가 `check --deploy`라는 내장 점검 명령을 만든 이유 자체가 이 반복이다. 교훈: ① 프레임워크의 친절(풍부한 디버그 정보)은 환경 플래그 하나로 무기가 된다 — 설정 분리(안티패턴 4)는 편의가 아니라 보안 경계 ② 내장 점검 도구(`check --deploy`)가 있는데 안 돌리는 것은 무료 보험 거절이다.

## 사용자 환경 적용

- 신규 API는 FastAPI가 기본값(기존 결정) — Django 출동은 admin이 필요한 운영 도구·CRUD 백오피스(예: 수집 데이터 검수 화면을 admin 공짜로). 그 경우 모델은 collector DB를 `managed=False`로 읽기 전용 매핑하는 경로가 자연스럽다.

## 레퍼런스

- `scripts/django_check.py` — DEBUG=True·하드코딩 SECRET_KEY·루프 내 관계 접근 모양 검출 (표준 라이브러리만, `python scripts/django_check.py` 데모)
- `references/orm-querysets.md` — 쿼리셋 평가 의미론 상세·annotate/F/Q 레시피·매니저 패턴·assertNumQueries 활용
- `references/evidence-checklist.md` — 출처(공식·Two Scoops) + 출고 전 체크리스트

## 한계

Django 5.2 LTS 기준 — 비동기 Django(async 뷰·ORM 부분 지원)는 성숙 진행 중이라 신규 채택 전 확인 필요(동기 Django가 기본 권장). DRF 상세(직렬화기 고급·viewset 라우팅)는 본 스킬 범위의 경계만 — 깊은 API 설계는 rest-api-design + 공식 문서. 템플릿·프론트 통합(HTMX류)은 다루지 않음.
