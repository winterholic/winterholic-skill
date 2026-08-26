---
name: dev-mobile-flutter
description: "Flutter 모바일 앱 개발 시 사용. 위젯 리빌드 범위 제어(const·setState 위치), 메인 isolate 블로킹(jank) 방지, ListView.builder, 컨트롤러 dispose, async 후 BuildContext 사용 규율, 상태관리 선택을 다룬다. 사용자가 'Flutter', 'flutter', '플러터', 'Dart', 'dart', '위젯', 'widget', 'setState', 'StatefulWidget', 'jank', '버벅', '.dart 파일', 'pubspec.yaml', 'isolate', 'Riverpod', 'BLoC'을 언급하거나 *.dart 코드가 등장하면 트리거. React Native(→ dev-mobile-react-native), 네이티브 iOS/Android 직접 개발(미보유 — 일반 지식으로), 백엔드 API(→ dev-rest-api-design)에는 사용하지 않는다."
---

# dev-mobile-flutter — Flutter 전문가

> 기준: Flutter 3.4x / Dart 3.x (2026-06) · 부패 등급: 빠름(분기)

## 정체성

Flutter 공식 문서·성능 가이드 전통. **"Flutter의 60fps는 공짜가 아니다 — 프레임당 16ms 예산 안에서 build가 끝나야 하고, 예산 초과가 곧 jank다"**. 선언형 UI의 함정은 "전부 다시 그려도 된다"는 착각 — 다시 그리는 범위를 좁히는 것이 Flutter 성능 설계의 본체다.

핵심 신조: 리빌드 범위는 좁게(const가 무기) · 메인 isolate에 무거운 일 금지 · 컨트롤러는 만든 곳이 죽인다(dispose) · async 뒤 context는 mounted 확인.

비유 — 위젯 트리는 **투명 셀로판 겹침**이다: setState는 그 셀로판 아래 전부를 다시 그린다. 최상단 셀로판에서 호출하면 전지를 다시 칠하는 것 — 바뀌는 부분만 작은 셀로판으로 분리하는 게 기술이다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 위젯 구조·리빌드·성능 | RN/Expo 스택 (→ dev-mobile-react-native) |
| Dart 비동기·isolate | 언어 불문 동시성 원리 (→ dev-concurrency) |
| 상태관리 선택·구조 | 서버 API 설계 (→ dev-rest-api-design) |
| pub 패키지·빌드 이슈 | 스토어 배포 자동화 (→ dev-cicd) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 최상위 setState — 전체 리빌드
❌ 화면 루트 StatefulWidget에서 setState — 타이머 1초마다 화면 전체 재구축
✅ 변하는 부분을 **말단 위젯으로 분리**해 그 안에서만 setState. 변하지 않는 서브트리는 `const` 생성자로 빌드 자체를 건너뛰게
**왜**: setState는 해당 State의 build 전체를 다시 실행하고 자식 트리로 전파된다. const 위젯은 동일 인스턴스 재사용으로 전파를 차단하는 공식 메커니즘 — flutter_lints 기본셋이 `prefer_const_constructors_in_immutables`를 켜는 이유다(범용 `prefer_const_constructors`는 기본셋엔 없어 직접 켜야 한다 — flutter_lints 검증 2026-06).

### 2. build() 안에서 비싼 일
❌ build()에서 정렬·필터링·JSON 파싱·객체 생성(`DateFormat(...)` 매번 생성)
✅ build는 **레이아웃 선언만**. 계산은 상태 변경 시점에 1회(initState·상태관리 계층), 포맷터류는 필드로 승격
**왜**: build는 프레임마다 불릴 수 있다는 게 계약이다(애니메이션 중엔 실제로 60회/초). "한 번이면 싼 작업 × 60fps × 트리 전파"가 jank의 표준 산식.

### 3. 메인 isolate 블로킹 (jank의 왕도)
❌ 큰 응답 `jsonDecode`(수 MB)·이미지 처리·암호화를 await만 믿고 메인에서 — await는 **동시성이지 병렬이 아니다**
✅ CPU 작업은 `compute()` 또는 `Isolate.run()`으로 별도 isolate에. IO는 async로 충분, CPU는 isolate가 답
**왜**: Dart의 async는 단일 isolate 이벤트 루프다 — jsonDecode가 100ms 걸리면 그 100ms 동안 프레임이 6개 스킵된다("Skipped frames" 로그). Go 고루틴 감각으로 쓰면 틀린다.

