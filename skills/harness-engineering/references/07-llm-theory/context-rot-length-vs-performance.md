---
name: context-rot-length-vs-performance
topic: 컨텍스트가 길수록 LLM 성능이 떨어진다 — "많이 넣을수록 좋다"는 거짓
category: 07-llm-theory
added: 2026-05-27
updated: 2026-05-28
source: https://www.trychroma.com/research/context-rot · https://arxiv.org/abs/2307.03172 · https://arxiv.org/abs/2404.06654 · https://arxiv.org/abs/2502.05167 · https://arxiv.org/abs/2311.11829 · https://arxiv.org/abs/2310.11324 · LLMLingua (EMNLP 2023)
tags: [context-rot, long-context, lost-in-the-middle, effective-context-length, prompt-design, attention-budget, brittleness, prompt-compression]
status: partial
verification_note: Chroma 본문·Lost-in-the-Middle abstract는 직접 fetch로 verbatim 확정(2026-05-27). RULER·NoLiMa 수치는 WebSearch 요약 기반이라 원문 full 직접 확인 필요. 2026-05-28 보강 — vault `sources/papers/`의 lost-in-the-middle·system-2-attention·prompt-format-sensitivity(Sclar) + `sources/articles/prompt-compression-llmlingua` + `wiki/prompt-engineering/prompt-brittleness-empirical`(status: review) cross-link. 수치를 사용자에게 단정 인용하기 전 arXiv 원문 대조 권장.
---

# Context Rot — 컨텍스트 길이 vs 성능

## 핵심 한 줄
**컨텍스트가 길어지면 윈도우가 꽉 차기 한참 전부터 LLM 성능이 떨어진다.** "context window가 200K니까 다 넣어도 된다"는 흔한 가정은 거짓 — 모델은 토큰을 균일하게 처리하지 않는다. 따라서 프롬프트·FC 설계의 default는 "최대한 넣기"가 아니라 **고신호 토큰만 추려 넣기**다.

## 본문

### 1. 무엇이 틀린 통념인가
- 통념: "context window 안에만 들어가면 위치·분량은 상관없다. 많이 넣을수록 모델이 더 잘 안다."
- 실증: **윈도우 한계 근처가 아니어도** 입력이 길어지는 것만으로 성능이 내려간다. Chroma는 이를 **"context rot"** 로 명명.
- Chroma verbatim: *"the model should handle the 10,000th token just as reliably as the 100th. However, in practice, this assumption does not hold."* → 이 가정이 깨진다는 것을 18개 frontier 모델(GPT-4.1·Claude 4·Gemini 2.5·Qwen3 포함)에서 입증.

### 2. 근거 (공신력순)

| 자료 | 출처 | 핵심 발견 | 신뢰도 |
|------|------|----------|--------|
| **Context Rot** | Chroma 2025-07 (Hong·Troynikov·Huber) | task 복잡도 고정 + 입력 길이만 변화시켰을 때도 18개 모델 전부 성능 하락. "non-uniform" | 본문 직접 확인 ✅ |
| **Lost in the Middle** | Liu et al., TACL 2024 (Stanford) | U자형 곡선: 관련 정보가 처음/끝이면 성능 최고, 중간이면 급락 | abstract 직접 확인 ✅ |
| **RULER** | NVIDIA, arXiv 2404.06654 | "effective length"(≥85% 유지 최대 길이) ≪ "claimed length". 32K 주장 모델 중 절반만 32K에서 통과 | 검색 요약 — 원문 확인 필요 |
| **NoLiMa** | Adobe Research, ICML 2025 | 어휘 중첩 제거 시 32K에서 다수 모델이 baseline의 50% 미만. GPT-4o 99.3%→69.7% | 검색 요약 — 원문 확인 필요 |

→ 서로 다른 4개 팀이 **다른 태스크·다른 방법론으로 같은 방향의 결과**에 도달. 단일 보고서의 우연이 아니라 robust한 현상.

