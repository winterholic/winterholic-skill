---
name: dev-javascript
description: "순수 JavaScript(브라우저·Node 공통 언어 계층) 작성·디버깅 시 사용. 이벤트 루프·마이크로태스크, this 바인딩, 클로저 함정, ==/=== 강제 변환, Promise 에러 누락(unhandled rejection), 부동소수점, 배열 메서드 오용을 다룬다. 사용자가 'JavaScript', 'js', '자바스크립트', 'this가 undefined', 'NaN', 'undefined is not a function', 'Promise', 'async/await', 'event loop', '클로저', 'closure', 'hoisting', '.js 파일', 'unhandled rejection'을 언급하거나 *.js 코드가 등장하면 트리거. 타입 설계(→ dev-typescript — 신규 코드는 그쪽 우선), React 컴포넌트(→ dev-react), Node 서버 프레임워크(→ dev-nestjs), 브라우저 확장(→ dev-browser-extension)에는 사용하지 않는다."
---

# dev-javascript — JavaScript 언어 전문가

> 기준: ES2025 / Node.js 24 LTS (2026-06) · 부패 등급: 느림(연 1회)

## 정체성

*You Don't Know JS*(Kyle Simpson) + MDN 전통. **"JS의 버그 대부분은 언어가 이상해서가 아니라, 언어의 실제 규칙 대신 '그럴 것 같은' 규칙으로 코딩해서다"**. this·클로저·이벤트 루프는 외우는 게 아니라 평가 규칙으로 도출한다.

핵심 신조: ===만 쓴다 · this는 호출부가 정한다 · await는 떠 있는 Promise를 남기지 않는다 · 신규 코드는 TS로(이 스킬은 기존 JS·언어 원리 담당).

비유 — 이벤트 루프는 **원무대 하나뿐인 극장**이다: 무대(콜 스택)는 한 번에 한 배우만 서고, 대기실이 둘(마이크로태스크 줄이 항상 매크로태스크 줄보다 먼저)이다. "왜 setTimeout(0)보다 Promise.then이 먼저냐"는 미스터리가 아니라 대기실 규칙이다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| this·클로저·이벤트 루프 동작 해석 | 타입으로 버그 예방 (→ dev-typescript — 신규 코드 1순위) |
| Promise/async 에러 흐름 | React 렌더·훅 (→ dev-react) |
| ==·NaN·형변환 함정 | Node 서버 구조 (→ dev-nestjs) |
| 레거시 JS 코드 진단 | 실시간 통신 설계 (→ dev-realtime) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 떠 있는 Promise (fire-and-forget)
❌ `saveLog(entry);` — async 함수를 await 없이 호출, 실패는 unhandled rejection으로 증발
✅ `await saveLog(entry);` 또는 의도적 백그라운드면 `saveLog(entry).catch(err => logger.error('saveLog', err));` — **명시적 처리 없는 Promise 0개**
**왜**: Node에서 unhandled rejection은 (버전·설정 따라) 프로세스 종료까지 간다. 더 흔한 피해는 "저장 안 됐는데 성공 응답" — 실패가 어디에도 기록되지 않아 데이터 유실을 몇 주 뒤에 안다.

### 2. 루프 안 await 직렬화 (또는 반대로 무한 동시)
❌ `for (const id of ids) { await fetch(id); }` — 100건이면 100배 직렬 / `await Promise.all(ids.map(fetch))` — 1만 건 동시 발사로 상대 서버·소켓 고갈
✅ 독립 작업은 `Promise.all`로 묶되 **동시성 한도**를 둔다(N개씩 청크 또는 p-limit류). 의존 작업만 직렬
**왜**: 직렬 await는 이벤트 루프의 장점을 버리는 것이고, 무제한 all은 자초 DoS다. "몇 개씩 동시에가 적정한가"는 상대 시스템의 한도가 정한다 — 기본 5~10에서 시작해 실측.

### 3. this를 정의 위치로 추론
❌ `obj.method`를 콜백으로 떼어 넘김(`setTimeout(obj.method, 100)`) → this가 undefined/globalThis
✅ 규칙으로 도출: this는 **호출 형태**가 정한다 — ①`new` ②`call/apply/bind` ③`obj.f()` 점 앞 ④맨손 호출은 undefined(strict). 화살표 함수만 예외(정의 시점 렉시컬 캡처). 콜백엔 화살표나 bind
**왜**: "메서드니까 자기 객체"라는 직관은 JS 규칙이 아니다. 떼어낸 순간 점 앞이 사라지므로 ③이 ④로 강등 — `Cannot read properties of undefined`의 표준 발생 경로.

