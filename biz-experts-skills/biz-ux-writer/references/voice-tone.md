# 보이스 & 톤 · 접근성 · 현지화 · 다크패턴 (실무 레퍼런스)

> biz-ux-writer 실무 레퍼런스. 보이스/톤 프레임워크, 권위 스타일가이드 비교, 접근성 문구, i18n, 다크패턴 회피.
> 1차·공식 스타일가이드 우선. 검증일 2026-07-01.

---

## 1. 보이스 vs 톤 — 핵심 구분

> "You have the same voice all the time, but your tone changes."(Mailchimp)

- **보이스(Voice)** = 브랜드의 변하지 않는 성격. 한 번 정의하면 일관 유지.
- **톤(Tone)** = 상황·사용자 감정 상태에 따라 조절하는 강도. 같은 보이스로 축하할 때와 에러를 알릴 때 톤이 다르다.

Mailchimp의 톤 프레임워크는 **사용자의 감정 상태를 먼저 읽으라**고 요구한다:
> "Your tone also changes depending on the emotional state of the person you're addressing. Are they relieved to be finished with a campaign? Are they confused and seeking our help?"

즉 톤은 "이 화면을 보는 사람이 지금 안도/혼란/불안/만족 중 무엇인가?"에서 출발한다.

> 출처: Mailchimp Content Style Guide — Voice and Tone https://styleguide.mailchimp.com/voice-and-tone/

---

## 2. 상황 → 톤 매핑 (보이스는 일관, 톤만 조절)

| 사용자 감정·상황 | 톤 | 예 |
|---|---|---|
| 성공·완료 (안도·만족) | 경쾌·간결 | "저장됐어요" |
| 온보딩·빈 상태 (기대·막막) | 안내·격려 | "아직 프로젝트가 없어요. [새 프로젝트]로 시작해보세요" |
| 에러·실패 (당황·좌절) | 차분·지지적·자세히, 비난 0 | "카드 승인이 거절됐어요. 다른 카드로 다시 시도해보세요" |
| 파괴·위험 (삭제·결제) | 진지·명확, 농담 금지 | "삭제하면 복구할 수 없어요" |
| 대기·로딩 (초조) | 안심 | "불러오는 중… 잠시만요" |

Material도 같은 원칙: 톤은 사용자 여정의 지점(온보딩·확인·에러)에 따라 변하며, 에러에선
**"casual and conversational → supportive and detailed"**로 전환한다.
Mailchimp: **"more important to be clear than entertaining"** — 심각한 순간엔 위트를 접는다.
**"don't go out of your way to make a joke — forced humor can be worse than none at all."**

**이해관계자 톤 충돌**(법무=경고 강화 vs 마케팅=친근): 정확성·안전 > 친근함. 위험·법적 고지는 진지 톤 우선, 브랜드 위트는 비위험 문구(성공·빈상태)에서만.

> 출처: Material https://m1.material.io/style/writing.html · Mailchimp https://styleguide.mailchimp.com/voice-and-tone/

---

## 3. 브랜드 보이스 정의법 (voice chart)

브랜드 보이스는 형용사 나열로 끝내지 말고 **"이렇다/이렇지 않다" + Do/Don't 예시**의 표로 조작 가능하게 만든다. (상세 정의는 biz-brand-marketing 관할 — 여기선 UX 라이팅에 적용하는 최소형.)

| 보이스 속성 | 이렇다 | 이렇지 않다 | UI 예 |
|---|---|---|---|
| 예: 명료함 | 짧고 직접적 | 장황·현학적 | "저장됐어요"(○) / "귀하의 변경사항이 성공적으로 반영되었습니다"(✗) |
| 예: 따뜻함 | 사람답게, 격려 | 기계적·차가움 | "다시 해봐요"(○) / "작업 실패"(✗) |
| 예: 정직함 | 과장 없음 | 하이프·과약속 | "요금은 청구되지 않았어요"(○) |

Mailchimp 보이스 정의: plainspoken(명료), genuine(진솔), dry humor(건조한 유머). 능동태·평이한 언어·긍정형을 보이스 차원에서 규정.

> 출처: Mailchimp https://styleguide.mailchimp.com/voice-and-tone/ · 브랜드 보이스 상세 정의 = biz-brand-marketing 스킬

---

## 4. 접근성 문구 (a11y)

### 4-1. 링크 텍스트 — 그 자체로 목적이 통해야
스크린리더 사용자는 링크만 목록으로 훑는 경우가 많아, **주변 문맥 없이 링크 텍스트만으로 목적지가 분명해야** 한다.
- ❌ "여기 클릭", "더 보기", "자세히"(문맥 밖에서 무의미)
- ✅ "요금제 비교 보기", "배송 정책 읽기"
- "링크", "~로 이동" 같은 말은 넣지 않는다 — 스크린리더가 이미 "링크"라고 읽는다.
- 다운로드 링크엔 형식·용량 표기: "접근성 체크리스트 내려받기 (PDF, 1.2MB)".

> WCAG 2.4.4 Link Purpose: 링크 목적을 링크 텍스트만으로(또는 프로그램적 문맥과 함께) 판단할 수 있어야 한다.
> 출처: WCAG 2.4.4 · Section508.gov https://www.section508.gov/blog/accessibility-bytes/descriptive-links-and-hypertext/ · Yale Usability https://usability.yale.edu/web-accessibility/articles/links

### 4-2. 아이콘 버튼 · 대체 텍스트
- 아이콘 단독 버튼은 `aria-label`로 동작을 말한다("검색", "메뉴 열기").
- 이미지 대체텍스트(alt): 이미지의 **기능·의미**를 서술. 장식용이면 빈 alt(`alt=""`).
- 버튼은 "타입"이 아니라 라벨을 지칭: "**계속** 누르기"(Material: "Click **Continue**", not "click the Continue button").

