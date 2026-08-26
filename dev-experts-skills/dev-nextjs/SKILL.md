---
name: dev-nextjs
description: "Next.js 앱 작업 시 사용. App Router 구조, 서버/클라이언트 컴포넌트 경계('use client'), 데이터 fetch·캐싱 전략, hydration 에러, Server Actions, 메타데이터·이미지 최적화, 배포 형태(standalone) 판단을 다룬다. 사용자가 'Next.js', 'next', 'App Router', 'use client', 'SSR', 'hydration', 'Server Action', 'ISR', 'generateMetadata', 또는 'Hydration failed', 'Text content does not match' 에러를 언급하면 트리거. React 훅·상태 설계 자체(→ dev-react), 타입(→ dev-typescript), API 계약(→ dev-rest-api-design), Vercel 외 인프라 배포 상세(→ dev-docker/dev-cicd)에는 사용하지 않는다. 기보유 sub-skills의 next-best-practices(Vercel 공식)와 병용 — 그쪽이 버전 상세의 1차 출처, 이쪽은 경계 설계·함정."
---

# dev-nextjs — Next.js 전문가

> 기준: Next.js 16 / App Router / Turbopack 기본(dev·build 모두) / React 19.2 / Node 20.9+ (2026-06, 16 발표 2025-10-21·공식 블로그) · 부패 등급: **최속(분기 점검 의무)** — 버전 의존 세부는 항상 공식 문서·기보유 next-best-practices가 이긴다. 이 문서는 잘 안 변하는 경계 원칙·함정 위주.
>
> Next 16 진입 시 즉시 깨지는 것: ① `cookies()`·`headers()`·`draftMode()`·`params`·`searchParams`는 **async**(반드시 `await`) — 15에서 비동기화, 16에서 동기 사용 경로 제거 ② `experimental.ppr`/`experimental.dynamicIO` 플래그 폐지 → `cacheComponents: true`로 통합 ③ Turbopack이 빌드까지 기본(webpack은 `--webpack` 명시). 업그레이드는 `npx @next/codemod@canary upgrade latest` 전제.

## 정체성

Vercel 공식 문서 전통. **"서버가 기본, 클라이언트는 선언한 만큼만"** — App Router의 모든 설계 질문은 결국 하나다: *이 코드는 어디서 실행되는가, 그리고 그걸 내가 선택했는가.* hydration 에러·비밀 유출·과대 번들 전부 이 질문을 안 한 대가다.

핵심 신조: 'use client'는 경계 선언이지 파일 표시가 아니다 · fetch는 서버에서 · 캐시는 명시적으로 · 페이지는 RSC, 상호작용은 잎(leaf)에서.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 서버/클라 경계·라우팅·캐싱 | 훅·상태·리렌더 (→ dev-react) |
| hydration 진단 | 타입 (→ dev-typescript) |
| Server Actions·route handler | API 계약 규약 (→ dev-rest-api-design) |
| Next 빌드·standalone 산출 | 컨테이너·CI 일반 (→ dev-docker/dev-cicd) |
| 버전 상세·신기능 | 기보유 next-best-practices + 공식 문서 (1차) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 최상단 'use client' 도배
❌ 페이지·레이아웃에 'use client' — 트리 전체가 클라이언트 번들로
✅ 페이지는 서버 컴포넌트 유지, 상호작용 필요한 **잎 컴포넌트만** 분리해 'use client' — 경계 아래는 전부 클라이언트임을 인지
**왜**: 'use client'는 그 파일이 아니라 **그 지점 아래 서브트리 전체**를 클라이언트로 만든다. 최상단 선언 = 서버 컴포넌트 포기 = 번들 비대 + 서버 fetch 이점 상실. 경계는 좁게, 잎에서.

### 2. 서버 전용 비밀을 클라이언트 경계 안으로
❌ 'use client' 파일(또는 그 임포트 체인)에서 `process.env.API_SECRET` 사용 — 번들에 박제
✅ 비밀 사용은 서버 컴포넌트·Server Action·route handler에서만. 클라이언트에 필요한 설정만 `NEXT_PUBLIC_` 접두(=공개 선언). `server-only` 패키지 임포트로 서버 전용 모듈 오용을 빌드 에러화
**왜**: 클라이언트 번들은 누구나 읽는 텍스트다. `NEXT_PUBLIC_` 없는 env가 클라이언트에서 undefined로 나오는 건 보호 장치인데, 이를 NEXT_PUBLIC_으로 "고치면" 유출이 된다 — 접두의 의미는 "공개해도 됨" 선언이다.

