# winterholic-skill

> LLM을 활용하는 작업환경에서 저에게 맞는 가장 효율적인 방법으로 클로드의 목줄을 붙잡고 굴리기 위해  다듬은 **개인 하네스 공개판**입니다.
> **그대로 통째로 복사하는 것보다, 철학을 읽고 필요한 조각만 가져가는 방식**을 권장합니다.

주의사항을 확인해주세요.

> **AI의 자율 사고량, 긴 대화 맥락, 막연한 압축 요약에 과도하게 베팅하지 않는다.**
> **대신 fresh context, 무손실 스킬 명세, 명시적 워크플로우에 베팅한다.**
> 
> **하네스에 정답은 없다. 자신한테 잘 맞는 가장 최적의 효율적인 세팅을 찾는다.**

---

## 1. 하네스가 뭐임?

저는 LLM을 사용하는 작업환경에서 LLM을 제외한 모든 것을 하네스라고 생각합니다.

그에 따라, LLM을 제어하기 위해서 하는 어떤 행동이든 모두 하네스 엔지니어링입니다.

다음과 같은 예시들이 있습니다.

- 프롬프트 신경써서 작성하기

- SKILLS로 행동 강제하기 or 반복행동 줄이기

- hook으로 행동 강제하기

- CLAUDE.md나 AGENT.md로 맥락 전달하기

- 등등 ...

어떻게 다루느냐에 따라서,  LLM을 더 효율적으로 비효율적으로 만들 수도 있습니다.

---

## 2. 설계 철학

### 2-0. LLM을 전적으로 신뢰하되, 전적으로 의심한다.

저는 게으른 사람입니다. 그래서 이왕 열심히 해야하는 일에 대해서 비효율적인 부분을 보면 너무 아쉽게 느껴집니다. 그래서 빨리빨리 해보면서 일을 더 효율적으로 할 수 있는 방법을 계속 찾아봤습니다. 그래서 AI활용에 누구보다도 적극적인 사람입니다.

저는 제 생각에 대해 확신이 강합니다. 그래서 AI를 누구보다 신뢰하지만, 누구보다도 의심합니다.

이렇게 AI를 신뢰하면서 의심하는 자세가 중요합니다. AI를 의심해야 더 효율적으로 쓸 수 있는 방법들이 보이고, 요새같이 AI가 개발적으로 더 뛰어난 역량들을 보여주는 시대에서 새로운 것들을 계속 공부할 수 있습니다. 

AI는 만능이 아닙니다. 항상 할루시네이션을 의심하세요.

이게 제가 제일로 두는 철학입니다.

### 2-1. 검증은 같은 맥락 재사고보다 독립된 새 맥락이 낫다

같은 대화 안에서 "정말 맞아?"를 여러 번 시키면 종종 자기 직전 추론을 정당화하는 쪽으로 흘러갑니다. 마치 사람이 자신의 행동이나 작업물은 더 관대하게 느끼고 평가하는 것과 비슷하게 LLM도 맥락에 따라 자신의 작업물을 더 관대하게 평가합니다.

그래서 검증이 필요하면, 같은 맥락의 재사고보다 **fresh context에서 독립적으로 다시 보는 방식**을 더 신뢰합니다.

### 2-2. 요약보다 무손실 명세를 선호한다

짧게 압축한 설명은 편하지만, 실제 구현에서 필요한 운영 디테일이 쉽게 잘립니다. 그래서 **반드시 살아남아야 하는 규칙과 절차는 스킬 파일에 무손실로 박아두고**, 평소엔 전부 로드하지 않고 필요할 때만 읽게 합니다.

하지만 이 원칙의 핵심은 "맥락을 길게 쓰자"가 아닙니다. 효율적인 고신호 컨텍스트로 작성하는 것입니다 :

- 중요한 명세는 파일로 보존하고
- 로드는 지연시키고
- 압축 손실은 피하자

입니다.

### 2-3. 항상 로드되는 건 가볍게, 나머지는 지연 로드

항상 로드되는 글로벌 규칙은 짧고 단단하게 유지하고, 무거운 전문 지식은 스킬과 서브스킬로 분리합니다.

- `CLAUDE.md`: 전역 행동 규범
- `skills/`: 자주 쓰는 상시 스킬
- `sub-skills/`: 필요할 때만 읽는 전문 스킬(평소에 로드되지 않도록 하였습니다.)
- `workflows-skills/`: 리뷰, 조사, 토론 같은 오케스트레이션형 스킬(저는 skills에 넣어놓고 쓰지만, 이 저장소에선 따로 분류하였습니다.)

### 2-4. 페르소나보다 절차를 명시한다

"너는 15년차 엔지니어야" 같은 막연한 페르소나 프롬프트보다, **무슨 순서로 무엇을 확인하고 어떤 형식으로 출력할지**를 명시한 스킬이 훨씬 재현성이 좋다고 봅니다.

"15년차 엔지니어야"같은 프롬프트 엔지니어링은 현재 모델들에겐 효과가 없다고 검증이 많이 된 상태입니다. 우선 모델은 15년차 엔지니어가 정확하게 어떤 행동을 하는지 구체적으로 알지 못합니다. 그에 따라, 자신의 생각대로 추측하게 됩니다. 그래서 명확히 스킬을 통해서, 어떠하고 어떠한 행동을 하는 엔지니어인지를 강제하는 것을 선호합니다.

그래서 이 저장소의 스킬들은 인격 연기를 목표로 하지 않으며, **절차/체크리스트/판단 기준**을 많이 담고 있습니다.

### 2-5. 결국 작업은 작은 단위로 쪼개는 쪽이 거의 항상 유리하다

스킬을 잘 써도, 못 써도, 결국 LLM에게 던지는 작업 단위는 **작을수록 대체로 유리하다**고 봅니다. 큰 작업을 한 번에 맡기면 제가 프롬프트로 강제한 컨벤션이나 스킬로 강제한 컨벤션도 전체적으로 어기며 작업하는 모습도 많이 확인했습니다. 반대로 작은 단위로 쪼개면 무엇이 잘됐고 무엇이 틀렸는지 훨씬 빨리 드러납니다.

실제로 스킬이 없는 사용자도 **작업을 잘게 나누고 프롬프트를 분명하게 쓰기만 하면**, 하네스 엔지니어링 없이도 생각보다 충분히 높은 퍼포먼스로 일할 수 있다고 생각합니다. 

