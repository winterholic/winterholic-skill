# llm-product-checklist — LLM eval·환각 UX·HITL·거버넌스·비용/지연 실무판

> AI PM이 LLM 기능을 데모에서 제품으로 넘길 때 통과시켜야 할 실무 체크리스트. evidence.md의 검증 사실(Air Canada CAD$650.88·NIST AI 600-1 12범주·ISO 42001·PAIR≠MS HAX·Ji 환각분류) 위에 "그래서 어떻게"를 얹는다.
> **부패 빠름**: 모델 ID·실단가·파라미터·정책은 여기 하드코딩하지 말고 항상 → claude-api / 공식 문서 최신 확인.

---

## 1. 유스케이스 위험 분류 (자동화 범위의 출발점)

먼저 **가역성 × 피해 크기**로 분류한다 — 이게 HITL 수준과 자동화 범위를 정한다.

| 가역성\피해 | 저피해 | 고피해 |
|---|---|---|
| **가역(되돌림 쉬움)** | 완전 자동 OK (예: 요약 초안, 태그 제안) | 자동 + 되돌리기·확인 UX (예: 대량 분류) |
| **비가역(되돌림 어려움)** | 자동 + 로그 (예: 알림 발송) | **HITL 필수** — AI는 제안, 인간이 승인 (예: 환불·삭제·계약·의료/법률/금융 조언) |

> 원칙: **비가역·고피해 행동을 AI 단독 실행 금지.** 확률적 시스템에 비가역 권한을 주면 드물지만 비싼 사고가 난다(Air Canada: 챗봇이 지어낸 정책에 회사 책임 인정, CAD$650.88, evidence §3).

---

## 2. eval 설계 (Husain "evals not vibes", 검증)

### 2-1. eval 3레벨 (섞어 쓴다)
| 레벨 | 방법 | 언제 | 비용 |
|---|---|---|---|
| **L1 단위/assertion** | 결정적 규칙(형식·정규식·금지어·JSON 스키마·필수 필드) | 항상, CI에 | 매우 쌈 |
| **L2 LLM-as-judge** | LLM으로 개방형 출력 채점(Zheng et al. NeurIPS 2023) | 정답 애매한 품질 | 중간 |
| **L3 인간 평가** | 골든셋 소량, 전문가 라벨 | 고위험·미묘한 품질 | 비쌈 |

### 2-2. eval셋 구성
- **대표 입력**(happy path) + **엣지**(빈값·초장문·다국어·모호) + **적대적**(프롬프트 인젝션·탈옥·유도) — 세 종류 모두.
- **프로덕션 실패 로그를 환류** — 실제로 틀린 케이스를 eval셋에 추가(드리프트 대응, 안티패턴 6).
- **LLM-judge는 먼저 인간 라벨과 대조 검증** 후 신뢰(judge 자기선호·편향 주의).

### 2-3. 회귀 게이트
- 프롬프트·모델·RAG 변경 **전후 동일 eval셋 점수 비교**. 합격선 미달이면 배포 보류. "느낌상 좋아졌다"로 변경 금지(안티패턴 2).

---

## 3. 환각 UX — "막기"가 아니라 "감싸기"

현 LLM은 환각(NIST 용어 confabulation)을 0으로 못 만든다. 비용은 "틀림"이 아니라 **"틀린 걸 사용자가 믿고 행동"**할 때 발생. 그러니 UX로 방어한다.

### 3-1. 환각 방어 UX 패턴
- **출처 표시(citation/grounding)** — 근거 문서·링크를 붙여 사용자가 검증 가능하게(RAG면 필수).
- **확신도/불확실성 신호** — 자신 없을 때 "확실치 않습니다", 답 대신 "확인이 필요합니다".
- **검증 유도** — 고위험 답변에 "원문을 확인하세요" + 원문 경로.
- **되돌리기(undo)·미리보기** — 행동 전 사용자 확인, 실행 후 취소 가능.
- **우아한 실패(graceful failure)** — 모르면 지어내지 말고 "모릅니다"·상담사 연결(PAIR Guidebook 원칙).
- **범위 제한** — 답할 수 있는 영역을 명시, 벗어나면 거절.

### 3-2. 정전 UX 소스 (혼동 금지)
- **Google PAIR, People + AI Guidebook** — UX 패턴(멘탈모델·설명가능성·피드백/통제·우아한 실패). https://pair.withgoogle.com/guidebook/
- **Microsoft, Guidelines for Human-AI Interaction**(Amershi et al., CHI 2019) — 검증된 **18개 가이드라인** + HAX Toolkit. https://www.microsoft.com/en-us/haxtoolkit/
> PAIR(Google, UX 가이드북) ≠ MS HAX(18 가이드라인) — 별개.

### 3-3. 프롬프트 인젝션 (보안 UX)
- 사용자·외부 콘텐츠가 시스템 지시를 덮어쓸 수 있음(OWASP LLM01). 대표 사고: Chevrolet 딜러 챗봇이 "$1에 판다"에 동의(evidence §3).
- 방어: 신뢰경계 분리·출력 검증·권한 최소화·행동 게이트(비가역 행동은 §1대로 HITL). 구현 상세 → dev-llm-engineering.

