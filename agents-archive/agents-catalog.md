# Agent Teams · 라우팅 카탈로그

## 책임 영역

`~/.claude/agents/` 하위 에이전트들. 호출 시 **TeamCreate/SendMessage** 방식.

| Agent | 책임 영역 |
|---|---|
| `backend-specialist` | 백엔드 일반 철학 — API·동시성·인증·캐싱·트랜잭션·멱등성·재시도·분산락·이벤트 큐·회복력. **언어·도메인 무관** |
| `domain-expert-backend` | **주식·금융 거래 + 온프레미스 도메인 특화**. OMS/EMS/Risk/Matching/Settlement, FIX, 시세 분배, 한국 시장(T+2·동시호가·KRX·망분리). 일반 패턴은 `backend-specialist` 위임 |
| `python-specialist` | Python 언어·생태계. Pythonic 관용구·타입 힌트(PEP 484/544/612/695)·asyncio·GIL·패키징(uv/pyproject.toml)·numpy/pandas/polars |
| `js-ts-specialist` | JS·TS 언어·런타임. TS 타입 시스템(satisfies/discriminated union/branded)·ESM/CJS·Promise/AbortController·Node/Bun/Deno/Edge·React 19/Next.js 15 시맨틱 |
| `db-specialist` | DB 스키마·인덱스·쿼리 최적화·마이그레이션·파티셔닝·HA·백업·PITR. 대용량(시세 틱·체결 내역) |
| `infra-ops` | 서버·네트워크·스토리지·LB·방화벽·배포 파이프라인·모니터링·**장애 분석/postmortem**. 온프레미스 |
| `ux-ui` | UX·UI·컴포넌트·스타일·a11y·디자인 토큰. **주식·핀테크 UI**(호가창·시세·주문·체결·잔고). `.tsx/.jsx/.ts(컴포넌트)/.css/.scss/.html` 직접 수정 가능 |
| `stock-domain` | 주식·금융 도메인 정합성·규제. KRX·FSS·자본시장법·SEC. T+N·세금·권리 이벤트·휴장·호가 단위·표준(FIX/ITCH/ISIN) |
| `tester` | 단위·통합·E2E·속성·변이·계약·성능(load/stress/spike/soak)·카오스·보안(SAST/DAST/SCA/Secret)·시각 회귀·접근성·결정성 |
| `reviewer` | 코드 리뷰. 의도·버그·보안·스타일·일관성. **읽기 전용**(파일 수정·git/gh 변경 명령·외부 API write 금지) |
| `critic` | 다른 agent·메인의 결론에 대한 **반대 가설·숨은 가정·누락·SPOF**. 무차별 반박 금지(근거 필수) |
| `report-writer` | **HTML 보고서·문서·정리본 전담**. 사용자 노출 마지막 게이트. 사실·인용·확신도 변형 없이 유지 |
| `lead` | **위 12개 서브에이전트의 오케스트레이터**. 다중 도메인·고위험 다단 파이프라인을 분해·라우팅·합성. 직접 코드 수정 안 함. 자세한 라우팅 케이스북·모델 정책은 `~/.claude/agents/lead.md` 참조 |

자연어 트리거 등 상세는 각 agent의 `~/.claude/agents/<name>.md` description 참조.

## 라우팅 충돌 시 경계

- **백엔드 일반 원리(멱등성·트랜잭션·캐시·재시도 등)는 `backend-specialist`**, **거래·정산·시세·온프레미스 도메인 특화는 `domain-expert-backend`** — 일반 직렬 순서: backend-specialist(일반 패턴) → domain-expert-backend(도메인 구체화) → stock-domain(법·규제·표준 적합성)
- **언어 관용구·타입·런타임 표현은 `python-specialist` / `js-ts-specialist`** — 본 agent들은 "그 설계를 해당 언어로 어떻게 표현할지"만. API 계약·트랜잭션 경계는 그쪽이 아니라 backend-specialist
- **API 호출 패턴·트랜잭션 경계는 `backend-specialist`**, **DB 안쪽 스키마·쿼리 플랜은 `db-specialist`** — 둘은 호출 패턴 ↔ 스키마·인덱스로 합의
- **시각·디자인·a11y는 `ux-ui`**, **`.tsx`에서 TS 타입·hook·`"use client"` 경계·페칭은 `js-ts-specialist`** — 혼합 발화는 ux-ui → js-ts-specialist 직렬
- **보고서 자체는 `report-writer`** — 보고서 내부 차트 스타일만 ux-ui와 협업
- **코드 리뷰는 `reviewer`(읽기 전용)**, **반박·sanity check는 `critic`**, **회귀 테스트 작성은 `tester`** — 셋은 직렬: reviewer 지적 → critic 가설 검증 → tester 회귀 테스트
- **도메인 규칙(호가·세금·결제일·휴장)은 `stock-domain`**, 이걸 **이벤트·코드로 구현하는 건 `domain-expert-backend`/`ux-ui`**
- **인프라(서버·네트워크·배포·모니터링)는 `infra-ops`**, **애플리케이션 로직은 `backend-specialist`/`domain-expert-backend`**
- **여러 agent를 직렬·병렬로 묶어야 하는 다중 도메인·고위험 작업은 `lead`로 위임** — 단일 agent로 끝나는 작업에는 lead 거치지 않는다

## PR 리뷰 파이프라인 — reviewer · critic · pr-review 스킬 조합

| 상황 | 트리거 | 파이프라인 |
|---|---|---|
| **타인의 GitHub PR 리뷰** | "PR 리뷰", "PR #N 봐줘", "리뷰해줘" | `/pr-review` 스킬 호출 → 내부에서 `reviewer` agent로 코드 깊이 분석 → `critic`으로 누락/반례 sanity check → 최종 HTML 보고서 산출 |
| **본인 PR 셀프 점검** | "셀프 리뷰", "PR 올리기 전 점검" | `/self-review` 스킬 호출 → `reviewer` agent로 본인 코드 검토 → critic 1회 → 사용자 결정 |
| **보안 전용 리뷰** | "security review", "보안 우려" | `/security-review` 스킬 → `reviewer` (보안 관점) → critic |
| **PR 코드만 빠르게 봐줘** | "이 코드 어떻게 생각해", 스킬 호출 없이 짧은 답 원할 때 | `reviewer` agent 단독 → critic 생략 가능 (trivial 변경 시) |

**핵심 원칙**:
- **PR 리뷰 산출물은 `/pr-review` 스킬 기준 HTML 보고서가 표준**. reviewer agent를 단독 호출해 마크다운으로만 끝내지 말 것.
- **reviewer는 읽기 전용** — 파일 수정·git/gh 변경 명령·외부 API write 절대 금지. PR 코멘트 작성도 사용자 확인 후 사용자가 직접.
- **critic은 reviewer 결론 직후 1회 권장** — 단, trivial PR(오타·import 정리 등)은 생략.
- **회귀 테스트 필요하면 `tester` 추가** — reviewer 지적 → critic 가설 검증 → tester 회귀 테스트. 세 agent 직렬.
