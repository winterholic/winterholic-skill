---
name: stop-hook-promotion-criteria
topic: Skill·CLAUDE.md 룰을 Stop hook으로 승격할 시점 결정 기준
category: 05-decision-trees
added: 2026-05-26
source: 내부 분석 + 사용자 셋업 관찰
tags: [decision-tree, stop-hook, promotion, enforcement]
status: partial
verification_note: "A급 4주 연속" 같은 정량 기준은 사용자 내부 운영 룰. Anthropic 공식 docs에는 hook 승격 기준이 별도 명시되지 않음.
---

# Stop Hook 승격 기준

## 핵심 한 줄
**A급 4주 연속 사용 + 실패 비용이 검증 비용을 능가**할 때만 Stop hook으로 승격. 그 전엔 Skill/CLAUDE.md로 유지.

## 왜 신중해야 하나

Stop hook은 **모든 응답 마무리 직전에 발동**한다. 매번. → 조건 부정확하면:
- 사용자가 무시 시작 → 죽은 룰 (학습 루프 회귀)
- 노이즈 → 작업 속도 손해 (사용자 최우선 가치 위반)
- 거짓 발동 시 매번 디버깅 필요

승격은 일방향. 되돌리기는 가능하지만 한번 자리잡으면 잘 안 뺀다.

## 결정 트리

```
1. 룰이 이미 안정적으로 운영되는가?
   - Skill 또는 CLAUDE.md 형태로 4주 이상 운영
   - skills-estimate A급(85+) 또는 사용자가 명시적 만족
   ├─ NO → 아직 승격 X. 안정화 우선
   └─ YES → 2번

2. 사용자가 잊어서 실패한 사례가 있는가?
   - work-history grep으로 "잊었음·놓쳤음" 패턴 1건 이상
   - 또는 사용자가 "왜 이거 안 하지?"라고 한 적
   ├─ NO → Skill 충분. 강제 불필요
   └─ YES → 3번

3. 실패 비용이 검증 비용을 능가하는가?
   - 실패 비용: 데이터 손실·시간 손실·반복 작업·사용자 불만 점수
   - 검증 비용: hook 발동마다 사용자가 읽고 무시할지 판단하는 시간
   ├─ NO → Skill 유지
   └─ YES → 4번

4. 발동 조건을 정확히 정의 가능한가?
   - "의미 있는 작업"·"코드 변경"·"파일 수정" 등 명확한 시그널
   - false positive 비율 < 20%로 추정
   ├─ NO → 조건 다듬을 때까지 보류
   └─ YES → 승격 GO
```

## 본 사용자 셋업 예시

| 룰 | 현재 위치 | 승격 시점 |
|----|-----------|----------|
| work-history 작성 | Stop hook ✅ | 이미 승격됨. 잊어서 실패 사례 다수 → 적합 |
| verification (검증 강제) | Skill (~89/A) | A급 4주 연속 후 (현재 1주차 — 2026-05-26 기준) |
| caveman 압축 | Skill (91.4/A+) | 승격 X. 강제할 영역 아님 (사용자 발화 트리거) |
| handoff 인계 | Skill + CLAUDE.md 1줄 | 승격 X. 발동 빈도 낮음 |
| systematic-debugging | Skill (~87/A) | 승격 X. 라이브러리형 |

## 안티 패턴

- **새 룰 발견 즉시 Stop hook으로** → 패턴 검증 없이 강제 → 거짓 발동 폭발
- **A급 1주만 보고 승격** → 통계 부족. 4주 minimum
- **트리거 조건 모호** → "뭔가 중요한 작업이면" 같은 표현은 hook에 못 쓴다. 명확한 시그널(파일 수정·tool 호출·키워드) 필요
- **승격 후 평가 안 함** → 2주마다 false positive 점검 필요

## 승격 절차

1. 조건 시그널 명문화 (예: "Write/Edit tool 호출 + non-test 파일")
2. hook 스크립트 작성 (`~/.claude/settings.json` 또는 `~/.claude/hooks/`)
3. 1주 dry-run (log만, 차단 X)
4. false positive 비율 측정
5. < 20%면 enforce 모드 전환, 아니면 시그널 다시
6. 2주마다 재평가

## 관련 자료
- [[skill-vs-hook-vs-claude-md]] — 셋의 본질 차이
- [[hook-noise]] *(예정)* — hook 노이즈 안티 패턴
- [[learning-loop-diagnosis]] *(예정)* — A급 평가 기준

## 출처
- **공식 (확인일 2026-05-26)**: https://code.claude.com/docs/en/hooks — hook events 명세 (~29개)
- 사용자 settings.json (Stop hook 현재 작동 중)
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html`
