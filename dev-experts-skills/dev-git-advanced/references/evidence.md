# dev-git-advanced evidence — 실증 사례

## 1. Uber GitHub 자격증명 유출 (2016 발생·2017 공개) — git에 시크릿의 비용

- **체인**: 엔지니어가 프라이빗 레포에 AWS 자격증명 포함 코드 커밋 → 공격자가 레포 접근(계정 침해 경유) → 그 키로 S3 접근 → 5,700만 사용자+60만 기사 면허 데이터 유출 → 은폐 시도(보안 책임자 형사 기소)·1.48억 달러 합의.
- **교훈 체계화**: ① 프라이빗 ≠ 안전 — 레포 접근권은 회전·감사가 안 되는 그림자 키 배포 채널 ② 시크릿은 코드와 수명이 다르다(코드는 공유될수록 좋고 시크릿은 반대) — 저장소 분리가 원칙의 근거 ③ 현재 표준 방어: GitHub push protection(공개 레포 기본)·pre-commit 스캐너(gitleaks 등)·시크릿 매니저(사용자 환경: Infisical).
- **사고 시 순서**: 회전(1시간 내) → 영향 조사(그 키로 뭘 할 수 있었나) → 이력 청소(filter-repo) → 재발 가드. 회전 없는 청소는 무의미(이미 복제됐다고 가정).

## 2. reflog 복구 — "브랜치 삭제 복구 5분" (객체 모델 실증)

- **무슨 일**: `git branch -D feature`로 머지 안 된 브랜치 삭제 — 통념과 달리 커밋은 그대로 객체 저장소에 있다. `git reflog`(HEAD 일지) 또는 삭제 직후 출력된 sha로 `git branch feature <sha>` 한 줄 복구. 같은 원리로 reset --hard·rebase 꼬임·detached HEAD에서의 커밋도 전부 동일 절차.
- **시한**(git 공식 기본값): reflog 도달 가능 항목은 `gc.reflogExpire` 90일, 도달 불가 항목은 `gc.reflogExpireUnreachable` 30일까지 보존 — 이 동안 `git reflog`로 sha를 집어낼 수 있다. reflog에서 빠진 뒤의 loose object는 `gc.pruneExpire` 기본 2주(2.weeks.ago)가 지나야 실제 삭제 대상이 된다(`git gc` 또는 자동 gc 실행 시점). 즉 "어제 날린 것"은 사실상 100% 복구권 — 단 명시적 `git gc --prune=now`나 reflog 만료를 직접 당기지 않은 경우.
- **유일한 진짜 유실**: 커밋·stash 안 된 작업 트리 변경을 덮는 명령(reset --hard·checkout -- 등). 그래서 "위험 명령 전 stash"가 보험이고, 사고 후엔 추가 명령 동결이 철칙(uncommitted를 덮는 2차 사고 방지).

## 3. git bisect run — 회귀 추적 전자동 (생산성 실증)

- **무슨 일**: "2주 전엔 됐는데 지금 깨짐" — 커밋 137개. `git bisect start; git bisect bad HEAD; git bisect good <2주전sha>; git bisect run pytest tests/test_x.py` 한 세트로 git이 이진 탐색하며 테스트를 자동 실행, ~8회 만에 범인 커밋 출력.
- **요건**: ① 깨짐을 판별하는 명령(exit 0/비0) ② 과거의 good 지점. 플레이키 테스트면 bisect가 오판하므로 판별 명령의 안정성 먼저(반복 실행 옵션으로 보강).
- **활용 폭**: 기능 회귀뿐 아니라 성능 회귀(판별 스크립트가 시간 측정 후 임계 비교)·빌드 깨짐에도 동일 — "언제부터"가 들어간 모든 질문의 1순위 도구.

## 4. force push 안전판 — `--force-with-lease` 단독은 불충분 (git 2.30+ 보강)

- **무슨 일**: `--force-with-lease`는 "원격이 내 remote-tracking ref와 같을 때만 밀기"인데, IDE/툴의 백그라운드 `git fetch`가 ref를 갱신해버리면 동료의 새 커밋을 "이미 본 것"으로 오인하고 그대로 덮는다 — git-push 문서와 메인테이너 안내 모두 "단독으로는 `--force`보다 거의 안 나음"으로 경고.
- **현재 권고**: `git push --force-with-lease --force-if-includes` 병용. `--force-if-includes`(git 2.30, 2021 도입)는 로컬 reflog로 "그 원격 커밋이 실제 내 브랜치 이력에 통합됐는지"를 검사해 fetch 레이스를 닫는다. 단독 지정 시 no-op이라 반드시 bare `--force-with-lease`와 함께 써야 하며, `git config --global push.useForceIfIncludes true`로 상시화 가능.
- **한계**: 로컬 브랜치명과 원격 추적 브랜치명이 다르면 정상 push를 거부하는 오탐이 있을 수 있다.

> 출처(2026-06 확인):
> - Uber 2016 유출 — [DOJ Non-Prosecution Agreement](https://www.justice.gov/usao-ndca/pr/uber-enters-non-prosecution-agreement) · [NPR(2018, $148M 합의)](https://www.npr.org/2018/09/27/652119109/uber-pays-148-million-over-year-long-cover-up-of-data-breach). 57M 사용자(60만 운전면허 포함), $148M 50개주 합의, CSO Joe Sullivan 사법방해 유죄(2022) — 모두 1차/보도 확인.
> - reflog·gc 보존 기본값 — git 공식 [git-gc 문서](https://git-scm.com/docs/git-gc) (reflogExpire 90일·reflogExpireUnreachable 30일·pruneExpire 2.weeks.ago) · [git-reflog 문서](https://git-scm.com/docs/git-reflog).
> - GitHub 파일 한도 — [About large files on GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github) (50MiB 경고·100MiB 푸시 차단).
> - force push 안전 — git 공식 [git-push 문서](https://git-scm.com/docs/git-push) (`--force-if-includes`).
> - 이력 청소 도구 — git이 [git-filter-branch 문서](https://git-scm.com/docs/git-filter-branch)에서 filter-branch 비권장·[git-filter-repo](https://github.com/newren/git-filter-repo) 권장 명시.
> - bisect 자동화 — git 공식 git-bisect 문서(`git bisect run`).
