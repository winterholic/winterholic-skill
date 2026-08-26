# evidence + 출고 전 체크리스트

## 실증·출처

- **react.dev "You Might Not Need an Effect"** — 안티패턴 1·2·7의 1차 출처(공식 안티패턴 문서). "Effect는 외부 시스템과의 동기화"라는 정의도 여기.
- **react.dev "Thinking in React"** — 정적 마크업 → 상태 최소 집합 → 위치 결정 워크플로우의 원전.
- **react.dev "Synchronizing with Effects"** — StrictMode 이중 실행이 cleanup 결함 검출 장치라는 공식 설명.
- **React Compiler 1.0 stable** (react.dev/blog/2025/10/07/react-compiler-1, 2025-10-07) — 자동 메모이제이션이 production-ready. 공식 권고: 컴파일러 채택 시 수동 useMemo/useCallback/React.memo는 원칙 불필요(안티패턴 4의 근거 — "측정 후"에서 "컴파일러에 위임"으로 갱신). Meta 자사 제품(인스타그램 등)에서 검증.
- **eslint-plugin-react-hooks v6+** (npm, v6.0.0은 2025년 RC→stable) — react-compiler 룰을 흡수(독립 `eslint-plugin-react-compiler`는 통합됨), ESLint 9 flat config 지원. exhaustive-deps + 컴파일러 규칙이 한 플러그인에(정량 기준 표·안티패턴 3의 룰 출처).
- **Dan Abramov "A Complete Guide to useEffect" (overreacted.io, 2019-03-09)** — stale closure·의존성 정직성의 고전 해설(안티패턴 3). 저자가 react.dev Effect 문서 집필진이라 1차 출처에 준함.
- 오픈소스 차용 표기: 기보유 vercel-react-best-practices(sub-skills — 병용 관계를 frontmatter에 명시), openai/frontend-skill(색인 확인만). **역흡수**: 검출 가능한 형태(setState-only Effect·index key)의 기계 검사·Effect 결정 트리 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (컴포넌트 출고 시)

- [ ] 파생값을 상태로 들고 있지 않다 (계산 또는 useMemo)
- [ ] 각 useEffect에 "외부 동기화" 사유가 있다 (결정 트리 통과)
- [ ] Effect cleanup 정합 (구독-해지 쌍) — StrictMode에서 정상
- [ ] exhaustive-deps 경고 0, 억제 주석 없음 (`react_check.py` 0건)
- [ ] 리스트 key가 안정 식별자
- [ ] 상태가 가장 낮은 공통 조상에 있다 (페이지 최상위 덩어리 없음)
- [ ] 서버 데이터가 useState 사본이 아니다 (Query 캐시 소유)
- [ ] 수동 메모이제이션은 Profiler 근거 또는 memo-자식 사유가 있다
- [ ] 상호작용 1개 이상 실동작 확인 (webapp-testing 또는 수동)

## 점검 주기 (부패 빠름 — 분기)

- React 마이너 버전 추적(현재 19.2.x) → 라벨 갱신. Compiler는 1.0 stable 완료 — 이후엔 메이저 변경·디폴트 채택 여부만 추적
- eslint-plugin-react-hooks 메이저 변화(현재 v6+ — compiler 룰 통합 완료)
- vercel-react-best-practices(기보유)와의 중복·충돌 재점검
