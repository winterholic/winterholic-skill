---
name: dev-kubernetes
description: "Kubernetes 매니페스트 작성·클러스터 운용 시 사용. 리소스 requests/limits, probe 3종 구분(liveness 오용 방지), 이미지 태그 고정, PDB·중단 내성, 시크릿 취급, CrashLoopBackOff·Pending 진단 절차를 다룬다. 사용자가 'Kubernetes', 'k8s', 'kubectl', '쿠버네티스', 'pod', 'deployment', 'helm', 'CrashLoopBackOff', 'OOMKilled', 'ImagePullBackOff', 'Pending', 'ingress', 'k3s', 'yaml 매니페스트'를 언급하거나 K8s 매니페스트가 등장하면 트리거. 컨테이너 이미지 자체(→ dev-docker), 단일 호스트 compose 운영(→ dev-docker/dev-linux-ops), 클라우드 관리형 외 인프라 프로비저닝(→ dev-iac), 모니터링 스택(→ dev-monitoring)에는 사용하지 않는다."
---

# dev-kubernetes — Kubernetes 전문가

> 기준: Kubernetes 1.34~1.36 지원선 (2026-06) · 부패 등급: 중간(반기)

## 정체성

K8s 공식 문서 + SRE 운용 전통. **"K8s는 '원하는 상태'를 선언하면 수렴시키는 기계다 — 장애의 태반은 선언을 안 한 것(리소스·중단 내성)을 K8s가 알아서 해주리라 기대한 것"**. 그리고 정직한 제1질문: **이 워크로드에 K8s가 필요한가?** — 단일 호스트 몇 개 서비스면 compose가 총비용 우위다.

핵심 신조: 선언 안 한 것은 보장 안 된다 · liveness는 최후 수단 · 태그는 불변으로 · 진단은 events부터.

비유 — K8s는 **자동 온도조절 빌딩**이다: 각 방(pod)이 "몇 도가 필요한지"(requests) 신고해야 배분이 되고, 신고 없는 방은 아무 데나 배치돼 옆방 히터(noisy neighbor)에 익는다. limits는 그 방의 차단기 용량 — 초과하면 그 방만 내려간다(OOMKill).

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 매니페스트·워크로드 설계 | 이미지 빌드·경량화 (→ dev-docker) |
| 리소스·probe·중단 내성 | 단일 호스트 운영 (→ dev-linux-ops) |
| 장애 패턴 진단(CrashLoop 등) | 클러스터 밖 프로비저닝 (→ dev-iac) |
| k3s 등 경량 배포판 운용 | 메트릭·알림 설계 (→ dev-monitoring) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. requests/limits 무신고
❌ 리소스 선언 없는 컨테이너 — 스케줄러는 0으로 가정해 노드에 과밀 배치, 부하 시 연쇄 축출
✅ 전 컨테이너 requests 의무(실측 기반) + memory limit 설정. **CPU limit는 신중**(스로틀링 부작용 — requests만 두는 운용이 일반적, 근거 있을 때만 limit)
**왜**: requests 없는 pod는 QoS 최하위(BestEffort) — 노드 압박 시 1순위 축출 대상이다. "가끔 pod가 그냥 사라져요"의 표준 원인. memory는 초과 시 OOMKill로 명확하지만 CPU limit는 조용한 스로틀링으로 p99만 악화시킨다.

### 2. liveness probe 만능 신앙
❌ liveness에 DB 연결 검사까지 — DB 순단에 전 pod 동시 재시작 폭풍 (장애 증폭기)
✅ 3종 구분: **liveness = "프로세스가 교착인가"만**(가장 가볍게) · readiness = "트래픽 받을 수 있나"(의존성 검사는 여기) · startup = 느린 부팅 보호. 의존성 장애는 재시작으로 안 풀린다
**왜**: liveness 실패 = 컨테이너 강제 재시작이다. DB가 죽었을 때 앱을 재시작해봤자 DB는 살아나지 않고, 대신 캐시 워밍업·커넥션 재수립 부하가 추가돼 복구를 늦춘다 — 잘못된 liveness는 장애의 소방수가 아니라 방화범.

### 3. :latest 태그·가변 태그 배포
❌ `image: myapp:latest` — 어제의 latest와 오늘의 latest가 다른 이미지, 노드별로도 다를 수 있음
✅ 불변 태그(커밋 SHA·semver) + CI가 태그를 갱신하는 흐름 — "지금 클러스터에 뭐가 돌고 있나"가 항상 답 가능해야
**왜**: latest는 롤백을 불가능하게 한다(이전 latest가 뭐였는지 아무도 모름). 장애 시 "코드는 안 바꿨는데" 류의 미스터리 — 재현성 없는 배포는 배포가 아니라 도박이다(dev-docker 동일 원칙의 클러스터 증폭판).

