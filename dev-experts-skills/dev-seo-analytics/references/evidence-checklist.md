# evidence + 출고 전 체크리스트

## 실증·출처

- **Google Search Central, "Core Web Vitals" / web.dev/vitals** — 임계값 LCP < 2.5s · INP < 200ms · CLS < 0.1, 모두 **75퍼센타일·28일 롤링 CrUX 필드값**(랩 아님)에서 동시 충족해야 통과. 정량 기준 표의 1차 출처. (일부 LCP 2.0s 강화설은 2026-06 현재 공식 미확인 — "확인 필요" 유지.)
- **INP가 FID 대체** (Google, **2024-03-12**부터 공식 응답성 지표) — INP는 페이지 방문 전체 상호작용 중 최악을 보고(FID는 첫 입력 지연만). 2026 기준 가장 통과하기 어려운 지표(약 43%가 200ms 실패). 버전 라벨·정량 기준 표 근거. FID는 폐기됨 — 옛 문서/코드에 FID 잔재 있으면 갱신.
- **Universal Analytics(UA) 종료** (2023-07-01 표준·2024-07 360 종료) → **GA4가 유일 현행 버전**. 버전 라벨 근거. UA 기준 이벤트/속성 설계는 전부 폐기.
- **Google Search Central, "JavaScript SEO basics" / 렌더링 문서** — 크롤러의 JS 렌더링은 렌더링 큐 지연·실패 변수. 안티패턴 1(CSR 단독+검색 기대), 0번 관문(`curl` HTML에 본문 존재)의 근거. Search Console URL 검사의 "렌더링된 HTML"이 1차 진실.
- **Google "Helpful Content / Spam Updates"** (2022~, 이후 코어 업데이트에 통합) — AI 양산·어필리에이트 저품질 사이트 트래픽 최대 90% 증발 사례가 장르화. 안티패턴 6(구식 꼼수)·E-E-A-T 정렬·실전 케이스 절의 정기 실증.
- **사이트 이전 트래픽 폭락 장르** (이커머스 리뉴얼·블로그 이주에서 반복) — 301 매핑 없는 URL/도메인 이전 후 수십% 폭락, 회복 수개월. 안티패턴 3(리다이렉트 누락)의 실증. 검색 순위가 URL 단위 자산임을 보여줌.
- **schema.org / Google 구조화 데이터 가이드 + 리치 결과 테스트** — JSON-LD 유형(Article·Product·LocalBusiness·TouristTrip 등)·검증 도구. 안티패턴 2(메타·구조화 데이터 공백)의 근거.

## 출고 전 체크리스트 (SEO·측정 작업 출고 시)

- [ ] 0번 관문: 검색 유입 페이지의 초기 HTML(`curl`)에 핵심 콘텐츠 존재 (CSR 단독이면 SSR/SSG/프리렌더)
- [ ] robots.txt·sitemap.xml 접근 가능하고 의도대로 (크롤 차단·누락 없음)
- [ ] 페이지 정체성 4종: 고유 title(~60자)·description(~155자)·OG/트위터 카드·해당 유형 JSON-LD (템플릿 변수로 시스템화)
- [ ] 리치 결과 테스트(구글 공식 도구) 통과
- [ ] 전 페이지 self-canonical + 변형(파라미터·정렬)은 대표 URL로 canonical, 도메인 정규화(한 형태로 301)
- [ ] URL/도메인 이전이면 구 URL 100% → 신 URL 301 매핑표 + 이전 후 Search Console 커버리지·404 모니터링
- [ ] Core Web Vitals 75퍼센타일 통과(LCP<2.5s·INP<200ms·CLS<0.1), 미달 시 → dev-performance. FID 잔재 코드 없음
- [ ] 추적 이벤트는 질문 3~5개에서 역산, GA4 권장 이벤트명(`sign_up`·`view_item`) 우선, 명명 규칙 문서화
- [ ] Search Console + GA4 연결 완료 (측정 기반 없이 SEO 단정 금지), 개인정보 동의는 dev-privacy-compliance와 협업
- [ ] 꼼수(키워드 채우기·숨김 텍스트·구매 백링크·AI 양산) 없음, 기술 SEO는 "방해 제거"까지

## 점검 주기 (부패 빠름 — 분기)

- 코어 알고리즘 업데이트 발표 추적(분기) → 안티패턴 6·실전 케이스의 사례 갱신. 단일 시점 등락은 추세로 판단(패닉 금지).
- Core Web Vitals 임계·구성 변화 추적(분기) — 특히 LCP 2.0s 강화설이 공식화되는지(현재 "확인 필요"). INP가 FID 대체한 사실은 확정.
- GA4 권장 이벤트·Search Console 리포트 UI/지표 변화(분기). 국내 네이버 서치어드바이저 등록 절차는 별도 확인.
- title/description 잘림 픽셀 기준은 변동 → 글자 수는 출발점일 뿐("확인 필요" 유지).