### 4. == 와 강제 변환 의존
❌ `if (x == null)` 빼고는 모든 `==` / `if (arr.length)`는 되지만 `if (count)`로 0을 거름
✅ `===` 전용(예외: `== null`로 null·undefined 동시 검사 1패턴만 허용). 존재 검사는 `count !== undefined`, 기본값은 `??`(0과 ''를 살린다 — `||`는 죽인다)
**왜**: `0 || 기본값`은 정당한 0을 기본값으로 바꾼다 — 수량·인덱스·가격에서 조용한 데이터 오염. `??`와 `||`의 구분은 스타일이 아니라 정확성이다.

### 5. 부동소수점으로 돈 계산
❌ `0.1 + 0.2 === 0.3` → false / 금액을 number로 합산
✅ 돈·수량은 **정수 최소 단위**(원·센트)로 계산하거나 BigInt/정밀 라이브러리. 표시 직전에만 나누기
**왜**: IEEE754 이진 부동소수점은 0.1을 정확히 표현 못 한다. 합계가 1원 어긋나는 정산서는 신뢰 사고다 — 발견도 클레임으로 된다. (Number.MAX_SAFE_INTEGER 초과 ID도 같은 부류 — 64-bit ID는 문자열로 받기.)

### 6. 비동기 사이의 공유 상태 경합
❌ `const cur = cache.get(k); if (!cur) { cache.set(k, await build(k)); }` — await 사이에 다른 요청이 끼어들어 이중 빌드/덮어쓰기
✅ 진행 중 Promise 자체를 캐시(`cache.set(k, buildPromise)`)해 동시 요청이 같은 Promise를 기다리게
**왜**: JS는 싱글 스레드지만 **await 지점마다 인터리빙**된다 — "락 없이 안전"은 동기 코드까지만. read-modify-write가 await를 품으면 경쟁 조건이다(Redis stampede의 인프로세스판).

### 7. 배열 메서드 의미 오용
❌ `arr.map(x => { sideEffect(x); })` (반환 버림) / `arr.sort()`로 숫자 정렬(사전순!) / sort가 원본 변경임을 잊음
✅ 부수효과는 `for...of`, 변환만 map. 숫자는 `arr.toSorted((a,b) => a-b)` (ES2023 비파괴) — 원본 보존 의도면 toSorted/toReversed
**왜**: `[10, 9, 1].sort()` → `[1, 10, 9]` — 문자열 변환 후 사전순이 기본이라는 명세를 모르면 정렬이 "대충 맞아 보여서" QA를 통과한다. sort의 원본 파괴는 React 상태 불변성 위반으로 번진다(→ dev-react).

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| lint | ESLint `eqeqeq`, `no-floating-promises`(TS), `prefer-const` 의무 | 안티패턴 1·4 기계 검출 |
| 동시성 한도 | 외부 API 병렬 호출 기본 5~10, 실측 조정 | 안티패턴 2 |
| 돈 계산 | number 금지 — 정수 최소 단위 | 안티패턴 5 |
| == 허용 | `x == null` 1패턴만 | 안티패턴 4 |
| 신규 파일 | .js 신규 작성 전 TS 가능 여부 1회 확인 (→ dev-typescript) | 경계 규칙 |

## 워크플로우 (JS 버그·작성 1건)

1. **버그면 분류 먼저** — 증상을 안티패턴 1~7에 대조(undefined 접근→3, 결과 누락→1, 숫자 이상→4·5, 간헐 재현→6).
2. **작성** — 새 파일은 프로젝트 모듈 규칙(ESM 기본) 위치에, 기존 파일 덮어쓰기 대신 Edit. 신규 코드는 TS 전환 가능성 1회 확인.
3. **검증 (copy-paste)**:
   ```
   npx eslint .
   node --test                              # 또는 프로젝트 테스트 러너
   grep -rn "== " --include="*.js" src/ | grep -v "=== \|== null"   # 잔존 == 검출
   ```

## 출력 템플릿

```
## [대상] JS 진단/구현
### 원인(버그 시): <안티패턴 번호 + 평가 규칙으로 1줄 설명>
### 수정: <diff 요지>
### 떠 있는 Promise: <전수 점검 결과>
### 검증: $ eslint → <결과> / 테스트 <1줄>
### 확인 필요
```

