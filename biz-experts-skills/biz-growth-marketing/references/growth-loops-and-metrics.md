# 성장 루프 & 핵심 지표 참조 (Growth Loops & Metrics)

> 작성: 2026-07-01. 부패 등급: 중간. 벤치마크 수치는 시점 라벨 필수. 확인 안 된 수치는 "확인 필요" 표기.

---

## 1. AARRR 단계별 지표 표

McClure(2007) 원 순서: **A**cquisition → **A**ctivation → **R**etention → **R**eferral → **R**evenue.
⚠️ RARRA·AAARRR는 후대 파생이며 원전이 아님.

| 단계 | 핵심 질문 | 대표 지표 | 보조 지표 | 실무 기준선 (참고값, 확인 필요) |
|---|---|---|---|---|
| **Acquisition** | 어떻게, 얼마나 오는가 | CAC(채널별)·신규 가입수·채널 전환율 | CPM·CPC·유기 vs. 유료 비율 | LTV:CAC ≥ 3:1 (SaaS 일반 기준, 확인 필요) |
| **Activation** | 첫 가치 경험(aha)에 도달했는가 | 활성화율(aha 행동 도달 %)·TTV(time-to-value) | 온보딩 완료율·첫 세션 길이 | SaaS 온보딩 완료율 20~40% (확인 필요) |
| **Retention** | 다시 돌아오는가 | D1/D7/D30 리텐션·코호트 곡선 평탄화 | DAU/MAU·세션 빈도·코호트별 N주 리텐션 | 모바일 앱 D30 평균 ~5~10% (2023 Adjust, 확인 필요) |
| **Referral** | 남을 데려오는가 | 바이럴 k-factor·추천 경유 가입 % | NPS·초대 발송수·초대 전환율 | 현실 K 범위 0.2~0.8 (소비자앱 일반, 확인 필요) |
| **Revenue** | 돈을 내는가(지속적으로) | ARPU·LTV·MRR(SaaS)·전환율 | Churn rate·Expansion MRR·Payback period | SaaS LTV:CAC ≥ 3:1, Payback ≤ 12개월 (확인 필요) |

**지표 선택 원칙**:
- 코호트 기준으로 보지 않으면 성장·이탈이 뒤섞여 왜곡됨.
- 누적·총량(가입자 합계 등)은 허영 지표(vanity metric) — 비율·코호트 기반 지표로 대체.
- 단계별 전환율 중 가장 낮은 곳(biggest leak)이 우선 공략 지점.

---

## 2. 노스스타 메트릭(NSM) 프레임 — Amplitude/Reforge

출처: Amplitude, *The North Star Playbook*(2018~). https://amplitude.com/books/north-star/about-north-star-framework

### 정의
고객이 제품에서 얻는 가치를 가장 잘 대표하는 **단일 지표**. 매출의 **선행지표**이며 팀이 직접 영향을 줄 수 있어야 한다.

### 좋은 NSM의 세 조건
1. **사용자 가치 대표**: "더 많아질수록 사용자가 더 많은 가치를 얻는다"는 명제가 성립해야 함.
2. **팀이 영향 가능**: 너무 광범위하면 아무 팀도 소유하지 못함.
3. **수익의 선행지표**: 매출 자체(후행)나 DAU 단독(허영)이 아님.

### NSM 예시 (공개 자료 기반 추정 — 내부 공식 수치와 다를 수 있음, 확인 필요)
| 제품 | NSM (추정) | 이유 |
|---|---|---|
| Airbnb | 예약된 숙박 밤 수(nights booked) | 숙박 = 호스트·게스트 모두에게 가치 교환 완성 |
| Spotify | 월간 청취 시간 | 시간 = 음악 가치 소비의 직접 신호 |
| Slack | 팀 내 전송 메시지 수 | 소통 = 협업 가치의 직접 단위 |
| Facebook | DAU(초기) | 규모 성장기 단순 지표; 성숙기엔 변경 |

### NSM 아래 Input Metrics 구조
```
NSM (단일)
 ├── Input 1: [팀 A 소유] — NSM에 가장 직접 영향
 ├── Input 2: [팀 B 소유]
 └── Input 3: [팀 C 소유]
```
각 팀은 Input 1개를 소유하고, 그 Input이 NSM에 어떻게 기여하는지 명확히 정의.

### 흔한 실수
- NSM을 매출·DAU 등 후행·허영 지표로 설정.
- 복수 NSM — 팀 정렬이 분산됨.
- Goodhart's Law 경계: 지표가 목표가 되면 왜곡 행동 발생(숫자를 올리기 위한 꼼수). 정기 재검토 필요(분기~반기).

---

## 3. 성장 루프 4유형 비교표

출처: Brian Balfour/Reforge, "Growth Loops are the New Funnels"(~2018). https://blog.brianbalfour.com/p/the-four-fits-a-growth-framework

