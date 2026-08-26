---
name: harness-concept
topic: 하네스란 무엇인가 — 모델이 commodity가 된 시대의 진짜 IP
category: 01-fundamentals
added: 2026-05-26
source: Viv Trivedy "Anatomy of an Agent Harness" · Addy Osmani "Agent Harness Engineering" · awesome-harness-engineering
tags: [harness, fundamentals, commodity, ip]
status: revised-2026-05-26
revision_note: 핵심 인용 출처 검증 완료. 인용문 verbatim·출처 URL 추가.
---

# 하네스 엔지니어링 개념

## 핵심 한 줄
**Harness는 LLM 본체가 아닌 모든 것** — 도구·메모리·훅·권한·평가·관측·확장성 전체. Viv Trivedy: *"Agent = Model + Harness. If you're not the model, you're the harness."*

## 본문

### 정의 (verbatim 인용)

**Viv Trivedy "The Anatomy of an Agent Harness" (2026-03-10):**
> "Agent = Model + Harness. If you're not the model, you're the harness."
> "A harness is every piece of code, configuration, and execution logic that isn't the model itself."

**Addy Osmani "Agent Harness Engineering" (O'Reilly):**
> "A decent model with a great harness beats a great model with a bad harness."
> "The gap between what today's models can do and what you see them doing is largely a harness gap."

**awesome-harness-engineering (GitHub README):**
> "Harness engineering is the discipline of designing the scaffolding — context delivery, tool interfaces, planning artifacts, verification loops, memory systems, and sandboxes — that surrounds an AI agent and determines whether it succeeds or fails on real tasks."
> "Every component here exists because the model can't do it alone — and the best harnesses are designed knowing those components will become unnecessary as models improve."

### 왜 지금 중요한가
- 2026년 들어 모델 성능 격차가 좁혀지면서, 차별화 포인트가 모델 자체에서 하네스로 이동
- "harness gap" — 모델 잠재력과 실제 산출 결과 사이의 격차는 대개 하네스 격차
- Anthropic 자체가 "harness design" 시리즈 글을 engineering 블로그에 게재 — 공식 분과로 자리잡음

### 시대 인식

| 명제 | 의미 |
|------|------|
| **모델은 commodity** | 모델 교체 가능성을 전제로 시스템 설계 |
| **하네스가 IP** | 같은 모델을 누가 어떻게 운영하느냐가 진짜 차별점 |
| **first-class artifact** | 하네스를 코드처럼 버전 관리·평가·개선 대상으로 다룸 |

이전 references의 "TechTimes 2026-05-21: 4개 경쟁 팀이 비슷한 하네스 구조에 수렴" 인용은 2차 보도 — **확인 필요**, 1차 자료 미확인.

### 좋은 하네스 vs 나쁜 하네스

**좋은 하네스**
- 같은 실수를 두 번 하지 않는다 (학습이 CLAUDE.md/Skill로 굳어짐)
- "Success is silent, failures are verbose" — 실패를 시끄럽게 (커뮤니티 격언)
- deny-first, prompt injection을 가정한 권한 설계
- 모델이 보는 것을 명시적으로 관리, lazy load 기본
- Generator와 Evaluator 분리, skeptical evaluator
- 모든 파괴적 작업에 snapshot/revert
- Skills·MCP·Subagent로 직교적 확장

**나쁜 하네스**
- "Loop and a dream" — while 루프에 LLM만 박은 구조 (이 표현은 사용자 내부 코인 — 외부 1차 자료에선 미확인)
- 같은 실패가 반복되는데도 학습이 남지 않음
- 모든 도구를 system prompt에 박아넣어 컨텍스트 폭발
- self-evaluation에만 의존
- permission/audit 없는 광범위 filesystem·shell 접근
- 모델 업그레이드에도 똑같은 컴포넌트를 들고 가는 관성

## 관련 자료
- [[prompt-vs-context-vs-harness]] — 3계층 중첩 모델
- [[12-standard-components]] — awesome-harness-engineering 카테고리
- [[claude-code-7-components]] — Claude Code 하네스의 7대 컴포넌트
- [[2026-trends]] — 2026 핵심 트렌드 6가지

## 출처
- **1차 자료 (확인일 2026-05-26)**:
  - Viv Trivedy, "The Anatomy of an Agent Harness" — https://x.com/Vtrivedy10/status/2031408954517971368 (2026-03-10)
  - Addy Osmani, "Agent Harness Engineering" — https://addyosmani.com/blog/agent-harness-engineering/ · O'Reilly Radar https://www.oreilly.com/radar/agent-harness-engineering/
  - ai-boost/awesome-harness-engineering — https://github.com/ai-boost/awesome-harness-engineering
- Louis Bouchard, "Harness Engineering" — https://www.louisbouchard.ai/harness-engineering/
- MindStudio, "What Is an Agent Harness?" — https://www.mindstudio.ai/blog/what-is-agent-harness-architecture-explained
