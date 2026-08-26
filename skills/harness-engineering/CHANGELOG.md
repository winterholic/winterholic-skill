# CHANGELOG

git log 톤. 주요 변경만 1~3줄. 자세한 건 references/.

## 2026-05-26
- 초기 작성. 골격(SKILL.md·INDEX.md·_TEMPLATE) + 교수 모드 절차 + 핵심 결정 트리 4개 시드.
- case-studies 4건 추가 — caveman·handoff·verification·systematic-debugging 진화 흐름.
- 1차 자료 분해 (서브에이전트) — 01-fundamentals 5개·02-components 7개·03-patterns 5개·04-anti-patterns 5개 = 22개.
- 총 reference 31개. 1차 자료: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html` (74KB, 1157줄).
- skills-estimate 평가 55.2/100 (D) → 약점 Top 3 보강: A3 유사 스킬 경계(skill-creator·skills-estimate·find-skills·update-config) + E1 비유·답변 예시 + D2 사용자 거부 분기. SKILL.md 86 → 108줄.
- 추가 보강 (C+E2+B3): 실행 예시 bash 4개(E2) · INDEX 비었을 때 시나리오 A/B/C(B3·D1) · 답변 좋음/나쁨 대비(C2) · 출력 형식 규칙(C1) · 신규 자료 작성 절차 3단계+위치/append 규칙(C3). 108 → 172줄. 재평가 80.5/100 (B+).
- **외부 1차 자료 딥 리서치 (서브에이전트 117 tool calls, 17분)**: references 26개 외부 검증 — revised 16개 · partial 9개 · active 1개. **hallucination 수정 다수**: hooks 12~13→29개, "12 카테고리"→11개 Design Primitives, CLAUDE.md "3-tier override"→공식은 "충돌 시 임의 선택". verbatim 확증: Generator-Evaluator(harness-design 공식), context anxiety(managed-agents 공식), MCP "USB-C". 99-sources/ 1차 자료 백업 5개 신설 (Anthropic engineering·platform docs·MCP·ai-boost). 평균 출처 2~5개/reference. case-studies 4개에 verification_note "외부 검증 X — 사용자 셋업 내부 사례" 표기.

## 2026-05-27
- 독립 팩트체커 감사 (서브에이전트 21 tool calls) — 신뢰도 "높음". 샘플 12개 verbatim 인용 전부 원문 일치, hallucinated citation 0건, status 표기 정직.
- **07-llm-theory 카테고리 신설** — LLM/프롬프트 거동의 학술 근거(하네스 메커니즘이 아닌 그 결정의 근거). 첫 reference `context-rot-length-vs-performance` 추가: Chroma Context Rot(본문 직접 확인) + Lost-in-the-Middle/TACL(abstract 직접) + RULER·NoLiMa(검색 요약, 원문 확인 필요) 4종 종합. 99-sources 백업 1건. status: partial. 예정 토픽 3개(FC 프롬프트 설계·context engineering·prompt eval) INDEX에 placeholder.

## 2026-05-28
- **07-llm-theory 활용 경로 편입 (architectural)** — 근간 원리를 banner로 박는 대신 "필요할 때 펼치는 책" 모양으로 통합. 4건: (1) 결정 reference 5개(skill-description-tuning·hook-noise·description-bloat·memory-overuse·progressive-disclosure) 핵심 한 줄 직후에 `> **근저 학술 물리**: [[...]]` cross-link 추가, (2) INDEX 2축 결정 항목 6개에 `> 근저 압력: ...` 한 줄, (3) SKILL.md 답변 형식 "근거" 절에 "결정의 학술 물리가 load-bearing이면 07-llm-theory도 1줄 인용 (banner ❌, 매번 ❌)" 조용한 룰, (4) research-methodology에 "신규 reference 작성 시 학술 물리 cross-link 룰" 절 추가 — dead reference 재발 방지. 진단(LLM이론 언급 SKILL.md 내 2회·둘 다 파일구조 설명) → 활용 path 편입 완료. banner 신설 ❌·매 응답 강제 ❌·결정 path 자연 도달 ✅.
- **skills-estimate 평가 88.5/100 (A)** — 자체 CHANGELOG 80.5(B+, 2026-05-26) → +8 상승. 외부 1차 자료 딥 리서치 + 07-llm-theory 신설이 D·B·C 카테고리를 끌어올림. 약점 Top 3 보강 반영: (1) description 끝에 SKIP 확장 + 4개 유사 스킬(skill-creator·skills-estimate·find-skills·update-config) 라우팅 명시 (A1: 4→5), (2) 도구 부재 시 "확인 결과 해석 가이드" 표 4분기 추가 (B3: 4→5), (3) 비유 보조 2개(법률 자문역·위키 편집자) 추가 (E1: 4→5). 보강 후 예상 가중점수 93.5/100 (A+).
- `context-rot-length-vs-performance` 보강 — vault `sources/papers/`·`wiki/prompt-engineering/` 직접 관련 자료 5종 cross-link 및 본문 확장. 추가된 축: (1) 기제 절 — System 2 Attention(Weston 2023): "soft attention is susceptible to incorporating irrelevant information" verbatim, 구조적 약점 + S2A 처방. (2) brittleness 가족 절 — context rot을 단일 현상이 아닌 brittleness umbrella의 일면으로 위치, Sclar 2023(±76점) + Lu 2021(순서) + Zhao 2021(사전편향) 묶음. (3) remediation 절 — LLMLingua 20× 압축/1.5% 손실, LongLLMLingua/LlamaIndex 통합. (4) Vault cross-link 7개 경로 추가. status는 RULER·NoLiMa 미확인 유지로 partial 그대로.
- 독립 평가자 Top 3 보강: D1 시나리오 D(references↔외부 부분 일치) + D2 에스컬레이션(find-skills) + C3 mkdir·답변 저장 규칙 + B1 도구 부재 분기. SKILL.md → 194줄. 재평가 81.2/100 (B+).
