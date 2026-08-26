# dev-cloud-aws evidence — 장애·실증 사례

## 1. Capital One (2019) — 설정 3겹 실패의 교과서 (공개 기소장·사후 분석)

- **체인**: WAF EC2의 SSRF 취약점 → IMDSv1로 역할 자격증명 탈취 → 그 역할의 과대 S3 권한으로 1억 건+ 개인정보 유출 → 벌금·합의 수억 달러.
- **각 겹의 방어**: ① 앱: SSRF 차단(→ dev-web-security) ② 플랫폼: IMDSv2 강제(`aws ec2 modify-instance-metadata-options --http-tokens required`) ③ IAM: 역할 최소 권한 — **셋 중 하나만 있었어도** 결과가 달랐다. 다층 방어의 정량적 실증.
- **현재 표준**: 신규 인스턴스 IMDSv2 기본 — 그러나 오래된 AMI·복붙 스크립트가 v1을 부활시키니 점검 대상.

## 2. 공개 S3 노출 — 단일 사건이 아니라 장르 (반복 집계)

- **무슨 일**: 유권자 명부(1.98억 건, 2017)·국방 관련 문서·기업 고객 DB 등 — 공개 S3 발견 사고가 연 단위로 반복(UpGuard 등 보안업체가 장르적으로 발굴). 공통점: 의도적 공개가 아니라 "임시로 풀었다 잊음" 또는 정책 오해.
- **구조적 원인**: 버킷 정책·ACL·BPA 3계층이 얽혀 "지금 공개인가"를 사람이 암산하기 어려움 → 그래서 **계정 수준 BPA ON 고정**이 답이다(개별 판단 자체를 제거). 공개 서빙은 CloudFront OAC 경유로 패턴 통일.
- **점검**: `aws s3api get-public-access-block` + Access Analyzer 외부 공유 탐지 활성화.

## 3. us-east-1 S3 장애 (2017-02-28) — 오타 한 줄과 의존성 사각 (AWS 공식 포스트모템: https://aws.amazon.com/message/41926/)

- **무슨 일**: 결제 서브시스템 디버깅 중 엔지니어의 명령 인자 오타로 의도보다 많은 서버 제거 → S3 인덱스 서브시스템 붕괴 → us-east-1 S3 약 4시간 장애 → S3에 기댄 수많은 서비스 연쇄(아이러니: AWS 상태 대시보드도 S3 의존이라 정상 표시).
- **교훈**: ① 운영 도구에 안전장치(최소 용량 미만 제거 차단)가 사후 도입됨 — 사람의 오타는 막을 수 없고 도구가 흡수해야 한다 ② "AWS도 죽는다" — 단일 리전·단일 서비스 의존의 가용성 상한은 그 서비스의 실적이다 ③ 상태 페이지가 장애 대상에 의존하면 장애 시 거짓말을 한다(→ dev-monitoring 동일 원리).

## 4. 요금 폭탄 — 개인 개발자 표준 패턴 3종 (커뮤니티 반복 보고)

- **구조적 원인**: AWS에는 "지출 상한선(hard cap)"이 없다 — Budgets/CloudWatch 알람은 *알림*일 뿐 서비스를 자동 차단하지 않는다(차단을 원하면 Budgets Actions로 직접 SCP·IAM 정책을 트리거해야 함). 즉 잘못 새면 막아주는 천장이 기본 없음.
- **패턴**: ① 유출 키 → 채굴 인스턴스 대량 생성(GitHub 푸시 후 수 분 — 자동 스캐너) ② 지우다 만 리소스(NAT Gateway·EIP·스냅샷 — "인스턴스는 껐는데" 시간당 과금 잔존) ③ 재귀 호출(Lambda↔S3 트리거 루프·무한 재시도)로 호출량 폭주.
- **방어 대응**: ① 키 없는 구조 + git-secrets/push protection ② "지우는 법을 모르면 만들지 않는다" + 태그 기반 청소 ③ 재시도에 상한·DLQ(→ dev-api-integration), Lambda 동시성 상한 설정. + Budgets Actions로 임계 초과 시 자동 차단.
- **사후**: AWS 지원에 감면 요청은 가능하나 선의(courtesy)에 의존 — 통상 1회성 구제이며 보장이 아니다(커뮤니티에 €/£ 수천 청구가 일부만 감면된 사례 다수). 천장은 스스로 세워야 한다.

> 출처(2026-06 웹 재검증):
> - 미 법무부 기소장·Capital One 공시(2019) — SSRF→IMDSv1→ISRM-WAF-Role 과대권한→S3 약 1억 600만 건 유출, OCC 벌금 $80M + 집단소송 합의 $190M. AWS는 사건 직후 2019-11 IMDSv2 출시(이 사건이 직접 촉발). 신뢰성: 법원 기록 + 규제기관 처분이라 1차 사실.
> - AWS 공식 포스트모템 S3 us-east-1 2017-02-28: https://aws.amazon.com/message/41926/ — 벤더 자신의 RCA라 사건 사실관계의 1차 출처.
> - UpGuard / Chris Vickery, Deep Root Analytics 유권자 1.98억 건 공개 S3 노출(2017-06) — 보안 연구기관의 원 발견 보고. 공개 S3 "장르"의 대표 사례.
> - IMDSv2 기본화: AWS What's New 2024-03 "Set IMDSv2 as default for all new instance launches" (https://aws.amazon.com/about-aws/whats-new/2024/03/set-imdsv2-default-new-instance-launches/) — *기본값*은 리전별 설정이며 launch 시 override 가능, 진짜 강제는 별도 enforcement 설정/SCP 필요(그래서 "오래된 AMI·복붙 스크립트가 v1 부활" 주의가 유효).
