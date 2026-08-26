# dev-iot-raspberry evidence — 실증 사례

## 1. Mirai (2016) — 기본 자격증명의 인터넷 규모 청구서 (공개 분석·기소 기록)

- **무슨 일**: 대학생들이 만든 봇넷 — 텔넷 열린 IoT를 스캔해 하드코딩 기본 계정 61쌍 사전 대입, 수십만 대 장악. 2016-09 보안 블로거 KrebsOnSecurity에 620Gbps, 2016-10 DNS 제공자 Dyn에 대규모 DDoS — 트위터·넷플릭스·레딧 등 동시 마비. 소스 공개로 변종(현재도 활동)이 상시 생태계화.
- **구조 교훈**: ① 공격 단가 0(자동 스캔) vs 방어 단가 0(비번 변경) — 그런데도 수십만 대가 뚫린 건 "설정하고 잊는" IoT의 본성 때문 ② 피해자=가해자 구조(내 카메라가 남을 때림) ③ 제조사가 펌웨어를 버린 기기는 영구 취약 — 망 격리(VLAN·게스트망)만이 지속 가능한 방어.
- **홈서버 적용**: CCTV 카메라류는 인터넷 직접 노출 금지 + 별도 망 + 외부 접근은 VPN 단일 관문(Frigate 설계의 보안 전제).

## 2. 저전압 미스터리 — "귀신 들린 파이"의 정체 (공식 문서·커뮤니티 집적)

- **증상의 다양성**: 무작위 재부팅 · USB 장치(SSD·카메라) 간헐 단절 · SD 손상 반복 · 와이파이 불안정 · 성능 저하 — 전부 다른 문제처럼 보이지만 한 원인(전압 강하)의 다른 얼굴인 경우가 커뮤니티 진단의 다수.
- **판정 1줄**: `vcgencmd get_throttled` — 비트 플래그로 기록. 공식 정의(아래 출처): **bit0(0x1) 현재 저전압 · bit1(0x2) ARM 주파수 캡 · bit2(0x4) 현재 스로틀 · bit3(0x8) 소프트 온도 한계 활성**, 상위 비트는 과거 이력 sticky(**bit16(0x10000) 저전압 발생함 · bit18(0x40000) 스로틀 발생함** 등). 흔히 보는 `0x50005`는 "현재 저전압+스로틀 + 과거 저전압·스로틀 이력"의 조합. **0x0이 아니면 전원부터** — 소프트웨어 디버깅은 그 다음(진단 순서가 시간을 산다). (주의: 0x2는 스로틀이 아니라 *주파수 캡*, 실제 스로틀은 0x4다.)
- **흔한 진범**: 폰 충전기(전압 강하 보상 없음) · 얇고 긴 USB 케이블(저항) · USB 허브 없이 SSD+카메라 동시 구동(피크 초과). 처방: 공식 어댑터 + 전력 큰 주변기기는 유전원 허브.

## 3. SD카드 사망 장르 — "어느 날 안 부팅"의 해부 (운용 집적)

- **사망 경로 2종**: ① 쓰기 사이클 소진(셀 마모 — 24시간 로깅·DB·스왑이 가속) ② 정전 중 쓰기로 파일시스템 손상(SD는 전원 보호 캐시가 없다) — 증상은 같다: 부팅 실패·읽기 전용 전락·파일 오염.
- **수명 연장 서열**: tmpfs 로그(log2ram) → 스왑 비활성/최소화 → 쓰기 워크로드 외부화(NAS·SSD) → USB SSD 부팅(상시 서비스의 정답) → 읽기 전용 루트(키오스크) — 워크로드 강도에 비례해 단계 선택.
- **죽음의 전제화**: 어떤 단계든 "이 카드는 죽는다"가 전제 — ① 주기 이미지 백업(dd/rpi-clone) 또는 ② 셋업 자동화 스크립트(재구축 30분) 중 하나는 의무. 둘 다 없는 파이는 "죽으면 고고학"이 된다(설정을 기억하는 사람이 없음).

> 출처 (2026-06 웹 확인, Pi 5/4 기준):
> - **vcgencmd get_throttled 비트 정의** — bit0/1/2/3(현재 상태: 저전압·ARM 주파수 캡·스로틀링·소프트 온도한계) + bit16~19(전원 인가 후 1회 이상 발생 sticky, 재부팅 시 리셋). 임계: 저전압 <4.63V, ARM 캡 >80°C, 강제 감속 >85°C. 라즈베리파이 공식 문서 `https://www.raspberrypi.com/documentation/computers/os.html`(get_throttled 항목) + 공식 포럼 엔지니어 답변으로 교차확인(1차+근접 출처). 검증 명령: `vcgencmd get_throttled`(0x0=정상) / `dmesg | grep -i voltage`(커널 "Undervoltage detected!" 로그).
> - **Pi 5 전원 5.1V/5A(27W) USB-PD** — 공식 제품/데이터시트: `https://www.raspberrypi.com/products/27w-power-supply/` · 제품 브리프 `https://datasheets.raspberrypi.com/power-supply/27w-usb-c-power-supply-product-brief.pdf` (정격·USB-PD 협상 근거. 1차 출처)
> - **Mirai 61개 기본 자격증명·Dyn 공격** — CISA 경보 `https://www.cisa.gov/news-events/alerts/2016/10/14/heightened-ddos-threat-posed-mirai-and-other-botnets` (정부 1차 경보) · 자격증명 목록 분석 CSO Online `https://www.csoonline.com/article/558215/here-are-the-61-passwords-that-powered-the-mirai-iot-botnet.html` · 개요 Wikipedia `https://en.wikipedia.org/wiki/Mirai_(malware)` (소스 코드의 62줄 중 1개 중복 → 61개 고유 자격증명. KrebsOnSecurity ~620Gbps·Dyn 2016-10-21·Jha/White 기소 사실 교차확인)
> - **GPIO 핀당 ~16mA·총 50mA·3.3V 로직** — 라즈베리파이 공식 핀아웃/하드웨어 문서 `https://www.raspberrypi.com/documentation/computers/raspberry-pi.html` 및 커뮤니티 합의(forums.raspberrypi.com)로 교차확인. [확인 필요: Pi 5 공식 데이터시트가 핀당 전류를 명시 수치로 박아둔 단일 표는 못 찾음 — 16/50mA는 역대 모델 공통 보수적 권고치]
> - SD카드 수명 연장(log2ram·USB SSD 부팅·overlayfs read-only) — 라즈베리파이 공식 문서 + 홈랩 커뮤니티 운용 집적.
