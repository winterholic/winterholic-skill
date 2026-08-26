# evidence + 출고 전 체크리스트

## 실증·출처

- **Airbnb ts-migrate (2020, 공개 블로그·컨퍼런스 발표)** — 포스트모템 버그의 ~38%가 TS로 예방 가능했을 것이라는 사내 분석(확인 필요: 원문 수치). SKILL.md 실전 케이스 출처. null/형태 불일치가 그 대부분이라는 점이 strict·경계 검증 우선순위의 근거.
- **"To type or not to type" (Gao, Bird, Barr — ICSE 2017)** — JS 공개 버그 표본의 **약 15%를 TS/Flow가 컴파일 타임에 검출** 실측 연구. 타입의 효과를 측정한 대표 학술 출처.
- **Effective TypeScript (Vanderkam, 2판)** — any 전염·단언 절제·구별된 유니언·satisfies 활용의 표준 교과서.
- **TypeScript 공식 핸드북·릴리스 노트** — satisfies(4.9)·enum 주의(erasableSyntaxOnly 흐름)·TS 7 네이티브 포트 발표(2026)의 1차 출처.
- 오픈소스 차용 표기: mcpmarket TS 스킬들·jeffallan python-pro의 TS 자매편 조사(2026-06, 본문 비복사). **역흡수**: 경계 런타임 검증(컴파일/런타임 구분)·@ts-expect-error 사유 의무·브랜드 타입 판단 기준 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (TS 코드 출고 시)

- [ ] `npx tsc --noEmit` 통과
- [ ] 신규 any·as any·이중 단언 0 (`ts_check.py` 0건)
- [ ] 외부 데이터 진입점 전부 스키마 검증 (fetch/storage/URL)
- [ ] 상태 모델이 불가능 상태를 허용하지 않음 (옵셔널 조합 → 유니언 검토 흔적)
- [ ] switch 완전성 (assertNever 또는 만족스러운 default 사유)
- [ ] 에러 억제는 @ts-expect-error + 사유만
- [ ] 공개 함수 시그니처: 입력 너그럽게(readonly·유니언) 출력 구체적으로
- [ ] enum 신규 도입 없음 (기존분은 마이그레이션 백로그)
- [ ] tsconfig strict 유지 (변경했다면 사유와 복귀 계획)

## 점검 주기 (부패 중간 — 반기)

- TS 메이저와 tsconfig 권장값 변화 확인. **타임라인(2026, devblogs.microsoft.com/typescript)**: 6.0 stable(2026-03) → 7.0 beta(2026-04-21) → **7.0 RC(2026-06-18)**. 7.0은 Go 네이티브 포트로 tsc 약 10배 가속, 타입 검사 의미론·문법 불변 — GA 시점과 도구 패키징(`tsgo`/기존 `typescript` 흡수) 확인 필요.
- typescript-eslint 룰셋 메이저 변화 + eslint-plugin-react-hooks의 flat config(`reactHooks.configs.flat.recommended`, ESLint 9) 권장 형태 추적.
- ledger의 타입 관련 삽질 3회 패턴 → 에러 해석 레시피 보강
