# dev-search evidence — 장애·실증 사례

## 1. 공개 Elasticsearch 유출 장르 — "내부 인프라"라는 착각 (보안 연구 집계)

- **무슨 일**: 무인증 공개 ES에서 대규모 개인정보 발견 사고가 장르적으로 반복 — 수억 건 규모 사례 다수(보안 연구자들의 Shodan 스캔 발굴). 원인은 취약점이 아니라 9200 포트 공개 바인딩 + 인증 미설정.
- **구조적 원인**: 검색 색인은 "원본은 DB에 있으니 사본일 뿐"이라는 감각으로 보안 우선순위가 밀린다 — 그러나 색인에는 검색을 위해 **가장 민감한 필드가 평문으로** 들어간다.
- **방어**: ① 인증 활성(현 버전 기본) + 내부망 바인딩 + 방화벽 ② 스냅샷 정기화(색인도 복구 대상) ③ 외부 점검: 공인 IP에서 `curl http://<ip>:9200` 1회.

## 2. nori 형태소 분석 — 전후 비교 실증 (한국어 검색의 분수령)

- **무슨 일**: standard analyzer는 "삼성전자가 신제품을 발표했다"를 공백 기준 [삼성전자가, 신제품을, 발표했다]로 토큰화 — "삼성전자"·"신제품"·"발표" 검색이 전부 미스. nori는 [삼성전자, 가, 신제품, 을, 발표, 하, 었, 다]로 분해해 어근 매칭이 성립한다.
- **확인 방법**: `_analyze` API로 두 분석기의 토큰을 나란히 — 도입 설득·검증이 1분에 끝나는 명령.
- **운영 축적**: 형태소가 풀어주는 건 어형 변화까지 — "삼전→삼성전자" 같은 별칭·동의어는 사전 운영(synonym filter)으로 축적해야 하며, 이게 검색 품질의 장기 자산이 된다(검색 로그에서 "결과 0건 질의"를 주기 수집해 사전에 반영하는 루프).

## 3. "매핑 바꾸려면 전체 재색인" — reindex 보험 부재 사고 (운영 반복 패턴)

- **무슨 일**: 운영 중 매핑 결함 발견(text/keyword 오지정·분석기 교체 필요) → ES 매핑은 기존 필드 변경 불가 → 신규 인덱스 + 전체 재색인 + 알리아스 전환이 표준 절차인데, **원본이 ES에만 있거나 재색인 스크립트가 없어** 막히는 사례가 반복된다.
- **표준 절차**(보험이 있을 때): 새 인덱스 v2 생성(올바른 매핑) → DB에서 v2로 전체 색인(또는 `_reindex`) → 알리아스를 v1→v2 원자 전환 → v1 삭제. 무중단이고 롤백도 알리아스 한 번.
- **이 스킬과의 연결**: 안티패턴 3·5. "알리아스로 인덱스를 직접 가리키지 않기"는 첫 색인 설계 때 정해야 공짜인 결정 — 나중엔 클라이언트 전수 수정이 된다.

## 출처 (2026-06 웹 검증 완료)

1차 출처(공식 문서·공식 블로그) 우선, 보조로 보안 연구 집계.

- **nori 형태소 분석기** — Elastic 공식 플러그인. mecab-ko-dic 사전 기반, decompound 모드 지원. [analysis-nori plugin docs](https://www.elastic.co/docs/reference/elasticsearch/plugins/analysis-nori) (사례 2의 1차 근거 — "공식 플러그인" 주장 확정)
- **reindex + 알리아스 무중단 전환** — Elastic 공식 블로그 "Changing Mapping with Zero Downtime". 매핑 immutable(필드 추가는 가능·타입/분석기 변경 불가)→신규 인덱스+`_reindex`+알리아스 원자 전환이 표준임을 1차 출처가 명시. [Changing Mapping with Zero Downtime](https://www.elastic.co/blog/changing-mapping-with-zero-downtime) (사례 3의 1차 근거)
- **search_after / 10,000 결과창 한계** — `index.max_result_window` 기본 10000, 깊은 페이지네이션은 from+size 대신 search_after(+PIT) 권장이 공식 가이드. [Paginate search results](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/paginate-search-results) (안티패턴 4의 1차 근거)
- **ES 보안 기본 활성** — TLS/인증이 8.0부터 기본 on(6.8/7.1에서 무료화). 사례 1의 "과거 무인증→현재 기본 활성" 주장의 근거. [Configure security for the Elastic Stack](https://www.elastic.co/guide/en/elasticsearch/reference/current/configuring-stack-security.html)
- **pg_trgm** — PostgreSQL 공식 contrib. 트라이그램 유사도 + GIN/GiST 인덱스로 `LIKE '%foo%'` 가속. [pg_trgm docs](https://www.postgresql.org/docs/current/pgtrgm.html) (안티패턴 2의 PG 대안 근거)
- **버전 라벨** — 2026-06 기준 Elasticsearch 9.x(9.4까지 확인)·OpenSearch 3.x(3.4까지 확인) 최신 정상. "9.x / 3.x" 라벨 유효.
- **공개 ES 유출** — Shodan 스캔 발굴류 보안 연구 집계(개별 사고는 비공식·집계 장르). 무인증 9200 공개 바인딩이 원인이라는 구조적 주장은 ES 보안 공식 가이드와 정합.
