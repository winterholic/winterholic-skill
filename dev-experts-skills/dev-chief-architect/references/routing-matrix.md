# 라우팅 매트릭스 — 트리거 색인 · 호출 체인 · 평가표

## 목차
- 트리거 색인 (증상·키워드 → 전문가)
- 상호 호출 체인 (대표 작업 유형별)
- 라우팅 평가표 (eval 10문항)
- eval 운영 규칙

> 전문가 전체 카탈로그·Phase·제작 상태는 `../../README.md`가 원본이다(여기 중복 금지). 이 파일은 **라우팅 판단 보조**만 한다.

## 트리거 색인 (증상·키워드 → 전문가)

grep용 색인. 사용자 발화·에러 메시지에 아래 토큰이 보이면 해당 전문가가 1차 후보.

| 토큰(한·영·에러) | 전문가 |
|---|---|
| async, await, GIL, mutable default, venv, pip, "ModuleNotFoundError" | dev-python |
| "type 'any'", tsconfig, generic, "is not assignable to" | dev-typescript |
| Depends, Pydantic, "422 Unprocessable", uvicorn, APIRouter | dev-fastapi |
| useEffect, hook, 리렌더, "Too many re-renders", props | dev-react |
| hydration, "use client", App Router, ISR, vercel | dev-nextjs |
| 인덱스, EXPLAIN, vacuum, "deadlock detected", 커넥션 풀 | dev-postgres |
| N+1, 조인, 정규화, 스키마 설계, ERD | dev-database-modeling, dev-sql |
| Dockerfile, 이미지 크기, compose, "exited with code", 볼륨 | dev-docker |
| systemd, journalctl, cron 안 돎, 디스크 풀, ssh | dev-linux-ops |
| Actions, 파이프라인 실패, 배포 자동화, "workflow_dispatch" | dev-cicd |
| 수집기, 크롤링 스케줄, ETL, 결측, 멱등, 백필 | dev-data-engineering |
| 테스트 짜줘, fixture, mock, 커버리지, "flaky" | dev-testing |
| 레드그린, 테스트 먼저, red-green-refactor | dev-tdd |
| JWT, OAuth, 세션, 토큰 만료, refresh token | dev-auth |
| XSS, SQL injection, CSRF, OWASP, 시크릿 노출 | dev-web-security |
| 느려요, 병목, 프로파일링, 메모리 누수, CPU 100% | dev-performance |
| 로그 설계, Sentry, 구조적 로깅, 에러 추적 | dev-error-logging |
| 캐시, TTL, "cache stampede", 세션 스토어 | dev-redis |
| RTSP, 트랜스코딩, ffmpeg, 코덱, 스트리밍 | dev-media-ffmpeg |
| 객체 탐지, OpenCV, YOLO, 프레임 | dev-computer-vision |
| 텔레그램 봇, 디스코드 봇, webhook 봇 | dev-bot-building |
| RAG, 프롬프트, 에이전트 설계, 임베딩, 평가셋 | dev-llm-engineering |
| rebase, cherry-pick, "detached HEAD", reflog, bisect | dev-git-advanced |
| 정규식, "catastrophic backtracking", ReDoS | dev-regex |
| DNS, MX, SPF, DKIM, 도메인, 인증서 | dev-dns-domain-email |
| 백업, 복구, 스냅숏, 3-2-1 | dev-backup-dr |
| Kafka, RabbitMQ, DLQ, 컨슈머 랙, 재처리 | dev-messaging-queue |
| WebSocket, SSE, 실시간, 폴링 | dev-realtime |
| 스레드, 락, race condition, 데드락(코드) | dev-concurrency |
| 결제, PG, 웹훅 검증, 이중결제, 환불 | dev-payments |
| 모놀리스, MSA, 서비스 분리, 경계 | dev-msa, dev-ddd |
| 코드 냄새, 중복, 함수 추출, 레거시 | dev-refactoring, dev-legacy-code |
| PowerShell, cp949, 인코딩(Windows), 레지스트리 | dev-windows-powershell |
| goroutine, 채널, "concurrent map writes", go.mod | dev-go |
| borrow checker, unwrap, lifetime, cargo, unsafe | dev-rust |
| OFFSET, LIKE 검색, "인덱스 안 타", NOT IN, 풀스캔 | dev-sql |
| this undefined, Promise, unhandled rejection, 이벤트 루프 | dev-javascript |
| ref, reactive, v-for, Pinia, "반응성이 안 돼" | dev-vue |
| Tailwind, 클래스 안 먹어, @apply, 다크모드, flexbox | dev-css-tailwind |
| 위젯, setState, jank, isolate, pubspec | dev-mobile-flutter |
| Expo, FlatList, EAS, metro, 네이티브 모듈 | dev-mobile-react-native |
| BrowserWindow, ipcMain, preload, contextBridge | dev-electron-desktop |
| manifest.json, MV3, content script, chrome.storage | dev-browser-extension |
| $lookup, 16MB, COLLSCAN, mongoose, 도큐먼트 | dev-mongodb |
| pod, CrashLoopBackOff, OOMKilled, helm, kubectl | dev-kubernetes |
| proxy_pass, 502, location 블록, upstream, 413 | dev-nginx |
| EC2, S3, IAM, Lambda, 요금 폭탄, 프리티어 | dev-cloud-aws |
| 전문검색, nori, 형태소, Elasticsearch, 검색 품질 | dev-search |
| 좌표, 위도 경도, 지도 API, 반경 검색, geocoding | dev-geo-maps |
| SEO, 검색 노출, og:image, sitemap, canonical, GA | dev-seo-analytics |
| 스크레이핑, robots.txt, bs4, 셀렉터 깨짐, 403 차단 | dev-web-scraping |
| 차트, 그래프, matplotlib, 파이차트, 히스토그램 | dev-data-viz |
| pandas, DataFrame, EDA, 결측치, groupby, 이상치 | dev-data-analysis |
| crontab, APScheduler, misfire, 중복 실행, 배치 누락 | dev-cron-scheduling |
| segfault, valgrind, unique_ptr, UB, malloc | dev-c-cpp |
| async void, .Result, LINQ, EF Core, NuGet | dev-csharp-dotnet |
| 코틀린 !!, 코루틴, GlobalScope, suspend, lateinit | dev-kotlin |
| 시간복잡도, Big-O, 코딩테스트, 자료구조, DP, BFS | dev-algorithms |
| OOM Killed, "Too many open files", fsync, 좀비 프로세스, inode | dev-cs-fundamentals |
| p값, 표본, A/B 테스트, 상관 인과, 몬테카를로 | dev-math-stats |
| sklearn, 과적합, accuracy, train test split, 데이터 누출 | dev-ml-basics |
| Proxmox, VM, LXC, 패스스루, IOMMU, 스냅샷 | dev-virtualization |
| RAID, ZFS, NAS, scrub, SMART, RAIDZ | dev-storage-nas |
| 장애 대응, 포스트모템, 온콜, 타임라인, 재발 방지 | dev-incident-response |
| PC 조립, 견적, 중고 거래, 부팅 안 돼, POST, 파워 | dev-hardware |
| 라즈베리파이, GPIO, SD카드 죽음, undervoltage, Home Assistant | dev-iot-raspberry |
| README, ADR, 문서화, 온보딩 문서, 기술 문서 | dev-tech-writing |
| 라이선스, GPL, MIT, AGPL, 카피레프트, LICENSE | dev-opensource-license |
| 캐파, QPS, 동접, 설계 면접, SPOF, 확장성 | dev-system-design |
| CAP, 복제 지연, split brain, saga, 분산 트랜잭션, 합의 | dev-distributed-systems |
| 타임아웃, 재시도, 429, 서킷브레이커, 웹훅 수신 | dev-api-integration |
| 알림 발송, 푸시, FCM, SMTP, 스팸함, 수신 거부 | dev-notification |
| 부하 테스트, k6, locust, TPS, 동시 접속, stress | dev-load-testing |
| 암호화, bcrypt, AES, 해시, IV, nonce, 보안 난수 | dev-cryptography |
| 개인정보, GDPR, 동의, 파기, 보유 기간, 유출 신고 | dev-privacy-compliance |
| CVE, npm audit, lockfile, 공급망, Dependabot, SBOM | dev-dependency-security |