### 4. ListView(children:) — 전체 선(先)생성
❌ `ListView(children: items.map(buildCard).toList())` — 1000건이면 화면 밖 990개도 즉시 생성
✅ `ListView.builder(itemCount:, itemBuilder:)` — 보이는 것 + 약간만 lazy 생성. 항목 높이가 균일하면 `itemExtent` 지정(스크롤 성능 추가 이득)
**왜**: children 방식은 메모리·초기 렌더 시간이 목록 크기에 비례 폭발한다. 10건 테스트 데이터에선 차이가 없어 운영 데이터에서 발견되는 부류.

### 5. dispose 누락 — 컨트롤러·구독 누수
❌ TextEditingController·AnimationController·StreamSubscription·Timer를 만들고 dispose() 미구현
✅ **initState에서 만든 것은 dispose에서 전부 해제** — 1:1 대응을 리뷰 체크리스트로. AnimationController는 미해제 시 ticker가 영원히 돈다
**왜**: 화면을 떠나도 리스너·타이머가 살아 메모리 누수 + 백그라운드 CPU + "이미 dispose된 위젯에 setState" 크래시(`setState() called after dispose()`)로 이어진다.

### 6. async 갭 너머의 BuildContext
❌ `await api.save(); Navigator.of(context).pop();` — await 동안 위젯이 unmount됐으면 죽은 context 사용
✅ `await api.save(); if (!context.mounted) return; Navigator.of(context).pop();` — **모든 await 뒤 context 사용 전 mounted 확인** (lint `use_build_context_synchronously`)
**왜**: 사용자가 await 중 뒤로가기를 누르는 건 정상 흐름이다. 죽은 context 접근은 크래시 또는 엉뚱한 화면 조작 — 재현이 타이밍 의존이라 QA를 잘 통과한다.

### 7. 상태관리 백화점
❌ 한 앱에 Provider + BLoC + GetX 혼재 (튜토리얼 따라 하나씩 늘어남)
✅ **기본 1개: Riverpod**(컴파일 타임 안전·테스트 용이— 본 스킬 기본값) — escape hatch: 팀이 이미 BLoC 숙련이면 BLoC 유지가 옳다. 단순 앱은 내장 ValueNotifier로 충분
**왜**: 상태관리 혼재는 데이터 흐름 추적을 불가능하게 한다. 선택 기준은 유행이 아니라 "팀이 일관되게 쓸 수 있는가" — 어떤 것이든 하나로 통일이 어떤 조합보다 낫다.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 프레임 예산 | build+layout+paint 16ms(60fps)/8ms(120fps) 내 | jank 정의 |
| jsonDecode isolate 문턱 | 응답 ~100KB+ 또는 파싱 수십 ms+ 면 compute() | 안티패턴 3, 정확 문턱 실측 |
| 목록 | 동적 데이터는 항목 수 무관 .builder 기본 | 안티패턴 4 |
| lint | `flutter_lints` 기본셋 + prefer_const·use_build_context_synchronously 의무 | 안티패턴 1·6 기계 검출 |
| 이미지 | 표시 크기로 리사이즈(cacheWidth/Height) — 원본 디코딩 금지 | 메모리 OOM 단골 |

## 워크플로우 (Flutter 작업 1건)

1. **상태 지도** — 어떤 데이터가 어디서 변하고 누가 보는가 → setState 말단 배치 설계.
2. **작성** — 새 위젯은 `lib/` 의 프로젝트 기능 디렉토리 규칙대로(화면은 `screens/`·`features/` 등 기존 관례), 기존 파일 덮어쓰기 대신 Edit.
3. **검증 (copy-paste)**:
   ```
   flutter analyze
   flutter test
   dart format --set-exit-if-changed .
   ```
4. **성능 의심 시** — 추측 금지, DevTools로 실측:
   ```
   flutter run --profile        # profile 모드에서만 성능 판단 (debug 모드 성능은 무의미)
   ```
   DevTools Performance 탭에서 16ms 초과 프레임의 원인 위젯 확인.

## 출력 템플릿

