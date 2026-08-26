# evidence + 출고 전 체크리스트

## 실증·출처

- **terraform destroy/replace 데이터 손실** — 다수 기업의 공개 회고(plan 미독으로 DB·디스크 replace). SKILL.md 실전 케이스. plan 읽기·prevent_destroy의 근거.
- **Terraform S3 backend 공식 문서** (`developer.hashicorp.com/terraform/language/backend/s3`) — 원격 state·잠금·암호화의 1차 출처. **2026 기준 확인**: `use_lockfile=true`로 S3 네이티브 잠금 지원(Terraform 1.11.0, 2025-02-27 GA), `dynamodb_table`은 deprecated(향후 minor에서 제거 예정). `encrypt`/`kms_key_id`/`sse_customer_key`로 state·lock 암호화. 안티패턴 3의 1차 근거.
- **Terraform 공식 문서 — lifecycle(`prevent_destroy`)·import** (`developer.hashicorp.com/terraform/language`) — 상태 리소스 보호·점진 코드화의 1차 출처. 안티패턴 6·워크플로우 import 근거.
- **Ansible `command` 모듈 공식 문서** (`docs.ansible.com/ansible/latest/collections/ansible/builtin/command_module.html`) — **2026 확인**: `creates`/`removes`/`chdir` 지원, check mode는 `creates`/`removes`를 줄 때만 동작(없으면 task skip — partial). 공식 문서가 "shell은 메타문자 파싱으로 의도치 않은 명령 실행 위험, 가능하면 command가 더 안전" 명시 → command 권장. 안티패턴 2(생 셸 guard)의 1차 근거.
- **Ansible Vault 공식 문서** (`docs.ansible.com/.../vault_guide`) — 민감 변수 암호화. 안티패턴 4의 근거.
- **"SnowflakeServer" (Fowler, `martinfowler.com/bliki/SnowflakeServer.html`)** — 손 구성 서버의 재현 불가 문제. 짝 개념 "PhoenixServer"(`martinfowler.com/bliki/PhoenixServer.html`)는 재현 가능 인프라. 안티패턴 1의 원전(dev-linux-ops #7과 공유).
- **12-Factor / Pets vs Cattle** — 인프라를 코드로·재현 가능하게의 철학적 배경.
- 오픈소스 차용 표기: IaC 가이드 다수(색인 인지, 본문 비복사). **역흡수**: 드리프트 정기 감지·손 수정 즉시 역반영·상태 리소스 보호(prevent_destroy+백업)·Terraform/Ansible 선택 기준·plan 미독 위험 검출 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (IaC 출고 시)

- [ ] 모든 변경이 코드 경유 (드리프트 감지 켜짐)
- [ ] 프로비저닝 멱등 (생 command/shell에 guard) — `iac_lint.py` 0건
- [ ] state 원격 + 잠금 + 백업 + 암호화 (Terraform S3는 `use_lockfile=true` + `encrypt=true`; DynamoDB 잠금은 신규 지양)
- [ ] 시크릿 코드·state 평문 0 (매니저/Vault 참조)
- [ ] plan/--check 리뷰 후 apply (auto-approve는 CI 검증 경로만)
- [ ] destroy/replace 대상 확인 — 상태 리소스 prevent_destroy + 백업
- [ ] 모듈/role로 구조화 (과분할 주의)
- [ ] 드리프트 정기 감지 + 발견 시 알림

## 점검 주기 (부패 중간 — 반기)

- 드리프트 감지가 실제 도는지 + 누적 드리프트 정리
- Terraform/Ansible 메이저·프로바이더 변경 확인 (특히 S3 backend `dynamodb_table` 실제 제거 시점 추적 — 1.11부터 deprecated)
- ledger의 IaC 사고(destroy·state) 3회 패턴 → 체크리스트 보강