> 색인에 없는 토큰: README 카탈로그를 grep → 그래도 없으면 폴백 선언(라우터 절차 2).

## 상호 호출 체인 (대표 작업 유형)

```
신규 API 기능:   dev-rest-api-design(계약) → dev-fastapi(구현) → dev-testing(검증) → dev-cicd(배포)
데이터 파이프라인: dev-data-engineering(설계) → dev-postgres(적재) → dev-cron-scheduling(스케줄) → dev-monitoring(관측)
프론트 기능:     dev-react(구현) ↔ dev-typescript(타입) → dev-testing(검증)
운영 장애:       systematic-debugging(절차, 글로벌) + 해당 레이어 전문가(도메인) → dev-incident-response(사후)
보안 민감 기능:  dev-auth(설계) + dev-web-security(검토, veto급) → dev-testing
성능 문제:       dev-performance(계측 먼저) → 계측 결과가 가리키는 레이어 전문가 1명
CCTV 파이프라인: dev-computer-vision + dev-media-ffmpeg → dev-iot-raspberry → dev-linux-ops
```

규칙: 체인은 순서 제안일 뿐 전부 호출하라는 뜻이 아니다 — 현재 단계의 1~3명만.

## 라우팅 평가표 (eval 10문항)

각 문항: 입력(사용자 발화) → 기대 라우팅. 판정 = 1차 전문가 일치(필수) + 보강 합리성 + 과호출 없음(4명 이상이면 실패).

