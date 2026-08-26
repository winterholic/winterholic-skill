---
name: memory
topic: Memory — 세션 간 persist되는 정보 계층
category: 02-components
added: 2026-05-26
source: 내부 분석 + Claude Code memory tool docs
tags: [memory, persistence, indexing, auto-memory]
status: partial
verification_note: 사용자 셋업의 auto-memory 구조는 내부 자료이며 Anthropic의 공식 "memory tool" (managed-agents 글에 등장)과는 다른 자리. 두 자리를 명확히 구분. 공식 memory tool 동작은 부분 검증, 사용자 auto-memory 4-type 분류는 내부 관찰.
---

# Memory — 메모리 컴포넌트

## 핵심 한 줄
**대화 간 persist되는 정보**의 자리. 사용자 셋업의 auto-memory(`~/.claude/projects/.../memory/`)와 Anthropic 공식 "memory tool"(managed agents의 파일 기반 memory)은 다른 레이어임에 주의.

## 본문

### 두 종류 메모리 구분 (중요)

| 종류 | 위치 | 동작 |
|------|------|------|
| **사용자 셋업 auto-memory** | `~/.claude/projects/<project-id>/memory/MEMORY.md` + 개별 파일 | Claude Code가 대화 컨텍스트에서 자동 추출·저장, 매 세션 인덱스 주입 |
| **Anthropic "memory tool"** | sandbox 내 파일 (managed agents) | LLM이 직접 파일로 컨텍스트 작성, 세션 간 학습 |

Anthropic 공식 verbatim:
> "the memory tool lets Claude write context to files, enabling learning across sessions" — managed-agents 글

사용자 셋업의 `feedback_*.md`는 첫 번째 종류 (auto-memory).

### 사용자 셋업 메모리 구조
- **인덱스**: `~/.claude/projects/<project-id>/memory/MEMORY.md`
- **개별 메모리 파일**: `feedback_git.md`, `feedback_comments.md`, `feedback_work_history.md`, `feedback_response_style.md` 등
- **자동 주입**: 매 턴 conversation context에 자동 주입

### CLAUDE.md vs Memory vs Skill 역할
- **CLAUDE.md**: 정적 정책 (응답 언어, 금지 룰)
- **Memory**: 사용자 학습된 선호·반복 피드백 (자주 갱신)
- **Skill**: 도메인 전문 지식 (필요 시 트리거)

상세 판단은 [[../05-decision-trees/memory-vs-claude-md-vs-skill]] 참조.

### 좋은 메모리 설계
- **인덱스 + 본문 분리**: 메인 컨텍스트엔 한 줄 요약·링크만
- **카테고리 명시**: 어떤 종류의 피드백인지 슬러그로 표시 (`feedback_<topic>`)
- **삭제 가능성**: 메모리는 stale 가능 → 주기적 정리
- **세션 간 일관성**: 같은 피드백을 두 번 받지 않는지 확인 (학습이 굳어졌는가)

### awesome-harness-engineering 인용
> "Memory quality is mostly a freshness and invalidation problem — stale, branch-specific memories are often more dangerous than having no memory at all."

→ 메모리 freshness가 핵심 품질 축. 단순 누적은 안티 패턴.

### 메모리에 들어가는 것 vs 안 들어가는 것

| 들어감 | 안 들어감 |
|--------|----------|
| 반복된 사용자 피드백 ("주석 자명하면 빼라") | 일회성 작업 결과 |
| 응답 태도 선호 ("거친 말투는 친밀감") | 코드 스니펫 |
| 메타 룰 ("git 보수적으로") | 도메인 지식 (→ Skill) |
| 자주 묻는 컨벤션 | 변경 잦은 프로젝트 설정 |

### Context Reset vs Compaction
- **Compaction**: 컨텍스트 가득 차면 자동 요약 — 정보 손실 큼
- **Reset + Handoff**: 명시적 종료 + 다음 세션이 읽을 artifact 작성 — 손실 적음
- 2026 Anthropic 검증: Sonnet 4.5에선 reset 필수, Opus 4.5에선 단일 세션도 OK
- 상세: [[../03-patterns/context-reset-vs-compaction]]

## 관련 자료
- [[claude-md]] — 정적 정책
- [[skills]] — 도메인 전문 지식
- [[../03-patterns/context-reset-vs-compaction]] — Reset/Handoff 패턴
- [[../05-decision-trees/memory-vs-claude-md-vs-skill]] — 어디에 둘지

## 출처
- **공식 (확인일 2026-05-26)**:
  - https://www.anthropic.com/engineering/managed-agents — "memory tool" 공식 언급
  - https://github.com/ai-boost/awesome-harness-engineering — memory freshness 인용
- 사용자 셋업 auto-memory: `~/.claude/projects/<project-id>/memory/`
