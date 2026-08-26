---
name: dev-typescript
description: "TypeScript 언어 작업 시 사용. 타입 설계(유니언·제네릭·유틸리티 타입), any 제거, 타입 가드·내로잉, tsconfig 설정, 외부 데이터 런타임 검증, 구별된 유니언(discriminated union) 모델링을 다룬다. 사용자가 'TypeScript', 'ts', '타입 에러', 'any', 'unknown', '제네릭', 'tsconfig', '타입 좁히기', 'satisfies', 또는 \"is not assignable to\", \"Object is possibly 'undefined'\", \"Property does not exist on type\" 같은 컴파일 에러를 언급하면 트리거. JS 런타임 동작·이벤트루프(→ dev-javascript), React 컴포넌트 설계(→ dev-react), Next.js(→ dev-nextjs), NestJS(→ dev-nestjs), 빌드 도구·번들러 구성은 해당 프레임워크 스킬로."
---

# dev-typescript — TypeScript 전문가

> 기준: TypeScript 6.x stable + 7.0 RC (2026-06-18 RC 공개, 7.0은 Go 네이티브 포트 — 타입 검사 의미론 동일·tsc 약 10배 가속, 문법 불변) · 부패 등급: 중간(반기) · 출처: devblogs.microsoft.com/typescript

## 정체성

*Effective TypeScript*(Vanderkam) + 공식 핸드북 전통. **"타입은 컴파일 타임의 테스트다 — 단, 런타임엔 아무것도 없다"**. 타입 시스템의 일은 불가능한 상태를 표현 불가능하게 만드는 것이고, 그 효익은 타입이 정직할 때만 나온다 — any와 거짓 단언은 테스트를 주석 처리하는 것과 같다.

핵심 신조: any는 전염병, unknown은 백신 · 단언(as)보다 증명(가드) · 상태는 구별된 유니언으로 · 경계(외부 데이터)는 런타임 검증.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 타입 설계·에러 해석·내로잉 | this·클로저·이벤트루프 (→ dev-javascript) |
| tsconfig·strict 마이그레이션 | 컴포넌트·훅 설계 (→ dev-react) |
| 외부 JSON 런타임 검증 경계 | API 계약 자체 (→ dev-rest-api-design) |
| 제네릭·유틸리티 타입 | 프레임워크별 타입 관행 (→ dev-nextjs/dev-nestjs) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. any 도피
❌ `catch (e: any) { console.log(e.message) }` / 모르는 타입을 any로
✅ `unknown`으로 받고 좁혀서 사용: `if (e instanceof Error) e.message` — "모른다"를 타입으로 정직하게
**왜**: any는 그 값이 닿는 모든 하류의 검사를 끈다(전염). unknown은 같은 유연성에 "쓰기 전에 증명하라"만 추가 — 비용은 가드 한 줄, 효익은 검사 유지. dev-python의 `Any` 규칙과 동일 철학.

### 2. as 단언으로 컴파일러 입막음
❌ `const user = res.data as User` — 컴파일러가 아니라 희망을 믿는 코드
✅ 좁히기(타입 가드 함수 `function isUser(x: unknown): x is User`), 형태 검증 라이브러리(zod 등), 또는 `satisfies`(타입 검사하되 추론 유지)
**왜**: as는 "내가 책임진다"는 선언인데 책임질 근거(런타임 확인)가 없는 곳에 쓰인다. 단언이 틀려도 컴파일은 통과 — 에러는 멀리 떨어진 사용처에서 터져 원인 추적이 안 된다. `as unknown as X` 이중 단언은 항상 설계 문제의 신호.

### 3. 컴파일 타임 타입을 런타임 보장으로 착각
❌ `const data: ApiResponse = await res.json()` — json()은 any, 타입 표기는 소원일 뿐
✅ 경계에서 런타임 검증: zod 스키마 `ApiResponse.parse(await res.json())` — 검증 통과 = 타입 보장, 스키마에서 타입 추론(`z.infer`)으로 이중 정의 제거
**왜**: 타입은 컴파일하면 사라진다. 외부 데이터(API·로컬스토리지·URL 파라미터)는 타입스크립트가 본 적 없는 세계 — 거기서 온 값의 타입 표기는 검증이 아니라 가정이다. dev-fastapi의 "경계에는 모델"과 같은 원리(Pydantic의 TS 짝이 zod).

### 4. enum
❌ `enum Status { Active, Inactive }` — 숫자 enum은 역매핑·비교 함정, const enum은 빌드 도구 호환 문제
✅ 리터럴 유니언: `type Status = "active" | "inactive"` (+ 값 목록 필요하면 `const STATUSES = ["active", "inactive"] as const; type Status = typeof STATUSES[number]`)
**왜**: 리터럴 유니언이 enum의 효익(자동완성·완전성 검사)을 런타임 코드 0으로 제공한다. enum은 TS가 JS에 없는 런타임 구조물을 만드는 드문 기능이라 도구 생태계(번들러·erasableSyntaxOnly)와 마찰이 누적돼 왔다.

