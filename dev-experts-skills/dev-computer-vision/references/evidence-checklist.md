# evidence + 출고 전 체크리스트

## 실증·출처

- **Eykholt et al., "Robust Physical-World Attacks on Deep Learning Visual Classification" (CVPR 2018, arXiv:1707.08945)** — 정지 표지판 스티커 적대적 사례(랩 100%·주행 84.8% 오분류). SKILL.md 실전 케이스(단일 출력 맹신의 위험). 1차 출처: <https://arxiv.org/abs/1707.08945> · 발표 PDF: openaccess.thecvf.com CVPR 2018.
- **OpenCV 공식 문서** — 배경 차분(MOG2/KNN)·좌표/배열 규약의 1차 출처. `createBackgroundSubtractorMOG2()`·`createBackgroundSubtractorKNN()` API 확인: <https://docs.opencv.org/4.x/d1/dc5/tutorial_background_subtraction.html>.
- **Frigate 공식 문서** — CCTV NVR + 객체 탐지(OpenCV/TensorFlow) + 녹화·RTSP 리스트림 + Coral EdgeTPU 가속 + MQTT/Home Assistant 연동. 안티패턴 4(기성 우선)의 권장 도구. <https://docs.frigate.video/>.
- **추적 알고리즘**: SORT(Bewley et al. 2016, ICIP, arXiv:1602.00763 <https://arxiv.org/abs/1602.00763>)·ByteTrack(Zhang et al. ECCV 2022, arXiv:2110.06864 <https://arxiv.org/abs/2110.06864>) 논문 — 탐지+추적 조합의 표준.
- 오픈소스 차용 표기: 비전 튜토리얼 다수(색인 인지, 본문 비복사). **역흡수**: "파이프라인이 모델보다 먼저"·움직임 게이트로 추론 절감·시간 일관성 이벤트·Frigate 우선·하드웨어 맞춤 모델 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (비전 파이프라인 출고 시)

- [ ] 기성(Frigate 등) 검토 후 커스텀 범위 확정
- [ ] 움직임/샘플 게이트 (전 프레임 추론 0) — `cv_check.py` 0건
- [ ] 처리 fps ≥ 필요 fps (드롭 0 실측)
- [ ] 신뢰도 임계 용도별 측정 결정 + NMS
- [ ] 모델이 하드웨어에 맞음 (CPU=경량/가속기)
- [ ] 좌표계 변환 명시 (모델→원본, x/y 순서)
- [ ] 이벤트는 N프레임/추적 기반 (단일 프레임 0)
- [ ] 안전 의사결정에 비전 단독 판정 없음 (다중 증거/사람 확인)

## 점검 주기 (부패 중간 — 반기, 모델 생태계)

- 모델·가속기 세대 변화 확인 (경량 모델 정확도 향상 추세)
- 야간·계절 환경 변화에 오탐률 재점검 → 임계·ROI 조정
