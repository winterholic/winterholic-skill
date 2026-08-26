# evidence + 출고 전 체크리스트

## 실증·출처

- **GitLab DB 사고 postmortem (2017-01-31)** — 5중 백업 전부 미작동, 6시간 손실. SKILL.md 실전 케이스. "백업 여러 개 ≠ 안전, 검증된 복구 = 안전"의 결정적 실증. 1차 출처(GitLab 공식 사후분석 블로그): https://about.gitlab.com/blog/gitlab-dot-com-database-incident/ — pg_dump가 PostgreSQL 9.2 바이너리로 9.6 DB를 덤프하려다 수 바이트짜리 빈 파일만 생성한 게 "파일 존재≠유효"의 직접 근거.
- **3-2-1 규칙** — Peter Krogh, *The DAM Book: Digital Asset Management for Photographers* (O'Reilly, 2009)에서 정식화(사진 데이터 관리) → 업계 표준. CISA·NIST가 베이스라인으로 채택(아래 #StopRansomware 가이드).
- **카카오 데이터센터 화재 (2022-10-15)** — SK C&C 판교 데이터센터 화재(원인: 리튬이온 배터리), 단일 데이터센터 의존으로 카카오톡 등 광역 서비스가 장시간 중단. 오프사이트(3-2-1의 1) 부재의 실증. 출처: DataCenterDynamics https://www.datacenterdynamics.com/en/news/sks-li-ion-batteries-blamed-for-data-center-fire-behind-kakao-outage/
- **PostgreSQL 공식 문서 — Backup and Restore·Continuous Archiving (PITR)·pg_verifybackup** — DB 백업 3형의 1차 출처(현행 PG 18에 존재). pg_verifybackup은 pg_basebackup 백업을 backup_manifest와 대조 검증하되 공식 문서 스스로 "test restore는 여전히 수행하라"고 명시 — 리허설 격상의 1차 근거. https://www.postgresql.org/docs/current/app-pgverifybackup.html
- **랜섬웨어 대비 불변 백업** — CISA #StopRansomware Guide(2023, CISA·MS-ISAC·NSA·FBI 공동, CISA·NIST CPG 정렬): 백업은 오프라인 유지·정기 테스트·object lock/delete protection 권고. https://www.cisa.gov/stopransomware/ransomware-guide — 최근에는 불변/에어갭 1개 + 복구 0-에러를 더한 **3-2-1-1-0**로 확장(NIST SP 800-184, CSF 2.0 정렬).
- 오픈소스 차용 표기: 백업 가이드 다수(색인 인지, 본문 비복사). **역흡수**: 복구 리허설을 백업의 정의로 격상·RPO/RTO를 데이터별 차등·재수집 가능성(dev-data-engineering)과 연계·정책 감사 자동화 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (백업·DR 출고 시)

- [ ] 복구 리허설 1회+ 완료 (RTO 실측) — `backup_audit.py` 0건
- [ ] 3-2-1 충족 (사본 3·매체 2·오프사이트 1)
- [ ] 데이터별 RPO/RTO 합의됨 (재수집 가능 구분)
- [ ] 백업 직후 무결성 검증 (체크섬/테스트 복원/행수)
- [ ] 불변/오프라인 사본 1개 (랜섬웨어)
- [ ] 백업 암호화 + 키 분리 보관
- [ ] 자동 스케줄 + 마지막 성공 모니터링 + 실패 경보
- [ ] 복구 런북 문서화 (리허설로 검증)
- [ ] 인프라 구성도 백업 대상(ServerManager 레포 — dev-iac)

## 점검 주기 (부패 느림 — 연 1회, 단 리허설은 분기)

- **분기**: 복구 리허설 실행 (이것만은 연 1회로 미루지 않는다)
- 연: 3-2-1 구성·RPO/RTO 재평가·백업 키 접근 점검
