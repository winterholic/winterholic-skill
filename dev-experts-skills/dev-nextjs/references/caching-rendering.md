# 캐싱·렌더링 — 레이어 지도·전략 선택·hydration 디버깅 (SKILL.md 비중복)

> 주의: 이 영역은 Next 버전마다 기본값·옵션명이 가장 많이 변해왔다(15에서 fetch 기본 반전). 표의 개념 구분은 유지되지만 **옵션명·기본값은 사용 버전 공식 문서로 재확인**이 전제.

## 캐시 레이어 지도 (무엇이 캐시되는가)

| 레이어 | 대상 | 무효화 수단 |
|---|---|---|
| 요청 메모이제이션 | 단일 렌더 패스 내 동일 fetch 중복 제거 (서버) | 요청 끝나면 소멸 (React 캐시) |
| fetch 데이터 캐시 | fetch() 응답 (서버, 요청 간 영속) | `revalidate` 시간 / `revalidateTag` |
| 전체 라우트 캐시 | 정적 렌더된 페이지 HTML/RSC (서버) | `revalidatePath` / 재배포 |
| 라우터 캐시 | 방문한 세그먼트 (클라이언트 메모리) | 시간 만료·`router.refresh()` |

(공식 "Caching in Next.js"가 정의하는 4레이어. Next 16 Cache Components(`cacheComponents: true`)를 켜면 fetch 단위 데이터 캐시 대신 `use cache`로 표시한 함수·컴포넌트가 캐시 단위가 되고, `cacheLife`/`cacheTag`로 수명·무효화를 단다 — 캐시를 "어디에 무엇이"가 아니라 "이 함수가 캐시된다"로 명시화하는 방향. 확인 필요: 사용 프로젝트가 이 플래그를 켰는지부터.)

"갱신했는데 안 보임" 디버깅: 어느 레이어가 잡고 있나를 위에서 아래로 — 서버 데이터(curl로 확인) → 라우트(시크릿 창) → 라우터(refresh).

## 페이지 렌더 전략 선택

| 데이터 성격 | 전략 | 선언 |
|---|---|---|
| 거의 불변(문서·소개) | 정적 | 기본(동적 API 미사용 시) |
| 주기 갱신 허용(일봉·랭킹) | ISR | `export const revalidate = 60` (초) |
| 요청마다 달라야(사용자별·실시간) | 동적 | `cookies()`/`headers()` 사용 시 자동, 또는 `dynamic = "force-dynamic"` |
| 변경 이벤트 시 갱신(글 작성 후) | on-demand | Action에서 `revalidatePath/Tag` |
| 초 단위 실시간(체결 틱) | 페이지 캐시 무관 — 클라이언트 폴링/SSE | dev-realtime 영역 |

- ISR revalidate 값은 "이 데이터가 몇 초 낡아도 되는가"를 사용자 언어로 답한 것 — 주석으로 그 답을 남긴다(작성 예시의 "1분 신선도 충분").
- `cookies()`·`headers()`·searchParams 사용은 그 라우트를 동적으로 만든다 — "왜 정적이 안 되지"의 1순위 원인. (Next 15+에서 이들은 **async** — `const c = await cookies()`. 16에서 동기 사용 경로가 제거됐으니 `await` 누락은 빌드/런타임 에러 신호.)

## hydration 에러 디버깅 절차

1. 에러 메시지의 **컴포넌트 스택**에서 첫 자작 컴포넌트 찾기.
2. 3대장 대조: 시간/랜덤(서버·클라 다른 값) → 브라우저 분기(`typeof window` 렌더 분기) → HTML 중첩 위반(p>div, a>a 등 — 브라우저가 DOM을 고쳐버려 불일치).
3. 처방:
   - 시간·로캘: 서버에서 고정 문자열로 포맷해 내려보내거나, 클라 전용 표시(`mounted` 상태 후 렌더)
   - 브라우저 분기: 첫 렌더는 서버와 동일하게, 분기는 Effect 이후
   - 중첩 위반: 마크업 수정 (suppress 아님)
4. 의도된 불일치(로캘 시계)만 그 요소에 한해 suppressHydrationWarning + 사유 주석.

## 빌드 출력 읽기 (next build)

```
Route (app)                 Size     First Load JS
/                           5 kB     95 kB
/stocks/[code]              48 kB    128 kB     ← 차트 라이브러리가 여기만 추가됨 = 경계 성공
+ symbol: ○ 정적 / ƒ 동적 — 의도와 다르면 동적 전환 원인 추적(cookies 등)
```

- First Load JS가 전 라우트에서 같이 크면 → 공용 레이아웃이 클라이언트로 오염됐다는 신호(안티패턴 1).
- 무거운 클라 라이브러리는 `next/dynamic`으로 지연 — 차트·에디터의 표준 처리. 단 App Router에서 **`ssr: false`는 서버 컴포넌트 안에서 직접 쓸 수 없다**(에러). 페이지(RSC)에서 차트를 지연시키려면 `'use client'` 래퍼 컴포넌트를 만들고 그 안에서 `dynamic(..., { ssr: false })`를 호출 — 안티패턴 1의 "잎에서 client" 원칙과 같은 자리.

## standalone 배포 (홈서버)

```dockerfile
# next.config: output: "standalone"
FROM node:22-slim AS builder
...
RUN npx next build
FROM node:22-slim
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
CMD ["node", "server.js"]
```

standalone은 node_modules 전체 대신 추적된 의존만 복사 — 이미지가 수백 MB 절약된다(dev-docker 멀티스테이지와 합류). 환경변수는 런타임 주입 — 단 `NEXT_PUBLIC_*`은 **빌드 시점에 박제**되므로 환경별 빌드가 필요함을 인지(런타임 교체 불가).
