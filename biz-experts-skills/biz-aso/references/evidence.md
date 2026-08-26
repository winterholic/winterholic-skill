# biz-aso — 프레임 & 출처 (검증판)

> SKILL.md 보강. 부패 빠름 — 공식 가이드 우선. 출처 2026-06-30~07 웹 검증. 1단계 참조. 실무 심화: `keyword-research.md`(스토어별 키워드 전술)·`store-testing-playbook.md`(PPO/CPP/Google 실험).

## 1. Apple App Store 메타데이터 (공식·검증)
앱명 30자, 부제 30자, **키워드 필드 100자(쉼표·공백 없이)**, 프로모 텍스트 170자(**랭킹 비인덱싱**), 스크린샷 10·프리뷰 3(≤30s). https://developer.apple.com/app-store/product-page/ · 검색 https://developer.apple.com/app-store/search/ ⚠️ 설명·프로모텍스트는 키워드 비인덱싱, 중복 키워드 회피.

## 2. Google Play (공식)
제목 ≤30, 짧은 설명 ≤80, 전체 설명 ≤4000. **키워드 필드 없음**(제목+설명 인덱싱). 제목은 A/B 불가(전체 업데이트 필요). https://support.google.com/googleplay/android-developer/answer/9958766 · https://support.google.com/googleplay/android-developer/answer/13393723

## 3. 두 축 (발견+전환)
키워드 최적화 + 전환율 최적화(CRO). 용어/실무 공동 귀속 Dave Bell(Gummicube), "ASO" ~2012-02 확산. https://en.wikipedia.org/wiki/App_store_optimization

**발견(discovery)** = 스토어 검색·브라우즈·차트·추천에서 노출되는 힘. 레버: 인덱싱된 키워드(관련성·검색량·난이도 균형), 카테고리, 다운로드·참여 속도, 지역화.
**전환(conversion)** = 페이지에 온 사람을 설치로 바꾸는 힘. 레버: 아이콘, 첫 1~3 스크린샷(대부분 그것만 보고 결정), 프리뷰, 평점·리뷰, 짧은 설명(Play는 검색결과에 노출). 두 축은 상호작용 — 낮은 전환은 다운로드 속도를 떨궈 발견(랭킹)까지 깎는다(전환→랭킹 인과는 §4 벤더 컨센서스).

## 4. 전환율→랭킹 (지위 정확)
공식 확인: 평점·리뷰·다운로드·참여가 랭킹에 영향(Apple·Google 문서). ⚠️ "고 CVR→고 랭킹"의 직접 인과는 **벤더/2차 출처만** — Apple/Google이 그 입도로 확정 안 함. 업계 컨센서스로 표기, 벤더를 진실원으로 인용 금지.

**랭킹 인디케이터(벤더 컨센서스 — 진실원 아님)**: 임프레션→PPV(product page view)→CVR(설치 전환)→리텐션(설치 후 유지)의 퍼널이 다운로드 속도·참여를 만들고, 스토어 알고리즘이 이를 랭킹 신호로 반영한다는 것이 ASO 벤더 공통 주장. Apple/Google 공식은 "다운로드·참여·평점이 영향"이라는 수준까지만 확정, 각 지표의 가중치·인과 입도는 미공개(확인 필요). 실무 함의: CVR·리텐션이 낮으면 유료로 노출을 사도 랭킹이 지속 안 됨.

## 5. 스토어 알고리즘 차이 (인덱싱 — 핵심)
- **Apple**: 앱명·부제·**키워드 필드(100자, 비공개)**를 인덱싱. 설명·프로모텍스트는 **키워드 비인덱싱**. → 키워드 필드가 발견의 핵심 무기(공백·중복·복수형 낭비 회피가 곧 문자수 확보).
- **Google Play**: **키워드 필드 없음**. 제목·짧은 설명·**전체 설명(4000자) 전부를 NLP로 인덱싱**. 키워드 우선순위 제목 > 짧은 설명 > 전체 설명. 밀도(density) 개념 존재 — 벤더 권장 주 키워드 ~2~3%, 보조 1~2%(과밀은 스터핑 리스크, 저밀은 관련성 약화). ⚠️ 밀도 수치는 **벤더 권장**(Google 공식 아님, 확인 필요). https://phiture.com/asostack/google-play-store-keywords-how-to-find/ · https://www.apptweak.com/en/aso-blog/play-store-keyword-research
- 함의: **iOS·안드로이드 메타데이터 복붙은 양쪽 다 비최적**(SKILL 안티패턴 3). Apple은 조합·비공개 키워드 게임, Google은 자연어·밀도·가독성 게임.

