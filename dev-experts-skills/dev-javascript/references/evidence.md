# dev-javascript evidence — 장애·실증 사례

## 1. left-pad — 11줄이 생태계를 멈춤 (2016-03)

- **무슨 일**: 패키지명 분쟁 끝에 작성자가 자신의 npm 패키지 273개를 unpublish — 그중 `left-pad`(문자열 왼쪽 채우기 11줄)에 Babel·React 등 수천 패키지가 간접 의존 → 전 세계 빌드 연쇄 실패. npm이 사상 처음으로 강제 un-unpublish.
- **이중 교훈**:
  1. 공급망: 의존성 트리는 내가 고른 것보다 훨씬 깊다 (→ dev-dependency-security 본진)
  2. **언어 계층(이 스킬)**: padStart(ES2017)·includes·at·structuredClone·toSorted(ES2023)·Object.groupBy(ES2024) 등이 표준에 들어온 뒤에도 polyfill·유틸 의존이 관성으로 남는다 — 의존성 추가 전 MDN 1회 확인이 공짜 리스크 제거.
- **점검 명령**: `npm ls left-pad lodash.padstart 2>$null` 식으로 화석 의존성 확인.

## 2. unhandled rejection — "성공 응답, 데이터 없음" (Node 운영 표준 사고)

- **무슨 일**: async 저장 함수를 await 없이 호출하는 패턴이 만드는 표준 사고 — 호출부는 즉시 다음 줄로 진행해 성공 응답을 보내고, 저장 실패는 unhandled rejection 핸들러(없으면 stderr 또는 프로세스 종료)로만 흔적을 남긴다. Node 15+부터 unhandled rejection 기본 동작이 **프로세스 종료**로 강화됨 — "가끔 서버가 그냥 죽어요"의 단골 원인.
- **운영 방어**:
  ```js
  process.on('unhandledRejection', (reason) => { logger.fatal({ reason }, 'unhandled'); process.exit(1); });
  ```
  — 핸들러로 "조용히 삼키기"가 아니라 **기록 후 죽기**(좀비 상태 방지). 근본 해법은 lint(no-floating-promises)로 발생 자체를 차단.
- **이 스킬과의 연결**: 안티패턴 1. 코드 리뷰 grep: `grep -rn "^\s*[a-zA-Z_]*(.*);$" `보다 TS 도입 + lint가 유일하게 신뢰 가능한 검출.

## 3. sort 사전순 — "정렬이 대충 맞아서" QA 통과 (명세 함정 실증)

- **무슨 일**: `[5, 25, 100].sort()` → `[100, 25, 5]`. 비교 함수 없는 sort는 요소를 문자열 변환 후 UTF-16 코드 유닛 순으로 정렬한다(ECMA-262 명세). 작은 데이터·한 자리 숫자에선 결과가 우연히 맞아 테스트를 통과하고, 두 자리 숫자가 섞이는 운영 데이터에서 드러난다.
- **파생 함정**: sort는 원본 파괴(in-place) — React 상태·props를 직접 정렬하면 불변성 위반으로 렌더 버그(→ dev-react). ES2023 `toSorted()`가 비파괴 대안.
- **이 스킬과의 연결**: 안티패턴 7. 수치 정렬은 항상 `(a, b) => a - b` 명시 — "기본 동작이 합리적일 것"이라는 가정이 JS에서 가장 자주 깨지는 지점.

> 출처 (전부 1차, 2026-06 웹 확인):
> - left-pad 사건 — npm 공식 블로그 포스트모템 `kik, left-pad, and npm`(https://blog.npmjs.org/post/141577284765/kik-left-pad-and-npm), 교차확인 Wikipedia `npm left-pad incident`. 273개 패키지 unpublish·npm이 삭제 스크립트 제공·사상 첫 un-unpublish·Babel/React 빌드 실패 모두 일치 확인.
> - unhandledRejection 기본 종료 — Node.js 공식 문서 Process API(https://nodejs.org/api/process.html), 동작 변경의 1차 근거는 PR #33021 `process: change default --unhandled-rejections=throw`(https://github.com/nodejs/node/pull/33021, Node 15 semver-major). "throw 모드는 unhandledRejection 이벤트를 먼저 emit, 핸들러 없으면 uncaught exception으로 격상해 비정상 종료" 확인.
> - sort 문자열 정렬 — ECMA-262 `Array.prototype.sort` 명세(비교 함수 없으면 요소를 String 변환 후 코드 유닛 순 정렬). toSorted/toReversed/with 등 비파괴 배열 메서드는 ES2023, Object.groupBy는 ES2024 신규 표준으로 확인.
