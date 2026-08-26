# evidence + 출고 전 체크리스트

## 실증·출처

- **Next.js 15 release notes·upgrade guide (2024)** — fetch 기본 캐시 반전(force-cache→no-store). SKILL.md 실전 케이스 원 출처 — "기본값 의존 금지"의 직접 근거. (https://nextjs.org/docs/app/guides/upgrading/version-15 — async request API 변경도 여기서 시작)
- **Next.js 16 발표 (2025-10-21, 공식 블로그 nextjs.org/blog/next-16)** — Turbopack dev·build 기본화·React 19.2 채택·React Compiler 안정화·Cache Components 도입. 버전 라벨 출처(웹 확인 2026-06, 최신 패치 16.2.x).
- **공식 업그레이드 가이드 "Upgrading: Version 16" (https://nextjs.org/docs/app/guides/upgrading/version-16, lastUpdated 2026-05)** — Node 20.9+·TS 5.1+·React 19.2 요구, `cookies()/headers()/params/searchParams` async 강제(동기 경로 제거), `experimental.ppr`/`experimental.dynamicIO` 폐지→`cacheComponents` 통합, `middleware.ts`→`proxy.ts` 이름변경. 부패 최속 항목의 1차 점검처.
- **공식 문서 "use cache" 디렉티브 + cacheComponents 설정** (https://nextjs.org/docs/app/api-reference/directives/use-cache , .../config/next-config-js/cacheComponents) — Next 16 캐시 모델 전환(fetch 옵션→함수/컴포넌트 단위 캐시, `cacheLife`/`cacheTag`)의 1차 출처. PPR 안정화의 실체.
- **공식 문서 "Server and Client Components"** — 'use client' 경계 의미론(서브트리 전체)·합성 패턴의 1차 출처. `next/dynamic` `ssr:false`가 서버 컴포넌트 직접 사용 불가라는 제약도 여기/lazy-loading 문서 근거.
- **공식 문서 "Caching in Next.js"** — 4레이어 캐시 지도(요청 메모이제이션·데이터 캐시·전체 라우트 캐시·라우터 캐시)의 원전(버전별 재확인 전제).
- **React 공식 "Hydration mismatch" 에러 문서** — 3대장(시간/브라우저 분기/중첩 위반) 분류의 출처.
- 오픈소스 차용 표기: **기보유 vercel-labs/next-best-practices가 1차 참조**(frontmatter에 병용 명시), vercel-labs/next-cache-components·next-upgrade는 색인 인지. **역흡수**: 공식 스킬들은 자사 플랫폼 전제가 강함 — 홈서버 standalone 배포·NEXT_PUBLIC_ 빌드 박제 함정·기계 검출이 본 스킬 차별점.

## 출고 전 체크리스트 (페이지·기능 출고 시)

- [ ] 라우트 파일(page/layout)에 'use client' 없음 (`next_check.py` 0건)
- [ ] 모든 fetch에 캐시 의도 선언(+사유 주석)
- [ ] 비밀이 클라이언트 체인에 없음 / NEXT_PUBLIC_에 비밀 없음
- [ ] 서버 전용 모듈에 `import "server-only"`
- [ ] Server Action에 인증+검증 (route handler 기준과 동일)
- [ ] Action 후 revalidatePath/Tag (갱신 안 보임 예방)
- [ ] Date 등 비직렬화 값이 props로 안 넘어감 (ISO 문자열)
- [ ] 개발 콘솔 hydration 경고 0
- [ ] next build의 First Load JS 확인 — 급증 시 경계 재검토
- [ ] loading.tsx / error.tsx 비치 (fetch하는 세그먼트)
- [ ] (Next 15+) `cookies()`/`headers()`/`params`/`searchParams`에 `await` (16에서 동기 경로 제거 — 누락 시 에러)
- [ ] (Cache Components 켠 프로젝트) 캐시 의도를 fetch 옵션이 아니라 `use cache` + `cacheLife`/`cacheTag`로 표현
- [ ] (홈서버 배포 시) standalone + 환경별 NEXT_PUBLIC_ 빌드 인지

## 점검 주기 (부패 최속 — 분기 의무)

- Next 메이저·마이너 vs 라벨(현 16) — upgrade guide의 캐시·기본값 변화 최우선 확인
- 기보유 next-best-practices 스킬 갱신 여부 대조
- 검출기 룰(라우트 파일 목록·옵션명) 유효성
