# life-english 근거 자료

> 목차: 1) 습득론 출처 2) 개발 영어 관용표현집 3) 콩글리시 직역 함정 4) 학습 루프 설계 5) 입력원

> 정확한 서지·URL은 `sources.md` 참조.

## 1. 습득론 출처

- **Krashen 입력가설(Input Hypothesis)** — *The Input Hypothesis: Issues and Implications* (1985, Longman). 이해 가능한 입력(comprehensible input, i+1: 현재 수준보다 약간 위)이 습득을 이끈다. 양과 이해 가능성이 핵심.
- **Swain 아웃풋 가설(Output Hypothesis)** — Swain (1985), in Gass & Madden eds., *Input in Second Language Acquisition*, 235–253. 산출(쓰기·말하기)이 학습자에게 자신의 빈틈을 인식시키고(noticing) 언어를 처리·고정하게 한다. 캐나다 몰입교육에서 듣기·읽기는 원어민급이나 산출이 뒤처진 관찰에서 출발.
- **화석화(fossilization)** — 피드백 없는 출력은 오류가 굳어버린다(Selinker "Interlanguage" 1972 계열, 확인 필요). 교정 루프가 필요한 이유.
- **간격·인출** — 어휘·표현 암기에는 → life-learning의 간격 반복·인출 원리 동일 적용.

## 2. 개발 영어 관용표현집

**코드리뷰**
| 한국어 의도 | 영어 |
|---|---|
| 사소한 지적 | "Nit:" (nitpick) |
| 좋아 보임/승인 | "LGTM" (Looks Good To Me) |
| 봐주세요 | "PTAL" (Please Take A Look) |
| 잘 잡았다 | "Nice catch!" |
| 동의 | "SGTM" (Sounds Good To Me) |
| 작업 중 | "WIP" (Work In Progress) |
| 제안(부드럽게) | "Could we ~?" / "What do you think about ~?" |
| 반대(부드럽게) | "I'm not sure about ~. Have we considered ~?" |
| 차단성 의견 | "Blocking: ~" / "필수 아님: Non-blocking: ~" |

**이슈/PR**
- 재현: "Steps to reproduce:", "Expected vs Actual:"
- 환경: "Environment:", "Version:"
- 요청: "Could you ~ when you get a chance?"
- 감사: "Thanks for the fix!" / "Appreciate the quick turnaround."

**커밋 메시지(관행)**
- 명령형 현재: "Add", "Fix", "Refactor", "Remove" (과거형 X: "Added" 비권장 관행)
- 예: "Fix null check in order parser", "Add retry to API client"

**회의/스탠드업**
- 명확화: "Sorry, could you repeat that?" "Do you mean ~?" "Just to confirm, ~?"
- 보강: "Let me follow up in the chat." "I'll send details async."
- 진행: "Yesterday I ~, today I'll ~, blocker is ~."

## 3. 콩글리시 직역 함정

| 한국어 | 직역(❌) | 자연스러운 영어(✅) |
|---|---|---|
| 확인 부탁드립니다 | "Confirm please" | "Could you confirm?" / "PTAL" |
| 수고하셨습니다 | "You worked hard" | "Thanks for the work!" / "Great job!" |
| 제 생각에는 ~인 것 같습니다 | "I think it seems like ~" | "I think ~" / "It looks like ~" |
| ~해도 될까요? | "Can I do ~ ?" (맥락 무시) | "Would it be okay to ~?" / "Mind if I ~?" |
| 참고 부탁드립니다 | "Please reference" | "FYI" / "For reference, ~" |

원칙: 한국어 정중 표현을 단어 대치하지 말고, 같은 상황에서 영어권 개발자가 실제 쓰는 표현을 검색·모방.

## 4. 인풋/아웃풋 학습 루프 설계

```
입력(읽기/듣기, i+1)  →  출력(쓰기/말하기, 저위험부터)  →  피드백(용례 대조·리뷰·AI 교정)  →  다시 입력
```
- 입력만: "알아듣는데 못 씀" → 출력 추가.
- 출력만: 화석화(오류 고정) → 피드백 추가.
- 새 표현은 간격 반복으로 고정(→ life-learning).
- 개발자 이점: 매일 보는 영어 문서(입력) + 커밋/이슈/PR(출력 기회)이 이미 환경에 있음.

## 5. 입력원 추천 (개발자용)

- 공식 docs·릴리스 노트·changelog (가장 실무 직결, 반복 노출)
- 활동하는 오픈소스의 이슈/PR 코멘트 (관용표현 관찰)
- 기술 블로그·엔지니어링 블로그
- 컨퍼런스 토크(영어 자막) — 듣기 입력
- RFC·설계 문서 — 격식 있는 기술 영어
- 수준: 70~80% 이해되는 것(i+1). 너무 어려우면 입력 효율↓.