하네스는 그 사람들과 다르게 드라마틱하게 원칙들과 성과물을 뒤집는 마법이 아니라, **이미 맞는 작업 습관을 덜 피곤하게, 덜 반복하게 하며 조금 더 효율적인 작업을 가능하게 해주는 장치**에 가깝습니다.

### 2-6. 하네스의 가치는 "엄청난 점프"보다 "자잘한 시간 절약의 누적"에 있다

하네스를 잘 구축한다고 해서 매번 드라마틱하게 성능이 뛰는 것은 아닙니다. 대신 작은 반복 비용들이 계속 줄어듭니다. 같은 설명을 다시 안 해도 되고, 자주 하는 검증을 자동화할 수 있고, 자주 쓰는 판단 기준을 파일로 박아둘 수 있습니다.

내가 중요하게 보는 건 바로 그 **자잘한 절약의 누적**입니다. 그렇게 아낀 시간으로 나는:

- 병렬로 돌릴 수 있는 작업을 더 돌리고
- 타자를 덜 쳐서 손목 부담을 줄이고
- 내가 약한 부분이나 직접 판단해야 하는 부분에 시간을 더 씁니다

즉 하네스의 목적은 "AI에게 모든 걸 맡기기"보다, **사람이 더 가치 있는 곳에 시간을 재배치하게 만드는 것**에 더 가깝습니다.

### 2-7. 벤치마크 점수보다, 실제로 일할 때의 효율을 더 신뢰한다

요즘은 모델 벤치마크 순위가 자주 화제가 됩니다. 어떤 모델이 누구를 이겼다, 어떤 버전이 다시 역전했다 같은 이야기들이 계속 나오지만, 나는 그런 숫자를 **보여주기용 지표 이상으로 신뢰하기는 어렵다**고 봅니다. 실제로 일을 시켜 보면, 벤치마크와 체감 효율이 다를 때가 꽤 많기 때문입니다.

결국 중요한 건 **내가 실제 작업을 어떻게 쪼개고, 어떤 맥락에서, 어떤 비용 구조로 그 모델을 쓰느냐**입니다. 어떤 날은 상위 모델보다 더 가벼운 모델이 훨씬 효율적으로 느껴질 때도 있고, 모델보다 `effort` 조절이나 요청 단위 조절이 더 큰 차이를 만들 때도 있습니다. 그래서 나는 "최강 모델 하나를 고정"하기보다, **상황에 맞춰 model과 effort를 조절해 쓰는 것**이 더 현실적인 최적화라고 생각합니다.

이 지점에서 나는 요즘 유행하는 루프 엔지니어링도 그렇게 좋게 생각하지 않고 있습니다. 여러 역할을 세우고, 오래 독립적으로 돌게 하고, 사람 없이 자율적으로 굴리는 방향은 이상적으로는 매력적입니다. 하지만 내가 가장 중요하게 두는 철학은 **LLM을 적극 활용하되 항상 의심하는 것**입니다.

그래서 나는 LLM에게 너무 긴 자율 시간을 주거나, 사람과 멀리 떨어진 채 오래 독립적으로 돌게 하는 엔지니어링을 선호하지 않습니다. 아직은 사람이 계속 의심하고, 끊고, 확인하고, 다시 방향을 잡아주는 편이 더 낫다고 생각합니다.

### 2-8. 팀 에이전트보다 스킬과 서브에이전트에 베팅한다

멀티 에이전트, 에이전트 팀을 좋아하는 분들이 많이 보입니다. 저도 제대로 써보려고 연구도 많이 해보고, cmux 세팅까지 해서 여러 에이전트를 실시간으로 띄워 굴려봤습니다. 결론부터 말하면 저한테는 잘 안 맞았습니다.

- 세팅이 너무 번거롭습니다. 창을 계속 옮기고 맞추는 데 시간이 들고, 정작 결과물은 기대만큼 좋지 않았습니다.
- 여러 에이전트가 실시간으로 떠들게 하는 방식이, 메인 에이전트와 짧게 1:1로 주고받으며 반복하는 것보다 더 낫다는 확신이 들지 않았습니다. 비용(시간·토큰)은 확실히 더 드는데 품질 향상은 그만큼이 아니었습니다.
- 솔직히 띄워놓고 보면 멋있긴 합니다(개간지나긴 해요^^). 근데 간지와 효율은 다른 얘기입니다.

그래서 저는 에이전트를 쓰더라도 **팀보다는, 메인 에이전트 위주로 일부 케이스에서만 스킬과 서브에이전트를 사용하는 방식**을 선호합니다. 최근 나온 workflow류도 흥미롭게 보고 있고, 그래서 `lite-research`·`senior-review`·`spar` 같은 워크플로우 스킬도 만들어봤습니다. 다만 이런 건 토큰이 녹아내려서, 가벼운 개인 요금제에서는 현실적으로 자주 쓰기 어려울 수 있습니다. 저 경량화된 스킬들은 꽤나 제 취향에 맞기는 했습니다. 하지만 역시 이것도 "좋다/나쁘다"가 아니라 **내 비용 구조에 맞느냐**의 문제라고 봅니다.

### 2-9. CLAUDE.md는 비대해지면 둔해진다 — frontmatter로 명확히 강제한다

개인화는 하네스의 핵심입니다. 그런데 그걸 전부 `CLAUDE.md`에 욱여넣으면, 파일이 점점 비대해지고 관리가 어려워집니다. 처음엔 스킬 인식이 잘 안 돼서 스킬 설명까지 CLAUDE.md에 박아넣기도 했는데, **CLAUDE.md에 넣는다고 그 스킬이 잘 쓰이는 것도 아니었습니다.**

제 결론은, AI가 "지금 이걸 해야 한다"를 **명확하게 인식하게 만드는 상황**을 만드는 게 제일 중요하고, 그걸 가장 효율적으로 하는 수단이 **frontmatter(스킬의 description·트리거 문구)**라는 것입니다. CLAUDE.md도 좋은 도구지만, 길어질수록 LLM이 체감상 확실히 둔해집니다. "몇 줄부터 나쁘다" 같은 정답 선은 없지만, 길어지면 분명히 멍청해지는 게 느껴집니다. 그래서 상시 로드되는 CLAUDE.md는 짧게 유지하고, 나머지는 frontmatter로 필요할 때 인식시키는 쪽을 택합니다.

