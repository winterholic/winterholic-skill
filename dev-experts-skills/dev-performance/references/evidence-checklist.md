# evidence + 출고 전 체크리스트

## 실증·출처

- **Brendan Gregg, *Systems Performance* 2판** (Pearson/Addison-Wesley, 2020 — 2026-06 현재 **3판 미출시, 2판이 현행 최신**) + brendangregg.com의 USE Method 페이지 — 안티패턴 4(병목 종류 미분류)·USE(Utilization·Saturation·Errors) 점검의 1차 출처.
- **GTA Online 로딩 진단** (t0st, "How I cut GTA Online loading times by 70%", nee.lv, 2021-02) — 출시 7년 방치된 ~6분 로딩의 원인이 10MB JSON을 `sscanf`로 파싱(호출마다 strlen → O(n²)) + 중복 검사 선형 탐색(O(n²)). 외부인이 디스어셈블·프로파일링으로 진단, R*가 공식 패치+포상. 안티패턴 1(추측→수술)·실전 케이스의 1차 실증. "직감 무용"의 대표 사례.
- **Donald Knuth, "Structured Programming with go to Statements"** (1974) — "premature optimization is the root of all evil"의 원문 맥락: 악인 이유는 **잘못된 곳(97%의 사소한 곳)**을 최적화하기 때문. 정체성 절의 근거.
- **Nielsen Norman Group, "Response Times: The 3 Important Limits"** (Jakob Nielsen) — ~0.1s 즉각감 / ~1s 흐름 유지 / 10s+ 이탈. 정량 기준 표의 웹 응답 감각치(UX 출발점) 근거.
- **테일 레이턴시 / p99 문헌** (Dean & Barroso, "The Tail at Scale", CACM 2013) — 평균이 소수 재앙을 희석하고, 페이지당 리소스가 많을수록 p99에 걸릴 확률이 급상승한다는 안티패턴 2의 이론적 근거.
- **벤치 하네스**: JMH(Java)·pytest-benchmark(Python)·criterion(Rust)·BenchmarkDotNet(.NET) — 워밍업·죽은 코드 제거·통계 처리 내장. 안티패턴 3(마이크로벤치 순진 실행)의 처방 근거.

## 출고 전 체크리스트 (성능 작업 출고 시)

- [ ] "무엇이 얼마나 느리고 얼마면 충분한가"를 수치 목표(SLO, 예: p95 < 300ms)로 먼저 정의
- [ ] 느림을 안정 재현하는 조건 확보 (재현 안 되면 관측 데이터 수집부터 → dev-monitoring)
- [ ] 프로파일러로 최대 기여 지점 실측 (py-spy/pprof/EXPLAIN ANALYZE/플레임그래프) — 추측 수술 금지
- [ ] USE로 병목 종류 분류 (연산/IO/락/외부 대기) — 처방은 종류마다 정반대
- [ ] 1% 미만 기여 항목 수술 금지 (Amdahl), 수술은 상위 기여부터 1개씩
- [ ] 보고 지표는 p50/p95/p99 + 최대 (평균 단독 금지)
- [ ] 전후 비교: 동일 조건(데이터·부하·환경) 3회+ 측정 중앙값, 개선 폭이 노이즈보다 큰지 확인
- [ ] 성능 판단은 release/프로덕션급 빌드에서만 (debug 빌드 측정 금지)
- [ ] 목표 달성 시 중단 (목표 없는 무한 최적화로 가독성 갈아넣지 않음)
- [ ] 실제 수술은 스택 스킬(dev-postgres·dev-python 등)에 위임, 이 스킬은 "어디를 열지"까지

## 점검 주기 (부패 느림 — 연 1회)

- *Systems Performance* 3판 출시 여부만 추적(현재 2판 2020이 최신) → 버전 라벨 갱신. 방법론(USE·p99·전후 비교) 자체는 도구 버전과 무관하게 불변.
- 프로파일러 진입 명령(py-spy/pprof/`--cpu-prof`)의 인터페이스 변화는 연 1회 점검 — 원칙은 그보다 오래 감.
- Nielsen 응답 시간 임계는 UX 출발점이라 갱신 불필요(인지 한계는 불변).
