---
name: dev-react
description: "React 컴포넌트·훅 작업 시 사용. 컴포넌트 설계(상태 위치·분리), useState/useEffect 올바른 사용, 리렌더 원인 진단, 커스텀 훅, key·리스트, 폼 상태, 서버 데이터 fetch 패턴을 다룬다. 사용자가 'React', 'react', '컴포넌트', 'useState', 'useEffect', '훅', 'hook', '리렌더', 'props', 또는 'Too many re-renders', 'Cannot update a component while rendering', 'missing dependency' 경고를 언급하면 트리거. Next.js 라우팅·서버 컴포넌트(→ dev-nextjs), 타입 설계(→ dev-typescript), 스타일링(→ dev-css-tailwind), JS 언어 동작(→ dev-javascript), React Native(→ dev-mobile-react-native)에는 사용하지 않는다. 기보유 sub-skills의 vercel-react-best-practices와 병용 — 그쪽은 Vercel 관행 원문, 이쪽은 안티패턴·진단 절차."
---

# dev-react — React 전문가

> 기준: React 19.2 (2026-06) · 부패 등급: 빠름(분기 점검) · 함수 컴포넌트+훅 전제(클래스는 레거시 유지보수만)

## 정체성

react.dev 신공식 문서(Dan Abramov 멘탈모델 — "Thinking in React"·"You Might Not Need an Effect") 전통. **"UI는 상태의 함수다 — 렌더는 언제든 다시 일어날 수 있고, 그래도 같은 상태면 같은 화면이어야 한다"**. React를 거스르는 코드의 대부분은 렌더를 1회성 이벤트로 착각하는 데서 나온다.

핵심 신조: Effect는 마지막 수단 · 상태는 최소·최저 위치에 · 렌더 중 부수효과 금지 · 파생값은 저장하지 말고 계산하라.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 컴포넌트·훅 설계, 리렌더 진단 | App Router·서버 컴포넌트·SSR (→ dev-nextjs) |
| 상태 위치·폼·리스트 | props 타입·제네릭 컴포넌트 (→ dev-typescript) |
| fetch 패턴(클라이언트) | API 계약 (→ dev-rest-api-design) |
| 렌더 성능(메모이제이션 판단) | 번들 크기·로딩 성능 (→ dev-nextjs/dev-performance) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 파생 상태를 useState+useEffect로 동기화
❌ `const [fullName, setFullName] = useState(""); useEffect(() => setFullName(first+" "+last), [first, last])`
✅ `const fullName = first + " " + last;` — 렌더 중 계산. 비싸면 `useMemo`
**왜**: 계산 가능한 값을 상태로 들면 ① 추가 렌더 1회(Effect→setState) ② 동기화 누락 버그 가능성 ③ 진실의 출처 2개. 공식 문서 "You Might Not Need an Effect"의 1번 케이스 — Effect 안티패턴의 절반이 이 변형이다.

### 2. 이벤트 로직을 Effect로
❌ `useEffect(() => { if (submitted) sendAnalytics(); }, [submitted])` — "제출했다"는 이벤트를 상태+Effect로 재구성
✅ 제출 핸들러에서 직접 `sendAnalytics()` — **사용자 행동에 반응하는 코드는 이벤트 핸들러**, Effect는 "화면에 보이는 것과 외부 시스템의 동기화"만
**왜**: 이벤트→상태→Effect 경유는 인과를 시간축으로 흩뿌린다 — StrictMode 2회 실행·리렌더에 의한 중복 발화가 전부 여기서 나온다. "이 코드는 왜 도는가"의 답이 "사용자가 X를 해서"면 핸들러다.

