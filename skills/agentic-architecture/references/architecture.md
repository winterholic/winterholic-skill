# ① 아키텍처 — 워크플로우 / 단일 / 멀티 / 메모리 / 복구 / 긴 호라이즌

최종 검증: 2026-08-26 (심층 lite-research + AgentArch 본문 직접 확인)

## 핵심 판단 1 — "쪼개진 쪽이 결정(쓰기) 권한을 갖는가?"

멀티에이전트 논쟁 전체를 가르는 축이다. "멀티에이전트 찬반"은 잘못 세운 질문이다.

| 서브에이전트가 하는 일 | 판정 | 이유 |
|---|---|---|
| 읽기·조사·탐색, 결과를 문장으로 반환 | **팬아웃 OK** | 결정이 누적되지 않으니 충돌할 것도 없다 |
| 코드·문서·산출물을 직접 쓰기 | **단일 스레드로** | 각 행동이 암묵적 결정을 수반하고, 서로의 결정을 못 봐서 병합이 불가능해진다 |
| 외부 상태 변경(DB 쓰기·배포·결제) | **단일 스레드 + 직렬화** | 위와 같고 되돌리기까지 어렵다 |

`💭해석` Anthropic·Cognition 1차 자료를 대조해 도출. 어느 쪽도 이 형태로 명시하진 않았지만 근거는 강하다(아래).

### 두 진영은 사실 안 싸운다

- `✅확인` Anthropic이 스스로 배제한 조건: *"Some domains that require all agents to share the same context or involve many dependencies between agents are not a good fit for multi-agent systems today. For instance, most coding tasks involve fewer truly parallelizable tasks than research."* — [multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system), 2025-06
- `✅확인` Cognition은 **그 배제된 영역(코딩)**을 다루고, 근거는 성능이 아니라 **결정 일관성**이다. 원칙 2개: *"Share context, and share full agent traces, not just individual messages"*, *"Actions carry implicit decisions, and conflicting decisions carry bad results."* — [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents), Walden Yan, 2025-06-12
- `✅확인` Cognition 본인이 Claude Code를 **모범**으로 든다: *"Claude Code is an example of an agent that spawns subtasks. However, it never does work in parallel with the subtask agent, and the subtask agent is usually only tasked with answering a question, not writing any code."*
- `✅확인` Flappy Bird 사례: 서브에이전트로 쪼갠 결과 한쪽은 Super Mario 풍 배경, 다른 쪽은 스타일 안 맞는 새를 만들어 조정 에이전트가 충돌을 화해시켜야 하는 상황에 빠졌다. 원인은 **서로의 결정·가정을 볼 수 없다**는 것.

## 핵심 판단 2 — 경제성에는 가격표가 있다

`✅확인` *"In our data, agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats."* — Anthropic, 2025-06. **"우리 데이터"라는 한정을 살릴 것** (벤치마크 아님).

`✅확인` 게이트 문장: *"For economic viability, multi-agent systems require tasks where the value of the task is high enough to pay for the increased performance."*

`✅확인` 같은 문서에 **90.2% 우수**(Opus 4 리드 + Sonnet 4 서브)와 **BrowseComp에서 토큰 사용량만으로 성능 분산의 80% 설명**이 공존한다.
`💭해석` 후자를 받으면 전자가 **아키텍처 효과인지 토큰 투입 효과인지 분리되지 않는다.** 멀티에이전트를 권하기 전에 **"같은 토큰을 단일 에이전트에 태우면?"**을 먼저 묻는 근거다.

⚠️ "리서치 시간 90% 단축"은 `✅확인`이지만 **병렬 툴 호출** 도입 효과이지 멀티 대 단일 비교가 아니다. 분리해서 말한다.

`✅확인` 구조적 원인(2025-06 시점): *"LLM agents are not yet great at coordinating and delegating to other agents in real time."*

## 이 축 최고의 ablation — AgentArch

