---
name: prompt-vs-context-vs-harness
topic: 프롬프트 · 컨텍스트 · 하네스 3계층 중첩 모델
category: 01-fundamentals
added: 2026-05-26
source: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents · Atlan blog
tags: [layering, prompt, context, harness, fundamentals]
status: revised-2026-05-26
revision_note: Anthropic "Effective context engineering" 글의 공식 정의 인용 추가.
---

# 프롬프트 vs 컨텍스트 vs 하네스

## 핵심 한 줄
**하네스 ⊃ 컨텍스트 ⊃ 프롬프트**. 세 단어는 비슷해 보이지만 범위가 다르고, 작업 단위가 다르다. 어느 레이어의 문제인지 먼저 분류해야 해결책이 보인다.

## 본문

### Anthropic 공식 정의 (Context Engineering)

> "Context engineering refers to the set of strategies for curating and maintaining the optimal set of tokens (information) during LLM inference, including all the other information that may land there outside of the prompts."
> "At Anthropic, context engineering is viewed as the natural progression of prompt engineering."
> "As we move towards engineering more capable agents that operate over multiple turns of inference and longer time horizons, we need strategies for managing the entire context state."

→ Anthropic 공식 입장: Context engineering은 prompt engineering의 자연스러운 확장. Harness는 그 위 상위 레이어(시스템 전체)로 본 references가 정리.

### 3계층 정의

| 레이어 | 답하는 질문 | 범위 | 산출물 |
|--------|------------|------|--------|
| **Prompt** | "한 턴에서 모델에게 뭐라고 시킬까?" | 단일 메시지 | 잘 쓰인 instruction |
| **Context** | "이 턴에서 모델이 뭘 봐야 하나?" | 한 턴의 입력 전체 | 적절히 선별된 RAG·툴 결과·메모리 |
| **Harness** | "에이전트 전체가 어떻게 굴러가나?" | 시스템 전체 | 루프·도구·권한·평가·관측 인프라 |

### 중첩 관계
- **프롬프트**는 한 턴 안에서 모델에게 직접 던지는 문장. "이걸 해줘"의 본문.
- **컨텍스트**는 그 프롬프트를 둘러싼 모든 입력 — system prompt, 이전 대화, RAG 결과, 메모리, 도구 호출 결과. 프롬프트는 컨텍스트의 한 조각.
- **하네스**는 컨텍스트를 누가·언제·어떤 기준으로 채우는지, 도구를 어떻게 노출하는지, 실패하면 어떻게 회복하는지를 정하는 시스템. 컨텍스트는 하네스가 매 턴 만들어내는 산출물.

### 어느 레이어 문제인가 — 판단 가이드

| 증상 | 의심 레이어 | 해결 방향 |
|------|------------|-----------|
| 한 번의 답이 안 좋다 | Prompt | 지시문 다시 쓰기, few-shot, structured output |
| 답이 들쭉날쭉, 맥락을 놓침 | Context | RAG 정제, 메모리 인덱싱, 도구 결과 요약 |
| 같은 실수 반복, 시스템적 결함 | Harness | 훅·스킬·권한·평가 인프라 재설계 |

### 흔한 혼동
- "프롬프트 엔지니어링"이라고 부르지만 실제로는 컨텍스트나 하네스 문제인 경우가 많다.
- 모델 교체로 해결될 줄 알았는데 안 되는 문제는 대개 하네스 문제.
- 반대로 하네스 과설계로 트리비얼한 한 줄 응답을 무겁게 만드는 것도 흔한 실수.

## 관련 자료
- [[harness-concept]] — 하네스 전체 정의
- [[12-standard-components]] — 하네스를 구성하는 카테고리

## 출처
- **Anthropic 공식 (확인일 2026-05-26)**:
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents — context engineering 공식 정의
- Atlan, "Harness Engineering vs Prompt Engineering" — https://atlan.com/know/harness-engineering-vs-prompt-engineering/
