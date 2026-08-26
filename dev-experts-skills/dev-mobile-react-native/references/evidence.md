# dev-mobile-react-native evidence — 실증 사례

## 1. Airbnb RN 철수 5부작 (2018) — 시점 박힌 교훈 (공개 기술 블로그)

- **무슨 일**: Airbnb가 "React Native at Airbnb" 5부작으로 2년 운용 경험과 철수 결정을 공개. 당시 사유: ① 브리지 직렬화 병목(JSON으로 모든 통신) ② JS+iOS+Android 3중 전문성 요구 ③ RN 업그레이드마다 대규모 작업 ④ 네이티브 기능 경계에서의 복잡성.
- **2026 시점 재평가**: ①은 New Architecture(JSI·Fabric — 직렬화 없는 직접 호출)로 구조 해소, ③은 Expo SDK가 관리 대행, ②④는 잔존하되 Expo config plugin·development build로 경계 비용 축소. Shopify·Microsoft·Discord의 지속 대규모 운용이 반례 데이터.
- **이 스킬과의 연결**: 기술 평가 글은 반드시 시점·버전과 함께 인용 — "RN은 느리다(2018)"를 2026 의사결정에 그대로 쓰는 게 본 스킬군이 막는 부패 함정의 표본.

## 2. 목록 이미지 OOM — "저사양 Android에서만 죽어요" (크래시 리포트 단골)

- **무슨 일**: 피드형 앱의 표준 크래시 — 고해상 원본 이미지를 목록 썸네일로 그대로 로드, 스크롤 누적으로 네이티브 힙 폭발. iOS·고급 단말은 버티고 RAM 적은 Android에서만 죽어 "특정 기기 크래시"로 보고된다.
- **산식**: 디코딩 메모리 = 원본 W×H×4바이트(표시 크기 무관). 4000×3000 = 48MB/장. ScrollView+map(가상화 없음)과 결합하면 화면 밖 이미지도 전부 적재.
- **방어**: ① CDN 리사이즈 변형 URL(표시크기×2 픽셀 밀도) ② expo-image(디스크/메모리 캐시·다운샘플링) ③ FlatList 가상화로 적재 수 자체를 제한 — 3겹이 표준.
- **2026 보강**: 행이 수백~수천이거나 복잡 행이면 FlashList v2(셀 재활용·추정치 불필요)가 현 표준 권장. v2는 New Architecture 전용·JS 전용이라 SDK 54부터 제공되고 New Architecture가 기본 강제된 SDK 55+에서는 Expo Go에서 dev client 없이 동작하며, v1의 `estimatedItemSize` 등은 제거됨(구 아키텍처면 `@shopify/flash-list@^1.7` 고정). 출처: Expo 공식 `@shopify/flash-list` 문서 https://docs.expo.dev/versions/latest/sdk/flash-list/ · Shopify FlashList https://shopify.github.io/flash-list/ (1차 공식·라이브러리 메인테이너).

## 3. 네이티브 모듈 버전 부정합 — "빌드는 되는데 그 화면만 죽어요" (생태계 반복 실증)

- **무슨 일**: RN 코어 업그레이드 후 특정 라이브러리 화면 진입 시에만 크래시(`UIManager`·TurboModule 관련 네이티브 예외). 빌드·타입체크 전부 통과라 배포 후 발견되는 최악 패턴.
- **메커니즘**: 네이티브 모듈은 RN 코어의 네이티브 API에 컴파일 타임 결합 — semver가 JS 계약만 보장하고 네이티브 ABI 호환은 보장하지 않는다. New Architecture 전환기(라이브러리별 지원 시차)에 특히 빈발.
- **방어**: ① 패키지 추가·업그레이드는 `npx expo install`/`--fix`로만 ② `npx expo-doctor`를 CI에 ③ SDK 업그레이드는 공식 가이드 순서 + 전 화면 스모크 테스트. bare 프로젝트는 이 매트릭스를 수동 관리하는 것 — 안티패턴 1의 비용 실체.

> 출처:
> - Airbnb 5부작 — "React Native at Airbnb"(1편) https://medium.com/airbnb-engineering/react-native-at-airbnb-f95aa460be1c · "Sunsetting React Native" https://medium.com/airbnb-engineering/sunsetting-react-native-1868ba28e30a (2018-06, Airbnb 엔지니어링 1차 공개 글).
> - New Architecture 구조 해소·Hermes 기본·iOS 네이티브 모듈 호출 경로 단축 — Expo SDK 56 공식 체인지로그 https://expo.dev/changelog/sdk-56 (RN 0.85.2·React 19.2·Hermes v1 기본, 2026-05 공식).
> - 버전 정합/패키지 관리 — Expo SDK 업그레이드 공식 가이드 https://docs.expo.dev/workflow/upgrading-expo-sdk-walkthrough/ (`npx expo install`·한 버전씩 업그레이드, 1차 공식).
> - 크래시 리포트 패턴은 커뮤니티 반복 실증(특정 1차 출처 없음 — 패턴 집적).
> 2026-06 기준, RN 0.85 / Expo SDK 56 / React 19.2.
