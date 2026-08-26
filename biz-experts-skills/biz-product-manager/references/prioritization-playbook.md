# 우선순위 플레이북 — 실전 산정·프레임 비교·지표 트리

> biz-product-manager 심화 참조. 프레임 정의는 2026-07 웹 검증. 실무 바로 투입용 — 표를 그대로 채워 쓴다.

## 목차
1. RICE 실전 산정표 (채워 쓰는 양식 + 워크시트 예시)
2. 프레임 비교표 — RICE / ICE / Kano / MoSCoW / WSJF (언제 뭘)
3. Kano 실전 — 설문·분류·함정
4. WSJF 실전 — Cost of Delay 3요소 산정
5. MoSCoW 실전 — 배분 규칙과 "Won't"의 힘
6. 제품 지표 트리 (North Star → input → 실행지표)
7. 스코어링 워크숍 진행법 (합의 도출)
8. 흔한 계산 실수 5가지
9. 출처

---

## 1. RICE 실전 산정표

**RICE = (Reach × Impact × Confidence) ÷ Effort.** 점수 자체는 무의미하고 **후보 간 상대 순위**만 의미 있다.

### 각 인자 정의(Intercom 원안)
| 인자 | 단위 | 산정법 |
|---|---|---|
| **Reach** | 기간당 영향받는 사람 수(실수치) | "분기당 이 기능에 도달할 고객 수" — 애널리틱스에서. 추정 금지, 측정. |
| **Impact** | 척도 {3 Massive · 2 High · 1 Medium · 0.5 Low · 0.25 Minimal} | "도달한 1인당 목표 지표를 얼마나 움직이나" |
| **Confidence** | {100% · 80% · 50%} | 근거 강도. 정량 데이터=100, 정성 근거=80, 직감=50. **추측 방지 장치.** |
| **Effort** | person-months(사람·개월) | 설계+개발+테스트 총합. 팀 합의. |

> Confidence 50% 미만이면 "이건 아이디어지 프로젝트가 아니다" — 우선순위 표에 올리기 전에 발견(discovery)으로 돌린다(Intercom 원문의 "50% and below = this is a moonshot").

### 채워 쓰는 워크시트 (그대로 복사)
```
기능: ______________________
Reach   : ____명/분기   (출처: 대시보드 ____)
Impact  : ____ (3/2/1/0.5/0.25)  근거: __________
Confidence: ____% (100/80/50)   근거: __________
Effort  : ____ person-months   (테크리드 합의)
──────────────────────────────
RICE = (Reach × Impact × Confidence%) ÷ Effort = ____
```

### 워크시트 예시 (다크모드 vs 결제 재시도 — 상대 비교)
| 기능 | Reach | Impact | Conf | Effort | RICE | 순위 |
|---|---|---|---|---|---|---|
| 결제 실패 자동 재시도 | 8,000 | 2.0 | 80% | 2 | **6,400** | 1 |
| 다크모드 | 20,000 | 0.5 | 50% | 3 | **1,667** | 2 |
| 알림 센터 개편 | 15,000 | 1.0 | 50% | 4 | **1,875** | (2위 근처) |

교훈: Reach가 큰 다크모드(2만)보다 Reach 작아도 Impact·Confidence 높은 재시도가 이긴다 — "많이 쓰는 기능"이 아니라 "지표를 확실히 움직이는 기능"이 우선. 툴 검산은 `scripts/rice.py`.

---

## 2. 프레임 비교표 — 언제 무엇을

| 프레임 | 산식/구조 | 입력 데이터 | 강점 | 약점 | 언제 쓰나 |
|---|---|---|---|---|---|
| **RICE** | (R×I×C)÷E | Reach 실측·Effort 추정 | Confidence로 추측 억제, 상대 순위 명확 | Reach 데이터 없으면 무력 | 후보 10~30개를 데이터로 줄 세울 때 |
| **ICE** | I×C×E(각 1~10) | 셋 다 주관 점수 | 5분 안에, 데이터 없이 | 자의성 높음(같은 점수 남발) | 초기·데이터 부족·빠른 스크리닝 |
| **Kano** | 만족도 비선형 분류 | 고객 설문(기능별 2문항) | "당연/성능/매력" 구분 → 무엇이 차별화인지 | 설문 비용, 시간 지나면 매력→당연 이동 | 기능 성격 판단·차별화 포인트 찾기 |
| **MoSCoW** | Must/Should/Could/Won't | 이해관계자 합의 | 릴리스 범위 협상에 직관적 | 정량 근거 없음, "다 Must" 함정 | 마감 있는 릴리스 범위 고정 |
| **WSJF** | CoD ÷ JobSize | 3요소×Fibonacci | 지연비용 명시, 큰 조직 정렬 | 상대 추정의 상대 추정(오차 누적) | SAFe·대규모·의존성 많은 백로그 |

