# biz-seo-marketing — 프레임 & 출처 (검증판)

> SKILL.md 보강. 부패 빠름 — 공식 가이드 우선. 출처 2026-07-01 웹 검증(핵심 사실 재확인). 1단계 참조.
> 실무 심화는 별도 파일: `technical-seo-checklist.md`, `search-intent-and-content.md`.

---

## 1. Search Essentials (공식)

2022-10 Webmaster Guidelines에서 개명. 기술 요건+스팸 정책+베스트프랙티스.
https://developers.google.com/search/docs/essentials

---

## 2. E-E-A-T (지위 정확 — 중요 교정)

⚠️ **E-E-A-T는 랭킹 팩터/점수가 아니다** — 품질 평가자(rater) 평가 프레임. "EEAT 점수"라는 건 없음. 평가자 평점은 랭킹을 직접 안 움직임(알고리즘 변경을 평가). John Mueller도 "QRG는 통찰은 되지만 랭킹 가이드가 아니다"라고 공식 확인. YMYL은 주제 범주이지 페널티 아님. Experience 추가(E-A-T→E-E-A-T) 2022-12.
- https://developers.google.com/search/blog/2022/12/google-raters-guidelines-e-e-a-t
- 평가자 가이드 PDF: https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf

**실무 함의(랭킹 팩터 주장 아님, rater 관점 최적화)**: E-E-A-T는 "직접 켜는 스위치"가 아니라 *알고리즘이 흉내 내려는 목표*다. 실무는 "E-E-A-T 점수를 올린다"가 아니라 **평가자가 신뢰를 판단하는 근거를 콘텐츠에 실재시키는 것**이다 — 실제 저자·실제 경험·1차 출처·근거. 이 신뢰 신호가 *직접* 순위를 올린다고 약속하는 벤더 주장은 인용 금지. 상세는 `search-intent-and-content.md` §3.

**E-E-A-T 구성 요소**:
- **Experience(경험)**: 저자의 직접 경험 증거 — 1차 경험담, 실제 사용·방문 근거 (2022-12 추가)
- **Expertise(전문성)**: 해당 주제의 전문 지식·자격·이력
- **Authoritativeness(권위)**: 타인·업계가 이 저자/사이트를 권위로 인정하는 증거 (인용·링크·언급)
- **Trustworthiness(신뢰)**: 정확성·투명성·보안·정직성 — E-E-A-T의 핵심(Google)

---

## 3. Helpful Content / 스팸

- Helpful Content(2022-08) → **2024-03 코어 랭킹에 통합, 별도 분류기 폐지** (연속 작동, 토글/페널티 아님).
  https://developers.google.com/search/blog/2024/03/core-update-spam-policies
- **2024-03 스팸 3종 추가**: scaled content abuse, site reputation abuse(parasite SEO), expired domain abuse.
  - site reputation abuse 정책 업데이트(강화): 2024-11-19 효력 발생.
    https://developers.google.com/search/blog/2024/11/site-reputation-abuse
- ⚠️ **AI 콘텐츠 자체는 금지 아님** — 조작적/대량/무가치가 문제("어떻게 만들었든"). Google: "reward high-quality content, however it is produced."

---

## 4. 검색 의도 (3종 — 교정)

**Broder(2002), "A Taxonomy of Web Search," ACM SIGIR Forum 36(2):3–10** — navigational/informational/transactional **3종**.
https://sigir.org/files/forum/F2002/broder.pdf

⚠️ "commercial investigation"(상업 조사) 4번째는 **SEO 업계 추가**(Broder·Google 공식 아님). 실무에서 4구분으로 쓸 때는 매번 "업계 분류, 공식 아님"을 명시해야 한다.

**실무(업계 하위분류 매핑, 공식 아님을 명시하고 사용)**:
실무자는 4구분(정보형 / 상업조사형 / 거래형 / 내비형)으로 콘텐츠 포맷을 결정한다. 판별은 이론이 아니라 **SERP 관찰**로 한다 — "지금 그 키워드에 뭐가 랭크돼 있나"가 Google이 판단한 의도의 실증. 상세·매핑표는 `search-intent-and-content.md` §1~2.

---

## 5. 토픽 권위 / 토픽 클러스터 (지위 + 실무 원전)

⚠️ **"토픽 권위 점수"는 공식 Google 문서 없음·랭킹 팩터 아님.** John Mueller "신경 쓰지 마라"(2023). DA(Moz)/DR(Ahrefs)는 **벤더 지표**(Google 신호 아님, Google엔 사이트 권위 점수 없음).