### 3. hydration 불일치를 suppressHydrationWarning으로 덮기
❌ 경고가 시끄럽다고 suppress / 무시
✅ 원인 3대장부터: ① `Date.now()`·`Math.random()`·로캘 포맷(서버와 클라가 다른 값) ② `typeof window` 분기 렌더 ③ HTML 중첩 규칙 위반(`<p>` 안 `<div>`). 시간·랜덤은 클라이언트 전용 표시(`useEffect` 후 표시) 또는 서버에서 고정값 전달
**왜**: hydration 불일치는 "서버가 그린 것과 클라이언트 첫 렌더가 다르다"는 사실 보고다 — 덮으면 그 불일치가 사용자 화면 깜빡임·상태 꼬임으로 남는다. suppress는 `<time>` 로캘 표시처럼 불일치가 의도인 좁은 지점만.

### 4. 클라이언트에서 자기 API route로 fetch (불필요 왕복)
❌ 서버 컴포넌트로 만들 수 있는 페이지에서 useEffect→`/api/list` fetch — [브라우저→내 서버→DB]를 [내 서버→DB]로 끝낼 수 있는데
✅ 데이터는 서버 컴포넌트에서 직접(DB·내부 API 호출) — route handler는 **외부 소비자**(웹훅·모바일·다른 서비스)용. 상호작용 후 변경은 Server Action + revalidate
**왜**: 자기 자신에게 HTTP를 치는 것은 직렬화·왕복·로딩 상태를 자초하는 우회로다. App Router에서 "내 페이지를 위한 내 API route"는 대부분 서버 컴포넌트 미사용 신호.

### 5. 캐시 동작을 추측 (명시 없는 fetch)
❌ "왜 데이터가 안 바뀌지?"/"왜 매번 느리지?" — 캐시·렌더 모드를 기본값에 맡기고 추측
✅ 의도를 코드로: 정적이면 명시적 revalidate(`export const revalidate = 3600` 또는 fetch 옵션), 항상 신선해야 하면 `dynamic = "force-dynamic"`/`cache: "no-store"`, 변경 시점 갱신은 `revalidatePath/Tag`. **버전마다 기본값이 변해온 영역이므로(15에서 fetch 기본 no-cache화) 기본값 의존 금지**. Next 16의 Cache Components(`cacheComponents: true` + `use cache` 디렉티브)를 켰다면 캐시는 fetch 옵션이 아니라 `use cache`로 표시한 함수·컴포넌트 단위로 옮겨간다 — 이 경우 PPR이 기본이 되어 정적 셸 + 동적 구멍 모델로 사고한다(아래 실전 케이스 참조)
**왜**: Next 캐싱은 강력하지만 레이어가 많다(fetch 캐시·라우트 캐시·라우터 캐시). 명시가 없으면 "되는 것 같은" 상태와 "안 바뀌는" 상태를 오간다 — 캐시는 선언한 만큼만 믿는다.

### 6. Server Action을 공개 API가 아니라고 착각
❌ Action 안에서 인증·검증 생략 — "내 폼에서만 불리니까"
✅ Action도 네트워크로 노출되는 엔드포인트다: 인증 확인 + 입력 zod 검증(dev-typescript 경계)을 route handler와 동일 기준으로
**왜**: Server Action은 빌드 시 RPC 엔드포인트가 된다 — 폼 밖에서도 호출 가능하다. "UI가 막아준다"는 보안이 아니다(dev-web-security의 클라이언트 검증 무신뢰 원칙).

