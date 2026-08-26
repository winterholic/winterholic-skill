# biz-business-ops — 프레임 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 웹 검증(2026-07-01 확장). 1단계 참조. 실무 절차는 `playbook.md`.

## 1. 정전 소스
- **Eliyahu Goldratt & Jeff Cox, *The Goal*(1984)** — TOC: 시스템 산출은 단일 제약(병목)이 결정; 비병목 국소 최적화는 무의미. https://www.tocinstitute.org/the-goal-summary.html
- **Womack & Jones, *Lean Thinking*(1996)** — "value stream" 용어 + 5원칙(value/value stream/flow/pull/perfection).
- **Rother & Shook, *Learning to See*(Lean Enterprise Institute, 1998/99)** — VSM 매핑 기법(현재상태도→미래상태도)의 정본. https://www.lean.org/store/learning-to-see/

## 2. 프레임
- **TOC 5 Focusing Steps**(Goldratt): IDENTIFY→EXPLOIT→SUBORDINATE→ELEVATE→**PREVENT INERTIA(1로 복귀)**. https://www.tocinstitute.org/five-focusing-steps.html
  - EXPLOIT=돈 안 들이고 병목 낭비 제거, ELEVATE=투자로 병목 향상. 순서 중요(ELEVATE 먼저 = 낭비 위에 돈 붓기).
- ⚠️ **VSM 출처 교정**: "value stream" 용어=Womack&Jones(1996)지만 **매핑 기법 자체는 Rother & Shook, *Learning to See*(1998/99)**. 뿌리는 Toyota MIFA(Material and Information Flow Analysis)·Ford 흐름생산. 핵심 지표=Process Cycle Efficiency(부가가치시간/총리드타임), 대개 5~15%.
- **SIPOC**(Suppliers-Inputs-Process-Outputs-Customers): Six Sigma DMAIC의 **Define 단계** 프로세스 맵 도구. 프로세스를 5~7 상위 단계로만, 경계·이해관계자 합의용. VSM(정량 진단)과 목적 다름. https://en.wikipedia.org/wiki/SIPOC
- RevOps: 단일 창안자 없는 업계 기능. 세일즈·마케팅·CS를 하나의 데이터·프로세스·목표로 정렬. ✅ Gartner 예측 1차 확정: **"75% of the highest growth companies will deploy a RevOps model by 2025"**(Gartner 공식 보도자료 2021-05-17). https://www.gartner.com/en/newsroom/press-releases/2021-05-17-gartner-predicts-75--of-the-highest-growth-companies- (※ 원문 목표연도는 **2025**, 일부 후속 자료에서 2026으로 인용 — 1차는 2025.)
  - 리드-투-캐시 핸드오프 단계: Lead→MQL→SAL(Sales Accepted)→SQL→Opportunity→Closed-Won→온보딩→갱신. 각 핸드오프에 공통 정의+SLA+구조화 노트. (실무 통설, 벤더 문서 다수 일치)
- **SLA**(팀 간): 응답시간·품질기준의 문서화된 상호 약속. speed-to-lead(자동 라우팅+acceptance timer+미준수 재배정) + 자격정의 합의 + 구조화 인수인계 노트. (RevOps 실무 통설 — 특정 1차 출처 아닌 업계 합의)

## 3. 교정
- Goldratt 오독①: "모든 단계 최적화" 정반대(국소 최적의 합 ≠ 전역 최적).
- 오독②: TOC는 병목 찾기로 끝나지 않음(step 5, **제약은 이동**). 병목 풀리면 다른 곳이 새 병목 → 1단계 복귀. 프로세스 성역화(관성)가 함정.
- ⚠️ **"Single source of truth=단일 DB" 오류** — SSOT는 **거버넌스 원칙**(지표별 단일 권위 정의 + 오너 + 소스 명시)이지 물리적 단일 시스템 아님. 데이터가 흩어져 있어도 "공식 값·공식 정의"가 하나면 성립.
- ⚠️ 지표 정의를 결과에 맞춰 사후 조정 = **분식**(무결성 게이트 위반). 정의 변경은 합의+이력으로만, 시계열 단절 명시.
- ⚠️ 대기시간(queue) 무시 함정 — 핸드오프 사이 대기시간이 처리시간보다 훨씬 큰 낭비인 경우 대부분. VSM이 이를 드러냄.

## 4. 출처
- Goldratt & Cox, *The Goal*(1984) · TOC Institute(5 Focusing Steps). · Womack & Jones, *Lean Thinking*(1996). · **Rother & Shook, *Learning to See*(1998, Lean Enterprise Institute)**. · SIPOC(Six Sigma DMAIC Define, Wikipedia/6sigma.us). · RevOps: Gartner 보도자료(2021-05-17, "75% by 2025"). · SLA/lead-to-cash: RevOps 업계 통설(1차 단일 출처 아님, "확인 필요"로 취급).
