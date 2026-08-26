# dev-algorithms evidence — 실증 사례

## 1. Accidentally Quadratic — 일급 소프트웨어의 반복 지뢰 (공개 사례 모음)

- **장르 표본**: GTA Online(10MB JSON 파싱 — sscanf가 매번 내부에서 strlen 전체 순회 + 6.3만 항목 중복검사 O(n²) ≈ 19.8억 비교, 2013년 출시 후 ~8년 방치를 외부 개발자 t0st가 로딩 6분→1분50초 ≈ 69.4% 단축) · npm(의존성 처리 경로의 중복 순회) · systemd·grep·여러 컴파일러의 수차례 사례 — 동명 블로그(accidentallyquadratic.tumblr.com, 현존)가 수년간 수집한 실존 장르.
- **공통 골격**: 루프 자체는 선형 → 루프 안 호출(선형 검색·문자열 누적·재파싱)이 곱을 만듦 → 테스트 데이터(소형)에선 무증상 → 운영 데이터 성장이 기폭 → 프로파일 한 번에 발견.
- **의심 목록(리뷰 체크리스트화)**: 루프 안의 `in list` / `list.remove` / `insert(0)` / 문자열 `+=` / 정규식 재컴파일 / DataFrame 행 접근(dev-data-analysis) / DB 쿼리(dev-sql N+1 — 같은 구조의 IO판) — 전부 "개별로는 무죄, 곱해서 유죄".

## 2. 이진 탐색 오버플로 — 표준 라이브러리에서 9년 잠복 (Bloch 공개 고백)

- **무슨 일**: Java 표준 라이브러리(JDK)의 이진 탐색 `mid = (low + high) / 2` 가 거대 배열(길이 2³⁰≈10억 이상)에서 `low+high`가 int 최대값(2³¹-1)을 넘어 음수로 오버플로 → C에서는 인덱스 범위 밖, Java에서는 `ArrayIndexOutOfBoundsException`. *Effective Java* 저자 Joshua Bloch 본인이 작성했고, 2006년 Google Research Blog 공개 글("Extra, Extra — Read All About It: Nearly All Binary Searches and Mergesorts are Broken", 2006-06-02)로 고백. 같은 버그가 Bentley의 *Programming Pearls* 예제(증명된 코드)에도 있었다 — 검증된 알고리즘의 검증된 구현조차 수년간 잠복했다.
- **수정**: `mid = low + (high - low) / 2` (C 이식성 버전) 또는 Bloch가 제시한 무부호 시프트 `mid = (low + high) >>> 1` — 한 줄.
- **교훈 2겹**: ① "교과서 알고리즘 직접 구현"의 위험 실증 — off-by-one·오버플로는 대가도 밟는다 → 내장 우선 원칙의 근거 ② 거꾸로, 내장도 한때 틀렸다 — "검증됨"은 사용량×시간의 함수지 권위의 함수가 아니다. 의심스러운 동작은 권위 말고 테스트로.

## 3. 코테 ↔ 실무 전환표 (모드 스위칭 실용 정리)

- **복잡도 어림 (코테 공용)**: 시간 제한 1초 ≈ 연산 10⁷~10⁸회 기준 — n 제약에서 허용 복잡도 역산: n≤20(2ⁿ 완전탐색·비트마스크) / n≤500(O(n³)) / n≤5,000(O(n²)) / n≤10⁵~10⁶(O(n log n)) / 그 이상(O(n)·O(log n)·수학).
- **패턴 1차 분류**: 구간·연속 부분 = 투포인터/슬라이딩 윈도우 · 최단/최소 단계 = BFS · 모든 경로/백트래킹 = DFS · "최적값 + 겹치는 부분 문제" = DP · 정렬 후 욕심 = 그리디(교환 논증으로 검증) — 분류가 구현보다 먼저.
- **실무 반입 금지품**: 입출력 트릭·한 글자 변수·전역 상태·"맞으면 됨" 예외 무시 / **실무→코테 반입 금지품**: 과한 추상화·방어 코드·설정성 — 두 문체의 의식적 분리가 양쪽 성과를 지킨다.

> 출처(2026-06 웹 재확인):
> - Bloch, "Nearly All Binary Searches and Mergesorts are Broken", Google Research Blog 2006-06-02 — 표준 라이브러리 저자 본인의 1차 고백, 오버플로 버그의 정전(正典) 출처: https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/
> - t0st, "How I cut GTA Online loading times by 70%", 2021-02-28 — sscanf/strlen·O(n²) 중복검사 실증, 디스어셈블+벤치마크로 입증된 1차 분석(Rockstar가 공식 패치+버그바운티로 인정): https://nee.lv/2021/02/28/How-I-cut-GTA-Online-loading-times-by-70/
> - 복잡도 어림 표는 코테 플랫폼 공통 관행(1초 ≈ 10⁷~10⁸ 연산) — 교차확인: Codeforces "A Time Complexity Guide"(https://codeforces.com/blog/entry/104888), USACO Guide Time Complexity(https://usaco.guide/bronze/time-comp).