### 2-1. 기제 — 왜 그런가 (System 2 Attention)
Weston & Sukhbaatar (Meta AI, arXiv 2311.11829, 2023) — *"Soft attention in Transformer-based Large Language Models (LLMs) is susceptible to incorporating irrelevant information from the context into its latent representations, which adversely affects next token generations."* (verbatim)
- 즉 transformer의 soft attention은 무관한 토큰까지 잠재 표현에 섞는 **구조적 약점**이 있음. context rot의 distractor 효과(Chroma)·U자 곡선(Liu) 모두 이 기제의 표면 증상으로 해석 가능.
- 처방: **S2A** — LLM이 자신의 추론 능력으로 "무엇에 주목할지" 결정해 컨텍스트를 관련 부분만 남도록 **재생성**한 뒤 다시 attention. QA·수학·longform에서 사실성↑·sycophancy↓.
- 함의: 모델 안에서 자동 처리되길 기대하지 말고 **프롬프트 엔지니어가 먼저 정제**해 넣어야 한다는 게 실무적 결론.

### 2-2. 더 큰 그림 — brittleness 가족
context rot은 LLM brittleness의 한 얼굴. vault `wiki/prompt-engineering/prompt-brittleness-empirical.md` (status: review)가 같은 가족 4편을 묶음:
- **Lost in the Middle**(Liu 2023): 위치
- **Calibrate Before Use**(Zhao 2021): few-shot 사전편향
- **Fantastically Ordered Prompts**(Lu 2021): 예시 순서만으로 SOTA~랜덤 수준 출렁
- **Prompt Format Sensitivity**(Sclar et al., arXiv 2310.11324, 2023): 의미 보존하는 포맷 차이(구분자·대소문자 등)만으로 LLaMA-2-13B 정확도 **최대 76점** 변동. 모델 크기 증가·instruction tuning으로도 안 사라짐. → "단일 포맷 단일 점수" 평가의 방법론적 위험.

→ Chroma의 "구조적 haystack이 셔플본보다 더 안 좋다"(섹션 3-3)는 이 포맷·구조 민감도 가족과 같은 줄기.

### 3. 성능을 떨어뜨리는 요인 (Chroma 격리 실험)
입력 길이 자체 외에, 같은 길이라도 다음이 성능을 더 깎는다:
1. **needle-question 유사도 낮음** — 질문과 정답의 어휘/의미 겹침이 적을수록 길이에 따른 하락이 가팔라짐 (NoLiMa와 일치). 현실에선 정답이 질문과 똑같은 표현으로 들어있는 경우가 드물다 → 현실 난이도가 더 높음.
2. **distractor(헷갈리는 유사 정보)** — *"Even a single distractor reduces performance"*, 4개면 더 악화. 길수록 영향 증폭.
3. **haystack 구조** — 의외로 논리적으로 잘 구성된 문서가 셔플된 것보다 성능이 **더 낮았다** (attention이 구조에 영향받는다는 정황).

### 4. position 효과 — 두 자료가 갈리는 지점 (주의)
- Lost-in-the-Middle: 정보 **위치**가 핵심 변수 (U자 곡선).
- Chroma의 특정 NIAH 태스크: *"Testing across 11 needle positions, we find no notable variation"* — 위치 효과 안 보임.
- → 모순이 아니라 **태스크 의존적**. "중간에 묻으면 무조건 못 찾는다"고 단정하지 말 것. 위치 민감도는 태스크·모델마다 다르다. 안전한 일반 명제는 "위치 효과가 있을 수 있으니 핵심 정보는 앞/뒤에 배치하는 게 보수적으로 안전"까지.

### 5. 본 사용자 작업에의 함의

**컨텍스트 크기 트레이드오프 판단** (직접 적용):
- "일단 다 넣자"가 아니라 **focused input**이 거의 항상 이긴다. Chroma LongMemEval: focused(~300 tok) > full(~113k tok), 전 모델 공통.
- 판단 기준: 토큰을 추가할 때 "이게 신호인가 noise인가". noise면 길이만 늘리고 retrieval 부담을 얹어 순수 reasoning을 방해한다.
- "effective length ≪ claimed length"(RULER). 광고된 윈도우를 신뢰 상한으로 쓰지 말 것.

**FC 프롬프트 설계** (간접):
- 툴 description·예시를 무한정 늘리면 그 자체가 context rot 유발. 툴이 많아질수록 distractor처럼 작동 → 다음 reference [[function-calling-prompt-design]]에서 별도로 다룸.

**프롬프트 완성도 평가** (간접):
- eval 시 입력 길이를 변수로 분리해야 함 (Chroma 방법론 차용): 길이를 늘렸을 때 성능 하락이 "문제가 어려워서"인지 "길어서"인지 분리. 길이 sweep을 eval 축에 포함.