### 4-3. 명확성 = 접근성
평이한 언어·능동태·전문용어 회피는 인지 접근성이기도 하다. Polaris는 **7학년 읽기 수준**을 권장("Aim for a 7th grade reading level").

> 출처: Material https://m1.material.io/style/writing.html · Shopify Polaris https://polaris.shopify.com/content/actionable-language

---

## 5. 현지화(i18n) 고려

- **길이 변화**: 독일어·핀란드어는 영어 대비 최대 ~35% 길어질 수 있고(확인 필요 — 언어·문자열별 편차 큼), 한국어↔영어도 버튼 라벨 길이가 달라진다. 고정폭 버튼은 넘침 대비. 텍스트 잘림 금지.
- **문자열 결합(concatenation) 금지**: "You have " + n + " messages" 식 조립은 어순·복수형이 다른 언어에서 깨진다. 완전한 문장을 변수 치환으로("메시지 {count}개"). ICU MessageFormat 등 복수형 규칙을 코드에서 처리(구현은 dev-experts).
- **복수형**: 언어마다 복수 형태 수가 다르다(영어 2, 아랍어 6 등). 한국어는 복수 표지가 약해 "{count}개"로 통일 가능하나, 다국어 지원 시 복수 규칙 위임.
- **문화·관용구·유머**: 지역 관용구·농담·밈은 번역에서 무너진다. 보편적 명확함을 우선.
- **날짜·숫자·통화·이름 순서**: 로캘 포맷 따르기(구현 위임).
- 마이크로카피를 **i18n 키 표**로 산출하면(키 / 원문 / 맥락 주석) 번역자가 문맥을 안다.

> 주: 구체 확장률·복수형 규칙 코드 구현은 dev-experts(i18n) 관할. 여기선 카피 설계 시 고려사항만.

---

## 6. 다크패턴 회피 — 관할권 구분 (중요)

거절 버튼 흐리기, 죄책감 유발("정말 이 혜택을 포기하시겠어요?"), 구독 취소 방해는 **다크패턴**이며 신뢰 훼손 + 규제 리스크다. UX 라이터는 중립·동등한 선택지를 제시한다("취소" / "유지"를 대등하게).

- **명명**: Harry Brignull(2010). 현재 "deceptive patterns"로 개명. https://www.deceptive.design/
- **EU DSA Art.25(1)**: EU 전역 직접적용(2024-02-17), "다크패턴"을 명시한 최초의 EU법. 단 **"온라인 플랫폼" 대상 한정**, 그리고 **이미 UCPD·GDPR이 규율하는 행위엔 적용 제외**(중복 회피). 전면 금지가 아님(EUR-Lex 1차).
- **미국**: FTC법 + ROSCA, FTC 다크패턴 보고서(2022). 캘리포니아 CPRA.
- **집행 사례**:
  - **Epic Games $5.2억**($245M 다크패턴 환불 + $275M COPPA 벌금, 2022, FTC).
  - **Amazon $25억**(2025-09-25 판결, FTC) = $10억 민사벌금 + $15억 환불, 약 3,500만명 대상(1인당 최대 $51, 2025.11~12 자동 환불; FTC 1차 확정). Prime 무단가입·취소 방해.
- ⚠️ "다크패턴은 어디서나 불법" 식 뭉뚱그림 금지 — 관할(EU DSA / 美 FTC·ROSCA / 캘리포니아)을 구분해 말한다.

**중립 라벨 원칙**: 확인/취소 두 선택지의 시각적·언어적 무게를 대등하게. 사용자가 원치 않는 선택으로 유도되는 문구·색·크기 조작 금지.

> 출처: deceptive.design(Brignull) · EUR-Lex DSA Art.25 · FTC(Epic·Amazon 집행)

---

## 7. 권위 스타일가이드 비교표 (공개 문서 기반)

| 축 | Apple HIG | Material (Google) | Mailchimp | GOV.UK | Shopify Polaris |
|---|---|---|---|---|---|
| 핵심 지향 | 사람답고 명료 | 직관·효율·캐주얼·신뢰 | plainspoken·명료 우선 | plain English(강제) | 대화체·직접·간결 |
| 인칭 | 사용자 중심 | 2인칭 "you", "we" 회피 | 독자 시점 | 사용자·명령형 | 직접("add apps") |
| 버튼 대문자 | 플랫폼 규칙 | **sentence case**, ALL CAPS 금지 | — | sentence case | sentence case |
| 에러 | 명확·해결 제시 | **긍정형**("Try again") | 명료 우선 | plain·긍정·"field" 금지 | 직접·해결 |
| 톤 조절 | 상황 적합 | 여정 지점별(에러=지지적) | **감정 상태 기반** | 절제·중립 | 대화체, 7학년 수준 |
| 읽기 검증 | — | 짧게·스캔가능 | 소리내어 | plain 강제 | **소리내어 읽기** |

주: 위 각 셀은 공개 문서 요지를 요약한 것. 정확한 문구·최신판은 각 원문 확인.

- Apple HIG — Writing: https://developer.apple.com/design/human-interface-guidelines/writing (JS 렌더링, 원문 확인 권장)
- Material — Writing: https://m1.material.io/style/writing.html · M3 Style guide: https://m3.material.io/foundations/content-design/style-guide
- Mailchimp: https://styleguide.mailchimp.com/voice-and-tone/
- GOV.UK: https://www.gov.uk/guidance/style-guide/a-to-z
- Shopify Polaris: https://polaris.shopify.com/content/actionable-language
