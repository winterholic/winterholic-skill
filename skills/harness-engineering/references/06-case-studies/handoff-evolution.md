---
name: handoff-evolution
topic: handoff 스킬 — 단순 인계 도구에서 CLAUDE.md 1줄 룰과 결합된 자동 트리거 체계로 진화
category: 06-case-studies
added: 2026-05-26
source: work-history 2026-05-26 (line 95-99, 574-586) + 사용자 셋업 현황
tags: [case-study, handoff, claude-md-integration, session-bridge]
status: active
verification_note: 외부 검증 X — 사용자 셋업 내부 사례. work-history·skills-estimate 점수 등 1차 사료는 내부 기록.
---

# Case Study — handoff (88.9/A)

## 핵심 한 줄
**"파일만 있으면 안 됨, 다음 세션이 그 파일을 읽도록 강제해야 함"** — handoff 스킬은 본 파일 작성 도구지만, **CLAUDE.md `## Handoff` 섹션**이 짝이 되어야 비로소 작동한다. Skill + CLAUDE.md 1줄의 결합 사례.

## 진화 핵심

1. **초기 문제**: 사용자가 "handoff했어 상황파악" 발화 시 work-history를 먼저 읽는 오동작. handoff 파일 경로가 어디 적혀있지 않아 못 찾음
2. **CLAUDE.md 룰 추가** (work-history 2026-05-26 line 95-99): `## Handoff` 섹션 신설 — "handoff했어/상황파악/이어받아/인계 읽어줘" 발화 시 `~/.agents/skills/handoff/handoff-contents.md` 최우선 읽기 룰
3. **본 스킬은 작성 도구**: 인계 문서를 만들고, **읽는 행위는 CLAUDE.md 룰이 강제**. 책임 분리
4. **단일 파일 한계 노출** (본 세션 2026-05-26): handoff-contents.md를 다른 작업(NXT API)에 재사용하면서 이전 작업(harness-engineering) 컨텍스트가 덮어쓰임. **세션 종료 시점에 1개 파일**이라는 단순한 모델의 한계

## 무엇이 가르치는가

1. **Skill 단독으론 부족** — 트리거 발화 인식 + 강제 발동은 CLAUDE.md/hook이 보완
2. **결합 패턴**: Skill(작성·구조) + CLAUDE.md(읽기 강제) + 위치 명시(경로 박기). 셋 다 있어야 작동
3. **단일 파일 모델 한계** — 작업이 여러 갈래일 때 덮어쓰기 발생. 해결책 후보: 작업별 파일 분리 / 다중 항목 stack 구조 / 마지막 항목만 보존하고 이전은 work-history로 위임
4. **본 사용자 셋업 핵심 의존성**: handoff 파일이 사라지거나 잘못된 컨텍스트로 덮이면 다음 세션 시작 비용 큼

## 미해결

- 단일 파일 한 작업만 보존 → 여러 작업 동시 진행 시 어떻게 할지 (work-history로 위임 vs 다중 파일)
- 본 스킬(harness-engineering) 신설 컨텍스트가 NXT 작업으로 덮인 본 세션에서 실제 발생. 후속 검토 필요

## 본 스킬과의 연계

이 case는 [[skill-vs-hook-vs-claude-md]] "결합 패턴" 입력. **하나의 룰을 여러 컴포넌트에 분산**하는 패턴 사례.

## 관련 자료
- [[skill-vs-hook-vs-claude-md]] — 결합 패턴
- [[memory-vs-claude-md-vs-skill]]

## 출처
- work-history 2026-05-26: line 95-99 (CLAUDE.md 룰 추가), 574-586 (handoff 작성·재작성)
- 사용자 CLAUDE.md `## Handoff` 섹션
- 본 세션 2026-05-26 실 사례 (NXT 덮어쓰기)
