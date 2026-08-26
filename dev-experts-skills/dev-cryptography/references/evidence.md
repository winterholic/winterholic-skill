# dev-cryptography evidence — 장애·실증 사례

## 1. Adobe (2013) — 안티패턴의 합주 (공개 분석)

- **유출 내용**: ~1.5억 계정 — 비밀번호가 3DES-**ECB 가역 암호화**(해시 아님) + 솔트 없음 + **힌트 평문**.
- **붕괴 메커니즘**: ECB는 같은 입력 블록 = 같은 출력 블록 → 동일 비밀번호 사용자들이 같은 암호문으로 군집 → 최대 군집 = 최다 사용 비밀번호("123456") → 평문 힌트("우리 강아지 이름")가 군집별 정답을 누설 → 키 없이도 대규모 복원. XKCD가 "역대 최고의 십자말풀이"로 만평화.
- **교훈 체계화**: ① 비밀번호 = 해시(가역 저장은 요구 위반) ② ECB는 어떤 신규 코드에도 금지 ③ 보호 대상 정의는 주변 데이터까지(힌트·로그·백업) ④ "암호화했으니 안전" 보고서가 가장 위험한 문서였다 — 무엇을 어떻게가 빠진 보안 주장은 검증 대상.

## 2. ECB 펭귄과 GCM nonce 재사용 — 모드의 수학적 붕괴 (공개 시연·연구)

- **ECB 펭귄**: 리눅스 마스코트 이미지를 AES-ECB로 암호화하면 윤곽이 그대로 보이는 유명 시연 — "강한 알고리즘(AES) + 잘못된 모드 = 무보호"의 시각적 증명. 블록 단위 결정성이 구조를 보존하기 때문.
- **GCM nonce 재사용**: 같은 키로 nonce를 재사용하면 두 메시지의 XOR 관계 노출 + **인증 서브키(H) 복원 → 위조 가능** — "Forbidden Attack"으로 실서비스(일부 TLS 서버) 적발 연구까지 있다(2016). 카운터를 재시작하는 재부팅·컨테이너 복제가 현실 재사용 경로.
- **실무 처방**: 모드·nonce를 사람이 다루지 않는 API(libsodium secretbox — nonce 자동)·또는 nonce 자동 생성 고수준 함수만 — "옵션을 고를 일 자체를 없애는" 것이 이 영역의 안전 설계다.

## 3. 예측 가능 난수 — 토큰이 계산되는 사고 (실사례 집적)

- **사례들**: 메르센 트위스터 출력 624개로 전체 상태 복원(공개 도구 존재 — 세션 토큰 몇 페이지면 충분) · 시간 시드(`srand(time())`) 토큰의 초 단위 전수 대입 · 과거 Debian OpenSSL 엔트로피 버그(2008 — 생성 가능 키가 3만여 개로 축소돼 전 세계 SSH 키 재발급 사태) — "난수의 품질"이 직접 계정·키 탈취로 이어진 계보.
- **판별 규칙**: 그 값이 추측되면 보안이 무너지는가? — 무너지면 보안 난수(secrets·crypto.randomBytes), 아니면(셔플·샘플링·게임) 일반 난수로 충분. 중간은 없다.
- **점검**: `grep -rn "random\.\|Math.random\|rand(" src/ | grep -iE "token|key|secret|otp|reset|session|invite"` — 교차분이 곧 취약점 후보 목록이다.

## 출처 (1차 — 2026-06 웹 재확인)

- **Adobe 2013 암호 분석** — Bruce Schneier, "Cryptographic Blunders Revealed by Adobe's Password Leak" (schneier.com/blog/archives/2013/11/cryptographic_b.html): 3DES-ECB·평문 힌트·키 미복원 메커니즘을 1차 분석한 보안계 표준 인용원.
- **XKCD 1286 "Encryptic"** — xkcd.com/1286 / 해설 explainxkcd.com/wiki/index.php/1286:_Encryptic: "역대 최고의 십자말풀이" 만평 원본.
- **GCM nonce 재사용(Forbidden Attack)** — Böck·Zauner·Devlin·Somorovsky·Jovanovic, "Nonce-Disrespecting Adversaries", USENIX WOOT'16 (usenix.org/system/files/conference/woot16/woot16-paper-bock.pdf, ePrint 2016/475): 인증 서브키 H 복원·TLS 서버 184대 실측을 보인 1차 논문(저자명은 Demirel 아님 — 위 5인이 정확).
- **Debian OpenSSL 2008(CVE-2008-0166)** — Debian DSA-1571-1 (debian.org/security/2008/dsa-1571): PID만 엔트로피로 남아 키공간 ~32,767개 축소, 전 키 재발급 권고한 공식 권고문.
- **비밀번호 해시 권고** — OWASP Password Storage Cheat Sheet (cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html): argon2id 1순위(최소 m=19 MiB·t=2·p=1)→scrypt→bcrypt(work factor ≥10, 레거시)→PBKDF2(FIPS) 순, 2026-06 현행 확인. 권고 파라미터는 부패하므로 작업 시점 재확인.
