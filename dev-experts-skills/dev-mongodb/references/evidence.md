# dev-mongodb evidence — 장애·실증 사례

## 1. 2017 MongoDB 랜섬 대란 — 기본값의 죄 (보안 연구 집계)

- **무슨 일**: 2017-01 수 주간 무인증 공개 MongoDB ~2.7만+ 대가 자동화 공격으로 데이터 삭제·랜섬 노트 치환(보안 연구자 Victor Gevers·Niall Merrigan 집계). 피해 다수는 지불해도 복구 불가(공격자가 데이터 미보관) — 이중 손실.
- **원인**: 당시 패키지 기본 설정이 무인증 + 0.0.0.0 바인딩 — "설치하면 바로 도는" 편의가 그대로 공격면. 이후 기본 bindIp가 127.0.0.1로 변경(3.6+).
- **교훈 체계화**: ① 데이터 스토어는 공개망에 직접 노출 금지(내부망 + 방화벽 + 인증 3겹) ② "기본값이 안전하겠지"는 버전·제품마다 거짓일 수 있다 — Redis·Elasticsearch도 같은 부류 사고 반복 ③ 노출 점검: `mongosh --host <공인IP>` 가 외부에서 붙는지 1회 확인이 가장 싼 감사.

## 2. 16MB 문서 한도 — "인기 콘텐츠가 먼저 죽는다" (반복 실증)

- **무슨 일**: 댓글·로그·이력을 부모 문서 배열에 push하는 설계가 운영 수개월 후 한도 도달 — 해당 문서 대상 모든 쓰기가 `BSONObjectTooLarge` 에러. MongoDB 포럼·스택오버플로 반복 사례.
- **왜 늦게 발견되나**: 평균 문서는 수 KB — 상위 0.1% 인기 항목만 한도에 접근한다. 즉 **트래픽 가장 많은 항목부터** 장애. 모니터링도 평균값을 보면 못 잡는다(최대 문서 크기 추적 필요).
- **방어**: ① 설계 시 배열마다 "최대 몇 개?"에 답 — 답이 '무한'이면 분리 ② 하이브리드(최근 N 임베드 + 전체 참조)로 조회 성능 유지 ③ 점검 쿼리: `db.coll.aggregate([{$project: {size: {$bsonSize: "$$ROOT"}}}, {$sort: {size: -1}}, {$limit: 5}])`.

## 3. 타입 혼재 — "합계가 조용히 적게 나온다" (스키마리스 비용 실증)

- **무슨 일**: 여러 코드 경로(레거시 스크립트·신규 API·수동 수정)가 같은 컬렉션에 쓰며 price가 int32·double·string으로 혼재 → `$sum` 집계가 문자열을 0으로 취급, 합계 과소 — 에러 없이 틀린 숫자. 정산·리포트에서 발견되는 부류.
- **진단**: `db.coll.aggregate([{$group: {_id: {$type: "$price"}, n: {$sum: 1}}}])` — 필드별 타입 분포 1줄 확인.
- **방어**: ① $jsonSchema validator(`bsonType: "decimal"` 등) — 쓰기 시점 차단 ② 돈은 decimal128(부동소수점 금지 — dev-javascript 안티패턴 5와 동일 원리) ③ 기존 혼재분은 마이그레이션으로 일괄 정규화 후 validator 적용.

> 출처(2026-06 웹 확인, MongoDB 8.3 기준):
> - 2017 랜섬 사태: The Register 2017-01-09 "27,633 in 12 hours, Gevers·Merrigan 집계" (https://www.theregister.com/2017/01/09/mongodb/) — 당시 1차 추적자 인용 보도. ~99,000 노출·복구 불가 다수도 동일 보도.
> - 16MB 한도·100MB 집계 stage 한도·`allowDiskUseByDefault`(6.0+): MongoDB 공식 limits 문서 (https://www.mongodb.com/docs/manual/reference/limits/) — 공식 1차 스펙.
> - 기본 bindIp=127.0.0.1 전환(3.6, SERVER-28229): MongoDB JIRA (https://jira.mongodb.org/browse/SERVER-28229) — 변경의 근거 티켓.
