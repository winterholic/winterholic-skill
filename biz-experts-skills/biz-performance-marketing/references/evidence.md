# biz-performance-marketing — 프레임 & 출처 (검증판 심화)

> SKILL.md 보강. 부패 빠름 — 플랫폼 공식 우선. 출처 2026-07-01 웹 검증. 1단계 참조.
> 실무 심화: **[unit-economics.md](unit-economics.md)** (CAC/LTV/페이백/컨트리뷰션마진 완전판) · **[incrementality-and-measurement.md](incrementality-and-measurement.md)** (iROAS/MER/ATT측정스택) · **[channel-playbook.md](channel-playbook.md)** (채널별 구조·입찰·소재·벤치마크).

---

## 1. 플랫폼 (공식)

- **Meta Advantage+** (2022-08, CBO 리브랜드+ML 예산): https://about.fb.com/news/2022/08/introducing-new-automation-tools-to-increase-sales-and-drive-growth/ (소재 최대 150조합). ⚠️ "set and forget" 아님 — Pixel/CAPI·전환량·소재 품질 필수. "20소재/$10K/50전환" 임계는 에이전시 통설(공식 아님).
  - **2024~2025 성과 데이터**: Advantage+ Shopping 캠페인(ASC) 수동 대비 **ROAS 15~25% 개선**, CPA ~32% 낮음(AdAmigo 2026 벤치마크; Black Friday 2024 사례: ASC 3.14 vs 수동 2.70). ⚠️ 소재·Pixel 신호 품질 전제, 산업별 편차 큼(확인 필요).
  - ASC 연간 광고비 run-rate $200억+ 달성(2024 말 기준 YoY 70% 성장, Meta 공개 수치).

- **Google 광범위 매칭 + Smart Bidding**: https://support.google.com/google-ads/answer/10195720 (2020 데이터 tCPA +~25% 전환). 광범위 매칭은 **Smart Bidding + 깨끗한 전환 데이터와 함께**라야 효과(단독 사용 금물).

- **Google Performance Max**: https://support.google.com/google-ads/answer/10724817 . 전 인벤토리 자동 배분·블랙박스·리포팅 투명성 낮음 → 증분성 검증 권장.

---

## 2. 단위경제 (David Skok) — 상세는 unit-economics.md

LTV:CAC >3(때로 7~8), CAC 회수 5~7개월 최선·12개월 넘으면 빈약. **GM(총마진) 조정 LTV** 사용. https://www.forentrepreneurs.com/saas-metrics-2/

⚠️ **실제 중앙값 회수기간은 통설 상회**: Benchmarkit 2025 리포트 기준 2024년 SaaS 데이터 중앙값 **~18개월**(2023년 ~14개월에서 상승). 2025년은 ~16개월으로 개선(G2M 합리화 영향). 계약규모별 분화: SMB 셀프서브 ~9~11개월 / 미드마켓 14~18개월 / 엔터프라이즈 18~24개월+ (세그먼트 수치 확인 필요). 3:1은 바닥 휴리스틱(>5:1은 과소투자일 수도). https://www.benchmarkit.ai/2025benchmarks

**핵심 실무 포인트(unit-economics.md 요약):**
- **CAC = 전체 획득비용(광고비+인건비+툴+에이전시 수수료) ÷ 신규 고객 수.** 광고비만 넣은 "광고 CAC"는 실제보다 낮게 나옴(fully-loaded CAC와 구분).
- **Blended CAC**(총비용÷전체 신규, 오가닉 포함) vs **Paid CAC**(유료비용÷유료로 획득한 신규). 오가닉 비중 크면 Blended가 실제 유료 효율을 숨긴다 — 확장 판단은 **Paid(marginal) CAC**로. 실측 갭 통상 20~40%.
- **LTV 3계산법**: ① 단순 `ARPU×평균 수명(=1/이탈률)` ② **GM 조정** `ARPU×GM%÷이탈률`(Skok 권장, 마진 반영) ③ **할인 코호트/DCF**(미래 현금흐름 할인, 가장 정확). 함정: 초기 코호트 수명을 낙관 외삽하면 LTV 과대 → CAC 회수 착시.
- **페이백** = CAC ÷ (월 ARPU × GM%). 현금흐름 관점 — 회수 전까지는 고객 늘수록 현금 마름.
- **컨트리뷰션 마진** = 매출 − 변동비(원가+채널 광고비+변동 인건비). DTC·이커머스는 GM만으로는 채널 비용이 숨어 있어 CM까지 봐야 실상 파악.

---

## 3. MER / aMER / blended ROAS (실무 정의)

- **ROAS**(채널) = 채널 기여매출 ÷ 채널 광고비. **채널 ROAS 합산은 중복 계상**(겹치는 기여 윈도우 — 한 매출을 Meta·Google이 둘 다 클레임).
- **MER**(Media Efficiency Ratio) = **총매출 ÷ 총광고비**(기여 무관·전사). 플랫폼 픽셀 붕괴(ATT) 이후 이커머스 북극성으로 부상. ⚠️ Triple Whale은 spend÷revenue(역수, %)로 표기 — 대시보드 관례 확인.
- **aMER**(acquisition MER) = **총매출 ÷ 신규고객 획득 광고비**(리타게팅·브랜드 제외한 신규수요 광고비만 분모). 신규 획득 효율을 MER보다 정확히 봄.
- **blended ROAS** ≈ MER과 사실상 동의어로 쓰이나, 맥락 따라 "전 채널 합산 ROAS"를 뜻하기도 — 정의를 팀 내 합의할 것.

