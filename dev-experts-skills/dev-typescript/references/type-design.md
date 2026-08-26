# 타입 설계 — 구별된 유니언·제네릭 절제·유틸리티 지도 (SKILL.md 비중복)

## 구별된 유니언 레시피

```typescript
type FetchState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ok"; data: T }
  | { status: "error"; error: Error };

function render(s: FetchState<Candle[]>) {
  switch (s.status) {
    case "ok": return draw(s.data);        // 여기서만 data 접근 가능 - 자동 내로잉
    case "error": return show(s.error);
    case "idle":
    case "loading": return spinner();
    default: return assertNever(s);        // 새 status 추가 시 컴파일 에러로 알림
  }
}
function assertNever(x: never): never { throw new Error(`unreachable: ${JSON.stringify(x)}`); }
```

- 판별 필드(status)는 리터럴 타입이어야 내로잉이 작동 — string이면 무효.
- `assertNever` 완전성 검사가 유니언의 절반 가치 — 케이스 추가를 컴파일러가 추적해준다.
- 이벤트·액션·API 응답 변형(성공/실패) 전부 같은 패턴.

## 제네릭 절제 가이드

| 신호 | 판정 |
|---|---|
| 타입 파라미터가 두 곳 이상에서 관계를 만든다 (`(xs: T[], f: (x: T) => U): U[]`) | ✅ 제네릭의 일 |
| 타입 파라미터가 한 번만 등장 (`function f<T>(x: T): void`) | ❌ 그냥 `unknown` — 제네릭 의미 없음 |
| 호출자가 타입을 명시해야만 작동 | ⚠️ 추론 실패 — 시그니처 재설계 |
| 조건부 타입 3단 중첩+ | ⚠️ 읽기 비용 초과 — 오버로드·함수 분리 검토 |

- `extends` 제약은 "이 연산을 쓰니까"만큼만: `<T extends { id: string }>` — 넓은 제약은 호출처를 불필요하게 조인다.

## 유틸리티 타입 지도 (언제 무엇)

| 도구 | 용도 | 한 줄 |
|---|---|---|
| `Pick / Omit` | 기존 타입의 부분집합 | DTO 파생 — 단 3개 이상 파생되면 기반 타입 분리 신호 |
| `Partial / Required` | 전 필드 옵셔널/필수화 | PATCH 입력(Partial) — 깊은 중첩엔 미적용(얕음) |
| `Record<K, V>` | 키 맵 | `Record<Status, Color>` — 키 추가 시 값 누락이 에러 |
| `ReturnType / Parameters` | 함수에서 타입 추출 | 외부 라이브러리 함수 타입 재사용 |
| `as const` | 리터럴 고정 | 설정 객체·튜플 — enum 대체 패턴의 반쪽 |
| `satisfies` | 검사하되 추론 보존 | `const config = {...} satisfies Config` — 타입 표기(`: Config`)는 추론을 넓혀버림, satisfies는 유지 |
| `NonNullable` | null/undefined 제거 | 필터 후 타입 정리 |

## 브랜드(명목) 타입 — 같은 string끼리 섞임 방지

```typescript
type StockCode = string & { readonly __brand: "StockCode" };
const asStockCode = (s: string): StockCode => {
  if (!/^\d{6}$/.test(s)) throw new Error(`invalid code: ${s}`);
  return s as StockCode;   // 검증 직후의 as - 정당한 단언의 예
};
```

- userId와 orderId가 둘 다 string이라 바꿔 넣어도 컴파일되는 문제의 처방.
- 비용(생성 함수 강제)이 있으니 **섞이면 사고인 식별자**에만 — 모든 string에 바르면 체조가 된다.

## 함수 타입 정밀화

- 옵션 객체가 인자 3개를 이긴다: `f(code, from, to, limit?)` → `f({ code, range, limit })` — 호출처 가독 + 추가가 비파괴.
- 콜백 시그니처는 받는 쪽이 정의: `onTick: (t: Tick) => void` — 콜백 반환값을 쓰지 않으면 `void`로 선언해 "반환해도 무시됨"을 계약화.
- 오버로드는 마지막 수단 — 유니언 입력 + 내로잉으로 안 되는 경우만(보통 된다).