## 6. Apple 크로스-로컬라이제이션 (지역화 트릭 — 벤더 실무)
Apple은 **로컬 스토어프론트별로 키워드를 인덱싱**한다. 한 스토어프론트가 primary + secondary(추가) 로컬라이제이션을 가질 수 있어(예: US 스토어에 en-US + es-MX), 각 로컬라이제이션의 키워드 필드가 **모두 인덱싱**되어 실효 키워드 공간이 늘어난다. ⚠️ **제약(중요)**: (a) **반복은 가중 안 됨** — 같은 단어가 여러 필드/여러 로컬라이제이션에 있어도 1회만 카운트, (b) **로컬라이제이션 간 단어는 교차 조합 안 됨** — en-US의 "blocks" + es-MX의 "kids"로 "kids blocks" 쿼리에 잡히지 않음(각 로컬라이제이션이 의미적으로 독립이어야). 벤더 컨센서스이며 Apple 공식 문서는 로컬라이제이션 구조만 기술, 크로스-로컬 "트릭"은 명시 안 함(확인 필요). https://developer.apple.com/help/app-store-connect/reference/app-information/app-store-localizations/ · https://www.mobileaction.co/blog/app-store-cross-localization/ · https://www.apptweak.com/en/aso-blog/how-to-benefit-from-cross-localization-on-the-app-store

## 7. Apple Search Ads가 오가닉에 미치는 영향 (halo — 벤더 컨센서스)
ASA 활성 캠페인이 오가닉 설치를 끌어올리는 "halo effect"가 벤더 사이 공통 주장. 메커니즘(벤더): (a) 특정 키워드로 유료 설치가 늘면 그 키워드의 오가닉 랭킹도 개선, (b) 페이지 트래픽 증가가 전반 랭킹에 긍정, (c) 신규 메타데이터가 유료 볼륨 덕에 더 빨리 인덱싱. ⚠️ **Apple 공식 확인 없음** — 직접 인과 미확정, 벤더 측정치(예: Mobile Action "오가닉 설치 +20~30%")는 **관찰치이지 실험 인과 아님**(선택편향 가능). 벤더 명시 인용. https://www.apptweak.com/en/aso-blog/how-search-ads-can-boost-your-apps-organic-keyword-rankings · https://tenjin.com/blog/apple-search-ads-and-aso-synergy-best-practices-and-success-stories-for-2024/

## 8. 스토어 A/B — 실험 (공식, 상세는 store-testing-playbook.md)
- **Apple PPO**(Product Page Optimization): 기준 대비 **최대 3 treatment**, 아이콘/스크린샷/프리뷰만(**텍스트 아님**), 90일, ≥90% 신뢰. 기준 대비 랜덤 A/B → 승자 선정. https://developer.apple.com/app-store/product-page-optimization/
- **Apple CPP**(Custom Product Pages): **최대 70페이지/앱(2025-10-29 기준; 이전 35에서 2배 상향)**, 스크린샷·프로모텍스트·프리뷰 변형, 키워드 할당·캠페인별 딥링크 URL(딥링크 iOS 18+). CPP=상시 독립 페이지(승자 선정 아님, 트래픽 소스별 맞춤), PPO=기준 대비 랜덤 A/B — **별개 도구**. https://developer.apple.com/app-store/custom-product-pages/
- **Google Play Store Listing Experiments**: 아이콘/피처그래픽/스크린샷/설명, 최대 3변형, **텍스트 테스트 가능**(Apple PPO와 결정적 차이). https://play.google.com/console/about/store-listing-experiments/

## 9. 전환 크리에이티브 위계 (실무)
전환 영향력 대략 순: **아이콘 ≈ 첫 스크린샷(1~3컷) > 평점·리뷰 수 > 프리뷰 영상 > 나머지 스크린샷 > 설명**. 근거: 사용자는 검색결과·페이지에서 수 초만 본다 — 첫인상(아이콘+첫 컷)이 클릭·설치의 대부분을 정함. 스크린샷은 기능 나열이 아니라 **가치·후크 우선**(가로형 스토리텔링 캡션). ⚠️ 순위·수치는 벤더 A/B 관찰의 컨센서스이며 앱·카테고리별 상이(확인 필요) — 그래서 §8 스토어 A/B로 자기 앱에서 검증하는 게 원칙.

## 10. 평점·리뷰 관리 실무 (공식)

