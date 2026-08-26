---
name: memory-overuse
topic: 메모리 남용 — 모든 걸 auto memory에 박아넣음
category: 04-anti-patterns
added: 2026-05-26
source: 내부 분석 + awesome-harness-engineering · 사용자 운영 관행
tags: [anti-pattern, memory, context-bloat, persistence]
status: partial
verification_note: 메모리 freshness가 핵심 품질이라는 명제는 awesome-harness-engineering README에서 verbatim 확인. 구체 수치 가이드(50-150줄 등)는 사용자 운영 관행.
---

# 메모리 남용 안티 패턴

## 핵심 한 줄
**모든 사용자 발화·작업 결과를 auto memory에 누적**하면 컨텍스트가 부풀고 stale 정보가 결정을 흐린다. 메모리는 "반복된 학습"만의 자리다.

> **근저 학술 물리**: [[../07-llm-theory/context-rot-length-vs-performance]] — 누적 메모리 = 매 세션 입력 길이↑ + distractor↑. Chroma: *"Even a single distractor reduces performance."* stale 메모리는 의미상 distractor. 메모리 freshness가 품질이라는 명제의 물리적 근거.

## 본문

### 증상
- 일회성 작업 결과까지 메모리에 저장
- 코드 스니펫·파일 경로·도메인 데이터를 메모리에 누적
- 메모리 파일 개수가 50+, 100+로 무제한 증가
- 매 세션 메모리 인덱스 자체가 컨텍스트의 큰 부분 차지
- stale된 피드백(이미 해결된 것)이 계속 주입됨

### 왜 안 되는가
- 메모리는 **매 턴 자동 주입** — 부풀수록 다른 컨텍스트 밀려남
- stale 정보는 잘못된 결정 유도
- 검색·인덱싱 없이 누적만 하면 어느 메모리가 적용될지 예측 불가

### 메모리에 들어갈 것 vs 안 들어갈 것 (재강조)

| 들어감 (반복 학습) | 안 들어감 |
|-------------------|----------|
| 같은 피드백 2회 이상 받음 | 일회성 작업 결과 (→ work-history) |
| 응답 태도 메타 룰 | 코드 스니펫 (→ git) |
| 자주 묻는 컨벤션 | 도메인 지식 (→ Skill) |
| 프로젝트 unrelated 글로벌 룰 | 프로젝트 설정 (→ 프로젝트 CLAUDE.md) |

### 교정
1. **주기적 정리**: 메모리 파일을 분기마다 점검, stale 표시 또는 삭제
2. **인덱스 + 본문 분리**: 한 줄 요약만 인덱스에, 본문은 별도 파일
3. **카테고리 명시**: `feedback_<topic>` 같은 명명으로 그룹화
4. **삭제 가능성 인정**: 학습이 굳어진 메모리는 CLAUDE.md/Skill로 승격 후 삭제

### 좋은 메모리 사이즈 가이드
- 인덱스(MEMORY.md): 50~150줄 이내
- 개별 메모리 파일: 각 30~100줄
- 전체 메모리 파일 수: 두 자리 (수십 개) 수준 유지

### 메모리 vs work-history 혼동
사용자 셋업에서 자주 헷갈리는 경계:
- **메모리**: 사용자 학습 (영구적 선호·룰)
- **work-history**: 일별 작업 일지 (vault `logs/work-history/YYYY-MM-DD.md`)
- 일회성은 work-history로, 반복 학습은 메모리로

## 관련 자료
- [[components/memory]] — 메모리 컴포넌트
- [[components/claude-md]] — 정적 정책 자리
- [[../05-decision-trees/memory-vs-claude-md-vs-skill]] — 어디에 둘지

## 출처
- **외부 (확인일 2026-05-26)**:
  - https://github.com/ai-boost/awesome-harness-engineering — "Memory quality is mostly a freshness and invalidation problem — stale, branch-specific memories are often more dangerous than having no memory at all." verbatim
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html` (섹션 2.4, 4.3)
