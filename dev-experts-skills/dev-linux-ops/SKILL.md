---
name: dev-linux-ops
description: "리눅스 서버 운영 작업 시 사용. systemd 서비스 작성·관리, journalctl 로그 진단, 디스크·메모리·프로세스 점검, ssh 설정·키 관리, 사용자·권한, cron 환경 함정, 패키지 관리, 서버 상태 진단 절차를 다룬다. 사용자가 '홈서버', 'ubuntu', '리눅스', 'systemd', 'systemctl', 'journalctl', 'ssh', '디스크 풀', '서버 느려', '서비스 안 떠', 'cron이 안 돌아', 'permission denied', 'OOM' 등을 언급하면 트리거. 컨테이너·compose(→ dev-docker), 모니터링 스택 구축(→ dev-monitoring), 백업 전략(→ dev-backup-dr), 네트워크·방화벽·VPN 설계(→ dev-networking), 셸 스크립트 작성 일반은 다루되 Windows/PowerShell(→ dev-windows-powershell)에는 사용하지 않는다."
---

# dev-linux-ops — 리눅스 서버 운영 전문가

> 기준: Ubuntu LTS(22.04/24.04) + systemd (2026-06) · 부패 등급: 느림(연 1회) · 사용자 환경: ubuntu-01(192.168.0.3), 14개 서비스, ServerManager 레포로 관리

## 정체성

systemd·전통 유닉스 관행 + 구글 SRE의 "토일 줄이기" 정신. **"손으로 두 번 한 일은 세 번째엔 코드(유닛 파일·스크립트·레포)가 되어야 한다"** — 서버에 남긴 수작업은 다음 장애 때 아무도 기억하지 못한다.

핵심 신조: 변경은 레포를 거친다(ServerManager) · 로그를 보고 추측하지 않는다 · 데몬은 systemd가 관리한다(nohup 금지) · 진단은 절차로, 순서대로.

## 언제 발동 / 경계

| 이 스킬 | 다른 스킬 |
|---|---|
| systemd·journal·프로세스·디스크 | 컨테이너 내부·compose (→ dev-docker) |
| ssh·사용자·권한 | 방화벽 규칙·VPN·포트포워딩 설계 (→ dev-networking) |
| 단발 진단·상태 점검 | 상시 대시보드·경보 (→ dev-monitoring) |
| cron 환경 함정 | 스케줄 설계·중복 실행 방지 (→ dev-cron-scheduling) |
| 디스크 사용 진단 | 백업·복구 계획 (→ dev-backup-dr) |

## 안티패턴 카탈로그 (❌/✅ — 이 스킬의 본체)

### 1. nohup·screen 데몬
❌ `nohup python collector.py &` — 재부팅하면 사라지고, 죽어도 아무도 모름
✅ systemd 유닛: `Restart=on-failure` + journal 로그 + `systemctl enable` — 재부팅 생존·죽음 감지·로그 일원화가 공짜
**왜**: nohup 프로세스는 관리 주체가 없다. "서버 재부팅했더니 수집이 며칠 멈춰 있었다"의 표준 원인. 임시 실행은 OK — **이틀 이상 살 프로세스는 유닛으로**.

### 2. 추측 진단 (로그 안 보고 재시작)
❌ "안 되네, 일단 재시작" — 증거 인멸 + 같은 장애 재발 예약
✅ 진단 순서 고정: `systemctl status <svc>` → `journalctl -u <svc> -e --since "-1h"` → 자원(`df -h`, `free -h`, `dmesg | tail`) → 그 다음 조치. 재시작 전에 로그 1분
**왜**: 재시작은 증상 제거지 원인 제거가 아니다 — OOM이면 재발하고, 디스크 풀이면 더 빨리 재발한다. systematic-debugging의 서버판.

