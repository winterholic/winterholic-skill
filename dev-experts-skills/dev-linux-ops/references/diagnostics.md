# 증상별 진단 트리·권한·ssh 안전 절차 (SKILL.md 비중복)

## 증상별 진단 트리

### "서비스가 안 떠요"
```
systemctl status <svc>
├─ failed (exit code) → journalctl -u <svc> -e : 앱 에러 (설정/의존/포트 점유 ss -tlnp | grep :PORT)
├─ activating (auto-restart) 반복 → 플래핑: 같은 에러 무한 — 로그의 첫 실패 원인만 보면 됨
├─ inactive (dead) → enable 안 됐거나 수동 stop — systemctl is-enabled <svc>
└─ status 깨끗한데 동작 안 함 → 프로세스는 살았으나 일 안 함: 앱 로그·헬스 지표 (dev-monitoring)
```

### "서버가 느려요"
```
uptime (load) → 코어 수 대비
├─ load 높음 → top (CPU 범인) / iostat -x 1 (디스크 대기 %util)
├─ load 낮은데 느림 → 메모리: free -h (available 기준 - buff/cache는 자유 메모리다, 'used 많음'에 속지 말 것)
│   └─ swap 사용 중 + si/so 활발 (vmstat 1) → 실질 메모리 부족
└─ 특정 서비스만 느림 → 그 서비스 레이어로 (DB면 dev-postgres, 앱이면 dev-performance)
```

### "디스크가 찼어요"
```
df -h (어느 파일시스템) → du -xh --max-depth=1 <마운트> | sort -h | tail
단골: journalctl --disk-usage / docker system df / 앱 로그 디렉토리 / 오래된 백업
지웠는데 안 줄어듦 → 삭제된 파일을 잡고 있는 프로세스: lsof +L1 → 해당 서비스 재시작
```

### "OOM으로 죽었어요"
```
dmesg --ctime | grep -i oom  또는 journalctl -k | grep -i oom
→ 누가 죽었나(피해자)와 누가 메모리를 먹었나(원인)는 다를 수 있다 - oom_score 순 저격
→ 처방: 범인 서비스에 MemoryMax(유닛) / mem_limit(컨테이너) - 폭주를 그 서비스 안에 가두기
```

## 권한 진단 (777 대신)

```
id <user>                        # 그 사용자의 그룹
ls -l <파일> / ls -ld <디렉토리>  # 소유자·권한
namei -l /srv/app/data/file      # 경로 전체의 권한 체인 - 중간 디렉토리 x 권한 누락 색출
sudo -u app cat <파일>           # 그 사용자로 재현 - 추측 대신 확인
```

처방 순서: 소유권 정렬(chown) → 그룹 추가(usermod -aG) → 그래도 안 되면 ACL(setfacl) — 777은 목록에 없다.

## ssh 안전 변경 절차 (자기 잠금 방지)

```
1. 새 설정 검증: sudo sshd -t                    # 문법 에러 시 적용 금지
2. sudo systemctl reload sshd                     # restart 아닌 reload (기존 세션 유지)
3. 현재 세션 유지한 채 - 새 터미널에서 접속 시험
4. 성공 후에만 기존 세션 종료
```

- 키 등록 전 비밀번호 인증을 끄지 않는다(순서: 키 등록 → 키 접속 확인 → 비번 off).
- `~/.ssh` 권한: 디렉토리 700, authorized_keys 600 — 느슨하면 sshd가 키를 무시한다(에러 메시지 없이 비번을 물어보는 게 신호).
- 홈 네트워크 밖 노출(포트포워딩) 결정은 dev-networking — 기본은 VPN 경유, 직접 노출은 최후.

## 패키지·시스템 갱신 규율

- `unattended-upgrades`(보안 패치 자동)는 켜되, 메이저 업그레이드(`do-release-upgrade`)는 백업(dev-backup-dr) + 시간 확보 후 의도적으로.
- 설치 기록: 수동 설치 패키지는 ServerManager 레포의 설치 목록에 추가 — `apt-mark showmanual`이 현황 대조 도구.
