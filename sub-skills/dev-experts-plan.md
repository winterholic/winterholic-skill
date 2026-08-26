# dev-experts — 개발 전문가 스킬군 구축 계획

> 작성: 2026-06-10 · 상태: **계획 (착수 전)**
> 목표: stock-experts(21종, A 대역)에서 검증된 제작 공식을 이식해, **개발하면서 쓰일 가능성이 있는 전문가 스킬을 미리 전부 만들어둔다.**
> 배치 경로: `~/.claude\sub-skills\dev-experts\` (자동 로드 안 됨 — 디스패처 1개만 글로벌 상주)

---

## 1. 목표와 철학

- **"필요할 때 만든다" → "미리 만들어두고 꺼내 쓴다."** FastAPI 개발을 시작하는 날 FastAPI 전문가를 만들면 그 세션은 스킬 제작에 소모된다. 미리 만들어두면 첫 세션부터 전문가 품질로 개발한다.
- **레이어 분리 원칙**: Python 전문가 ≠ FastAPI 전문가 ≠ TDD 전문가. 언어/프레임워크/방법론/인프라/유틸은 별개 전문가다(주식에서 deepvalue ≠ trend ≠ portfolio-risk인 것과 동일). 한 작업에 여러 전문가가 조합된다(예: FastAPI 개발 = python + fastapi + rest-api-design + testing).
- **거장 앵커링**: 각 스킬은 "그 분야 최고 전문가의 머리"를 빌린다 — Spring이면 김영한·토비(이일민), Python이면 Fluent Python·PEP, Refactoring이면 마틴 파울러. 일반론이 아니라 **그 거장이 실제로 가르치는 기준·함정**을 박는다.
- **안티패턴 우선**: 기술 스킬의 가치 절반은 "하지 말 것"에 있다. 잘 하는 법은 LLM이 이미 알지만, **흔한 함정을 일관되게 피하게 만드는 것**이 스킬의 역할(주식에서 실패 실증·LTCM·ARK를 박은 것과 같은 원리).

## 2. stock-experts에서 검증된 공식 (그대로 이식)

| 공식 | stock-experts에서의 형태 | dev-experts 이식 |
|---|---|---|
| 디스패처 + 라우터 | 글로벌 1줄 디스패처 → CIO 라우터 → 전문가 1~3명 | 동일: `dev-experts` 디스패처 → `dev-chief-architect` 라우터 |
| 강한 frontmatter | What + 트리거 10개+ + SKIP 조건 | 동일 (트리거에 한·영 키워드, 파일 확장자·에러 메시지 패턴 포함) |
| 경계 표 | "이 스킬 vs 다른 스킬" 표 | 동일 (python vs fastapi vs testing 경계 명시) |
| 정량 기준 | NCAV 2/3, PEG<1, −7~8% 손절 | 설정 기본값·임계치 (커넥션 풀 크기, 타임아웃, 인덱스 기준, 커버리지 목표 등) |
| ❌/✅ 대비 예시 | 작성 예시 + 나쁜/좋은 판단 | **안티패턴 카탈로그 — 스킬당 최소 5쌍** (핵심 차별점) |
| 실증·실패 사례 | LTCM·ARK −80%·Knight | **유명 장애 포스트모템** (GitLab DB 삭제, Cloudflare regex, AWS S3 typo, 카카오 DC 화재 등) |
| scripts 계산기 | 표준 라이브러리 계산기 19개 | **스캐폴딩·검증 스크립트** (보일러플레이트 생성, 설정 lint, 체크리스트 실행) |
| references 3~4겹 | 원전·심화·실증 | 원전 요약 · 안티패턴 심화 · 실전 체크리스트 · evidence(장애 사례) |
| 사후 채점 (scorecard) | 분석 예측 채점·3회 룰 | **트러블슈팅 일지** 변형 — §10 참조 |
| skills-estimate 게이트 | 등급 B+ → A 반복 채점 | Phase별 일괄 채점, **85점(B+) 미만 출고 금지** |

## 3. 기술 스킬만의 차이점 3가지 (주식과 다른 설계 포인트)

1. **시효성(부패 속도)**: 그레이엄은 90년 가지만 Next.js는 18개월이면 낡는다. → 전 스킬 frontmatter에 **기준 버전·작성일 의무**(`기준: Python 3.12 / FastAPI 0.115 (2026-06)`), README에 분기 점검 목록. 부패 빠른 스킬(프론트엔드·클라우드)은 "공식 문서 우선, 스킬은 원칙·함정 위주" 구조로 써서 부패 면적을 줄인다.
2. **검증 가능성**: 주식 분석은 결과가 수개월 뒤에 오지만 코드는 **즉시 실행 검증**된다. → scripts는 계산기가 아니라 실행 가능한 스캐폴딩·체크 도구. 스킬 예시 코드는 작성 시점에 실제 실행해 검증(stock-experts의 "스크립트 전수 실행" 규율 유지).
3. **오픈소스 생태계 존재**: 주식 스킬은 무에서 만들었지만 개발 스킬은 **이미 시장이 있다**(anthropics/skills, 커뮤니티 마켓플레이스, awesome-claude-skills 류). → §7 수집 전략으로 기존 스킬을 분석·흡수하되, 그대로 복사하지 않고 "장점 + 그 스킬이 빠진 함정(안티패턴)"을 추출해 우리 템플릿에 재조립. 라이선스 확인·출처 표기 필수.

## 4. 아키텍처

```
~/.claude\
├── skills\
│   └── dev-experts\SKILL.md          # 글로벌 디스패처 (상주 1줄 — 유일한 컨텍스트 비용)
└── sub-skills\
    ├── dev-experts-plan.md            # 이 문서
    └── dev-experts\
        ├── README.md                  # 카탈로그 + 공통 규칙 (버전 라벨·안티패턴 우선·검증 명령·트러블슈팅 일지)
        ├── dev-chief-architect\       # 라우터: 작업 분해 → 전문가 1~3 조합 + eval 평가표
        ├── dev-python\                # SKILL.md + references\ + scripts\
        ├── dev-fastapi\
        ├── ... (카탈로그 전체)
        └── troubleshooting\ledger.md  # 트러블슈팅 일지 (append-only)
