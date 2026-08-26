# evidence + 출고 전 체크리스트

## 실증·출처

- **GitLab postmortem (2017-01-31)**: "Postmortem of database outage of January 31" (about.gitlab.com/blog/postmortem-of-database-outage-of-january-31) — db1.cluster(프라이머리)/db2.cluster(레플리카) 혼동 rm로 300GB→4.5GB, 5중 백업/복제 전부 침묵 고장(pg_dump 9.2↔9.6 버전 불일치, S3 미작동, Azure 스냅숏 미설정, 레플리카는 이미 삭제됨), 6시간 묵은 스테이징으로 복구. 웹 확인(2026-06) 공식 블로그 일치. SKILL.md 실전 케이스 원 출처. 피로 수작업·호스트 확인 절차·복구 리허설 규칙의 실증.
- **구글 SRE (Site Reliability Engineering, 2016)** Ch.5 "Eliminating Toil" — 수작업의 코드화(안티패턴 7)의 출처. 원문 기준은 "토일을 SRE 각자 시간의 **50% 미만**으로 묶고 나머지 50%+는 엔지니어링에"(토일을 방치하면 100%까지 팽창). 토일 정의: manual·repetitive·automatable·tactical·devoid of enduring value·linearly scaling. 웹 확인: O'Reilly ch05, sre.google/sre-book/eliminating-toil (2026-06).
- **free -h의 available**: 리눅스 커널 문서·`man free` — buff/cache는 회수 가능 메모리. "메모리 부족" 오진의 1순위 원인이라 진단 트리에 명시.
- **systemd 공식 문서**(freedesktop.org/software/systemd/man/latest/): systemd.service·systemd.timer·systemd.exec(SANDBOXING 절) — 지시어 의미의 1차 출처. `systemd-analyze security`도 공식 도구. 웹 확인(2026-06): ProtectSystem=strict는 전체 FS 읽기전용(예외 /dev·/proc·/sys), =full이 /usr·/boot·/etc·/efi, =true가 /usr·/boot·/efi — strict는 ReadWritePaths로만 쓰기 개방. TimeoutStart/StopSec 기본 90s(DefaultTimeoutStartSec), DefaultRestartSec 기본 100ms.
- 오픈소스 차용 표기: 리눅스 운영류 스킬 다수 존재(VoltAgent 색인) — **역흡수**: 자기 잠금 방지 ssh 절차·"기존 세션 유지" 규칙·ServerManager 역반영 규율(스노우플레이크 방지) 부재가 본 스킬 차별점.

## 출고 전 체크리스트 (서버 변경·유닛 추가 시)

- [ ] 이틀+ 살 프로세스는 유닛 또는 컨테이너 (nohup 없음)
- [ ] 유닛: Restart·User·절대경로·network-online (`unit_check.py` 0건)
- [ ] daemon-reload 실행함 (파일만 고치고 끝 아님)
- [ ] 죽음 테스트(kill 후 재기동) 통과
- [ ] 변경이 ServerManager 레포에 반영됨 (커밋 해시 기록)
- [ ] 위험 명령(rm·dd·DROP) 전 hostname·대상 확인 출력 선행
- [ ] ssh 설정 변경 시 안전 절차(sshd -t → reload → 새 세션 시험) 준수
- [ ] journald 상한 설정 확인 (`journalctl --disk-usage`)
- [ ] 주간 점검 4종(df·docker df·journal·--failed)이 일정에 있음
- [ ] 새 서비스가 Discord 봇 운영 명령 체계에 등록됨

## 점검 주기 (부패 느림 — 연 1회)

- Ubuntu LTS 버전·지원 기간 확인 (현 22.04/24.04)
- `systemctl --failed` + `systemd-analyze security` 상위 노출 유닛 재점검
- ledger의 서버 삽질 3회 패턴 → 진단 트리 보강