**실무 원전 — Pillar-Cluster 모델(HubSpot)**: HubSpot이 2017년 정식화. 뿌리는 사내 실험 Anum Hussain & Cambria Davies의 "Topics Over Keywords"(~2015): 관련 페이지 간 **내부 링크를 늘릴수록 SERP 순위·노출이 올랐다**는 관찰. 구조 = 넓은 주제를 다루는 **필러 페이지(pillar)** 1 + 세부 키워드를 각각 다루는 **클러스터 콘텐츠(서브)** 다수, 서브가 모두 필러로 (그리고 서로) 내부 링크.
- https://blog.hubspot.com/marketing/topic-clusters-seo
- https://blog.hubspot.com/marketing/pillar-cluster-model-transform-blog

⚠️ 이건 벤더(HubSpot)의 콘텐츠 조직화 방법론이자 자사 실험 결과다 — "Google 공식 랭킹 방식"이 아니다. 효과의 메커니즘은 검증된 부분(내부 링크·주제 응집으로 크롤/이해 도움)과 벤더 마케팅이 섞여 있음. 실무 표준으로 널리 쓰이나 "이대로 하면 오른다"는 보장 아님. 상세는 `search-intent-and-content.md` §4.

---

## 6. 기술 SEO — Core Web Vitals (현행 지표)

**검증 날짜: 2026-07-01 / 출처: web.dev/articles/vitals (2024~)**

- **INP(Interaction to Next Paint)가 FID를 대체 — 2024-03-12 정식 Core Web Vital 전환.**
  FID는 이날 Search Console에서 즉시 제거. 기타 도구(PageSpeed Insights, CrUX 등)는 6개월 폐기 기간.
  - https://web.dev/blog/inp-cwv-march-12
  - 예고: https://developers.google.com/search/blog/2023/05/introducing-inp

- **현행 3지표 임계값(P75 필드 데이터)**:

  | 지표 | Good | Needs Improvement | Poor | 측정 대상 |
  |---|---|---|---|---|
  | LCP | ≤ 2.5s | 2.5s~4.0s | > 4.0s | 가장 큰 콘텐츠 요소의 로딩 시간 |
  | INP | ≤ 200ms | 200ms~500ms | > 500ms | 방문 전체 상호작용 중 대표 최악값 |
  | CLS | ≤ 0.1 | 0.1~0.25 | > 0.25 | 레이아웃 이동 누적 점수 |

  출처: https://web.dev/articles/vitals

- **FID vs INP 차이**: FID는 *첫 상호작용의 입력 지연만* 측정 → INP는 *방문 전체의 모든 상호작용을 관찰해 대표 최악값* 보고(입력→다음 프레임 렌더까지 전체). INP가 실제 사용자 경험을 더 포괄적으로 반영.

- ⚠️ CWV는 페이지 경험 신호의 일부일 뿐 강한 랭킹 팩터 아님 — Google "동점 상황의 타이브레이커"에 가깝게 표현. 콘텐츠 관련성이 우선. 상세 체크리스트는 `technical-seo-checklist.md`.

---

## 7. 기술 SEO — 크롤링·인덱싱·구조화데이터 (공식 확인)

**검증: 2026-07-01 / 출처: developers.google.com/search**

### 크롤링 제어
- **robots.txt**: 크롤러 접근 제어 (서버 과부하 방지 주목적). 숨기기 목적엔 noindex 사용 — robots.txt는 인덱싱 보장 안 함.
  https://developers.google.com/search/docs/crawling-indexing/robots/intro
- **robots meta tag / X-Robots-Tag**: `noindex`(색인 제외), `nofollow`(링크 추종 금지), `nosnippet` 등. HTML 또는 HTTP 헤더로 구현.
  https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag

### 인덱싱 신호
- **Sitemap**: 어떤 페이지가 중요한지 Google에 알리는 신호. 비텍스트 콘텐츠(이미지·동영상)에 특히 중요. URL은 절대경로·canonical URL 사용.
  https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- **Canonical(rel="canonical")**: 중복 URL 통합. rel="canonical" 링크 요소가 권장. 강도: 리다이렉트 > rel=canonical > sitemap 포함.
  https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls

### 국제화
- **hreflang**: 다국어·다지역 사이트의 언어/지역 타겟팅 신호. hreflang 사용 시 같은 언어의 canonical 페이지도 함께 명시해야 함.
  https://developers.google.com/search/docs/specialty/international/localization

