# ADR — Architecture Decision Record 운영 가이드

> 큰 기술 결정은 **왜 그렇게 정했는지**를 남긴다. 나중에 "왜 이렇게 돼 있지?"에 답하기 위해.

## 1. ADR이란
Michael Nygard가 2011년 "Documenting Architecture Decisions"에서 대중화. 핵심 철학:
> "큰 문서는 절대 최신으로 유지되지 않는다. 작고 모듈화된 문서는 갱신될 가능성이라도 있다."
- ADR 1건 = **1~2페이지**, 하나의 결정.
- 코드 저장소 안(`docs/adr/0001-*.md`)에 두고 git으로 버전 관리 — 결정과 코드가 같이 산다.
> 근거: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions · Fowler https://martinfowler.com/bliki/ArchitectureDecisionRecord.html

## 2. Nygard 원본 템플릿
```markdown
# NNNN. <결정 제목>

## Status
proposed | accepted | deprecated | superseded by ADR-NNNN

## Context
이 결정을 내리게 된 상황. 기술적·정치적·사회적·프로젝트 제약.
(중립적 사실 서술 — "무엇이 우리를 이 결정으로 몰았나")

## Decision
우리가 내린 결정. **능동태 "We will…"** 로 명확히.

## Consequences
이 결정으로 생기는 결과 — **긍정·부정 모두**.
(트레이드오프를 숨기지 말 것. 여기가 정직함을 강제하는 자리)
```
- **Status 전이**: proposed → accepted. 나중에 뒤집히면 옛 ADR을 `superseded by ADR-0012`로 표시하고 **지우지 않는다**(왜 바꿨는지의 역사가 자산).
- **Consequences가 핵심**: 많은 결정 문서가 트레이드오프를 빠뜨리거나 "Risks"에 숨긴다. Nygard 포맷은 부정적 결과를 명시하게 강제.

## 3. CTO가 ADR을 언제 요구하나
모든 결정이 아니라 **되돌리기 비용이 큰(Type 1) 큰 결정**만:
- 주요 스택·프레임워크·DB 선택
- build vs buy vs partner 판정
- 아키텍처 경계·서비스 분리
- 데이터 모델·API 계약의 근본 변경
→ 사소한 결정까지 ADR을 요구하면 관료제. 판단 기준: "6개월 뒤 신규 입사자가 '왜 이렇게?'라고 물을 만한가."

## 4. 운영 관행
- **번호는 단조 증가**, 삭제 없음(superseded로만 무효화).
- PR에 ADR을 함께 제출 → 리뷰에서 **결정 자체를 토론**(코드가 아니라).
- 경량 도구: `adr-tools`(CLI)로 생성·인덱싱 가능. 없어도 마크다운 수기로 충분.
- 팀이 늘면 ADR이 **온보딩 자산**이 된다 — 신규 입사자가 결정 이력을 읽고 맥락을 흡수.

## 5. SKILL 출력 템플릿과의 연결
biz-cto 출력 템플릿(사업문맥/단계/결정/대안·되돌리기비용/가설·확인시점)은 사실상 **경량 ADR**이다. 큰 결정은 이 출력을 그대로 `docs/adr/`에 저장하면 결정 기록이 된다.
- 매핑: 사업문맥→Context / 결정→Decision / 대안·트레이드오프·되돌리기비용→Consequences / 가설·확인시점→(추가 필드, Nygard 원본엔 없으나 실전 유용).
