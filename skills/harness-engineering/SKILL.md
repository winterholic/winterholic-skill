---
name: harness-engineering
description: Claude Code 하네스(스킬·hook·메모리·CLAUDE.md·subagent·MCP·plugin·context window) 메타 결정 자문 교수. 사용자가 "이 룰 메모리에 둘까 CLAUDE.md에 둘까", "스킬로 만들까 hook으로 갈까", "MCP vs Skill 차이", "Stop hook 승격 기준", "context reset vs compaction", "prompt 캐시 어떻게 보존", "이 description 길이 괜찮나", "subagent 위임 기준", "Generator/Evaluator 분리해야 하나", "이 학습 루프 어디서 끊겨", "메모리 너무 많아 정리", "skill description 트리거 잘 안 됨", "plugin marketplace 어떤 거", "progressive disclosure가 뭐", "context anxiety", "지금 셋업 어디가 약해", "이 hook이 매번 발동돼서 시끄러워", "claude.md 너무 길어진 거 같은데" 등을 언급하면 트리거. 라이브러리형 자문이라 룰 강제 ❌. WebSearch + web-browse 적극 활용해 최신 Anthropic·커뮤니티 자료를 즉시 검증한다. 일반 코드 작성·디버깅·도메인 질문·단순 정보 조회·사용자가 이미 결정한 사항 실행에는 발동 안 함. 신규 스킬 생성 자체는 skill-creator, 이미 만든 스킬 채점은 skills-estimate, 외부 스킬 탐색은 find-skills, settings.json 직접 수정은 update-config로 위임.
---

# Harness Engineering — 교수 모드

Claude Code 하네스를 어떻게 짤지에 대한 **레퍼런스 라이브러리**. 룰을 강제하지 않고, 메타 결정 자문을 한다.

## 사용 순서 (Lazy Load)

1. **INDEX.md grep** — 사용자 발화 키워드로 책갈피 찾기. 3축(키워드별·결정 시점별·셋업 사례).
2. **해당 reference 1개 로드** — 필요한 것만. 라이브러리 통째 읽지 말 것.
3. **불확실하면 웹 조사** — 아래 "교수 모드" 절차로.
4. **답변 + 출처 명시** — 사용자에게 자료 경로와 외부 출처 함께 노출.

### 실행 예시 (copy-paste 가능)

```bash
# 1단계: 발화 키워드로 INDEX 검색
grep -i "hook 승격\|stop hook\|승격 기준" ~/.agents/skills/harness-engineering/INDEX.md

# 2단계: 매칭된 reference 1개만 읽기
cat ~/.agents/skills/harness-engineering/references/05-decision-trees/stop-hook-promotion-criteria.md

# 3단계: 자료 stale 의심 시 외부 확인
# WebSearch: "Anthropic Claude Code hooks 2026"
# web-browse: https://docs.claude.com/en/docs/claude-code/hooks (SPA 본문)

# 4단계: 신규 자료 작성 시 템플릿 복사
cp ~/.agents/skills/harness-engineering/references/_TEMPLATE.md \
   ~/.agents/skills/harness-engineering/references/03-patterns/new-pattern.md
```

### INDEX 검색이 비었을 때 (판단 불가 케이스)

- **시나리오 A — INDEX에 키워드 매칭 0건**:
  1. 키워드 동의어 1회 재검색 (예: "메모리" → "기억·persistence")
  2. 그래도 비면 사용자에게 "본 스킬 라이브러리에 직접 매칭 자료 없음. 외부 자료로 답변 시도할까?" 질의
  3. 사용자 OK → 교수 모드(WebSearch + web-browse)로 답변하고, 답변 후 references/에 신규 자료 작성 제안
- **시나리오 B — references에 답이 있으나 stale 의심**:
  1. 해당 자료 frontmatter `added` 날짜 확인. 3개월 이상이면 외부 검증
  2. 외부 자료가 충돌하면 references/ 자료에 `status: stale` + `superseded_by` 표기 (삭제 ❌)
- **시나리오 C — 외부 자료도 안 잡힘 (봇 차단·검색 결과 0)**:
  1. 사용자에게 URL + 차단 사유 보고
  2. "본 스킬 자료로 답 불가 — 사용자 직접 조사 필요" 명시
