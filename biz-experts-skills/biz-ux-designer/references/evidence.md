# biz-ux-designer — 원전 & 출처 (검증판)

> SKILL.md 보강. 출처 2026-06-30 웹 검증. 1단계 참조.

## 1. 니엘슨 10 휴리스틱 (Nielsen-Molich, 1994 확정; 2020 설명 갱신)
1.시스템 상태 가시성 2.시스템-현실 일치 3.사용자 통제·자유 4.일관성·표준 5.에러 예방 6.회상보다 인식 7.유연성·효율 8.심미·최소주의 9.에러 인식·진단·회복 10.도움말·문서. https://www.nngroup.com/articles/ten-usability-heuristics/

## 2. 노먼 6원칙 (*DOET* 개정판 2013)
어포던스·**시그니파이어(2013판 추가 개념)**·매핑·피드백·제약·개념모델. ⚠️ affordance(가능성) ≠ signifier(지각 단서) — 혼동 금지.

## 3. 응답시간·기타 법칙
- NN/g 3한계: 0.1s(즉각)·1s(흐름 유지)·10s(주의 한계). https://www.nngroup.com/articles/response-times-3-important-limits/
- **Fitts(이동 시간, 운동)** vs **Hick-Hyman(선택 시간, 결정)** — 혼동 금지. 1차: Paul Fitts(1954, *J. Exp. Psychol.* 47(6):381, DOI 10.1037/h0055392); Hick(1952)·Hyman(1953). ISO 9241-210:2019(인간중심 상호작용 설계 표준).

## 4. 실전 케이스 — 하와이 미사일 오경보 (2018-01-13) ⚠️ 교정 (1차 출처 확정)
오경보 8:08 발령, 정정 메시지 8:45 — **38분 13초** 경과. **주 보고서(Oliveira 내부조사, 하와이 DoD 2018-01-30) 확정 사실**: ① 직원은 "test missile alert"와 "missile alert"라는 **유사 메뉴 항목 중 실제 경보를 선택**했고(주정부 spokesman 확인), ② **본인은 실제 공격이라 100% 확신**한 상태였다(다른 5명은 훈련임을 인지). 즉 "단순 오클릭"이 아니라 **상황 인지 실패 + 안전장치 부재**의 복합. **널리 퍼진 "2개 항목 드롭다운 스크린샷"은 주정부가 부인한 재현 이미지** — "정확히 2개짜리 드롭다운"으로 단정 금지. 보고서 원인 = **불충분한 관리통제 + 부실한 SW 설계 + 인적 요인**(확인 화면은 있었으나 그냥 통과). 교훈: 비싼 실수가 한 번의 선택으로 가능하면 인터페이스를 고쳐야(에러 예방, 니엘슨 #5).
> 근거(1차): Oliveira 내부조사 보고서(하와이 DoD, 2018-01-30). FCC 예비/최종 보고서(2018, docs.fcc.gov DOC-348923A1·DOC-350119A1). NN/g 에러 예방 https://www.nngroup.com/articles/error-prevention/

## 5. 노먼 7단계 행동 모델 (Seven Stages of Action)
사용자가 목표를 실행하는 인지 사이클 — UX 실패는 대개 두 "간극"에서 난다.
- **목표 → 실행(execution) 3단계:** ①목표 형성 ②의도·행동계획 수립 ③실행. **실행의 간극(gulf of execution)** = "내가 원하는 걸 이 UI로 어떻게 하지?"를 모를 때. 시그니파이어·좋은 매핑·제약으로 좁힌다.
- **평가(evaluation) 3단계:** ④세계 상태 지각 ⑤해석 ⑥목표와 대조 평가. **평가의 간극(gulf of evaluation)** = "방금 내 행동이 먹혔나?"를 모를 때. 피드백·가시성(니엘슨 #1)으로 좁힌다.
- 실전: 어떤 화면이 "어렵다"면 두 간극 중 어디서 막히는지부터 진단 — 실행 간극이면 발견성 문제(시그니파이어), 평가 간극이면 피드백 문제.
> 근거: Don Norman, *DOET* 개정판(2013) 2장. https://www.nngroup.com/articles/actions-not-buttons/(관련 개념)

## 6. 플로우·인터랙션 설계 원칙 (실무)
- **진행성 노출(progressive disclosure):** 기본은 단순, 고급은 접어두기 — 니엘슨 #7·#8 동시 충족. https://www.nngroup.com/articles/progressive-disclosure/
- **점진적 관여(progressive engagement):** 가입·온보딩에서 정보를 한 번에 다 받지 말고 가치를 보여준 뒤 필요할 때 요청(마찰 최소화).
- **에러 예방 위계(강→약):** 제약(불가능하게) > 인라인 검증 > 위험 액션 분리 > 확인/재인증 > undo. 확인 다이얼로그 남발은 무시(경보 피로)를 부르니 비가역·고비용에만.
- **폼 설계:** 필드 최소화·논리적 그룹화·인라인 검증·명확한 에러 위치·자동저장. 라벨은 필드 위(상단 정렬)가 완료 속도 유리(확인 필요, Baymard/NN/g 폼 연구).
- **모바일 인터랙션:** 엄지 도달 범위(thumb zone)·최소 터치 타깃 44×44pt(iOS HIG)·48dp(Material). 파괴 액션은 실수 탭 방지 위해 도달 쉬운 곳 피하기.

## 7. 출처
- Don Norman, *The Design of Everyday Things* 개정판(Basic Books, 2013) — 어포던스/시그니파이어/7단계 행동 모델.
- Jakob Nielsen, "10 Usability Heuristics"(NN/g, 1994). · Alan Cooper, *About Face* 4판(2014, goal-directed design).
- 슬립/실수 구분·심각도 등급·실전 위반 예: `heuristics-playbook.md` 참조.
