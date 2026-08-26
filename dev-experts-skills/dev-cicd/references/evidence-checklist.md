# evidence + 출고 전 체크리스트

## 실증·출처

- **tj-actions/changed-files 공급망 공격 (2025-03, CVE-2025-30066)**: 공개 보안 권고(GitHub Advisory GHSA-mrrh-fwg8-r2c3·NVD·CISA Alert 2025-03-18) — 가변 태그 전 버전(~45.0.7) 악성 재지정으로 러너 메모리 스캔→CI 시크릿을 로그에 덤프, 23,000+ 레포 영향. StepSecurity가 2025-03-14 최초 보고, `v46.0.1`에서 패치. **SHA 핀(불변 참조)을 쓴 레포만 무사** — SHA 핀 표준화의 직접 계기. SKILL.md 실전 케이스 원 출처.
- **pull_request vs pull_request_target**: GitHub 공식 문서 "Events that trigger workflows" + GitHub Security Lab "Preventing pwn requests" — fork PR 시크릿 미제공이 보호 장치이고 pull_request_target+checkout이 그걸 우회하는 구조임을 명시.
  - 보강(2026-06 확인): `actions/checkout@v7.0.0`(2026-06-18 릴리스, CHANGELOG·릴리스 노트)은 `pull_request_target`·`workflow_run`에서 fork PR 헤드의 체크아웃을 기본 차단한다 — 검출기 C2의 안티패턴을 액션 자체가 막아주는 방향. 단 안전장치는 보조일 뿐, "메타데이터만 작업" 원칙은 그대로 유지.
- **기본 잡 타임아웃 360분**: GitHub 공식 문서 "Usage limits" — timeout-minutes 명시 규칙의 근거.
- **"빠른 피드백" 10분**: 지속 통합 고전(Fowler "Continuous Integration" — 10분 빌드 절) — 느린 CI가 무시되는 심리의 표준 출처.
- 오픈소스 차용 표기: openai/gh-fix-ci(VoltAgent 색인 — CI 실패 디버깅 절차 참고), alirezarezvani ci-cd-pipeline-builder(골격 생성 접근 참고, 본문 비복사). **역흡수**: 두 소스 모두 공급망 핀 정책·롤백 절차·pull_request_target 함정 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (워크플로우 추가·수정 시)

- [ ] 검증 로직이 스크립트로 분리 — 로컬에서 같은 명령 실행 가능
- [ ] 서드파티 액션 전부 SHA 핀 (`workflow_check.py` 0건)
- [ ] 모든 잡에 timeout-minutes
- [ ] 캐시 키에 hashFiles(명세 파일)
- [ ] concurrency로 중복 실행 취소
- [ ] 시크릿이 쓰는 스텝 env로만 — 워크플로우 전역 env에 없음
- [ ] pull_request_target 사용 시 PR 코드 체크아웃 없음
- [ ] paths 필터로 문서 변경에 무거운 잡 안 돎
- [ ] 배포 잡: 식별자 태그·헬스체크 게이트·롤백 1명령 문서화
- [ ] 비호환 마이그레이션 낀 배포는 2단계로 쪼갬
- [ ] gh run watch로 실제 1회 통과 확인

## 점검 주기 (부패 중간 — 반기)

- 액션 메이저 버전(checkout·setup-python 등) vs 핀 — Dependabot PR diff를 사람이 확인 후 머지
- 게이트 잡 실행 시간 추이 — 10분 초과 시 분리·캐시 재설계
- self-hosted runner 사용 시 러너 버전·호스트 보안 패치
