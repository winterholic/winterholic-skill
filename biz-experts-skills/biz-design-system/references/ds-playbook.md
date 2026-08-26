# ds-playbook — 거버넌스·기여·버저닝·성숙도 실무 (검증판)

> evidence.md §4 확장. 팀 모델·기여 워크플로우·semver·deprecation·성숙도·채택 지표. 출처 2026-07 웹 검증. 디자인 시스템은 "제품"이다 — 내부 팀이 사용자.

---

## 1. 팀·거버넌스 모델 3종 (Nathan Curtis)

출처(1차): [Team Models for Scaling a Design System (EightShapes)](https://medium.com/eightshapes-llc/team-models-for-scaling-a-design-system-2cf9d03be6a0)

| 모델 | 정의 | 강점 | 약점 | 적합 |
|---|---|---|---|---|
| **① Solitary(단독)** | 한 팀이 만들되 자기 제품 니즈를 우선. 남는 걸 공유. | 승인된 비주얼 언어 기반 프로덕션 코드 제공, 제작팀 비용으로 유지 | 다른 팀 문제를 절반만 해결, 내향적 동기, 채택팀이 커스터마이즈 부담 → 이탈 유발 | 공유할 자산이 이미 있는 팀, 부분 해결로 충분한 조직 |
| **② Centralized(중앙집권)** | 전담팀이 결정·컴포넌트를 조직 전체에 배포. **자기 제품은 안 만듦.** | 포트폴리오 전반에 언어 확산, 특정 제품 편향 없음, 요청 수집·검증 체계 | 실제 제품 제약의 맥락 부족, 제품팀 참여 유도 힘 약함, 존재 증명 압박이 역효과 | 단절된 여러 제품 라인에 일관성·효율이 필요한 조직 |
| **③ Federated(연합)** | 여러 제품팀 대표가 제품 역할을 유지하며 방향을 공동 결정. | 다수 플랫폼에 정당성, 편향 인식↓, 전도사↑, 상호 자율 인센티브 | 의사결정 복잡, 부족(tribe) 충성 vs 시스템 헌신 갈등, 결정 추적 어려움, **강한 중앙 문서화 필수** | 수백 명 디자이너·다수 플랫폼의 대규모 고성능 조직 |

**핵심 통찰**: **"Overlords don't scale"** — 순수 중앙집권 통제는 규모에서 무너진다. 성숙 조직은 협업형으로 이동.
**현실 조합**: 대부분 성숙 시스템은 **연합 기여 + 중앙 코어팀**(hybrid). "연합 팀도 대의에 충분히 헌신하는 중앙 인력이 필요하다 — 그 정성 없이는 살아있는 스타일가이드도 죽은 것처럼 보인다."

---

## 2. 기여(Contribution) 워크플로우

출처: [Defining Design System Contributions](https://medium.com/eightshapes-llc/defining-design-system-contributions-eb48e00e8898), [Why Contributions Matter](https://medium.com/eightshapes-llc/why-contributions-matter-22652d8676c6)

- **기여자 정의**(Curtis): 기여자는 시스템 유지를 본업으로 하는 **코어팀 밖** 인력. 넓은 커뮤니티에서 오는 연합 기여.
- **규모별 처리**: 큰 규모의 작업은 독립 기여로 추진하지 않고 **중앙팀이 조율·수행**. 작은 것(토큰 추가, 버그, 문서)만 커뮤니티 PR로 흡수.
- **표준 절차**: 제안(RFC/이슈) → 트리아지(코어팀이 중복·범위 판정) → 설계 리뷰 → 구현 PR → a11y·토큰 준수 리뷰 → 병합 → 문서·체인지로그.
- **기여 판정 기준(트리아지)**: 기존 컴포넌트의 variant/prop으로 흡수 가능? → 흡수. 정말 새 원자? → 신설. 실험적? → `unstable-` 접두 격리 후 채택률 보고 승격.
- **최근 관점 전환**(Curtis): 중앙 거버넌스 통제 → **공유·재사용 촉진**으로 마인드셋 이동.([Chicago Camps Tent Talks](https://chicagocamps.org/nathan-curtis-from-contribution-to-evolution-charting-the-path-of-design-systems/))

---

## 3. 버저닝(Semver)·브레이킹 체인지·Deprecation

디자인 시스템은 다운스트림(제품 팀)이 의존하는 라이브러리 → **Semantic Versioning** 준수.

- **MAJOR.MINOR.PATCH**
  - MAJOR: 파괴적 변경(토큰 이름 삭제·의미 변경, prop 제거, DOM 구조 변경 등 사용처 수정 강제)
  - MINOR: 하위호환 기능 추가(새 컴포넌트·variant·토큰)
  - PATCH: 하위호환 버그·시각 수정
- **토큰 이름 변경 = 파괴 변경**: 시맨틱 토큰 이름은 사용처 전체에 파급 → 이름 바꾸려면 MAJOR + 마이그레이션 가이드.
- **Deprecation 정책**(권장 흐름):
  1. 신규 토큰/컴포넌트 도입, 구버전은 **삭제 대신 deprecated 표시**. DTCG는 `$deprecated`(문자열로 대체 안내) 지원(token-naming.md §3.2).
  2. 최소 1개 MAJOR 사이클 병행 유지 → 다운스트림 이관 기간 부여.
  3. 체인지로그·마이그레이션 가이드·(가능하면) codemod 제공. Carbon은 v10→v11 대규모 토큰 개편 시 마이그레이션 가이드를 냈다.([Carbon migrating guide](https://carbondesignsystem.com/migrating/guide/design/))
  4. 유예 후 제거.
- **브레이킹 관리 원칙**: 파괴 변경은 몰아서 MAJOR로 배치(잦은 소규모 파괴 금지), 사전 공지, deprecated 경고를 도구(린트)로 노출. Carbon은 `stylelint-plugin-carbon-tokens`로 미사용/폐기 토큰을 린트.([GitHub](https://github.com/carbon-design-system/stylelint-plugin-carbon-tokens))

---

## 4. 성숙한 DS 구조 비교 (공개 문서 기반)

| 시스템 | 토큰 계층·네이밍 | 특징 |
|---|---|---|
| **Material Design 3**(Google) | 3계층 명시: `md.ref.*`(reference) → `md.sys.*`(system) → `md.comp.*`(component). 이름은 일반→구체 순, `system.class.purpose` (예 `md.sys.color.primary`). | Dynamic Color(배경화면에서 팔레트 생성), 컴포넌트는 시맨틱 참조로 자동 테마. 출처 [m3.material.io](https://m3.material.io/foundations/design-tokens/overview) |
| **IBM Carbon** | 역할 기반 시맨틱 토큰(`text-*`, `layer-*`, `background`, `interactive`, `support`). 동일 토큰명이 4개 테마(White/Gray 10/90/100)별로 다른 값에 매핑. | v11에서 토큰·테마·사이즈 네이밍 대개편, 접근성 강화. 린트 플러그인 제공. 출처 [carbondesignsystem.com](https://carbondesignsystem.com/elements/color/tokens/) |
| **Shopify Polaris** | 잘 문서화된 토큰 + 일관된 컴포넌트 API. | 예외적으로 상세한 **콘텐츠 가이드라인**(보이스·톤·문법·에러 문구). 출처 [uxpin 사례집](https://www.uxpin.com/studio/blog/best-design-system-examples/) |
| **Atlassian** | 토큰·거버넌스·기여 모델 공개(공개 DS 중 성숙 사례로 자주 인용). | 상세 스펙은 확인 필요 — 공식 atlassian.design 참조 권장. |

공통점: **예외 없이 시맨틱 계층에서 테마 분기**, 컴포넌트는 원시 직접참조 금지, 파괴 변경은 MAJOR + 마이그레이션 가이드.

---

## 5. 성숙도 모델·채택 지표 (Sparkbox / Ben Callahan)

출처: [Sparkbox Design System Maturity Model](https://sparkbox.com/foundry/design_system_maturity_model_assessment_design_system_evolution), [Design Systems Survey](https://designsystemssurvey.sparkbox.com/2022/)

### 조사 수치(검증)
- **오직 16%**의 응답자만 디자인 시스템 지표를 추적 — 업계 전반 지표 측정률이 낮음.
- **44%**만 거버넌스 모델을 갖췄거나 로드맵을 공유 — 거버넌스 부재가 흔함.
- 에이전시 응답자의 **52%**: "채택 부족"이 클라이언트 DS 실패의 가장 흔한 이유.
- 디지털 제품에서 **더 많이 쓰일수록** 성공으로 인식됨(사내 응답자). 성공으로 인식한 팀은 채택을 문제로 덜 꼽음.

### 실무 채택 지표(추적 대상)
- **채택률/커버리지**: 시스템 컴포넌트로 만들어진 UI 비율, 토큰 참조 비율.
- **우회(bypass)/부채**: 하드코딩된 색·간격 개수, 시스템 밖 자작 컴포넌트 수(=드리프트 신호).
- **침투도(penetration)**: 채택한 팀/제품 수.
- **기여·건강도**: 기여 PR 수, 이슈 처리 시간, deprecated 토큰 잔존율.
- 실행: 코드베이스 정적 분석(하드코딩 grep), Figma 라이브러리 사용률, 린트로 미준수 검출.

### 성숙도 단계(개념)
사후 만들어진 스타일가이드 → 컴포넌트 라이브러리 → 토큰화·거버넌스·채택 관리 → 다플랫폼·자동 파이프라인·조직 문화화. (Sparkbox/Callahan 모델의 단계 명칭 세부는 확인 필요 — 핵심은 "만드는 것"이 아니라 "채택·운영"으로 성숙이 이동)

---

## 6. 실전 체크리스트

**거버넌스 도입 전:**
- [ ] 소유 주체 명확한가(Solitary/Centralized/Federated 중 무엇, 코어팀 존재?)
- [ ] 기여 절차 문서화(제안→트리아지→리뷰→병합→체인지로그)됐나
- [ ] 버저닝 = semver, 파괴 변경 = MAJOR 규칙 합의됐나
- [ ] deprecation 정책(병행 기간·마이그레이션 가이드·codemod)이 있나
- [ ] 채택 지표(하드코딩 수·커버리지·우회 컴포넌트 수)를 실제로 추적하나
- [ ] 문서·예시·사용 가이드가 채택을 지원하나(안 하면 팀들이 자작 → 드리프트)

**"시스템은 제품" 원칙**: 내부 팀이 사용자다. 채택률이 성공 지표. 만들고 방치 = 비싼 장식(evidence.md §4, 안티패턴 5).

---

## 출처
- Nathan Curtis, *Team Models for Scaling a Design System* — https://medium.com/eightshapes-llc/team-models-for-scaling-a-design-system-2cf9d03be6a0
- Nathan Curtis, *Defining Design System Contributions* / *Why Contributions Matter* — eightshapes-llc(Medium)
- Material Design 3, *Design tokens overview* — https://m3.material.io/foundations/design-tokens/overview
- Carbon Design System — https://carbondesignsystem.com/elements/color/tokens/ · migrating guide · stylelint-plugin-carbon-tokens(GitHub)
- Sparkbox Design Systems Survey(2022) & Maturity Model — https://designsystemssurvey.sparkbox.com/2022/ · sparkbox.com/foundry
- 보조: uxpin 사례집, Chicago Camps Tent Talks
