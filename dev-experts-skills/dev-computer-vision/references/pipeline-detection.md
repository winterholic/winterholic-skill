# 파이프라인·탐지 — 게이트·모델·NMS·추적·좌표·Frigate (SKILL.md 비중복)

## 움직임 게이트 (배경 차분 — 추론량 절감)

```python
# 가벼운 게이트: 변화 있는 프레임만 무거운 모델로
backsub = cv2.createBackgroundSubtractorMOG2()
mask = backsub.apply(frame)
motion = cv2.countNonZero(mask) > MOTION_PIXELS   # 임계 픽셀 이상 변화
if motion:
    run_detection(frame)   # 여기만 무거운 추론
```

- MOG2/KNN 배경 차분은 OpenCV 내장·CPU 가벼움. 야간·조명 변화·바람(나뭇잎)에 오작동 → ROI 한정 + 최소 영역 임계로 완화.
- 게이트의 효과: 주차장 CCTV는 99% 정지 → 추론 1/100. 안티패턴 1의 핵심 처방.

## 탐지 모델 선택표 (하드웨어 기준)

| 환경 | 모델 | 비고 |
|---|---|---|
| GPU 있음 | YOLO 중대형·RT-DETR류 | 정확도 우선 가능 |
| CPU만 | YOLO-nano/small·MobileNet-SSD | 해상도 다운스케일 병행 필수 |
| 엣지 가속기(Coral TPU) | TPU 최적화 모델(Frigate 권장) | 저전력·저가·CCTV 적합 |
| 라즈베리파이 | 경량 + 가속기(파이는 dev-iot-raspberry) | CPU 단독은 비현실적 |

- 정확도-속도는 직접 거래 — 실시간(드롭 0)이 정확도보다 우선인 경우가 CCTV에선 흔하다(안티패턴 5).
- 사전학습(COCO 80클래스)으로 충분한지 먼저 — 차량·사람은 기본 클래스. 특수 객체만 파인튜닝(dev-ml-basics).

## NMS·중복 박스

- Non-Max Suppression: 같은 객체에 겹친 박스를 IoU 임계로 1개만 — 대부분 모델/라이브러리 내장(중복 알림 방지).
- 신뢰도 임계와 NMS 임계는 별개 다이얼 — 전자는 "탐지 여부", 후자는 "겹침 제거".

## 추적(tracking) — 시간 정보

```
탐지(무거움, N프레임마다) + 추적(가벼움, 사이 프레임) = 실시간 + 궤적
```

- 추적기(ByteTrack·SORT류)가 객체에 ID 부여 → 프레임 간 같은 객체 연결 → 궤적·속도·정지 판정 가능.
- 이벤트는 궤적에서: "충돌" = 차량 궤적이 외벽 ROI 진입 + 급감속/정지(안티패턴 6). 단일 프레임 박스가 아니라 ID의 시간 행동.

## 좌표 변환 (안티패턴 3 상세)

```python
# 모델 입력(리사이즈/정규화) -> 원본 해상도
# 정규화 출력(0~1): x_px = x_norm * orig_w
# 리사이즈 출력: x_orig = x_resized * (orig_w / model_w)
# OpenCV 배열은 frame[y, x] (행=y 먼저), 좌표 튜플은 보통 (x, y) - 혼동 주의
```

- ROI(관심 영역: 주차구역·외벽선)는 원본 해상도 픽셀로 정의 — 박스와 같은 좌표계여야 진입 판정이 맞다.
- 카메라 각도·왜곡(어안)이 크면 좌표 정확도 저하 — 필요 시 캘리브레이션(과한 경우가 많음, 확인).

## Frigate 연동 (기성 우선 — 안티패턴 4)

- Frigate가 제공: RTSP 수신·움직임 게이트·객체 탐지(Coral 가속)·녹화·이벤트 클립·MQTT/HA 연동·웹 UI.
- 커스텀 위치: Frigate 이벤트(객체 감지)를 받아 **특수 판정**(외벽 충돌 궤적)을 추가하는 후처리 — Frigate가 못 하는 도메인 로직만.
- RTSP 입력·DVR 연동은 dev-media-ffmpeg, 알림은 dev-bot-building, 이벤트 멱등은 dev-event-driven — Frigate가 허브, 나머지는 위성.
