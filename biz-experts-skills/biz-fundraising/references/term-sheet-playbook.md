# biz-fundraising — 텀시트·캡테이블·단계별 지표 실전 (신설)

> evidence.md의 조항 정의를 "협상 실무 + 단계별 눈높이"로 확장. 법적 조항은 반드시 변호사 검토. 출처 2026-07 검증, Cooley/Carta 등 1차 우선.

---

## 1. 텀시트 2버킷 — 협상 우선순위 (Venture Deals, Feld & Mendelson 2019)

밸류에이션만 보다 통제·경제 독소조항을 놓치면 나중에 창업자가 갉인다.

### 경제권 (누가 얼마 가져가나)
| 조항 | 창업자 친화 표준 | 독소 신호 |
|---|---|---|
| 청산우선(liquidation pref) | **1x non-participating** | 2x+·participating(double dip) |
| 참가(participation) | non-participating | participating(우선 회수 후 잔여도 배분) |
| 반희석(anti-dilution) | broad-based weighted average | **full ratchet**(창업자 적대) |
| 옵션풀 | 라운드 후(post) 설정 협상 | pre-money 풀 = 희석이 창업자에게(#1 숨은 레버) |
| pay-to-play | 상황별 | — |

### 통제권 (누가 결정하나)
- 이사회 구성, 보호조항(protective provisions), drag-along.

### 청산우선 시장 표준 (Cooley Q2 2025, 1차 확정)
**1x = 98% / non-participating = 95%**. 2025 분기별로 1x 94~98%·non-participating 95~97% 일관. → "1x non-participating이 표준"은 데이터로 뒷받침됨.

---

## 2. SAFE — post-money의 함정 (YC)

- 2013말 도입(Carolynn Levy), **2018 post-money SAFE로 전환**(누적 SAFE 간 지분 계산 불가 문제 해결, pre-money 폼 제거).
- 변형: Cap-no-Discount / Discount-no-Cap / Uncapped-MFN (+ Pro Rata Side Letter).
- ⚠️ **post-money SAFE는 누적 시 희석이 거의 전부 창업자에게** 간다. cap이 높다고 "공짜"가 아니며, SAFE는 부채가 아니다. 여러 장의 SAFE를 쌓기 전에 **총 희석을 캡테이블로 시뮬레이션**하라(dilution.py 활용). (경고 근거: Pillar Legal "Post-Money SAFE Risks for Founders" 2023.)

---

## 3. 희석·캡테이블 산수 (Carta)
- `post = pre + 투자액`
- `투자자 지분% = 투자액 ÷ post`
- `창업자 신규% = 기존% × (pre ÷ post)`
- 반희석 broad-based 공식: `CP2 = CP1 × (A+B)/(A+C)` (다운라운드에만 트리거).
- **옵션풀 셔플(Feld/Mendelson)**: 투자자가 풀을 pre-money로 만들게 하면 희석이 창업자에게만 실림 — 표준 협상 포인트.

---

## 4. 단계별 투자자 눈높이 (2024~2025 벤치마크, 시장 요약 — "확인 필요")

숫자는 시장 상황·섹터로 크게 변동. 절대 상수 아님. (출처: SVB State of the Markets, Zeni, 각종 2025~2026 벤치 집계.)

| 단계 | 통상 조달액(US SaaS) | 통상 밸류 | 트랙션 눈높이 |
|---|---|---|---|
| **Seed** | ~$1.5~5M (중앙 $2.5~3.2M) | ~$10~20M (중앙 $14~17M) | MVP + 실사용 피드백, ~$300~500K ARR, 100~200% YoY, CAC/LTV/burn 이해 |
| **Series A** | ~$10~20M (중앙 ~$12M) | — | ~$1~3M+ ARR(중앙 A가 $2.5M ARR로 상승), 2~3x YoY, NRR >110%, CAC payback <12개월, burn multiple <1.5x |
| **Series B** | — | ARR의 ~8~15x 밸류 | ~$10~20M ARR, 반복 가능한 세일즈, 확장(세그먼트/지역), 효율적 성장 |

**핵심 시프트(2024~)**: 속도만으로 안 됨 → **단위경제·획득 효율·흑자 경로**를 본다. "burn에 raise하지 말고 burn에 grow해라"(SVB). 상세 지표는 finance-fpa 참조.

---

## 5. 교정
- **밸류 높고 나쁜 텀(2x participating + full ratchet + 큰 pre-money 풀) < 낮아도 클린 텀(1x non-participating).**
- ⚠️ 반희석 broad-based/full-ratchet 채택 비율, 풀랫쳇 와이프아웃 명명 사례는 공개 집계 부족 — 1차 확인 필요.
- 단계별 숫자는 벤치마크지 통과선 아님. 섹터(수직 SaaS vs 소비자)로 크게 갈림.

---

## 6. 출처
- Feld & Mendelson *Venture Deals* 4판(2019) https://venturedeals.com/ · YC SAFE https://www.ycombinator.com/documents · NVCA 모델 https://nvca.org/model-legal-documents/ · Cooley Q2 2025 Venture Financing Report(1차) · Carta https://carta.com/learn/startups/equity-management/cap-table/ · 단계 벤치: SVB/Zeni/Pitchwise 2025~2026 집계("확인 필요"). **모든 조항 변호사 검토.**
