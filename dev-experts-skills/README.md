# dev-experts — 개발 전문가 스킬군

Claude Code용 개발 전문가 스킬을 **언어 × 프레임워크 × 방법론 × 인프라 × 품질** 축으로 세분화한 93종(전문가 91 + 라우터 1 + 메타 규칙 1) 체계. (계획 문서의 "95종"은 초기 산정 오차 — 실물 기준 이 수치가 진실, 2026-06-12 전수 대조)
단일 범용 스킬 대신, 각자 거장/원전 앵커와 안티패턴 카탈로그를 갖춘 전문가를 미리 만들어두고 꺼내 쓴다.

> **설계 근거**: `~/.claude\sub-skills\dev-experts-plan.md` (카탈로그 §5 · DoD §6 · 파이프라인 §8 · Phase §9).
> **품질 기준점**: stock-experts 21종(`~/.claude\stock-experts\`)에서 검증된 제작 공식의 이식.

## 이 폴더의 성격

- **자동 로드되지 않는 전용 폴더**다. 글로벌 `.claude/skills/`에 두지 않은 이유: 95개 description이 매 세션 컨텍스트를 상시 점유하는 것을 피하기 위함.
- 사용하려면: ① 라우터 `dev-chief-architect/SKILL.md`를 먼저 Read해 어떤 전문가를 부를지 정하고 ② 해당 전문가 `SKILL.md`를 Read해 그 매뉴얼대로 작업한다.
- **전역 디스패처**: `~/.claude/skills/dev-experts/SKILL.md`가 설치되어 있어, 일반 세션에서 개발 작업이 나오면 이 폴더로 자동 라우팅된다.
- 본문·레퍼런스의 `[[이름]]` 표기는 이 스킬군 내 다른 SKILL/레퍼런스 파일을 가리킨다. `(→ dev-x)`는 해당 전문가 스킬로의 위임 표시다.
- 개별 스킬을 자주 쓰게 되면 그 폴더만 글로벌 `skills/`로 승격한다.

## 제1원칙 — 우선순위 사다리 (모든 스킬 적용)

```
프로젝트 CLAUDE.md·프로젝트 스킬 > 이 스킬군의 전문가 > LLM 일반 지식
```

프로젝트별 컨벤션이 전문가 일반론과 충돌하면 **항상 프로젝트 규칙이 이긴다**. 전문가 스킬은 프로젝트 규칙이 침묵하는 영역만 채운다. 충돌을 발견하면 따르되, 프로젝트 규칙이 알려진 안티패턴일 경우 한 줄로 지적만 한다(무단 변경 금지).

## 공통 규칙 (모든 스킬 적용)

1. **버전 라벨 의무**: 모든 스킬은 frontmatter 직하에 `> 기준: <스택> <버전> (YYYY-MM)` 표기. 스킬의 주장과 현재 버전이 다르면 **공식 문서가 이긴다** — 스킬은 원칙·함정 위주, 버전 의존 세부는 공식 문서 확인.
2. **안티패턴 우선**: 잘 하는 법은 LLM이 이미 안다. 스킬의 가치 절반은 ❌/✅ 안티패턴 카탈로그(스킬당 5쌍 이상)에 있다. 작업 전 해당 스킬의 안티패턴 섹션을 먼저 본다.
3. **검증 명령 의무**: 코드 산출물에는 그 스킬이 정의한 검증 명령(테스트·린트·타입체크·빌드)을 실행하고 출력을 첨부한다. 실행 불가면 "미실행: <이유>" 한 줄 (verification-before-completion 규칙과 동일).
4. **불확실 수치는 "확인 필요"**: 설정 기본값·임계치·버전별 동작은 변한다. 확신 없는 값은 추측으로 메우지 않고 "확인 필요" 표기 + 공식 문서 경로 제시.
5. **모르는 스택은 정직하게**: 카탈로그에 없는 스택이거나 스킬이 미제작(⬜)이면 그 사실을 밝히고 일반 지식 + 공식 문서로 진행한다. 미제작 스킬을 있는 것처럼 Read 시도하지 않는다.
6. **경로 표기**: 스킬 내부 참조는 상대 경로 + 슬래시(`references/x.md`, `scripts/check.py`) — Anthropic 공식 안티패턴 가이드(백슬래시 금지) 준수. 스킬 폴더 밖(다른 스킬군·vault)을 가리킬 때만 절대 경로.
7. **참조 깊이 1단계**: SKILL.md → references/*.md 까지만. 레퍼런스가 또 다른 레퍼런스를 가리키지 않는다(부분 읽기로 정보 누락됨). 100줄 넘는 레퍼런스는 맨 위에 목차 의무.

## 공통: 빠른 사용 (Quick Start)

1. **라우터부터** — `dev-chief-architect/SKILL.md`를 읽어 작업을 [언어 × 프레임워크 × 방법론 × 품질] 축으로 분해, 전문가 1~3명을 고른다. (스택이 이미 명확하면 해당 전문가 직행)
2. **그 전문가 SKILL.md의 "워크플로우 + 안티패턴"** 만 따라 바로 작업한다. 심화는 `references/`로 미룬다.
3. **막히면** 트러블슈팅 ledger(아래)를 먼저 검색 — 같은 삽질의 기록이 있을 수 있다.

## 트러블슈팅 일지 (피드백 루프 — stock-scorecard의 이식)

개발의 사후 채점은 **"같은 삽질 두 번 안 하기"**다:

- 디버깅·삽질이 **30분을 넘긴 문제가 해결되면** `troubleshooting/ledger.md`에 1행 추가 (append-only, 기존 행 수정 금지):
  `| 날짜 | 스택 | 증상 | 근본 원인 | 해결 | 관련 스킬 | 스킬에 있었나(Y/N) |`
- **"스킬에 있었나 = N"이 같은 패턴으로 3회 누적** → 해당 스킬의 안티패턴 섹션에 정식 추가(3회 룰 — 일화 과적합 방지).
- 새 삽질 시작 전 ledger를 grep해 기존 기록 확인 — 있으면 그 해결책부터 시도.

## 시효성 관리 — 부패 속도 3등급

| 등급 | 대상 | 점검 주기 | 점검 내용 |
|---|---|---|---|
| **빠름** | nextjs, react, cloud-aws, llm-engineering, mobile-* | 분기 | 버전 라벨 갱신 + 깨진 정량 기준 수정 |
| **중간** | 프레임워크·인프라(fastapi, spring, docker, k8s, postgres 등) | 반기 | 동일 |
| **느림** | 언어 코어·방법론(python, tdd, ddd, refactoring, cs 기초 등) | 연 1회 | 동일 |

점검 = 라벨 갱신 + 수치 수정이지 전면 재작성이 아니다(원칙·안티패턴은 오래 간다). **낡은 스킬은 없는 것보다 나쁘다**(자신 있게 틀림) — 버전 라벨이 1년 이상 지난 스킬은 공식 문서 우선 모드로 쓴다.

## 2계층 스펙

- **풀스펙** (Phase 1·2): DoD 12항목 전체 — frontmatter 트리거 10+, 경계 표, 안티패턴 5쌍+, 정량 기준, 워크플로우+템플릿+예시, 실전 케이스(유명 장애), scripts 1+(실행 검증), references 3~4겹, 한계 섹션, skills-estimate 85+.
- **코어스펙** (Phase 3·4): SKILL.md + 안티패턴 5쌍 + evidence 1겹. scripts 생략 가능. 실사용 발생 시 풀스펙 승격.

DoD 전문: `dev-experts-plan.md` §6. 제작 템플릿: `_template/SKILL-template.md`.

## 전문가 카탈로그 (92 폴더 + 메타 1)

> 상태: ✅ 제작됨 · ⬜ 미제작 (Phase 숫자는 제작 우선순위). **⬜ 스킬은 Read 시도 금지** — 일반 지식 + 공식 문서로 진행.

### A. 언어 코어 (10)
| 스킬 | 거장/원전 앵커 | Phase | 상태 |
|---|---|---|---|
| dev-python | Fluent Python·Effective Python·PEP | 1 | ✅ |
| dev-typescript | Effective TypeScript·공식 핸드북 | 1 | ✅ |
| dev-javascript | You Don't Know JS·MDN | 3 | ✅ |
| dev-java | Effective Java(Bloch) | 2 | ✅ |
| dev-go | Effective Go·Pike proverbs | 3 | ✅ |
| dev-rust | The Book·Rustonomicon | 3 | ✅ |
| dev-sql | Use The Index, Luke·SQL Antipatterns | 3 | ✅ |
| dev-c-cpp | K&R·Effective Modern C++ | 4 | ✅ |
| dev-csharp-dotnet | C# in Depth(Skeet) | 4 | ✅ |
| dev-kotlin | 공식 문서·코틀린 인 액션 | 4 | ✅ |

### B. 백엔드 프레임워크 (5)
| 스킬 | 앵커 | Phase | 상태 |
|---|---|---|---|
| dev-fastapi | tiangolo 공식·full-stack 템플릿 | 1 | ✅ |
| dev-django | Two Scoops of Django | 2 | ✅ |
| dev-spring | 김영한·토비의 스프링 | 2 | ✅ |
| dev-spring-jpa | 김영한 JPA·Java Persistence | 2 | ✅ |
| dev-nestjs | 공식 문서 | 2 | ✅ |

### C. 프론트·클라이언트 (8)
| 스킬 | 앵커 | Phase | 상태 |
|---|---|---|---|
| dev-react | react.dev 신공식(Abramov 멘탈모델) | 1 | ✅ |
| dev-nextjs | 공식 문서 — 부패 최속, 버전 라벨 필수 | 1 | ✅ |
| dev-css-tailwind | 공식·Refactoring UI | 3 | ✅ |
| dev-vue | 공식 문서 | 3 | ✅ |
| dev-mobile-flutter | 공식 문서 | 3 | ✅ |
| dev-mobile-react-native | 공식·Expo | 3 | ✅ |
| dev-electron-desktop | 공식 문서 | 3 | ✅ |
| dev-browser-extension | Chrome MV3 | 3 | ✅ |

### D. 데이터·스토리지 (5)
| 스킬 | 앵커 | Phase | 상태 |
|---|---|---|---|
| dev-postgres | 공식·The Art of PostgreSQL | 1 | ✅ |
| dev-redis | 공식·캐시 패턴 | 2 | ✅ |
| dev-database-modeling | 정규화·DDIA 일부 | 2 | ✅ |
| dev-mongodb | 공식 문서 | 3 | ✅ |
| dev-search | Elasticsearch·한국어 형태소 | 3 | ✅ |

### D2. 데이터 분석·AI (5)
| 스킬 | 앵커 / 비고 | Phase | 상태 |
|---|---|---|---|
| dev-data-engineering | 수집·ETL·스케줄링 — **sample-service 직결** | 1 | ✅ |
| dev-data-analysis | pandas·EDA | 3 | ✅ |
| dev-ml-basics | scikit-learn·고전 ML | 4 | ✅ |
| dev-computer-vision | OpenCV — CCTV/Frigate 직결 | 2 | ✅ |
| dev-media-ffmpeg | ffmpeg·RTSP — CCTV 직결 | 2 | ✅ |
| dev-math-stats | 개발자용 확률·통계·선형대수 | 4 | ✅ |

### E. 인프라·운영 (16)
| 스킬 | 앵커 | Phase | 상태 |
|---|---|---|---|
| dev-docker | 공식·멀티스테이지 | 1 | ✅ |
| dev-linux-ops | systemd·홈서버(ubuntu-01) | 1 | ✅ |
| dev-cicd | GitHub Actions 중심 | 1 | ✅ |
| dev-nginx | 공식·리버스 프록시 | 3 | ✅ |
| dev-monitoring | Prometheus/Grafana·SRE | 2 | ✅ |
| dev-networking | TCP/IP Illustrated + 홈 네트워크 | 2 | ✅ |
| dev-messaging-queue | Kafka·RabbitMQ — 멱등성·DLQ | 2 | ✅ |
| dev-backup-dr | 3-2-1 규칙·복구 리허설 | 2 | ✅ |
| dev-kubernetes | 공식 문서 | 3 | ✅ |
| dev-cloud-aws | Well-Architected | 3 | ✅ |
| dev-iac | Terraform·Ansible — ServerManager 직결 | 2 | ✅ |
| dev-virtualization | Proxmox·VM/LXC | 4 | ✅ |
| dev-storage-nas | RAID·ZFS·SMB/NFS | 4 | ✅ |
| dev-dns-domain-email | DNS·SPF/DKIM/DMARC — example-domain.com 직결 | 2 | ✅ |
| dev-incident-response | 장애 대응·blameless 포스트모템 | 4 | ✅ |

### F. 방법론·설계 (15)
| 스킬 | 거장 앵커 | Phase | 상태 |
|---|---|---|---|
| dev-tdd | 켄트 벡 | 1 | ✅ |
| dev-ddd | 에반스·버논 | 2 | ✅ |
| dev-msa | 샘 뉴먼 — "모놀리스 먼저" 1원칙 | 2 | ✅ |
| dev-clean-architecture | 밥 마틴 + 비판 동비중 | 2 | ✅ |
| dev-refactoring | 마틴 파울러 2판 | 2 | ✅ |
| dev-design-patterns | GoF + 패턴 강박 경계 | 2 | ✅ |
| dev-rest-api-design | Stripe/GitHub API 사례 | 1 | ✅ |
| dev-event-driven | Kleppmann·아웃박스 패턴 | 2 | ✅ |
| dev-code-review | 구글 엔지니어링 가이드 | 2 | ✅ |
| dev-system-design | 캐파 산정·병목 | 4 | ✅ |
| dev-distributed-systems | Kleppmann DDIA 본진 | 4 | ✅ |
| dev-legacy-code | Feathers | 4 | ✅ |
| dev-api-integration | 인증·재시도·백오프·웹훅 | 4 | ✅ |
| dev-payments | PG·멱등키·이중결제 | 4 | ✅ |
| dev-notification | 푸시·이메일·발송 큐 | 4 | ✅ |

### G. 품질·보안 (9)
| 스킬 | 앵커 | Phase | 상태 |
|---|---|---|---|
| dev-testing | 테스트 피라미드·pytest/jest | 1 | ✅ |
| dev-web-security | OWASP Top 10 | 2 | ✅ |
| dev-auth | OAuth2/OIDC/JWT — 직접 구현 금지 영역 | 2 | ✅ |
| dev-performance | 측정 우선·Gregg | 3 | ✅ |
| dev-error-logging | 구조적 로깅·관측 가능성 | 2 | ✅ |
| dev-load-testing | k6/locust | 4 | ✅ |
| dev-cryptography | "직접 구현 금지"가 본체 | 4 | ✅ |
| dev-privacy-compliance | 개인정보보호법·GDPR 기초 | 4 | ✅ |
| dev-dependency-security | 공급망·버전 고정 | 4 | ✅ |

### H. 유틸·도구 (9)
| 스킬 | 비고 | Phase | 상태 |
|---|---|---|---|
| dev-git-advanced | rebase·bisect·복구 | 3 | ✅ |
| dev-regex | ReDoS 함정(Cloudflare) | 3 | ✅ |
| dev-web-scraping | Playwright/bs4·약관 준수 | 3 | ✅ |
| dev-data-viz | 차트 선택 가이드 | 3 | ✅ |
| dev-bot-building | 텔레그램/디스코드 봇 | 3 | ✅ |
| dev-cron-scheduling | APScheduler/cron | 3 | ✅ |
| dev-geo-maps | 지도 API·좌표계 — tour-data 직결 | 3 | ✅ |
| dev-seo-analytics | SEO·이벤트 추적 | 3 | ✅ |
| dev-windows-powershell | Windows 개발 환경 | 3 | ✅ |

### I. 특수 도메인·CS 기초 (10)
| 스킬 | 비고 | Phase | 상태 |
|---|---|---|---|
| dev-hardware | PC 부품·중고 사기 체크리스트 | 4 | ✅ |
| dev-llm-engineering | 프롬프트·RAG·에이전트 (claude-api와 경계: 그쪽은 API 레퍼런스) | 3 | ✅ |
| dev-concurrency | 스레드·락·async 모델 — 언어 불문 | 3 | ✅ |
| dev-realtime | WebSocket·SSE | 3 | ✅ |
| dev-iot-raspberry | 라즈베리파이·홈 자동화 | 4 | ✅ |
| dev-algorithms | 자료구조·복잡도 | 4 | ✅ |
| dev-cs-fundamentals | OS·메모리·파일시스템 | 4 | ✅ |
| dev-tech-writing | README·ADR | 4 | ✅ |
| dev-opensource-license | GPL/MIT/Apache 판단 | 4 | ✅ |

### J. 메타 (2)
| 스킬 | 역할 | 상태 |
|---|---|---|
| dev-chief-architect | 라우터 — 작업 분해 → 전문가 조합 + 충돌 조율 | ✅ |
| troubleshooting/ledger.md | 트러블슈팅 일지 (위 공통 규칙) | ✅ |

## 오픈소스 흡수 소스맵 (Phase 1+ 제작 시 참조)

절차는 `dev-experts-plan.md` §7 (흡수 + 역흡수 + 라이선스 표기). 2026-06 1차 조사로 검증된 소스:

| 소스 | 라이선스 | 용도 |
|---|---|---|
| anthropics/skills (공식 17종) | 공식 | skill-creator·webapp-testing 등 — 작성 표준의 원전 |
| alirezarezvani/claude-skills (337종) | MIT | api-test-suite-builder·pr-review-expert·database-designer 등. stdlib-only 원칙 동일. **역흡수**: 스택 버전 라벨·부패 관리 부재 → 우리 차별점 |
| VoltAgent/awesome-agent-skills (1000+) | MIT(목록) | 공식 팀 스킬 색인 — vercel-labs/next-*, openai/gh-fix-ci, trailofbits/property-based-testing |
| vercel-labs/next-best-practices · vercel-react-best-practices | — | **이미 sub-skills에 보유** — dev-nextjs·dev-react는 중복 제작 말고 이를 흡수·참조 |

### 기존 스킬 등재 (중복 제작 금지 — 그쪽으로 위임)
| 영역 | 위임 대상 |
|---|---|
| 문서 산출물(pptx·pdf·xlsx·docx) | `sub-skills\<이름>\SKILL.md` 수동 Read |
| 디버깅 절차 | 글로벌 systematic-debugging |
| MCP 서버 제작 | 글로벌 mcp-builder |
| E2E 브라우저 테스트 | 글로벌 webapp-testing |
| UI/접근성 리뷰 | 글로벌 web-design-guidelines |
| Claude API 레퍼런스 | 글로벌 claude-api |
| 주식 '분석·판단' | stock-experts 디스패처 |

## 상태

**전 Phase 완료(2026-06-12)**: 전문가 93종 + 라우터 1 = 94 폴더 전부 제작 완료 (Phase 0 인프라 2026-06-10 → Phase 1·2 풀스펙 38종 2026-06-11 → Phase 3·4 코어스펙 53종 2026-06-12).
- **스펙 구분**: Phase 1·2 = 풀스펙(scripts+references 3~4겹) / Phase 3·4 = 코어스펙(SKILL.md + evidence 1겹, scripts 없음) — 실사용 발생 시 풀스펙 승격.
- 다음 운영 과제: 시효성 분기 점검(부패 빠름 등급부터) · 트러블슈팅 ledger 가동 · 실사용 마모 테스트(sample-service 재설계 등).
