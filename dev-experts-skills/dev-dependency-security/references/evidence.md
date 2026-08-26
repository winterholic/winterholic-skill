# dev-dependency-security evidence — 장애·실증 사례

## 1. Log4Shell (CVE-2021-44228) — 전이 의존성의 전국 소집령 (공개 대응 기록)

- **무슨 일**: log4j 2.x의 JNDI 룩업 — `${jndi:ldap://...}` 문자열이 **로그에 기록되기만 하면** 원격 클래스 로드·실행. User-Agent·검색어·닉네임 등 "로그에 찍힐 수 있는 모든 입력"이 공격 벡터가 돼 사실상 전 Java 서비스가 대상. 스캔·공격 시도가 공개 수 시간 내 시작.
- **대응을 가른 것**: ① 의존성 조회 체계(전이 포함) 보유 여부 — log4j는 직접보다 간접 유입이 많았다 ② 평소 업데이트 위생 — 구버전 고착 프로젝트는 호환성 작업부터 ③ 패치 추적 — 2.15가 불완전해 2.17까지 연쇄(1회성 대응 조직은 재노출).
- **교훈**: "우리 그거 쓰나"의 답변 속도가 보안 등급이다 — 그리고 그 답은 사고 당일이 아니라 평소의 lockfile·SBOM이 만든다.

## 2. event-stream(2018)·xz(2024) — 사람을 노린 공급망 (공개 분석)

- **event-stream**: 지친 유지자가 "돕겠다"는 새 기여자에게 npm 패키지 권한 양도 → 새 유지자가 특정 암호화폐 지갑을 노리는 악성 의존성을 주입 — 주간 수백만 다운로드 패키지가 몇 주간 오염. 표적이 좁아 일반 테스트로는 무증상.
- **xz utils**: 수년에 걸친 신뢰 구축(꾸준한 기여·압박 여론전까지)으로 공동 유지자가 된 인물이 sshd에 닿는 백도어를 주입 — 배포 직전 한 엔지니어의 성능 이상(0.5초) 추적으로 발각(2024-03). 오픈소스 역사상 가장 정교한 공급망 침투 시도로 기록.
- **공통 교훈**: 공격 대상이 코드가 아니라 **신뢰 구조**(번아웃된 유지자·권한 양도 관행)였다 — ① 핵심 의존성의 유지자 변경은 뉴스다(경계 신호) ② "1인 유지·핵심 인프라" 조합이 생태계의 구조적 약점 ③ 개인이 할 일: 유예 기간·버전 고정·최소 의존 — 막기보다 늦게 받기·적게 노출되기.

## 3. Codecov (2021) — CI가 공급망의 관문 (공개 사고)

- **무슨 일**: 커버리지 도구 Codecov의 bash 업로더 스크립트가 공격자에 의해 변조 — 이를 CI에서 `curl | bash`로 실행하던 수천 조직의 **CI 환경변수(클라우드 키·토큰)가 외부 전송**. 2개월간 미발각(스크립트 해시 검증으로 발견).
- **경로의 일반성**: "외부 스크립트를 CI에서 실행"은 보편 관행이었고, CI에는 시크릿이 몰려 있다 — 공급망 오염 1건이 수천 조직의 클라우드 열쇠로 직결된 증폭 구조.
- **방어 도출**: ① `curl | bash` 금지 — 버전 고정 다운로드 + 체크섬/서명 검증 ② CI 시크릿 잡별 최소 주입(테스트 잡에 배포 키가 있을 이유 없음 — 안티패턴 5) ③ CI 아웃바운드 트래픽 관찰(시크릿이 나가는 길목) ④ 사고 시: 그 CI를 거친 모든 시크릿은 유출 간주·전량 회전(dev-git-advanced #4와 동일 — 회전이 1순위).

> 출처(1차·공식 우선, 2026-06 웹 확인):
> - Log4Shell: NVD CVE-2021-44228(CVSS 10.0 공식 스코어) https://nvd.nist.gov/vuln/detail/CVE-2021-44228 · 패치 연쇄 2.15→2.16→2.17→2.17.1(CVE-2021-45046/45105/44832) https://en.wikipedia.org/wiki/Log4Shell
> - event-stream: npm 공식 사후 공지(유지자 권한 양도→flatmap-stream 주입→Copay 지갑 표적) https://blog.npmjs.org/post/180565383195/details-about-the-event-stream-incident
> - xz: NVD CVE-2024-3094(CVSS 10.0) https://nvd.nist.gov/vuln/detail/CVE-2024-3094 · Freund의 oss-security 최초 보고(2024-03-29, ~0.5초 SSH 지연 추적) https://www.openwall.com/lists/oss-security/2024/03/29/4
> - Codecov: 공식 보안 공지(bash 업로더 변조, ~2개월 미발각, CI 환경변수 유출) https://about.codecov.io/security-update/
> - Equifax(SKILL.md 본문): NVD CVE-2017-5638(Apache Struts) https://nvd.nist.gov/vuln/detail/CVE-2017-5638 · 약 1.47억 명 영향(미 의회 조사 보고서) https://en.wikipedia.org/wiki/2017_Equifax_data_breach
> 보조 교차확인: Snyk·Akamai·Datadog 등 업계 사후 분석. 위 URL은 본 감사에서 실제 응답 확인.
