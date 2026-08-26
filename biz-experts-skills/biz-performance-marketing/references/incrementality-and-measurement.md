# 증분성 & 측정 스택 — iROAS · MER · ATT 이후 대응

> 부패 매우 빠름 — 플랫폼 기여 모델·측정 정책은 공식 문서 최신 확인. 벤치마크는 YYYY 라벨 필수. 불확실 "확인 필요". 업데이트: 2026-07-01.

---

## 1. 세 가지 ROAS 개념 비교표

| 지표 | 공식 | 무엇을 측정 | 한계 |
|---|---|---|---|
| **플랫폼 ROAS** | 채널 기여 매출 ÷ 채널 광고비 | 채널이 클레임한 기여 매출 | 중복 계상·상관(인과 아님)·ATT 이후 모델링 비중↑ |
| **MER** (Media Efficiency Ratio) | 총 매출 ÷ 총 광고비 | 전사 광고 효율(기여 무관) | 광고 외 매출(오가닉·SEO)도 분자에 포함돼 매출↑에 과대 신호 가능 |
| **iROAS** (증분 ROAS) | 증분 매출(처리−대조) ÷ 광고비 | 광고의 인과적 매출 기여 | 실험 설계·검정력·지역 유사성 등 실행 난이도 높음 |

**핵심 원칙**: 플랫폼 ROAS = 상관/기여. iROAS = 인과. MER = 비즈니스 레벨 건강도 체크. **셋 다 봐야 한다 — 하나만 보면 속는다.**

---

## 2. 플랫폼 ROAS가 iROAS보다 높은 3대 이유

### 2-1. 어차피 살 사람에게 크레딧 (브랜드·리타게팅)
- 브랜드 검색 광고·리타게팅은 이미 구매 의향이 있는 사람을 포착 → 광고 없어도 전환됐을 가능성↑.
- 결과: 플랫폼 ROAS는 높게 찍히지만 실제 증분은 낮음.
- **실측 사례** (Stella 2025, N=225 지오 테스트): Google 브랜드 검색 중앙값 iROAS = **0.70x** — 브랜드 검색 $1 지출당 증분 매출 $0.70. 광고 없어도 왔을 사람이 더 많다는 의미.

### 2-2. 클릭/뷰스루 과다 클레임 (여러 채널 중복)
- Meta 기본 기여 윈도우: 1일 뷰스루 + 7일 클릭. Google, TikTok도 각자 클레임.
- 한 구매를 Meta·Google이 각자 100% 기여로 계산 → 전체 클레임 합산 ≫ 실제 매출.

### 2-3. ATT 이후 모델링 전환 비중↑
- iOS 14.5 ATT(2021-04) 이후 실측 IDFA가 대폭 감소 → 플랫폼이 모델링·추정 전환을 리포트에 포함.
- 모델링 전환은 실측이 아님. 특히 Meta에서 "전환 급증"이 실제 구매 급증인지 모델 변경인지 구분 어려움.

---

## 3. 증분성 측정 방법론

### 3-1. 지오 리프트 (Geo Holdout) — 프라이버시 안전, 현재 표준

**원리**: 유사한 지역군을 처리(광고 집행)·대조(광고 중단)로 분리 → 매출 차이 = 증분.

```
증분 매출 = 처리 지역 매출 − (대조 지역 매출 × 인구/규모 보정 계수)
iROAS = 증분 매출 ÷ 처리 지역 광고비
```

**설계 요소**:
- 지역 유사성(사전 기간 매출 패턴 일치 — MAPE ≤0.15 / R² 0.85~0.94이면 100% 유의도 달성. 출처: Stella 2025)
- 충분한 지역 수와 기간: 신호 대 잡음비 확보 필요
- 통계적 검정력(power): 탐지하려는 효과 크기에 맞는 표본 설계

**장점**: 유저 추적 불필요 · 프라이버시 안전 · ATT·GDPR 무관 · 오픈소스 도구(Facebook GeoLift R 패키지, Google Causal Impact) 이용 가능

### 3-2. 유저 홀드아웃 / Ghost Ads — 완벽 대조군

**원리**: 노출됐을 광고를 실제로 미노출하는 대조군 구성(PSA 플라시보보다 우월).

- Google Conversion Lift https://support.google.com/google-ads/answer/12003020
- Meta Conversion Lift (RCT 방식, 2014~)

**장점**: 완벽한 대조군(진짜 비노출). **단점**: 플랫폼 인프라 의존 → 플랫폼 외부 채널엔 적용 불가.

### 3-3. MMM (Media Mix Modeling)

**원리**: 역사적 지출·매출·외부 변수(시즌·경쟁 등)로 채널별 기여도를 통계 모델로 추정. ATT 이후 앱·모바일 캠페인의 보완재로 재부상.

**장점**: 모든 채널 동시 평가 가능 · 프라이버시 안전. **단점**: 데이터량 필요(최소 2~3년 권장) · 결과 신뢰성은 모델 가정에 크게 의존.

---

## 4. 채널별 iROAS 벤치마크 (2025)

