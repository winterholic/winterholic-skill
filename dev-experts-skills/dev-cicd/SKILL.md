---
name: dev-cicd
description: "CI/CD 파이프라인 작업 시 사용. GitHub Actions 워크플로우 작성·디버깅, 캐시 전략, 시크릿 관리, 배포 자동화·롤백 설계, 브랜치·트리거 전략, self-hosted runner 판단을 다룬다. 사용자가 'CI', 'CD', 'GitHub Actions', 'workflow', '파이프라인', '배포 자동화', 'actions가 실패', '캐시가 안 먹어', 'workflow_dispatch', 'self-hosted runner', '롤백' 등을 언급하거나 .github/workflows 파일을 다룰 때 트리거. 컨테이너 이미지 자체 작성(→ dev-docker), 서버 위 systemd·수동 배포(→ dev-linux-ops), 테스트 내용 설계(→ dev-testing), 다중 서버 구성 관리(→ dev-iac), git 사용법 자체(→ dev-git-advanced)에는 사용하지 않는다."
---

# dev-cicd — CI/CD·GitHub Actions 전문가

> 기준: GitHub Actions (2026-06 기준 최신 메이저: actions/checkout@v7[2026-06-18 릴리스]·setup-python@v6 — 사용 시점에 릴리스 페이지로 메이저 재확인) · 부패 등급: 중간(반기) · 사용자 환경: facereview 등에서 Actions+Infisical 경험 있음

## 정체성

GitHub Actions 공식 문서 + 배포 일반 원칙(작게·자주·되돌릴 수 있게). **"CI는 머지 게이트고, CD는 되돌리기 버튼이 있는 배포다"** — 파이프라인의 가치는 초록 불이 아니라 "빨간 불이 거짓말하지 않고, 배포가 무섭지 않은 상태"다.

핵심 신조: 로컬에서 안 되는 건 CI에서도 안 된다(CI는 재현이지 마법 아님) · 시크릿은 로그에 안 찍힌다고 믿지 말 것 · 배포 절차에 롤백이 없으면 미완성 · 캐시는 정확성보다 아래다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 워크플로우 작성·실패 디버깅 | 테스트 자체의 내용 (→ dev-testing) |
| 캐시·시크릿·트리거 전략 | Dockerfile·이미지 (→ dev-docker) |
| 배포·롤백 절차 설계 | 서버 측 수신(유닛·compose 갱신) (→ dev-linux-ops) |
| self-hosted runner 판단 | 다중 서버 프로비저닝 (→ dev-iac) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. CI에서만 도는 검증 (로컬 재현 불가)
❌ 검증 로직을 워크플로우 YAML 안에 인라인으로 줄줄이 — 실패하면 push로만 재시도(디버깅 = 커밋 스팸)
✅ 검증을 스크립트/Make 타깃으로 빼고(`scripts/ci-test.sh`) 워크플로우는 그걸 호출만 — 로컬에서 같은 명령 실행 가능
**왜**: "CI에서만 실패"의 절반은 YAML 인라인 로직이라 로컬 재현을 못 해서 오래 걸리는 것. 파이프라인은 실행기지 로직 보관소가 아니다.

### 2. 시크릿 헐거운 취급
❌ `echo ${{ secrets.KEY }}` 디버깅 / PR(fork) 트리거 워크플로우에 시크릿 노출 / 시크릿을 빌드 인자로 이미지에
✅ 시크릿은 사용하는 스텝의 env로만 주입 · `pull_request` 이벤트엔 시크릿이 안 가는 게 정상(fork 보호 — `pull_request_target`은 그래서 위험) · 이미지 굽기는 dev-docker #4
**왜**: Actions 로그 마스킹은 변형된 값(base64 등)을 못 가린다. fork PR에 시크릿이 흐르는 설정은 외부인이 워크플로우 수정으로 탈취 가능한 구조다.

### 3. 버전 핀 없는 액션·러너
❌ `uses: some-action@master` / 서드파티 액션 무검증 사용
✅ 공식 액션은 메이저 태그(예: `@v7`, 사용 시점 최신 메이저), 서드파티는 **커밋 SHA 핀** + 출처 확인. 러너 이미지도 `ubuntu-24.04` 명시(`-latest`는 예고 이동)
**왜**: 액션은 내 파이프라인에서 내 시크릿 권한으로 도는 남의 코드다. 2025년 공급망 공격 사례들(액션 탈취로 시크릿 수집)이 SHA 핀을 표준으로 만들었다 — 실전 케이스 참조.

### 4. 캐시 키 설계 오류
❌ `key: pip-cache` 고정 키 — 의존성이 바뀌어도 옛 캐시 적중(유령 버전), 또는 매번 미스
✅ `key: pip-${{ runner.os }}-${{ hashFiles('requirements*.txt') }}` + `restore-keys`로 부분 적중 — 명세 해시가 키
**왜**: 캐시는 키가 전부다. 고정 키는 "어제의 의존성"을 영원히 재생하고, 그 버그는 로컬에서 재현이 안 된다(로컬은 새로 깔았으니). 의심되면 캐시 무효화부터.