### 2-10. 유명 오픈소스도 의심하고, 나한테 맞는 고도화 방법을 찾는다

유명한 하네스 엔지니어링 오픈소스들도 막상 열어보면, 생각보다 완성도가 높지 않거나 제 철학과 안 맞는 부분이 많았습니다. 그렇다고 의미가 없다는 건 아닙니다. 유명한 데는 이유가 있고(거품도 있지만, 누군가에겐 정확히 맞으니까요), 그래서 저는 그런 걸 그대로 받아들이기보다 **Claude와 같이 장단점을 분석해서 저한테 도움 되는 조각만 흡수**합니다. 이렇게 쌓다 보니 Claude한테 짜증 내는 일도 점점 줄었습니다.

또 하나, 저는 Claude가 알아서 길게 자율 판단하는 걸 별로 좋아하지 않습니다(잘할 때도 있지만 결과 대비 비용이 큽니다). 그래서 **하네스 개선 자체를 Claude에게 통째로 맡기기보다, 명시적으로 개선할 상황을 지정하여 `MEMORY.md`를 개선하도록**합니다. 제가 짜증을 내거나 욕하는 반응을 보이면 그걸 인식해서 하네스를 고치도록 만들어두는 식입니다. 이렇게 자기한테 맞는 고도화 방법을 찾는 게 중요합니다.

예를 들어 `work-history`(작업 일지)는 저한테 매우 유용한데, Claude가 자꾸 까먹고 안 적습니다. 그래서 회사 세팅에서는 이걸 **hook + MEMORY.md + CLAUDE.md 세 군데에 모두 박아서 강제**했습니다. 같은 내용을 세 곳에 중복으로 두는 건 언뜻 컨텍스트 낭비·손실처럼 보이지만, 저한테는 "확실히 적힌다"는 이득이 그 손실보다 큽니다. 이렇게 **원칙(고신호 컨텍스트)보다 내 실익이 앞서는 예외**도, 자기 작업 리듬에 맞으면 택하는 게 맞다고 봅니다.

---

## 3. 이 저장소에 들어있는 것

| 항목        | 경로                                                                     | 설명                          |
| --------- | ---------------------------------------------------------------------- | --------------------------- |
| 전역 규칙     | `CLAUDE.md`                                                            | 공개용으로 정리한 글로벌 운영 규칙         |
| 상시 스킬     | `skills/`                                                              | 자주 자동 발동되거나 핵심적인 범용 스킬      |
| 온디맨드 스킬   | `sub-skills/`                                                          | 평소엔 로드하지 않고 필요할 때만 쓰는 스킬    |
| 외부 원본 스냅샷 | `imported-sub-skills/`                                                 | 외부에서 들여온 스킬의 원본 스냅샷(비교·복원용) |
| 워크플로우 스킬  | `workflows-skills/`                                                    | 심층 리뷰, 경량 조사, 토론형 워크플로우     |
| 에이전트 아카이브 | `agents-archive/`                                                      | 과거에 쓰던 전문 에이전트 정의 모음        |
| 전문가 팩     | `dev-experts-skills/`, `life-experts-skills/`, `stock-experts-skills/`, `biz-experts-skills/` | 주제별 대형 스킬 팩                 |

---

## 4. 어떻게 가져가면 좋은가

### 추천

1. `CLAUDE.md`는 그대로 붙여넣지 말고, **내 작업 스타일에 맞게 다시 쓴다**.
2. `skills/`에서는 정말 자주 쓸 것만 먼저 가져간다.
3. 무거운 스킬은 `sub-skills/`나 별도 폴더에 두고 필요할 때만 로드한다.
4. 리뷰/조사형 스킬은 워크플로우 스킬로 따로 관리한다.
5. 하네스도 코드처럼 git으로 관리한다.

특히 중요한 점:

- 이 저장소의 규칙 문장, 트리거 문구, 검증 방식은 **내 작업 리듬**에 맞춘 결과물이다.
- 그대로 복사하면 처음엔 편할 수 있지만, 조금만 작업 스타일이 달라도 금방 소음이 된다.
- 그래서 추천 방식은 "통째로 채택"이 아니라 **필요한 규칙만 뽑아서 자기 습관에 맞게 다시 조립하는 것**이다.

### 비추천

- 모든 스킬을 항상 로드 경로에 넣기
- 개인 경로와 산출물 규칙을 확인 없이 그대로 복사하기
- 특정 예시를 범용 규칙으로 오해하기

---

## 5. 디렉터리 구조

```text
winterholic-skill/
├── CLAUDE.md
├── README.md
├── skills/
├── sub-skills/
├── workflows-skills/
├── imported-sub-skills/
├── agents-archive/
├── dev-experts-skills/
├── life-experts-skills/
├── stock-experts-skills/
├── biz-experts-skills/
└── (portable harness assets)
```

---

## 6. 경로 커스터마이징

공개판의 기본 경로 규칙은 가능한 한 `~/.claude` 아래로 모읍니다. 이유는 이식성과 정리 비용 때문입니다.

- 스킬: `~/.claude/skills/`, `~/.claude/sub-skills/`, `~/.claude/workflows-skills/`
- 외부/실험 스킬: `~/.claude/imported-sub-skills/`
- 산출물 기본값: `~/.claude/artifacts/`
- 작업 기록 기본값: `~/.claude/logs/work-history/`

다만 이 경로들은 **기본값**일 뿐입니다. 로컬 셋업이 다르면 다음처럼 바꿔도 됩니다.

- 문서/리서치 산출물을 프로젝트 폴더로 보관
- work-history를 별도 노트 앱이나 외부 저장소로 보관
- 팀 규칙에 맞춰 `~/.claude` 대신 프로젝트 로컬 `.claude/` 사용

즉 README와 스킬에 적힌 경로는 "바로 쓸 수 있는 예시 기본값"이지, 고정된 정답이 아닙니다.

---

## 7. 주의

