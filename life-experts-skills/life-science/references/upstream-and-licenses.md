# 원본과 라이선스

- 원본: `https://github.com/K-Dense-AI/scientific-agent-skills`
- 로컬 경로: `~/.claude\imported-sub-skills\scientific-agent-skills`
- 고정 commit: `330c8e764435a731eff571e3efdda70b363d0792`
- 확인일: 2026-09-19
- 카탈로그: 원본 `docs/skills.md` (166종)

## 해석 원칙

원본 저장소 루트 `LICENSE.md`는 MIT이며 K-Dense Inc.의 저작권 고지와 허가문을 복제물 또는 상당 부분에 포함하라고 요구한다. 그러나 원본 README는 각 스킬의 `SKILL.md`에 적힌 개별 라이선스를 별도로 확인하라고 명시한다.

현재 체크아웃 166종의 frontmatter에는 MIT 계열뿐 아니라 BSD, Apache, GPL, CC, 비상업 라이선스, Proprietary, Unknown, 누락이 함께 있다. 따라서 아래처럼 처리한다.

| 행동 | 기본 정책 |
|---|---|
| 로컬에서 스킬을 읽어 연구 절차를 보조 | 선택한 스킬의 라이선스·호환성·데이터 경계를 확인한 뒤 사용 |
| 답변에 스킬 이름과 출처를 밝힘 | 원본 URL, commit, 개별 스킬 이름·버전을 기록 |
| 원본 파일을 공개 저장소에 복사 | 기본 금지. 개별 라이선스와 고지 파일을 확인한 별도 배포 작업에서만 허용 |
| Unknown·Proprietary·NC 스킬 재배포 | 하지 않는다. 링크만 제공 |
| GPL·CC·BSD·Apache 스킬 재배포 | 라이선스 전문·고지·소스 제공 등 해당 조건을 별도 검토하기 전에는 하지 않는다 |

`winterholic-skill`에는 이 원본 트리를 싣지 않는다. 로컬 동기화 스크립트의 denylist가 `imported-sub-skills/scientific-agent-skills` 전체를 차단한다. 공개 가능한 것은 독자 작성한 라우터와 이 출처 안내뿐이다.