```

- 디스패처 트리거: 개발 작업 전반("구현해줘", "API 만들어", 에러 메시지, 리팩터링, 설계 질문...) — 단 **프로젝트 자체 CLAUDE.md·프로젝트 스킬이 있으면 그쪽이 우선**(디스패처에 명시).
- 라우터(dev-chief-architect): 작업을 [언어 × 프레임워크 × 방법론 × 품질] 축으로 분해해 조합 호출. 충돌 조율 규칙(예: "빠른 프로토타입 vs TDD"는 모순이 아니라 단계 차이 — 시간축 분리의 이식).
- 명명 규칙: `dev-` 접두사 (stock-experts의 `stock-`과 동일 패턴).

## 5. 전문가 카탈로그 (총 95 = 전문가 93 + 메타 2) — 2026-06-10 최대 확장판

> 선정 기준: "혹시 쓸지도 모르는가?"에 예라면 포함. 단 깊이는 2계층(§9)으로 차등.
> 명시적 제외(최종): PHP·Ruby·Swift/iOS네이티브·게임엔진(Unity/Unreal)·블록체인/웹3·하드웨어 설계(FPGA/회로) — 현재 접점 0이고, 필요해지면 그때 1세션으로 추가 가능한 게 이 체계의 장점. 이 제외 목록 밖에서 "쓸지도 모르는" 후보는 더 이상 없다고 판단함.
> 일상·비개발 전문가는 별도 스킬군 — `life-experts-plan.md` 참조.

### A. 언어 코어 (7)
| 스킬 | 거장/원전 앵커 | 핵심 안티패턴 영역 |
|---|---|---|
| dev-python | *Fluent Python*(Ramalho)·*Effective Python*(Slatkin)·PEP 8/20/484 | mutable default, 동기/비동기 혼용, 패키징 |
| dev-typescript | *Effective TypeScript*(Vanderkam)·TS 공식 핸드북 | any 남용, 타입 단언, enum 함정 |
| dev-javascript | *You Don't Know JS*(Simpson)·MDN | this·클로저·이벤트루프 오해, == 비교 |
| dev-java | *Effective Java*(Bloch)·*모던 자바 인 액션* | equals/hashCode, 원시 컬렉션, 체크예외 남용 |
| dev-go | 공식 *Effective Go*·Rob Pike proverbs | 고루틴 누수, 에러 무시, 인터페이스 남용 |
| dev-rust | *The Book*·*Rustonomicon* | clone 남발, unsafe 오용, 라이프타임 우회 |
| dev-sql | *Use The Index, Luke*(Winand)·*SQL Antipatterns*(Karwin) | N+1, 인덱스 미사용 패턴, 암시적 변환 |
| dev-c-cpp | K&R·*Effective Modern C++*(Meyers) | 메모리 관리·UB·RAII — 임베디드/성능 접점용 |
| dev-csharp-dotnet | 공식 문서·*C# in Depth*(Skeet) | async 데드락·LINQ 남용 |
| dev-kotlin | 공식 문서·코틀린 인 액션 | 자바 관성 코드·null 처리 우회 |

### B. 백엔드 프레임워크 (5)
| 스킬 | 앵커 | 비고 |
|---|---|---|
| dev-fastapi | tiangolo 공식 문서·full-stack-fastapi-template | 의존성 주입·async 함정·Pydantic v2 |
| dev-django | 공식 문서·*Two Scoops of Django* | ORM N+1·마이그레이션·설정 분리 |
| dev-spring | **김영한 커리큘럼 구조**·토비의 스프링 | DI·AOP·트랜잭션 경계 — "왜" 중심 |
| dev-spring-jpa | 김영한 JPA·*Java Persistence* | 영속성 컨텍스트·N+1·fetch 전략 (Spring과 분리 — 함정 밀도가 별개 스킬감) |
| dev-nestjs | 공식 문서·Node 생태계 관행 | 모듈 설계·DI 스코프 |

### C. 프론트·클라이언트 (8)
| 스킬 | 앵커 |
|---|---|
| dev-react | react.dev 신공식 문서(Dan Abramov 멘탈모델)·useEffect 함정 |
| dev-nextjs | 공식 문서 — **부패 최속(最速) 스킬: 버전 라벨 필수** |
| dev-css-tailwind | 공식 문서·Refactoring UI(디자인 감각) |
| dev-vue | 공식 문서 (Phase 3) |
| dev-mobile-flutter | 공식 문서 — 크로스플랫폼 모바일 1순위 후보 |
| dev-mobile-react-native | 공식 문서·Expo — React 자산 재활용 경로 |
| dev-electron-desktop | 공식 문서 — 데스크톱 앱(메모리·보안 함정) |
| dev-browser-extension | Chrome MV3 — 확장프로그램(개인 도구 제작에 유용) |

### D. 데이터·스토리지 (5)
| 스킬 | 앵커 |
|---|---|
| dev-postgres | 공식 문서·*The Art of PostgreSQL*(Fontaine) |
| dev-redis | 공식 문서·캐시 패턴(cache stampede·TTL 설계) |
| dev-database-modeling | 정규화·인덱스 설계·*Designing Data-Intensive Applications*(Kleppmann) 일부 |
| dev-mongodb | 공식 문서 (Phase 3) |
| dev-search | Elasticsearch/OpenSearch·전문검색·한국어 형태소 — "DB LIKE 검색"이 안티패턴이 되는 지점 |

### D2. 데이터 분석·AI (5)
| 스킬 | 앵커 / 비고 |
|---|---|
| dev-data-analysis | pandas·EDA·시각화 관행 — 주식 데이터 분석과도 직결 |
| dev-ml-basics | scikit-learn·고전 ML(분류·회귀·클러스터링) — stock-ml-alt-data와 경계: 그쪽은 금융 특화 검증론 |
| dev-computer-vision | OpenCV·객체 탐지 — **CCTV/Frigate 프로젝트 직결** |
| dev-media-ffmpeg | ffmpeg·영상/음성 처리(트랜스코딩·스트리밍·RTSP) — **CCTV·녹화 직결** |
| dev-math-stats | 개발자용 확률·통계·선형대수 — 다른 스킬들의 수학 기초 공급자 |

### E. 인프라·운영 (10)
| 스킬 | 앵커 |
|---|---|
| dev-docker | 공식 문서·멀티스테이지·이미지 경량화 안티패턴 |
| dev-linux-ops | 셸 관행·systemd·홈서버 운영(사용자 ubuntu-01 환경 반영) |
| dev-cicd | GitHub Actions 중심 + 일반 원칙(캐시·시크릿·배포 전략·롤백) |
| dev-nginx | 공식 문서·리버스 프록시·TLS 설정 |
| dev-monitoring | Prometheus/Grafana/Loki·SLO 사고방식(구글 SRE) |
| dev-networking | *TCP/IP Illustrated*(Stevens)·HTTP/1.1→3·DNS·TLS + 홈 네트워크(공유기·VPN·포트포워딩·DDNS) |
| dev-messaging-queue | Kafka·RabbitMQ·Redis Streams — 멱등성·DLQ·재처리·순서 보장 (event-driven에서 인프라 실무 분리) |
| dev-backup-dr | 백업·복구 전략(3-2-1 규칙·복구 리허설) — 홈서버 14개 서비스 직결 |
| dev-kubernetes | 공식 문서 (Phase 3 — 홈서버 규모에선 후순위) |
| dev-cloud-aws | Well-Architected (Phase 3) |
| dev-iac | Terraform·Ansible — **ServerManager 레포(홈서버 관리) 직결**, 스노우플레이크 서버 안티패턴 |
| dev-virtualization | Proxmox·VM/LXC — 홈서버 가상화 |
| dev-storage-nas | RAID·ZFS·SMB/NFS — NAS·스토리지 설계(백업과 분리: 이쪽은 저장 계층) |
| dev-dns-domain-email | 도메인·DNS 레코드·이메일 인증(SPF/DKIM/DMARC) — **자기 도메인(example-domain.com) 운영 직결** |
| dev-incident-response | 장애 대응 절차·포스트모템 작성(blameless) — 구글 SRE |

### F. 방법론·설계 (9)
| 스킬 | 거장 앵커 | 비고 |
|---|---|---|
| dev-tdd | 켄트 벡 *Test-Driven Development* | red-green-refactor 실제 리듬 + "TDD가 안 맞는 곳"도 정직하게 |
| dev-ddd | 에반스·버논(*구현 DDD*) | 전술 패턴보다 **유비쿼터스 언어·바운디드 컨텍스트** 우선 |
| dev-msa | 샘 뉴먼 *마이크로서비스 아키텍처 구축* | **"모놀리스 먼저"를 1원칙으로** — MSA 과적용이 최대 안티패턴 |
| dev-clean-architecture | 밥 마틴 + **비판(과도한 추상화 비용)을 같은 비중으로** | 주식 스킬의 "비판과 한계" 정신 |
| dev-refactoring | 마틴 파울러 *Refactoring* 2판 | 코드 냄새 카탈로그·작은 단계 |
| dev-design-patterns | GoF + 현대적 재해석("패턴 강박" 경계) | |
| dev-rest-api-design | RESTful 관행·Stripe/GitHub API 사례 | 버저닝·페이지네이션·에러 스키마 |
| dev-event-driven | Kleppmann·카프카 관행 | 멱등성·순서 보장·아웃박스 패턴 |
| dev-code-review | 구글 엔지니어링 가이드 | 리뷰 문화·코멘트 작법 |
| dev-system-design | 대용량 시스템 설계(*System Design Interview*류) | 캐파 산정·병목 — 면접 겸용 |
| dev-distributed-systems | Kleppmann *DDIA* 본진 | CAP·합의·복제 지연 — 분산의 근본 원리 |
| dev-legacy-code | Feathers *Working Effectively with Legacy Code* | 테스트 없는 코드 길들이기·심 기법 |
| dev-api-integration | 외부 API 연동 일반 | 인증·재시도·백오프·웹훅 수신·서킷브레이커 |
| dev-payments | PG 연동·정기결제 | 멱등키·이중결제·웹훅 검증·환불 흐름 |
| dev-notification | 푸시·이메일·SMS 발송 시스템 | 발송 큐·수신 동의·도달률 |

### G. 품질·보안 (5)
| 스킬 | 앵커 |
|---|---|
| dev-testing | 테스트 피라미드·pytest/jest 구체 관행·*xUnit Test Patterns* |
| dev-web-security | OWASP Top 10·실제 침해 사례 |
| dev-auth | OAuth2/OIDC/JWT/세션 — 직접 구현 금지 영역 명시 |
| dev-performance | 측정 우선(프로파일링)·*Systems Performance*(Gregg) 사고방식 |
| dev-error-logging | 구조적 로깅·에러 추적·관측 가능성 |
| dev-load-testing | k6/locust — 부하 시나리오 설계·병목 해석 |
| dev-cryptography | 암호화 실무(해시·대칭/비대칭·키 관리) — **"직접 구현 금지" 영역 명시가 본체** |
| dev-privacy-compliance | 개인정보보호법·GDPR 기초 — 수집 최소화·파기·동의 설계 |
| dev-dependency-security | 공급망 보안·취약점 스캔·버전 고정 전략 |

### H. 유틸·도구 (8)
| 스킬 | 비고 |
|---|---|
| dev-git-advanced | rebase·bisect·worktree·복구 시나리오 |
| dev-regex | 패턴 라이브러리 + ReDoS 함정(Cloudflare 사례) |
| dev-web-scraping | Playwright/bs4 — robots·약관 준수 명시 |
| dev-data-viz | matplotlib/차트 선택 가이드 |
| dev-bot-building | 텔레그램/디스코드 봇(사용자의 monitoring-discord-bot 운영 경험 반영) |
| dev-cron-scheduling | APScheduler/cron/스케줄 설계(사용자의 collector 경험 반영) |
| dev-geo-maps | 지도 API·좌표계·거리 계산 — **여행가챠(tour-data) 직결** |
| dev-seo-analytics | 검색 노출(SEO)·이벤트 추적 설계(GA류) — 웹 서비스 운영 |
| (등재) pptx·pdf·xlsx·docx | 기존 sub-skills 보유 — 신규 제작 없이 README 카탈로그에 등재만 |
| (등재) systematic-debugging·mcp-builder·webapp-testing 등 | 기존 글로벌 스킬 — 카탈로그에 경계만 명시(중복 제작 금지) |

### I. 특수 도메인·CS 기초 (11) — "혹시 쓸지도 모르는 것까지"
| 스킬 | 앵커 / 비고 |
|---|---|
| dev-hardware | PC 부품·조립·호환성·스펙 읽기 + **중고/신품 구매 사기 체크리스트**(사용자 피해 경험 반영) |
| dev-llm-engineering | LLM 앱 개발(프롬프트·RAG·에이전트·평가) — claude-api 글로벌 스킬과 경계: 그쪽은 API 레퍼런스, 이쪽은 설계 |
| dev-data-engineering | 수집·ETL 파이프라인·스케줄링·결측 처리 — **sample-service collector 재설계 직결** |
| dev-concurrency | 동시성·병렬성 일반(스레드·락·async 모델·경쟁 조건) — 언어 불문 원리 |
| dev-realtime | WebSocket·SSE·폴링 — 실시간 통신 설계 |
| dev-iot-raspberry | 라즈베리파이·IoT·홈 자동화 — CCTV/Frigate 프로젝트 연관 |
| dev-windows-powershell | Windows 개발 환경·PowerShell 관행(사용자 주 환경) |
| dev-algorithms | 자료구조·알고리즘·복잡도 — 코딩테스트 겸용 |
| dev-cs-fundamentals | OS·메모리·프로세스·파일시스템 동작 원리 |
| dev-tech-writing | 기술 문서·README·ADR 작성 |
| dev-opensource-license | 라이선스(GPL/MIT/Apache) 판단·의무사항 |

### J. 메타 (2)
| 스킬 | 역할 |
|---|---|
| dev-chief-architect | 라우터 — 작업 분해(언어×프레임워크×방법론×품질) → 전문가 조합 + 충돌 조율 + eval 평가표 |
| (규칙) troubleshooting ledger | 별도 스킬이 아니라 README 공통 규칙 — §10 |

## 6. 스킬당 품질 기준 (DoD — 이거 못 채우면 미완성)

- [ ] frontmatter: What + 트리거 10개+(한·영, 에러 메시지·확장자 포함) + SKIP 3개+(인접 스킬 리다이렉트)
- [ ] **기준 버전·작성일** 명시 (frontmatter 또는 정체성 직하)
- [ ] 정체성: 거장/원전 앵커 + 그 거장의 핵심 한 문장
- [ ] 경계 표: 인접 전문가와의 분담
- [ ] **안티패턴 카탈로그 ❌/✅ 5쌍 이상** (각각 "왜 나쁜가" 포함)
- [ ] 정량 기준: 설정 기본값·임계치 (불확실하면 "확인 필요")
- [ ] 워크플로우 + 출력 템플릿 + 작성 예시
- [ ] **실전 케이스 1개+**: 유명 장애 포스트모템 (그 스킬 규칙의 "왜"를 증명하는 사례)
- [ ] scripts: 스캐폴딩 또는 검증 스크립트 1개+ (**작성 시 실제 실행 검증**)
- [ ] references 3~4겹 (Phase 3 스킬은 1겹 허용 — §9 2계층)
- [ ] 한계 섹션 ("이 방법론이 안 맞는 상황"을 정직하게 — clean-architecture·MSA·TDD 특히)
- [ ] skills-estimate **85점(B+) 이상**

## 7. 오픈소스 스킬 수집·흡수 전략

1. **탐색**: `/find-skills` + anthropics/skills 공식 레포 + 커뮤니티 목록(awesome-claude-skills 류, 시점 기준 최신을 WebSearch로) — 스킬당 후보 1~3개 수집.
2. **분석 프레임** (그대로 복사 금지):
   - 흡수: 정량 기준·체크리스트·트리거 키워드 중 우리 템플릿에 없는 것
   - **역흡수(더 중요)**: 그 스킬이 빠뜨린 함정 = 우리 안티패턴 섹션의 재료
   - 검증: 그 스킬의 주장(버전·설정값)을 공식 문서와 대조 — 오픈소스 스킬은 부패한 경우가 많음
3. **라이선스**: 차용 시 references에 출처(레포·라이선스) 표기. 의심스러우면 재작성.
4. 공식 1차 소스가 항상 우선: 공식 문서 > 거장 원전 > 오픈소스 스킬 > 블로그.

## 8. 제작 파이프라인 (스킬 1개당 3-pass — stock-experts 검증 절차)

```
Pass 1 생성: 소스 수집(§7) → skill-creator로 초안 → 템플릿 정합
Pass 2 채점: skills-estimate → 약점 Top 3 → 보강 (85 미만이면 반복)
Pass 3 무장: 안티패턴 5쌍+ / 실전 케이스 / scripts 실행 검증 / 버전 라벨
```

세션당 처리량 추정: 풀스펙 4~6개 (stock-experts 실측 기준 — 한 세션에서 19 scripts + 20 케이스 + 20 심화를 처리했으므로 보수적 추정).

## 9. Phase 계획 (우선순위 = 사용 확률 × 사전 제작 이득)

| Phase | 내용 | 수량 | 세션 추정 |
|---|---|---|---|
| **0. 인프라** | README(공통 규칙)·dev-chief-architect 라우터·글로벌 디스패처·스킬 템플릿 보일러플레이트 | 4파일 | 0.5 |
| **1. 현재 스택 코어** | python, fastapi, typescript, react, nextjs, postgres, docker, linux-ops, cicd, tdd, rest-api-design, testing, **data-engineering**(sample-service 직결) | 13 | 2~3 |
| **2. 확장(방법론+백엔드+홈서버)** | spring, spring-jpa, django, nestjs, ddd, msa, clean-architecture, refactoring, design-patterns, event-driven, messaging-queue, redis, database-modeling, web-security, auth, monitoring, error-logging, code-review, networking, backup-dr, **computer-vision, media-ffmpeg**(CCTV 직결), **dns-domain-email, iac**(홈서버 직결) | 24 | 4~5 |
| **3. 롱테일+유틸+클라이언트** | go, rust, sql, javascript, vue, css-tailwind, mongodb, k8s, nginx, aws, performance, git-advanced, regex, scraping, data-viz, bot-building, cron, llm-engineering, concurrency, realtime, windows-powershell, data-analysis, search, geo-maps, seo-analytics, mobile-flutter, mobile-react-native, electron-desktop, browser-extension + 기존 유틸·글로벌 스킬 등재 | 29+5 | 4~5 |
| **4. 특수·연동·심화** | hardware, iot-raspberry, algorithms, cs-fundamentals, tech-writing, opensource-license, c-cpp, csharp-dotnet, kotlin, ml-basics, math-stats, virtualization, storage-nas, incident-response, system-design, distributed-systems, legacy-code, api-integration, payments, notification, load-testing, cryptography, privacy-compliance, dependency-security | 24 | 3~4 |
| 합계 | | **95** | **14~18 세션** |

- **2계층 전략**: Phase 1·2는 풀스펙(DoD 전체). Phase 3는 **코어스펙**(SKILL.md + evidence 1겹 + 안티패턴 5쌍, scripts 생략 가능)으로 출고하고, 실사용 발생 시 풀스펙 승격. 47개 전부 풀스펙은 유지비가 효익을 넘는다 — "최대한 다 만들되, 깊이는 사용 확률에 비례."
- Phase 1 선정 근거: 사용자 현재 프로젝트(sample-service FastAPI·collector·홈서버·RemoteCode)의 실스택.
- 각 Phase 종료 시: skills-estimate 일괄 채점 + 라우터 eval 문항 추가 + README 카탈로그 갱신.

## 10. 피드백 루프 — 트러블슈팅 일지 (stock-scorecard의 이식)

주식의 "예측 채점"에 해당하는 개발의 등가물은 **"같은 삽질 두 번 안 하기"**다:

- 디버깅·삽질이 30분을 넘긴 문제가 해결되면 `troubleshooting/ledger.md`에 1행: `날짜 | 스택 | 증상 | 근본 원인 | 해결 | 관련 스킬 | 스킬에 있었나(Y/N)`.
- **"스킬에 있었나 = N"이 3회 누적된 패턴** → 해당 스킬의 안티패턴 섹션에 추가 (3회 룰 그대로 이식 — 일화 과적합 방지).
- 이 루프가 스킬군을 "내 삽질 데이터로 단련된" 고유 자산으로 만든다 — 오픈소스 스킬과의 장기적 차별점.

## 11. 시효성 관리 (기술 스킬 고유 리스크)

- 전 스킬 frontmatter 직하에 `> 기준: <스택> <버전> (YYYY-MM)` 의무.
- README에 **부패 속도 3등급** 분류: 빠름(nextjs·react·클라우드 — 분기 점검) / 중간(프레임워크·인프라 — 반기) / 느림(언어 코어·방법론 — 연 1회).
- 점검 = 버전 라벨 갱신 + 깨진 정량 기준 수정. 전면 재작성 아님(원칙·안티패턴은 오래 감).

## 12. 리스크와 반례 (정직하게)

- **재고 과잉**: 47개 중 절반은 안 쓰일 수 있다 → 2계층 전략 + Phase 3 코어스펙으로 제작비 절감. "만든 것"보다 "안 만들 것"(예: 지금 안 쓰는 PHP·Ruby·Swift)을 명시하는 것도 결정.
- **프로젝트 CLAUDE.md와의 충돌**: 프로젝트별 컨벤션이 전문가 일반론과 다를 수 있음 → 디스패처에 "프로젝트 규칙 > 전문가 스킬" 우선순위 명문화.
- **LLM이 이미 아는 것의 재포장 위험**: "Python은 가독성이 중요합니다" 같은 내용이면 만들 가치 없음 → DoD의 안티패턴 5쌍·정량 기준·실전 케이스가 이 함정의 방어선. 채점에서 일반론 스킬은 탈락시킨다.
- **시효성 미관리 시 역효과**: 낡은 스킬은 없는 것보다 나쁨(자신 있게 틀림) → §11 필수.

## 13. 다음 액션

1. [ ] Phase 0: README + 라우터 + 디스패처 + 템플릿 (다음 세션, 이 문서를 핸드오프 삼아)
2. [ ] Phase 1 첫 배치: dev-python, dev-fastapi, dev-tdd, dev-testing (현 sample-service 재설계와 직결되는 4종 우선)
3. [ ] /find-skills로 기존 오픈소스 스킬 1차 탐색 (python·fastapi·react 후보 수집)
4. [ ] Phase 1 완료 후 sample-service 재설계에 실전 투입 → 트러블슈팅 일지 가동 (스킬 마모 테스트를 데이터 프로젝트로)
