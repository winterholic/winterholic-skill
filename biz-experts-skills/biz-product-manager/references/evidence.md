# biz-product-manager — evidence & 출처 (검증판)

> SKILL.md의 안티패턴·프레임을 뒷받침하는 실증·심화. 출처는 2026-06-30 웹 검증. 1단계 참조.

## 목차
1. 빌드트랩(build trap) 진단 신호
2. feature factory 12신호 (John Cutler)
3. Cagan 4대 리스크 심화
4. output vs outcome
5. RICE 정확한 정의
6. "64% 기능 미사용" 통계의 진실 (중요 교정)
7. 출처

## 1. 빌드트랩 진단 신호 (Melissa Perri)
조직이 "고객 가치"가 아니라 "기능 출시"를 성공으로 측정할 때 빠지는 함정. 신호: 로드맵이 날짜별 기능 목록(문제·지표 없음) · "올해 N개 출시"가 목표 · 출시 후 성과 미측정 · PM이 프로젝트 매니저로 전락 · "왜 만드나"에 "요청이 들어와서".

## 2. feature factory 12신호 (John Cutler, 2016)
대표 신호: ① 출시 후 영향 측정 안 함 ② 롤백/제거가 없음 ③ "속도(velocity)"가 유일 지표 ④ 디스커버리 부재 ⑤ 기능을 "완료/미완료"로만 추적 ⑥ 성공=일정 준수. (전체는 원문)

## 3. Cagan 4대 리스크 (제품 발견에서 먼저 검증)
| 리스크 | 질문 | 책임 |
|---|---|---|
| 가치(Value) | 살/쓸 이유가 있나 | PM |
| 사용성(Usability) | 쓸 줄 아는가 | 디자이너 |
| 실현성(Feasibility) | 만들 수 있나 | 테크리드 |
| 사업성(Viability) | 사업/법무/마케팅/재무가 받아들이나 | PM |
가장 흔한 실패 = **가치 리스크** 미검증("잘 만들었는데 아무도 안 쓰는" 제품).

## 4. output vs outcome
- output: 출시 기능 수·코드량·스프린트 완료율 → 활동량.
- outcome: 활성화·리텐션·전환·NRR → 행동 변화.
- impact: 매출·LTV·시장점유 → 사업 결과.
PM은 outcome 책임. 기능마다 "어떤 outcome을 얼마나" 가설을 못 박고 출시 후 확인.

## 5. RICE 정확한 정의 (출처: Sean McBride, Intercom)
RICE = (Reach × Impact × Confidence) ÷ Effort. Impact 척도 {Massive 3·High 2·Medium 1·Low 0.5·Minimal 0.25}; Confidence {100/80/50%}; Effort = person-months. Confidence가 추측 방지 장치(데이터 없으면 50%).

## 6. "기능의 64%가 거의/전혀 안 쓰인다" 통계의 진실 (중요 교정)
- 흔히 "Standish CHAOS Report"로 인용되지만 **틀린 출처(오귀속)**다.
- 실제 출처: **Jim Johnson(Standish Group 회장)의 2002년 키노트 "ROI, It's Your Job"**, 제3회 XP 국제 컨퍼런스(이탈리아 사르데냐 알게로 Alghero, 2002-05-26~29). CHAOS Report가 아니다.
- 수치(검증): Never 45% / Rarely 19%(합 64%) / Sometimes 16% / Often 13% / Always 7%. 45/19 분할은 복수 2차 출처(Mike Cohn, fairness.coop의 원 도표 복원, ResearchGate 도표)에서 일치 확인. 현장 참석자 Martin Fowler의 XP2002 후기도 "45% never / 20% often+always"로 정합. (원 슬라이드 자체는 미아카이브 — 수치는 위 2차 출처로 교차확인.)
- **결정적 한계**: 표본이 **내부용 앱 4개뿐**(서로 다른 회사), 상용 제품 없음. 방법론 미공개. "모든 소프트웨어"로 일반화하는 게 흔한 오류. (Standish의 후속 2010 보고서는 "1996년 100개 커스텀 앱" 연구를 별도로 거론 — 출처 혼선 주의.)
- 따라서 인용 시: "Jim Johnson 2002 XP 키노트(내부앱 4개 표본, 일반화 한계)"로 표기하고 방향성 근거로만 사용.

## 6b. 우선순위 프레임 심화 (→ 실전 표는 `prioritization-playbook.md`)
프레임별 선택 기준·산정표·지표 트리·워크숍 진행법은 별도 파일로 분리했다.
- **RICE 상대 순위의 본질**: Reach 큰 기능이 아니라 (Impact×Confidence)/Effort가 높은 기능이 이긴다. Confidence는 데이터 없는 아이디어를 걸러내는 장치(50% 이하는 프로젝트가 아니라 발견 대상).
- **Kano의 시간 축**: delighter는 몇 년 뒤 must-be로 하락(decay) — 차별화 기능은 유효기간이 있다. 정기 재분류 필요.
- **WSJF의 결론**: 작고(JobSize↓) 지연비용 큰(CoD↑) 일부터 — 큐잉이론상 총 지연비용 최소. 큰 조직 정렬용.
- **MoSCoW의 Must≤60% 규칙**: Must가 100%면 안전마진 0. DSDM 권고는 Must ≤ 총 노력 60%.

## 7. 출처 (검증)
- Marty Cagan, *INSPIRED* 2판 (Wiley, 2017) / *EMPOWERED* (w/ Chris Jones, Wiley, 2020), SVPG. https://www.svpg.com/books/
- Melissa Perri, *Escaping the Build Trap* (O'Reilly, 2018). https://melissaperri.com/book
- Sean McBride, "RICE: Simple prioritization for product managers" (Intercom, 2018-01-05). https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
- John Cutler, "12 Signs You're Working in a Feature Factory" (2016-11-17). https://cutle.fish/blog/12-signs-youre-working-in-a-feature-factory/
- "64%" 통계 검증·반론: Mike Cohn, "Are 64% of Features Really Rarely or Never Used?" https://www.mountaingoatsoftware.com/blog/are-64-of-features-really-rarely-or-never-used (원 출처가 Jim Johnson 2002 XP 키노트·내부앱 4개임을 Standish에 직접 확인)
- 45/19/16/13/7 분할 도표 출처: ResearchGate "Features use presented by Standish Group at the XP 2002 conference" https://www.researchgate.net/figure/Features-use-presented-by-Standish-Group-at-the-XP-2002-conference_fig2_221186023 · Martin Fowler, "The XP 2002 Conference"(현장 후기, 2002-07) https://martinfowler.com/articles/xp2002.html
- Eric Ries, *The Lean Startup* (Crown Business, 2011) — MVP 정의. ISBN 978-0307887894.
