# 배포·롤백 — 식별자·헬스체크 게이트·홈서버 경로 (SKILL.md 비중복)

## 배포 식별자 규약

- 이미지 태그 = `sha-<7자리>` (모든 main 빌드) + 릴리스 시점에 `vX.Y.Z` 추가 태깅 — 같은 이미지에 태그 2개.
- `latest`는 배포 참조로 금지(dev-docker #1) — compose 파일이 가리키는 태그가 곧 "지금 떠 있는 버전"의 단일 진실이 되게.
- 배포 기록은 git이 한다: compose의 태그 변경 커밋 = 배포 이력. 별도 배포 대장 불필요(소규모).

## 배포 절차 표준형 (홈서버)

```bash
# scripts/deploy.sh <tag>  - CI와 수동 실행이 같은 스크립트 (안티패턴 1)
set -euo pipefail
TAG=$1
ssh ubuntu-01 "cd /srv/sample-service \
  && sed -i 's|image: ghcr.io/.../api:.*|image: ghcr.io/.../api:'$TAG'|' compose.yml \
  && docker compose pull api && docker compose up -d api"

# 헬스체크 게이트 - 통과해야 배포 '성공'
for i in $(seq 1 12); do
  curl -fsS http://192.168.0.3:8000/health && exit 0
  sleep 5
done
echo "health check failed - rolling back hint: deploy.sh <previous-sha>" && exit 1
```

- 헬스체크 실패 = 배포 실패로 빨간 불 — "떠는 있는데 안 되는" 상태를 초록으로 두지 않는다.
- 자동 롤백(실패 시 이전 태그 자동 재배포)은 소규모에선 과설계 — 실패를 시끄럽게 + 수동 1명령이면 충분. 이전 태그는 `git log -2 compose.yml`이 알려준다.

## self-hosted runner vs ssh 스텝

| | self-hosted runner | ssh 스텝 |
|---|---|---|
| 네트워크 | 아웃바운드만(러너가 폴링) — 포트 안 염 | 서버 ssh 노출 또는 VPN 필요 |
| 관리 | 러너 프로세스 상주·갱신 관리 | 키 1개 관리 |
| 보안 | **공개 레포 금지**(외부 PR 코드 실행) | 키 유출 = 서버 접근 |
| 적합 | 사설 레포 여러 개 + 잦은 배포 | 레포 1~2개·가끔 배포 |

ssh 스텝 선택 시: 배포 전용 사용자 + authorized_keys에 `command=` 제한(그 키로는 배포 스크립트만 실행 가능)이 키 유출 피해를 줄인다.

## 환경 분리 (그 규모가 되면)

- dev/prod 분리는 환경별 compose 파일이 아니라 **같은 파일 + env_file 차이**가 우선(파일 2개는 반드시 어긋난다 — 백필 스크립트 분리 금지와 같은 원리, dev-data-engineering).
- GitHub `environment:`의 보호 규칙(수동 승인)은 prod 배포에 사람 게이트가 필요해질 때 — 1인 운영에선 보통 불필요(자기 승인은 의식일 뿐).

## 마이그레이션이 낀 배포

- 순서: 마이그레이션이 **하위호환**(컬럼 추가 등)이면 [마이그레이션 → 새 코드 배포]. 비호환 변경은 2단계 배포(추가 → 코드 전환 → 제거)로 쪼갠다 — 롤백 가능성을 유지하는 유일한 방법.
- 롤백 불가 구간(비호환 마이그레이션 직후)은 배포 메시지에 명시 — dev-docker 갱신 절차의 DB 메이저 업그레이드와 같은 주의.
