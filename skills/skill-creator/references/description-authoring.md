# description 작성법 — 스킬의 생명줄

`description` 은 요약이 아니다. **언제 이 스킬을 켤지에 대한 판정 로직**이다.
Anthropic 공식 표현: *"The description field is not a summary, it's a description of when to trigger this skill."*
(출처: `skills/harness-engineering/references/03-patterns/skills-in-practice-anthropic.md`)

스킬 본문이 아무리 좋아도 description 이 부실하면 그 스킬은 존재하지 않는 것과 같다. **트리거 실패의 1차 원인은 언제나 name/description 이다.**

---

## 하드 제약 (어기면 등록 자체가 깨진다)

| 항목 | 제약 | 출처 |
|---|---|---|
| `description` 길이 | **최대 1024자**, 비어 있을 수 없음 | Anthropic 공식 |
| `description` 내용 | **XML/HTML 태그 금지** | Anthropic 공식 |
| `name` | **디렉터리명과 반드시 일치** | 이 하네스 실사고 — `references/gotchas.md` §1 |
| 상시 비용 | 스킬당 **~100토큰** (frontmatter 만 매 세션 로드) | Anthropic 공식 |

1차 자료 백업: `skills/harness-engineering/references/99-sources/progressive-disclosure-anthropic-docs-2026-05-26.md`

기계 확인은 `scripts/check-skill.py` 가 한다. 눈으로 세지 말 것.

---

## 4요소 — 이 순서로 쓴다

### ① What — 한 문장

무엇을 하는 스킬인지. 명사구로 끝내지 말고 동사로 끝낸다.

```
나쁨:  데이터 포맷팅 도구
좋음:  CSV·JSON·Excel 데이터를 정리하고 변환한다
```

### ② When — 트리거 키워드를 실제 어형으로 나열

**사용자가 실제로 칠 법한 표현**을 그대로 적는다. 개념어가 아니라 발화다.

```
나쁨:  데이터 정제가 필요할 때
좋음:  '데이터 정리해줘'·'포맷 바꿔'·'열 추가'·'필터링'·'clean up' 을 언급하면 트리거
```

**한국어를 먼저, 영어를 나중에 병기한다.** 이 사용자는 한국어로 친다. 영어 키워드만 있는 description 은 한국어 발화에서 침묵한다. 반대로 영어만 쓰는 도구형 스킬이면 영어를 먼저 둔다.

발화가 여러 갈래면 **카테고리로 묶는다.** 나중에 "왜 안 걸렸지"를 디버깅할 때 갈래 단위로 좁힐 수 있다.

```
① 명시적 요청: '스킬 만들어줘'·'skill 작성'
② 개선 요청:   '이 스킬 고도화'·'트리거 정확도 높여'
③ 상황 발화:   '이 워크플로우를 스킬로'
```

### ③ When NOT — 경계를 명시한다

인접 스킬과 겹치는 지점을 이름으로 지목한다. 이게 없으면 오발동을 막을 장치가 하나도 없다.

```
좋음:  이미 만든 스킬 채점은 skills-estimate, 외부 스킬 탐색은 find-skills,
      스킬이 맞는 형태인지 자체를 묻는 메타 결정은 harness-engineering 이 담당한다.
      단순 정보 조회·일반 코드 작성에는 발동하지 않는다.
```

`check-skill.py` 는 description 에 부정 신호(`않`·`금지`·`제외`·`skip` 등)가 하나도 없으면 경고한다.

### ④ 모드·강도 (있을 때만)

lite/full 같은 옵션이 있으면 한 줄. 없으면 쓰지 않는다.

---

## pushy 하게, 그러나 1024자 안에서

Claude 는 **스킬을 안 켜는 쪽으로 기운다.** 그래서 description 은 의도적으로 적극적이어야 한다. 동시에 매 세션 로드되는 비용이라 길이가 곧 세금이다. 이 둘이 정면으로 부딪친다.

해소 방법은 길이를 늘리는 게 아니라 **키워드 밀도를 올리는 것**이다.

```
늘리기(나쁨):  "이 스킬은 매우 유용하며 다양한 상황에서 활용할 수 있습니다. 예를 들어..."
밀도(좋음):    "'A'·'B'·'C'·'D' 를 언급하면 트리거. E 에는 쓰지 않는다."
```

설명 문장을 빼고 발화 토큰을 넣는다. 산문은 본문에서 하면 된다.

---

## description-space 경합 — 새 스킬은 남의 트리거를 훔친다

description 은 서로 경쟁한다. 새 스킬을 넣으면 **기존 스킬의 발동률이 떨어질 수 있다.** 특히 상위어를 쓰면(예: "코드 관련 작업") 하위 스킬들을 통째로 가린다.

새 스킬을 만들 때 반드시 확인한다.

1. 기존 스킬 목록에서 **트리거 키워드가 겹치는 스킬**을 찾는다.
2. 겹치면 **양쪽 description 에 서로를 이름으로 지목**한다. 한쪽만 고치면 반쪽짜리다.
3. 상위어를 피하고 구체 발화를 쓴다.

---

## 검증 — 저자가 자기 스킬을 테스트하면 안 된다

**저자의 저주**: 스킬을 쓴 세션은 의도를 이미 컨텍스트에 갖고 있어서, description 이 부실해도 알아서 트리거하고 본문의 모호함을 메워 읽는다. 그 세션의 "잘 되는데요"는 증거가 아니다.

Anthropic 공식 권장은 **인스턴스 분리**다.

> "Work with one instance (Claude A) to create a Skill used by other instances (Claude B)... If Claude B struggles, return to Claude A with specifics... improves Skills based on observed behavior rather than assumptions."

실행 방법은 `../SKILL.md` 의 5단계를 따른다. 요지는 하나다. **fresh 세션이 description 만 보고 스킬을 켜는지를 관찰한다.** 켜지지 않으면 본문을 고칠 게 아니라 description 을 고친다.

출처: `skills/harness-engineering/references/03-patterns/two-instance-skill-authoring.md`

---

## 나쁜 예 / 좋은 예

```yaml
# 나쁨 — 무엇을 하는지만 있고 언제 켤지가 없다
description: "데이터를 포맷팅합니다"

# 나쁨 — 너무 넓어 거의 모든 요청에 걸리거나, 넓어서 오히려 아무것도 안 걸린다
description: "코드 관련 작업을 할 때 사용"

# 좋음 — What + 실제 발화 + 경계
description: "Python FastAPI 프로젝트의 REST 엔드포인트를 만들고 고친다.
  'API 만들어줘'·'endpoint 추가'·'FastAPI 라우터'·'REST API' 를 언급하면 트리거.
  Django·Flask 프로젝트에는 쓰지 않고, 스키마 설계 자체는 dev-experts 가 담당한다."
```
