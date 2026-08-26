# evidence + 출고 전 체크리스트

## 실증·출처

- **GoF, *Design Patterns: Elements of Reusable Object-Oriented Software* (Addison-Wesley, 1994-10-31)** — 서문/1장의 두 원칙("인터페이스에 프로그램하라", "상속보다 객체 합성을 선호하라")이 23개 카탈로그보다 앞에 있다. 패턴별 구조의 원전. (출처: Addison-Wesley 서지 — 웹 확인)
- **"Design Patterns 15 Years Later: An Interview with Erich Gamma, Richard Helm, and Ralph Johnson" (Larry O'Brien 진행, InformIT, 2009-10-22)** — 세 저자 합동 인터뷰. Singleton을 가장 후회되는 패턴으로 꼽고 DI(의존성 주입)로 대체·카테고리 재구성을 논함. 안티패턴 2의 1차 근거. https://www.informit.com/articles/article.aspx?p=1404056 (URL 응답 확인)
- **Peter Norvig, "Design Patterns in Dynamic Programming" (Object World, 1996-05-05)** — GoF 23개 중 16개가 Lisp/Dylan의 언어 기능(일급 함수·다중 디스패치 등)으로 소멸·단순화됨을 시연. 현대 번역표의 원조 논거. https://norvig.com/design-patterns/ (저자 사이트, URL 응답 확인)
- **FizzBuzzEnterpriseEdition (GitHub `EnterpriseQualityCoding`, 2012-11~)** — 15줄 FizzBuzz를 패턴 수십 층으로 구현한 풍자. 23k+ 스타. 패턴 강박의 공용 어휘. SKILL.md 실전 케이스. https://github.com/EnterpriseQualityCoding/FizzBuzzEnterpriseEdition (URL 응답 확인)
- 오픈소스 차용 표기: 패턴 교육류 스킬 다수(색인 인지, 본문 비복사). **역흡수**: 대부분 GoF 구조 직역 교육 — 번역표·단순 사다리·함정 체크리스트(이름의 색인 가치) 부재가 본 스킬 차별점.

## 출고 전 체크리스트 (구조 설계 출고 시)

- [ ] 변하는 축이 한 문장으로 적혀 있다 (없으면 패턴 도입 금지)
- [ ] 단순 사다리에서 멈춘 지점과 이유 기록
- [ ] 구현체 1개뿐인 인터페이스 없음 (`indirection_probe.py` 참고)
- [ ] 상속 깊이 2단 이내, 변형 축 2개면 조합
- [ ] 변형 추가 시연이 "기존 코드 무수정"으로 통과
- [ ] 선택한 패턴의 함정 체크리스트(situation-map) 점검
- [ ] 패턴 이름이 주석/PR에 기록됨 (색인)

## 점검 주기 (부패 느림 — 연 1회)

- 언어 기능 변화로 번역표 갱신(예: 파이썬 패턴 매칭이 State 번역에 미친 영향류)
- ledger의 과설계/재발명 3회 패턴 → 사다리·표 보강