### 6. 실무 룰 (보수적)
- 컨텍스트는 **추가**가 아니라 **큐레이션**. 고신호 토큰만.
- 긴 입력이 불가피하면 핵심 정보를 앞/뒤로, 중간에 묻지 않기.
- distractor(유사하지만 틀린 정보)를 적극적으로 제거. 한 개도 비싸다 (Chroma: "Even a single distractor reduces performance").
- 광고 윈도우(1M 등)를 작업 상한으로 신뢰하지 말고, 해당 모델의 effective length를 의심.
- **자동 처리 기대 금지**: soft attention은 무관 정보를 잠재표현에 섞는다(S2A). 모델이 알아서 무시할 거란 가정 ❌ → 프롬프트 단계에서 정제.
- **평가 방법론**: 단일 포맷·단일 순서로 측정한 점수를 과신 ❌. Sclar는 포맷만으로 ±76점. Chroma 방법론처럼 길이를 변수로 분리하고 포맷·순서 변형도 sweep.
- 단, 위 수치(32K에서 50% 등)는 모델·벤치마크 의존 — 사용자에게 단정 인용 전 원문 대조.

### 7. 구체적 remediation — Prompt Compression
LLMLingua (Microsoft Research, EMNLP 2023): 작은 LM으로 토큰별 perplexity를 스코어링, 정보량 낮은 토큰을 제거. 3-component(budget controller·iterative compression·작은 LM).
- 보고된 수치: **최대 20× 압축, 정확도 손실 1.5%.**
- 함의: "긴 컨텍스트의 noise가 신호를 가린다"는 진단과 정합 — 압축이 토큰·비용을 줄이면서 결과도 개선되는 경우가 있다 (입력이 짧아질수록 context rot이 약해지므로).
- LongLLMLingua는 long-context 시나리오 확장. RAG 프레임워크(LlamaIndex)에 통합됨.
- 본 reference의 큐레이션 룰을 자동화하고 싶을 때의 진입점.

## 관련 자료
- [[../03-patterns/context-reset-vs-compaction]] — 길어진 컨텍스트를 운영으로 어떻게 끊을지 (reset/handoff)
- [[function-calling-prompt-design]] — (예정) 툴 정의 비대화도 context rot의 한 형태
- [[context-engineering-principles]] — (예정) attention budget·고신호 토큰 큐레이션 원리
- [[../99-sources/context-rot-chroma-2025-07-14]] — verbatim 인용 백업

### Vault cross-link (Obsidian)
- `sources/papers/lost-in-the-middle-liu-2023.md` — Liu 2023 abstract + 정리
- `sources/papers/system-2-attention-weston-2023.md` — 기제(soft attention의 무관 정보 흡수)
- `sources/papers/prompt-format-sensitivity-sclar-2023.md` — 포맷 민감도 ±76점 (Sclar 2023)
- `sources/papers/calibrate-before-use-zhao-2021.md` · `fantastically-ordered-prompts-lu-2021.md` — brittleness 가족
- `sources/articles/prompt-compression-llmlingua.md` — LLMLingua 20× 압축
- `wiki/prompt-engineering/prompt-brittleness-empirical.md` (status: review, updated 2026-05-27) — 상위 umbrella 정리본
- `sources/papers/prompt-report-survey-2024.md` — Schulhoff 2024 종합 서베이(58기법 taxonomy)

## 출처
- **Chroma (본문 직접 확인 2026-05-27)**: https://www.trychroma.com/research/context-rot — "context rot" 용어 출처, 18개 모델, 격리 실험
- **Liu et al. TACL 2024 (abstract 직접 확인)**: https://arxiv.org/abs/2307.03172 — U자형 곡선
- **NVIDIA RULER (검색 요약, 원문 확인 필요)**: https://arxiv.org/abs/2404.06654 — effective vs claimed length
- **Adobe NoLiMa, ICML 2025 (검색 요약, 원문 확인 필요)**: https://arxiv.org/abs/2502.05167 — 비-어휘 매칭 시 급락
- **Weston & Sukhbaatar, arXiv 2311.11829 (vault 정리본 확인 2026-05-28)**: https://arxiv.org/abs/2311.11829 — System 2 Attention, soft attention의 구조적 약점
- **Sclar et al., arXiv 2310.11324 (vault 정리본 확인 2026-05-28)**: https://arxiv.org/abs/2310.11324 — 포맷 민감도 정량
- **Jiang et al. LLMLingua, EMNLP 2023 (vault 정리본 확인 2026-05-28)**: 20× 압축 / 1.5% 손실