### 7. 이미지·폰트·메타데이터 수동 처리
❌ `<img>` 생 태그·CSS @import 폰트·head 수동 조작
✅ `next/image`(자동 최적화·레이아웃 시프트 방지)·`next/font`(셀프 호스팅·FOUT 방지)·`generateMetadata`(라우트별 SEO) — 프레임워크가 만든 길
**왜**: 이 셋은 Next가 존재하는 이유의 절반(성능 기본값) — 우회하면 Core Web Vitals(LCP·CLS)를 수동으로 다시 발명해야 한다. SEO 상세는 dev-seo-analytics.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 'use client' 위치 | 라우트 세그먼트 파일(page/layout) 금지, 잎 컴포넌트만 | 안티패턴 1 |
| 캐시 선언 | 데이터 fetch마다 캐시 의도 명시(주석 또는 옵션) | 안티패턴 5 |
| 비밀 접두 | NEXT_PUBLIC_은 공개 가능 값만 — 코드리뷰 항목 | 안티패턴 2 |
| 번들 점검 | `next build` 출력의 First Load JS — 라우트당 150kB 넘으면 경계 재검토 (확인 필요: 현 권장치) | 경계 설계의 정량 신호 |
| self-host 배포 | `output: "standalone"` + dev-docker 멀티스테이지 | 홈서버 배포 기본형 |

## 워크플로우 (페이지·기능 신설)

1. **경계 스케치 먼저** — 라우트 트리에 서버(데이터)와 클라이언트(상호작용) 경계를 표시: "페이지=RSC, <검색창>·<차트>만 client". 이 스케치가 코드보다 먼저.
2. **데이터 흐름** — 읽기: 서버 컴포넌트 직접 fetch(+캐시 의도 명시). 쓰기: Server Action(검증+인증) → revalidate. 외부 소비자 있을 때만 route handler(계약은 dev-rest-api-design).
3. **클라이언트 잎 구현** — dev-react 규칙으로(훅·상태). 서버에서 받은 props는 직렬화 가능해야 함(함수·Date 주의 — Date는 문자열로 넘겨 클라에서 파싱).
4. **검증 (피드백 루프)**:
   ```
   python scripts/next_check.py app/        # 경계·비밀·suppress 기계 검출, exit 0이 통과 (표준 라이브러리만 — Python 3 있으면 즉시 실행; 없으면 이 단계만 생략하고 아래 수동 점검 3항목으로 대체)
   npx tsc --noEmit && npx eslint app/
   npx next build                            # 빌드 + First Load JS 확인 (Turbopack 기본)
   # hydration: 개발 콘솔 경고 0 확인
   # next_check.py 미실행 시 수동 점검: ① page/layout에 'use client' 없는지 ② 클라 경계 안 NEXT_PUBLIC_ 없는 env 비밀 없는지 ③ suppressHydrationWarning 위치·사유 기록
   ```

## 출력 템플릿

```
## [페이지/기능] 구현
### 경계 스케치: <RSC 트리 + 'use client' 잎 목록>
### 데이터: <읽기 경로(캐시 의도) / 쓰기 경로(Action+revalidate)>
### 검증:
$ python scripts/next_check.py app/ → <1줄>
$ npx next build → First Load JS <라우트별 1줄>
콘솔: hydration 경고 <0건>
### 확인 필요 / 한계
```

### 작성 예시

```
## 종목 대시보드 페이지
### 경계 스케치: app/stocks/[code]/page.tsx(RSC) → <CandleChart>(client, 잎) + <PeriodSelect>(client, 잎)
### 데이터: 읽기 — page에서 API 서버 fetch, revalidate 60(분봉 아님·1분 신선도 충분 — 주석 명시)
  / 쓰기 없음 (조회 전용)
### 검증:
$ python scripts/next_check.py app/ → total: 0 finding(s)
$ npx next build → /stocks/[code] First Load JS 128kB
콘솔: hydration 경고 0건 (차트 시간축은 서버에서 ISO 문자열로 전달)
### 확인 필요: revalidate 60이 장중 체감에 충분한지 (불충분하면 클라 Query 폴링 병행 검토)
```

❌ "page.tsx에 'use client' 박고 useEffect로 fetch" (RSC 포기 + 왕복 + 경쟁)
✅ "페이지는 서버에서 fetch, 차트 잎만 client — 캐시 의도는 주석으로"

### 사용자가 권고를 거부하면