**실무 조합**: 초기 스크리닝 ICE → 상위 후보 RICE 정밀 → 기능 성격은 Kano로 보완 → 마감 릴리스는 MoSCoW로 범위 협상. 하나에 올인하지 않는다.

---

## 3. Kano 실전 (Noriaki Kano, 1984)

### 5개 카테고리
| 유형 | 있으면 | 없으면 | 예 |
|---|---|---|---|
| **당연(Must-be)** | 만족 안 오름 | 격한 불만 | 은행앱 로그인 보안 |
| **성능(Performance)** | 선형 만족↑ | 선형 불만↑ | 로딩 속도, 배터리 |
| **매력(Attractive/Delighter)** | 감동 | 불만 없음 | 예상 못한 자동화 |
| **무관(Indifferent)** | 반응 없음 | 반응 없음 | 아무도 안 보는 설정 |
| **역(Reverse)** | 오히려 불만 | 만족 | 과한 알림·강제 튜토리얼 |

### 설문 방식 (기능마다 2문항 — 기능·역기능)
- **기능형(있을 때)**: "이 기능이 있으면 어떤가?" — {좋다 / 당연하다 / 상관없다 / 감수한다 / 싫다}
- **역기능형(없을 때)**: "이 기능이 없으면 어떤가?" — 동일 5택
- 두 답의 교차표로 카테고리 판정(Kano 평가표). 응답 30명+ 권장(확인 필요 — 표본 크기는 목적별 상이).

### 실전 함정
- **매력의 자연 하락(decay)**: 오늘의 delighter(예: 지문 로그인)는 몇 년 뒤 must-be가 된다 — 정기 재분류.
- Kano는 "무엇을 먼저"가 아니라 "무엇의 성격"을 알려준다 — RICE와 상호보완이지 대체 아님.

---

## 4. WSJF 실전 (SAFe, Reinertsen 큐잉이론 기반)

**WSJF = Cost of Delay ÷ Job Size**, CoD = 사업가치 + 시간민감도 + 리스크감소/기회창출.

### 산정표 (각 열 Fibonacci 1·2·3·5·8·13·20 상대 점수)
| 항목 | 사업가치 | 시간민감도 | 리스크/기회 | CoD(합) | JobSize | WSJF |
|---|---|---|---|---|---|---|
| A | 8 | 5 | 3 | 16 | 5 | **3.2** |
| B | 13 | 3 | 2 | 18 | 13 | **1.4** |
| C | 3 | 8 | 3 | 14 | 3 | **4.7** ← 먼저 |

핵심 통찰: **작고(JobSize↓) 지연비용 큰(CoD↑) 일부터.** C처럼 "빨리 되고 급한" 일이 A·B를 제친다 — 큐잉이론의 결론(짧은 작업 먼저 처리 시 총 지연비용 최소).

### 언제
의존성 많고 팀이 여럿인 대규모 백로그, Epic 시퀀싱. 작은 팀엔 과함 — RICE로 충분.

---

## 5. MoSCoW 실전 (Dai Clegg 1994, DSDM에 기증)

| 등급 | 의미 | 규칙 |
|---|---|---|
| **Must** | 없으면 릴리스 실패(법·안전·핵심가치) | 이번 릴리스에 반드시 |
| **Should** | 중요하나 없어도 릴리스 가능 | 여유 있으면 |
| **Could** | 있으면 좋음(nice-to-have) | 버퍼가 남으면 |
| **Won't (this time)** | 이번엔 명시적으로 안 함 | **범위 크리프 방어선** |

### DSDM 배분 규칙 (실무 핵심)
- **Must는 총 노력의 60% 이하**로 유지 — Must가 100%면 버퍼 0, 지연 시 전부 실패. (DSDM 권고: Must ≤ 60%, 나머지 40%가 안전마진.)
- "다 Must" 함정: 이해관계자는 전부 Must라 우긴다 → "이게 없으면 정말 못 내나? 우회책은?"으로 강등 압박.
- **Won't의 힘**: 명시적으로 "이번엔 안 함"을 적어야 나중에 "왜 안 했냐" 분쟁을 막는다 — PRD의 비목표(Non-goals)와 직결.

---

## 6. 제품 지표 트리 (North Star Framework — Amplitude/Sean Ellis)