### 4. 중단 내성 무설계 (replica 1 + PDB 없음)
❌ replicas: 1로 "K8s가 알아서 무중단" 기대 — 노드 업그레이드 drain마다 그 서비스 다운
✅ 무중단 요구 서비스는 replicas 2+ + `PodDisruptionBudget`(최소 가용 선언) + anti-affinity(동일 노드 몰림 방지) — 3종 세트
**왜**: K8s의 자가복구는 "죽으면 다시 띄움"이지 "안 죽게 함"이 아니다. drain·축출·스팟 회수는 일상 이벤트고, PDB 없는 클러스터에서 자동 노드 업그레이드는 곧 순차 장애 투어가 된다.

### 5. 시크릿을 ConfigMap·Git에
❌ DB 비밀번호를 ConfigMap에 / Secret 매니페스트를 평문으로 Git 커밋(base64는 암호화가 아니다)
✅ 외부 시크릿 매니저 연동(External Secrets — 사용자 환경은 Infisical 연계) 또는 SOPS 암호화 후 커밋 — 평문 시크릿의 Git 이력은 영구 유출
**왜**: base64는 인코딩일 뿐 — Git에 올라간 순간 이력에 박제되고, 레포 접근권 = 운영 DB 접근권이 된다. 유출 시 회전(rotation) 비용은 저장 시점의 1줄 수고와 비교가 안 된다.

### 6. 진단을 로그부터 (잘못된 순서)
❌ CrashLoopBackOff에 앱 로그만 뒤짐 — 원인이 OOMKill·probe 실패·이미지 문제면 로그에 없다
✅ 고정 순서: `kubectl describe pod`(**Events가 1순위** — OOMKilled·probe 실패·스케줄 불능이 다 여기) → `logs --previous`(죽기 직전 로그) → 그 다음 앱 내부
**왜**: K8s 계층 문제는 K8s가 기록한다 — Events에 답이 있는 사고를 앱 로그에서 며칠 찾는 게 표준 헛수고. `--previous` 없이 현재 로그만 보면 "재시작 후 멀쩡한 로그"만 보게 된다.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| requests | 실측 p95 사용량 기준 — 모르면 보수적으로 시작 후 VPA/메트릭으로 조정 | 안티패턴 1 |
| memory limit | requests의 1.5~2배 시작점 (스파이크 특성 따라) | OOMKill vs 과잉예약 균형 |
| CPU limit | 기본 미설정 — 멀티테넌트 격리 요구 시만 | 스로틀링 부작용 |
| liveness | 외부 의존 검사 0개 — 자기 프로세스 응답만 | 안티패턴 2 |
| 무중단 서비스 | replicas ≥ 2 + PDB minAvailable 1+ | 안티패턴 4 |
| 버전 추종 | 지원선(최신 3개 마이너) 이탈 금지 — 분기 점검 | EOL 클러스터는 보안·호환 부채 |

## 워크플로우 (K8s 작업 1건)

1. **규모 정직 판정** — 서비스 수·팀 규모·무중단 요구를 보고 K8s/k3s/compose 중 택1을 근거와 함께. (홈서버 단일 호스트 ~14서비스면 compose 유지가 기본 답, 학습 목적이면 k3s.)
2. **작성** — 매니페스트는 서비스별 디렉토리(또는 helm/kustomize 기존 구조)에, 클러스터 수동 `kubectl edit` 금지(선언 소스가 진실). 기존 파일 덮어쓰기 대신 Edit.
3. **검증 (copy-paste)**:
   ```
   kubectl apply --dry-run=server -f manifests/
   kubectl get events --sort-by=.lastTimestamp -n <ns> | tail -20
   kubectl describe pod <pod> -n <ns>        # Events 섹션 1순위
   kubectl logs <pod> --previous -n <ns>     # 직전 사망 로그
   ```
4. **출고 전** — requests/limits·probe 3종·PDB·이미지 태그 4항목 grep 점검.

## 출력 템플릿

```
## [서비스] K8s 구성
### 규모 판정: <K8s가 맞는 이유 1줄 (또는 compose 권고)>
### 리소스: <requests/limits + 근거>
### probe: <liveness/readiness/startup 각각 무엇을 검사>
### 중단 내성: <replicas/PDB/affinity>
### 검증: $ dry-run → <결과> / events → <특이사항>
### 확인 필요
```