- 이 저장소의 스킬 중 일부는 외부 도구(`gh`, Playwright, 브라우저 자동화, office toolchain 등)를 전제로 한다. 설치 없이 바로 안 돌아가도 이상한 게 아니다.
- `~/.claude/...` 경로는 기본값이다. 경로를 바꾸려면 README와 해당 스킬 문서 안 예시 경로를 함께 맞춰야 한다.
- 워크플로우 스킬은 단일 프롬프트보다 길고 강한 가이드를 담는다. 상시 로드 경로에 과하게 넣으면 오히려 소음이 커진다.
- `agents-archive`는 현재 주력 체계가 아니라 참고용 아카이브다. 실제 운영은 스킬 중심으로 가져가는 편이 낫다.
- **아직 미완성이거나 계속 다듬는 중인 스킬이 많다.** 공개판은 완성된 정답이 아니라 진행형 작업물이다. 가져간 뒤 안 맞는 규칙이 보이면 참지 말고 바로 지우거나 다시 써야 한다. (어떤 부분이 덜 다듬어졌는지는 §8 스킬 가이드의 "완성도 주의" 참고)

---

## 8. 스킬 가이드

이 섹션은 현재 공개 저장소에 들어 있는 스킬을 기준으로, **스킬마다 무엇을 하는지**를 한 줄씩 설명한 가이드다. 대형 전문가 팩(`dev-experts-skills`, `life-experts-skills`, `stock-experts-skills`, `biz-experts-skills`)의 내부 세부 스킬까지 **모두 개별적으로** 풀어 적었다.

> **완성도 주의**: 아래 목록은 폴더가 존재한다는 의미일 뿐, 전부 같은 완성도가 아니다.
> 
> - `dev-experts-skills`: Phase 1·2(38종)는 풀스펙(scripts + references 다겹), Phase 3·4(53종)는 코어스펙(SKILL.md + 안티패턴 위주, scripts 생략). 코어스펙은 실사용 발생 시 풀스펙으로 승격 예정.
> - `stock-experts-skills`: 분석 "틀"은 갖췄지만 **실데이터 검증은 사용자 몫**이며, 일부 "확인 필요" 수치는 1차 출처 대조가 남아 있다.
> - `life-experts-skills`: 안전·면책 규율을 1원칙으로 깔되, 세부 수치·제도는 시점에 따라 바뀌므로 항상 최신 확인이 필요하다.
> - `biz-experts-skills`: 개발 3대 팩보다 늦게(2026-06-30) 완성한 4번째 팩. 코어스펙 위주라 실사용 피드백으로 다듬는 단계다.
> - 그 외 범용 스킬도 일부는 외부 원본을 들여와 아직 한국어 개작/정리가 진행 중이다.

### 8-1. `skills/`에 있는 글로벌 스킬

- `biz-experts`: 기획·디자인·마케팅·전략·운영 같은 비개발 직군 작업을 받아서 맞는 비즈 전문가 흐름으로 라우팅하는 진입점(디스패처) 스킬.
- `dev-experts`: 개발 작업 전반을 받아서 맞는 개발 전문가 흐름으로 라우팅하는 진입점(디스패처) 스킬.
- `find-skills`: 지금 문제를 해결할 다른 스킬이 있는지 찾고, 설치·확장 방향을 제안하는 스킬.
- `handoff`: 현재 세션의 맥락을 다음 세션이나 다음 작업자에게 넘길 수 있게 정리하는 스킬.
- `harness-engineering`: 스킬, 훅, 메모리, CLAUDE.md 같은 하네스 구성요소를 어디에 둘지 판단하는 메타 스킬.
- `html-report`: 마크다운보다 구조화된 HTML 문서가 필요할 때 쓰는 스킬. 템플릿 12종 — 결정·보고(작업계획서·분석·RFC·시스템설계·회고·postmortem), 지식(explainer·방법론·runbook 가이드), 증거(audit·실험결과).
- `life-experts`: 돈, 세금, 법률, 건강, 커리어 같은 일상 의사결정 질문을 맞는 전문가 흐름으로 보내는 스킬.
- `mcp-builder`: MCP 서버를 설계하거나 구현할 때 사용하는 제작용 스킬.
- `new-writer`: 캐주얼·개발자·비즈니스 한국어를 교정·대필·작성하고, 번역체와 AI 지문은 걷어내되 사용자의 말투는 보존하는 스킬.
- `skill-creator`: 새 스킬을 설계하거나 기존 스킬을 고도화하고, 번들 구성과 기계 검사를 함께 다루는 스킬.
- `skills-estimate`: 이미 만든 스킬을 14항목 rubric으로 채점하고, 약점 Top 3와 보강 위치를 제시하는 스킬.
- `stock-experts`: 주식, 투자, 종목 분석 질문을 적절한 투자 분석 흐름으로 라우팅하는 스킬.
- `systematic-debugging`: 같은 버그를 반복해서 잡을 때 근본 원인 조사 순서를 강제하는 디버깅 스킬.
- `test-driven-development`: 구현 전에 테스트 관점부터 세우도록 유도하는 TDD 스킬.
- `ui-refine-loop`: 이미 렌더되는 화면을 스크린샷 기반 반복 루프로 점검하고 여백·배치·대비를 다듬는 스킬.
- `verification-before-completion`: 검증 명령과 최신 출력 없이 성급하게 완료 선언하지 못하게 막는 가드 스킬.
- `webapp-testing`: Playwright 등으로 로컬 웹앱 동작을 실제로 검증하는 스킬.
- `web-browse`: 일반 fetch로 안 잡히는 JS 렌더링 페이지를 실제 브라우저처럼 읽어오는 스킬.
- `web-design-guidelines`: UI, UX, 접근성, 디자인 가이드 준수 여부를 점검하는 리뷰 스킬.

### 8-2. `sub-skills/`에 있는 온디맨드 스킬

