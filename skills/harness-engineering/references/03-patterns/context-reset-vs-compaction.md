---
name: context-reset-vs-compaction
topic: Context Reset이 Compaction의 한계를 보완한다 — handoff artifact 패턴
category: 03-patterns
added: 2026-05-26
source: https://www.anthropic.com/engineering/managed-agents · https://www.anthropic.com/engineering/harness-design-long-running-apps · https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
tags: [context-reset, compaction, handoff, long-horizon, sonnet-anxiety]
status: revised-2026-05-26
revision_note: "Reset이 Compaction을 이긴다"는 과한 단순화 — 공식 표현은 "compaction alone wasn't sufficient"로 수정. Opus 4.5에선 reset 불필요해졌다는 사실 추가.
verification_note: "context anxiety" 문장은 managed-agents·harness-design 두 페이지 워딩이 다름(managed-agents "sensed its context limit approaching" vs harness-design "begin wrapping up work prematurely"). 의미 동일, 출처 분리 표기됨. 인용 시 어느 페이지 표현인지 구분 권장.
---

# Context Reset vs Compaction

## 핵심 한 줄
**Sonnet 4.5의 "context anxiety"로 인해 compaction만으로는 long-horizon이 부족**해, Anthropic은 hash에 context resets + handoff artifact를 추가했다. Opus 4.5에선 이 현상이 거의 사라져 reset 없이도 single continuous session 가능.

## 본문

### Anthropic 공식 verbatim 인용

**Managed-agents 글:**
> "Claude Sonnet 4.5 would wrap up tasks prematurely as it sensed its context limit approaching—a behavior sometimes called 'context anxiety.'"
> "We addressed this by adding context resets to the harness."
> "Compaction lets Claude save a summary of its context window and the memory tool lets Claude write context to files, enabling learning across sessions."

**Harness-design 글:**
> "Claude Sonnet 4.5 exhibited context anxiety strongly enough that compaction alone wasn't sufficient to enable strong long task performance"
> "A reset provides a clean slate, at the cost of the handoff artifact having enough state for the next agent to pick up the work cleanly."

**Effective-harnesses 글:**
> "each new session begins with no memory of what came before"
> "a two-fold solution to enable the Claude Agent SDK to work effectively across many contexts: an initializer agent that sets up the environment on the first run, and a coding agent that is tasked with making incremental progress in every session"
> "leaving clear artifacts for the next session"
> "claude-progress.txt file that keeps a log of what agents have done, and an initial git commit"
> "work on only one feature at a time. This incremental approach turned out to be critical"

### 정확한 명제 정리

이전 references의 "Context Reset이 Compaction을 **이긴다**"는 표현은 과한 단순화. 공식 입장:
1. Sonnet 4.5에서 **compaction alone wasn't sufficient** → reset 추가가 필요했다
2. Reset의 cost: handoff artifact를 잘 만들어야 함
3. Opus 4.5에선 context anxiety가 거의 사라져 reset 없이도 가능 — Anthropic은 reset을 harness에서 제거하고 single continuous session으로 운영

→ "Reset > Compaction"이라는 일반 명제가 아니라, **특정 모델·long-horizon 조건에서 reset이 필수가 됐다**가 정확한 표현.

### Compaction의 한계 (공식 인용 기반)
- 자동 요약 → 정보 손실 발생
- 모델이 컨텍스트 한계 근처에서 "anxiously" 작업 마무리하려는 경향
- 단순 요약만으로는 무엇이 중요한지 보존 어려움

### Reset + Handoff의 우위 — Anthropic 패턴
- **Initializer agent + coding agent**: 환경 셋업과 incremental progress 분리
- **handoff artifact**: `claude-progress.txt` 같은 진척 로그 + 초기 git commit
- **work on only one feature at a time**: incremental 접근
- **Self-verify all features**: 검증 디시플린

### handoff 스킬 패턴 (사용자 셋업)
`handoff` 스킬 (A 등급):
1. 세션 복잡도 평가
2. 깊이 조절 (단순 Q&A는 handoff 불필요)
3. 실패한 접근 명시 보존
4. 미해결 결정 명시
5. WIP 상태 보존

### 언제 reset, 언제 compaction
| 상황 | 선택 |
|------|------|
| 단일 Q&A · 완료된 작업 | 둘 다 불필요 |
| Sonnet 4.5에서 long-horizon | Reset + Handoff 권장 (공식) |
| Opus 4.5에서 long-horizon | 단일 세션도 가능, 그래도 handoff는 안전판 |
| 컨텍스트 가득 차서 강제 | Compaction이 default (어쩔 수 없음) |
| 다음 사람·다음 세션 인계 | Reset + Handoff 필수 |

### 실무 적용 룰
- 세션 작업이 길어진다 싶으면 **선제적 handoff 작성** 후 새 세션
- 사용자가 "다음 세션", "인계", "이어받을 수 있게" 같은 발화 → handoff 트리거
- handoff 문서는 vault나 work-history에 저장

## 관련 자료
- [[../02-components/memory]] — 메모리 시스템
- [[../01-fundamentals/2026-trends]] — Context Reset 트렌드
- [[../99-sources/context-anxiety-anthropic-managed-agents-2026-05-26]] — verbatim 인용 백업

## 출처
- **Anthropic 공식 (확인일 2026-05-26)**:
  - https://www.anthropic.com/engineering/managed-agents — "context anxiety" 용어 출처, context reset 도입 설명
  - https://www.anthropic.com/engineering/harness-design-long-running-apps — "compaction alone wasn't sufficient" verbatim
  - https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents — initializer+coding agent, handoff artifact, incremental approach