---

## 4. Human-in-the-Loop (HITL) 설계

- **HITL 배치 위치**: (a) 사전 승인(행동 전 인간 확인) (b) 사후 검토(샘플링 감사) (c) 에스컬레이션(AI가 자신 없으면 인간에게).
- **위험도별 차등**: 저위험·가역은 자동, 고위험·비가역은 사전 승인. 전부 HITL이면 자동화 이점 소멸, 전부 자동이면 사고 — 위험 매트릭스(§1)로 배분.
- **인간 부담 관리**: 승인 요청이 너무 많으면 rubber-stamping(무비판 승인)이 발생 → 진짜 위험한 것만 올리고 나머지는 자동+로그.

---

## 5. 비용·지연 예산 (제품 지표)

### 5-1. 측정
- **요청당 비용** = 입력토큰×입력단가 + 출력토큰×출력단가 (+RAG 검색/임베딩, +체인/에이전트 호출 배수).
- **지연**: TTFT(첫 토큰, 스트리밍 체감) · 총 지연은 **p95/p99**로(평균 금지 — 꼬리가 UX를 침).

### 5-2. 레버
모델 라우팅(쉬운 요청→작은 모델) · 프롬프트/컨텍스트 캐싱 · 응답 캐시 · 출력 토큰 상한 · 배치 · RAG 청크 최적화 · 스트리밍으로 체감 지연↓ · 작은 모델 폴백.
> 실단가·모델 ID는 → claude-api. 여기 숫자 박지 말 것(부패 빠름).

---

## 6. 거버넌스 매핑 (규제·조달 대응, 검증)

- **NIST AI RMF 1.0 + AI 600-1(GenAI Profile, 2024-07-26 최종)**: 자발적 프레임워크. GenAI **12 리스크 범주**(환각·데이터프라이버시·정보무결성·정보보안·IP·편향 등)에 GOVERN/MAP/MEASURE/MANAGE 액션. 제품 리스크 등록부의 체크리스트로 사용.
- **ISO/IEC 42001:2023**: 인증 가능한 AI 경영시스템(AIMS). Annex A 통제 + Statement of Applicability. 엔터프라이즈 조달·인증 요구 시.
- **조합**: RMF(무엇을 관리하나) + ISO 42001(조직 시스템으로 운용·인증) — 대체 아닌 상보.
- **EU AI Act** 등 지역 규제는 고위험 분류·투명성 의무 부과(빠르게 변함 — 최신 확인). 프라이버시·데이터 동의 → dev-privacy-compliance.

---

## 7. 성공지표 (출시 후)
- **과업 성공률**(task success) · **수용률**(AI 제안을 사용자가 채택한 비율) · **교정률**(사용자가 고친 비율 — 높으면 품질 문제) · **에스컬레이션율**(자동해결 실패) · **CSAT/재문의율** · **비용/지연 실측**.
> 데모 성공률 ≠ 실사용 성공률(안티패턴 1). 롱테일·적대 입력에서 무너진다.

---

## 8. AI 기능 출시 게이트 (배포 전 최종 체크)
- [ ] 유스케이스 위험 분류 완료(가역성×피해) → 자동화 범위·HITL 정해짐
- [ ] eval셋(대표+엣지+적대) 구축, 합격선 정의, 회귀 게이트 통과
- [ ] 환각 UX(출처·확신도·검증유도·undo·우아한 실패) 적용
- [ ] 프롬프트 인젝션·권한 최소화 검토
- [ ] 비용/지연 예산(요청당 비용, p95) 목표 내
- [ ] 고위험 영역 면책·인간검토·에스컬레이션 경로
- [ ] 성공지표·피드백 로그 → eval 환류 파이프라인
- [ ] (해당 시) NIST 12범주·ISO 42001 리스크 등록부 매핑

---

## 출처
- Husain, "Your AI Product Needs Evals"(2024) https://hamel.dev/blog/posts/evals/ · LLM-judge https://hamel.dev/blog/posts/llm-judge/
- Yan, "Patterns for Building LLM-based Systems"(2023) https://eugeneyan.com/writing/llm-patterns/ · "What We Learned from a Year of Building with LLMs"(O'Reilly 2024) https://www.oreilly.com/radar/what-we-learned-from-a-year-of-building-with-llms-part-i/
- Google PAIR https://pair.withgoogle.com/guidebook/ · MS HAX(Amershi et al. CHI 2019) https://www.microsoft.com/en-us/haxtoolkit/
- NIST AI RMF/600-1 https://www.nist.gov/itl/ai-risk-management-framework · ISO 42001 https://www.iso.org/standard/81230.html
- LLM-judge Zheng et al. NeurIPS 2023 arXiv:2306.05685 · 환각 Ji et al. ACM CSUR 2023 arXiv:2202.03629
- Air Canada 2024 BCCRT 149 https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html · Chevrolet 챗봇 https://incidentdatabase.ai/cite/622/
- Anthropic evals https://docs.anthropic.com/en/docs/test-and-evaluate/develop-tests · agents https://www.anthropic.com/engineering/building-effective-agents
> 모델·가격·정책은 → claude-api 최신이 항상 우선.
