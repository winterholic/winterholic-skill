# 트랜스코딩·RTSP·가속·세그먼트·HLS·옵션 (SKILL.md 비중복)

## 카피 vs 재인코딩 판정표

| 작업 | 카피 가능? | 명령 핵심 |
|---|---|---|
| 컨테이너 변경(mp4↔mkv) | ◎ 카피 | `-c copy` |
| 자르기(trim) | ◎ 카피(키프레임 단위) | `-ss ... -to ... -c copy` |
| 합치기(concat) | ◎ 카피(같은 코덱) | concat demuxer + `-c copy` |
| 코덱 변경(H.264→H.265) | ✕ 재인코딩 | `-c:v libx265` |
| 해상도·비트레이트 변경 | ✕ 재인코딩 | `-vf scale=` / `-b:v` |
| 자막 굽기(burn-in) | ✕ 재인코딩 | 필터 필요 |

원칙: 픽셀을 바꾸면 재인코딩, 안 바꾸면 카피. 카피는 거의 즉시·무손실.

## 코덱·컨테이너 조합

| 코덱 | 용량 | 호환 | 비고 |
|---|---|---|---|
| H.264 (AVC) | 기준 | ◎ 최대 | 웹·범용 기본값 |
| H.265 (HEVC) | ~절반 | △ (라이선스·일부 브라우저) | CCTV 저장 효율, 재생 호환 확인 |
| AV1 | 더 작음 | △ (인코딩 무거움) | 최신, 실시간엔 가속 필요 |
| VP9 | H.265급 | 웹(특히 구글) | |

| 컨테이너 | 용도 |
|---|---|
| mp4 | 웹·범용(H.264와 최대 호환) |
| mkv | 가장 관대(거의 모든 코덱·자막·다중 트랙) |
| ts (MPEG-TS) | 스트리밍 세그먼트·방송 |
| fmp4 | HLS/DASH 저지연 |

## 하드웨어 가속 (다중 스트림 필수)

| 플랫폼 | 디코드/인코드 | 인코더 예 |
|---|---|---|
| NVIDIA | NVENC/NVDEC | `-c:v h264_nvenc` `-hwaccel cuda` |
| Intel | Quick Sync (QSV) | `-c:v h264_qsv` `-hwaccel qsv` |
| 리눅스 범용 | VAAPI | `-hwaccel vaapi -c:v h264_vaapi` |
| 라즈베리파이 | 하드웨어 인코더(v4l2) | dev-iot-raspberry |

- 가속 인코더는 화질·옵션이 소프트웨어(libx264)보다 제약 — 화질 최우선이면 SW, 처리량 최우선(다중 CCTV)이면 HW.
- `-hwaccel`(디코드)과 가속 인코더(`_nvenc` 등)는 별개 — 둘 다 지정해야 풀 가속.

## RTSP 안정성

```bash
ffmpeg -rtsp_transport tcp -timeout 5000000 -i rtsp://user:pass@cam/stream \
       -c copy -f segment -segment_time 600 -strftime 1 ch_%Y%m%d_%H%M%S.mp4
```

- `-rtsp_transport tcp`: UDP 기본은 패킷 손실 → 깨진 프레임. tcp가 안정(약간 지연 증가).
- `-timeout 5000000`: 소켓 I/O 타임아웃(마이크로초, 즉 5초). 구버전(≤7.x 초기)에서 쓰던 `-stimeout`은 2021년 `-timeout`으로 리네임됐고 **FFmpeg 8에서 `stimeout` 별칭이 완전 제거**됨(사용 시 "Unrecognized option 'stimeout'" 에러). 신규 명령은 위처럼 `-timeout` 사용. 서버 listen 모드의 접속 대기는 별개 옵션 `-listen_timeout`(초 단위) — 혼동 주의.
- 재연결: ffmpeg 자체 재연결 옵션은 제한적 — systemd `Restart=always`(dev-linux-ops) 래퍼가 견고. 끊김을 정상으로 간주.
- 인증·URL은 제조사별 상이(Hikvision `/Streaming/Channels/101` 등) — 카메라 문서 확인.
- 서브스트림: 분석용 저해상도(`/102`)로 CPU 절약, 녹화는 메인(`/101`) 카피(실전 케이스).

## 세그먼트 녹화

```bash
-f segment -segment_time 600 -segment_format mp4 -strftime 1 rec_%Y%m%d_%H%M%S.mp4
```

- 10분 세그먼트 + 시간 파일명 → 보존 정책(16일 지난 파일 삭제 배치 — dev-linux-ops cron)·부분 손상 격리·이벤트 클립 추출 용이.
- `-reset_timestamps 1`로 각 세그먼트 독립 재생 가능.

## HLS(웹 스트리밍)

```bash
-f hls -hls_time 4 -hls_list_size 6 -hls_flags delete_segments out.m3u8
```

- 라이브 웹 재생 표준 — 4초 세그먼트 + 슬라이딩 윈도우. 저지연(LL-HLS)은 추가 설정.
- 카피 가능하면 카피(H.264 입력 → HLS 카피) — 재인코딩은 다중 화질(ABR) 필요 시만.

## 옵션 위치 (안티패턴 6)

```
ffmpeg [입력옵션] -i input [출력옵션] output
ffmpeg -ss 60 -i in.mp4 ...      # 입력 앞 -ss: 빠른 키프레임 탐색
ffmpeg -i in.mp4 -ss 60 ...      # 입력 뒤 -ss: 정확하나 거기까지 디코드(느림)
```

진단: ffprobe로 결과 확인 — `ffprobe -v error -show_streams output`으로 코덱·해상도·길이가 의도대로인지.
