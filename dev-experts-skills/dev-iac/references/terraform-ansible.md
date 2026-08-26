# Terraform vs Ansible·패턴·드리프트·import (SKILL.md 비중복)

## Terraform vs Ansible (선택)

| | Terraform | Ansible |
|---|---|---|
| 모델 | 선언형 + state(원하는 상태 추적) | 절차형(멱등 모듈)·state리스 |
| 강점 | 클라우드 리소스 프로비저닝(생성·삭제) | 서버 구성·설정·앱 배포 |
| state | 있음(신성·백업·잠금) | 없음(매 실행이 현재 상태 수렴) |
| 멱등 | 본질적(plan→apply) | 모듈이 멱등(command/shell은 직접 보장) |
| 홈서버(물리) | 제한적(물리 서버 생성 불가) | ◎ 적합 |
| 클라우드 | ◎ 적합 | 프로비저닝보다 구성에 |

조합이 흔하다: **Terraform으로 인프라 생성 → Ansible로 구성**. 홈서버(물리)는 Ansible 중심, 클라우드 리소스 생기면 Terraform.

## Terraform 패턴

```hcl
terraform {
  backend "s3" {                    # 원격 state + 잠금 + 암호화 — 안티패턴 3
    bucket = "tfstate"; key = "prod/terraform.tfstate"
    encrypt = true                  # state·lock 파일 서버측 암호화(평문 방지)
    use_lockfile = true             # S3 네이티브 잠금(TF 1.11+ GA·권장) — .tflock 객체로 동시 apply 차단
    # dynamodb_table = "tf-lock"    # 구방식: TF 1.11부터 deprecated(향후 제거). 신규는 use_lockfile만
  }
}
resource "db" "main" {
  lifecycle { prevent_destroy = true }   # 데이터 리소스 보호 — 안티패턴 6
}
```

- 변수·시크릿: `variable` + TF_VAR 환경변수 또는 시크릿 매니저 data source(코드에 평문 0).
- 모듈: 재사용 단위(`module "network"`) — 관심사 분리(안티패턴 5), 단 과분할 주의.
- `terraform plan -out=plan.tfplan` → 리뷰 → `apply plan.tfplan`(plan과 apply 사이 변경 방지).
- import: 기존 손 구성 리소스를 `terraform import`로 state에 편입(점진 코드화).

## Ansible 패턴

```yaml
- name: ensure nginx                 # 멱등 모듈 — 안티패턴 2
  ansible.builtin.apt: { name: nginx, state: present }
- name: config from template
  ansible.builtin.template: { src: nginx.conf.j2, dest: /etc/nginx/nginx.conf }
  notify: reload nginx               # handler — 변경 시에만 reload
- name: legacy script (guarded)
  ansible.builtin.shell: ./migrate.sh
  args: { creates: /opt/.migrated }  # 멱등화: 이미 있으면 skip
```

- role로 구조화(role = 재사용 구성 단위). inventory로 호스트 그룹.
- 시크릿: Ansible Vault(`ansible-vault encrypt`)로 민감 변수 암호화 + 외부 시크릿 매니저(Infisical) lookup.
- `--check`(dry run) + `--diff`로 적용 전 변경 미리보기 — Terraform plan의 등가물.
- handler: 변경됐을 때만 실행(매번 reload 방지) — 멱등의 일부.

## 드리프트 감지 (코드 = 실제 보장)

```
정기 실행 (CI/cron — dev-cicd/dev-linux-ops):
  terraform plan        -> "변경 없음"이 정상, 변경 있으면 손 수정 발생(드리프트)
  ansible-playbook --check -> changed=0이 정상
발견 시: 코드 역반영(손 수정을 코드로) 또는 재적용(코드로 덮기) — dev-linux-ops #7
```

드리프트는 IaC의 가치를 갉는다 — 정기 감지가 면역 체계. 발견을 알림(dev-monitoring)으로.

## 점진 코드화 (기존 손 구성에서)

1. 재구축 빈도·중요도 높은 것부터(전부 한 번에 금지 — dev-refactoring 빅뱅 회피).
2. Terraform import 또는 Ansible로 현 상태를 코드로 기술 → `plan`/`--check`로 "변경 없음"(코드가 현실과 일치) 확인.
3. 이후 모든 변경은 코드 경유 + 드리프트 감지 켜기.
4. 상태 보유(DB·볼륨)는 코드화하되 prevent_destroy + 백업(dev-backup-dr) — 코드가 데이터를 안 날리게.
