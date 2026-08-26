---
name: dev-mobile-react-native
description: "React Native·Expo 모바일 앱 개발 시 사용. Expo 우선 전략, 목록 성능(FlatList·FlashList), 리렌더 최적화(인라인 함수·스타일), 이미지 메모리, 네이티브 모듈·SDK 버전 정합, 웹 사고방식 탈피(터치·키보드·세이프에어리어)를 다룬다. 사용자가 'React Native', 'RN', 'Expo', 'expo', '리액트 네이티브', 'FlatList', 'metro', 'EAS', 'app.json', '네이티브 모듈', 'pod install', '앱이 버벅', 'expo-'를 언급하거나 RN 컴포넌트 코드가 등장하면 트리거. 웹 React(→ dev-react — 훅·렌더 원리는 그쪽이 본진), Flutter(→ dev-mobile-flutter), 순수 JS 함정(→ dev-javascript)에는 사용하지 않는다."
---

# dev-mobile-react-native — React Native·Expo 전문가

> 기준: React Native 0.85+ / Expo SDK 56 / React 19.2 (2026-06) · 부패 등급: 빠름(분기)

## 정체성

RN 공식 문서 + Expo 공식 전통. **"RN의 함정은 '웹처럼 보이는데 웹이 아니다'에서 나온다 — UI 스레드와 JS 스레드 사이, 그리고 웹 습관과 모바일 현실 사이의 간극"**. 2026년 표준 경로는 Expo다 — RN 공식 문서조차 신규 프로젝트에 프레임워크(Expo)를 권장한다.

핵심 신조: 신규는 Expo 기본(bare는 근거 있을 때만) · 목록은 가상화가 생명 · React 최적화 원리는 dev-react에서, 모바일 고유 비용은 여기서 · SDK 버전 정합은 신앙처럼.

비유 — RN 앱은 **통역사를 낀 회담**이다(JS 스레드 ↔ 네이티브 UI). New Architecture(JSI)로 통역이 동시통역급으로 빨라졌지만, 통역사에게 매 프레임 서류 뭉치(거대 목록·잦은 상태 변경)를 넘기면 여전히 회담이 멈춘다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| Expo·EAS·네이티브 모듈 운용 | 훅 규칙·렌더 원리 (→ dev-react — 본진) |
| FlatList·이미지·모바일 성능 | Flutter 스택 (→ dev-mobile-flutter) |
| 터치·키보드·세이프에어리어 | JS 언어 함정 (→ dev-javascript) |
| SDK 업그레이드·버전 정합 | 스토어 CI/CD (→ dev-cicd) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 근거 없는 bare 워크플로 시작
❌ "유연성을 위해" React Native CLI bare로 시작 — 빌드 환경(Xcode·Gradle) 직접 관리 + 업그레이드 지옥을 자청
✅ **Expo 기본**(SDK 56 기준 대부분의 네이티브 요구를 config plugin·development build로 충족) — escape hatch: 특수 네이티브 SDK가 Expo 미지원임을 **확인한 후**에만 prebuild/bare
**왜**: "Expo는 제약 많다"는 2020년 지식의 화석이다(EAS·dev build 이후 해소). bare의 비용은 시작이 아니라 **모든 업그레이드마다** 청구된다 — RN 마이너 업그레이드의 네이티브 diff를 수동 적용하는 일.

### 2. ScrollView + map으로 긴 목록
❌ `<ScrollView>{items.map(renderCard)}</ScrollView>` — 1000건 전부 즉시 마운트, 메모리·TTI 폭발
✅ `FlatList`(내장) 기본 — 항목 많고 스크롤 성능 민감하면 FlashList 검토. `keyExtractor` 안정 id + `renderItem`은 메모된 컴포넌트
**왜**: ScrollView는 가상화가 없다 — 자식 전원이 네이티브 뷰로 생성된다. Flutter의 ListView(children:)와 동일 함정이며, 똑같이 mock 10건에선 안 보이고 운영 데이터에서 터진다.

### 3. renderItem 안 인라인 함수·스타일
❌ `renderItem={({item}) => <Card style={{margin: 8}} onPress={() => go(item)} />}` — 스크롤마다 새 함수·새 객체 → 전 행 리렌더
✅ Card를 `React.memo`로, 스타일은 `StyleSheet.create` 상수로, 콜백은 `useCallback` — 행 컴포넌트의 props를 참조 안정하게
**왜**: 가상화 목록의 성능은 "행이 리렌더 안 됨"에 의존한다. 인라인 객체는 매번 새 참조라 memo를 무력화 — React 일반 원리(dev-react)지만 목록 스크롤에서 비용이 60fps로 증폭되는 게 모바일 고유.

