# life-english-usage — 항목별 어법 가이드

> 실무 빈발 항목을 **판별 규칙 + Language-Change Index 등급**으로 정리. 등급 정의와 출처는 `evidence.md`, 가이드 충돌은 `style-guides.md`.
> 처리 규칙: **stage 1~2 = 교정 / stage 3 = 격식 문서만 / stage 4~5 = 교정 안 함 / [미신] = 해방 안내**

## 1. 관사 — 판정 순서도

```
명사를 만난다
├─ 고유명사인가? → 무관사 (단 The United States, the Netherlands 등 관용 예외)
├─ 셀 수 있는가?
│   ├─ 예 · 단수 → 반드시 한정사 필요 (a/an/the/my/this…)
│   │       └─ 청자가 어느 것인지 아는가?
│   │            ├─ 예 → the   (앞서 언급 / 유일 / 문맥상 특정)
│   │            └─ 아니오 → a/an   (첫 등장 / 여럿 중 하나)
│   └─ 예 · 복수 → 총칭이면 무관사, 특정이면 the
└─ 아니오(불가산) → 무관사. 단 한정되면 the (the water in this cup)
```

### 자주 틀리는 관사 사례

| ❌ | ✅ | 이유 |
|---|---|---|
| I sent you email. | I sent you **an** email. | 가산 단수 |
| He is engineer. | He is **an** engineer. | 직업 = 가산 단수 |
| in the Korea | in Korea | 국가명 무관사(예외군 제외) |
| I go to the home. | I go home. | home은 부사 용법 |
| The life is hard. | Life is hard. | 총칭 추상명사 |
| Open the file A. | Open file A. | 고유 식별자 |
| discuss about the issue | discuss the issue | discuss는 타동사 |
| I have a headache/**the** flu | 둘 다 맞음 | 질병별 관용이 다름 |

> **총칭 3형식**: `Dogs are loyal.`(복수 무관사, 가장 자연) / `A dog is loyal.`(임의의 한 마리) / `The dog is loyal.`(종 전체, 격식·학술). 셋 다 맞으나 뉘앙스가 다르다.

## 2. 가산 / 불가산

### 항상 불가산 (복수형 ✕)
`information, advice, research, equipment, software, hardware, furniture, luggage, baggage, evidence, knowledge, progress, feedback, homework, work(노동), traffic, weather, news(형태는 s이나 단수)`

| ❌ | ✅ |
|---|---|
| many informations | much information / many pieces of information |
| an advice | a piece of advice |
| feedbacks | feedback / comments |
| equipments | equipment / pieces of equipment |
| a research | research / a research project / a study |
| staffs (직원들) | staff / staff members |

### 둘 다 되는 것 (의미가 달라짐)
| 불가산 | 가산 |
|---|---|
| experience (경험 일반) | an experience (한 사건) |
| time (시간) | three times (횟수) |
| paper (종이) | a paper (논문·신문) |
| room (공간) | a room (방) |
| business (사업) | a business (회사) |

### data — 등급 주의
- `data` 복수 취급(`data are`) = 전통·학술. `data` 단수 취급(`data is`) = **stage 4~5**, 이미 광범위 수용.
- **`a data` / `datas`는 stage 1** (오류).
- → `data is`를 교정하지 않는다. 학술 투고 시 저널 규정만 확인.

## 3. 시제 · 상

| 형태 | 쓰는 때 | 예 |
|---|---|---|
| 단순과거 | **과거 시점이 명시**되거나 끝난 사건 | I fixed it **yesterday**. |
| 현재완료 | 과거 사건의 **현재 결과·경험·계속** | I've fixed it. (지금 고쳐진 상태) |
| 과거완료 | 과거보다 더 앞선 사건 | The build **had failed** before I pushed. |
| 현재진행 | 지금 진행 / 예정된 가까운 미래 | I'm reviewing it now. / I'm meeting him tomorrow. |
| 현재 | 습관·일반 사실·**기술 문서의 동작 서술** | This function **returns** a list. |

**핵심 규칙**: 현재완료 + 명시적 과거 시점 = 오류 (stage 1).
- ❌ `I have finished it yesterday.` → ✅ `I finished it yesterday.`
- ❌ `When have you arrived?` → ✅ `When did you arrive?`

**기술 문서**: API·코드 동작은 **현재형**이 관례 — `The endpoint returns 404 if not found.` (과거형·미래형 아님)

**AmE/BrE**: `Did you eat yet?`(AmE 수용) ↔ `Have you eaten yet?`(BrE 선호). 둘 다 오류 아님.

## 4. 전치사 — 빈발 오류

| ❌ | ✅ | 비고 |
|---|---|---|
| discuss about | discuss | 타동사 |
| explain me | explain **to** me | |
| answer to the question(동사) | answer the question | 명사는 the answer to |
| married with | married **to** | |
| depend of | depend **on** | |
| consist **of** ○ / comprise **of** ✕ | comprise (단독) | comprise of는 stage 2~3 |
| in Monday | **on** Monday | 요일=on, 월·연=in, 시각=at |
| on the morning | **in** the morning | 단 on Monday morning |
| arrive **to** | arrive **at**(지점) / **in**(도시·국가) | |
| different **with** | different **from**(표준) / **than**(AmE 구어, stage 4) | |
| in the internet | **on** the internet | |
| responsible **of** | responsible **for** | |
| interested **on** | interested **in** | |

**시간 전치사 요약**: `at` 시각·시점(at 3 p.m., at night) / `on` 날짜·요일(on May 1) / `in` 월·계절·연·기간(in 2026, in an hour)

## 5. 주술 일치

| 규칙 | 예 |
|---|---|
| 삽입구는 무시 | The **list** of items **is** … |
| each/every/either/neither = 단수 | **Each** of them **has** … |
| a number of = 복수 / the number of = 단수 | A number of issues **were** … / The number of issues **is** … |
| either A or B → **B**에 일치 | Either the manager or the **members are** … |
| 집합명사 | AmE 단수(The team is) / BrE 복수 가능(The team are) |
| there is/are | 뒤 명사에 일치. `there's` + 복수 = **stage 4**(구어 보편) |
| 학문명 -ics | 단수 — Statistics **is** a field. |
| 금액·거리·시간 덩어리 | 단수 — Ten dollars **is** enough. |

## 6. Dangling / Misplaced modifier

**규칙**: 분사구·부정사구의 의미상 주어 = 주절 주어.

| ❌ | ✅ |
|---|---|
| After reviewing the PR, the tests failed. | After **I reviewed** the PR, the tests failed. |
| Having deployed, the site crashed. | **After we deployed**, the site crashed. |
| To improve performance, the cache was added. | To improve performance, **we added** the cache. |
| Running slowly, I restarted the server. | **Because it was running slowly**, I restarted the server. |

**Misplaced only**: 위치에 따라 뜻이 갈린다.
- `I only tested the API.` (테스트만 했다)
- `I tested only the API.` (API만 테스트했다) ← 대개 이 뜻을 의도

## 7. 구두점

### Comma splice (stage 1~2)
독립절 둘을 쉼표로만 연결 ✕ → 세미콜론 / 등위접속사 / 마침표.

### Oxford comma
`A, B, and C`의 마지막 쉼표. **CMOS 사용 / AP 미사용.** 둘 다 맞다 → 지정 가이드에 따른다. 모호함이 생기면 AP도 사용을 권한다.

### 세미콜론
- 밀접한 두 독립절: `The build failed; I'll investigate.`
- 항목 안에 쉼표가 있는 목록: `Seoul, Korea; Tokyo, Japan; Paris, France`

### 대시 / 하이픈
| 기호 | 용도 |
|---|---|
| 하이픈 `-` | 복합 수식어 — a **well-known** issue |
| en dash `–` | 범위 — pages 10–20 |
| em dash `—` | 삽입·강조 — The result — surprisingly — held. |

**복합 수식어 하이픈**: 명사 **앞**에 올 때만 — `a well-known bug` / `The bug is well known.`

### 인용부호와 구두점 (AmE)
마침표·쉼표는 **인용부호 안쪽** — `He said "yes."` (BrE는 논리적 배치 허용)

## 8. Wordiness — 치환표

| ❌ | ✅ |
|---|---|
| due to the fact that | because |
| in order to | to |
| at this point in time | now |
| in the event that | if |
| has the ability to | can |
| make a decision | decide |
| provide assistance to | help |
| in spite of the fact that | although |
| a large number of | many |
| it is important to note that | (삭제) |
| basically / actually / really | (대개 삭제) |

## 9. 혼동 어휘

| 쌍 | 구분 |
|---|---|
| affect / effect | affect=동사(영향 주다) / effect=명사(효과). 단 effect 동사=초래하다 |
| its / it's | its=소유 / it's=it is |
| their / there / they're | 소유 / 장소 / they are |
| then / than | 시간 / 비교 |
| complement / compliment | 보완 / 칭찬 |
| principal / principle | 주요한·교장 / 원칙 |
| ensure / insure / assure | 보장 / 보험 / 안심시키다 |
| e.g. / i.e. | 예시 / 즉(바꿔 말하면) |
| fewer / less | 가산 / 불가산 (`less items`=stage 3~4, 구어 보편) |
| among / between | 셋 이상 / 둘 — 단 개별 관계면 between도 셋 이상 가능 |
| comprise / compose | 전체가 부분을 comprise / 부분이 전체를 compose |
| lay / lie | 타동(눕히다) / 자동(눕다) |
| loose / lose | 느슨한 / 잃다 |
| stationary / stationery | 정지한 / 문구류 |

## 10. 비즈니스 이메일 레지스터

| 격식 | 인사 | 맺음 |
|---|---|---|
| 공식(첫 접촉) | Dear Mr./Ms. Lastname, | Sincerely, / Best regards, |
| 준격식(업무) | Hi Firstname, | Best, / Thanks, |
| 사내·친밀 | Hey, / (생략) | Cheers, / Thanks! |

| 기능 | 표현 |
|---|---|
| 후속 | I'm following up on… / Just checking in on… |
| 요청 | Could you…? / Would you mind…? / I'd appreciate it if you could… |
| 거절 | Unfortunately, we won't be able to… / I'm afraid… |
| 사과 | I apologize for… (격식) / Sorry about… (비격식) |
| 첨부 | Please find attached… (격식·다소 구식) / I've attached… (자연) |
| 재촉 | I wanted to check on the status of… |

> **주의**: `Please find attached`는 문법 오류는 아니나 다소 구식으로 읽힌다 → [선호]. `Dear Sir/Madam`은 수신자를 알 수 없을 때만.
> 축약형(`I'm`, `don't`)은 준격식~비격식. 최고 격식 문서에서만 완전형을 쓴다.
