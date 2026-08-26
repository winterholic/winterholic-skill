---
name: claude-md
topic: CLAUDE.md — 매 턴 컨텍스트에 로드되는 instruction file
category: 02-components
added: 2026-05-26
source: https://code.claude.com/docs/en/claude-directory · https://code.claude.com/docs/en/memory
tags: [claude-md, system-prompt, anchor, memory-files]
status: revised-2026-05-26
revision_note: 공식 docs 기반으로 precedence 규칙 정확화. "글로벌·프로젝트·로컬 3-tier" 명명이 정확하지 않음을 보정.
---

# CLAUDE.md — instruction file 컴포넌트

## 핵심 한 줄
`CLAUDE.md`는 Claude Code 세션마다 컨텍스트로 로드되는 instruction file. **user level (`~/.claude/`)과 project level (`./` 또는 `./.claude/`)이 모두 로드되며**, 공식 docs는 **충돌 시 Claude가 임의 선택할 수 있다**고 경고한다.

## 본문

### Memory file 계층 (공식 docs)

| 계층 | 위치 | 공유 범위 |
|------|------|----------|
| **System (관리자)** | 시스템 배포 경로 | 머신 전체 사용자 |
| **User** | `~/.claude/CLAUDE.md` | 본인의 모든 프로젝트 |
| **Project** | `./CLAUDE.md` 또는 `./.claude/CLAUDE.md` | git 커밋 → 팀 공유 |
| **Local (개인 override)** | `./CLAUDE.local.md` | git 제외, 본인만 |

**공식 precedence 주의사항** (Claude Code docs):
- 파일은 lowest → highest priority 순으로 로드된다고 안내되지만,
- **충돌 시 Claude가 어느 하나를 임의로 선택할 수 있음**. CSS처럼 엄격한 override가 아님.
- 명확한 personal override가 필요하면 `CLAUDE.local.md` 사용

이전 references가 "글로벌·프로젝트·로컬 3-tier"라고 적은 부분은 부정확:
- 공식 명칭은 user-level, project-level이며 "글로벌"이라는 용어는 공식 docs에 안 나옴
- 충돌 시 "프로젝트가 글로벌을 override"한다는 기존 표현은 잘못된 단순화

### 매 세션 로드되는 의미
- system prompt에 가까운 위치에 주입돼 prompt cache 적용
- 길이가 늘어도 매 턴 비용은 캐시 hit으로 거의 0 (단 cache miss 시 비용 발생)
- 단 컨텍스트 윈도우의 일부를 차지하므로 무한정 늘리면 다른 자료가 밀린다

### 좋은 CLAUDE.md의 특징 (사용자 관행)
- **정책 중심**: "이렇게 해라/하지 마라" 명시
- **금지 사항 명확화**: 위험 작업·민감 정보 접근 차단
- **응답 태도**: 한국어/영어, 토론 모드, "확인 필요" 마커 룰
- **포인터 형식 활용**: 큰 자료는 별도 파일 + "필요 시 읽기" 지시
- **변경 빈도 낮은 것만**: 자주 바뀌는 정보는 메모리·스킬로 분리

### 흔한 안티 패턴
- 모든 도메인 지식을 통째 박아넣어 컨텍스트 폭발
- 트리비얼 작업까지 의식 절차 강제 (Iron Law 류)
- 같은 룰을 user-level·project-level·local에 중복 작성

### settings.json과의 역할 분담
- **CLAUDE.md**: LLM이 읽는 정책·정체성·룰
- **settings.json**: 하네스가 읽는 권한·훅·모델 설정
- 정책은 CLAUDE.md, 결정론적 강제는 settings.json + 훅

## 관련 자료
- [[hooks]] — 결정론적 강제 자리
- [[memory]] — 변경 빈도 높은 정보의 자리
- [[skills]] — 도메인 전문 지식의 자리
- [[../03-patterns/progressive-disclosure]] — 포인터 형식 활용
- [[../04-anti-patterns/rule-over-enforcement]] — Iron Law 도그마 위험

## 출처
- **공식 (확인일 2026-05-26)**:
  - https://code.claude.com/docs/en/claude-directory — `.claude` 디렉토리 구조
  - https://code.claude.com/docs/en/memory — memory file 계층, precedence 동작
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html`
