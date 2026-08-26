# dev-kubernetes evidence — 장애·실증 사례

## 1. Reddit Pi-Day 장애 (2023-03-14) — 업그레이드와 화석 설정 (공식 포스트모템)

- **무슨 일**: K8s 1.23→1.24 업그레이드 직후 클러스터 네트워킹 전면 붕괴, 314분 장애. 원인: Calico route reflector가 `node-role.kubernetes.io/master` 라벨로 노드를 선택했는데, K8s가 1.20대에 "master→control-plane"으로 용어를 바꾸고 1.24에서 `master` 라벨을 실행 중 클러스터에서도 제거 → route reflector 대상 0 → BGP 라우팅 소멸.
- **진짜 근본 원인(공식 포스트모템의 핵심)**: 라벨 변경 자체는 changelog에 있었다. 함정은 **그 라벨에 route reflector가 의존한다는 사실이 어디에도 문서화되지 않았다**는 것 — 수동 설정한 담당자는 이미 퇴사. 즉 "changelog를 실제 시스템이 아니라 머릿속 모델에 대조"한 게 진짜 실패(Woods의 정리: 시스템이 복잡할수록 누구의 단일 모델도 부정확해진다).
- **이중 교훈**:
  1. **화석 설정**: 오래된 클러스터일수록 "그때는 표준이었던" 설정이 지뢰로 잔존 — 업그레이드 전 deprecated API·라벨·플래그 전수 스캔(pluto는 매니페스트/Helm 정적 분석, kubent는 라이브 클러스터 감사 — 둘은 상호보완, 둘 다 CI에서).
  2. **롤백 미검증**: 컨트롤플레인 다운그레이드는 공식 미지원 — "안 되면 롤백"이 전제인 변경 계획은 K8s 업그레이드에선 성립 안 한다. (Reddit의 복구 절차서는 수년 전 작성돼 이미 EOL 버전·CRI-O 전환 이전 기준이라 장애 중 실시간 재작성해야 했다.) 전진 복구 시나리오까지 리허설이 계획의 일부.
- **출처**: Overmind 분석 <https://overmind.tech/blog/reddit-pi-day-outage> (Reddit 공식 포스트모템 인용·해설, 신뢰: 사고 당사자 글 기반 1차 인용) · pluto <https://github.com/FairwindsOps/pluto> (공식 도구 리포)

## 2. Monzo 장애 (2017) — liveness/플랫폼 연쇄의 교과서 (공식 포스트모템)

- **무슨 일**: 은행 Monzo가 K8s+linkerd 스택에서 결제 처리 장애. 잠복 트리거는 2주 전 etcd를 3→9 노드로 확장한 것(클러스터 재구성 후 요청 타임아웃을 유발하는 K8s/etcd 클라이언트 버그로 linkerd가 K8s 업데이트를 못 받음). 금요일 결제 서비스 변경이 이를 노출 → 엔지니어가 linkerd 전체 재기동 → 이때 linkerd가 **빈 서비스 디스커버리 응답을 파싱하다 NullPointerException(K8s↔linkerd 버전 비호환)** → pod가 아예 안 떠 일부 장애가 플랫폼 전면 장애로 증폭. 즉 핵심 증폭기는 "전부 재기동"이라는 복구 시도 자체였다.
- **이 스킬과의 연결**: 안티패턴 2의 일반형 — **복구 메커니즘(재시작·재배포)이 장애를 증폭하는 구조**를 경계하라. liveness가 의존성까지 검사하면 의존성 순단 → 전 pod 동시 재시작 → 부팅 부하 → 더 큰 순단의 루프. 검사는 좁게, 재시작은 보수적으로.
- **점검 질문**: "이 probe가 실패하는 모든 시나리오에서, 재시작이 정말 도움이 되는가?" — 하나라도 '아니오'면 그 검사는 liveness가 아니라 readiness 소관.

## 3. OOMKilled — "로그에 아무것도 없이 죽어요" (운영 표준 진단)

- **무슨 일**: 컨테이너가 limit 초과로 커널 OOM killer에 즉사 — 앱은 정리 로그를 남길 기회조차 없다. 앱 로그만 보면 "그냥 끊김"이라 미스터리로 남는 표준 사례.
- **진단 1순위**: `kubectl describe pod` → Last State: Terminated, Reason `OOMKilled`, Exit Code 137(= 128+9, SIGKILL — 잡을 수도 유예할 수도 없는 즉살). 메모리 추이는 메트릭(`container_memory_working_set_bytes`)으로 — limit 대비 여유율 추적.
- **혼동 주의**: 137(SIGKILL/OOMKill)과 143(= 128+15, SIGTERM — graceful 종료 신호)을 구분. 또 Reason가 `Error`면 메모리가 아니라 probe 실패 등 다른 원인. **노드 압박(node-pressure) 축출**은 OOMKill과 다른 메커니즘 — pod status가 `Failed`/Reason `Evicted`로 뜨고 pod 전체가 제거된다(limit 안 넘겨도 발생).
- **흔한 진범**: ① JVM/언어 런타임이 컨테이너 limit를 인지 못 하고 호스트 메모리 기준 힙 설정(현대 JVM은 컨테이너 인지 — 구버전·수동 -Xmx 주의) ② 점진 누수(→ 해당 언어 스킬) ③ limit가 실사용보다 낮게 잡힘(실측 없는 복붙 값).
- **이 스킬과의 연결**: 안티패턴 1·6. "describe 먼저"가 며칠짜리 미스터리를 5분으로 줄인다.

> 출처(웹 검증 완료, 2026-06):
> - Reddit Pi-Day(2023-03-14): Overmind 해설 <https://overmind.tech/blog/reddit-pi-day-outage> — Reddit 공식 포스트모템 인용·분석(신뢰: 사고 당사자 글 1차 인용)
> - Monzo(2017-10): InfoQ 요약 <https://www.infoq.com/news/2017/11/Monzo-Outage-Post-Mortem/> · 원문은 Monzo 커뮤니티 포럼(Beattie)·KubeCon EU 2018 "Anatomy of a Production Kubernetes Outage" 키노트
> - 버전 지원선: K8s 공식 version-skew 정책 <https://kubernetes.io/releases/version-skew-policy/> — 2026-06 기준 최신 1.36, 패치 지원 1.36/1.35/1.34(최신 3 마이너)
> - deprecated API 스캔 도구: pluto <https://github.com/FairwindsOps/pluto>(매니페스트/Helm 정적 분석) · kubent(Kube No Trouble, 라이브 클러스터 감사)
> - OOMKill/exit code: 137 = 128+9(SIGKILL), 143 = 128+15(SIGTERM) — Linux signal+128 관례(K8s describe pod Last State에 Reason OOMKilled로 표기)