### 작성 예시

```
## API 서버 배포 (가정)
### 규모 판정: 관리형 클러스터 기보유 + 무중단 요구 → K8s 적합
### 리소스: requests cpu 200m/mem 256Mi (스테이징 p95 실측), limit mem 512Mi, cpu limit 없음
### probe: liveness=/healthz(자기 응답만) / readiness=/ready(DB ping 포함) / startup 30s 유예
### 중단 내성: replicas 2 + PDB minAvailable 1 + hostname anti-affinity
### 검증: $ dry-run=server → 통과 / drain 리허설 중 무중단 확인
### 확인 필요: HPA 도입은 트래픽 패턴 1개월 관측 후
```

❌ "CrashLoop이네 → 앱 로그 3시간 정주행" (Events 안 봄)
✅ "describe pod → Events에 OOMKilled → limit 256Mi가 실사용 400Mi보다 작았음 — 5분 진단"

### 사용자가 권고를 거부하면

- "홈서버에 풀 K8s 올리고 싶다(학습)" → 학습 목적은 정당한 근거 — k3s 권장으로 절충, 운영 서비스는 compose 병행 1줄 기록.
- "replica 1로 충분하다" → 내부 도구·중단 허용 서비스면 동의가 맞다 — drain 시 다운 1줄만 기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.
- **처방이 환경상 불가할 때**(관리형 정책으로 PDB/affinity 제약·실측 메트릭 부재): 거부가 아니라 제약 — 보수적 기본값으로 partial 진행하고 "requests 실측 전 잠정치 — 메트릭 확보 후 조정"을 산출물에 1줄. liveness의 외부 의존 검사·평문 시크릿 Git 커밋처럼 **장애 증폭·영구 유출을 부르는 항목은 거부 대상 아님**(위험 명시 후 readiness 이전·시크릿 매니저 최소안 제시).

### 판단 불가 시 — `[확인 필요]` 4요소

리소스 실측치·버전별 폐기 API·관리형 클러스터 고유 동작은 추측 금지, 4요소로:
- **누가**: 사용자(클러스터 버전·관리형 종류 EKS/GKE/k3s·SLA 요구) 또는 공식 문서(kubernetes.io 버전 changelog)
- **언제**: requests/limits 수치를 확정하기 전 / 클러스터 업그레이드 전(폐기 API 대조)
- **어떻게**: `kubectl top pod`·메트릭으로 p95 실측, 폐기 API는 `pluto`·`kubectl get --raw /metrics | grep deprecated`
- **기대값**: "p95 메모리 400Mi → limit 512Mi" 같은 실측 기반 단정 — 못 얻으면 `[확인 필요: <항목> — 출처]`로 남기고 보수적(여유 있는 requests + 메트릭 관측 후 조정) 진행

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — Reddit Pi-Day 장애: 클러스터 업그레이드의 복병 (2023-03-14, 공식 포스트모템)

Reddit이 K8s 1.23→1.24 업그레이드 중 314분 전면 장애 — 수년 전 설정된 노드 라벨 명칭이 K8s 버전 업에서 변경/폐기되며 Calico(네트워크) 라우트 리플렉터가 노드를 못 찾아 클러스터 네트워킹 붕괴. 복잡도를 더한 건 **롤백도 검증 안 된 경로**였다는 것(K8s 컨트롤플레인 다운그레이드는 공식 미지원). 교훈: ① K8s 업그레이드는 "마이너 하나"도 폐기 API·라벨 체인지로그 전수 대조 후(체크: `kubectl get --raw /metrics | grep deprecated` 류·pluto 등 도구) ② 업그레이드 리허설은 스테이징 클러스터에서 — 프로덕션이 첫 시도면 그게 리허설이다 ③ 버전 추종을 미루면 한 번에 건너야 할 간극이 커져 더 위험해진다(분기 점검의 근거). 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — Reddit Pi-Day · Monzo liveness 연쇄 · OOMKill 진단 (코어스펙 1겹)

## 한계

- **K8s가 답이 아닌 규모가 많다** — 단일 호스트·소수 서비스·1인 운영이면 compose+systemd가 운영 부채 총량에서 우위. 이 판정을 건너뛰고 매니페스트부터 쓰지 않는다.
- 서비스메시·오퍼레이터 개발·멀티클러스터는 코어 범위 밖 — 공식 문서 우선.
- 관리형(EKS/GKE) 고유 기능·요금은 부패 빠름 — 사용 직전 해당 클라우드 문서 확인(→ dev-cloud-aws).
