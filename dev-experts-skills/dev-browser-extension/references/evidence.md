# dev-browser-extension evidence — 실증 사례

## 1. The Great Suspender — 신뢰 채널의 탈취 (2021)

- **무슨 일**: 200만+ 사용자 확장이 익명 인수자에게 매각 → 추적 스크립트·원격 코드 실행 경로가 조용히 추가된 업데이트 배포 → 커뮤니티 발각 → Google이 악성 판정, 전 사용자 강제 비활성화. 유사 패턴(인기 확장 매입 후 악성화)이 이후로도 반복 — 확장 생태계의 구조적 공격 벡터로 정착.
- **메커니즘**: 확장 업데이트는 자동·무알림이다. 사용자가 설치 시점에 신뢰한 것은 코드가 아니라 **계정**이고, 계정은 거래된다.
- **개발자 측 교훈**: ① MV3 원격 코드 금지는 이 부류 대응 — 우회 시도(설정으로 위장한 코드 등)는 퇴출 사유 ② 권한 최소화는 자기 확장이 탈취됐을 때의 피해 상한 설정 ③ 수집 공시와 실제 트래픽의 불일치는 발각 즉시 제재.

## 2. SW 수명 — "개발자도구를 닫으면 다른 앱" (MV3 전환기 최다 함정)

- **무슨 일**: MV2→MV3 전환기(2022~2024) Chrome 개발자 포럼·스택오버플로 최다 질문 유형 — "background 변수가 가끔 사라진다", "setInterval이 안 돈다", "이벤트 리스너가 등록 안 된 것 같다". 전부 SW 이벤트 기반 수명(idle ~30초 종료) 미이해.
- **개발 중 못 보는 이유**: SW 개발자도구(inspect)를 열어두면 SW가 종료되지 않는다 — 즉 디버깅하는 동안만 버그가 사라진다. 하이젠버그의 교과서 사례.
- **올바른 패턴 3종**: ① 상태 → chrome.storage(이벤트 진입마다 복원) ② 주기 작업 → chrome.alarms(최소 간격 30초·SW 깨움) ③ 리스너 등록 → SW 최상위 동기 코드에서(비동기 후 등록하면 재기동 시 이벤트 유실).

## 3. 셀렉터 침묵 사망 — "별점 1점으로 알게 되는 고장" (운영 구조 실증)

- **무슨 일**: 특정 사이트에 기능을 얹는 확장(가격 비교·UI 개선류)의 표준 사멸 경로 — 대상 사이트 프론트 리뉴얼(클래스 해시 변경) → 셀렉터 전멸 → 확장은 에러 없이 "아무것도 안 함" → 개발자는 서버가 없어 모름 → 리뷰 폭탄으로 인지.
- **방어 설계**: ① 셀렉터 단일 모듈 집약(수리 시간 단축) ② 핵심 셀렉터 미발견 시 사용자 가시 배너 + (동의 기반) 익명 고장 신호 ③ 가능하면 사이트의 공개 API·구조적 마크업(JSON-LD 등) 우선 — DOM 셀렉터는 최후 수단.
- **이 스킬과의 연결**: 안티패턴 6. "남의 DOM은 계약 없는 API" — 깨짐을 전제로 한 감지·복구 설계가 코드보다 중요하다.

> 출처 (2026-06 확인):
> - [The extension service worker lifecycle — Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle) — SW 수명 1차 출처. idle 30초·단일 요청 5분·fetch 응답 30초 종료, "전역 변수는 SW 종료 시 소실 → storage 사용" 명시. 사례 2의 근거.
> - [chrome.alarms API 레퍼런스 — Chrome for Developers](https://developer.chrome.com/docs/extensions/reference/api/alarms) — alarms 최소 주기가 SW 수명에 맞춰 30초로 정렬됨을 확인. 사례 2 "주기 작업 → alarms"의 근거.
> - [Remotely hosted code — Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/migrate/remote-hosted-code) — MV3 원격 코드 금지 1차 출처. eval()·Function()·외부 JS 로드 차단, 로직은 패키지 동봉만 허용. 사례 1 교훈①의 근거.
> - [The Great Suspender removed for containing malware — 9to5Google (2021-02-04)](https://9to5google.com/2021/02/04/the-great-suspender-extension-has-been-removed-from-chrome-web-store-for-containing-malware/) — Great Suspender 사건 보도. 200만+ 설치, 익명 인수 후 악성 업데이트, Google 강제 비활성화 사실 확인. 사례 1의 근거.
> - [Message passing — Chrome for Developers](https://developer.chrome.com/docs/extensions/develop/concepts/messaging) — onMessage 비동기 응답 명세 1차 출처. 리스너가 `true`를 반환해야 sendResponse 채널이 유지됨. 안티패턴 4의 근거.