**2025 DTC 벤치마크 (Triple Whale)**: 고객 중앙값 MER **2.4x** — 절반이 비용 차감 후 손익분기 이하. 성숙 DTC 브랜드 3x~5x, 구독 브랜드 6x+ 가능(확인 필요). https://www.triplewhale.com/blog/marketing-efficiency-ratio

**MER 목표 역산 공식**: 목표 MER = 1 ÷ 허용 광고비율(예: 광고비 20% 한도 → 목표 MER 5.0x).

---

## 4. 증분성 (iROAS) — 왜 플랫폼 ROAS가 부풀려지나

**iROAS = 증분매출(처리−대조) ÷ 광고비.** Google Conversion Lift(공식: "광고의 인과 영향 측정") https://support.google.com/google-ads/answer/12003020 · Meta Conversion Lift(RCT, 2014~). 지오 홀드아웃·ghost ads. **플랫폼 ROAS=상관/기여, iROAS=인과.**

**플랫폼 리포트 ROAS가 부풀려지는 3대 이유:**
1. **어차피 살 사람에게 크레딧**(브랜드검색·리타게팅) — 광고 없어도 전환됐을 사람. 증분 ≪ 기여.
2. **클릭/뷰스루 과다 클레임** — Meta 1일 뷰/7일 클릭 기본, 여러 플랫폼이 같은 전환을 각자 클레임.
3. **모델링/추정 전환** — ATT 이후 모델링 전환 비중↑, 실측 아님.

**플랫폼 ROAS vs iROAS 갭**: 30~70% 낮게 나오는 경우 흔함(Measured.com 실무 가이드 기준, 확인 필요). 특히 브랜드검색·리타게팅이 포트폴리오에서 큰 비중을 차지할수록 갭 큼.

**채널별 iROAS 벤치마크 (Stella 2025, N=225 지오 테스트, 이커머스/DTC):**
- 전체 중앙값: 2.31x (IQR 1.36x~3.24x)
- Google PMax: 2.98x / Meta: 2.92x / Google 비브랜드 검색: 1.46x / TikTok: 0.94x / **Google 브랜드 검색: 0.70x**
- ⚠️ 이커머스/DTC 편향, 자기 산업·계정으로 재조정. 출처: https://www.stellaheystella.com/blog/2025-dtc-digital-advertising-incrementality-benchmarks

**증분성 실전 설계:**
- **지오 리프트(geo holdout)**: 유사한 지역군을 처리/대조로 나눠 한쪽만 광고 → 매출 차이가 증분. 유저 추적 불필요·프라이버시 안전(ATT 시대 표준). 검정력 위해 충분한 지역 수·기간 필요. 사전 기간 MAPE ≤0.15·R² 0.85~0.94이면 100% 유의도 달성(Stella 2025).
- **유저 홀드아웃(ghost ads)**: 노출됐을 광고를 실제 미노출하되 식별 → 완벽 대조군(PSA 플라시보보다 우월). Google/Meta Conversion Lift가 내부적으로 이 방식.
- **결과 해석**: iROAS 1.0 미만이면 그 지출은 순손실(광고 없이도 왔을 매출). 브랜드검색이 iROAS 낮게 나오는 건 정상(방어 목적은 별도 판단).

---

## 5. 입찰 전략 선택 로직 (Smart Bidding)

- **Maximize Conversions**(전환 최대화): 예산 소진하며 전환 수 극대. 타깃 없음 — 초기·데이터 부족·전환수 자체가 목표일 때. 예산이 실질 상한.
- **tCPA**(목표 전환당 비용): 전환당 비용을 목표에 맞춤. 전환 볼륨·안정 신호 쌓인 뒤. 목표를 너무 낮게 잡으면 전환량 급감.
- **Maximize Conversion Value / tROAS**(목표 광고비수익률): 전환 "값"이 다를 때(이커머스 객단가 차이). tROAS는 값/비용 비율 목표 — **가치 데이터가 정확해야**(장바구니 값·마진 반영). 목표 과high면 노출 위축.
- **선택 순서(실무)**: 데이터 없음 → Max Conversions로 데이터 축적 → 전환 안정(tCPA: 캠페인당 주 ~30전환, tROAS: 주 ~50전환 + 가치 데이터 정확) → tCPA/tROAS 전환.
  - ⚠️ "30/50전환" 임계는 Google 공식 문서 기반 업계 통설이며, Google이 일부 문서에서 명시. 공식 확정 절대치로 사용 금지(캠페인 유형별 편차, "확인 필요").