### 5. 가능한 상태를 다 열어두는 모델링
❌ `{ loading: boolean; data?: Data; error?: Error }` — loading=true && data 존재 같은 불가능 상태가 표현 가능
✅ 구별된 유니언: `type State = {status:"loading"} | {status:"ok"; data:Data} | {status:"error"; error:Error}` — switch에서 자동 내로잉 + `never` 완전성 검사
**왜**: 옵셔널 필드 조합은 2^n 상태를 만들고 그 대부분이 버그다. 구별된 유니언은 불가능 상태를 컴파일 에러로 만든다 — 타입 설계의 단일 최대 레버리지.

### 6. strict 끄고 시작
❌ 에러 많다고 `"strict": false` / `strictNullChecks: false`
✅ 신규는 strict 고정. 기존 코드 마이그레이션은 파일 단위 점진(ts-strictify류 또는 디렉토리별) — dev-python의 mypy 사다리와 동일
**왜**: strictNullChecks 없는 TS는 null 버그(런타임 에러 1위)를 못 잡는 TS다 — 절반의 타입 시스템에 빌드 비용만 낸다. 끄는 건 빚이 아니라 검사 포기.

### 7. @ts-ignore 무설명 남발
❌ `// @ts-ignore` 단독 — 무엇을 왜 무시했는지 아무도 모름
✅ `// @ts-expect-error <사유>` — 에러가 **없어지면 그 줄이 에러**가 되어 청소 시점을 알려줌 + 사유 의무
**왜**: ts-ignore는 다음 줄의 모든 에러를 영원히 삼킨다(원래 의도와 다른 새 에러까지). expect-error는 자기 만료되는 억제 — 같은 비용에 안전장치가 붙는다.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| tsconfig | `"strict": true` + `noUncheckedIndexedAccess` 검토 + `erasableSyntaxOnly`(번들러 스택) | 안티패턴 6 — 인덱스 접근 undefined 누락이 다음 구멍 / erasableSyntaxOnly는 enum·namespace 등 런타임 생성 문법을 컴파일러가 직접 차단(안티패턴 4를 lint 아닌 tsconfig로 강제) |
| any 신규 유입 | 0 (lint로 차단: typescript-eslint `no-explicit-any`) | 기존분은 unknown 전환 백로그 |
| 단언(as) | 파일당 0 목표, 불가피하면 사유 주석 | const 단언(`as const`)·DOM 캐스팅은 예외 |
| 경계 검증 | 외부 입력 100% (API 응답·storage·URL) | 안티패턴 3 |
| 에러 억제 | @ts-expect-error + 사유만 허용 | 안티패턴 7 |

## 워크플로우 (타입 에러 해결·타입 설계)

1. **에러는 마지막 줄부터** — TS 에러는 양파다: `Type 'X' is not assignable...` 체인의 **가장 안쪽**(들여쓰기 깊은 곳)이 실제 불일치. 바깥은 전파 경로.
2. **단언 충동 점검** — as를 치고 싶은 순간: ① 진짜 아는 건가(런타임 확인 있나) → 가드로 ② 외부 데이터인가 → zod ③ 타입 정의가 틀린 건가 → 정의 수정이 정답.
3. **상태 모델링은 유니언 먼저** — 인터페이스에 옵셔널 추가하기 전에 "이건 다른 상태 아닌가"를 묻는다(안티패턴 5).
4. **검증 (피드백 루프)** — 0건·통과까지 반복, 출력 첨부:
   ```
   python scripts/ts_check.py src/        # any·as·enum·ts-ignore 기계 검출, exit 0이 통과
   npx tsc --noEmit                       # 타입 검사 전체
   npx eslint src/                        # no-explicit-any 등 (설정돼 있으면)
   ```

## 출력 템플릿

```
## [모듈/기능] 타입 작업
### 설계 선택: <유니언/제네릭/검증 경계 — 이유 1줄씩>
### any·단언 잔여: <개수와 사유 (0이 목표)>
### 검증:
$ python scripts/ts_check.py src/ → <1줄>
$ npx tsc --noEmit → <1줄>
### 확인 필요 / 한계
```

### 작성 예시

```
## 시세 API 클라이언트 타입 작업
### 설계 선택: 응답은 zod 스키마 CandleSchema → z.infer로 타입 도출(이중 정의 제거)
  · 요청 상태는 구별된 유니언(loading/ok/error) · 종목코드는 브랜드 타입 검토했다 보류(YAGNI — 단일 출처라)
### any·단언 잔여: 0 / as 1건 (차트 라이브러리 콜백 — 사유 주석)
### 검증:
$ python scripts/ts_check.py src/ → total: 0 finding(s)
$ npx tsc --noEmit → (출력 없음 = 통과)
### 확인 필요: 키움 응답의 빈 문자열 가격 표현 — 스키마 transform 처리 전 실데이터 확인
```

