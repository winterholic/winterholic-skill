# 경계 검증·tsconfig·마이그레이션 사다리 (SKILL.md 비중복)

## zod 경계 패턴 (Pydantic의 TS 짝)

```typescript
import { z } from "zod";

const CandleSchema = z.object({
  code: z.string().regex(/^\d{6}$/),
  baseDate: z.string().transform((s) => new Date(s + "T00:00:00Z")),
  close: z.number().int().nonnegative(),
});
type Candle = z.infer<typeof CandleSchema>;          // 스키마가 타입의 단일 출처

const CandlesResponse = z.object({
  data: z.array(CandleSchema),
  next_cursor: z.string().nullable(),
});

async function fetchCandles(code: string): Promise<Candle[]> {
  const res = await fetch(`/v1/stocks/${code}/candles`);
  if (!res.ok) throw new ApiError(await res.json()); // 에러도 스키마로 (rest-api-design 표준 에러)
  return CandlesResponse.parse(await res.json()).data; // 검증 실패 = 즉시 ZodError (조용한 오염 차단)
}
```

- `parse`(throw) vs `safeParse`(Result) — 경계 한 곳에서 throw하고 위에서 잡는 게 기본, 부분 허용 흐름만 safeParse.
- 검증은 **경계 한 번만** — 내부 함수마다 재검증은 비용·소음. 경계 통과 후엔 타입을 믿는다(그래서 경계가 새면 안 된다).
- 적용 대상 전수: fetch 응답·localStorage·URLSearchParams·postMessage·JSON.parse 전부 — "내가 직렬화한 것"도 버전이 다르면 남이다.

## tsconfig 핵심 해설 (strict 패밀리)

```jsonc
{
  "compilerOptions": {
    "strict": true,                      // 아래 전부 포함하는 스위치
    "noUncheckedIndexedAccess": true,    // arr[i]가 T | undefined - 인덱스 구멍 봉쇄 (strict 밖!)
    "noEmit": true,                      // 번들러가 빌드하면 tsc는 검사만
    "target": "ES2022",
    "module": "ESNext", "moduleResolution": "Bundler",   // 번들러 프로젝트 기본 (확인 필요: 도구 권장값)
    "skipLibCheck": true                 // 의존성 d.ts 충돌 회피 - 실용 기본값
  }
}
```

- `noUncheckedIndexedAccess`는 strict에 **포함 안 됨** — 켜면 초기 에러가 늘지만 배열 인덱스·동적 키 접근의 undefined를 잡는 마지막 조각.
- 프레임워크(Next 등)가 생성한 tsconfig는 그쪽 기본을 따르되 strict 패밀리만 확인(우선순위 사다리).

## 점진 마이그레이션 사다리 (JS→TS / loose→strict)

1. `allowJs: true` + 새 파일만 .ts — 빌드 통합 먼저, 변환은 나중.
2. 파일 단위 변환: **의존 트리의 잎(유틸·타입 없는 순수 함수)부터** — 뿌리(엔트리)부터 하면 any가 위에서 아래로 전염.
3. 변환 시 임시 any 허용하되 `// TODO(ts): <사유>` 태그 — 검출기로 잔량 추적.
4. strict는 디렉토리별: 별도 `tsconfig.strict.json` + CI에서 그 디렉토리만 검사 → 전체 도달 시 본 설정에 병합.
5. 게이트: 신규·수정 파일은 any 0 (lint 차단) — 총량은 줄지 않아도 비율은 는다(dev-python mypy 사다리와 동일 구조).

## 에러 메시지 해석 레시피

| 메시지 | 실제 의미 |
|---|---|
| `X is not assignable to Y` 긴 체인 | 가장 안쪽 줄만 읽기 — 거기가 실제 불일치 |
| `Object is possibly 'undefined'` | 좁히기 누락 — `?.`로 도피하기 전에 "왜 undefined일 수 있나"부터(설계 문제일 수 있음) |
| `Property 'x' does not exist on type 'never'` | 내로잉이 모든 케이스를 소거 — 유니언 정의와 가드 조건 모순 |
| `Type instantiation is excessively deep` | 타입 체조 한계 초과 — 구조 단순화 신호(절제 가이드) |
| 라이브러리 타입과 싸움 | 내 코드 문제 아닐 수 있음 — DefinitelyTyped 버전 vs 라이브러리 버전 정합부터 확인 |
