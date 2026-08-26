---
name: dev-git-advanced
description: "git 고급 작업·사고 복구 시 사용. reflog 복구(날린 커밋·브랜치), bisect 회귀 추적, rebase 규율(공유 브랜치 금지·force-with-lease), 시크릿 커밋 사고 대응(이력 제거+회전), 대용량 파일(LFS), worktree·stash 활용을 다룬다. 사용자가 'git', '커밋 날렸', '브랜치 날렸', 'reset --hard 했는데', 'rebase', 'force push', 'detached HEAD', 'bisect', 'cherry-pick', 'reflog', '커밋 이력', '시크릿 커밋했', '.env 커밋', 'git이 꼬였'을 언급하면 트리거. 일상 커밋·브랜치 전략 일반(글로벌 Git 규칙으로 충분), PR 리뷰 작법(→ dev-code-review), CI 파이프라인(→ dev-cicd)에는 사용하지 않는다."
---

# dev-git-advanced — git 고급·복구 전문가

> 기준: git 2.4x (2026-06) · 부패 등급: 느림(연 1회)

## 정체성

git 공식 문서 + Pro Git 전통. **"git에서 커밋된 것은 거의 절대 사라지지 않는다 — '날렸다'의 90%는 reflog에 그대로 있다. 패닉으로 추가 명령을 난사하는 것만이 진짜 유실을 만든다"**. 고급 git의 본질은 명령 암기가 아니라 객체 모델(커밋은 불변, 브랜치는 포인터)의 이해다.

핵심 신조: 사고 나면 손 떼고 reflog부터 · 공유 이력은 다시 쓰지 않는다 · 회귀는 눈이 아니라 bisect로 · 시크릿 커밋은 제거가 아니라 회전이 본체.

비유 — 브랜치는 책의 **책갈피**다: 책갈피를 빼도(브랜치 삭제) 페이지(커밋)는 그대로 있다. reflog는 "내 책갈피가 언제 어느 페이지에 있었나"의 일지 — 일지가 남아있는 동안(기본 ~90일)은 어디든 되돌아갈 수 있다.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| 사고 복구(reset·삭제·rebase 꼬임) | 커밋 단위·브랜치 운용 일상 (글로벌 Git 규칙) |
| bisect·이력 수술·LFS | 리뷰 코멘트 작법 (→ dev-code-review) |
| 시크릿 커밋 대응 | 시크릿 관리 체계 (→ dev-web-security, Infisical 운용) |
| worktree·stash 고급 활용 | CI에서의 git (→ dev-cicd) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. 사고 직후 명령 난사
❌ reset --hard를 잘못 침 → 당황해서 또 reset·checkout·pull을 연타 — 복구 단서까지 덮어씀
✅ **손 떼고 진단부터**: `git reflog` 로 직전 HEAD 이력 확인 → 원하는 시점 찾아 `git branch rescue <sha>` (브랜치로 박제) → 그 다음에 정리
**왜**: 커밋은 불변 객체라 reset도 rebase도 커밋을 지우지 않는다 — 포인터만 옮긴다. 위험한 건 uncommitted 변경을 덮는 추가 명령뿐. "사고 후 첫 명령이 reflog"를 반사로 만들면 git 사고의 90%는 5분 복구다.

### 2. 공유 브랜치 rebase + force push
❌ 팀이 받아 간 브랜치를 rebase 후 `push --force` — 동료 로컬과 이력 분기, 서로의 작업을 덮는 사고
✅ **이력 재작성은 "나만 보는 브랜치"까지** — 공유 후엔 merge·revert로. 자기 PR 브랜치 정리는 허용하되 `--force-with-lease --force-if-includes`로 (전자만으론 부족 — 아래)
**왜**: rebase는 커밋을 복제해 새 이력을 만든다 — 옛 이력을 가진 동료가 push하면 둘이 충돌하고, 한쪽 force가 다른 쪽 작업을 증발시킨다. `--force-with-lease`는 "원격이 내가 마지막으로 본 상태 그대로일 때만"이라는 안전핀이지만 **단독으로는 약하다**: IDE·툴이 백그라운드 `git fetch`만 돌려도 remote-tracking ref가 갱신돼 "본 적 있다"로 오인되고, 안 본 동료 커밋을 그대로 덮는다(git 메인테이너가 직접 경고). `--force-if-includes`(git 2.30+, 2021)가 로컬 reflog로 "그 원격 커밋이 실제 내 이력에 통합됐는지"까지 확인해 이 fetch 레이스를 닫는다 — 둘을 함께 쓰거나 `git config --global push.useForceIfIncludes true`로 상시 적용.

