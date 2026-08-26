# life-concierge 라우팅 트리거 색인

> 사용자 발화 → 전문가 매핑표. 라우터가 영역 판정에 쓴다. 한 발화가 여러 행에 걸리면 긴급 게이트 우선 → 그다음 주/보조 선정.

## 긴급 게이트 (이 신호면 라우팅 전에 즉시 행동)

| 발화/신호 | 즉시 행동 | 후속 |
|---|---|---|
| "가슴이 아파", "숨이 안 쉬어져", "말이 어눌", "한쪽 마비", "피가 많이" | 119/응급실 | life-emergency |
| "방금 송금했는데 사기", "원격앱 깔았어", "계좌가 털렸어" | 송금은행 지급정지 → 112/1332 | life-fraud-response |
| "협박당해", "스토킹", "위협" | 112 | life-legal |
| "불이", "가스 냄새" | 119/대피 | life-emergency |
| "죽고 싶어", "자해" | 109 / 1577-0199 | life-mental-care |

## 영역별 트리거

| 발화 예 | 주 전문가 |
|---|---|
| 사기, 보이스피싱, 중고나라 사기, 더치트, 에스크로, 환불 안 해줘 | life-fraud-response |
| 접촉사고, 뺑소니, 과실비율, 블랙박스, 보험사 합의, 대물/대인 | life-car-accident |
| 전세, 월세, 등기부등본, 확정일자, 깡통전세, 보증보험, 임대차 | life-real-estate |
| 연말정산, 종합소득세, 공제, 환급, 부가세 | life-tax |
| 사업자등록, 간이과세, 세금계산서, 외주, 프리랜서 3.3 | life-small-business |
| 신용점수, 대출, 금리, 대환, 중도상환, 예적금 | life-banking-credit |
| 비상금, 자산배분, 연금저축, IRP, ISA, 청약, 노후 | life-personal-finance |
| 실손보험, 종신보험, 자동차보험, 보험금 청구, 리모델링 | life-insurance |
| 정부지원금, 근로장려금, 청년정책, 복지로, 바우처 | life-welfare-subsidy |
| 내용증명, 지급명령, 소액소송, 근로기준, 부당해고 | life-legal |
| 운동 시작, 헬스, 3대 운동, 근손실, 자세 | life-fitness |
| 단백질, 다이어트, 칼로리, 식단 | life-nutrition |
| 잠이 안 와, 수면, 카페인, 불면 | life-sleep |
| 번아웃, 스트레스, 무기력, 불안 | life-mental-care |
| 어느 병원, 무슨 과, 건강검진 결과, 2차 소견 | life-medical-navigation |
| 집중이 안 돼, 딴짓, 할 일 관리, GTD | life-productivity |
| 공부법, 암기, 시험 준비, 인강 | life-learning |
| 연봉 협상, 중고 흥정, 계약 협상 | life-negotiation |
| 이직, 이력서, 포트폴리오, 면접, 경력기술서 | life-career |
| 보고서, 이메일, 글쓰기, 블로그 | life-writing |
| 발표, PT, 스피치, 질의응답 | life-speaking |
| 영어 공부, 문서 독해, PR 영어 | life-english |
| 2FA, 비밀번호 관리자, 피싱, 계정 해킹, 백업 | life-digital-security |
| 가전 구매, 노트북 추천, 출시 시기, 중고 시세 | life-smart-buying |
| 여행 일정, 항공권, 숙소 예약 타이밍 | life-travel |
| 요리, 식재료 보관, 자취 요리 | life-cooking |
| 심폐소생술, 응급처치, 재난 대비 | life-emergency |
| 이사, 이삿짐 견적, 전입신고 | life-moving |
| 곰팡이, 누수, 결로, 하자보수, 셀프 인테리어 | life-interior-repair |
| 통신비, 요금제, 알뜰폰, 위약금 | life-telecom-saving |
| 세탁, 청소, 정리, 냄새 제거 | life-cleaning-laundry |
| 중고 판매, 당근 판매, 사진 잘 찍기 | life-resell-secondhand |
| 축의금, 부의금, 경조사 복장, 상조 | life-ceremony |

## 면책 영역 (안내 말미 면책 라벨 의무)

life-legal · life-tax · life-small-business · life-insurance · life-medical-navigation · life-mental-care · life-real-estate(법률 부분) · life-personal-finance(투자 권유 아님).
