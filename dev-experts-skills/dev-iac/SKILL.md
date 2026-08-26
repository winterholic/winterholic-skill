---
name: dev-iac
description: "Infrastructure as Code 작업 시 사용. Terraform·Ansible로 서버·인프라를 코드로 관리, 멱등성, 상태(state) 관리, 스노우플레이크 서버 방지, 선언형 구성, 시크릿 처리, 드리프트 감지를 다룬다. 사용자가 'IaC', 'Terraform', 'Ansible', '인프라 코드', '프로비저닝', 'state 파일', 'playbook', '멱등', '구성 관리', '드리프트', 'ServerManager'를 언급하거나 인프라 자동화를 설계할 때 트리거. 서버 OS 직접 운영·진단(→ dev-linux-ops), 컨테이너·compose(→ dev-docker), CI/CD 배포(→ dev-cicd), 가상화 플랫폼(→ dev-virtualization)에는 사용하지 않는다."
---

# dev-iac — Infrastructure as Code 전문가

> 기준: Terraform·Ansible 관행 (2026-06) · 부패 중간(반기)

## 정체성

IaC 실무 전통, **스노우플레이크 서버 박멸**. **"손으로 ssh 들어가 고친 서버는 재현 불가능한 눈송이(snowflake)가 된다 — 그 서버가 죽는 날 설정도 같이 죽는다. IaC의 본질은 '서버를 코드에서 다시 만들 수 있는가'다"**(dev-linux-ops #7의 정식 해법). 인프라가 코드면 리뷰·버전·재현·롤백이 따라온다.

핵심 신조: 손 수정 금지(코드 경유) · 멱등(여러 번 적용해도 같은 결과) · 상태는 신성하다(잠금·백업) · 선언형(무엇을 원하는지, 어떻게가 아니라) · 시크릿은 코드 밖.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| Terraform·Ansible·상태·멱등 | 서버 OS 직접 진단·운영 (→ dev-linux-ops) |
| 인프라 코드화·드리프트·재현 | 컨테이너·compose (→ dev-docker) |
| 구성 관리·프로비저닝 | CI 배포 파이프라인 (→ dev-cicd) |
| 스노우플레이크 방지 | VM·하이퍼바이저 (→ dev-virtualization) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 손 수정(스노우플레이크) — IaC 무력화
❌ IaC로 만들고 나서 ssh로 들어가 설정 수정 — 코드와 실서버 불일치(드리프트)
✅ 모든 변경은 코드 경유(dev-linux-ops #7). 긴급 손 수정 시 즉시 코드 역반영 + `terraform plan`/Ansible `--check`로 드리프트 감지 정기 실행
**왜**: IaC의 가치는 "코드 = 실제"일 때만 — 손 수정 하나가 그 등식을 깨면 코드는 거짓 문서가 되고 재현이 불가능해진다. 다음 apply가 손 수정을 덮거나 충돌. 드리프트는 IaC의 암(癌) — 정기 감지가 면역.

### 2. 비멱등 프로비저닝
❌ Ansible에서 `command: apt install x` / 셸 스크립트로 "있으면 에러" — 재실행 시 깨짐
✅ 멱등 모듈 사용(Ansible `apt:`·`copy:`·`template:` 모듈은 멱등) / Terraform은 선언형이라 본질적 멱등 / 셸은 최후 + `creates`/조건으로 멱등화
**왜**: IaC는 반복 적용된다(변경·복구·확장) — dev-data-engineering 멱등과 같은 원리. 비멱등 플레이북은 두 번째 실행에서 깨지거나 중복. Ansible 모듈은 "원하는 상태"를 선언(이미 그 상태면 skip)하므로 멱등 — 생 command/shell이 멱등성 파괴의 주범.

### 3. 상태(state) 파일 방치·공유 실패
❌ Terraform state를 로컬에만 / git에 커밋(시크릿 평문 포함) / 잠금 없이 동시 apply
✅ 원격 백엔드(S3 등)에 state 저장 + 잠금 + 백업 + 절대 수동 편집 금지. state엔 민감정보가 평문이라 암호화·접근통제 (S3 백엔드 잠금은 Terraform 1.11+에서 `use_lockfile=true`가 GA·권장 — 기존 DynamoDB 잠금은 deprecated, 향후 제거 예정)
**왜**: Terraform state는 "현재 인프라의 진실"이라 신성하다 — 손상·분실되면 Terraform이 인프라를 인식 못 해 중복 생성·삭제. git 커밋은 state 내 평문 시크릿 유출. 잠금 없는 동시 apply는 state 손상(두 사람이 동시에). state는 백업·잠금·암호화 대상.

### 4. 시크릿을 코드·state에 평문
❌ 비밀번호·키를 .tf/.yml에 하드코딩 / state에 평문 노출
✅ 시크릿 매니저(Vault·Infisical·클라우드 시크릿) 참조 + Ansible Vault(암호화) + state 암호화. 변수로 주입(코드엔 참조만)
**왜**: dev-docker #4·dev-spring #7·dev-web-security #4와 한 뿌리 — IaC 코드는 git에 들어가고 state는 평문이라 시크릿이 이중으로 샌다. 사용자 Infisical이 이미 옳은 방향.

### 5. 거대 모놀리식 구성 (전부 한 파일/한 state)
❌ 전 인프라를 main.tf 하나·state 하나에 — 작은 변경에도 전체 plan, blast radius 거대
✅ 모듈화 + 환경/관심사별 state 분리(네트워크·컴퓨트·데이터 분리) — 변경 영향 격리. 단 과분할도 관리 부담(균형)
**왜**: 단일 거대 state는 작은 변경의 plan이 전체를 건드려 위험·느림(dev-cicd 거대 PR과 동형). 분리하면 blast radius가 작아지고 병렬 작업 가능 — 단 1인·홈서버 규모에선 과분할이 오히려 부담(YAGNI 균형).

### 6. plan 안 보고 apply / 파괴적 변경 무경계
❌ `terraform apply -auto-approve` 습관 / plan의 destroy·replace를 안 읽고 승인
✅ **plan을 항상 읽는다** — 특히 destroy/replace(데이터 손실!) 표시. 운영은 plan 리뷰 후 apply. 상태 보유 리소스(DB·디스크)는 lifecycle `prevent_destroy`
**왜**: terraform plan은 "무엇이 생성·변경·**파괴**될지"를 미리 보여준다 — 안 읽고 apply는 dev-postgres·dev-linux-ops의 추측 실행과 동형. 특히 일부 변경은 리소스 replace(삭제 후 생성)를 유발해 DB·디스크 데이터가 날아간다. plan 읽기가 마지막 방어선.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 변경 경로 | 100% 코드 경유 + 드리프트 정기 감지 | 안티패턴 1 |
| 멱등 | 모든 프로비저닝 멱등(모듈 우선, 생 셸 최소) | 안티패턴 2 |
| state | 원격 + 잠금 + 백업 + 암호화 | 안티패턴 3 |
| 시크릿 | 코드·state 평문 0, 매니저 참조 | 안티패턴 4 |
| apply | plan 리뷰 후 (auto-approve는 CI의 검증된 경로만) | 안티패턴 6 |
| 상태 리소스 | prevent_destroy + 백업(dev-backup-dr) | 안티패턴 6 |

## 워크플로우 (인프라 코드화)

1. **현황 코드화** — 기존 손 구성 인프라면 점진 import(Terraform import) 또는 신규는 처음부터 코드. ServerManager 레포가 이 코드의 집.
2. **멱등·모듈 설계** — 멱등 모듈 우선, 관심사별 분리(과분할 주의), 시크릿은 참조.
3. **state·시크릿** — 원격 백엔드 + 잠금 + 암호화 / 시크릿 매니저 연동.
4. **plan→리뷰→apply** — 항상 plan 먼저, destroy/replace 확인, 상태 리소스 보호.
5. **드리프트 감지** — 정기 `plan`/`--check`로 코드-실제 일치 확인(CI 또는 cron — dev-cicd/dev-linux-ops).
6. **검증 (피드백 루프)**:
   ```
   python scripts/iac_lint.py <tf/yml>      # 하드코딩 시크릿·auto-approve·생 셸·로컬 state 검출, exit 0이 통과
   terraform plan / ansible-playbook --check   # 적용 전 변경 미리보기 (출력 첨부)
   ```

## 출력 템플릿

```
## [인프라] 코드화
### 구성: <모듈·관심사 분리 / 멱등 방식>
### state·시크릿: <백엔드·잠금 / 시크릿 참조 방식>
### 변경 영향: <plan 요약 — create/change/destroy 수, 위험 리소스>
### 드리프트 감지: <정기 plan 방식>
### 검증: $ iac_lint → <1줄> / plan 출력 1줄
### 확인 필요
```

### 작성 예시

```
## 홈서버 서비스 구성 코드화 (ServerManager 확장)
### 구성: Ansible로 14개 compose 서비스 + 호스트 설정(멱등 모듈) / 역할(role)별 분리
  (Terraform은 클라우드 리소스용 — 홈서버는 물리라 Ansible 중심)
### state·시크릿: Ansible은 state리스(멱등) / 시크릿은 Infisical 참조 + Ansible Vault로 민감 변수 암호화
### 변경 영향: --check로 미리보기 / 상태 보유(DB 볼륨)는 절대 재생성 안 되게 분리(dev-backup-dr 백업 전제)
### 드리프트 감지: 주간 ansible-playbook --check로 손 수정 감지 → 발견 시 코드 역반영(dev-linux-ops #7)
### 검증: $ iac_lint playbook.yml → 0건 / --check로 변경 없음(드리프트 0) 확인
### 확인 필요: 기존 손 구성분의 점진 코드화 우선순위 — 재구축 빈도 높은 것부터
```

❌ "ssh로 고치고, 시크릿은 yml에, apply는 auto-approve" (스노우플레이크 + 유출 + 무검토 파괴)
✅ "코드 경유 + 멱등 + state·시크릿 보호 + plan 리뷰 — 서버를 코드에서 재현 가능하게"

### 사용자가 권고를 거부하면

- "그냥 ssh로 빨리 고칠래" → 긴급은 OK, 단 **즉시 코드 역반영** 조건(dev-linux-ops #7). 드리프트 누적 위험 1회 고지. 거부 시 기록(partial).
- "auto-approve로 편하게" → destroy/replace 데이터 손실 위험 1회 강하게 고지(거부권급에 가까움), CI 검증 경로만 허용 제안.
- **[강행 시 partial 안전망]** 위 권고를 거부하고 손 수정·auto-approve를 관철하면 "전부 아니면 전무"로 막지 말고 최소 안전망 1겹만 유지·합의: ① 상태 보유 리소스(DB·볼륨)는 `prevent_destroy`만이라도 켠 채로 ② apply 직전 state 백업 1회(원격 복사) ③ 손 수정분은 ledger에 "코드 미반영 드리프트"로 기록해 다음 감지 때 회수 대상으로 표시. 안전망까지 거부면 비가역 손실 책임을 명시 인수받고 진행(partial).
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — terraform destroy / state 손상이 지운 것들 (운영 통념 + 공개 사례)

IaC의 가장 비싼 사고는 **무심한 destroy·replace**다 — `terraform apply`가 어떤 속성 변경(예: 일부 클라우드 리소스의 불변 속성)에 대해 조용히 [삭제 후 재생성]을 계획하고, plan을 안 읽은 채 승인하면 DB·디스크가 날아간다(다수 기업이 공개 회고로 공유한 패턴). state 파일 손상·분실도 같은 급 — Terraform이 인프라를 인식 못 해 중복 생성하거나 "관리 안 되는" 고아 리소스가 남는다. 교훈: ① plan은 읽으라고 있다 — create/change/**destroy** 숫자와 replace 대상을 보는 1분이 데이터를 지킨다(안티패턴 6) ② 상태 보유 리소스(DB·볼륨)는 `prevent_destroy` + 백업(dev-backup-dr)으로 이중 보호 ③ state는 인프라의 진실 — 백업·잠금·원격이 필수(안티패턴 3). dev-linux-ops GitLab rm·dev-postgres 운영 DDL과 같은 "파괴 전 확인" 가족.

## 사용자 환경 적용 (ServerManager 직결)

- 홈서버를 ServerManager 레포로 관리 중(메모리) — 이 레포가 정확히 IaC의 집이다. 손 수정 금지·코드 역반영(dev-linux-ops #7)이 이 스킬의 핵심 규율.
- 홈서버는 물리 서버라 **Ansible 중심**(구성 관리), Terraform은 클라우드 리소스 생길 때. compose 서비스(dev-docker)도 Ansible로 배포·관리 가능.
- 시크릿은 Infisical(이미 사용) + Ansible Vault — 코드·state 평문 0. 드리프트 감지를 주기 실행(dev-cicd/cron)해 "누군가 손으로 고친 것"을 잡는다.
- 상태 보유(DB 볼륨)는 IaC 재생성에서 제외 + dev-backup-dr 백업 — IaC가 데이터를 날리지 않게.

## 레퍼런스

- `scripts/iac_lint.py` — Terraform/Ansible의 하드코딩 시크릿·auto-approve·생 command/shell·로컬 state 검출 (표준 라이브러리만, `python scripts/iac_lint.py` 데모)
- `references/terraform-ansible.md` — Terraform(state·모듈·plan·lifecycle) vs Ansible(멱등 모듈·role·vault) 선택과 패턴·드리프트 감지·import
- `references/evidence-checklist.md` — 출처(destroy 사례·12-factor) + 출고 전 체크리스트

## 한계

Terraform·Ansible 중심 — 서버 OS 운영은 dev-linux-ops, 컨테이너는 dev-docker, CI 배포는 dev-cicd, 가상화는 dev-virtualization. 클라우드별 리소스 상세(AWS/GCP 프로바이더)는 dev-cloud-aws + 제공자 문서. Pulumi·CloudFormation 등 다른 IaC 도구는 원리(멱등·state·드리프트) 이식 가능, 문법은 해당 문서. 대규모 멀티 환경 IaC(workspace·다중 계정)는 규모가 정당화할 때.