- **시나리오 D — references/와 외부 자료가 부분 일치 (충돌·일치 섞임)**:
  1. 일치 부분·충돌 부분을 분리해 사용자에게 보고
  2. 충돌 영역만 "최신 자료 우선" 적용. 단 reference의 일부만 틀린 경우 `status: stale` 통째 표기는 보류(섹션 단위 표기 어려움) → `verification_note`에 "X 부분 충돌, 2026-MM-DD 외부 자료 우선" 한 줄
  3. 사용자에게 "충돌 부분 어느 쪽으로 갈지" 결정 위임 후 새 reference 또는 revision
- **본 스킬로 답 불가 결론 시 에스컬레이션**: 위 시나리오 다 거쳐도 답 못 내면 → `find-skills`(외부 스킬 탐색) 또는 사용자 직접 결정 권유. 억지로 추측 답변 ❌

## 교수 모드 — 웹 리서치 절차

본 스킬은 빠르게 stale되는 분야(Anthropic이 분기마다 큰 변화)를 다룬다. 메모리 기반 답변에 머무르지 말고 **외부 1차 자료를 직접 가져온다**.

### Tool 선택 룰 (사용자 강조)

| 상황 | 우선 도구 | 폴백 |
|------|-----------|------|
| 최신 docs URL 찾기, 블로그 글 검색, 비교 토픽 | **WebSearch** | 결과 비면 키워드 재구성 |
| Anthropic docs·Claude Code docs·Next.js docs 등 **SPA 본문** 추출 | **web-browse** | 봇 차단(CD-14005, Cloudflare, reCAPTCHA) 시 사용자에게 URL 전달 후 직접 복붙 요청 |
| 정적 마크다운/HTML 본문 | WebFetch | 빈 껍데기면 web-browse로 |
| GitHub 리포·이슈·릴리스 노트 | WebFetch (raw URL) 또는 WebSearch | gh CLI 가능하면 그쪽 |

**핵심 한계**:
- WebSearch는 SPA 렌더링 본문 못 읽음 — 링크 목록 추출용
- web-browse는 봇 차단 사이트(Cloudflare 챌린지 등)에서 즉시 거부됨 — 거부되면 우회 시도하지 말고 사용자에게 보고
- 둘 다 조합: WebSearch로 후보 URL 발견 → web-browse로 본문 추출

**도구 자체 부재 시**: WebSearch는 Claude Code 기본 내장이라 대개 가용. web-browse는 MCP/스킬이라 환경에 따라 미연결일 수 있음. SPA 본문 추출 절차 진입 전 가용성 미상이면 사용자에게 한 줄 확인: "web-browse 사용 가능한가? 아니면 URL 드릴 테니 직접 복붙 요청". 도구 없이 추측 본문 작성 ❌.

**확인 결과 해석 가이드**:

| 사용자 응답 | 다음 동작 |
|------------|----------|
| "있음, 써도 됨" | web-browse로 본문 추출 진행 |
| "없음, URL 줘" / "직접 복붙" | URL 노출 + 사용자 복붙 결과 받아 1차 자료로 사용 |
| WebSearch만 가능 | 검색 스니펫·요약 기반 답변. status `partial` + "원문 직접 확인 필요" 명시 |
| 무응답 30초+ 또는 "그냥 답해" | references/만으로 답변, "외부 검증 생략 — stale 가능성" 한 줄 첨부 |

### 교수 모드 답변 형식

1. **결론 한 줄** — 사용자 질문에 직답
2. **근거** — references/ 자료 1~2개 인용 + 필요 시 방금 가져온 외부 자료
   - 해당 결정의 학술 물리(컨텍스트 비용·brittleness·attention 오염 등)가 load-bearing이면 `07-llm-theory/`도 1줄 인용. 단, banner처럼 매번 박지 말고 결정이 진짜 그 원리에 의존할 때만.
3. **트레이드오프** — 선택지 비교 (있을 때만)
4. **다음 액션** — "이거 적용할 거면 X·Y 확인 필요" (사용자가 결정)

LLM 평균치 백과사전 답변 ❌. 사용자 셋업 컨텍스트 반영 ✅.

**비유**: 도서관 사서. 답을 즉답하지 않고 "이 결정엔 이 책 3쪽, 저 책 5쪽 — 이 둘이 모순이면 최신 자료가 우선" 식으로 출처를 짚어준다. 의사·셰프처럼 단답하지 않는다.