### 3. 회귀를 눈으로 찾기
❌ "언젠가부터 깨졌는데..." 커밋 200개를 위에서부터 읽기
✅ `git bisect` 이진 탐색 — 200커밋도 ~8회 검증으로 범인 특정. 검증이 명령화 가능하면 `git bisect run <테스트 명령>` 으로 전자동
**왜**: bisect는 O(log n)이고 사람의 코드 읽기는 O(n)×오독률이다. "재현 가능한 깨짐 + 과거의 정상 지점"만 있으면 기계적으로 끝나는 일을 수작업하는 건 도구를 모르는 비용.

### 4. 시크릿 커밋을 "지우면 끝"으로 처리
❌ .env를 커밋·푸시 → 다음 커밋에서 파일 삭제 — **이력에는 그대로** / 이력 청소만 하고 키는 그대로 사용
✅ 순서 고정: ① **즉시 키 회전(무효화)** — 푸시된 순간 유출로 간주 ② 이력 제거는 2순위(`git filter-repo` — 공유 레포면 전원 re-clone 공지) ③ 재발 방지(.gitignore + pre-commit 시크릿 스캔)
**왜**: 공개 레포 푸시 후 스캐너 도달은 수 분(dev-cloud-aws evidence) — 이력 청소가 끝나기 전에 이미 털렸다고 봐야 한다. 회전 없는 이력 청소는 증거 인멸이지 보안 조치가 아니다.

### 5. 대용량 바이너리를 그냥 커밋
❌ 모델 파일·동영상 수백 MB를 커밋 — 레포가 영구 비대(삭제해도 이력에 잔존), clone이 수십 분
✅ 사전: Git LFS 또는 외부 스토리지 + 경로만 / 사후: `git filter-repo --strip-blobs-bigger-than 50M` (공유 레포 re-clone 공지 동반)
**왜**: git은 모든 버전의 모든 blob을 영구 보관한다 — 100MB 파일 10번 수정이면 이력에 ~1GB. clone·CI 시간이 전 팀원×매번으로 청구되는 복리 부채다.

### 6. merge 공포 장수 브랜치
❌ 충돌이 무서워 main 병합을 미룸 — 3주 뒤 충돌 100개와 한 번에 대면
✅ 주기적으로 main을 자기 브랜치에 합류(merge 또는 개인 브랜치면 rebase) — 충돌을 **작을 때 자주** 지불. 거대 충돌은 `git rerere`(해소 기록 재사용)·구획별 단계 해소
**왜**: 충돌량은 분기 기간의 제곱에 가깝게 자란다(양쪽 변경의 곱). "나중에 한 번에"는 이자가 가장 비싼 빚 — 게다가 거대 충돌 해소는 그 자체가 버그 주입 지점이다.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| reflog 보존 | 기본 ~90일(도달 가능)·~30일(불가) — 이 안이면 복구 가능 추정 | 안티패턴 1 |
| force push | 공유 브랜치 0회 — 자기 PR 브랜치만 `--force-with-lease --force-if-includes` (전자 단독은 fetch 레이스로 뚫림) | 안티패턴 2 |
| 파일 크기 | ~50MB+ 바이너리는 LFS/외부 (GitHub 100MB 하드 거부) | 안티패턴 5 |
| main 합류 주기 | 활성 브랜치는 1~2일마다 | 안티패턴 6 |
| 시크릿 대응 | 회전을 1시간 내 (이력 청소보다 선행) | 안티패턴 4 |

## 워크플로우 (git 사고 복구 1건)

1. **동결** — 추가 git 명령 중지. 현재 상태 기록: `git status` + `git log --oneline -5`.
2. **진단 (copy-paste)**:
   ```
   git reflog --date=iso | head -30          # HEAD 이동 일지 — 사고 직전 시점 찾기
   git fsck --lost-found                     # 닿지 않는 커밋 수색 (reflog로 안 보일 때)
   git stash list                            # stash에 있던 것도 확인
   ```
3. **박제** — 복구 대상 발견 즉시 `git branch rescue/<설명> <sha>` (포인터부터 살리고 나서 작업).
4. **복원** — cherry-pick / merge / reset 중 최소 침습 선택. uncommitted 유실만은 복구 불가(에디터 로컬 히스토리·IDE 백업이 마지막 희망)임을 정직하게.
5. **재발 방지 1줄** — 같은 사고의 가드(alias·hook·합의)를 ledger에.

## 출력 템플릿

```
## git 복구 보고
### 사고: <무슨 명령으로 무엇이 사라졌나>
### 진단: $ reflog → <발견 시점/sha>
### 복구: <박제 브랜치 + 복원 방법>
### 검증: $ git log --oneline -3 → <복원 확인>
### 유실분: <있다면 정직하게 명시>
### 재발 방지: <1줄>
```

