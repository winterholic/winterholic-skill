---
name: loop-and-a-dream
topic: "Loop and a dream" — while 루프에 LLM만 박은 구조
category: 04-anti-patterns
added: 2026-05-26
source: 내부 분석 + Addy Osmani 블로그 (간접 참고)
tags: [anti-pattern, naive-loop, no-learning, no-recovery]
status: partial
verification_note: "Loop and a dream"이라는 정확 표현은 Addy Osmani 블로그에서 직접 인용 못함 (확인일 2026-05-26 WebFetch 결과). 안티 패턴 자체는 일반적 인식 — 단 정확한 표현 출처는 미확인.
---

# "Loop and a dream" 안티 패턴

## 핵심 한 줄
**while True에 LLM만 박은 구조**. 같은 실패가 반복돼도 학습이 남지 않고, 권한·평가·관측 없이 무작정 도구만 쥐여준 상태.

## 본문

### 증상
- `while not done: result = llm.run(prompt)` 같은 단순 루프
- 같은 에러가 5회, 10회 반복돼도 모델이 같은 답을 시도
- 실패 정보가 다음 시도에 누적되지 않음
- 권한·평가·관측 인프라 없음
- "모델만 좋아지면 다 해결된다"는 기대

### 왜 안 되는가
- LLM은 상태가 없음 — 같은 컨텍스트에서 같은 입력이면 비슷한 결과
- "loop"만 있고 "learning"이 없으면 비효율 무한 반복
- 실패가 audit trail에 안 남으면 사람도 디버깅 불가능

### 좋은 하네스의 대척점

| Loop and a dream | 좋은 하네스 |
|------------------|------------|
| while 루프에 LLM만 | plan-act-observe + 평가 게이트 |
| 같은 실패 반복 | 학습이 AGENTS.md/Skill로 굳어짐 |
| 권한 무제한 | deny-first, ask 모드 |
| self-eval만 | Generator/Evaluator 분리 |
| 무관측 | logging, trace, audit trail |
| 모델 의존 | 시스템적 회복 메커니즘 |

### 교정 절차
1. **실패 학습 저장**: 반복 실패 → CLAUDE.md/Memory/Skill에 정리
2. **평가 단계 분리**: 결과 검증을 별도 에이전트로
3. **관측 인프라**: 로깅·statusline·hook으로 진행 가시화
4. **권한 deny-first**: 처음 보는 도구는 ask, 검증 후 allow
5. **회복 메커니즘**: 파괴적 작업 전 snapshot, 실패 시 revert

### "모델만 업그레이드하면 된다"는 미신
- 모델 commodity 시대 — 하네스가 진짜 IP
- 같은 컴포넌트로 새 모델 받으면 같은 한계
- 하네스를 first-class artifact로 다뤄야 함

## 관련 자료
- [[harness-concept]] — 좋은 하네스 vs 나쁜 하네스
- [[generator-evaluator-separation]] — 평가 분리
- [[memory]] — 학습 저장 자리
- [[rule-over-enforcement]] — 반대편 안티 패턴

## 출처
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html` (섹션 2.4)
- Addy Osmani, "Agent Harness Engineering" — https://addyosmani.com/blog/agent-harness-engineering/ (관련 안티 패턴 논의, 단 "loop and a dream" 정확 표현은 미확인)
- Viv Trivedy "Anatomy of an Agent Harness" — https://x.com/Vtrivedy10/status/2031408954517971368 — harness 정의 출처