> 출처: Stella 2025 DTC Incrementality Benchmarks. 225개 지오 기반 증분성 테스트, 2024-08~2025-12. 이커머스/DTC 편향. 자기 카테고리·계정으로 재조정 필수.

| 채널 | 중앙값 iROAS | 표본 수 |
|---|---|---|
| Tatari CTV | 3.30x | N=18 |
| **Google Performance Max** | **2.98x** | — |
| **Meta** | **2.92x** | N=63 |
| Google YouTube | 2.17x | — |
| Google Shopping | 1.86x | — |
| Google Search (비브랜드) | 1.46x | — |
| TikTok | 0.94x | N=10 |
| **Google Search (브랜드)** | **0.70x** | — |

⚠️ 주의:
- 전체 중앙값 iROAS = **2.31x** (IQR 1.36x~3.24x)
- 88.4% 테스트가 90%+ 신뢰수준에서 통계적 유의미
- **브랜드 검색 0.70x** — $1 지출당 $0.70 증분. 광고 없어도 왔을 트래픽 비중이 큼. 방어 목적(경쟁사 노출 방지)은 별도 판단.
- **TikTok 0.94x** — iROAS 1.0 미만이면 광고 없어도 왔을 매출이 광고 기여보다 많은 것(브랜드 인지도·오가닉 뷰 기여 별도 고려).
- 플랫폼 ROAS 대비 iROAS는 **30~70% 낮게 나오는 경우 흔함** (출처: Measured.com 실무 가이드, 확인 필요)

---

## 5. MER / aMER 운영 기준

### 5-1. MER (Media Efficiency Ratio) — 이커머스 북극성

```
MER = 총 매출 ÷ 총 광고비 (전사, 기여 무관)
```

⚠️ **Triple Whale 표기 주의**: spend ÷ revenue(역수, %)로 표기 — 높을수록 나쁨. 팀 내 정의 합의 필수.

**2025 DTC 벤치마크** (Triple Whale 2025 고객 중앙값): MER **2.4x** (중앙값). 대다수 DTC 브랜드 중 절반이 비용 차감 후 손익분기 이하 운영. 성숙 브랜드 3x~5x, 구독 브랜드 6x 이상 가능(확인 필요, 산업 편차 큼). 출처: Triple Whale 2025 https://www.triplewhale.com/blog/marketing-efficiency-ratio

**왜 ATT 이후 MER이 부상했나**: 플랫폼 픽셀 붕괴(iOS ATT) → 채널별 기여 신뢰도 하락 → 기여 무관 전사 효율 지표(MER)가 더 신뢰성 있는 북극성이 됨.

### 5-2. aMER (Acquisition MER) — 신규 획득 효율

```
aMER = 총 매출 ÷ 신규 고객 획득 광고비 (리타게팅·브랜드 제외)
```

MER보다 신규수요 창출 효율을 정밀하게 봄. 리타게팅 지출이 분모에 들어가면 기존고객 수확이 aMER을 부풀리므로, 진짜 신규 획득에 쓰인 광고비만 분모에.

### 5-3. 운영 기준 설정법

MER 목표는 **사업 모델의 단위경제에서 역산**:
```
목표 MER = 1 ÷ 허용 광고비율 (예: 광고비를 매출의 20%로 유지 → MER 목표 5.0x)
```
실제 운영: MER이 목표 이하면 예산 조이기 / 이상이면 증액 신호 — 단, iROAS 교차 확인 후 결정.

---

## 6. ATT 이후 측정 스택 (iOS 앱 캠페인)

### 6-1. SKAdNetwork 4 (SKAN 4) 개요

Apple 공식: https://developer.apple.com/documentation/storekit/skadnetwork/
다중 윈도우 postback: https://developer.apple.com/documentation/storekit/receiving-postbacks-in-multiple-conversion-windows

| SKAN 4 핵심 | 내용 |
|---|---|
| **Postback 수** | 최대 3개 (iOS 16.1+, SKAN 4 서명 광고) |
| **윈도우** | PB1: 0~2일 / PB2: 3~7일 / PB3: 8~35일 → 설치 후 최대 35일 커버 |
| **Conversion value 2종** | fine (6비트, 0~63, 64조합) — PB1만 가능 / coarse (none·low·medium·high) — PB2·3은 coarse만 |
| **lockWindow** | 전환값 조기 확정, postback 빨리 받는 옵션 |
| **지연·익명화** | 프라이버시 임계 미충족 시 지연 최대 수일, crowd anonymity 적용 |

### 6-2. SKAN 4 전략 워크시트 (Postback별 이벤트 매핑)

| Postback | 윈도우 | 매핑 이벤트 예시 |
|---|---|---|
| **PB1** (fine) | 0~2일 | 설치 → 첫 실행 → 가입 → 첫 구매 / 트라이얼 시작 |
| **PB2** (coarse) | 3~7일 | D3 리텐션 · 핵심 기능 사용 깊이 |
| **PB3** (coarse) | 8~35일 | 구독 시작 · 인앱 결제 · D30 리텐션 |

