# dev-mobile-flutter evidence — 실증 사례

## 1. jank 산식 — 16ms 예산과 "Skipped frames" (공식 성능 문서 실증)

- **무슨 일**: Flutter 공식 성능 문서가 명시하는 계약 — 60Hz 단말에서 프레임당 약 16.67ms(120Hz는 8.33ms) 안에 UI 스레드 build/layout/paint + 라스터 스레드 작업이 끝나야 한다. 초과분은 프레임 드롭이고 Android는 `Skipped N frames!`로 로그에 남는다.
- **흔한 합산 초과**: 개별로는 무해한 것들의 곱 — build 내 객체 생성(2ms) × 트리 전파(×10 위젯) × 애니메이션 중 매 프레임 = 예산 초과. "어느 한 줄이 느린 게 아니라 구조가 느린" 상태라 프로파일러 없이는 못 찾는다.
- **진단 절차**: `flutter run --profile` → DevTools Performance → 빨간(초과) 프레임 선택 → Timeline에서 최장 구간 위젯 확인. **debug 모드 성능은 JIT·assert 비용 때문에 판단 근거가 못 된다** — debug에서 느리다고 최적화 시작하는 게 흔한 헛수고.

## 2. dispose 누락 — "뒤로 갔는데 타이머가 산다" (크래시 리포트 단골)

- **무슨 일**: `setState() called after dispose()` — Flutter 크래시 리포트 상위 단골. 화면 이탈 후에도 Timer·Stream 구독·AnimationController가 살아 콜백이 죽은 State에 setState를 호출.
- **메커니즘**: State.dispose()는 자동으로 리소스를 해제해주지 않는다 — initState에서 구독한 것은 개발자가 명시 해제해야 한다. AnimationController는 Ticker가 vsync마다 깨어나므로 누수 시 배터리까지 먹는다.
- **방어**: ① initState↔dispose 1:1 대응 리뷰 ② 콜백 안 `if (!mounted) return;` 가드(이중 방어) ③ Riverpod/BLoC 등 상태관리 계층은 수명 관리를 대신해줌 — 위젯에서 직접 구독을 줄이는 구조적 해법.

## 3. async 갭 context — "QA 통과, 사용자 크래시" (lint 승격 실증)

- **무슨 일**: await 후 BuildContext 사용 패턴이 워낙 사고가 잦아, Flutter 팀이 `use_build_context_synchronously` lint를 만들고 권장셋에 포함시킨 역사 자체가 실증이다. 사용자가 await 중 화면을 떠나는 타이밍에만 발현 — 테스트 시나리오엔 없고 운영의 수만 사용자 중 일부가 매일 밟는다.
- **올바른 형태**: 모든 await 뒤 context 사용 직전 `if (!context.mounted) return;` (Flutter 3.7+에서 BuildContext.mounted 사용 가능). StatefulWidget 내부면 `if (!mounted)`.
- **이 스킬과의 연결**: 안티패턴 6. "lint가 있는 함정"은 전부 켜는 게 공짜 보험 — flutter_lints 기본셋에서 빼는 순간 이 역사를 다시 산다.

> 출처(2026-06 웹 검증, 현행 안정판 Flutter 3.44 / Dart 3.12 — Google I/O 2026):
> - 프레임 예산·jank·UI/raster 스레드: Flutter 공식 성능 프로파일링 문서 — https://docs.flutter.dev/perf/ui-performance ("each frame must render approximately every 16ms to avoid jank", 60fps 기준). 1차 출처.
> - async 갭 lint: Dart 공식 진단 문서 `use_build_context_synchronously` — https://dart.dev/tools/diagnostics/use_build_context_synchronously . flutter_lints 기본셋(flutter.yaml)에 포함됨을 확인. 1차 출처.
> - `BuildContext.mounted`: Flutter 3.7에서 추가(flutter/flutter PR #111619) — async 갭 가드의 표준 형태.
> - isolate 오프로딩: `Isolate.run` (Dart 2.19+, `@Since("2.19")`) / `compute` — https://api.flutter.dev/flutter/foundation/compute.html .
> - 커뮤니티 크래시 리포트는 보조 교차확인(공식 1차 출처 우선).