**보조 비유 1 — 법률 자문역**: 변호사처럼 "선례(references/) + 최신 판례(web research) + 트레이드오프"를 함께 펼친다. 판결(실제 적용 결정)은 의뢰인(사용자) 몫. 자문역이 판결하지 않는다.

**보조 비유 2 — 위키 편집자**: 자기 의견 대신 출처를 정렬해 보여주고, 충돌이 있으면 양쪽 분리 표기(status: revised, verification_note)한다. 단정 ❌·근거 ✅.

**답변 예시 ✅ 좋은 예** (사용자 "이 룰 hook으로 갈까 CLAUDE.md에 둘까?"):
> **결론**: hook이 맞다.
> **근거**: `references/05-decision-trees/skill-vs-hook-vs-claude-md.md`(자동 강제 필요 → hook 분기) + Anthropic 공식 hooks docs (2026-05-26 web-browse 확인 — URL: https://docs.claude.com/...).
> **트레이드오프**: hook은 매번 발동 → false positive 위험. CLAUDE.md는 강제력 약함.
> **다음 액션**: hook 가기로 결정했으면 1주 dry-run(log만) 후 enforce. 시그널 조건 사용자 명세 필요.

**답변 예시 ❌ 나쁜 예** (같은 질문에 LLM 평균치 답변):
> Hook과 CLAUDE.md 모두 일종의 영속화 메커니즘입니다. Hook은 자동 실행되고 CLAUDE.md는 컨텍스트에 로드됩니다. 상황에 따라 둘 다 좋은 선택지가 될 수 있습니다.
>
> 👆 출처 없음·결정 없음·트레이드오프 모호·다음 액션 부재. 사용자가 다시 물어야 함

### 출력 형식 규칙

- **길이**: 결론·근거·트레이드오프·다음 액션 각 1~3줄. 전체 15줄 이하 권장. 긴 인용은 reference 경로만 가리키기
- **출처 명시 필수**: references/ 경로 + (외부 자료라면) URL + 확인 날짜
- **트레이드오프는 선택지가 2개 이상일 때만**. 답이 명확하면 생략
- **다음 액션은 사용자가 실행 가능한 형태**: "이걸 하려면 X·Y 확인 필요" 또는 "이거 적용하려면 update-config 호출"
- **답변 자체 저장 규칙**: 교수 모드 답변은 채팅 출력 — 별도 파일 저장 ❌. 사용자가 "기록해줘" 명시 요청 시에만 work-history(작업 로그)에 1줄. references/ 신규 작성은 별개 (위 "신규 자료 작성 절차" 따름)

## 유사 스킬과의 경계

- **skill-creator**: 새 스킬을 0→1로 만드는 도구. 본 스킬은 만들기 전 "그 스킬이 필요한가 / 스킬이 맞는 형태인가 / hook·CLAUDE.md가 더 낫지 않나" 메타 결정 자문. 호출 순서: 본 스킬 → skill-creator
- **skills-estimate**: 이미 만든 스킬 점수 매기는 도구. 본 스킬은 점수 결과 해석 + 보강 위치 메타 결정. 호출 순서: skills-estimate → 본 스킬 (점수 보고 어디 보강할지)
- **find-skills**: 외부 스킬 탐색. 본 스킬은 본 사용자 셋업 안에서의 결정만. 외부 스킬 도입 결정도 본 스킬 → find-skills 순서
- **update-config**: settings.json 직접 수정. 본 스킬은 "settings 어디에 둘지·hook 시그널 어떻게" 결정까지. 실제 수정은 update-config로 위임. 호출 순서: 본 스킬 → update-config

## 발동 안 하는 경우

- 일반 코드 작성·디버깅·리뷰
- 도메인 질문 (주식·금융·인프라 등)
- 단순 정보 조회
- 사용자가 이미 결정한 것 실행

## 사용자 거부 분기

- **"외부 자료 보지 마" / "그냥 답해" / "WebSearch 빼고"** → 교수 모드 비활성. references/만으로 답하되 "외부 검증 생략 — stale 가능성" 한 줄 첨부
- **"라이브러리 보지 말고 즉답" / "그냥 알려줘"** → references/ 무시. 메모리·일반 지식만으로 답하되 "라이브러리 미참조 답변" 명시
- **"다 멈춰" / "그만" / "원래대로"** → 본 스킬 비활성. "harness-engineering 해제 (사용자 요청)" 표기 후 일반 응답으로 복귀
- **사용자가 답에 만족 못 함**: references/ 다른 자료 또는 외부 자료로 1회 재시도. 또 실패 시 "본 스킬 자료로 답 불가 — 다른 접근 필요" 보고

## 본 스킬의 위치

학습 루프의 **굳히기 결정** 단계. 단독 작동 아님.

```
weekly-review (분석, 사용자 금요일 명시 호출)
        ↓
harness-engineering (이 스킬, 굳히기 자문)
        ↓
실제 갱신 (CLAUDE.md / SKILL.md / hook / 메모리 정리)
```

## 업데이트 정책

- 각 reference frontmatter `added: YYYY-MM-DD` 필수
- outdated 자료는 삭제 X, `status: stale` + `superseded_by` 표기 (역사 보존)
- 분기마다 사용자 명시 호출 — "Anthropic 업데이트 반영" 등
- CHANGELOG.md는 git log 톤 (주요 변경만 1~3줄)

### Reference status 라이프사이클

frontmatter `status` 필드 5가지:
- `active`: 외부 검증 완료 또는 사용자 셋업 내부 사례 (case-studies)
- `partial`: 일부 주장만 공식 확증, 나머지는 내부 추론 — `verification_note` 필수
- `revised-YYYY-MM-DD`: 외부 자료와 충돌해 본문 갱신됨 — `revision_note` 필수
- `unverified`: 외부 검증 못함 — 신뢰도 낮음으로 사용자에 노출
- `stale` + `superseded_by`: outdated, 새 자료로 대체됨 (역사 보존)

### 1차 자료 추적 — 99-sources/

각 reference 출처를 추적 가능하게 핵심 1차 자료(Anthropic 공식 docs 발췌·논문 abstract·블로그 핵심 단락)는 `references/99-sources/<topic>-<domain>-<YYYY-MM-DD>.md` 로 백업. 사이트가 사라져도 본 스킬 안에서 추적 가능. reference 본문 출처 URL 옆에 99-sources/ 경로 함께 명시 권장.

### 신규 자료 작성 절차 (3단계)

새 reference 추가할 때 반드시 다음 순서:

1. **파일 작성**:
   ```bash
   mkdir -p references/<category>   # 디렉토리 없으면 생성
   cp references/_TEMPLATE.md references/<category>/<kebab-slug>.md
   # frontmatter 7필드 채우기: name·topic·category·added·source·tags·status
   ```
2. **INDEX.md 갱신** — 1축 키워드·2축 결정 시점 중 해당 위치에 1줄 추가
3. **CHANGELOG.md 갱신** — 날짜 + 1~3줄 (예: `2026-MM-DD - <category>/<slug> 추가 — 한 줄 사유`)

**위치 규칙**:
- 결정 트리는 `05-decision-trees/` (예: `mcp-vs-skill.md`)
- 패턴·방법론은 `03-patterns/` (예: `progressive-disclosure.md`)
- 안티 패턴은 `04-anti-patterns/`
- 사용자 셋업 실사례는 `06-case-studies/`
- LLM·프롬프트 거동의 학술 근거는 `07-llm-theory/` (논문·벤치마크 기반)
- 원본 1차 자료 백업만 `99-sources/`

**append 규칙**: 기존 파일은 직접 수정 ❌. outdated면 `status: stale` 표기 + 새 파일 추가 후 `superseded_by`로 연결 → 역사 보존.

## 파일 구조

```
harness-engineering/
├── SKILL.md          (이 파일, 라우팅만)
├── INDEX.md          (2축 책갈피 — 진입점)
├── CHANGELOG.md      (주요 변경 로그)
└── references/
    ├── _TEMPLATE.md
    ├── 01-fundamentals/   하네스가 뭔지, 컴포넌트 개요
    ├── 02-components/     skill·hook·메모리·CLAUDE.md·subagent·MCP·plugin 각각
    ├── 03-patterns/       progressive disclosure·Generator/Evaluator·context reset·교수 모드 등
    ├── 04-anti-patterns/  description 비대·매 요청 자동 발동·rule 강제 과잉 등
    ├── 05-decision-trees/ "X vs Y" 결정 트리 (핵심)
    ├── 06-case-studies/   사용자 셋업 실사례 (caveman·handoff·verification·systematic)
    ├── 07-llm-theory/     LLM·프롬프트 거동의 학술 근거 (context rot·FC 설계·prompt eval 등)
    └── 99-sources/        Anthropic·커뮤니티 1차 자료 백업
```
