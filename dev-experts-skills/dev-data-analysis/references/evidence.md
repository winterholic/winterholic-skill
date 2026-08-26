# dev-data-analysis evidence — 실증 사례

## 1. Reinhart-Rogoff (2010/2013) — 재현이 무너뜨린 정책 근거 (공개 학술 검증)

- **무슨 일**: "Growth in a Time of Debt"(부채/GDP 90% 초과 시 평균 성장 -0.1%)가 각국 긴축의 학술 인용처였으나, UMass 대학원생 Herndon이 재현 과정에서 발견: ① 엑셀 평균 수식이 알파벳순 첫 5개국 행 누락 ② 특정 연도 선택적 제외 ③ 비표준 가중치. 보정 시 해당 구간 평균 +2.2% — "절벽"이 사라짐.
- **교훈 체계화**:
  1. **재현 요청이 검증의 전부였다** — 원 데이터·계산 공개가 3년 만에야 이뤄졌고, 공개 즉시 무너졌다. 분석 산출물에 데이터 버전+코드 동봉이 기본인 이유.
  2. **수작업 범위 선택의 위험** — 엑셀 드래그든 노트북 숨은 상태든 "눈으로 고른 범위"는 검증 불가. 코드화가 방어.
  3. **새니티 체크 한 줄** — "평균에 들어간 국가 수 = 전체 국가 수" 확인만 했어도. 교차 검증은 사치가 아니라 1줄 보험.

## 2. 유전자명 엑셀 자동 변환 — 도구의 침묵 오염 (학술 집계)

- **무슨 일**: 유전자명 SEPT2(Septin 2)·MARCH1 등이 엑셀에서 날짜(9월 2일·3월 1일)로 자동 변환 — 2016년 조사에서 검토 논문 부속 데이터의 약 1/5에서 오염 발견, 2020년에는 학계가 **유전자명 자체를 개명**(SEPT2→SEPTIN2)하는 항복 선언. 도구의 "친절한" 기본 동작이 데이터를 침묵 오염시킨 사상 최대 규모 사례.
- **실무 번역**: ① CSV를 엑셀로 열어 저장하는 순간 타입 오염 가능(선행 0 소실·날짜 변환·지수 표기) — 원본은 읽기 전용, 가공은 코드로 ② pandas도 `read_csv` 자동 타입 추론이 같은 부류(우편번호가 int로·ID가 float로) — 핵심 식별자는 `dtype=str` 명시 ③ 프로파일 4수의 value_counts가 이런 오염을 잡는 그물이다.

## 3. pandas CoW 전환 — "경고가 사라지고 함정이 침묵화" (버전 경계 실증)

- **무슨 일**: pandas 3.0(2026-01-21 정식 릴리스)에서 Copy-on-Write가 **유일한 모드로 기본화**(`mode.copy_on_write` 옵션 제거 — 끌 수 없음)되며 chained assignment(`df[mask]['col'] = v`)의 동작이 확정 — **항상 원본 미반영**(이전엔 메모리 사정 따라 반영되기도). SettingWithCopyWarning도 제거 — 즉 옛 코드의 "원본 수정 의도" 체인 할당이 경고 없이 무동작이 된다(공식 v3.0.0 whatsnew의 CoW·"Chained assignment" 절에서 확인).
- **전환기 점검**: `grep -rn "\]\[.*\] *=" *.py notebooks/` 류로 체인 할당 후보 수색 → `.loc[조건, 컬럼] = 값` 단일 인덱서로 전환. 부분 DataFrame 작업은 의도를 `.copy()`로 명시.
- **교훈**: 라이브러리 메이저 전환은 "에러 나는 변경"보다 "조용히 달라지는 변경"이 위험하다 — 릴리즈 노트의 behavior change 절을 업그레이드 전 정독(버전 라벨·부패 점검 규율의 근거).

> 출처(웹 확인 2026-06):
> - Herndon, Ash & Pollin, "Does High Public Debt Consistently Stifle Economic Growth?" (Cambridge J. of Economics, 2014; PERI 워킹페이퍼 2013) — 1차 재현 논문. 누락 5개국(Australia·Austria·Belgium·Canada·Denmark)·-0.1%→+2.2% 수치 원본. 사건 요약은 Retraction Watch(2013-04-18)가 신뢰도 높은 2차 정리.
> - Ziemann, Eren & El-Osta, "Gene name errors are widespread in the scientific literature" (Genome Biology, 2016) — 부속파일 약 20% 오염의 1차 출처. 후속 "Gene name errors: lessons not learned"(Abeysooriya et al., PLOS Comput. Biol., 2021)가 2014–2020 재조사. HGNC 27개 유전자 개명(MARCH1→MARCHF1, SEPT2→SEPTIN2)은 2020년 Nature Genetics 가이드라인 — HGNC가 1차 권위.
> - pandas 공식 v3.0.0 whatsnew(release: 2026-01-21) + PDEP-7(Copy-on-Write) — CoW 기본·유일 모드화, SettingWithCopyWarning/chained assignment 제거의 1차 출처. pandas 3.0이 정식 릴리스되어 "보급 확인 필요" 해소(다만 사내 환경의 실제 채택 버전은 프로젝트별 확인).
