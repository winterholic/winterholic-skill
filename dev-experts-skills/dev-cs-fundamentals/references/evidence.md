# dev-cs-fundamentals evidence — 실증 사례

## 1. fsyncgate (2018) — fsync 실패의 배신 (PostgreSQL 커뮤니티 공개 분석)

- **무슨 일**: PG 개발자들이 확인 — 리눅스(및 일부 OS)에서 fsync가 EIO로 실패하면 커널이 해당 더티 페이지를 버리고 클린 표시 → **다음 fsync는 성공 반환**(데이터는 이미 유실). "실패하면 재시도"라는 합리적 설계가 유실을 커밋 성공으로 둔갑시킬 수 있었다. LWN·학회 발표로 공론화, PG는 fsync 실패 시 즉시 PANIC으로 전환(다른 DB들도 후속 점검).
- **교훈 체계화**: ① "재시도하면 되겠지"는 멱등 가정 — fsync는 멱등이 아니었다. 에러 후 상태가 명세에 없으면 가장 보수적으로(크래시 후 WAL 복구) ② 내구성 경로의 에러 처리는 성공 경로보다 중요하고 테스트는 더 어렵다(전원 단절 시뮬레이션) ③ 앱 개발자의 실용 결론: 유실 불가 데이터는 이 계약을 이미 싸운 계층(DB)에 위임.

## 2. OOM killer — "프로세스가 흔적 없이 사라졌다" (리눅스 운영 표준 진단)

- **무슨 일**: 메모리 압박 시 커널 OOM killer가 점수 기반으로 프로세스를 즉살(SIGKILL) — 앱 로그엔 아무것도 없다(정리 기회 0). "에러도 없이 죽었어요"의 1순위 용의자.
- **진단 1줄**: `dmesg -T | grep -i "killed process"` 또는 `journalctl -k | grep -i oom` — 누가 언제 얼마나 쓰다 죽었는지 커널이 기록해뒀다. 컨테이너면 exit code 137 + `docker inspect`의 OOMKilled(→ dev-kubernetes evidence와 동일).
- **방어**: ① 메모리 추세 모니터링(급사 전 경사가 있다) ② 중요 프로세스의 oom_score_adj 조정은 미봉 — 본질은 메모리 예산 설계 ③ 스왑 유무에 따라 양상이 다름(스왑 없으면 즉사, 있으면 먼저 전체가 늪처럼 느려짐 — "느려졌다 죽음"의 전조 해석).

## 3. 좀비·고아 프로세스 — ps의 Z와 PID 1 문제 (프로세스 모델 실증)

- **무슨 일**: ① **좀비(Z)**: 자식이 종료됐는데 부모가 wait()로 종료 코드를 안 거둠 — 프로세스 테이블 슬롯 점유(메모리는 거의 0이지만 누적되면 PID 고갈). 부모의 자식 관리 버그 신호 ② **고아**: 부모가 먼저 죽은 자식 — init(PID 1)이 입양. 컨테이너에서 앱이 PID 1이면 **입양한 좀비를 거둘 책임**까지 지는데 대부분의 앱은 그 코드가 없다 — 컨테이너 좀비 누적의 원인.
- **진단**: `ps aux | awk '$8 ~ /Z/'` (좀비 목록) — 좀비는 kill 불가(이미 죽음), 부모를 고치거나 부모 재시작.
- **컨테이너 처방**: tini 등 경량 init 사용(`docker run --init` / Dockerfile ENTRYPOINT tini) — PID 1의 거둠 책임을 전담시킨다(→ dev-docker와 접속). "컨테이너에 좀비가 쌓여요"의 표준 답.

> 출처 (2026-06 확인, 모두 응답 확인):
> - fsyncgate — PostgreSQL 공식 wiki 정리(권위 1차): https://wiki.postgresql.org/wiki/Fsync_Errors (PG12 커밋에서 "fsync 실패 시 PANIC", 9.4~11 백패치 명시. 수정 마이너 릴리스 2019-02-14)
> - fsyncgate 원 메일링 스레드(Craig Ringer, 2018-03 발단): https://www.postgresql.org/message-id/CAMsr+YHh+5Oq4xziwwoEfhoTZgr07vdGG+hu=1adXx59aTeaoQ@mail.gmail.com
> - 커뮤니티 아카이브(스레드 전문 정리, 신뢰도 높은 2차): https://danluu.com/fsyncgate/
> - tini 경량 init(좀비 거둠·시그널 포워딩, PID 1 전담) — 공식 레포: https://github.com/krallin/tini · Docker `--init` 빌트인은 1.13+
> - OOM killer·프로세스 상태(Z) — 리눅스 커널 문서 + OSTEP(Three Easy Pieces). exit code 137 = 128+9(SIGKILL), 143 = 128+15(SIGTERM).
