# evidence + 출고 전 체크리스트

## 실증·출처

- **docs.python.org "What's New in Python 3.14"** (docs.python.org/3/whatsnew/3.14.html, 3.14.x stable — 3.14.3은 2026-02-03) — 버전 라벨의 1차 출처. t-string(PEP 750)·지연 annotation(PEP 649)·실험적 JIT·sub-interpreters(PEP 734) 등 3.14 신규 기능(정량 기준 표·로컬 3.10 호환 주석의 근거).
- **PEP 779 "Criteria for supported status of free-threaded CPython"** (Phase II 수락, 3.14) + **docs.python.org/3/howto/free-threading-python.html** — free-threaded 빌드가 "실험"에서 "공식 지원"으로 격상됐으나 **기본은 GIL on**(별도 `python3.14t` 빌드), 단일스레드 오버헤드 ~5–10%로 축소(3.13의 ~40%에서). 한계 절·안티패턴 2의 동시성 근거. Phase III(기본화)는 미정.
- **NumPy 2.3.0 free-threaded 지원** — 주요 C-확장이 전환 가능함을 입증했으나, 다수 C-확장 휠이 아직 thread-safe하지 않은 게 채택 병목(한계 절 "확인 필요"의 근거).
- **Astral ty 블로그/문서** (astral.sh/blog/ty, beta 2025-12-16) — Rust 기반 타입 체커, mypy/Pyright 대비 10–60배. **2026-06 현재 beta·stable 미출시**(2026 목표), 플러그인 시스템 없음(Django ORM·Pydantic v1 mypy 플러그인 의존 프로젝트는 대체 불가), "gradual guarantee" 설계. → 정량 기준 표의 "CI 단독 대체 금지, 에디터 병용만"의 근거.
- **Pyrefly 1.0 stable** (2026-05-12, Meta Pyre 후신) — Instagram Python의 기본 타입 체커, 1.85M라인/초. ty와 함께 "Rust 타입 체커" 지형 변화의 실증(정량 기준 표 보강).
- **PEP 686 "Make UTF-8 mode default"** — 3.14에서도 아직 opt-in(`-X utf8`/`PYTHONUTF8=1`), 기본 활성은 미래 버전 예정 → `open(encoding="utf-8")` 명시는 계속 필수(안티패턴 6의 근거, 활성 버전은 "확인 필요").
- **Instagram Engineering "Dismissing Python Garbage Collection at Instagram"** (2017) — `gc.set_threshold(0)`로 CoW 메모리 공유 보존, ~10% 용량 개선(실전 케이스 절, 수치는 원문 "확인 필요"로 유지). CPython 참조카운팅+순환 GC 모델 이해의 실증.
- **Effective Python(Slatkin)·Fluent Python(Ramalho)·PEP 8/20/484** — 안티패턴 1·3·4·5(가변 기본 인자·bare except·늦은 바인딩·naive datetime)의 고전 1차 출처.

## 출고 전 체크리스트 (모듈/기능 출고 시)

- [ ] 가변 기본 인자 없음 (`def f(x=[])` → `None` 가드) — `pitfall_scan.py` 0건
- [ ] async 함수 안에 블로킹 호출(requests·time.sleep·동기 file I/O) 없음
- [ ] except가 구체 타입 + 잡은 뒤 행동(로깅·폴백·재던지기) 있음, bare except 없음
- [ ] 저장·비교용 datetime은 aware UTC (`datetime.now(tz=timezone.utc)`), 표시할 때만 로컬 변환
- [ ] 파일 I/O 전부 `encoding="utf-8"` 명시, 콘솔 출력 ASCII만(Windows cp949)
- [ ] import는 패키지 구조로 해결, `sys.path` 조작 없음 (`python -m pkg.module` 또는 `pip install -e .`)
- [ ] `ruff check . && ruff format --check .` 통과 (미도입 시 `python -m py_compile`로 최소 검증 + 사유 기록)
- [ ] `mypy <변경 모듈>` 통과 (신규 코드 strict) — ty는 병용 가능하나 CI 단독 대체는 아직 금지
- [ ] HTTP 호출에 타임아웃 명시, 외부 패키지 추가 시 이유 1줄
- [ ] 버전 의존 문법(3.11+/3.12+/3.14+)은 배포 대상 최저 버전 확인 후에만, free-threaded 전제 금지

## 점검 주기 (부패 느림 — 연 1회)

- Python 마이너 시리즈 추적(현재 3.14.x stable, 3.13.x 유지보수) → 버전 라벨 갱신. free-threaded는 "Phase III 기본화" 여부만 추적(현재 미정).
- ruff 메이저 변화 + **`ty` stable 출시 여부**(2026 목표 — 출시되면 정량 기준 표의 "beta·CI 단독 금지" 문구 갱신) + pyrefly 채택 추세.
- PEP 686(UTF-8 기본화) 기본 활성 버전이 확정되면 안티패턴 6의 "확인 필요" 해제.
- Instagram GC 수치는 원문 재확인 전까지 "확인 필요" 유지.