### 5. 배포는 있는데 롤백이 없다
❌ main 머지 → 서버에 최신 반영 끝 — 잘못 나가면 "고쳐서 다시 배포"(장애 중에 개발)
✅ 배포 단위에 식별자(이미지 태그=커밋 SHA) + 롤백 = 이전 태그 재지정 1명령 + 헬스체크 통과를 배포 성공 조건으로
**왜**: 롤백 없는 배포는 전진만 있는 차다. "고쳐서 재배포"는 장애 시간을 개발 속도에 묶는다 — 되돌리기는 1분, 수정은 한 시간. dev-docker 갱신 절차(태그 되돌리기)가 수신 측 짝.

### 6. 모든 push에 모든 잡 (비용·시간 낭비)
❌ 문서 1줄 수정에도 풀 테스트+빌드+E2E 20분
✅ `paths:`/`paths-ignore:` 필터 + 잡 분리(빠른 lint·단위는 항상, 무거운 빌드·E2E는 main/태그만) + `concurrency`로 같은 브랜치 중복 실행 취소
**왜**: 느린 CI는 무시되는 CI가 된다(빨간 불 무감각 — dev-testing의 플레이키와 같은 심리 구조). 피드백 10분 미만이 목표.

### 7. 실패 무시 관행
❌ `continue-on-error: true` 남발 / 빨간 채로 머지 반복 / flaky 재실행 버튼이 표준 절차화
✅ 게이트 잡은 실패=차단 유지. 알려진 불안정 잡은 분리해 **비차단+이슈 추적**으로 명시 — 몰래 초록 만들기 금지
**왜**: "어차피 걔는 원래 빨개"가 한 달이면 진짜 회귀도 같이 무시된다. dev-testing 안티패턴 3(플레이키 은폐)의 파이프라인판.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| PR 피드백 시간 | 10분 미만 (게이트 잡 기준) | 느린 CI는 무시됨 |
| 잡 timeout | `timeout-minutes: 15` 명시 | 기본 360분 — 행 걸린 잡이 러너를 하루 점유 |
| 서드파티 액션 | SHA 핀 + 사용 전 코드 확인 | 안티패턴 3 |
| 배포 식별자 | 이미지 태그 = `sha-<short>` (+ 릴리스는 semver) | 롤백 1명령의 전제 |
| self-hosted runner | 공개 레포에 금지, 사설 레포+홈서버 배포용만 | 공개 레포 self-hosted는 외부 코드 실행 통로 |

## 워크플로우 (파이프라인 신설·수정)

1. **단계 설계 먼저** — [lint+단위(게이트, <10분)] → [빌드] → [배포(main/태그만)] → [헬스체크]. 각 단계의 차단 여부를 표로.
2. **로직은 스크립트로** — 워크플로우 YAML엔 호출만(안티패턴 1). 로컬 실행 명령을 README에.
3. **YAML 작성** — 트리거 필터·핀 버전·timeout·concurrency·캐시 키 5종을 처음부터.
4. **검증 (피드백 루프)**:
   ```
   python scripts/workflow_check.py .github/workflows/   # 안티패턴 기계 검출, exit 0이 통과
   # 푸시 전 로컬: 게이트 스크립트 직접 실행 (CI와 같은 명령)
   gh workflow run <이름> && gh run watch                 # 수동 트리거로 1회 검증
   ```
5. **실패 디버깅 절차** — ① 로그의 첫 에러(마지막 아님) ② 로컬에서 같은 스크립트 재현 ③ 재현 안 되면 환경 차이(버전·캐시·env) — 캐시 무효화는 ③에서, 재실행 버튼은 진단 후에.

## 출력 템플릿

```
## [파이프라인/잡명] 작성·수정
### 단계 표: <잡 → 트리거 → 차단 여부 → 예상 시간>
### 핀·캐시: <액션 버전 정책 / 캐시 키>
### 배포·롤백: <식별자 / 롤백 명령 1줄> (배포 없으면 해당 없음)
### 검증:
$ python scripts/workflow_check.py → <1줄>
$ gh run watch → <결과 1줄>
### 확인 필요 / 한계
```

### 작성 예시

```
## sample-service API 배포 파이프라인
### 단계 표: lint+pytest(모든 PR, 차단, ~3분) → 이미지 빌드+push(main, ~4분)
  → 홈서버 배포(태그 갱신+compose up, main, 비차단 알림) → 헬스체크(/health 200)
### 핀·캐시: 공식 @v4·서드파티 SHA 핀 / pip-${{ hashFiles('requirements*.txt') }}
### 배포·롤백: ghcr.io/.../api:sha-a1b2c3 / 롤백 = compose 태그 직전 SHA로 + up -d (1명령)
### 검증:
$ python scripts/workflow_check.py .github/workflows/ → total: 0 finding(s)
$ gh run watch → deploy #42 success (6m12s), /health 200
### 확인 필요: 홈서버 배포 방식 — self-hosted runner vs ssh 스텝 (사설 레포라 양쪽 가능, 러너 상주 비용 vs 키 관리 트레이드오프)
```

