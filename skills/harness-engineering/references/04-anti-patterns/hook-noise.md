---
name: hook-noise
topic: Hook 노이즈 — 같은 reminder 반복으로 학습 효과 0
category: 04-anti-patterns
added: 2026-05-26
source: 내부 분석 + 커뮤니티 운영 관행
tags: [anti-pattern, hooks, noise, reminder-fatigue]
status: partial
verification_note: "Success is silent, failures are verbose"는 커뮤니티 격언 (Anthropic 공식 아님). hook 노이즈로 인한 무시 학습 메커니즘은 사용자 운영 경험 + 일반적 UX 원칙.
---

# Hook 노이즈 안티 패턴

## 핵심 한 줄
**같은 reminder가 매 턴 반복**되면 LLM·사용자 모두 무시하기 시작. hook은 강력하지만 노이즈가 되는 순간 마이너스 자산.

> **근저 학술 물리**: [[../07-llm-theory/context-rot-length-vs-performance]] §2-1 — S2A(Weston 2023): *"Soft attention is susceptible to incorporating irrelevant information from the context into its latent representations."* 매 턴 같은 reminder는 무관 신호 누적 → 잠재 표현 오염. "무시하는 학습"의 mechanism 자체.

## 본문

### 증상
- Stop hook이 매 응답마다 같은 reminder 텍스트 주입
- PreToolUse가 거의 모든 명령에 경고 출력
- 환경 변수·flag·timestamp 같은 부수 정보까지 매번 stdout으로
- 응답에 "[reminder] ..." 패턴이 반복적으로 끼어듦

### 왜 안 되는가
- **무시 학습**: 같은 텍스트 반복 → LLM이 패턴으로 학습해 본문만 추출
- **컨텍스트 오염**: reminder 텍스트가 컨텍스트 차지
- **신호 vs 노이즈 비율 악화**: 진짜 중요한 reminder도 묻힘
- **사용자 피로**: 응답 가독성 ↓

### 좋은 hook 출력 원칙
- **success is silent**: 정상 흐름엔 출력 X
- **failures are verbose**: 진짜 막힘·차단 시에만 시끄럽게
- **상태 변화 시에만**: flag set/unset, 정책 위반 등
- **diff 출력**: 직전과 같은 reminder 반복 X

### 교정 절차
1. **출력 빈도 측정**: hook 로그를 시간순으로 보고 같은 텍스트 빈도 확인
2. **조건 강화**: "X가 미충족" 같은 조건 정밀화
3. **silent on success**: 정상이면 출력 자체 X
4. **diff 기반**: 직전 상태와 비교해 변화 있을 때만

### 안티 예
```
Stop hook 출력 (매 응답마다):
[work-history reminder]
[git status check]
[flag status: work=false]
[session 5h window: 2h remaining]
```
→ 4줄 × 매 응답 = 컨텍스트 압박

### 좋은 예
```
Stop hook 출력 (work-history 미작성 + 코드 수정 있을 때만):
[BLOCK] work-history 미작성: <오늘 작업 요약 + vault에 기록 필요>
```

### Hook reminder vs Skill prompt 차이
- **Hook**: 결정론적, 외부 주입 — 무시 못 함 (그래서 노이즈 되기 쉬움)
- **Skill prompt**: LLM이 트리거 판단 — 자연스러움
- 노이즈가 될 만한 건 Skill로, 진짜 차단해야 할 건 Hook로

## 관련 자료
- [[components/hooks]] — Hook 컴포넌트
- [[iron-laws-pattern]] — Hook 승격 판단
- [[../05-decision-trees/stop-hook-promotion-criteria]] — Skill을 Hook으로

## 출처
- **공식 (확인일 2026-05-26)**: https://code.claude.com/docs/en/hooks — hook events 명세 (29개)
- disler/claude-code-hooks-mastery — https://github.com/disler/claude-code-hooks-mastery
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html` (섹션 2.4)