- **학습 리셋 주의**: tCPA/tROAS 목표값 변경, 예산 ~30%+ 변경, 주요 소재·타깃 변경 시 학습 재시작. 변경 후 최소 1~2주 안정화 기간 부여.

---

## 6. 계정 구조·소재 테스트 원칙 (현대 통합형)

- **구조 단순화 추세**: 잘게 쪼갠 애드셋/캠페인은 전환 신호를 분산 → 학습 지연. 현대 플랫폼은 **소수의 넓은 캠페인 + 다양한 소재**를 선호(Meta Advantage+ / Google PMax의 설계 철학).
- **학습 보존**: ML 입찰은 전환 신호로 학습. 잦은 예산·타깃·소재 변경은 학습 리셋. 변경은 점진적(예산 ±20~30% 단위 통설).
- **소재가 1번 레버**: 타깃팅을 알고리즘이 대신하는 시대 → 크리에이티브가 최대 변수. **콘셉트 단위**로 다수 동시 테스트(훅·앵글·포맷 변주), 통계적으로 판단(소량 노출 조기판단 금물).

---

## 7. iOS 14.5 ATT (2021-04)

Apple 공식 https://developer.apple.com/app-store/user-privacy-and-data-use/ . Flurry 옵트인(2021 출시 직후 기준) **US ~4% / 전세계 ~11%**(확정, Flurry 공식 트래커) https://www.flurry.com/blog/ios-14-5-opt-in-rate-att-restricted-app-tracking-transparency-worldwide-us-daily-latest-update/ — 단, '프롬프트를 띄운 앱'으로 분모를 좁히면 ~25%로 올라감(방법론 차이 주의). 이후 수개월간 전체 옵트인 ~15%까지 상승.

"$10B" 3개 별개 주장 혼동 주의: (A) FT/Lotame H2-2021 ~$9.85bn(Snap+FB+Twitter+YT), **(B) Meta CFO Q4'21(2022-02) 자사 ~$10B FY2022 추정** https://www.cnbc.com/2022/02/02/facebook-says-apple-ios-privacy-change-will-cost-10-billion-this-year.html , (C) Lotame ~$16bn.

ATT는 크로스앱 추적 한정(전체 분석 아님). SKAdNetwork가 대체.

---

## 8. SKAdNetwork 4 (SKAN 4) — 앱 측정

Apple 공식: https://developer.apple.com/documentation/storekit/skadnetwork/ · 다중 윈도우 postback: https://developer.apple.com/documentation/storekit/receiving-postbacks-in-multiple-conversion-windows

- **postback 최대 3개**(iOS 16.1+, SKAN 4): PB1(0~2일·fine 가능) / PB2(3~7일·coarse만) / PB3(8~35일·coarse만) → 설치 후 최대 35일 커버.
- **conversion value 2종**: fine(6비트, 0~63) — PB1만 / coarse(none·low·medium·high) — PB2·3.
- **lockWindow**: 전환값 조기 확정, postback 빨리 받는 옵션.
- **coarse 전환·랜덤 지연·crowd anonymity**로 리포팅 지연·저해상 → MMM·지오리프트 상보 측정 필요.
- **conversion value schema 설계가 핵심 레버**: 기본값 방치 vs 의도적 설계 팀 간 성과 격차 큼(Singular·Segwise 2025, 확인 필요).

세부 실무: → incrementality-and-measurement.md §6

---

## 9. 크리에이티브 (소재) — 성과 주동인이 된 이유

플랫폼 알고리즘이 타깃팅을 대신하는 시대 → 크리에이티브가 남은 최대 변수. 실무적으로:
- **훅(첫 3초)**: 스크롤 멈춤 여부 결정. 아무리 좋은 소재도 훅이 약하면 스킵.
- **콘셉트 단위 테스트**: UGC·데모·증언·비교·문제해결 등 **앵글** 자체를 여러 개. 헤드라인/컬러/형식 변주는 그 다음.
- **소재 피로(fatigue)**: 같은 소재를 오래 돌리면 CPM↑·CTR↓. TikTok은 특히 빠름.
- **학습에 필요한 소재 다양성**: Meta Advantage+는 다수 소재를 학습에 활용 → 소재가 많을수록 알고리즘이 더 잘 최적화.

---

## 10. 출처

- Meta/Google/Apple 공식.
- David Skok, forEntrepreneurs (SaaS Metrics 2.0).
- Google/Meta Conversion Lift 공식.
- Apple ATT·SKAN 4 공식.
- Stella 2025 DTC Incrementality Benchmarks (N=225, 2024-08~2025-12): https://www.stellaheystella.com/blog/2025-dtc-digital-advertising-incrementality-benchmarks
- Benchmarkit 2025 SaaS Benchmarks (2024년 데이터): https://www.benchmarkit.ai/2025benchmarks
- Triple Whale 2025 MER guide: https://www.triplewhale.com/blog/marketing-efficiency-ratio
- Measured.com, Platform ROAS to iROAS: https://www.measured.com/faq/leveling-up-media-measurement-the-performance-marketers-journey-from-platform-roas-to-true-incrementality
- Singular SKAN 4 guide: https://www.singular.net/blog/skan-4-strategy/
