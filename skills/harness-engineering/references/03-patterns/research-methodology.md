---
name: research-methodology
topic: 교수 모드 — WebSearch + web-browse 폴백 전략으로 최신 1차 자료 즉시 검증
category: 03-patterns
added: 2026-05-26
source: 내부 분석 + Anthropic docs SPA 특성 관찰
tags: [methodology, websearch, web-browse, fallback, freshness]
status: active
---

# 교수 모드 — 웹 리서치 절차

## 핵심 한 줄
**메모리 답변에 머무르지 말고 매번 외부 1차 자료를 가져온다.** WebSearch와 web-browse는 서로의 한계를 보완하므로 둘을 폴백 체인으로 조합한다.

## 왜 필요한가

Anthropic·Claude Code는 분기마다 큰 변화를 낸다 — Skills(2025-08), Plugin Marketplace(2026-05-22), Managed Agents, Memory tool, Context Editing 등. LLM 내장 지식은 stale. 본 스킬 references/도 stale될 수 있음 → **답변 직전 외부 확인** 절차가 본 스킬의 핵심 차별점.

## Tool 한계 (사용자 강조)

| 도구 | 강점 | 한계 |
|------|------|------|
| **WebSearch** | 빠른 후보 URL 발견, 비교 검색 | SPA(React/Next/Vue) 렌더링 본문 못 읽음 — 검색 결과 스니펫에 의존 |
| **web-browse** | 헤드리스 Chromium으로 SPA 본문 추출 | 봇 차단(Cloudflare 챌린지, reCAPTCHA, CD-14005) 시 즉시 거부 |
| **WebFetch** | 정적 HTML/마크다운 빠름 | JS 렌더링 페이지에서 빈 div만 받음 |

**Anthropic 공식 docs는 Next.js**. WebFetch만 쓰면 본문 텅 빔.
**키움증권·일부 금융 포털**은 봇 차단. web-browse도 못 뚫음.

## 폴백 체인

```
질문 유형 판단
    ↓
[목록·비교·블로그 찾기]    →    WebSearch
[Anthropic/Next.js docs 본문]  →    web-browse (WebFetch 먼저 시도 → 빈 본문이면 web-browse)
[GitHub raw / 정적 문서]   →    WebFetch
    ↓
1차 시도 실패
    ↓
다른 도구로 1회 재시도
    ↓
또 실패 (봇 차단 등)
    ↓
사용자에게 URL 보고 + 직접 복붙 요청 (우회 시도 X)
```

## 절차 (답변 1건 기준)

1. **질문 → 검색 키워드 분해** — 한국어 발화를 영어 docs 용어로 매핑 (예: "메모리 정리" → "memory curation", "context window")
2. **WebSearch 1회** — 후보 URL 3~5개 확보
3. **출처 선별** — Anthropic 공식 > Claude Code 공식 > Anthropic 엔지니어 블로그 > 신뢰 커뮤니티 > 기타. **공식 우선**
4. **본문 추출** — 정적이면 WebFetch, SPA면 web-browse
5. **봇 차단 시** — 우회 시도 ❌. URL과 함께 사용자에게 보고
6. **답변에 출처 명시** — 자료 경로(URL + 가져온 날짜) 함께 노출. 사용자가 직접 검증 가능하게
7. **stale 자료 발견 시** — references/ 해당 파일 frontmatter `status: stale`로 표시 (삭제 X). 새 자료는 `superseded_by`로 연결

## 사용자에게 보고하는 형식

```
결론: <한 줄>

근거:
- references/05-decision-trees/skill-vs-hook-vs-claude-md.md
- 외부 (2026-05-26 확인): https://docs.claude.com/en/docs/claude-code/skills

트레이드오프:
- A: ...
- B: ...

다음 액션:
- 이거 적용하려면 X·Y 확인 필요
```

## 안 하는 것

- **백과사전식 답변** — LLM 평균치로 길게 늘이지 않는다
- **출처 없는 단정** — "공식 권장이다"라는 표현은 실제 URL 첨부할 때만
- **우회 시도** — 봇 차단 사이트를 User-Agent 변조 등으로 뚫지 않는다 (정책 위반 + 시간 낭비)
- **단일 도구 고집** — WebSearch만으로 답하지 않고 본문 추출까지 간다

## 신규 reference 작성 시 — 학술 물리 cross-link 룰

본 스킬의 결정(스킬·hook·메모리·description 등)은 거의 모두 LLM 거동의 물리(컨텍스트 비용·brittleness·attention 오염)에 기반한다. 새 reference 작성 시 다음을 점검:

1. **이 결정이 학술 물리에 의존하는가?** — 컨텍스트 길이/노이즈/형식 민감도가 load-bearing이면 YES.
2. **YES면 `07-llm-theory/` 중 해당 reference로 1줄 cross-link** — 핵심 한 줄 직후에 `> **근저 학술 물리**: [[...]] — 한 줄 이유` 형태. banner ❌, 매번 보일 필요 없음.
3. **NO여도 reference 본문에 한 번은 점검 — "내가 이 결정의 비용/이득을 학술 근거 없이 직관으로만 주장하는가?"**. 그 경우 unverified로 명시하거나 학술 물리를 찾아 보강.

이 룰의 목적: 07-llm-theory가 "쌓아두기만 한 dead reference"가 되지 않게, 결정 path에서 자연스럽게 끌려나오도록 보장.

## 관련 자료
- [[progressive-disclosure]] — 본 스킬 자체 구조 *(예정)*
- [[skill-description-tuning]] — 트리거 키워드 매핑 *(예정)*

## 출처
- 내부 분석 보고서: `./artifacts/reports/2026-05-26-analysis-harness-engineering-superpowers.html`
- 사용자 발화 2026-05-26: "web-browse스킬은 봇잡아내면 바로 거부당하더라", "웹서칭스킬은 리액트나 넥스트같이 SPA방식으로 나중에 랜더링 되는걸 못읽음"