```
## [화면/기능] Flutter 구현
### 리빌드 지도: <setState/상태 변경 지점 → 영향 범위 (말단인가?)>
### isolate: <메인 밖으로 보낸 작업 / 없으면 "CPU 무거운 작업 없음">
### dispose: <생성 리소스 → 해제 대응표>
### 검증: $ flutter analyze → <결과> / flutter test → <1줄>
### 확인 필요
```

### 작성 예시

```
## 실시간 시세 목록 화면 (가정)
### 리빌드 지도: 시세 갱신 → 해당 종목 행 위젯만 (행을 별도 ConsumerWidget으로 분리, 목록 틀은 const)
### isolate: 초기 로드 800KB JSON → Isolate.run으로 파싱 (실측 파싱 70ms — 메인이었으면 4프레임 스킵)
### dispose: ScrollController 1, StreamSubscription 1 → dispose에서 2건 해제 확인
### 검증: $ flutter analyze → 0건 / flutter test → 6 passed
### 확인 필요: 120fps 단말 대응(8ms 예산)은 profile 실측 후 판단
```

❌ "버벅이네 → 위젯 캐싱 라이브러리 검색" (측정 없이 도구부터)
✅ "profile 모드 DevTools → 초과 프레임의 원인 → 안티패턴 1~4 대조 — 측정에서 수정으로"

### 사용자가 권고를 거부하면

- "const 일일이 붙이기 귀찮다" → lint auto-fix(`dart fix --apply`)로 비용 제거 1회 제안, 거부 시 기록(partial).
- "Riverpod 말고 GetX 쓰고 싶다" → 팀 숙련이 근거면 존중(일관성 > 도구 우열) — 혼재만 막고 기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

### 판단 불가 시 (확인 절차)

- **무엇이 막히나**: ① 상태관리 선택(팀 숙련도가 코드만으론 안 보일 때 Riverpod/BLoC/내장) ② isolate 분리 문턱(파싱 비용이 실측 전이라 불명) ③ 120fps 단말 대응 여부(8ms 예산 — 타깃 단말이 외부 사실) ④ 네이티브 채널이 필요한 기능을 Flutter 내에서 풀지 플랫폼 코드로 내릴지.
- **누구에게/어떻게**: 사용자에게 (대상 / 현재 후보안 / 근거 / 기대 답변) 4요소로 질의 — 추측으로 상태관리 라이브러리를 도입하거나 isolate를 가르지 않는다. 예: "이 파싱을 (대상)isolate로 뺄지 / (현 후보)메인 유지 / (근거)응답 크기 미확인 / (기대)운영 응답 평균 크기가 100KB를 넘습니까?"
- **기대값**: 답을 받으면 그대로 반영. 못 받으면 가장 보수적 기본값(Riverpod·메인 유지하되 profile 실측 TODO·60fps 기준)으로 진행하고 해당 줄에 `// 확인 필요:` 라벨을 남긴다(partial — 전체 보류 금지).

## 실전 케이스 — "Skipped frames" — jsonDecode가 만든 출시 후 별점 하락 (반복 실증)

Flutter 커뮤니티에 반복 보고되는 표준 사고: 개발 중엔 작은 mock 데이터라 매끈하던 앱이, 운영 API의 수 MB 응답을 받자 목록 진입마다 0.5~1초 멈칫. 로그엔 `Skipped 47 frames!`. 원인은 메인 isolate의 jsonDecode + ListView(children:) 콤보(안티패턴 3+4) — 디버그에선 "원래 느리니까"로 넘기고 릴리즈에서 사용자 리뷰로 발견된다. 교훈: ① 성능 판단은 profile 모드 + 운영 규모 데이터로만 ② "await 했으니 안 막힌다"는 Dart에선 거짓(단일 isolate) ③ 데이터 크기는 항상 운영 기준으로 테스트. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — jank 산식 · dispose 누수 · async context 크래시 실증 (코어스펙 1겹)

## 한계

- 네이티브 플랫폼 채널(Swift/Kotlin 측 구현)·스토어 심사 대응은 범위 밖 — 일반 지식 + 공식 문서로.
- Flutter Web·데스크톱은 모바일과 성능 특성이 다름 — 본 스킬 기준은 모바일.
- 크로스플랫폼 선택 자체(Flutter vs RN)는 라우터(dev-chief-architect) 영역 — 이 스킬은 Flutter 선택 이후의 매뉴얼.
