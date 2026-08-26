# evidence + 출고 전 체크리스트

## 실증·출처

- **Therac-25 (1985–87)**: Leveson & Turner, "An Investigation of the Therac-25 Accidents" (IEEE Computer, 1993) — SKILL.md 실전 케이스의 원 출처. 경쟁 조건 미검증·재사용 코드 맹신·간헐 실패 보고 묵살의 3중 실패. 소프트웨어 안전 문헌의 표준 교본.
- **Google 플레이키 데이터**: Google Testing Blog "Flaky Tests at Google and How We Mitigate Them" (2016) — 구글 내부 테스트의 **약 1.5%가 플레이키**, 플레이키의 존재만으로 개발자가 진짜 실패도 재실행으로 넘기게 됨을 보고(확인 필요: 원문 수치 재대조). "재시도 금지가 기본" 정량 기준의 근거.
- **테스트 피라미드**: Mike Cohn 원전(*Succeeding with Agile*) + Fowler "TestPyramid"·"Practical Test Pyramid"(martinfowler.com, Ham Vocke) — 층 비율·역삼각형 비용의 표준 출처.
- **테스트 더블 분류**: Meszaros, *xUnit Test Patterns* — Dummy/Stub/Fake/Spy/Mock 5분류 원전. Fowler "Mocks Aren't Stubs"가 입문판.
- **"테스트는 결함의 부재를 증명 못 한다"**: Dijkstra, "Notes on Structured Programming" (1970) — 한계 섹션의 출처.
- 오픈소스 차용 표기: trailofbits/property-based-testing(VoltAgent 색인 — 속성 기반 테스트는 본 스킬 범위 외로 두되 존재를 인지, 수치 알고리즘 검증 시 hypothesis 도입 검토 메모), alirezarezvani api-test-suite-builder(라우트 스캔→스위트 생성 접근 참고, 본문 비복사). **역흡수**: 두 소스 모두 patch 위치 함정·이름 중복 침묵 증발·플레이키 3대 원천 분류 부재 → 본 스킬 안티패턴 2·3·4의 차별점.

## 출고 전 체크리스트 (테스트 추가·수정 시)

- [ ] 새 테스트가 **실패하는 것을 한 번 봤다** (구현을 잠깐 깨뜨리거나 기대값을 틀리게 — red 확인)
- [ ] 테스트명이 행동_조건_기대를 말한다 (실패 메시지만으로 진단 가능)
- [ ] AAA 구분이 보인다 / Act는 1줄
- [ ] mock은 프로세스 경계만 — 내부 호출 횟수 단언 없음
- [ ] patch 경로가 "사용되는 곳" 기준 (의심되면 일부러 깨뜨려 확인)
- [ ] time.sleep 없음 · datetime.now() 직접 비교 없음 (`test_smells.py` 0건)
- [ ] 테스트 간 공유 가변 상태 없음 (단독 실행과 전체 실행 결과 동일)
- [ ] parametrize 케이스 5개+ 면 id 부여
- [ ] 스위트 10초 초과 시 `--durations=10`으로 범인 확인·격리(slow 마커)
- [ ] 버그 수정이면 그 버그의 회귀 테스트가 먼저 추가됨

## 점검 주기 (부패 느림 — 연 1회)

- pytest 메이저 업과 pytest-asyncio 권장 방식 변화만 확인. **현재 pytest 9.x**(9.0.3/9.1.0, 2026 — docs.pytest.org/changelog): `PytestRemovedIn9Warning`이 기본 에러로 승격, Python 3.9 지원 제거 — 8.x→9 업그레이드 시 deprecation 청소 필요. coverage.py 7.14.x(coverage.readthedocs.io, 2026-05) / pytest-cov 7.1.0(2026-03, coverage ≥7.10.6 요구).
- ledger에서 "테스트가 있었으면 잡았을" 삽질 3회 패턴 → 선정 휴리스틱·체크리스트에 반영