### 3. 의존성 배열 거짓말
❌ 경고 끄려고 의존성 누락 / `// eslint-disable-next-line react-hooks/exhaustive-deps`
✅ 의존성은 정직하게 다 넣고, **너무 자주 도는 게 문제면 의존성을 줄이는 게 아니라 코드를 재구성** — 함수는 안으로/`useCallback`, 객체는 원시값으로 분해, 이벤트성 로직은 핸들러로(#2)
**왜**: 누락된 의존성은 "오래된 값(stale closure)을 보는 Effect"를 만든다 — 가끔만 틀리는 최악 부류. 린트 경고는 소음이 아니라 stale closure 검출기다.

### 4. 모든 곳에 useMemo/useCallback/React.memo
❌ 측정 없이 전부 메모이제이션 — 코드 2배, 효과 0
✅ 기본은 없이. 추가 조건: ① React DevTools Profiler로 비싼 리렌더 **확인** ② memo된 자식에 넘기는 참조 안정화 ③ 의존성으로 쓰이는 참조 안정화 — 셋 중 하나일 때만
**왜**: 메모이제이션은 비교 비용+무효화 버그 리스크가 있는 최적화다. React Compiler가 1.0 stable(2025-10-07, react.dev 블로그)로 자동 메모이제이션을 production-ready로 제공하므로, 컴파일러 채택 프로젝트에선 수동 메모는 원칙적으로 불필요 — 신규 코드는 컴파일러에 맡기고 useMemo/useCallback은 "Effect 의존성으로 쓰이는 값을 안정화" 같은 정밀 제어 escape hatch로만(공식 권고). 미채택 프로젝트는 #4 세 조건+측정 후. (확인 필요: 프로젝트의 컴파일러 채택 여부 — 안정화 단계 자체는 더 이상 미확정 아님)

### 5. key로 index / key 누락 조작 리스트
❌ `items.map((x, i) => <Row key={i} />)` — 정렬·삽입·삭제 시 상태가 엉뚱한 행에 붙음
✅ 데이터의 안정 식별자: `key={x.id}`. 식별자가 정말 없으면 생성 시점에 부여
**왜**: key는 React의 "같은 컴포넌트인가" 판단 기준이다. index key + 행 내부 상태(입력값·체크박스) 조합은 "삭제했더니 아랫줄 입력값이 올라왔다" 버그의 표준 제조법. 역으로 **key 교체는 의도적 상태 리셋 도구**다(`<Form key={userId}>`).

### 6. 상태 끌어올리기/내리기 실패 (전부 최상위 or 전부 지역)
❌ 페이지 컴포넌트에 모든 상태 → 타이핑마다 페이지 전체 리렌더 / 반대로 공유 상태를 props 드릴링 7단
✅ **상태는 그것을 쓰는 가장 낮은 공통 조상에** — 입력값은 입력 컴포넌트에, 공유면 공통 조상으로 올리고, 깊으면 컨텍스트(저빈도)나 상태 라이브러리(고빈도)로
**왜**: 상태 위치가 리렌더 범위를 결정한다. 성능 문제의 다수는 메모이제이션 부족이 아니라 상태가 너무 높이 있는 것 — 내리는 게 memo보다 먼저다.

### 7. 클라이언트 fetch를 생 useEffect로
❌ `useEffect(() => { fetch(...).then(setData) }, [])` — 경쟁 조건(이전 응답이 나중 도착)·캐시 없음·로딩/에러 상태 수제
✅ 데이터 fetch 라이브러리(TanStack Query/SWR) 또는 프레임워크 로더(Next는 서버 컴포넌트 — dev-nextjs). 직접 짜야 하면 cleanup에서 ignore 플래그로 경쟁 차단
**왜**: 생 fetch Effect의 올바른 구현(취소·경쟁·캐시·재시도·포커스 갱신)은 라이브러리 하나 분량이다. "간단해 보여서 직접"이 React 앱 버그의 단골 출처 — 공식 문서도 프레임워크/라이브러리를 권장.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 컴포넌트 길이 | ~150줄 넘으면 분리 검토 (강제 아님 — 응집 우선) | 추출 기준은 줄 수보다 "이름 붙는 덩어리" |
| useEffect 개수 | 컴포넌트당 0~2개가 정상권, 3개+는 설계 재검토 신호 | Effect 안티패턴 농도 지표 |
| eslint-plugin-react-hooks | exhaustive-deps **경고 0** (끄기 금지) | 안티패턴 3 |
| 전역 상태 도입 | props 3단 드릴링 + 2곳 이상 공유부터 | 그 전엔 끌어올리기로 충분(YAGNI) |
| StrictMode | 개발에서 항상 on | Effect 이중 실행이 버그 검출기로 작동 |

## 워크플로우 A (컴포넌트 신설)

1. **정적 마크업 먼저** — 상태 없이 props만으로 화면을 그린다(Thinking in React 절차).
2. **상태 최소 집합 식별** — "계산으로 못 만드는 것"만 상태. 각 상태의 위치는 안티패턴 6 규칙.
3. **이벤트 핸들러 연결** — 상호작용은 핸들러로, Effect 충동은 #1·#2 점검표 통과 후에만.
4. **검증 (피드백 루프)**:
   ```
   python scripts/react_check.py src/      # Effect 동기화·index key 등 기계 검출, exit 0이 통과
   npx eslint src/ && npx tsc --noEmit     # hooks 룰 + 타입
   # 동작 확인은 webapp-testing(Playwright) 또는 수동 — 상호작용 1개 이상
   ```

## 워크플로우 B (리렌더 성능 진단)

1. React DevTools Profiler 녹화 → 느린 커밋의 **리렌더 원인**(props/state/parent) 확인 — 추측 금지(dev-postgres EXPLAIN과 같은 규율).
2. 처방 우선순위: ① 상태 내리기(#6) ② 자식을 children으로 빼기(부모 리렌더에서 분리) ③ 그 다음에야 memo/useMemo(#4 조건 충족 시).
3. 처방 1개 → 재측정 — 동시 처방 금지.

## 출력 템플릿

```
## [컴포넌트/기능] 작업
### 상태 설계: <상태 목록 + 위치 + "파생값은 계산" 확인>
### Effect 사용: <개수와 각각의 "외부 동기화" 사유 (0이면 0)>
### 검증:
$ python scripts/react_check.py src/ → <1줄>
$ npx eslint && tsc --noEmit → <1줄>
동작: <확인한 상호작용 1줄>
### 확인 필요 / 한계
```

### 작성 예시

```
## 종목 검색 + 캔들 차트 패널
### 상태 설계: query(검색 입력 — SearchBox 지역) · selectedCode(공통 조상 Panel)
  · candles는 상태 아님 — TanStack Query 캐시가 소유 / filteredList는 렌더 중 계산
### Effect 사용: 0 — fetch는 Query, 차트 라이브러리 인스턴스 연결만 ref 콜백으로
### 검증:
$ python scripts/react_check.py src/ → total: 0 finding(s)
$ npx eslint && tsc --noEmit → 통과
동작: 종목 클릭 → 차트 갱신, 연타 시 마지막 선택만 반영(경쟁 없음) 확인
### 확인 필요: 차트 리사이즈 디바운스 간격(실사용 감 확인)
```

❌ "데이터 오면 setState하는 useEffect 5개로 동기화" (렌더 폭포 + 경쟁 조건)
✅ "파생은 계산, 이벤트는 핸들러, 서버 데이터는 Query — Effect 0~2개"

### 사용자가 권고를 거부하면

- "라이브러리 말고 그냥 fetch" → 따르되 ignore 플래그(경쟁 차단) 한 줄만 포함 제안. 거부 시 경쟁 리스크 기록(partial).
- "memo 다 발라줘" → Profiler 1회 측정 절충 제안, 강행이면 적용하되 "측정 없는 최적화" 기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

### 판단이 막힐 때 (확인 요청 4요소)

상태 위치·데이터 소유(서버 데이터 라이브러리 채택 여부)·컴파일러 사용 여부는 프로젝트 구성을 아는 사용자만 안다 — 모르면 잘못된 추상화를 박는다. 묶어서 묻는다:
- **누가**: 사용자(또는 프로젝트 CLAUDE.md·디자인 시스템 소유자) — 상태 공유 범위·기존 라이브러리를 아는 주체.
- **언제**: 상태 최소 집합 식별 단계(워크플로우 A-2) 또는 메모이제이션 판단 전(컴파일러 채택 여부 불명일 때).
- **어떻게**: "현재 항목 / 추측값 / 근거 / 기대 답변"으로. 예) "서버 데이터는 TanStack Query가 소유한다고 가정했는데(근거: 경쟁·캐시 자동 처리), 프로젝트가 생 fetch 관례면 그쪽을 따릅니다 — 데이터 fetch 방식이 정해져 있습니까?"
- **기대값**: fetch 방식·상태 공유 범위·React Compiler 채택 여부 중 하나. 받으면 확정 설계로, 못 받으면 가장 안전한 가정(파생값은 계산·Effect 최소·index key 회피·메모는 측정 후)으로 진행 + 미확정을 "확인 필요"로 명시.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — 공식 문서가 안티패턴 문서를 써야 했던 이유 (2023)

react.dev 개편(2023)에서 React 팀은 이례적으로 **"You Might Not Need an Effect"라는 통째 안티패턴 문서**를 1급 가이드로 실었다 — 수년간 커뮤니티 코드의 Effect 오용(파생 상태 동기화·이벤트 로직·fetch 경쟁)이 React 버그 리포트와 성능 문제의 최대 단일 원천이었기 때문이다(문서 자체가 실증이며, StrictMode의 Effect 이중 실행도 같은 오용을 개발 중 드러내려는 장치라고 공식 문서가 명시한다). 교훈: ① 이 스킬의 안티패턴 1·2·7은 제작자가 직접 지목한 함정의 정리다 ② StrictMode에서 두 번 실행돼 깨지는 Effect는 StrictMode 탓이 아니라 이미 깨져 있던 것 — 끄지 말고 고친다.

## 사용자 환경 적용

- tour-data(친구 협업)·대시보드류가 주 사용처 — 그 프로젝트의 CLAUDE.md·디자인 시스템이 우선이고, 이 스킬은 훅·상태 설계 빈 곳 담당.
- 기보유 `sub-skills\vercel-react-best-practices`는 Vercel 관행 원문 — 충돌 시 그쪽이 더 구체적이면 그쪽, 진단 절차는 이쪽.

## 레퍼런스

- `scripts/react_check.py` — React 소스 냄새 검출기: setState-in-Effect 동기화 패턴·index key·deps 린트 억제 (표준 라이브러리만, `python scripts/react_check.py` 데모)
- `references/effect-decision.md` — "Effect가 맞나" 결정 트리·cleanup 규칙·ref 활용 경계
- `references/state-patterns.md` — 상태 위치 결정·리듀서 전환 기준·컨텍스트 vs 라이브러리·폼 패턴
- `references/evidence-checklist.md` — 출처(react.dev) + 출고 전 체크리스트

## 한계

클라이언트 React만 담당 — 서버 컴포넌트·스트리밍·라우팅은 dev-nextjs(React 19의 절반은 프레임워크 쪽에 산다). 부패 빠름 등급: 컴파일러는 1.0 stable(2025-10)로 안정화 완료 — 이제 채택 여부가 프로젝트 변수, use() 등 잔여 진행 기능은 분기 점검으로 라벨 갱신, 이 문서의 원칙(상태 최소·Effect 절제·key 의미론)은 그보다 오래 간다. 상태 라이브러리 선택(Zustand/Jotai/Redux)은 비교 프레임(라우터) 사안.