| # | 입력 | 기대 1차 | 기대 보강 | 함정 |
|---|---|---|---|---|
| 1 | "주식 시세 수집기 새로 짤 건데 구조 좀" | dev-data-engineering | dev-postgres, dev-cron-scheduling | stock-experts로 보내면 오답(분석 아님·코드 작업) |
| 2 | "FastAPI 응답이 422만 떠" | dev-fastapi 직행 | — | 라우터 경유 자체가 감점(스택 특정) |
| 3 | "로그인 기능 만들어줘" | dev-auth | dev-web-security(veto급) | auth 없이 프레임워크만 부르면 실패 |
| 4 | "이 코드 좀 깔끔하게" | dev-refactoring | dev-legacy-code(테스트 없을 때) | 테스트 유무 미확인 시 감점 |
| 5 | "서비스가 갑자기 죽어요" | systematic-debugging(글로벌) 우선 | 레이어 판명 후 전문가 | 라우터가 절차를 가로채면 오답 |
| 6 | "Next.js냐 그냥 React냐" | 라우터 직접(비교 프레임) | dev-nextjs 또는 dev-react 1명 | "둘 다 좋아요" 결론이면 실패 |
| 7 | "테스트도 없는 옛날 코드에 기능 추가" | dev-legacy-code | dev-testing | 바로 dev-tdd부터 부르면 감점(특성화 테스트 먼저) |
| 8 | "홈서버에 새 서비스 올리고 백업도" | dev-linux-ops | dev-docker, dev-backup-dr | 프로젝트(ServerManager) 규칙 우선 미언급 시 감점 |
| 9 | "삼성전자 지금 사도 돼?" | **라우팅 거부** → stock-experts | — | dev 전문가를 부르면 실패(경계 밖) |
| 10 | "API 응답이 느려진 것 같아" | dev-performance(계측 먼저) | 계측 후 해당 레이어 | 계측 없이 dev-postgres 추측 호출이면 감점 |

## eval 운영 규칙

- **실행 시점**: 새 Phase 출고 직후 + 라우팅 표를 수정했을 때. 10문항을 새 세션 관점으로 읽고 라우팅 표만으로 판정이 재현되는지 확인.
- **합격선**: 10문항 중 9 이상. 미달이면 라우팅 표·트리거 색인을 보강(전문가 스킬이 아니라 라우터를 고친다).
- **문항 추가**: 실사용에서 오라우팅이 발생하면 그 사례를 문항으로 추가(append). 기존 문항 수정 금지 — 회귀 검출용.