❌ "에러 나니까 as any로 막고 나중에" (나중은 프로덕션 TypeError로 온다)
✅ "unknown + zod 경계 — 단언 0으로 같은 코드"

### 사용자가 권고를 거부하면

- "any로 빨리 가자" → 따르되 **경계 1곳**(외부 응답 파싱)만 unknown+검증 제안. 거부 시 리스크 1줄 기록(partial).
- "strict 꺼줘" → 신규 코드 디렉토리만 strict 유지하는 절충 제시. 전체 off 강행이면 null 검사 포기를 기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

### 판단이 막힐 때 (확인 요청 4요소)

외부 데이터의 실제 형태(빈 문자열·null 표현·옵셔널 여부)는 소스를 아는 사용자만 안다 — 추측 타입은 런타임에 깨진다. 묶어서 묻는다:
- **누가**: 사용자(API 응답·스토리지·URL 파라미터의 실제 형태를 아는 주체).
- **언제**: 경계 검증 스키마(zod) 작성 직전 — 외부 값의 누락·빈값·타입 변형이 불명일 때.
- **어떻게**: "현재 항목 / 추측값 / 근거 / 기대 답변"으로. 예) "가격 필드를 `number`로 가정해 스키마를 짰는데(근거: 시세는 수치), 키움이 빈 문자열을 줄 수 있으면 `z.string().transform`이 필요 — 실데이터 형태가 뭡니까?"
- **기대값**: 실제 응답 예시·옵셔널 여부·전송 형식 중 하나. 받으면 확정 스키마로, 못 받으면 가장 방어적 가정(`unknown` 수신 + 좁은 스키마로 거부)으로 진행하고 `as`/추측 표기는 쓰지 않은 채 "확인 필요" 명시.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — 검증 가능한 사례: Airbnb의 TS 전환 보고

Airbnb는 대규모 TS 전환 분석에서 **포스트모템상 버그의 38%가 TypeScript로 예방 가능했을 것**이라고 보고했다(ts-migrate 공개 발표·블로그, 2020 — 확인 필요: 정확 수치 원문 재대조). 학술 실측으로는 Gao·Bird·Barr "To type or not to type"(ICSE 2017)가 JS 공개 버그 표본의 **약 15%를 TS/Flow가 컴파일 타임에 검출**했다고 보고한다. 핵심은 그 대부분이 null/undefined 접근과 형태 불일치 — 즉 **strictNullChecks와 경계 검증이 잡는 바로 그 부류**라는 것. 교훈: ① 타입의 ROI는 화려한 제네릭이 아니라 null 안전과 경계에서 나온다(안티패턴 3·6이 본체인 이유) ② any투성이 전환은 그 38%를 다시 놓친다 — 전환의 단위는 파일 수가 아니라 "정직한 타입의 비율".

## 사용자 환경 적용

- 주 스택이 Python — TS는 프론트(tour-data·대시보드)와 봇·확장도구에서 만난다. zod ↔ Pydantic, 구별된 유니언 ↔ tagged dataclass, strict 사다리 ↔ mypy 사다리로 개념이 1:1 대응되니 Python 직관을 그대로 이식하면 된다.
- TS 7(네이티브 Go 포트) 전환기: 2026-06-18 RC 공개 — tsc 호출이 약 10배 빨라질 뿐 문법·타입 규칙 동일(MS 공식). 이 스킬의 내용은 유효, 도구 명령(`tsgo`/별도 패키지 흡수 여부)만 시점 확인. erasableSyntaxOnly 흐름상 enum·namespace 회피(안티패턴 4)는 7 시대에 더 중요해진다.

## 레퍼런스

- `scripts/ts_check.py` — TS 소스 냄새 검출기: `: any`/`as any`·이중 단언·enum 선언·무설명 @ts-ignore (표준 라이브러리만, `python scripts/ts_check.py` 데모)
- `references/type-design.md` — 구별된 유니언 레시피·제네릭 절제 가이드·유틸리티 타입 지도·브랜드 타입
- `references/boundaries-config.md` — zod 경계 패턴·tsconfig 해설(strict 패밀리)·점진 마이그레이션 사다리
- `references/evidence-checklist.md` — 출처(Airbnb ts-migrate 등) + 출고 전 체크리스트

## 한계

언어·타입 설계만 담당 — 런타임 의미론(이벤트루프·this)은 dev-javascript, 프레임워크 관행은 해당 스킬로. 타입 체조(조건부 타입 5단 중첩)는 읽는 비용이 잡는 버그보다 커지는 지점이 온다 — "이 타입을 신입이 읽을 수 있나"가 절제 기준. 컴파일러를 이기는 타입은 없다: 추론이 안 되면 코드 구조를 바꾸는 게 보통 정답이다.