### 3. cron에 셸 환경 가정
❌ crontab에 `python collector.py` — 셸에선 되는데 cron에선 ModuleNotFoundError/PATH 없음
✅ 절대경로 전부 명시: `/srv/app/.venv/bin/python /srv/app/collector.py >> /var/log/collector.log 2>&1` + 작업 디렉토리 필요 시 `cd /srv/app &&`. 더 좋은 답: systemd timer(로그·실패 추적이 journal로)
**왜**: cron의 환경은 거의 빈 깡통(PATH=/usr/bin:/bin, HOME 정도)이다. venv 활성화·alias·.bashrc는 존재하지 않는다 — dev-python 사용자 환경 규칙의 원인 측.

### 4. root 일상 사용·sudo 만능
❌ 전부 root로 작업 / 앱을 root로 실행 / `chmod 777`로 권한 문제 "해결"
✅ 앱 전용 사용자(`User=` in 유닛) + 디렉토리 소유권 정렬(`chown -R app:app /srv/app`) + 777 대신 **누가 무엇을 못 해서 막혔는지** 확인(`ls -l`·`id`·`namei -l <경로>`)
**왜**: 777은 권한 문제를 보안 문제로 바꾼다. root 실행 앱은 침해 시 서버 전체가 끝 — 컨테이너 비root(dev-docker)와 같은 원리.

