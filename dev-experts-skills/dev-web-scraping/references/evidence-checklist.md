# evidence + 출고 전 체크리스트

(법률·운영 실증 사례는 `evidence.md`, 여기서는 출처 색인 + 출고 체크리스트 + 점검 주기)

## 실증·출처

- **hiQ v. LinkedIn 판결·보도** (9th Cir., 2017~2022) — 공개 데이터 CFAA 비해당 vs 계약(약관) 책임의 분리. SKILL.md 실전 케이스·`evidence.md` 1번의 1차 근거.
- **Meta v. Bright Data** (N.D. Cal., 2024, Judge Edward Chen) — 로그아웃(공개) 상태 수집에 대한 계약 청구 기각, "로그인 여부"를 2026 핵심 분기선으로 확립. SKILL.md 후속 케이스.
- **Cloudflare — AI 크롤러 기본 차단 + Pay-Per-Crawl** (cloudflare.com 보도/블로그, 2025-07) — 신규 도메인 AI 봇 기본 차단, `402 Payment Required` 기반 크롤 마켓. 안티패턴 3 "2026 현실"의 근거. 봇 트래픽이 사람을 초과(Cloudflare Radar, 2026-06).
- **GDPR 집행 사례** (Clearview AI 등 다국적 과징금) — 공개 사진/데이터라도 적법 근거 없으면 위법. 개인정보 축의 근거. **확인 필요**: 관할·용도별 최신 판례·과징금은 법무 검토.
- **Playwright Python 1.60** (playwright.dev/python/docs/release-notes, 2026-05) — Chrome for Testing 번들, 버전 라벨의 근거. (참고: 구버전의 `_vue`/`_react` 실험적 셀렉터는 제거됨 — 동적 렌더 의존 회피 원칙은 불변.)
- **httpx · BeautifulSoup4 4.13** (pypi.org) — 정적 수집 표준 조합의 버전 라벨 근거.
- **robots.txt / RFC 9309** — 예절 수집(경로·crawl-delay 존중)의 표준 근거(워크플로우 2단계).

## 출고 전 체크리스트 (수집 작업 출고 시)

- [ ] robots.txt + 약관 + 봇 정책(Cf-/AI 크롤러 차단 여부) 사전 점검
- [ ] 용도·대상 3축 분류: 로그인/약관 동의 여부 · 개인정보 포함 여부 · 보호조치 우회 여부
- [ ] 요청 간 지터 있는 지연(저빈도) + 연락처 포함 명시 User-Agent
- [ ] 정적 우선(httpx+bs4), 동적 렌더(Playwright)는 필요 증명 후에만
- [ ] 셀렉터가 난독화 클래스가 아니라 안정 구조/속성 기반
- [ ] 필수 필드 스키마 검증 — None/빈 값은 적재 아니라 **실패**로 집계
- [ ] 실패율 임계 알림 + 일 단위 건수·통계 새니티(침묵 파서 오염 방어)
- [ ] 403/429 시 즉시 중단·백오프 (우회 고도화 금지)
- [ ] 공식 API/데이터 제휴/Pay-Per-Crawl을 우회보다 먼저 검토했다
- [ ] 사업 의존 수집이면 법무 검토 트리거를 기록했다

## 점검 주기 (부패 중간 — 반기, 단 차단 생태계는 더 빠름)

- 도구 버전: Playwright(현재 1.60)·httpx·beautifulsoup4(4.13) 반기 확인 → 버전 라벨 갱신.
- **차단 생태계(빠름 — 분기 권장)**: Cloudflare 등의 AI 크롤러 정책·Pay-Per-Crawl 확산, 봇 차단 강화 추세 재확인 — 안티패턴 3 "2026 현실" 갱신.
- 법률 축: 새 판례(CFAA·계약·DMCA §1201)·GDPR/개보법 집행 동향 → SKILL.md·`evidence.md` 케이스 반영. 법률 해석은 참고용, 사업 의존 시 전문 검토.