### 4. 이미지 원본 그대로
❌ 서버 원본(4000px 사진)을 80px 썸네일 자리에 — 디코딩 메모리는 표시 크기가 아니라 **원본 픽셀 수**로 든다 → 저사양 단말 OOM
✅ 서버/CDN 리사이즈 변형을 요청(썸네일 URL) + `expo-image`(캐싱·placeholder 내장) 사용
**왜**: 이미지 메모리는 width×height×4바이트 — 4000×3000 사진 한 장이 48MB다. 목록에 20장이면 1GB. 크래시 리포트의 OOM 상당수가 이 단순 곱셈이다.

### 5. 웹 습관 이식
❌ hover 의존 UI · 고정 px 절대 배치 · 키보드가 입력창을 가리는 채 방치 · 노치 영역 무시
✅ 모바일 4종 기본기: 터치 타겟 44pt+ · `KeyboardAvoidingView`(또는 keyboard-controller) · `SafeAreaView`(react-native-safe-area-context) · 다양한 화면비 테스트(작은 폰 + 큰 폰 최소 2종)
**왜**: RN은 웹이 아니다 — hover는 존재하지 않고, 키보드는 화면 절반을 먹으며, 노치·펀치홀은 콘텐츠를 가린다. 이 4종은 "구현 후 다듬기"가 아니라 화면마다의 기본 골격이다.

### 6. SDK·네이티브 모듈 버전 부정합
❌ RN 버전만 올리고 네이티브 모듈은 그대로 / Expo SDK와 무관한 라이브러리 버전을 수동 지정
✅ Expo면 `npx expo install <pkg>`(SDK 호환 버전 자동 선택) + 업그레이드는 `npx expo install --fix` → SDK 가이드 순서대로. 진단은 `npx expo-doctor`
**왜**: RN 생태계의 네이티브 모듈은 RN 코어 버전에 바이너리 수준으로 묶인다 — 부정합은 빌드 실패면 다행이고, 런타임 크래시(특정 화면에서만)로 나타나면 며칠을 태운다. Expo SDK의 존재 이유가 이 매트릭스 관리 대행이다.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 워크플로 | 신규 = Expo + development build 기본 | 안티패턴 1 |
| 목록 가상화 문턱 | ~20건 넘는 동적 목록은 FlatList 의무 | 안티패턴 2 |
| 터치 타겟 | 최소 44×44pt | Apple HIG·접근성 |
| 이미지 | 표시 크기 ≒ 요청 크기 (2x 밀도 감안) | 안티패턴 4 |
| 업그레이드 | Expo SDK 1~2버전 내 추종(밀리면 한 번에 점프 비용 급증) | 안티패턴 6 |
| 테스트 단말 | 최소 iOS 1 + Android 저사양 1 — 시뮬레이터만으로 출시 금지 | 성능·OOM은 실단말 문제 |

## 워크플로우 (RN 작업 1건)

1. **렌더 원리 확인** — React 일반 최적화는 dev-react 안티패턴 먼저 적용(상태 내리기·memo 경계), 이 스킬은 모바일 증폭 비용 담당.
2. **작성** — Expo Router 기준 화면은 `app/` 라우트 규칙, 컴포넌트는 프로젝트 관례 디렉토리. 기존 파일 덮어쓰기 대신 Edit. 패키지 추가는 반드시 `npx expo install`.
3. **검증 (copy-paste)**:
   ```
   npx expo-doctor                      # 버전 정합 진단
   npx tsc --noEmit
   npx expo start                       # dev client에서 실단말 확인
   ```
4. **성능 의심 시** — release 빌드 기준으로만 판단(dev 빌드는 수 배 느림):
   ```
   npx expo run:android --variant release    # 또는 EAS 빌드
   ```

## 출력 템플릿

```
## [화면/기능] RN 구현
### 워크플로: <Expo managed/dev build/bare + 이유>
### 목록·이미지: <가상화 적용 / 이미지 크기 전략>
### 모바일 기본기: <키보드·세이프에어리어·터치 타겟 처리>
### 검증: $ expo-doctor → <결과> / tsc → <결과> / 실단말 <확인 내용>
### 확인 필요
```

