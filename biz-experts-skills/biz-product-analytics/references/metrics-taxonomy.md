# metrics-taxonomy — 지표 프레임·리텐션·허영 vs 실질·이벤트 택소노미 실무판

> "무엇을 어떻게 측정·해석하는가"의 실무 레퍼런스. evidence.md의 검증 사실(HEART 3인저자·AARRR 2007·Simpson 1975·NSM Amplitude 정형화) 위에 실행 절차를 얹는다. 벤치마크 수치는 제품 유형별로 다름("확인 필요").

---

## 1. 지표 프레임 3종 — 언제 무엇을

| 프레임 | 저자/출처 | 쓰임 | 주의 |
|---|---|---|---|
| **HEART** | Rodden·Hutchinson·Fu, Google, CHI 2010 | UX 품질을 5차원(Happiness·Engagement·Adoption·Retention·Task success)으로. 각 차원을 **Goals→Signals→Metrics(GSM)**로 구체화 | 5개 다 쓸 필요 없음 — 제품에 맞는 2~3개만. 단독 저자 Rodden 아님 |
| **AARRR("해적 지표")** | Dave McClure, 2007 | 라이프사이클 퍼널(Acquisition·Activation·Retention·Revenue·Referral) 진단 | 퍼널은 "샌다" — 루프 사고와 병행(→ biz-growth-pm) |
| **North Star + 입력** | Amplitude 정형화(용어는 Ellis) | 조직 정렬용 단일 출력 + 입력 3~5 | NSM은 가치 선행지표 — 매출·MAU 아님 |

### GSM 적용 예 (HEART의 Engagement 차원)
- **Goal**: 사용자가 핵심 기능을 습관적으로 쓴다.
- **Signal**: 주간 핵심 액션 수행, 세션당 액션 수.
- **Metric**: WAU 중 핵심액션 3+회 비율, 세션당 평균 액션.

---

## 2. AARRR 각 단계 실무 지표

| 단계 | 질문 | 대표 지표 | 허영 함정 |
|---|---|---|---|
| Acquisition | 어떻게 찾아오나 | 채널별 유입, CAC | 총 방문수(비율 없이) |
| Activation | 첫 가치 경험했나 | 활성화율, TTV | "가입 완료"를 활성화로 오인 |
| Retention | 다시 오나 | N일 코호트 리텐션, 이탈률 | 전체 활성 수(신규가 이탈 가림) |
| Revenue | 돈 되나 | 전환율, ARPU, 코호트 LTV | 누적 매출 |
| Referral | 추천하나 | k-factor, 추천 유입 비율 | 총 공유 클릭(전환 없이) |

---

## 3. 리텐션 & 코호트 — 진실이 사는 곳

### 3-1. 리텐션 곡선 읽기
- **건강한 곡선 = 평탄화(flattening)**: 초반에 떨어지다 어느 수준에서 **수평선(asymptote)**을 그리면 = 붙잡힌 코어 유저 존재 = 지속 성장 가능.
- **평탄화 안 됨 = 0으로 수렴**: 아무리 신규를 부어도 새는 독 — 획득 중단 시 붕괴. 이건 성장이 아니라 누수.
- a16z는 AI 제품에서 리텐션이 초반 급락 후 반등하는 "smiling curve"(웃는 곡선) 패턴을 관찰(제품 유형별, 절대 기준 아님). https://a16z.com/ai-retention-benchmarks/

### 3-2. 리텐션 정의 3종 (섞으면 안 됨)
- **N-day**: 정확히 N일째 돌아온 비율(엄격, 저빈도 제품에 가혹).
- **Unbounded/Rolling**: N일 이후 언젠가 돌아온 비율(관대).
- **Bracket/Range**: 특정 기간(예: 7~13일) 내 방문(주간 제품에 적합).
> 제품의 자연 사용 주기에 맞춰 선택. 일 1회 제품에 N-day, 주 1회 제품에 weekly bracket.

### 3-3. 코호트 분석 3축
- **Acquisition 코호트**(가입 시점별) — 제품 개선이 신규 코호트 리텐션을 실제 올렸는지.
- **Behavioral 코호트**(특정 행동 수행자) — aha 행동과 리텐션 상관(활성화 정의용).
- **세그먼트 코호트**(채널·플랜·지역) — Simpson 역설 대비 분해.

### 3-4. 끈끈함(Stickiness)
- DAU/MAU = 한 달 중 며칠 쓰나. 0.2면 월 6일. **절대 기준 아님** — 일 사용 제품(메신저)은 높고, 월 1회 제품(세금)은 낮아도 정상. (SKILL 정량표 "확인 필요"와 일치)

---

## 4. 허영 지표(Vanity) vs 실질 지표(Actionable)

Lean Analytics(Croll·Yoskovitz, 2013) 기준 — 좋은 지표 = **비교 가능 · 이해 가능 · 비율(rate) · 행동 유발**.

