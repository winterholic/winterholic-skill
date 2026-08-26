# evidence + 출고 전 체크리스트

## 실증·출처

- **ffmpeg 공식 문서** — 스트림 카피·옵션 위치·세그먼트의 1차 출처. 검증(2026-06): `-c copy`는 "very fast and there is no quality loss"(SKILL의 "거의 즉시·무손실"과 일치), `-ss`를 입력 앞에 두면 closest seek point로 빠른 탐색·뒤에 두면 디코드/디스카드(accurate, 느림)로 명시됨 — 본 스킬 옵션 위치 표와 정확히 일치.
  - https://ffmpeg.org/ffmpeg.html — `-ss`·`-c copy` 메인 매뉴얼 (응답 확인)
  - https://ffmpeg.org/ffmpeg-all.html — RTSP 데묵서·segment 머서·`-reset_timestamps` 전체 옵션 (응답 확인)
  - https://trac.ffmpeg.org/wiki/Seeking — 입력/출력 -ss 탐색 정확도 위키 (확인 필요: 본문 미확인)
- **Frigate 공식 문서 — 서브스트림 권장** — 검증(2026-06): docs.frigate.video가 detect는 저해상도 서브스트림, record는 메인스트림 권장을 명시(go2rtc `video=copy` 재스트림 포함). SKILL.md 실전 케이스(서브스트림 지혜)와 정확히 일치.
  - https://docs.frigate.video/configuration/camera_specific/ (응답 확인)
  - https://docs.frigate.video/frigate/camera_setup/ (응답 확인)
- **RTSP 사양** — 검증(2026-06): RFC 2326(RTSP 1.0)은 대부분의 IP 카메라/DVR이 실제 구현하는 사양이나, **2016-12 RFC 7826(RTSP 2.0)으로 공식 obsolete됨**(비호환). 따라서 신규 인용 시 두 RFC를 함께 표기.
  - https://datatracker.ietf.org/doc/html/rfc2326 — RTSP 1.0 (카메라 실구현 기준, 응답 확인)
  - https://www.rfc-editor.org/info/rfc7826/ — RTSP 2.0, RFC 2326 obsolete (응답 확인)
- **ffmpeg RTSP 데묵서 옵션** — 검증(2026-06): 구버전 `-stimeout`(소켓 I/O 타임아웃, µs)은 2021년 `-timeout`으로 리네임됐고 **FFmpeg 8에서 `stimeout` 별칭 완전 제거**(사용 시 "Unrecognized option" 에러). SKILL/레퍼런스가 이미 `-timeout 5000000`(=5초, µs 단위)을 쓰고 있어 최신 기준 정확. `-rtsp_transport tcp`는 UDP 패킷 손실 회피용 권장.
  - https://ffmpeg.org/ffmpeg-protocols.html — RTSP `timeout`·`listen_timeout` (응답 확인)
  - https://github.com/seydx/homebridge-camera-ui/issues/1081 — FFmpeg v8의 stimeout 제거 커뮤니티 확인 (응답 확인)
- **코덱-컨테이너 호환** — Matroska/MP4 사양·브라우저 코덱 지원표(MDN). (확인 필요: 본문 미확인)
- 오픈소스 차용 표기: ffmpeg 레시피 모음 다수(색인 인지, 본문 비복사). **역흡수**: "카피 vs 재인코딩이 첫 질문"·서브스트림 CPU 절약·RTSP 재연결을 systemd로·옵션 위치 함정 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (영상 작업 출고 시)

- [ ] 카피로 될 일을 재인코딩 안 함 (`ffmpeg_lint.py` 0건)
- [ ] 코덱-컨테이너 조합 호환 확인
- [ ] (RTSP) tcp 전송 + 재연결 래퍼(systemd) + 타임아웃
- [ ] 다중 스트림이면 하드웨어 가속
- [ ] (녹화) 세그먼트 + 시간 파일명 + 보존 삭제 배치
- [ ] 옵션 위치 정확 (입력/출력, -ss 위치)
- [ ] 출력 ffprobe로 검증 (코덱·해상도·길이·재인코딩 여부)
- [ ] CPU 사용 관찰 (다중 스트림 드롭 없나)

## 점검 주기 (부패 중간 — 반기)

- ffmpeg 메이저 변경·가속 인코더 옵션 변화 확인 (현행: 8.0.x 최신 / 7.1.x 안정, 2026-06 확인)
- 옵션 deprecation 주시 — `stimeout→timeout`처럼 메이저 버전에서 별칭이 제거될 수 있음(FFmpeg 8에서 `stimeout` 제거 사례)
- CCTV 추가 시 CPU/가속 용량 재점검
