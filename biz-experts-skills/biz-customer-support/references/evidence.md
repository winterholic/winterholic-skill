# biz-customer-support — 운영 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 웹 검증, 2026-07-01 심화(교차검증). 1차 우선. 실무 절차는 `playbook.md` 참조.

## 1. 정전 소스 (정확)

- **HBR "Stop Trying to Delight Your Customers"** — ⚠️ **Dixon, Freeman, Toman(CEB), 2010-07/08, R1007L**. 75,000+ 상호작용 조사: delight(기대 초과)는 충성도에 거의 무영향, 핵심은 **노력(effort) 감소**. https://hbr.org/2010/07/stop-trying-to-delight-your-customers
- **The Effortless Experience** — Dixon, Toman, **DeLisi**(CEB), Penguin Portfolio 2013. CES v2.0 제시. https://www.penguinrandomhouse.com/books/312730/the-effortless-experience-by-matthew-dixon/
- **HBR "Kick-Ass Customer Service"** — Dixon·Toman·DeLisi, 2017-01/02. "Controllers"(전체 rep의 ~15%)가 문제 해결 최상위 프로필 → 채용·코칭으로 확산. https://hbr.org/2017/01/kick-ass-customer-service
> ⚠️ 교정: DeLisi는 **2013 책 + 2017 논문** 공저자이지 **2010 원논문 저자 아님**(2010 논문=Dixon/Freeman/Toman). 이 셋을 뭉뚱그려 인용 금지.

### Effortless Experience 핵심 수치 (교차검증)
- ✅ **"고노력(high-effort) 경험을 한 고객의 96%가 더 비충성적(disloyal)이 됨 vs 저노력은 9%"** — CEB 연구. 2개 독립 2차 소스(Qualtrics, chiefcustomerofficer.io)에서 동일 수치 교차확인. 단 CEB 1차 원문 PDF 직접 대조는 이번에 네트워크 접근 불가로 **미완**(확인 필요: 원 표본·정의). https://www.qualtrics.com/experience-management/customer/customer-effort-score/
- **고노력의 4대 신호(CEB)**: ①채널 전환(email→전화→SNS) ②정보 반복 진술 ③상담원 이관(transfer) ④기계적·일반적(generic) 응대. → 이 4개를 줄이는 것이 CES 개선의 실전 레버.
- **Next Issue Avoidance(NIA, 차기이슈 회피)**: 이번 문의만 닫지 말고 "곧 이어질 후속 문의"를 선제 예방(예: 배송 지연 안내 시 반품 정책도 함께). CEB 프레임. — 재문의를 구조적으로 줄이는 핵심 개념.
- ⚠️ "delight 무용" 과장 금지: 원 취지는 "delight의 ROI가 effort 감소보다 낮다"이지 "친절 불필요"가 아님. effort 감소가 **필요조건**, 공감은 그 위의 승수.

## 2. 지표 (관계와 함정)

- **CES 두 버전 — 혼용 금지**:
  - v1.0(CEB 2010): "이 문제 해결에 당신이 들인 노력은?" 1~5 점(노력 척도, 높을수록 나쁨).
  - **CES v2.0(2013)**: "[회사]가 내 문제 처리를 쉽게 해줬다" 7점 **동의 척도**(높을수록 좋음). 현 벤치마크 표준형.
- **FRT/AHT/TTR/FCR/CSAT/CES** 정의·함정은 `playbook.md`의 지표 대시보드 절 참조.
- **FCR 양호 벤치마크 ~70~80%**(채널·업종별 상이, 확인 필요). https://www.intercom.com/learning-center/customer-service-metrics
- **FRT 벤치마크(Zendesk/업계 참고, 확인 필요)**: 라이브챗 강자 ~40초·업계평균 ~2분 / 이메일 상위권 <4시간·평균 7~10시간 / SNS 기대 ~1시간·평균 4~5시간. 채널별 기대가 다름 — 단일 SLA 금지. https://www.zendesk.com/blog/first-reply-time/
- **디플렉션(self-service deflection)**: 진짜 해결+후속 문의 없음일 때만 카운트(실질 10~30%, 성숙 시 30~50%). KB 페이지뷰≠디플렉션.

## 3. 교정 (문서화된 함정)

⚠️ **속도 전용 지표는 CEB가 명시한 함정** — 원논문이 "문제 해결에 집중, 속도 아님" 명시. FRT/AHT만 최적화하면 미해결 빠른 종료→FCR·CES·재문의 악화(안티패턴 1).
⚠️ **CSAT ≠ 충성도 예측** — CEB 결론상 재구매·확대 예측력은 **CES가 CSAT/NPS보다 강함**(특히 서비스 상호작용 맥락). CSAT는 만족의 스냅샷, 충성도 대리지표 아님.
⚠️ **Deflection ≠ "티켓 회피"** — 답을 못 찾아 이탈한 것을 디플렉션으로 세면 부풀림. 후속 문의·이탈률로 검증.
⚠️ **매크로/봇 = 효율 도구이지 응대 대체 아님** — 정보성(refund 정책 등)엔 유효, 행동·감정 케이스엔 역효과.

## 4. 출처

- Dixon·Freeman·Toman(HBR 2010, R1007L). · Dixon·Toman·DeLisi, *The Effortless Experience*(Penguin 2013) + HBR "Kick-Ass Customer Service"(2017). · CES 96%/4대 신호(Qualtrics 교차확인). · Intercom·Zendesk 지표 벤치마크(업계 참고, 확인 필요).