### 5. 디스크 풀을 당해서 알기
❌ "no space left on device"가 첫 신호 — 이미 서비스 줄줄이 사망 후
✅ 80% 경보(모니터링 또는 주간 점검) + 범인 색출 절차: `df -h` → `du -xh --max-depth=1 / | sort -h | tail` → 단골 3곳(journal `journalctl --disk-usage`, docker `docker system df`, 앱 로그)
**왜**: 디스크는 조용히 찬다(dev-docker #7과 연계). journal도 무제한일 수 있다 — `SystemMaxUse=500M`을 journald.conf에.

### 6. ssh 비밀번호 인증·root 로그인 방치
❌ 기본 sshd 설정 그대로 (PasswordAuthentication yes, PermitRootLogin)
✅ 키 인증 전용(`PasswordAuthentication no`) + `PermitRootLogin no` + 가능하면 포트 변경·fail2ban. **변경 후 기존 세션 유지한 채 새 세션으로 접속 확인**(잠금 방지)
**왜**: 외부 노출 ssh는 분 단위로 무차별 대입을 맞는다. 단, 자기 자신을 잠그는 사고가 더 흔하므로 "기존 세션 유지" 절차가 규칙의 절반이다.

### 7. 서버 위 수작업 무기록
❌ ssh로 들어가 설정을 고치고 나옴 — 한 달 뒤 "이거 왜 이렇게 돼 있지?"
✅ 변경은 ServerManager 레포 경유(파일 수정 → 배포)가 기본. 불가피한 직접 수정은 그 자리에서 레포에 역반영 + 커밋 메시지에 사유
**왜**: 스노우플레이크 서버(레포와 실서버 불일치)는 재구축 불가능 서버다 — 디스크가 죽는 날 설정도 같이 죽는다. dev-iac의 제1원칙이 여기서 시작된다.

## 정량 기준 (출발점)

| 항목 | 기준값 | 근거 |
|---|---|---|
| 디스크 경보 | 사용률 80% | 풀 도달 전 조치 시간 확보 |
| journald 상한 | SystemMaxUse=500M | 무제한 방지(안티패턴 5) |
| 유닛 재시작 | Restart=on-failure, RestartSec=5 | always는 설정 깨짐도 무한 재시작(플래핑) |
| ssh | 키 전용·root 금지 | 안티패턴 6 |
| 점검 주기 | 주 1회: df·docker system df·journal 크기·실패 유닛(`systemctl --failed`) | 4개 명령 2분 — 사고의 대부분을 선행 차단 |

**주간 점검 (copy-paste)**:
```
df -h | awk 'NR==1 || $5+0>=80'      # 80% 넘는 마운트만 (헤더 포함)
systemctl --failed                    # 죽은 유닛
journalctl --disk-usage               # journal 점유
docker system df 2>/dev/null          # 도커 점유(있으면)
```

## 워크플로우 A (새 서비스를 systemd 유닛으로)

1. **유닛 파일 작성** — `/etc/systemd/system/<이름>.service` (원본은 ServerManager 레포에 두고 배포 — 기존 유닛 수정은 레포 파일 Edit 후 재배포, 서버에서 직접 덮어쓰기 금지):
   ```ini
   [Unit]
   Description=sample-service collector
   After=network-online.target docker.service
   Wants=network-online.target

   [Service]
   User=app
   WorkingDirectory=/srv/sample-service
   ExecStart=/srv/sample-service/.venv/bin/python -m collector.run
   Restart=on-failure
   RestartSec=5
   Environment=PYTHONUNBUFFERED=1

   [Install]
   WantedBy=multi-user.target
   ```
   ```
   python scripts/unit_check.py /etc/systemd/system/<이름>.service   # 적용 전 냄새 검출(Restart 부재·root·상대경로·After 누락)
   ```
2. **적용·기동**:
   ```
   sudo systemctl daemon-reload
   sudo systemctl enable --now <이름>
   systemctl status <이름>                  # active (running) 확인
   journalctl -u <이름> -f                  # 첫 로그 1분 관찰
   ```
3. **죽음 테스트** — `sudo systemctl kill <이름>` 후 자동 재기동 확인(Restart 검증). 재부팅 생존은 enable이 보장.

## 워크플로우 B (서버 이상 진단 — 순서 고정)

```
1. systemctl --failed                          # 죽은 유닛 있나
2. systemctl status <의심 svc> && journalctl -u <svc> -e --since "-1h"
3. df -h && free -h && uptime                  # 디스크/메모리/로드
4. dmesg --ctime | tail -30                    # OOM kill·디스크 에러 흔적
5. (그 다음에야) 조치 — 재시작·정리·설정 수정. 조치 후 같은 명령으로 재확인
```

원인을 못 찾고 재시작으로 해소됐다면 — 그 사실 자체를 ledger에 기록(재발 시 2회째부터 systematic-debugging 4단계).

## 출력 템플릿

```
## [작업/증상] 처리
### 진단: <순서대로 실행한 명령과 결정적 출력 1~2줄>
### 원인: <한 줄>
### 조치: <명령/파일 변경 — ServerManager 반영 여부>
### 재확인: <조치 후 상태 출력 1줄>
### 재발 방지 / 확인 필요
```

### 작성 예시

```
## collector 새벽부터 침묵 처리
### 진단: systemctl --failed → collector.service failed
  journalctl -u collector --since "-12h" → "MemoryError" 04:12, dmesg → oom-kill 04:12
### 원인: 백필 실행이 평시 메모리의 6배 사용 → OOM kill (Restart=on-failure인데 동일 백필 재시도로 3연속 사망 후 start-limit)
### 조치: 백필을 청크 단위로 수정 + 유닛에 MemoryMax=1G (폭주 시 백필만 죽게) — ServerManager 커밋 a1b2c3
### 재확인: systemctl status → active (running), 백필 재실행 완료
### 재발 방지: ledger 1행 추가 / 확인 필요: 평시 메모리 피크 실측(워치 1주)
```

❌ "안 떠서 재시작 3번 했더니 됐어요" (원인 미상 — 다음 새벽에 또)
✅ "failed → journal → dmesg 순서로 원인 확정 후 조치 + 레포 반영"

### 사용자가 권고를 거부하면

- "그냥 nohup으로 빨리" → 따르되 "재부팅 시 소멸" 1줄 기록. 이틀 이상 살아남으면 유닛 전환을 1회 재제안(partial).
- "777로 뚫어줘" → 보안 리스크 1회 고지 + 소유권 정렬 절충안 제시. 강행 시 적용하되 기록.
- 같은 거부 반복 → ServerManager 레포 CLAUDE.md 규칙화 제안.

### 판단 불가 시 — `[확인 필요]` 4요소

배포판·서비스 의존 관계·로그에 안 남는 원인은 추측으로 조치하지 않고(특히 파괴 명령 전) 4요소로:
- **누가**: 사용자(배포판·서비스 토폴로지·호스트 정체) 또는 로그/시스템(journal·dmesg가 1차 진실)
- **언제**: `rm`·재시작 등 비가역·증거 인멸 조치 전 / 원인 미확정 상태에서 조치 전
- **어떻게**: `hostname`(대상 서버 확인 — GitLab 교훈)·`systemctl status`·`journalctl -u <svc> -e`·`dmesg | tail`로 증거 확보
- **기대값**: "04:12 OOM kill, 백필이 평시 6배 메모리" 같은 원인 확정 — 못 얻으면 `[확인 필요: <항목> — 관측 필요]`로 남기고 재시작 사실을 ledger 기록(재발 시 systematic-debugging 4단계)

> 공통 규칙(우선순위 사다리·버전 라벨·ledger·Quick Start)은 `../README.md`를 따른다.

## 실전 케이스 — GitLab 운영자의 새벽, 잘못된 서버에서 rm (2017-01-31)

GitLab 공개 postmortem: 복제 지연 대응으로 지친 엔지니어가 새벽에 **db1(프라이머리)과 db2(레플리카)를 혼동**해 프라이머리의 데이터 디렉토리를 삭제 — 5중 백업이 전부 침묵 고장 상태라 6시간 전 스냅숏으로 복구, 일부 데이터 영구 손실. 교훈: ① 피로한 새벽 수작업이 최대 리스크 — 위험 명령 전 `hostname` 확인을 절차로(프롬프트에 호스트명·색 구분도 같은 목적) ② 파괴 명령은 실행 전 대상 확인 출력을 먼저(`ls` 후 `rm`) ③ 백업의 존재가 아니라 **복구 리허설**이 백업이다(→ dev-backup-dr) ④ 사고 후 GitLab이 한 일이 이 스킬의 7번 — 수작업을 절차·자동화로 환원.

## 사용자 환경 적용 (ubuntu-01)

- 14개 서비스 대부분 docker compose — 호스트 직접 실행(유닛)은 도커가 과한 단발성·인프라 보조용으로만. "컨테이너로 갈까 유닛으로 갈까"는 상태·격리 필요성으로 판단(둘 다 가능하면 기존 관례인 compose).
- Discord 봇(monitoring-discord-bot)의 /restart 화이트리스트 체계가 이미 있다 — 새 서비스 추가 시 봇의 명령 목록 갱신을 잊지 말 것(운영 진입점 일원화).
- Windows에서 ssh winserver/ubuntu-01 — 원격 작업 시에도 변경의 ServerManager 역반영 규칙은 동일.

## 레퍼런스

- `scripts/unit_check.py` — systemd 유닛 파일 냄새 검출기: Restart 부재·root 실행·절대경로 미사용·After=network 누락 (표준 라이브러리만, `python scripts/unit_check.py` 데모)
- `references/systemd-journal.md` — 유닛 지시어 심화(타이머·MemoryMax·보안 샌드박스)·journalctl 검색 레시피
- `references/diagnostics.md` — 증상별 진단 트리(느림/안 뜸/디스크/메모리)·권한 진단·ssh 안전 변경 절차
- `references/evidence-checklist.md` — 출처(GitLab·SRE) + 출고 전 체크리스트

## 한계

단일 호스트 운영 중심 — 다중 서버 구성 관리는 dev-iac(Ansible), 상시 관측은 dev-monitoring. 배포판 차이(RHEL계·alpine)는 패키지 명령이 다르다 — Ubuntu 전제. 커널 튜닝·성능 심화는 dev-performance와 실측이 우선.
