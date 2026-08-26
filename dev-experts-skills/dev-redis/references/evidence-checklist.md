# evidence + 출고 전 체크리스트

## 실증·출처

- **"Scaling Memcache at Facebook" (NSDI 2013)** — thundering herd·lease 메커니즘의 공개 논문. SKILL.md 실전 케이스.
- **Kleppmann, "How to do distributed locking" (2016) + antirez 반론 "Is Redlock safe?"** — Redis 분산 락의 정확성 한계 공개 논쟁. 안티패턴 6의 1차 출처(fencing token 논거).
- **Redis 공식 문서 — eviction 정책** (https://redis.io/docs/latest/develop/reference/eviction/) — 기본 정책은 `noeviction`(maxmemory 도달 시 쓰기 거부), `allkeys-lru`/`allkeys-lfu`/`volatile-*` 등 8종 정책 목록 확인. 공식 1차 출처.
- **Redis 8.0 GA 릴리스노트** (https://redis.io/blog/redis-8-ga/) — 2025년 5월 GA. RediSearch·RedisJSON·RedisTimeSeries·RedisBloom이 별도 모듈에서 **Redis Open Source 코어로 내장**(별도 설치 불필요). bloom·cuckoo·count-min·top-k·t-digest 등 확률적 자료구조 + HyperLogLog 코어 제공. 라이선스에 AGPLv3 추가(명칭 Community Edition→Open Source). 공식 확인 완료 — 더 이상 "확인 필요" 아님.
- **redis-py 공식 문서** (https://redis-py.readthedocs.io) — `set(name, value, ex=, px=, nx=, xx=)` 시그니처. `ex`=초 단위 TTL, `nx`=키 부재 시에만 설정(분산 락 표준형). 공식 1차 출처.
- 오픈소스 차용 표기: 캐시 패턴 자료 다수(색인 인지, 본문 비복사). **역흡수**: "캐시 전에 쿼리 먼저" 게이트·stale 허용량의 사용자 언어 합의·쓰기 지점 전수 DELETE 절차 부재 — 본 스킬 차별점.

## 출고 전 체크리스트 (캐시 도입·수정 시)

- [ ] 원천 최적화(dev-postgres) 선행 증거
- [ ] stale 허용량이 사용자 언어로 합의·주석화
- [ ] 전 키 TTL + 지터 (`redis_check.py` 0건)
- [ ] 쓰기 지점 전수 나열 → DELETE 추가 (무효화 테스트 green)
- [ ] stampede 등급 판정 + 해당 방어 단계
- [ ] maxmemory + eviction 정책 명시 (컨테이너 한도와 정렬 — dev-docker)
- [ ] KEYS·거대 컬렉션 명령 0
- [ ] 정확성 요구 작업에 Redis 락 미사용 (멱등/DB 제약으로)
- [ ] 적중률 관찰 일정 (도입 1주 후 INFO stats)

## 점검 주기 (부패 중간 — 반기)

- 적중률·evicted·bigkeys 재점검
- Redis 메이저(8.x — 2025-05 GA가 현행) 기능 변화 확인
