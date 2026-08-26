# 쿼리셋 심화 — 평가 의미론·annotate 레시피·매니저 패턴 (SKILL.md 비중복)

## 평가 트리거 전체 목록 (외우는 게 아니라 참조)

평가됨: 반복(for) · 슬라이스에 step · `len()` · `list()` · `bool()/if` · `repr()`(쉘!) · 직렬화
평가 안 됨(계획만 합성): `.filter/.exclude/.annotate/.order_by` 연쇄 · step 없는 슬라이스(LIMIT으로 변환)

- 쉘에서 `qs` 입력(repr)도 평가다 — "쉘에선 됐는데"의 한 원인.
- 캐시: 한 번 평가된 쿼리셋은 결과를 들고 있다(재반복 시 SQL 없음) — 단 `.all()`을 다시 부르면 새 쿼리셋.

## select_related vs prefetch_related 정밀 규칙

| | select_related | prefetch_related |
|---|---|---|
| 대상 | FK·OneToOne (ToOne) | ManyToMany·역방향 FK (ToMany) — ToOne도 가능 |
| 방식 | SQL JOIN 1방 | 본 쿼리 + IN 쿼리 (총 2방) |
| 함정 | 깊은 체인 JOIN 비대 | `Prefetch(queryset=...)` 없이 추가 filter 시 **프리페치 무효**(새 쿼리) |

```python
# 프리페치에 조건 걸기 - filter를 나중에 하면 무효가 된다
Order.objects.prefetch_related(
    Prefetch("items", queryset=Item.objects.filter(active=True), to_attr="active_items")
)
```

## annotate/F/Q 레시피 (raw 충동 전에 — 사다리의 중간)

```python
from django.db.models import F, Q, Count, Sum, Window
from django.db.models.functions import Rank

# 집계 컬럼
Order.objects.annotate(item_count=Count("items"))
# 필드 간 연산·원자 업데이트 (경합 안전 - dev-postgres 락 절 동형)
Stock.objects.filter(code=c).update(views=F("views") + 1)
# OR·부정 조건
Candle.objects.filter(Q(close__gte=hi) | Q(volume=0), ~Q(flag="suspect"))
# 윈도우 (랭킹류 - raw 충동 1순위였던 것)
Candle.objects.annotate(rank=Window(Rank(), partition_by=F("code"), order_by=F("close").desc()))
# 조건부 집계
Order.objects.aggregate(paid=Count("id", filter=Q(status="paid")))
```

- `values()/values_list()`로 dict/튜플 직행은 DTO 직접 조회의 Django판 — 표시 전용이면 모델 인스턴스 비용 생략.
- `only()/defer()`는 미세 최적화 — 잘못 쓰면 접근 시 추가 쿼리(부분 N+1). values가 보통 정답.

## 매니저·쿼리셋 패턴 (용도별 이름)

```python
class CandleQuerySet(models.QuerySet):
    def for_chart(self, code):           # 용도가 이름 - dev-spring-jpa '용도별 조회'와 동일
        return self.filter(code=code).order_by("-base_date")
    def with_quality(self):
        return self.exclude(flag="rejected")

class Candle(models.Model):
    objects = CandleQuerySet.as_manager()
# 사용: Candle.objects.with_quality().for_chart("005930")[:50]
```

체이닝 가능한 쿼리셋 메서드(매니저 메서드보다)가 기본 — 조합이 자유롭다.

## assertNumQueries 활용

```python
def test_order_list_two_queries(self):
    with self.assertNumQueries(2):          # 본문 1 + prefetch 1
        resp = self.client.get("/orders/")
```

- pytest-django는 `django_assert_num_queries` fixture.
- 횟수가 깨질 때: 정확 횟수 고집보다 상한(`<=3`) 단언이 유지비 낮음 — 목적은 N+1 회귀 검출이지 쿼리 회계가 아니다.

## 트랜잭션·동시성 요점

- 기본 autocommit — 묶음 원자성은 `transaction.atomic()` 명시(데코레이터/컨텍스트). 뷰 전체 트랜잭션(ATOMIC_REQUESTS)은 외부 호출 포함 시 dev-spring #3과 같은 함정.
- `select_for_update()`는 atomic 블록 안에서만 — 읽고-계산-쓰기 경합의 처방(dev-postgres 락 절).
- 커밋 후 실행은 `transaction.on_commit(lambda: notify())` — 이벤트 발행 위치(dev-event-driven #1의 Django 관용구).
