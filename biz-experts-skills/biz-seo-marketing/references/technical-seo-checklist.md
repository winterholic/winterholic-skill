# technical-seo-checklist — 기술 SEO 실무 체크리스트

> 기준 시점 라벨: 2026-07. CWV 임계값·정책은 부패 빠름 — web.dev / Search Central 공식 최신 확인.
> 출처: developers.google.com/search · web.dev · 2026-07-01 검증.
> ⚠️ 이 스킬(biz-seo)은 전략·의도·권위 축. **실제 구현·배포는 (→ dev-seo-analytics)로 위임.** 이 파일은 전략가가 "무엇이 빠졌나"를 진단·요청할 수 있는 수준의 체크리스트다. 어떤 항목도 "이대로 하면 순위 오른다"는 보장이 아니다 — 대부분은 "안 되면 확실히 손해, 되면 기본기" 성격.

## 1. 크롤 (crawl) — 검색엔진이 페이지에 도달하는가
- [ ] **robots.txt**: 중요 페이지·리소스(CSS/JS 포함) 차단 안 함. `Disallow`로 인덱싱 막지 말 것(그건 크롤 차단이지 인덱싱 차단이 아님 — noindex와 혼동 주의).
- [ ] **XML 사이트맵**: 정규 URL만, 200 응답만, `<lastmod>` 정확. Search Console 제출. 대형 사이트는 사이트맵 인덱스로 분할(URL 5만/파일, 50MB 한도).
- [ ] **내부 링크 도달성**: 고아 페이지(orphan) 없음 — 클릭 깊이 얕게. 크롤 예산은 대형/저품질 대량 사이트에서만 실질 이슈.
- [ ] **크롤 통계**: Search Console 크롤 통계로 5xx·과도한 크롤·응답 지연 점검.

## 2. 인덱스 (index) — 도달한 페이지가 색인되는가
- [ ] **인덱싱 제어 구분**(가장 흔한 실수): `robots.txt Disallow`(크롤 차단, 이미 알려진 URL은 색인될 수도) ≠ `<meta robots noindex>`(색인 제외 — 단 이게 먹히려면 크롤은 허용돼야 함). noindex + Disallow 동시 지정하면 noindex를 못 읽어 역효과.
- [ ] **canonical**: 중복/유사 URL(파라미터·페이지네이션·트래킹) 정규화. 자기참조 canonical 기본. ⚠️ canonical은 **힌트**지 명령 아님(Google이 무시 가능).
- [ ] **Search Console 페이지 색인 리포트**: "발견됨-미색인 / 크롤됨-미색인" 사유별 점검(품질·중복·크롤예산 신호).
- [ ] 상태코드: soft 404 없음, 이동은 301, 삭제는 410/404 일관.

## 3. Core Web Vitals (2026-07 현행) — 페이지 경험
> ⚠️ CWV는 **약한 신호·타이브레이커**. 콘텐츠 관련성이 우선. "CWV만 고치면 순위 급등"은 과장.
- [ ] **LCP** (Largest Contentful Paint, 로딩): **≤ 2.5s good** / 2.5~4s 개선필요 / >4s 나쁨. 주범: 느린 서버·렌더 차단 리소스·큰 이미지.
- [ ] **INP** (Interaction to Next Paint, 응답성): **≤ 200ms good** / 200~500ms 개선필요 / >500ms 나쁨. **2024-03-12부터 FID를 대체(정식 CWV 전환).** FID(첫 입력 지연만)와 달리 INP는 방문 전체 상호작용의 대표 최악값. 주범: 무거운 JS 메인스레드 점유.
- [ ] **CLS** (Cumulative Layout Shift, 시각 안정성): **≤ 0.1 good** / 0.1~0.25 개선필요 / >0.25 나쁨. 주범: 크기 미지정 이미지/광고·후삽입 요소.
- [ ] 측정은 **P75 필드 데이터**(CrUX/Search Console). 랩 데이터(Lighthouse)는 진단용이지 판정 기준 아님.
- 출처: https://web.dev/articles/vitals · https://web.dev/blog/inp-cwv-march-12

## 4. 구조화 데이터 (structured data / schema.org)
- [ ] 페이지 유형에 맞는 마크업(Article, Product, FAQ, HowTo, Breadcrumb, Organization 등) — JSON-LD 권장.
- [ ] **리치 결과 ≠ 랭킹 부스트**: 구조화 데이터는 리치 결과(별점·FAQ 아코디언 등) *자격*을 줄 뿐, 그 자체가 순위를 올린다는 공식 근거는 없다(벤더 주장 주의).
- [ ] 콘텐츠와 일치(가시 콘텐츠에 없는 정보 마크업 금지 = 스팸 정책 위반). Rich Results Test로 검증.
- ⚠️ Google이 특정 리치 결과 자격을 수시 축소(예: 과거 FAQ/HowTo 리치 결과 표시 대폭 제한) — 시점별 확인 필요.

## 5. 국제화 (international / hreflang)
- [ ] **hreflang**: 언어·지역별 대체 페이지 상호 지정(양방향 필수 — 한쪽만 걸면 무효). `x-default` 지정.
- [ ] hreflang은 순위 신호가 아니라 **올바른 버전을 올바른 사용자에게** 매칭하는 신호.
- [ ] 지역 타깃팅: Search Console 국제 타깃팅 또는 ccTLD/서브디렉터리 전략.
- [ ] 중복 언어 콘텐츠는 canonical과 hreflang을 혼동하지 말 것(hreflang 세트 내부에서는 각 페이지가 자기참조 canonical).

## 6. 모바일·기타 기본기
- [ ] **모바일 우선 색인**(mobile-first indexing, 전면 적용): 모바일 버전이 색인 대상 — 모바일에 콘텐츠·구조화 데이터 누락 없게.
- [ ] HTTPS 전면. 혼합 콘텐츠 없음.
- [ ] 페이지네이션·무한스크롤: 콘텐츠가 크롤 가능한 링크로 도달되게.

## 진단 → 위임 흐름
전략가(이 스킬)는 위 항목으로 **결손을 식별**하고 우선순위를 매긴다 → 실제 수정(schema 삽입, CWV 최적화, robots/hreflang 배포)은 **(→ dev-seo-analytics)** 에 명세와 함께 넘긴다. 이 스킬은 "왜 이게 중요하고 무엇을 고쳐야 하나"까지, 구현은 dev.