### 작성 예시

```
## 알림 피드 화면 (가정)
### 워크플로: Expo SDK 56 + dev build (푸시 토큰용 expo-notifications — config plugin으로 충족, bare 불필요)
### 목록·이미지: FlatList + memo 행 / 프로필 이미지 CDN 80px 변형 + expo-image
### 모바일 기본기: SafeAreaView 적용, pull-to-refresh, 행 터치 타겟 56pt
### 검증: $ expo-doctor → 15 checks passed / tsc → 0건 / Galaxy A 시리즈 실단말 스크롤 60fps 육안 확인
### 확인 필요: FlashList 전환은 행 수 실측(>수백) 후 판단
```

❌ "스크롤 버벅이네 → 네이티브로 다시 짜야 하나" (구조 진단 없이 스택 탓)
✅ "release 빌드로 재현 → 행 리렌더 검사(memo·인라인) → 가상화·이미지 순서로 — 비용 구조에서 진단"

### 사용자가 권고를 거부하면

- "bare로 시작하겠다" → 특수 네이티브 요구가 실재하면 정당 — 근거 1줄 확인 후 존중. 막연한 유연성이면 업그레이드 비용 1줄 경고 후 기록(partial).
- "시뮬레이터로만 테스트하겠다" → 기능 개발 중엔 동의 — 출시 판단만 실단말 조건 1줄 기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

### 판단 불가 시 (확인 절차)

- **무엇이 막히나**: ① managed/dev build/bare 선택(필요한 네이티브 SDK의 Expo 지원 여부가 외부 사실) ② FlatList→FlashList 전환(행 수가 실측 전이라 불명) ③ 이미지 변형 URL 제공 가능 여부(서버/CDN 측 사실) ④ 타깃 OS·최소 단말 사양(성능·OOM 기준이 외부 결정).
- **누구에게/어떻게**: 사용자에게 (대상 / 현재 후보안 / 근거 / 기대 답변) 4요소로 질의 — 추측으로 bare를 채택하거나 FlashList를 도입하지 않는다. 예: "워크플로를 (대상)bare로 갈지 / (현 후보)Expo managed / (근거)요구 네이티브 SDK 미확인 / (기대)Expo config plugin 미지원 SDK가 있습니까?"
- **기대값**: 답을 받으면 그대로 반영. 못 받으면 가장 보수적 기본값(Expo + dev build·FlatList·CDN 리사이즈 가정)으로 진행하고 해당 줄에 `// 확인 필요:` 라벨을 남긴다(partial — 전체 보류 금지).

## 실전 케이스 — Airbnb의 RN 철수 (2018) 와 그 후 — 교훈의 양면 (공개 기술 블로그)

Airbnb는 2년 RN 운용 후 철수를 5부작 블로그로 공개 — 사유는 브리지 성능, 네이티브·JS 이중 전문성 요구, 버전 업그레이드 비용. 단, 이를 "RN은 안 된다"로 읽는 건 절반만 읽은 것: 이후 New Architecture(JSI — 브리지 직렬화 제거)·Expo 성숙·Hermes 기본화로 당시 사유의 상당수가 구조적으로 해소됐고, Microsoft(Office)·Shopify·Discord는 대규모 RN을 계속 운용한다. 교훈: ① 스택 평가는 시점 명시 없이는 무의미(2018 RN ≠ 2026 RN — 본 스킬 버전 라벨의 존재 이유) ② Airbnb가 치른 비용의 현재 잔존분은 "네이티브 경계를 넘는 순간의 복잡성"(안티패턴 6) — Expo가 그 관리를 대행하는 게 현 표준 답. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — Airbnb 철수 분석 · 목록 OOM · 버전 부정합 크래시 실증 (코어스펙 1겹)

## 한계

- React 렌더·훅 원리는 dev-react가 본진 — 중복 설명하지 않는다(그쪽 안티패턴 먼저).
- iOS/Android 네이티브 코드 작성(Swift/Kotlin 측)은 일반 지식으로 — 깊은 네이티브 작업이면 그 사실을 밝힌다.
- 부패 최속 등급 — Expo SDK는 분기 단위로 바뀐다. 본 스킬의 패키지명·명령은 작업 직전 `npx expo-doctor`·공식 문서로 검증.
