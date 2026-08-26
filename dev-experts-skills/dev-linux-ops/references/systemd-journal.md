# systemd 심화 — 타이머·자원·샌드박스·journal 레시피 (SKILL.md 비중복)

## systemd timer (cron의 상위 호환)

```ini
# collector-daily.timer
[Unit]
Description=daily collect at 16:10 KST

[Timer]
OnCalendar=Mon..Fri 16:10
Persistent=true          # 꺼져 있던 동안 놓친 실행을 부팅 후 1회 보충
RandomizedDelaySec=60    # 정시 동시 기동 분산

[Install]
WantedBy=timers.target
```

같은 이름의 `.service`(Type=oneshot)와 쌍으로. cron 대비 이점: journal 로그 자동, `systemctl list-timers`로 다음 실행 확인, 실패가 `--failed`에 잡힘, Persistent로 놓침 보충. **단점**: 파일 2개 — 한 줄짜리는 cron도 충분(절대경로 규칙 지키면).

- 시간대 주의: OnCalendar는 **서버 로컬 타임존** 기준 — `timedatectl`로 서버 TZ 확인이 선행. 거래시간 의존 작업은 dev-data-engineering의 거래일 캘린더와 이중 게이트.

## 자원·안정성 지시어

| 지시어 | 용도 |
|---|---|
| `MemoryMax=1G` | 이 서비스만 OOM — 폭주가 서버 전체를 못 끌고 내려가게 |
| `CPUQuota=50%` | 배치가 대화형 서비스를 굶기지 않게 |
| `TimeoutStartSec=`/`TimeoutStopSec=` | 느린 기동·정리 허용 (기본 90s) |
| `StartLimitIntervalSec=60` `StartLimitBurst=3` | 재시작 폭주(플래핑) 차단 — 3연속 실패 시 멈추고 failed로 |
| `ExecStartPre=` | 기동 전 전제 확인(디렉토리·의존 서비스) |

## 보안 샌드박스 (앱 유닛 기본 세트)

```ini
NoNewPrivileges=true
ProtectSystem=strict        # 전체 파일시스템 읽기 전용(예외: /dev /proc /sys) — ReadWritePaths로만 구멍. (=full은 /usr /boot /etc /efi만, =true는 /usr /boot /efi만)
ProtectHome=true
ReadWritePaths=/srv/sample-service/data   # 쓸 곳만 명시 개방
PrivateTmp=true
```

`systemd-analyze security <svc>`가 노출 점수를 매겨준다 — 새 유닛 출고 전 1회.

## journalctl 검색 레시피 (copy-paste)

```
journalctl -u <svc> -e                          # 해당 유닛 끝부분
journalctl -u <svc> --since "2026-06-11 04:00" --until "05:00"
journalctl -u <svc> -p err                      # 에러 이상만
journalctl -u <svc> -o json --no-pager | tail   # 구조적 추출
journalctl --disk-usage                         # journal 크기
journalctl -k | grep -i -E "oom|killed"         # 커널 OOM 흔적
journalctl --list-boots                         # 부팅 경계 - 재부팅 시점 확정
```

- journal 상한: `/etc/systemd/journald.conf`에 `SystemMaxUse=500M` → `systemctl restart systemd-journald`.
- 앱이 stdout으로만 찍으면(파일 로그 없이) journal이 로테이션·보존을 다 해준다 — 파일 로그+logrotate 직접 관리보다 우선 고려.

## 유닛 변경 작업 절차

```
1. ServerManager 레포에서 유닛 파일 수정 → 서버 배치
2. sudo systemctl daemon-reload          # 파일 변경은 reload 없이 반영 안 됨 (단골 함정)
3. sudo systemctl restart <svc>
4. systemctl status <svc> && journalctl -u <svc> -e   # 확인
```

`daemon-reload` 누락 = "고쳤는데 그대로예요"의 1순위 원인.