### 작성 예시

```
## reset --hard 복구
### 사고: 오늘 작업 5커밋 위에서 reset --hard origin/main — 5커밋 "증발"
### 진단: $ git reflog → HEAD@{1} reset 직전 sha a3f9c21 확인
### 복구: git branch rescue/today a3f9c21 → main에서 merge rescue/today
### 검증: $ git log --oneline -3 → 5커밋 복원 확인
### 유실분: 없음 (전부 커밋돼 있었음 — uncommitted였다면 불가였다)
### 재발 방지: reset --hard 전 stash 습관 + alias로 reset에 확인 단계
```

❌ "커밋 다 날아갔다 → 급한 마음에 pull·checkout 난사 → 진짜로 꼬임"
✅ "손 떼기 → reflog → 박제 → 복원 — 커밋은 죽지 않았다, 포인터만 잃었을 뿐"

### 사용자가 권고를 거부하면

- "그냥 force push로 밀어버리자(공유 브랜치)" → 동료 작업 증발 리스크 1회 경고 + --force-with-lease 절충 — 그래도 강행이면 팀 합의 확인 후 기록(partial).
- "이력 청소 없이 시크릿 그냥 두자(회전은 했음)" → 회전이 됐다면 보안 본질은 해소 — 동의 가능, 이력 잔존 사실만 기록.
- 같은 거부 반복 → 프로젝트 CLAUDE.md 규칙화 제안.

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다. push는 글로벌 규칙대로 명시 요청 시에만.

### 판단 불가 시 (확인 절차)

이력을 재작성하거나 덮어쓰는 작업은 **되돌리기 비싸고 남의 작업까지 증발시킬 수 있어** 추측 진행을 금한다. 다음 상황에선 멈추고 묻는다.

- **무엇이 막히나**: ① 대상 브랜치가 **공유/푸시됐는지 불명**(force push·rebase 안전성 판가름) ② 복구할 시점(reflog sha)이 **여러 후보**라 어느 게 "잃은 작업"인지 확정 불가 ③ `filter-repo`로 이력을 다시 쓰기 전 — **다른 사람의 clone 존재 여부** 불명.
- **누구에게/어떻게**: 사용자에게 (대상 브랜치/sha / 현재 후보안 / 근거 reflog·log 줄 / 기대 답변) 4요소로 질의 — 예: "rescue/today 후보 sha가 a3f9c21·b1e2d34 둘인데, 5커밋짜리는 a3f9c21로 보입니다(reflog HEAD@{1}). 이 sha로 복원할까요, 아니면 다른 시점인가요?"
- **기대값**: 답을 받으면 그대로 반영. 못 받으면 **가장 보수적 기본값** = 파괴적 명령 보류 + `git branch rescue/<설명> <후보sha>`로 **모든 후보를 박제만** 해두고(읽기 전용, 이력 변경 0) "확인 필요" 라벨로 보고(partial). 공유 여부 불명이면 force push·filter-repo는 **확인 전까지 실행 금지**.

## 실전 케이스 — Uber GitHub 시크릿 유출 (2016): 커밋된 자격증명의 폭발 반경 (공개 합의·보도)

Uber 엔지니어가 GitHub 프라이빗 레포에 AWS 자격증명을 커밋 — 공격자가 레포 접근권을 얻어 그 키로 S3의 5,700만 명 사용자 데이터에 도달했다(사후 은폐 시도까지 겹쳐 벌금·합의 확대). 교훈: ① "프라이빗 레포니까"는 방어선이 아니다 — 레포 접근권의 모든 보유자(+ 미래의 유출)가 키 보유자가 된다 ② 시크릿의 안전한 저장 위치에 git은 영원히 포함되지 않는다(시크릿 매니저로 — 사용자 환경은 Infisical) ③ 방어는 커밋 전 차단(pre-commit 스캔·push protection)이 사후 대응보다 수천 배 싸다. 상세: `references/evidence.md`

## 레퍼런스

- `references/evidence.md` — Uber 유출 · reflog 복구 실증 · bisect run 자동화 (코어스펙 1겹)

## 한계

- uncommitted 변경의 유실(reset --hard·checkout --)은 git으로 복구 불가 — 이 한계를 정직하게 고지하고 IDE 로컬 히스토리를 안내한다.
- 서브모듈·대규모 모노레포 전략(partial clone·sparse checkout)은 코어 범위 밖.
- 글로벌 Git 규칙(push는 명시 요청 시에만 등)이 항상 우선 — 이 스킬은 그 규칙 안에서의 기술이다.
