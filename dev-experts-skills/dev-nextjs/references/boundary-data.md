# 경계·데이터 — 서버/클라 설계·직렬화·Server Action (SKILL.md 비중복)

## 경계 설계 패턴

```
app/stocks/[code]/page.tsx          (RSC - fetch, 비밀 OK, 훅 불가)
└─ <StockHeader name= .../>          (RSC - 표시만)
└─ <CandleChart data={...}/>         ('use client' - 차트 라이브러리/상호작용)
└─ <WatchButton code= .../>          ('use client' - 클릭 핸들러)
```

- **서버→클라 props는 한 방향 단순 데이터** — 함수·클래스 인스턴스 전달 불가. 클라→서버 호출은 Server Action만.
- 클라이언트 컴포넌트가 서버 컴포넌트를 **children으로 받는 것은 가능** — "client 안에 RSC 못 넣는다"가 아니라 "client가 RSC를 임포트 못 한다"가 정확한 규칙. 레이아웃 셸(client) + 콘텐츠(RSC) 합성이 이 원리.
- `server-only` / `client-only` 패키지: DB 모듈 맨 위에 `import "server-only"` — 클라이언트 체인에 섞이면 빌드 에러로 조기 검출(안티패턴 2의 기계화).

## 직렬화 규칙 (RSC → client props)

| 타입 | 처리 |
|---|---|
| string/number/boolean/null·배열·평면 객체 | 그대로 |
| Date | ISO 문자열로 넘기고 클라에서 파싱 — hydration 시간 불일치도 함께 예방 |
| Decimal·BigInt | 문자열로 (dev-rest-api-design 금액 규칙과 동일) |
| 함수·핸들러 | 불가 — 상호작용은 클라 컴포넌트 안에서 정의, 서버 일은 Action 전달 |
| 거대 데이터 | 전체 직렬화가 HTML에 박힌다 — 필요한 만큼만 가공해 전달(limit 규약) |

## Server Action 표준형

```tsx
// app/actions.ts
"use server";
import { z } from "zod";

const Input = z.object({ code: z.string().regex(/^\d{6}$/) });

export async function addWatch(raw: unknown) {
  const user = await requireUser();              // 1. 인증 - Action도 공개 엔드포인트
  const { code } = Input.parse(raw);             // 2. 검증 - 폼을 믿지 않는다
  await db.watchlist.add(user.id, code);         // 3. 작업
  revalidatePath("/watchlist");                  // 4. 캐시 갱신 - 이게 빠지면 "됐는데 안 보임"
}
```

- `useActionState`(클라)로 pending·에러 상태 연결 — 수제 loading state 불필요.
- Action에서 redirect는 try/catch **밖**에서 (redirect는 throw로 구현돼 있어 catch에 잡히면 안 됨 — 단골 함정).

## route handler가 정당한 경우

1. 외부 소비자(웹훅 수신·모바일 앱·타 서비스) — 계약은 dev-rest-api-design
2. 스트리밍·파일 응답 등 컴포넌트 모델 밖 응답
3. 서드파티가 요구하는 콜백 URL (OAuth redirect 등)

"내 페이지의 데이터"는 해당 없음(안티패턴 4) — 서버 컴포넌트가 그 일이다.

## 라우팅 구조 활용 요점

- `loading.tsx` = 그 세그먼트의 Suspense 폴백 — 데이터 fetch하는 페이지엔 기본 비치(스트리밍 무료).
- `error.tsx` = 세그먼트 에러 바운더리('use client' 필수) — 페이지 전체 백지 방지.
- 병렬 fetch: 한 페이지에서 fetch 2개를 await 연쇄하지 말고 `Promise.all` — RSC에서도 워터폴은 워터폴.
- `generateStaticParams` = 알려진 경로 사전 생성(구 getStaticPaths) — 종목 상위 N개 사전 렌더 같은 용도.