| 허영 (❌) | 실질 (✅) | 왜 |
|---|---|---|
| 누적 가입자 | 활성화율·N일 리텐션 | 누적은 절대 안 줄어 항상 "성장"처럼 보임 |
| 총 페이지뷰 | 세션당 핵심액션·전환율 | 총량은 유입만 늘려도 오름 |
| 총 다운로드 | 다운로드→활성화율 | 다운로드 후 안 쓰면 무의미 |
| 총 매출(vanity로 쓸 때) | 코호트 LTV, ARPU 추이 | 신규 유입에 가려진 이탈 안 보임 |
| 평균 세션 시간 | 분포(중앙값·분위) + 세그먼트 | 헤비유저가 평균 끌어올림(평균의 함정) |
| MAU 총량 | 코호트 리텐션 곡선 | 신규가 이탈을 가림(§3-1) |

> **OMTM(One Metric That Matters)**: 지금 이 단계에서 가장 중요한 하나에 집중(Lean Analytics). 단계 바뀌면 OMTM도 바뀐다.

---

## 5. 이벤트 택소노미 (Amplitude·Mixpanel 1차, 검증)

### 5-1. Object-Action 프레임
- **구조**: `Object`(명사, 대상) + `Action`(동사, 과거형). 예: `Order Completed`, `Message Sent`, `Video Played`.
- **과거형** — 성공적으로 일어난 사실의 기록. `Complete`(X) → `Completed`(O).
- **케이싱 통일**: Mixpanel은 웨어하우스 익스포트 고려 시 `snake_case` 권장, Amplitude 기본은 Title Case. **택일 후 사내 통일**이 핵심(혼용 금지).

### 5-2. 이벤트 vs 속성 설계
- **이벤트(Event)**: 무슨 일이 일어났나(동사). 너무 잘게 쪼개지 말 것 — `Button Clicked` + 속성 `button_name`이, 버튼마다 새 이벤트보다 낫다.
- **속성(Property)**: 그 일의 맥락(형용사) — user property(사용자 특성) vs event property(그 순간 맥락) 구분.
- **황금률**: 이벤트는 적게·재사용 가능하게, 맥락은 속성으로.

### 5-3. Tracking Plan (SSOT 문서)
살아있는 문서로 관리: `이벤트명 | 정의 | 트리거 시점 | 기대 속성 | 수집 이유 | 오너 | 플랫폼`. 분기별로 중복·폐기·모호 이벤트 정리. 오너 없는 이벤트는 방치되어 데이터 부패.
> 구현(SDK 연동·SQL·dbt)은 → dev-data-analysis. 이 문서는 "무엇을 어떻게 정의하나"까지.

### 5-4. 택소노미 착수 순서
1. **결정 질문 → 필요 지표 역산**(측정 먼저 X, 정의 먼저 O — 안티패턴 5).
2. 지표를 만드는 데 필요한 최소 이벤트 목록화.
3. Object-Action + 속성 스키마 확정, Tracking Plan에 기록.
4. 개발 핸드오프 → 데이터 검증(누락·중복·잘못된 트리거) → 대시보드.

---

## 6. 통계 함정 체크리스트 (해석 단계)

| 함정 | 증상 | 방어 | 앵커 |
|---|---|---|---|
| 심슨 역설 | 전체와 세그먼트 결론 반대 | 항상 세그먼트 분해 | Bickel et al. 1975 (데이터 1973) |
| 생존자 편향 | 현재 유저만 분석 | 이탈 코호트 포함 | Wald, WWII |
| 상관≠인과 | "X 쓴 사람이 잘 남음→X가 원인" | A/B로만 인과 확정 | Pearl, *Book of Why* |
| Peeking/조기중단 | 유의 뜨자마자 종료 | 표본·기간 사전 고정 | Kohavi et al. 2020 |
| SRM(표본비 불일치) | A/B 그룹 배정 비율 어긋남 | 실험 무효 처리 | Kohavi et al. 2020 |
| 다중비교 | 지표 20개 중 몇 개 "유의" | 사전 가설·보정 | Kohavi et al. 2020 |

---

## 출처
- HEART: Rodden·Hutchinson·Fu, CHI 2010. https://research.google/pubs/measuring-the-user-experience-on-a-large-scale-user-centered-metrics-for-web-applications/
- AARRR: McClure, 2007. https://www.slideshare.net/slideshow/startup-metrics-for-pirates-long-version/89026
- Lean Analytics: Croll & Yoskovitz, 2013. https://www.oreilly.com/library/view/lean-analytics/9781449335687/
- 이벤트 택소노미: Amplitude https://amplitude.com/explore/data/event-taxonomy · https://amplitude.com/docs/data/data-planning-playbook · Object-Action https://growthmethod.com/object-action-framework/
- 실험 함정: Kohavi/Tang/Xu, *Trustworthy Online Controlled Experiments*(2020). https://experimentguide.com/