### Apple — SKStoreReviewController (iOS)
- **API**: `SKStoreReviewController.requestReview()` / SwiftUI: `RequestReviewAction`. Apple이 내부적으로 표시 여부·빈도를 제어 — 호출해도 실제 다이얼로그가 뜨지 않을 수 있음.
- **빈도 제한**: **365일에 최대 3회** — SDK가 자동 제어. 개발자가 별도 카운팅 불필요. https://developer.apple.com/documentation/storekit/skstorereviewcontroller
- **타이밍 원칙(공식 HIG)**: 가치 경험(앱의 핵심 목적 달성) 직후 요청. **버튼·컨트롤로 트리거 금지** — 사용자가 이미 쿼터 소진시 아무것도 안 뜨면 broken UX. https://developer.apple.com/app-store/ratings-and-reviews/
- **전략 원칙**: 좋은 경험 직후(레벨 완료, 목표 달성, 작업 완성 등) → 긍정 편향된 리뷰 확보.

### Google Play — In-App Review API
- **API**: `Play Core` → `ReviewManager.requestReviewFlow()` → `launchReviewFlow()`. https://developer.android.com/guide/playcore/in-app-review
- **쿼터**: Google이 사용자별 시간-바운드 쿼터 관리(정확값 미공개, 약 수 주 단위 추정). 쿼터 소진 시 다이얼로그 미표시 — **버튼 트리거 금지**(Apple과 동일 이유).
- **ReviewInfo 유효기간**: pre-cache하되 너무 일찍 요청하지 않음 — 유효기간 내 `launchReviewFlow` 실행 필요.
- **Apple과 공통점**: 버튼 트리거 금지, 가치 경험 후 요청, 쿼터 시스템.

### 공통 전략
가짜 리뷰·인센티브 리뷰 = 양쪽 스토어 정책 위반 → 앱 제거·계정 정지 리스크. 부정 리뷰는 제품 개선 신호로 활용, 답글로 대응(Google Play 콘솔 답글 기능). 평점 3.0 미만은 전환에 즉각 타격 — 방치보다 적극 관리.

## 11. CPP 키워드 할당 (2025-10-29 신기능 — 공식)

2025-10-29 발표: CPP 70페이지 상향과 동시에 **각 CPP에 키워드 할당 기능 추가**. 키워드 할당된 CPP는 해당 키워드 검색결과에 기본 페이지 대신 노출 가능. 구체적:
- 캠페인별 맞춤 크리에이티브 + 검색 노출까지 연결 가능 (이전: 캠페인 딥링크만 가능).
- 검색에서 특정 오디언스(장르·기능별)에 최적화된 페이지 노출.
- ⚠️ 키워드 할당은 해당 CPP의 의도(컨텐츠·크리에이티브)와 일치해야 함(App Review 정책).
출처: https://developer.apple.com/news/?id=gf6mgrs6 · https://developer.apple.com/app-store/custom-product-pages/

## 12. 스토어별 핵심 차이 종합표

| 항목 | Apple App Store | Google Play |
|---|---|---|
| 키워드 필드 | ✅ 100자, 비공개, 쉼표·공백없이 | ❌ 없음 |
| 인덱싱 필드 | 앱명·부제·키워드필드·카테고리 | 제목·짧은설명·전체설명(NLP) |
| 설명 인덱싱 | ❌ 비인덱싱(공식 확인) | ✅ 인덱싱됨 |
| 프로모텍스트 인덱싱 | ❌ 비인덱싱(공식 확인) | N/A |
| 제목 A/B 테스트 | ❌ 불가(PPO 텍스트 미지원) | ✅ 가능(Store Listing Experiments) |
| 스토어 A/B 도구 | PPO(비주얼만) + CPP(상시 맞춤) | Store Listing Experiments(텍스트 포함) |
| CPP/맞춤 페이지 | ✅ 최대 70(2025-10-29) | N/A |
| 인앱 리뷰 API | SKStoreReviewController (365일 3회) | Play Core ReviewManager (쿼터 미공개) |
| 키워드 밀도 개념 | 없음(필드에 최대한 채우기) | 있음 — 주 2~3%, 보조 1~2%(벤더 권장) |
| 크로스 로컬라이제이션 | ✅ 실효 키워드 확장(벤더 컨센서스) | N/A(설명에 현지어 직접 작성) |

## 13. 출처
- Apple App Store / Google Play 공식 가이드(정책 급변 — 최신 확인). · Wikipedia ASO(용어 기원). · 크로스-로컬·halo·밀도·전환위계는 **벤더 컨센서스**(MobileAction·AppTweak·Phiture·Tenjin 등) — 진실원 아님, 인과 미확정 다수.
- CPP 70페이지·키워드할당: https://developer.apple.com/news/?id=gf6mgrs6 (2025-10-29 공식 발표)
- SKStoreReviewController: https://developer.apple.com/documentation/storekit/skstorereviewcontroller
- Google Play In-App Review API: https://developer.android.com/guide/playcore/in-app-review