`✅확인`(초록) Microsoft **AgentArch** — [arXiv 2509.10769](https://arxiv.org/html/2509.10769v1). GPT-4.1 / 4o / 4.1-mini / o3-mini / LLaMA-3.3-70B / Claude Sonnet 4 를 기업 워크플로 2종(Time Off 단순, Customer Request Routing 복잡, 각 60샘플)에서 4축 조합으로 평가. 최고점 TO **70.8%**(GPT-4.1), CR **35.3%**(Sonnet 4).

`✅확인` **본문 직접 확인 완료(2026-08-26).** 아래는 원문 축자 기준이다.

| ablation | 결과 | 함의 |
|---|---|---|
| 메모리 (전체 vs 요약) | *"variation in memory management styles and orchestration strategies both had minimal impact on scores."* 예: GPT-4.1 단일+function calling+thinking에서 **70.8% vs 70.8%** | 메모리를 떼도 성능이 안 떨어진 사례. **오케스트레이션 전략도 같이 무영향이었다** |
| thinking tool | GPT-4.1 단순 과제 **48.5% → 70.8%**. o3-mini **55.8% → 56.7%**(사실상 무효). 복잡 라우팅 과제는 *"minimal impact across all models"* | 추론 모델엔 중복, **복잡한 과제엔 전 모델에서 무효** |
| ReAct vs native function calling | function calling 우세. 환각이 ReAct 설정에서 집중 | ReAct는 단일 에이전트에 더 적합 |
| 멀티 vs 단일 (최종 결정 정확도) | **GPT-4.1: 멀티 97~99% vs 단일 79~86%** / **Sonnet 4: 멀티 84~87% vs 단일 72~76%** — 단 Sonnet 4의 *총점* 최고는 단일+function calling(전부 33% 이상) | **지표에 따라 결론이 정반대로 뒤집힌다** |
| 재현성 | *"Passˆk scores across all models and agentic configurations peak at 0.0634"* — **k=8에서 6.34%** | 아키텍처 선택보다 재현성 붕괴가 더 큰 문제 |
| 모델 의존성 | **o3-mini CV 143.7%** (*"extreme sensitivity to architectural choices"*) vs Sonnet 4 **32.1%**, GPT-4.1 **27.0%**(단순 과제) | **"이 아키텍처가 최고"라는 답은 없다** |

`💭해석` 멀티 vs 단일 행이 이 표의 핵심이다 — **총점으로 보면 단일이 이기고 최종 결정 정확도로 보면 멀티가 이긴다.** 즉 "멀티에이전트가 더 나은가"라는 질문은 **어느 지표를 볼지 정하기 전까지 답이 없다.** 사용자가 이 질문을 하면 먼저 "무엇을 최적화하려는가"를 되묻는다.

**자문에 쓰는 방식**: "메모리·플래닝·reflection을 다 붙이면 좋아진다"는 이론이 이 표 하나로 깨진다. 구성요소를 더하자는 제안에는 **"떼봤을 때 떨어지는지 재라"**고 답한다.

## Reflection / self-critique — 검증 신호 없으면 금지

`✅확인` Huang et al., *Large Language Models Cannot Self-Correct Reasoning Yet* — [arXiv 2310.01798](https://arxiv.org/abs/2310.01798), ICLR 2024. 외부 피드백 없는 **intrinsic self-correction은 추론 과제에서 성능을 못 올리고 오히려 떨어뜨린다.** 원인은 LLM이 자기 답의 오류를 판단하지 못하는 것.

`✅확인` 조건을 정리한 비판적 서베이 — [arXiv 2406.01297](https://arxiv.org/html/2406.01297v3), *When Can LLMs Actually Correct Their Own Mistakes?*

**판정 규칙**: reflection은 **외부 검증 신호(테스트 실행 결과·컴파일러·툴 에러·정답 오라클)가 있을 때만** 값한다. 그게 없으면 self-critique 층은 토큰만 태우고 성능을 깎는다. 이 도메인에서 가장 자주 잘못 붙이는 패턴이다.

`⚠️미검증` 단일 에이전트가 멀티에이전트 토론을 이겼다는 결과 — [arXiv 2604.02460](https://arxiv.org/abs/2604.02460), *Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Budgets*. **동일 사고 예산 조건**이 핵심이다(위 "토큰 15배" 논점과 정확히 같은 지적).
`🔴뒤집힘(2026-08)` ~~이 결과를 arXiv 2508.07407로 귀속~~ — 그 ID는 *Self-Evolving AI Agents* 서베이다. 출처 귀속 오류.

## 에이전트 메모리 — 저장량이 아니라 write gate가 본체

`⚠️미검증` *How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior* — ACL 2026 long #27 (Xiong et al.), https://aclanthology.org/2026.acl-long.27/

입력이 검색된 메모리의 입력과 유사하면 출력도 그 기록을 그대로 따라간다(**experience-following**). 여기서 두 실패가 파생:
- **error propagation** — 과거의 부정확이 누적된다
- **misaligned experience replay** — 도움 안 되거나 오히려 오도하는 경험이 재생된다

처방은 **저장 확대가 아니라 메모리 뱅크의 품질 규제**이고, 미래 과제 평가 결과를 저장된 메모리의 **공짜 품질 라벨**로 쓸 수 있다고 제안한다. LLM이 계속 갱신하는 메모리는 유용했던 것도 결함화된다는 관측 포함.

**자문에 쓰는 방식**: "메모리를 붙이자"는 제안에 **"무엇을 안 쓸지 정했나"**를 묻는다. 위 AgentArch의 메모리 ablation 무영향과 합치면 — 메모리는 기본값이 아니라 입증 책임을 지는 쪽이다.

## 긴 호라이즌 붕괴 — 시간이 갈수록 무너진다

`✅확인` *Diagnosing and Mitigating Context Rot in Long-horizon Search* — [arXiv 2606.29718](https://arxiv.org/abs/2606.29718) (Xia·Wang·Huang·Liu, 2026-06-29 제출 / 08-04 개정). **premature termination**(컨텍스트 윈도가 남았는데도 먼저 포기하거나 불확실한 오답을 내는 것)을 새 실패모드로 규정하고, 난이도를 통제하면 **조기종료율이 컨텍스트 길이와 양의 상관**을 보인다.
컨텍스트 관리 7기법을 test-time scaling으로 분석 — behavior-aware filtering이 집계방식 3종에서 2.6~4.9% 향상. **어떤 기법이 좋은지는 모델 특성에 의존.**

`✅확인` **SlopCodeBench** — [arXiv 2603.24755](https://arxiv.org/abs/2603.24755). 자기 코드를 반복 확장시키는 설정: **20문제·93체크포인트·11모델**, 궤적의 **80%에서 구조 침식, 89.8%에서 verbosity 상승**. **어떤 에이전트도 문제를 끝까지 풀지 못했고 최고 체크포인트 해결률 17.2%.**
`🔴뒤집힘(2026-08)` ~~"36문제·196체크포인트·77%·75.5%"~~ — 전부 틀린 수치였다. 위 값이 원문 초록이다.

`⚠️미검증` 원인을 컨텍스트 길이보다 넓은 **trajectory-induced degradation**(누적 실행 자체가 후속 작업을 어렵게 만듦)으로 재정의하는 연구 — arXiv 2607.27283. 짧은 변형에서 40~50% 성공하던 과제가 긴 상호작용 이력에 박히면 10% 미만으로 떨어진다고 보고(관련 정보가 컨텍스트 안에 남아 있어도). **미검증이지만 프레이밍 충돌로서 중요** — 이게 맞으면 "컨텍스트를 줄이면 해결된다"가 틀린다.

**설계 규칙**: 긴 작업은 **주기적 컨텍스트 리셋 / 서브에이전트 격리 / 재계획**을 처음부터 넣는다. 나중에 붙이는 게 아니다.

`✅확인` compaction을 만병통치로 쓰지 말 것 — Cognition 본인이 압축 모델에 대해 *"hard to get right... It takes investment into figuring out what ends up being the key information"*이라 했고 도메인 파인튜닝까지 갔다.

`⚠️미검증` Anthropic context engineering(2025-09-29): 서브에이전트의 1차 근거는 분업이 아니라 **컨텍스트 격리** — 상세 탐색을 서브에이전트에 가두고 리드는 종합에만 집중. just-in-time 로딩(경량 식별자만 유지, 툴로 런타임 로드), compaction 시 아키텍처 결정·미해결 버그·구현 세부는 보존하고 중복 툴 출력은 버린다. *(축자 미확인)*

## 에러 복구 — 재시도는 지고 재계획이 이긴다

`⚠️미검증` *When Tools Fail: Benchmarking Dynamic Replanning and Anomaly Recovery in LLM Agents* — [arXiv 2606.05806](https://arxiv.org/html/2606.05806). 이진 Task Success Rate를 넘어 **Perturbation Recovery Rate**와 **Recovery Cost**를 도입해 순수 재계획 능력을 분리하고 비효율적 시행착오를 벌점화한다. 주입 오류: timeout, 5xx, rate limit, malformed output, partial result. 보고된 것 — **내결함성 스케일링이 3.66배 느리고, 암묵적 실패에서 PRR이 약 37% 하락.**

`🔴뒤집힘(2026-08)` ~~"구조화 피드백 9/100→37/100, reason-guided replanning 55/100"~~ — **어느 논문에도 없는 수치다.** 검색 스니펫 출처. 인용 금지.

`⚠️미검증` *Why Retrying Fails: Context Contamination in LLM Agent Pipelines* — arXiv 2605.08563. **오염된 컨텍스트 안에서 재시도하는 것 자체가 문제**라는 정면 반증 리드.

`💭해석` 종합하면 설계 규칙은 **"재시도 예산보다 재계획 트리거 설계"**다. 같은 컨텍스트에서 N번 다시 부르는 루프는 오염을 키운다. 실패했으면 컨텍스트를 자르고 계획을 고친다.

## 실패 패턴 — 구조적이지 프롬프트 버그가 아니다

`✅확인` MAST — *Why Do Multi-Agent LLM Systems Fail?* [arXiv 2503.13657](https://arxiv.org/abs/2503.13657), NeurIPS 2025. 7개 시스템 **1,642 트레이스**, 14개 실패 모드를 3범주로. 분포 **FC1(명세·시스템 설계) 43.9% / FC2(에이전트 간 정렬 실패) 32.15% / FC3(태스크 검증) 23.95%**.
트레이스 구성: ChatDev 230, MetaGPT 330, **AG2/MathChat 427**, Magentic-One 195, HyperAgent 30, AppWorld 30, OpenManus 30.

`✅확인` **프레임워크를 바꾸면 실패가 줄지 않고 이사한다** — 동일 조건(GPT-4o, ProgramDev-v2)에서 MetaGPT는 ChatDev보다 FC1·FC2 실패가 60~68% 적지만 **FC3 실패는 1.56배 많다.**

`✅확인` 개입 실험: ChatDev에서 역할 명세 개선 **+9.4%p**, 상위 목표 검증 추가 **+15.6%p**. **그럼에도 절대 완료율은 낮게 남아** 저자들은 전술적 수정만으로 부족하고 **구조적 재설계**가 필요하다고 결론.

`✅확인` 시스템별 실패 지문이 있다 — AppWorld=조기 종료, OpenManus=단계 반복, HyperAgent=단계 반복+부정확한 검증. **"one-size-fits-all 해법은 없다."**

`🔴시효주의` "멀티에이전트 실패율 41~86.7%"는 그대로 쓰지 말 것 — 특정 프레임워크·벤치마크 조건의 값이 일반화돼 유통된 것.

## 미확인 (gap)

**해결됨(2026-08-26)**: AgentArch 본문 수치 전부 원문 확인 — 메모리 70.8 vs 70.8, thinking tool 모델별, 멀티/단일 최종결정 정확도(GPT-4.1·Sonnet 4 양쪽), pass^k 0.0634(k=8), CV 143.7/32.1/27.0.

남은 것:
- 멀티에이전트를 걷어낸 팀의 **실명 프로덕션 후기** 미확보(HN 스레드는 ID 미검증). Cognition 글이 현재 가진 최선.
- arXiv 2607.27283(trajectory-induced degradation)과 2605.08563(재시도 컨텍스트 오염) 원문 미확인. 전자는 "컨텍스트를 줄이면 해결된다"를 반박하는 프레이밍이라 확인 가치가 높다.
- 복구 전략 서열(재계획 > 에러메시지 개선 > 단순 재시도)의 **정량 근거 없음** — 방향만 있다.
- 2026-08 기준 Anthropic 포스트의 15배·90.2% 갱신 여부 미확인. Cognition의 2025-06 이후 입장 변화도 미조사 — **1년 이상 지났으므로 자문 전 검색 권장.**