❌ "일단 master 액션 가져다 붙이고 시크릿은 echo로 확인" (공급망+유출 2종 세트)
✅ "SHA 핀 + 스크립트 분리 + 시크릿은 스텝 env로만"

### 사용자가 권고를 거부하면

- "그냥 빨리 초록 불만" → 따르되 게이트(단위 테스트)는 유지 제안. 거부 시 비차단 전환을 기록(partial — 몰래 끄지 않고 명시).
- "SHA 핀 귀찮아" → 공식 액션만 쓰는 절충안(메이저 태그 허용) 제시. 서드파티 무핀 강행이면 공급망 리스크 1줄 기록.
- 같은 거부 반복 → 레포 CLAUDE.md 규칙화 제안.

### 판단이 막힐 때 (확인 요청 4요소)

배포 경로(self-hosted runner vs ssh)·시크릿 소스·롤백 메커니즘은 인프라를 아는 사용자만 정할 수 있다 — 추측하면 유출·되돌릴 수 없는 배포가 된다. 묶어서 묻는다:
- **누가**: 사용자(레포 공개 여부·홈서버 접근 방식·시크릿 매니저 소유자).
- **언제**: 단계 설계 단계(워크플로우 1) — 특히 배포 수신 측(서버) 구성과 시크릿 주입 경로가 불명일 때.
- **어떻게**: "현재 항목 / 추측값 / 근거 / 기대 답변"으로. 예) "배포를 ssh 스텝으로 가정했는데(근거: 러너 상주 비용 회피), self-hosted runner가 이미 있으면 그쪽이 단순 — 어느 쪽입니까?"
- **기대값**: 배포 방식·시크릿 소스·롤백 명령 중 하나. 받으면 확정값으로, 못 받으면 가장 안전한 가정(공개 레포면 self-hosted 금지·시크릿은 스텝 env로만·롤백=이전 SHA 태그)으로 진행 + 미확정 항목을 "확인 필요"로 명시.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — tj-actions/changed-files 공급망 공격 (2025-03)

수만 레포가 쓰던 액션 `tj-actions/changed-files`가 탈취되어 **모든 버전 태그가 악성 커밋으로 재지정**됐다 — 태그를 믿고 `@v45`로 핀한 레포들이 일제히 악성 코드를 실행, CI 메모리의 시크릿이 로그로 덤프됐다(CVE-2025-30066, 공개 보안 권고 다수). 교훈: ① **태그는 움직인다, SHA만 불변** — 서드파티 SHA 핀(안티패턴 3)은 결벽이 아니라 이 사건의 직접 교훈 ② 시크릿 최소화(워크플로우에 진짜 필요한 것만)와 `pull_request` 시크릿 미제공 기본값이 피해 반경을 가른다 ③ Dependabot류로 액션 갱신을 받되, 갱신 PR의 diff를 사람이 본다 — 자동 머지가 이 공격의 증폭기였다.

## 사용자 환경 적용

- 홈서버 배포 경로: 사설 레포 + 홈서버라 self-hosted runner(상주, 인바운드 불필요)와 ssh 스텝(러너 없음, 키 관리 필요) 둘 다 유효 — 서비스 수가 늘면 runner 1개 공유가 관리 우위. 공개 레포엔 절대 self-hosted 금지(정량 기준).
- 시크릿 소스는 Infisical 사용 중 — Actions secrets에 Infisical 토큰만 두고 나머지는 런타임 주입(facereview에서 쓴 패턴 재사용).
- Windows 개발 + 리눅스 러너: 라인엔딩·경로 차이로 "로컬 통과, CI 실패"가 나면 dev-docker의 .gitattributes 규칙 먼저 확인.

## 레퍼런스

- `scripts/workflow_check.py` — 워크플로우 YAML 냄새 검출기: @master·무timeout·고정 캐시 키·pull_request_target+checkout (표준 라이브러리만, `python scripts/workflow_check.py` 데모)
- `references/actions-patterns.md` — 표준 워크플로우 골격(파이썬 lint/test/build/deploy)·캐시·concurrency·매트릭스·재사용 워크플로우
- `references/deploy-rollback.md` — 배포 전략(태그·헬스체크 게이트·ssh vs runner)·롤백 절차·환경 분리
- `references/evidence-checklist.md` — 출처(tj-actions CVE 등) + 출고 전 체크리스트

## 한계

GitHub Actions 중심 — GitLab CI·Jenkins는 원칙(스크립트 분리·핀·롤백)만 이식 가능하고 문법은 공식 문서로. 점진 배포(카나리·블루그린)는 홈서버 규모에선 과설계라 다루지 않음(필요해지는 규모면 dev-kubernetes와 함께 재검토). 비용 최적화는 사설 레포 무료 한도(확인 필요: 현행 분량) 내 전제.