```
[North Star Metric]  — 제품이 주는 핵심 가치를 대표하는 단 하나 (선행지표)
     예: "주간 활성 협업 문서 수" (Notion류)
   ├─ Input 1 (breadth 폭)   : 신규 활성 사용자 수
   ├─ Input 2 (depth 깊이)   : 사용자당 생성 문서 수
   ├─ Input 3 (frequency)    : 주간 방문 횟수
   └─ Input 4 (efficiency)   : 문서 생성까지 걸리는 시간
        └─ 실행지표(팀이 매일 움직임): 온보딩 완료율, 템플릿 사용률 …
```

### 좋은 North Star 3조건 (Amplitude Playbook)
1. **고객 가치 반영** — 매출이 아니라 고객이 얻는 가치(매출은 후행).
2. **비전·전략 표현** — 회사가 이기려는 방식을 담음.
3. **지속가능 성장의 선행지표** — 이게 오르면 사업 결과가 따라온다.

### 안티 North Star
- 매출·가입자 총수 같은 **후행/허영 지표**를 NSM으로 삼으면 안 됨(선행성 없음).
- NSM은 1개 — 여러 개면 집중이 깨진다.

### AARRR(해적 지표, Dave McClure 2007)로 퍼널 매핑
Acquisition(발견) → Activation(첫 가치경험) → Retention(재방문) → Referral(추천) → Revenue(매출). PM은 보통 **Activation·Retention**을 outcome으로 잡는다(가장 레버리지 큼). North Star는 이 퍼널의 어느 단계를 대표하는지로 검증.

---

## 7. 스코어링 워크숍 진행법 (합의 도출)

1. **후보 나열** — 문제(해법 아님) 단위로 카드화.
2. **Effort 먼저 팀 합의** — 테크리드 주도 T셔츠(S/M/L)→person-month 환산. PM 단독 추정 금지.
3. **Reach는 데이터로** — 회의 전 대시보드에서 미리 뽑아 옴(회의 중 추측 금지).
4. **Impact·Confidence는 개별 → 공개 → 토론** — planning poker식으로 각자 적고 동시 공개, 편차 큰 항목만 토론(HiPPO 편향 억제).
5. **권력자 요청도 같은 표에** — "대표님 요청"도 RICE 매겨 트레이드오프를 보이게(안티패턴: HiPPO).
6. **상위 N개만 커밋** — 나머지는 "지금 안 함"으로 명시(Won't).

---

## 8. 흔한 계산 실수 5가지
1. **Effort 단위 혼동** — 사람·일 vs 사람·개월 섞음. 팀 전체 통일.
2. **Confidence 100% 남발** — 데이터 없으면 100% 금지. 대부분 50~80%.
3. **Reach를 추측** — 측정 안 하고 "많을 듯"으로 큰 수. Confidence로 벌점 줘야 함.
4. **Impact를 매출로 착각** — Impact는 "1인당 지표 이동"이지 총매출 아님(총량은 Reach가 반영).
5. **점수 절대값 신봉** — RICE 6400이 "6400점짜리"가 아니라 "1667짜리보다 위"일 뿐. 순위만 본다.

---

## 9. 출처 (검증)
- **RICE**: Sean McBride, "RICE: Simple prioritization for product managers" (Intercom, 2018-01-05). https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/ (Impact 척도 3/2/1/0.5/0.25, Confidence 100/80/50%, Effort=person-months, "50% 이하=moonshot" 원안 확인)
- **Kano**: Noriaki Kano, 1984, Tokyo University of Science. 5카테고리·기능/역기능 2문항 설문. https://en.wikipedia.org/wiki/Kano_model · 실무 해설 https://www.productplan.com/glossary/kano-model
- **WSJF**: Scaled Agile Framework, "WSJF". https://framework.scaledagile.com/wsjf (CoD = 사업가치+시간민감도+리스크/기회, ÷JobSize, Fibonacci) — Don Reinertsen 큐잉이론 계보.
- **MoSCoW**: Dai Clegg(Oracle, 1994), DSDM Consortium 기증. Must≤60% 배분은 DSDM 권고. https://en.wikipedia.org/wiki/MoSCoW_method · https://www.productplan.com/glossary/moscow-prioritization
- **North Star Framework**: Sean Ellis 명명, Amplitude *North Star Playbook*(output=NSM, input metrics=levers, breadth/depth/frequency/efficiency). https://amplitude.com/blog/pirate-metrics-framework · https://www.productplan.com/learn/north-star-metrics
- **AARRR**: Dave McClure, "Startup Metrics for Pirates" (2007). Acquisition·Activation·Retention·Referral·Revenue. https://www.productplan.com/glossary/aarrr-framework
