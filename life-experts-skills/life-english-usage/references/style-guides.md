# life-english-usage — 스타일가이드 대조

> **어느 가이드를 쓰는지 모르면 판정이 갈린다.** 아래 항목들은 "틀림"이 아니라 "가이드가 다름"이다. 출처는 `evidence.md`.

## 0. 판정 전 확인 순서

```
① 사용자가 지정한 스타일가이드가 있는가?
   ├─ 있음 → 그것을 따른다 (이 문서에서 해당 열만 본다)
   └─ 없음 → ② 로
② 문서 종류로 추정
   ├─ 학술·출판·일반 산문 → CMOS
   ├─ 보도자료·뉴스·홍보 → AP
   ├─ 사회과학 논문 → APA
   ├─ 기술 문서(소프트웨어) → Microsoft Writing Style Guide / Google Developer Docs
   └─ 불명 → CMOS를 기본값으로 쓰되 "기본값임을 명시"
```

## 1. 주요 가이드 성격

| 가이드 | 영역 | 톤 |
|---|---|---|
| **The Chicago Manual of Style (CMOS)** 18th ed. (2024) | 출판·학술·일반 산문 | 상세·보수적. Garner가 문법장 집필 |
| **AP Stylebook** | 언론·보도·홍보 | 간결·공간 절약 |
| **APA** 7th ed. | 심리·사회과학 논문 | 인용·편향 없는 언어 강조 |
| **MLA** 9th ed. | 인문학 | 인용 중심 |
| **Microsoft Writing Style Guide** | 소프트웨어 UI·문서 | 친근·짧게·2인칭 |
| **Google Developer Documentation Style Guide** | 개발자 문서 | 명료·포용적 언어 |

## 2. CMOS ↔ AP 충돌표 (가장 자주 부딪히는 것)

| 항목 | CMOS | AP |
|---|---|---|
| **Oxford comma** | **사용** (A, B, and C) | **미사용** (A, B and C) — 모호할 때만 |
| **숫자** | 1~100 문자 표기(일반 원칙) | 1~9 문자, 10 이상 숫자 |
| **시각** | 10:00 a.m. | 10 a.m. |
| **날짜** | July 4, 2026 | July 4, 2026 (월 약어: Jan., Feb., Aug., Sept., Oct., Nov., Dec.만) |
| **퍼센트** | percent 또는 % (문맥) | % 사용 (2019년부터) |
| **제목 대문자** | headline-style 상세 규칙 | 주요 단어 대문자, 4자 이하 전치사 소문자 |
| **긴 대시** | em dash, 공백 없음 — like this | em dash, **공백 있음** — like this |
| **주(州) 이름** | 전체 표기 선호 | 문맥별 약어 |
| **책 제목** | *이탤릭* | "따옴표" |

> 두 가이드 모두 "맞다". **Oxford comma를 AP 문서에 강요하거나 그 반대를 하면 오교정**이다.

## 3. 기술 문서 가이드 (개발자 문서 작성 시)

| 항목 | 권장 |
|---|---|
| 인칭 | **2인칭 you** (사용자 대상). `we` 남용 금지 |
| 시제 | **현재형** — "The API returns…" (will return ✕) |
| 태 | 능동 우선. 단 주체가 시스템이고 무관하면 수동 허용 |
| 명령문 | 절차는 명령형 — "Click **Save**." |
| 조건 순서 | 조건을 앞에 — "If the build fails, check the logs." |
| 축약형 | 허용·권장 (친근함) — don't, you'll |
| 포용적 언어 | whitelist/blacklist → allowlist/denylist, master/slave → primary/replica |
| 성별 | singular they 사용 |

> Microsoft·Google 가이드 모두 **포용적 언어**를 명시적으로 요구한다. 기술 문서 교정 시 이 항목을 반드시 점검한다.

## 4. 인용·참고문헌 형식 (요약)

| 가이드 | 본문 인용 | 특징 |
|---|---|---|
| CMOS notes-bibliography | 각주 번호 | 인문학. 각주 + 참고문헌 |
| CMOS author-date | (Smith 2020, 15) | 과학·사회과학 |
| APA | (Smith, 2020, p. 15) | 저자-연도. DOI 필수화 경향 |
| MLA | (Smith 15) | 저자-페이지 |
| IEEE | [1] | 번호순 |

> 상세 형식은 각 가이드 원문을 확인한다. 이 스킬은 **형식이 섞였는지**(한 문서에 APA와 MLA 혼용)를 잡는 수준까지만 다루고, 개별 서지 항목 조판은 범위 밖이다.

## 5. 포용적 언어 (inclusive language)

주요 가이드가 모두 이동 중인 영역이다. Garner 5판도 이 방향으로 갱신됐다.

| 피할 표현 | 대안 |
|---|---|
| chairman | chair, chairperson |
| manpower | workforce, staffing |
| mankind | humanity, humankind |
| he (총칭) | they (singular) / 복수로 재작성 |
| guys (혼성 집단) | everyone, folks, team |
| blacklist / whitelist | denylist / allowlist |
| master / slave | primary / replica, main / secondary |
| sanity check | quick check, validation |
| grandfathered | legacy, exempt |
| crazy / insane (비유) | intense, surprising |

> **주의**: 이건 [선호] 영역이며 조직 정책에 따른다. 사용자가 쓰는 조직에 정책이 있으면 그것이 우선이다. 강요하지 않고 **대안을 제시**한다.

## 6. 판정 시 인용 형식

```
[stage 1] Garner LCI 1 — 표준에서 배척
[stage 3] Garner LCI 3 — 격식 문서에서는 회피 권장
[stage 4] Garner LCI 4 — 보편 수용, 교정 대상 아님
[미신] zombie rule — 규칙이 아님 (split infinitive 등)
[가이드] CMOS 18th — Oxford comma 사용 / AP는 미사용
[확인] 스타일가이드 미지정 — CMOS 기본값 적용함
[확인] AmE/BrE 미확인 — AmE 기준으로 판정함
```

## 7. 기본값 선언 문구 (교정 결과에 반드시 포함)

사용자가 기준을 지정하지 않았다면 출력에 다음 중 하나를 넣는다:

> 기준 미지정이라 **미국 영어 + CMOS 18판**을 기본값으로 판정했습니다. 대상 독자가 영국이거나 회사가 AP·APA를 쓴다면 일부 항목(Oxford comma, 숫자 표기, 날짜 형식)이 달라집니다.

이 문장을 생략하면 사용자가 다른 기준의 문서에 잘못 적용하게 된다.
