---
name: context-rot-chroma-2025-07-14
topic: 컨텍스트 길이 증가 → LLM 성능 저하 실증 (Chroma 보고서 + 학술 벤치마크 4종) 1차 자료 백업
category: 99-sources
added: 2026-05-27
source: https://www.trychroma.com/research/context-rot · https://arxiv.org/abs/2307.03172 · https://arxiv.org/abs/2404.06654 · https://arxiv.org/abs/2502.05167
tags: [context-rot, long-context, lost-in-the-middle, RULER, NoLiMa, verbatim-backup]
status: active
---

# 1차 자료 백업 — Context Rot / Long-Context 성능 저하

`07-llm-theory/context-rot-length-vs-performance` 의 출처 verbatim 백업. 사이트가 사라져도 본 스킬 안에서 추적 가능.

---

## 1. Chroma — "Context Rot: How Increasing Input Tokens Impacts LLM Performance"

- **저자**: Kelly Hong, Anton Troynikov, Jeff Huber
- **발행**: 2025-07-14, Chroma Technical Report
- **URL**: https://www.trychroma.com/research/context-rot · 코드: https://github.com/chroma-core/context-rot
- **신뢰도**: 본문 직접 fetch (web-browse, 2026-05-27) — verbatim 확정

### Verbatim 인용 (본문에서 직접 추출)

> "Large Language Models (LLMs) are typically presumed to process context uniformly—that is, the model should handle the 10,000th token just as reliably as the 100th. However, in practice, this assumption does not hold. We observe that model performance varies significantly as input length changes, even on simple tasks."

> "In this report, we evaluate 18 LLMs, including the state-of-the-art GPT-4.1, Claude 4, Gemini 2.5, and Qwen3 models. Our results reveal that models do not use their context uniformly; instead, their performance grows increasingly unreliable as input length grows."

> "We demonstrate that even under these minimal conditions, model performance degrades as input length increases, often in surprising and non-uniform ways. Real-world applications typically involve much greater complexity, implying that the influence of input length may be even more pronounced in practice."

방법론 (input length를 유일 변수로 격리):
> "our experiments hold task complexity constant while varying only the input length—allowing us to directly measure the effect of input length alone."

핵심 결과 4개 (본문 요약 verbatim):
> "Across all experiments, model performance consistently degrades with increasing input length."
> "Lower similarity needle-question pairs increases the rate of performance degradation."
> "Distractors have non-uniform impact on model performance... We see this impact more prominently as input length increases."
> "Needle-haystack similarity does not have a uniform effect on model performance."

추가 발견:
> "Even a single distractor reduces performance relative to the baseline (needle only), and adding four distractors compounds this degradation further."
> "Surprisingly, we find that structural coherence consistently hurts model performance." (= 논리적으로 잘 구성된 haystack보다 셔플된 haystack에서 성능이 더 높음)
> "Testing across 11 needle positions, we find no notable variation in performance for this specific NIAH task." (← position 효과는 이 특정 태스크에선 안 보였음. Lost-in-the-Middle의 U자 곡선과 결이 다른 부분 — 태스크 의존적)

LongMemEval (현실적 세팅):
> "We verify that the models are highly capable of succeeding on the focused inputs, then observe consistent performance degradation with the full inputs."
> Focused prompt ~300 tokens vs Full prompt ~113k tokens. 전 모델에서 focused > full.

---

## 2. Liu et al. — "Lost in the Middle: How Language Models Use Long Contexts"

- **저자**: Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, Percy Liang
- **발행**: TACL 2024, Vol.12 pp.157-173 (arXiv 2307.03172, 2023)
- **URL**: https://arxiv.org/abs/2307.03172 · https://aclanthology.org/2024.tacl-1.9/
- **신뢰도**: abstract 직접 fetch (WebFetch, 2026-05-27) — verbatim 확정

### Abstract verbatim

> "While recent language models have the ability to take long contexts as input, relatively little is known about how well they use longer context. We analyze the performance of language models on two tasks that require identifying relevant information in their input contexts: multi-document question answering and key-value retrieval. We find that performance can degrade significantly when changing the position of relevant information, indicating that current language models do not robustly make use of information in long input contexts. In particular, we observe that performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle of long contexts, even for explicitly long-context models."

핵심: **U자형 성능 곡선** — 관련 정보가 문맥 처음/끝에 있을 때 성능 최고, 중간일 때 급락.

---

## 3. RULER — "What's the Real Context Size of Your Long-Context Language Models?"

- **출처**: NVIDIA (arXiv 2404.06654)
- **URL**: https://arxiv.org/abs/2404.06654 · https://github.com/NVIDIA/RULER
- **신뢰도**: WebSearch 요약 기반 — 원문 full 직접 확인 필요(확인 필요). 수치 인용 시 원문 대조 권장.

핵심 개념:
- **effective length** 정의: RULER에서 ≥85% 점수를 유지하는 최대 window 길이. "claimed length"(광고된 길이)와 구분.
- 13개 태스크 / 4범주(retrieval, multi-hop tracing, aggregation, QA).
- 발견(검색 요약): "32K+ 를 주장하는 모델 중 절반만 32K에서 만족스러운 성능 유지." vanilla NIAH는 거의 만점이어도 길이 증가 시 큰 하락.

---

## 4. NoLiMa — "Long-Context Evaluation Beyond Literal Matching"

- **출처**: Adobe Research (arXiv 2502.05167), ICML 2025 poster
- **URL**: https://arxiv.org/abs/2502.05167 · https://github.com/adobe-research/NoLiMa
- **신뢰도**: WebSearch 요약 기반 — 원문 full 직접 확인 필요(확인 필요).

핵심: NIAH에서 needle과 question의 **어휘 중첩(literal match)을 제거** → 모델이 latent association을 추론해야 함.
발견(검색 요약):
- 128K 지원 주장 13개 모델 평가. 짧은 문맥(<1K)에선 우수하나 길이 증가 시 급락.
- "32K에서 11개 모델이 짧은-길이 baseline의 50% 미만으로 하락."
- GPT-4o: 99.3% (baseline) → 69.7% (32K).