### 모바일 퍼스트 인덱싱
- Google은 **모바일 버전 콘텐츠를 기준으로 인덱싱·랭킹**. 모바일/데스크탑 콘텐츠 동일 유지 필수(메타태그, 구조화 데이터, 헤딩, 본문 일치).
  https://developers.google.com/search/docs/crawling-indexing/mobile/mobile-sites-mobile-first-indexing

### 구조화 데이터 / 리치 결과
- **schema.org 어휘 + JSON-LD 포맷**(Google 권장) 또는 Microdata/RDFa. 구조화 데이터 → 리치 결과(Rich Results) 자격. 필수 속성 누락 시 리치 결과 미적용.
- 지원 타입 갤러리: https://developers.google.com/search/docs/appearance/structured-data/search-gallery
- 일반 가이드라인: https://developers.google.com/search/docs/appearance/structured-data/sd-policies
- ⚠️ 구조화 데이터가 리치 결과를 *보장*하지는 않음 — Google 재량.

---

## 8. 링크 정책 (공식 스팸 정책)

**출처: https://developers.google.com/search/docs/essentials/spam-policies**

- **화이트햇 링크**: 콘텐츠 품질로 자연 획득하거나, 게스트 포스트·디지털 PR로 얻는 편집 링크.
- **링크 스팸(금지)**: 랭킹 조작 목적으로 링크를 사고파는 행위, 과도한 링크 교환, 자동화 프로그램으로 링크 생성 등.
  - 유료 링크·PBN(사설 블로그 네트워크) → 수동 조치(Manual Action) 또는 알고리즘 감지 → 순위 하락·제거.
  - **UGC/후원/비편집 링크**에는 `rel="nofollow"`, `rel="ugc"`, `rel="sponsored"` 속성으로 명시.
  - 이미 받은 비자연 링크는 **Disavow 도구**(Search Console)로 거부 가능.
- **링크 품질 > 링크 양**: 관련성·신뢰성 높은 사이트의 링크 1개 > 스팸성 사이트 링크 100개.
- ⚠️ 링크 매매는 지속적으로 탐지·제재 — Google 2021~2022 링크 스팸 업데이트로 AI 감지 강화.

---

## 9. AI Overviews / 생성형 검색

GA 출시 2024-05-14 (SGE 실험의 제품화 후계). 별도 랭킹 시스템/마크업 없음 — 헬프풀 콘텐츠 지침 적용.
https://blog.google/products-and-platforms/products/search/generative-ai-google-search-may-2024/

**콘텐츠 시사점(부패 빠름·상당수 확인 필요)**:
생성형 검색은 답을 요약해 무클릭(zero-click)을 늘린다 → 순위≠트래픽. 실무 대응 방향:
① 발췌·인용되기 쉬운 **명확한 직답 구조** (질문-답, 요약 문단, 리스트/표)
② 요약으로 대체 안 되는 **깊이·1차 경험·독자 데이터** (피인용 후 클릭 유인)
③ 브랜드·저자 실체 (인용 시 신뢰)
⚠️ "GEO/AEO 최적화로 AI 인용 보장" 류 벤더 주장은 검증 미비 — 확인 필요, 날조 금지.

---

## 10. 출처 요약

| 출처 | 지위 | URL |
|---|---|---|
| Google Search Essentials | 공식 | developers.google.com/search/docs/essentials |
| Google QRG (Search Quality Rater Guidelines) | 공식 | guidelines.raterhub.com |
| Google Helpful Content / Spam Policies | 공식 | developers.google.com/search/blog/2024/03/core-update-spam-policies |
| Google AI Overviews 발표 | 공식 | blog.google/... |
| web.dev Core Web Vitals | 공식 | web.dev/articles/vitals |
| INP CWV 전환 공지 | 공식 | web.dev/blog/inp-cwv-march-12 |
| Google Structured Data | 공식 | developers.google.com/search/docs/appearance/structured-data |
| Google Spam Policies | 공식 | developers.google.com/search/docs/essentials/spam-policies |
| Broder(2002) "A Taxonomy of Web Search" | 학술 (ACM SIGIR Forum 36(2)) | sigir.org/files/forum/F2002/broder.pdf |
| HubSpot Pillar-Cluster | 벤더 방법론 (명시) | blog.hubspot.com/marketing/topic-clusters-seo |
| DA(Moz)/DR(Ahrefs) | 벤더 지표 (Google 신호 아님) | — |
