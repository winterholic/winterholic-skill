# 엔지니어링 조직 스케일 — Team Topologies · Dunbar · span-of-control

> 조직 구조는 단계에 맞게 **분화(고통이 생긴 곳만)**. 앞선 단계 복붙 금지(안티패턴 2).

## 1. Team Topologies — 4팀 유형 (Skelton & Pais, 2019)
콘웨이 법칙("시스템 구조는 그것을 만든 조직의 소통 구조를 닮는다")을 역이용 → 원하는 아키텍처를 얻으려면 조직을 먼저 그렇게 짠다(inverse Conway maneuver).

| 팀 유형 | 역할 | 목표 |
|---|---|---|
| **Stream-aligned** (핵심) | 하나의 가치 흐름(제품·기능·사용자 세그먼트)을 end-to-end 담당 | 고객 가치 직접 전달, 대부분의 팀은 이 유형 |
| **Platform** | 내부 서비스(배포·관측·인증 등)를 셀프서비스로 제공 | stream-aligned 팀의 **인지 부하 감소** |
| **Enabling** | 특정 역량(테스트·보안·클라우드)을 다른 팀에 심어줌 | 다른 팀이 자립하게 코칭, 한시적 |
| **Complicated-subsystem** | 깊은 전문지식이 필요한 부분(ML·비디오코덱·결제엔진) | 전문성 집중, stream 팀 인지 부하 감소 |

**3가지 상호작용 모드**: Collaboration(밀착 협업, 한시적) · X-as-a-Service(서비스 소비, 저마찰) · Facilitating(코칭).

**핵심 개념 — 인지 부하(cognitive load)**: 팀이 감당할 도메인·책임에는 자연 한계가 있다. 너무 넓으면 "얇게 퍼져" 전달이 무너진다. Platform·Complicated-subsystem·Enabling 팀은 모두 **stream 팀의 인지 부하를 줄이기 위해** 존재. → 플랫폼팀을 "언제 만드나"의 답: stream 팀들이 인프라 인지부하로 느려지는 고통이 실제로 생겼을 때(예방적 분화 금지).
> 근거: https://teamtopologies.com/key-concepts · Fowler https://martinfowler.com/bliki/TeamTopologies.html

## 2. Dunbar 계층 — 조직 크기의 인지 한계
Robin Dunbar: 인간이 유지 가능한 안정적 관계 수 = 신피질 한계. **중첩 계층**:
- **~5**: 긴밀한 핵심(1:1 팀, 창업 코어)
- **~15**: 신뢰하는 협업자(하나의 스쿼드·부서)
- **~50**: 밀접한 업무 관계(사이트·트라이브)
- **~150**: 안정적 사회 관계 한계 — **이 선을 넘으면 공동체 감각이 무너지고 관료제가 들어선다**

조직 설계 함의: 150을 넘기 전에 **자율적 서브조직(팀-of-팀)으로 쪼갠다**. W.L. Gore가 공장을 150명으로 제한한 것이 유명 사례. 무조건 150 상한이 아니라, 인지 한계에 맞춰 작은 상호연결 팀으로 설계하라는 뜻.
> 근거: https://en.wikipedia.org/wiki/Dunbar%27s_number · 조직 적용 https://alamrafiul.com/blogs/dunbar-number/

## 3. Span of control — Larson 원전 수치
Will Larson "Sizing engineering teams":
- **매니저 1인당 엔지니어 6~8명** = 건강한 범위(코칭·조정·전략에 충분).
- **직속 4명 미만** → 사실상 **Tech Lead Manager**(설계·구현 겸함) — 풀타임 매니저 정당화 안 됨.
- **직속 8~9명 초과** → 매니저가 코치/안전망으로만 기능, 능동 투자 불가(과부하).
- **매니저-of-매니저는 매니저 4~6명** 지원.
> 근거: https://lethain.com/sizing-engineering-teams/ (An Elegant Puzzle 수록). `scripts/org_sizing.py`가 span 기본 6으로 계산.

## 4. 단계별 조직 (복붙 실패 = 안티패턴 2)
| 단계 | 구조 | Team Topologies 관점 |
|---|---|---|
| ~10명 | 단일 팀, CTO 직접 관리, 제너럴리스트 | stream-aligned 1개 |
| 10~30명 | 첫 매니저(들), 2~3 기능팀 | stream-aligned 여러 개 |
| 30~80명 | 매니저 계층 2단, 플랫폼/인프라 분화 시작 | **고통 생긴 곳에** platform 팀 신설 |
| 80~150명 | 디렉터 계층, SRE/플랫폼 전담, enabling 팀 | complicated-subsystem 분리 |
| 150+ | 트라이브/그룹으로 분할(Dunbar) | 자율 서브조직, X-as-a-Service 중심 |

**실패 모드**: 30명인데 80명 구조(과분화 관료제) / 80명인데 10명 구조(CTO 병목).

## 5. 재조직(reorg)의 원칙
- reorg는 비용이 크다(관계·컨텍스트 리셋) → **문제가 명확할 때만**, 자주 하지 마라.
- 콘웨이 법칙을 의식: 원하는 아키텍처 경계 = 팀 경계로 설계.
- 재조직 성공 판정 지표를 사전에 정한다(리드타임·온콜 부하·인지부하 설문). 감으로 판단 금지.