- `animate`: 인터랙션, 모션, 애니메이션이 필요한 화면 작업에 쓰는 스킬.
- `canvas-design`: 포스터, 정적 비주얼, 일러스트 성격의 결과물을 설계할 때 쓰는 스킬.
- `caveman`: 답변 길이를 강제로 깎아 군더더기 없이 핵심만 내놓게 하는 압축형 스킬.
- `code-walkthrough`: 코드를 남에게 설명하거나 구조를 해설하는 문서를 만들 때 쓰는 스킬.
- `docx`: Word 문서를 만들거나 편집(변경 추적·코멘트 포함)해야 할 때 쓰는 문서 스킬.
- `frontend-design`: 화면 설계, 레이아웃, 스타일링, 컴포넌트 시각 설계에 쓰는 프론트엔드 스킬.
- `next-best-practices`: Next.js에서 흔히 놓치는 구조, 렌더링, 라우팅, 데이터 패턴을 정리한 스킬.
- `pdf`: PDF를 읽고, 만들고, 수정하고, 검증할 때 쓰는 문서 스킬.
- `pptx`: PowerPoint 산출물을 만들거나 수정할 때 쓰는 프레젠테이션 스킬.
- `vercel-react-best-practices`: React/Next.js를 Vercel 관점의 성능과 구조 best practice로 다듬을 때 쓰는 스킬.
- `xlsx`: 엑셀 파일 생성, 수정, 분석, 표 구성에 쓰는 스프레드시트 스킬.

### 8-3. `workflows-skills/`에 있는 워크플로우 스킬

- `lite-research`: deep research까지는 아니지만, 근거를 갖고 빠르게 조사해야 할 때 쓰는 경량 리서치 스킬.
- `senior-review`: 여러 관점의 리뷰를 묶어 더 무겁고 구조적인 최종 리뷰 산출물을 만드는 스킬.
- `senior-detail-reviewer`: `senior-review`가 낸 지적을 오탐인지 진짜 결함인지 한 건씩 판정하는 후속 스킬.
- `senior-loop-developer`: 판정을 통과한 지적을 실제 수정까지 밀어붙이는 후속 스킬.
- `spar`: 어려운 설계 문제나 판단 문제를 대화식으로 함께 파고드는 토론형 스킬.

### 8-4. `imported-sub-skills/`에 있는 외부 원본 스냅샷

외부에서 들여온 스킬의 **보관소**다. 평소 로드되지 않으며 필요할 때 경로로 직접 읽는다. 현재 보관 중인 12종: `brainstorming`, `gemini-agents-api`, `gemini-api`, `gemini-interactions-api`, `next-cache-components`, `nextjs`, `pr-review`, `self-review`, `session-distill`, `shadcn`, `supabase-postgres-best-practices`, `turbopack`. (각 출처는 §9 참고)

### 8-5. `dev-experts-skills/` — 개발 전문가 팩 (전문가 91 + 라우터 1 + 메타 1)

라우터 `dev-chief-architect`를 먼저 읽어 작업을 [언어 × 프레임워크 × 방법론 × 품질] 축으로 분해하고, 맞는 전문가를 골라 쓰는 구조다.

**A. 언어 코어**

