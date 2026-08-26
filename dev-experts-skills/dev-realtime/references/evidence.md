# dev-realtime evidence — 장애·실증 사례

## 1. Slack 2021-01-04 — 재연결 폭발 + 축소된 인프라 (공식 포스트모템)

- **묶음 일**: 연휴 후 첫 출근 월요일, 트래픽 급증 중 클라우드 네트워크 이상으로 연결 대량 단절 → 클라이언트 재연결 쇄도 → 프로비저닝 서비스 과부하 → 수 시간 장애. 연휴 동안 낮은 트래픽 기준으로 축소된 인프라가 증폭 요인이 됐다. (공식 분석은 트리거를 AWS Transit Gateway가 복귀 수요 급증을 못 따라가 발생한 패킷 손실로 지목 — 버그가 아니라 포화/saturation 장애였다.)
- **구조 복구**: ① 트리거(네트워크 단절)는 사소했다 — 피해는 증폭 구조(동시 재연결)가 만들었다 ② 오토스케일은 "느린 증가"에 맞춰져 있고 재연결 폭발은 수직 상승이라 못 따라갔다 ③ 예측 가능한 동시 접속 이벤트(연휴 복귀·정시 알림)는 사전 워밍이 정답.
- **클라이언트 의무 도출**: 지수 백오프 + 지터 + 재연결 시 무거운 초기화(전체 동기화) 지연 시행 — "전 클라이언트가 동시에 가장 빽빽 요청" 최악 조합이다.

## 2. "55초마다 끊겨요" — 경로상 idle 정책 진단 (운영 표준 사고)

- **묶음 일**: WS/SSE가 특정 시간(60s 근처가 최다)마다 조용히 끊기는 보고 — 코드 어디에도 타임아웃이 없는데. 진범은 경로상 중간 장비: nginx `proxy_read_timeout`(기본 60s), 클라우드 LB idle/백엔드 타임아웃(AWS ALB idle 기본 60s, GCP HTTP LB 백엔드 서비스 타임아웃 기본 30s — LB 종류·설정마다 30s~수백 s로 다름), 통신사 NAT(모바일 — 수십 초~수 분). 무이벤트 구간이 길수록 발현.
- **진단 절차**: ① 끊김 간격의 규칙성 확인(고정 간격 = 정책, 무작위 = 네트워크) ② 경로 인벤토리(클라→CDN→LB→프록시→서버)와 각 idle 설정 대조 ③ 하트비트 주기 < 최소값으로 설정 후 재발 관찰.
- **이 스킬과의 연결**: 안티패턴 4. "내 코드엔 끊는 데가 없어요"가 맞다 — 끊는 건 경로다. 하트비트는 기능이 아니라 인프라 호환성 장치.

## 3. SSE 재평가 — "WS의 절반 비용으로 푸시의 대부분" (생태계 추세)

- **묶음 일**: LLM 스트리밍 응답(ChatGPT·Claude류 UI)의 표준이 SSE로 정착하며 재조명 — 단방향 푸시면 SSE가 WS 대비: HTTP 그대로(인증·프록시·HTTP/2 멀티플렉싱 호환), 브라우저 `EventSource`의 자동 재연결+`Last-Event-ID` 내장(WHATWG 스펙 명시 동작), 디버깅이 `curl -N`으로 끝남.
- **한계도 정직하게**: 단방향 전용(클라→서버는 별도 HTTP), 브라우저 동시 연결 제한(HTTP/1.1은 도메인당 6 — HTTP/2로 해소), 바이너리 비지원(텍스트 프레임), `EventSource`는 커스텀 헤더 불가(Authorization 토큰은 쿠키/쿼리로 우회).
- **이 스킬과의 연결**: 안티패턴 1의 사다리 중간 단계가 실전에서 검증된 사례 — "양방향이 정말 필요한가"를 묻는 근거. 시세 푸시·알림·진행률 같은 단방향 요구는 SSE가 기본 답이다.

## 출처 (1차 출처 우선 — 2026-06 웹 확인)

- [Slack's Outage on January 4th 2021 — Engineering at Slack](https://slack.engineering/slacks-outage-on-january-4th-2021/) — 공식 포스트모템 1차 출처. 재연결 쇄도·축소 인프라·점진 수용 복구를 당사자가 서술.
- [nginx ngx_http_proxy_module — proxy_read_timeout](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_read_timeout) — 공식 모듈 문서. `proxy_read_timeout` 기본 60s 명시(읽기 사이 무통신 시간 기준).
- [AWS — Connection idle timeout (Application Load Balancers)](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-load-balancer-attributes.html) — AWS 공식. ALB connection idle timeout 기본 60s.
- [GCP — Backend services overview](https://docs.cloud.google.com/load-balancing/docs/backend-service) — Google 공식. HTTP(S) LB 백엔드 서비스 타임아웃 기본 30s(요청/응답 기준), 클라이언트 keepalive 610s 등 LB별 idle 정책이 제각각임의 근거(구체 수치는 페이지 내 timeout 절 참조).
- [WHATWG HTML Living Standard §9.2 Server-sent events](https://html.spec.whatwg.org/multipage/server-sent-events.html) — SSE 1차 스펙. `EventSource` 자동 재연결·`retry:`·`Last-Event-ID` 재전송·CR/LF·NULL 금지 ID 규칙을 규범적으로 정의.
- [MDN — Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) — 구현 가이드 보조 출처. `id`/`retry` 필드, 재연결 동작, 커스텀 헤더 불가 한계.