**루프 vs. 퍼널 핵심 차이**:
- 퍼널: 선형·단방향(입력→손실→출력). 최적화는 각 단계 전환율 개선.
- 루프: 순환·복리(출력이 다음 사이클 입력으로 재투입). 최적화는 전환율 + 사이클 속도 + 재투입 비율.

| 유형 | 입력 | 핵심 행동 | 출력 | 재투입 방식 | 대표 사례 | 작동 조건 | 주요 레버 |
|---|---|---|---|---|---|---|---|
| **Viral Loop** | 신규 유저 획득 | 초대·공유·임베드 | 초대받은 잠재 유저 | 가입 후 다시 초대 발생 | Dropbox·WhatsApp·Slack | K > 0, 초대 마찰 낮을수록 | 초대 경험 UX·사이클 타임 단축·전환율 |
| **Content Loop** | 콘텐츠 제작 유저 | UGC 생성·SEO 인덱싱 | 검색 유입(새 유저) | 신규 유저가 또 콘텐츠 생성 | Pinterest·Reddit·Yelp·Medium | 검색 수요 존재·크롤 가능 | 콘텐츠 품질·SEO 구조·제작 마찰 제거 |
| **Paid Loop** | 광고비 투입 | 유료 광고 캠페인 | LTV > CAC인 신규 유저 | LTV 수익 → 더 많은 광고비 재투자 | 전형적 D2C·앱 | LTV:CAC > 1 (복리에는 > 3 권장) | CAC 감소·LTV 증가·리텐션 |
| **Sales-Driven Loop** | 영업 인력 | 엔터프라이즈 계약 | ARR·확장 계약 | ARR → 더 많은 영업 채용·마케팅 투자 | Salesforce·HubSpot 초기 | ACV > 영업비용·갱신율 높음 | ACV 크기·영업 사이클 단축·확장 MRR |

### 루프 선택 결정 기준 (Four Fits 요약)
Balfour의 Four Fits: Market↔Product, Product↔Channel, Channel↔Model, Model↔Market.
- **B2C 소비자앱 + 네트워크 효과**: Viral Loop 우선 탐색.
- **정보형/검색 의존 서비스**: Content Loop 탐색.
- **단위경제 검증된 상품**: Paid Loop 확장 가능.
- **엔터프라이즈 B2B**: Sales-Driven Loop → 성숙 후 Product-Led(Viral) 추가.
- 대부분의 성장한 제품은 **복수 루프 병용** — 유료로 초기 데이터 확보 후 바이럴·콘텐츠로 전환.

### 루프가 안 돌아가는 흔한 이유
- Viral: 초대 마찰 과다, 초대 동기 부족(보상이 제품 가치와 분리), 리텐션 부재로 초대 기반 소진.
- Content: SEO 접근성 차단(로그인 필수), 콘텐츠 품질 편차 과대, 크롤 막힘.
- Paid: LTV<CAC(단위경제 음), 시장 포화로 CAC 상승.
- Sales: ACV 너무 작아 영업비용 회수 불가, 갱신율 낮아 Expansion MRR 미발생.

---

## 4. 바이럴 k-factor 실무 계산 참조

K = i × conv%
- i = 기존 유저 1명이 평균 발송하는 초대 수 (코호트 30일 기준 측정 권장)
- conv% = 초대 수신자 중 실제 가입한 비율

**사이클 타임(ct) 지수 효과**: t시간 후 누적 유저 ≈ 초기 × K^(t/ct)
- K=0.8, ct=2일: 20일 후 ≈ 초기 × 1.49
- K=0.8, ct=30일: 20일 후 ≈ 초기 × 0.98 (성장 미미)
→ 같은 K라도 ct 단축 효과가 극적. 초대 발송~수락까지 UX 마찰 제거가 핵심 레버.

**funnel.py**로 k-factor 빠른 계산 가능: `python funnel.py k 1.5 0.3`

---

## 5. 리텐션 곡선 해석 (PMF 신호)

출처: Andrew Chen, andrewchen.com. https://andrewchen.com/more-retention-more-viral-growth/

- **하락 후 평탄화(flatten)**: D30 이후 코호트 곡선이 특정 수준(예: 15~30%)에서 수평 유지 → 고정 사용자 기반 존재 → PMF 신호.
- **0으로 수렴**: 이탈이 계속 → PMF 없음. 유입을 늘려도 밑 빠진 독.
- **평탄선 높이**: 장기 리텐션 상한이자 바이럴·유료 루프의 복리 기반.
- ⚠️ "스마일 커브(smiling retention curve)" — 리텐션이 떨어지다 다시 올라가는 형태. a16z가 AI 앱 분석에서 보고(2024). 성숙 사용자의 재활성화 또는 사용 패턴 심화 신호. 파워유저 곡선(히스토그램 U자)과 다른 개념이므로 혼용 주의. https://a16z.com/ai-retention-benchmarks/