**핵심 실무 포인트**: conversion value schema를 기본값 그대로 두지 말 것. 품질 유저를 최적화하는 schema를 의도적으로 설계한 팀과 기본값 팀 사이에 성과 차이가 큼(Singular, Segwise 2025 가이드 기준, 확인 필요).

### 6-3. CAPI (서버사이드 이벤트) — 브라우저 신호 복구

ATT는 크로스앱 추적을 제한하지만 **웹·서버사이드 이벤트는 별도**. Meta CAPI(Conversions API) / Google Enhanced Conversions로 서버에서 직접 전환 신호를 전달하면 픽셀 손실 일부 복구 가능.

- Meta CAPI 공식: https://developers.facebook.com/docs/marketing-api/conversions-api
- Google Enhanced Conversions: https://support.google.com/google-ads/answer/9888656

**중복 카운팅 주의**: 브라우저 픽셀 + CAPI를 동시에 쓸 때 중복 제거(event_id deduplication) 필수.

### 6-4. 통합 측정 스택 권장 구성

```
[앱 캠페인]
SKAN 4 (postback schema 최적화)
  + MMP (Adjust / AppsFlyer / Singular) — postback 집계·분석
  + CAPI (웹 전환이 있는 경우 서버사이드 보완)
  + MMM (히스토리컬 채널 기여 모델)
  + 지오 리프트 (주요 캠페인 증분성 정기 검증)

[웹 캠페인]
픽셀 + CAPI(서버사이드)
  + MER/aMER 대시보드 (전사 북극성)
  + 지오 리프트 or 유저 홀드아웃 (주요 채널 증분 검증)
  + MMM (장기 채널 배분 가이드)
```

---

## 7. 입찰 전략 — 학습기 & 전환 임계

### 7-1. Google Smart Bidding 전환 임계 (2025 기준 업계 통설)

| 전략 | 권장 최소 전환 | 비고 |
|---|---|---|
| **Max Conversions** | 제한 없음 | 데이터 없어도 사용, 예산이 실질 상한 |
| **tCPA** | 캠페인당 주 **30전환** 이상 | 이하면 학습 불안정 |
| **tROAS** | 캠페인당 주 **50전환** 이상 | 값(value) 데이터 정확성 필수 |

⚠️ "30전환/50전환" 임계는 Google 공식 지원 문서 기반 업계 통설이며, 구글이 일부 문서에서 명시. 단, 공식 확정 수치로 절대화 금지(캠페인 유형·업종·지역별 편차, "확인 필요"). 출처: https://support.google.com/google-ads/faq/10286469

### 7-2. 학습 리셋 트리거

- 입찰 목표(tCPA/tROAS 값) 변경
- 예산 변경 **30% 이상** (통설, 공식 확정 아님)
- 새 전환 이벤트 추가 / 소재 대폭 변경
- 광범위 타깃팅 · 지역·예약 변경

**실무 원칙**: 학습 중 성과가 불안정해도 최소 1~2주 안정화 기간 부여. 조급한 변경은 학습을 계속 리셋시켜 영구 불안정 상태 초래.

### 7-3. 입찰 전략 선택 순서

```
데이터 없음 → Max Conversions (데이터 축적)
↓ 주 30+ 전환 안정
→ tCPA 전환 (비용 목표 설정)
↓ 주 50+ 전환 & 가치 데이터 정확
→ tROAS 전환 (가치 최적화)
```

Meta ASC(Advantage+ Shopping) 전환 시 고려: 수동 캠페인보다 15~25% CPA 낮은 경우 다수 보고(2024-25 Black Friday 데이터 기준, 확인 필요). 단, 소재 다양성·Pixel/CAPI 신호 품질 필수 전제.

---

## 8. 출처

- Google Conversion Lift 공식: https://support.google.com/google-ads/answer/12003020
- Meta Conversion Lift 공식: https://www.facebook.com/business/help/1629053430834748
- Apple SKAN 4 공식: https://developer.apple.com/documentation/storekit/skadnetwork/
- Meta CAPI 공식: https://developers.facebook.com/docs/marketing-api/conversions-api
- Google Enhanced Conversions: https://support.google.com/google-ads/answer/9888656
- Stella 2025 DTC Incrementality Benchmarks (225 geo tests, 2024-08~2025-12): https://www.stellaheystella.com/blog/2025-dtc-digital-advertising-incrementality-benchmarks
- Measured.com, Platform ROAS to iROAS: https://www.measured.com/faq/leveling-up-media-measurement-the-performance-marketers-journey-from-platform-roas-to-true-incrementality
- Triple Whale, MER guide (2025): https://www.triplewhale.com/blog/marketing-efficiency-ratio
- Singular SKAN 4 전략 가이드: https://www.singular.net/blog/skan-4-strategy/
- Adjust SKAN 4 mapping: https://help.adjust.com/en/article/set-up-skan-4-mapping
- Segwise SKAN 4 구현 가이드: https://segwise.ai/blog/skan-4-implementation-guide