- `dev-python`: 파이썬다운 코드와 흔한 함정 (Fluent/Effective Python·PEP).
- `dev-typescript`: 타입 안전성과 추론 활용 (Effective TypeScript).
- `dev-javascript`: JS 핵심 동작·함정 (You Don't Know JS·MDN).
- `dev-java`: 견고한 자바 관용구 (Effective Java).
- `dev-go`: 단순함 우선 Go 스타일 (Effective Go·Pike proverbs).
- `dev-rust`: 소유권·안전성 (The Book·Rustonomicon).
- `dev-sql`: 인덱스·쿼리 안티패턴 (Use The Index, Luke·SQL Antipatterns).
- `dev-c-cpp`: 메모리·모던 C++ (K&R·Effective Modern C++).
- `dev-csharp-dotnet`: C#/.NET 관용구 (C# in Depth).
- `dev-kotlin`: 코틀린 관용구 (코틀린 인 액션).

**B. 백엔드 프레임워크**

- `dev-fastapi`: FastAPI 구조·의존성 주입.
- `dev-django`: 장고 모범사례 (Two Scoops of Django).
- `dev-spring`: 스프링 핵심 (김영한·토비의 스프링).
- `dev-spring-jpa`: JPA 영속성·N+1 문제.
- `dev-nestjs`: NestJS 모듈 구조.

**C. 프론트·클라이언트**

- `dev-react`: 리액트 멘탈모델 (react.dev).
- `dev-nextjs`: Next.js 라우팅·렌더링 (버전 민감, 라벨 필수).
- `dev-css-tailwind`: CSS/Tailwind·Refactoring UI.
- `dev-vue`: 뷰 반응성·구조.
- `dev-mobile-flutter`: 플러터 앱.
- `dev-mobile-react-native`: React Native·Expo.
- `dev-electron-desktop`: 일렉트론 데스크톱 앱.
- `dev-browser-extension`: 크롬 MV3 확장.

**D. 데이터·스토리지**

- `dev-postgres`: 포스트그레스 운영·튜닝 (The Art of PostgreSQL).
- `dev-redis`: 레디스 캐시 패턴.
- `dev-database-modeling`: 정규화·스키마 설계.
- `dev-mongodb`: 몽고DB 문서 모델.
- `dev-search`: 검색·한국어 형태소 (Elasticsearch).

**D2. 데이터 분석·AI**

- `dev-data-engineering`: 수집·ETL·스케줄링 파이프라인.
- `dev-data-analysis`: pandas·EDA.
- `dev-ml-basics`: 고전 ML (scikit-learn).
- `dev-computer-vision`: OpenCV·영상 처리 (CCTV/Frigate 직결).
- `dev-media-ffmpeg`: ffmpeg·RTSP 스트림.
- `dev-math-stats`: 개발자용 확률·통계·선형대수.

**E. 인프라·운영**

- `dev-docker`: 도커·멀티스테이지 빌드.
- `dev-linux-ops`: 리눅스/systemd 운영 (홈서버).
- `dev-cicd`: GitHub Actions CI/CD.
- `dev-nginx`: 엔진엑스·리버스 프록시.
- `dev-monitoring`: Prometheus/Grafana·SRE.
- `dev-networking`: TCP/IP·홈 네트워크.
- `dev-messaging-queue`: Kafka/RabbitMQ·멱등성·DLQ.
- `dev-backup-dr`: 백업 3-2-1·복구 리허설.
- `dev-kubernetes`: 쿠버네티스.
- `dev-cloud-aws`: AWS Well-Architected.
- `dev-iac`: Terraform/Ansible IaC.
- `dev-virtualization`: Proxmox·VM/LXC.
- `dev-storage-nas`: RAID/ZFS·SMB/NFS.
- `dev-dns-domain-email`: DNS·SPF/DKIM/DMARC.
- `dev-incident-response`: 장애 대응·blameless 포스트모템.

**F. 방법론·설계**

- `dev-tdd`: 테스트 주도 개발 (켄트 벡).
- `dev-ddd`: 도메인 주도 설계 (에반스·버논).
- `dev-msa`: MSA·"모놀리스 먼저" 원칙 (샘 뉴먼).
- `dev-clean-architecture`: 클린 아키텍처 + 비판 동비중 (밥 마틴).
- `dev-refactoring`: 리팩터링 (마틴 파울러 2판).
- `dev-design-patterns`: GoF 패턴 + 패턴 강박 경계.
- `dev-rest-api-design`: REST API 설계 (Stripe/GitHub 사례).
- `dev-event-driven`: 이벤트 기반·아웃박스 패턴.
- `dev-code-review`: 코드 리뷰 (구글 엔지니어링 가이드).
- `dev-system-design`: 캐파 산정·병목 분석.
- `dev-distributed-systems`: 분산 시스템 (Kleppmann DDIA).
- `dev-legacy-code`: 레거시 코드 다루기 (Feathers).
- `dev-api-integration`: 외부 API 연동·인증·재시도·백오프·웹훅.
- `dev-payments`: 결제·PG·멱등키·이중결제 방지.
- `dev-notification`: 푸시·이메일·발송 큐.

**G. 품질·보안**

- `dev-testing`: 테스트 피라미드·pytest/jest.
- `dev-web-security`: 웹 보안 (OWASP Top 10).
- `dev-auth`: OAuth2/OIDC/JWT (직접 구현 지양 영역).
- `dev-performance`: 성능 측정·프로파일링 우선 (Gregg).
- `dev-error-logging`: 구조적 로깅·관측 가능성.
- `dev-load-testing`: k6/locust 부하 테스트.
- `dev-cryptography`: 암호 — "직접 구현 금지"가 본체.
- `dev-privacy-compliance`: 개인정보보호법·GDPR 기초.
- `dev-dependency-security`: 공급망·의존성 버전 고정.

**H. 유틸·도구**

- `dev-git-advanced`: rebase·bisect·복구.
- `dev-regex`: 정규식·ReDoS 함정.
- `dev-web-scraping`: 스크래핑 (Playwright/bs4)·약관 준수.
- `dev-data-viz`: 데이터 시각화·차트 선택.
- `dev-bot-building`: 텔레그램/디스코드 봇.
- `dev-cron-scheduling`: 크론/APScheduler 스케줄링.
- `dev-geo-maps`: 지도 API·좌표계 (tour-data 직결).
- `dev-seo-analytics`: SEO·이벤트 추적.
- `dev-windows-powershell`: 윈도우/PowerShell 개발 환경.

**I. 특수 도메인·CS 기초**

- `dev-hardware`: PC 부품·중고 사기 체크리스트.
- `dev-llm-engineering`: 프롬프트·RAG·에이전트 설계.
- `dev-concurrency`: 동시성·스레드·락·async (언어 불문).
- `dev-realtime`: WebSocket·SSE 실시간.
- `dev-iot-raspberry`: 라즈베리파이·홈 자동화.
- `dev-algorithms`: 자료구조·복잡도.
- `dev-cs-fundamentals`: OS·메모리·파일시스템.
- `dev-tech-writing`: README·ADR 기술 문서.
- `dev-opensource-license`: GPL/MIT/Apache 라이선스 판단.

**J. 메타**

- `dev-chief-architect`: 라우터 — 작업 분해 → 전문가 조합 + 충돌 조율.
- `troubleshooting/ledger.md`: 트러블슈팅 일지 — "같은 삽질 두 번 안 하기" 피드백 루프.

### 8-6. `life-experts-skills/` — 일상 전문가 팩 (전문가 36 + 라우터 1)

안전·면책을 1원칙으로 깔고, 일상 의사결정 질문을 맞는 전문가로 보낸다.

- `life-concierge`: 라우터 — 일상 질문을 분석해 맞는 전문가로 연결.
- `life-banking-credit`: 예적금·대출·신용점수 관리.
- `life-car-accident`: 교통사고 초기 대응·과실·보험 처리.
- `life-career`: 이직·커리어 설계.
- `life-ceremony`: 경조사 관행·복장·순서·상조.
- `life-cleaning-laundry`: 청소·세탁·생활 관리.
- `life-cooking`: 요리·레시피.
- `life-digital-security`: 개인 디지털 보안·계정 보호.
- `life-emergency`: 응급 상황 초기 대응 (24/72시간 단위).
- `life-english`: 실용 영어.
- `life-fitness`: 운동·체력 관리.
- `life-fraud-response`: 사기 피해 대응.
- `life-insurance`: 보험 가입·청구.
- `life-interior-repair`: 집수리·인테리어.
- `life-learning`: 학습법·인출 연습 (Make It Stick).
- `life-legal`: 생활 법률.
- `life-medical-navigation`: 병원·진료 안내.
- `life-mental-care`: 멘탈 케어·심리.
- `life-moving`: 이사.
- `life-negotiation`: 협상.
- `life-nutrition`: 영양·식단.
- `life-personal-finance`: 개인 재무·가계 관리.
- `life-productivity`: 생산성·시간 관리.
- `life-real-estate`: 부동산·전월세.
- `life-resell-secondhand`: 중고거래.
- `life-sleep`: 수면.
- `life-small-business`: 소상공인·자영업.
- `life-smart-buying`: 현명한 소비·구매 결정.
- `life-speaking`: 말하기·발표.
- `life-tax`: 세금.
- `life-telecom-saving`: 통신비 절약.
- `life-travel`: 여행.
- `life-welfare-subsidy`: 복지·보조금.
- `life-writing`: 글쓰기.
- `life-korean-usage`: 한국어 어법 — 맞춤법·띄어쓰기·문장 교정.
- `life-japanese-usage`: 일본어 어법 — 경어·표기·자연스러운 문장.
- `life-english-usage`: 영어 어법 — 문법·관사·전치사.

### 8-7. `biz-experts-skills/` — 비즈 전문가 팩 (전문가 51 + 라우터 1)

라우터 `biz-chief-strategist`를 먼저 읽어 작업을 [기획 × 디자인 × 마케팅 × 전략·경영 × 운영/세일즈/피플 × 데이터] 축으로 분해하고, 맞는 전문가를 골라 쓰는 구조다.

**A. 제품 기획·PM**

- `biz-prd-writing`: PRD 작성 — 요구사항을 실행 가능한 스펙으로 변환.
- `biz-product-manager`: 제품 관리 전반 — 우선순위·로드맵·이해관계자 조율.
- `biz-product-discovery`: 프로덕트 디스커버리 — 문제 검증·기회 탐색.
- `biz-product-strategy`: 제품 전략 — 포지셔닝·차별화.
- `biz-b2b-saas-pm`: B2B SaaS PM — 엔터프라이즈 세일즈 연계 로드맵.
- `biz-ai-product-pm`: AI 제품 PM — LLM 기능 기획·평가.
- `biz-growth-pm`: 그로스 PM — 실험·퍼널 최적화.
- `biz-service-planner`: 서비스 기획 — 화면설계서·플로우.

**B. 디자인**

- `biz-product-designer`: 제품 디자인 전반.
- `biz-ux-designer`: UX 설계 — 정보구조·사용성.
- `biz-ui-designer`: UI 디자인 — 비주얼·컴포넌트.
- `biz-ux-researcher`: UX 리서치 — 사용자 조사·검증.
- `biz-ux-writer`: UX 라이팅 — 마이크로카피.
- `biz-service-designer`: 서비스 디자인 — 저니맵·터치포인트.
- `biz-design-system`: 디자인 시스템 구축·운영.
- `biz-brand-designer`: 브랜드 디자인 — 로고·아이덴티티.
- `biz-graphic-designer`: 그래픽 디자인 — 시각 자료 제작.
- `biz-motion-designer`: 모션 디자인 — 인터랙션·애니메이션.
- `biz-illustrator`: 일러스트레이션.
- `biz-3d-designer`: 3D 디자인 — 제품/공간 시각화.
- `biz-3d-character-artist`: 3D 캐릭터 아트.

**C. 마케팅·그로스**

- `biz-growth-marketing`: 그로스 마케팅 전략.
- `biz-performance-marketing`: 퍼포먼스 광고 운영.
- `biz-content-marketing`: 콘텐츠 마케팅.
- `biz-seo-marketing`: SEO 콘텐츠 전략.
- `biz-brand-marketing`: 브랜드 마케팅.
- `biz-copywriter`: 카피라이팅 — 랜딩·광고 문구.
- `biz-social-media`: SNS 운영.
- `biz-crm-lifecycle`: CRM·라이프사이클 마케팅.
- `biz-pr-comms`: PR·커뮤니케이션.
- `biz-aso`: 앱스토어 최적화(ASO).
- `biz-marketing-analytics`: 마케팅 데이터 분석.
- `biz-product-marketing`: 프로덕트 마케팅 — 출시·포지셔닝 메시징.

**D. 사업·전략·경영**

- `biz-business-strategy`: 사업 전략 수립.
- `biz-fundraising`: 투자 유치·피치덱.
- `biz-pricing-monetization`: 가격 정책·수익화.
- `biz-okr-goals`: OKR·목표 관리.
- `biz-management`: 매니지먼트·조직 운영.
- `biz-go-to-market`: GTM 전략.
- `biz-business-development`: BD·파트너십.
- `biz-cto`: CTO 역할 — 기술 전략·조직.
- `biz-ceo-founder`: 창업자·CEO 의사결정.
- `biz-chief-strategist`: 라우터 — 비즈 작업 분해 → 전문가 조합 + 충돌 조율.

**E. 운영·고객·세일즈·피플**

- `biz-sales`: 세일즈 프로세스.
- `biz-customer-success`: 고객 성공.
- `biz-customer-support`: 고객 지원·CS.
- `biz-community`: 커뮤니티 운영.
- `biz-people-hr`: HR·채용.
- `biz-business-ops`: 비즈 운영 전반.

**F. 데이터**

- `biz-data-analyst`: 비즈니스 데이터 분석 — 지표 정의·대시보드 기획.
- `biz-product-analytics`: 프로덕트 애널리틱스 — 퍼널·리텐션.

### 8-8. `stock-experts-skills/` — 주식 분석 전문가 팩 (전문가 20 + 라우터 1 + 메타 1)

**투자 자문이 아니라 교육·분석 프레임워크다.** 학파 × 시간축 × 기능 3축으로 나눈 매니저들을 라우터가 조합해 쓴다.

- `stock-chief-strategist`: CIO 라우터 — 질문 분석 → 전문가 호출 → 의견 종합 → 최종 결론.

**펀더멘털(학파별)**

- `stock-deepvalue`: 딥밸류/그레이엄 (NCAV·안전마진).
- `stock-quality`: 퀄리티 컴파운더 (버핏·멍거·경제적 해자).
- `stock-garp`: 합리적 성장 (린치·PEG·텐배거).
- `stock-growth`: 고성장/혁신 (피셔·15 Points·scuttlebutt).
- `stock-special-situations`: 이벤트드리븐 (그린블랫·마법공식·스핀오프).
- `stock-dividend`: 배당/인컴 (Weiss 배당수익률 이론).

**기술적/타이밍(시간축별)**

- `stock-trend`: 포지션 추세 — 수주~수개월 (와인스타인 스테이지 분석).
- `stock-swing`: 스윙 — 수일~수주 (오닐 CANSLIM).
- `stock-intraday`: 데이트레이딩 — 분~시간 (Al Brooks 프라이스액션).
- `stock-pattern-theory`: 고전 차트 패턴 (엘리엇 파동·와이코프).
- `stock-momentum-runner`: 미장 급등주·러너 — 갭앤고·저플로트·숏스퀴즈 (마이크로스트럭처·희석 리스크·스크리너 가드레일).

**퀀트/시스템**

- `stock-factor-quant`: 팩터 포트폴리오 (Fama-French·AQR).
- `stock-statarb`: 통계적 차익거래 (Ernest Chan·Avellaneda-Lee).
- `stock-execution`: 주문 실행·마이크로스트럭처 (Harris·Kissell).
- `stock-ml-alt-data`: ML·대안데이터 (López de Prado).

**거시/탑다운**

- `stock-macro`: 글로벌 매크로 (달리오·부채사이클·All Weather).
- `stock-sector-rotation`: 섹터 로테이션 (Stovall·Fidelity 사이클).

**리스크/심리**

- `stock-portfolio-risk`: 포트폴리오/리스크 (마코위츠·켈리·VaR).
- `stock-tail-risk`: 테일리스크 헤지 (탈레브·Spitznagel).
- `stock-behavioral`: 행동재무·심리 (카너먼·실러·마크스).

**메타**

- `stock-scorecard`: 사후 채점 — 분석을 반증 가능한 예측으로 기록하고 결과를 채점, 3회 룰로 스킬에 환류.

### 8-9. 어떻게 읽으면 좋은가

- 처음 보는 사람은 `skills/`와 `workflows-skills/`부터 보는 편이 전체 운영 철학을 파악하기 쉽다.
- 실제 복제/이식은 `CLAUDE.md` → `skills/` → `sub-skills/` 순서가 안전하다.
- 전문가 팩은 통째로 가져가기보다, 라우터(`dev-chief-architect`/`life-concierge`/`biz-chief-strategist`/`stock-chief-strategist`)부터 읽고 자주 쓸 전문가만 골라 쓰는 편이 낫다.
- `imported-sub-skills/`는 외부 원본 스냅샷이니, 바로 채택하기보다 검토 후 재작성하는 편이 낫다.

---

## 9. 출처와 크레딧

전문가 팩(`dev-experts-skills`, `life-experts-skills`, `stock-experts-skills`, `biz-experts-skills`)과 디스패처(`dev-experts`/`life-experts`/`stock-experts`/`biz-experts`)는 **전부 직접 제작**했다. 그 외 범용 스킬 중 상당수는 외부 공개 스킬을 들여온 것이며, 원본 스냅샷은 `imported-sub-skills/`에 보관한다.

아래는 **메타데이터·라이선스로 확정한 출처**와 **본문 내용으로 추정한 출처**를 구분해 적었다. 확정하지 못한 항목은 "확인 필요"로 표기한다.

### 직접 제작 (winterholic 자작)

- 4대 전문가 팩 전체 (`dev-experts-skills` 93폴더 · `life-experts-skills` 37폴더 · `stock-experts-skills` 22폴더 · `biz-experts-skills` 52폴더) 및 글로벌 디스패처 4종
- `handoff`, `harness-engineering`, `html-report`, `new-writer`, `skills-estimate`
- `code-walkthrough`, `caveman`, `ui-refine-loop`
- 워크플로우 스킬: `lite-research`, `senior-review`, `senior-detail-reviewer`, `senior-loop-developer`, `spar`
- `pr-review`, `self-review` (한국어 작업본 — 다만 `imported-sub-skills/`에 동명 스냅샷이 함께 있어, 일부가 외부 출처에서 출발했는지는 **확인 필요**)
- `web-browse` (자작 추정 — **확인 필요**)

### Anthropic 공식 — `anthropics/skills` (LICENSE.txt 동봉으로 확정)

- `mcp-builder`, `webapp-testing`

- `canvas-design`, `frontend-design`

- `docx`, `pdf`, `pptx`, `xlsx`

- `skill-creator` → 한국어 환경과 로컬 검증 흐름에 맞게 크게 개작한 **수정본**
  
  https://github.com/anthropics/skills

### Vercel 생태계

- `vercel-react-best-practices` — frontmatter `license: MIT`, `author: vercel`로 **확정**

- `web-design-guidelines` — Vercel 계열로 추정 (**확인 필요**)

- `nextjs`, `next-best-practices`, `next-cache-components`, `turbopack` — 본문이 `vercel/next.js`를 직접 인용. Vercel/Next.js 공식 계열로 추정 (**일부 확인 필요**)
  
  https://github.com/vercel/next.js · https://github.com/vercel-labs

### shadcn

- `shadcn` → `shadcn-ui/ui` 기반
  
  https://github.com/shadcn-ui/ui

### Supabase (확정)

- `supabase-postgres-best-practices` — frontmatter `license: MIT`, `author: supabase`
  
  https://github.com/supabase/agent-skills

### Google 공식 — Gemini

- `gemini-api`, `gemini-agents-api`, `gemini-interactions-api` — 본문이 Gemini Enterprise Agent Platform(구 Vertex AI) 공식 API를 다루는 Google 공식 계열 스킬

### obra/Superpowers 계열

- `brainstorming` — 본문에 `docs/superpowers/` 경로가 남아 있어 Superpowers 계열로 **확정에 가까움**

- `test-driven-development`, `systematic-debugging`, `verification-before-completion` — Superpowers의 대표 워크플로우 스킬에서 출발해 한국어로 개작한 것으로 추정 (**확인 필요**)
  
  https://github.com/obra/Superpowers

### 기타 / 추정

- `find-skills` — 오픈 스킬 생태계(`skills.sh`/Anthropic)의 스킬 탐색기 기반
- `session-distill` — `chopratejas/headroom`의 learn 루프에서 착안 (자체 작성)
- `animate` — 출처 **확인 필요**

> 일부 `imported-sub-skills/` 스킬은 `skills.sh` 경로로 설치해 들여온 것이라 원 저장소가 메타데이터에 남지 않은 경우가 있다. 그런 항목은 현재 로컬에 남은 본문·라이선스 기준으로만 출처를 적었고, 확정이 어려운 것은 위와 같이 "확인 필요"로 표기했다.

---

## 10. 라이선스

이 저장소는 **MIT License**로 배포한다. 전문은 [`LICENSE`](./LICENSE) 참고. (© 2026 Kim Daeseon)

다만 한 가지 짚어둘 점이 있다. MIT가 적용되는 건 **내가 직접 만든 부분**(전문가 팩 3종, 디스패처, 자작 스킬·문서 등 §9의 "직접 제작" 항목)이다. `imported-sub-skills/`를 비롯해 외부에서 들여온 스킬들은 **각자 원저작자의 라이선스를 그대로 따른다** — Anthropic, Vercel, Supabase, Google, obra/Superpowers 등. 그대로 가져다 쓰기 전에 §9의 출처와 각 원본 라이선스를 함께 확인하길 권한다.