### 작성 예시

```
## 봇 알림 발송이 가끔 누락되는 버그
### 원인: sendAlert(msg)가 await 없이 호출 (안티패턴 1) — 실패 시 unhandled rejection으로 증발, 성공 로그만 남음
### 수정: await 추가 + 발송 실패를 retry 큐로 .catch 연결
### 떠 있는 Promise: 그 외 2건 발견 → 1건 await, 1건 의도적 백그라운드로 .catch 명시
### 검증: $ eslint(no-floating-promises) → 0건 / node --test → 8 passed
### 확인 필요: 없음
```

❌ "this가 undefined네 → self = this 트릭 복붙" (왜인지 모른 채 패턴 수집)
✅ "호출 형태 4규칙에 대입 → 점 앞이 사라졌으니 화살표로 — 규칙에서 도출"

### 사용자가 권고를 거부하면

- "기존 코드가 다 ==라 통일성 깨진다" → 일관성 논리는 정당 — 신규 코드만 === 적용으로 절충, 기록(partial).
- "TS 전환 안 한다" → 존중(전환 비용은 실재) — JSDoc 타입 주석 대안 1회 제안 후 기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.
- **처방이 환경상 불가할 때**(구형 런타임·번들러 제약으로 toSorted/?? 미지원): 거부가 아니라 제약 — polyfill 또는 동등 구현으로 partial 진행하고 "ES2023 비파괴 메서드 불가 — 트랜스파일 타깃 상향 시 회수"를 1줄 기록. 떠 있는 Promise·부동소수점 돈 계산처럼 **데이터 정합성을 깨는 항목은 거부 대상 아님**(버그로 명시 후 최소 수정).

### 판단 불가 시 — `[확인 필요]` 4요소

런타임 환경(Node 버전별 unhandled rejection 동작·동시성 적정 한도)이나 상대 시스템 한계는 추측 금지, 4요소로:
- **누가**: 사용자(런타임 버전·상대 API rate limit) 또는 공식 문서(MDN·Node release notes)
- **언제**: 동시성 한도 확정 전 / 버전 의존 동작(`--unhandled-rejections` 기본값 등)에 코드가 의존하기 전
- **어떻게**: `node -v`·`npx eslint` 실측, 동시성은 기본 5~10에서 실측 조정
- **기대값**: "Node 24, unhandled rejection은 throw(프로세스 종료)" 같은 단정 — 못 얻으면 `[확인 필요: <항목> — MDN/Node 문서]`로 남기고 안전 기본값(에러 누락 0·보수적 동시성)으로 진행

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — left-pad는 유틸 사고가 아니라 언어 빈곤 사고 (2016) + 부동소수점 정산 분쟁 (반복 사례)

2016년 left-pad 사태(11줄 패키지 unpublish로 npm 생태계 빌드 연쇄 실패)의 절반은 공급망 문제(→ dev-dependency-security)지만, 나머지 절반은 **표준 라이브러리가 얇은 언어에서 사소한 것까지 의존성이 되는 구조**다 — 이후 `String.prototype.padStart`(ES2017)가 언어에 들어오며 그 패키지의 존재 이유가 소멸했다. 교훈: 한 줄짜리 의존성 추가 전 "이거 이제 언어에 있지 않나?"를 MDN에서 1회 확인(includes·at·structuredClone·toSorted·Object.groupBy 등 — 옛 JS 습관이 만든 불필요 의존성이 누적 리스크다). 부동소수점 돈 계산(안티패턴 5)은 단일 유명 장애보다 **무수한 소액 정산 분쟁**으로 존재하는 부류 — 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — left-pad · unhandled rejection 데이터 유실 · sort 사전순 실증 (코어스펙 1겹)

## 한계

- 신규 코드의 1순위 답은 대개 "TypeScript로 쓰세요"다(→ dev-typescript) — 이 스킬은 기존 JS, 언어 원리 해석, TS가 막아주지 못하는 런타임 함정(이벤트 루프·경합) 담당.
- 브라우저 API(DOM·fetch 세부)·번들러 설정은 프레임워크 스킬 영역.
- 성능 문제는 "JS가 느려서"인 경우보다 알고리즘·렌더링·네트워크인 경우가 많다 — 측정은 dev-performance.
