# Actions 패턴 — 표준 골격·캐시·concurrency·재사용 (SKILL.md 비중복)

## 파이썬 게이트 워크플로우 표준형

```yaml
name: ci
on:
  pull_request:
    paths-ignore: ["**.md", "docs/**"]
  push:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true        # 같은 브랜치 연속 push - 이전 실행 취소

jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v7      # 2026-06 기준 최신 메이저 — 사용 시점에 릴리스 페이지로 재확인
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: pip               # setup-python 내장 캐시 - 수동 actions/cache보다 간단
      - run: pip install -e ".[dev]"
      - run: ./scripts/ci-test.sh  # 로컬과 같은 명령 (안티패턴 1)
```

- `setup-*` 액션들의 내장 캐시(`cache:` 옵션)가 1순위 — 수동 `actions/cache`는 내장이 없는 경우만(그때 키는 hashFiles).
- 매트릭스는 필요해질 때만: `strategy: matrix: python: ["3.10", "3.12"]` — 라이브러리가 아니면 단일 버전이 보통 맞다(YAGNI).

## 배포 잡 패턴 (빌드와 분리)

```yaml
  deploy:
    needs: [test, build]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    environment: production        # 환경 보호 규칙(승인·시크릿 스코프) 연결점
    steps:
      - name: ssh deploy
        env:
          SSH_KEY: ${{ secrets.DEPLOY_KEY }}   # 쓰는 스텝에만 주입
        run: ./scripts/deploy.sh sha-${GITHUB_SHA::7}
```

- `environment:`로 시크릿을 환경 단위 스코프 — 테스트 잡은 배포 키를 아예 못 본다.
- 이미지 태그·식별자 규약과 헬스체크 게이트는 `deploy-rollback.md`.

## 재사용 워크플로우 (레포 여러 개에 같은 파이프라인)

```yaml
# .github/workflows/reusable-python-ci.yml (공용 레포)
on:
  workflow_call:
    inputs:
      python-version: { type: string, default: "3.12" }

# 사용하는 쪽
jobs:
  ci:
    uses: myorg/ci-templates/.github/workflows/reusable-python-ci.yml@<SHA>
    with: { python-version: "3.10" }
```

레포 3개째에 같은 YAML을 복사하고 있다면 이걸로 — 단 호출도 SHA 핀(공급망 규칙 동일).

## 디버깅 도구

```
gh run list --workflow ci --limit 5          # 최근 실행
gh run view <id> --log-failed                # 실패 스텝 로그만
gh run rerun <id> --failed                   # 실패 잡만 재실행 (진단 후에만)
ACTIONS_STEP_DEBUG=true                      # 레포 시크릿으로 설정 시 상세 로그
```

- "로컬은 되는데 CI 실패" 점검 순서: 버전(setup-python 출력) → 캐시(키 출력) → env(시크릿 부재) → OS 차이(경로·라인엔딩) — 워크플로우 실패 디버깅 절차 5의 상세.
- act(로컬 Actions 실행기)는 근사치일 뿐 — 게이트 스크립트 직접 실행이 더 정확한 재현.

## 트리거 선택 빠른 표

| 의도 | 트리거 |
|---|---|
| PR 게이트 | `pull_request` (fork 안전 — 시크릿 미제공) |
| main 반영 시 배포 | `push: branches: [main]` |
| 수동 실행(백필 등) | `workflow_dispatch` + inputs |
| 릴리스 | `push: tags: ["v*"]` |
| 주기 작업 | `schedule: cron` — 단 서버 작업은 서버 타이머(dev-linux-ops)가 우선, Actions cron은 레포 작업용 |
| fork PR에 라벨·코멘트 | `pull_request_target` — **체크아웃 없이** 메타데이터 작업만 (검출기 C2) |