- "그냥 다 클라이언트로, CSR처럼 쓸래" → 따르되 비밀 경계(#2)만 확인 — 그건 취향이 아니라 유출. 나머지는 번들 비용 1줄 기록(partial).
- "hydration 경고 끄자" → 원인 3대장 1회 점검 제안(보통 5분). 강행 시 suppress 위치와 사유 기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

### 판단이 막힐 때 (확인 요청 4요소)

캐시 신선도 요구·배포 형태(Vercel vs 홈서버)·데이터 소비자 범위는 운영 요구를 아는 사용자만 정한다 — 부패 최속 영역이라 추측은 버전 업마다 깨진다. 묶어서 묻는다:
- **누가**: 사용자(데이터 신선도 요구·배포 대상·외부 소비자 유무 소유자).
- **언제**: 데이터 흐름 설계 단계(워크플로우 2) — 캐시 의도(정적/동적/revalidate)나 route handler 필요 여부가 불명일 때.
- **어떻게**: "현재 항목 / 추측값 / 근거 / 기대 답변"으로. 예) "시세를 `revalidate 60`으로 가정했는데(근거: 1분 신선도면 충분 추정), 장중 실시간이 필요하면 클라 폴링 병행이 맞습니다 — 체감 신선도 요구가 얼마입니까?"
- **기대값**: 신선도 초·배포 대상·소비자 범위 중 하나. 받으면 캐시 의도를 코드로 확정 명시, 못 받으면 가장 안전한 가정(경계 좁게·캐시 의도 주석 명시·비밀은 서버에·standalone)으로 진행 + 버전 의존 항목은 공식 문서 확인 라벨.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — 기본값이 바뀌는 프레임워크 (Next 14→15 캐시 대전환, 2024)

Next 15는 **fetch 기본 캐시를 force-cache에서 no-store로 뒤집었다** — 14까지 "왜 데이터가 안 바뀌어요"를 양산하던 기본 캐싱이 반대로 뒤집히며, 이번엔 기본값에 기대던 정적 페이지들이 조용히 동적(매 요청 fetch)이 되어 비용·지연이 늘어난 사례가 커뮤니티에 줄을 이었다(출처: Next.js 15 공식 release notes·upgrade guide). 교훈: ① 부패 최속 스킬에서 **기본값 의존은 버전 업그레이드 때마다 행동이 바뀌는 코드**를 뜻한다 — 캐시 의도 명시(안티패턴 5)는 스타일이 아니라 업그레이드 보험 ② 메이저 업그레이드는 `next-upgrade`류 codemod + upgrade guide 정독이 전제(기보유 next-best-practices 참조) ③ 같은 이유로 이 스킬의 버전 의존 서술도 의심하라 — 라벨(16)과 다르면 공식 문서가 이긴다.

## 사용자 환경 적용

- 배포는 Vercel이 아니라 홈서버 가능성 — `output: "standalone"` + dev-docker 멀티스테이지 + dev-nginx 리버스 프록시가 그 경로. Vercel 전용 기능(Edge 일부·Analytics) 의존을 피하는 설계가 이식성 유지.
- 기보유 `sub-skills\next-best-practices`(vercel-labs)가 버전 상세의 1차 참조 — 이 스킬과 충돌하면 그쪽(더 최신·더 구체) 우선, 경계 설계 원칙은 이쪽.

## 레퍼런스

- `scripts/next_check.py` — Next 소스 냄새 검출기: 라우트 파일 'use client'·NEXT_PUBLIC_ 의심값·suppressHydrationWarning·클라이언트 env 비밀 (표준 라이브러리만, `python scripts/next_check.py` 데모)
- `references/boundary-data.md` — 서버/클라 경계 설계 상세·직렬화 규칙·Server Action 패턴·route handler 판단
- `references/caching-rendering.md` — 캐시 레이어 지도·revalidate 전략·정적/동적 판단·hydration 디버깅 절차
- `references/evidence-checklist.md` — 출처(공식 release notes) + 출고 전 체크리스트

## 한계

부패 최속 — 이 문서의 버전 의존 서술(기본값·옵션명)은 분기마다 라벨 점검 대상이고, 원칙(경계 좁게·캐시 명시·비밀 서버에)만 오래 간다. Pages Router 레거시는 다루지 않음(마이그레이션은 공식 가이드). Vercel 플랫폼 기능·과금은 공식 문서로.
