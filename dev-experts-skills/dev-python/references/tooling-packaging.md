# 도구·패키징 — venv/uv·pyproject·src 레이아웃·도입 사다리 (SKILL.md 비중복 심화)

> 기준: 2026-06. 도구 생태는 부패 중간 등급 — 반기 점검 대상(README 시효성 규칙).

## 프로젝트 구조 기본형 (sys.path 조작 안티패턴 #7의 정답 쪽)

```
myproj/
├── pyproject.toml          # 메타데이터 + 의존성 + 도구 설정 단일 파일
├── src/
│   └── myproj/
│       ├── __init__.py
│       └── core.py
└── tests/
    └── test_core.py
```

- **src 레이아웃인 이유**: 루트에 패키지를 두면 "설치 안 했는데 import 되는" 가짜 성공이 난다(현재 디렉토리가 sys.path에 있어서). src/면 `pip install -e .` 없이는 import 실패 → 패키징 문제를 개발 중에 발견.
- 진입 실행은 `python -m myproj.core` (패키지 컨텍스트 보장) — `python src/myproj/core.py` 직접 실행은 상대 import가 깨진다.
- 단발 스크립트(1파일)는 이 구조가 과하다 — 파일 2개 이상 + 재사용 시점부터 적용 (YAGNI).

## pyproject.toml 최소형

```toml
[project]
name = "myproj"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["httpx>=0.27"]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88

[tool.mypy]
strict = true              # 신규 프로젝트만. 기존 코드는 아래 사다리.
```

- setup.py·requirements.txt 신규 작성 금지(레거시 유지보수만). 의존성·도구 설정 전부 pyproject 한 파일.
- 버전 고정: 앱은 lock 파일로 전체 고정(uv lock / pip-tools), 라이브러리는 하한만(`>=`) — 앱과 라이브러리의 고정 전략은 반대다.

## venv·패키지 관리자 선택

| 도구 | 기본값 추천 | 비고 |
|---|---|---|
| `python -m venv` + pip | 표준, 어디서나 됨 | 사용자 현 환경 기본값 |
| **uv** | 신규 프로젝트 권장 | pip+venv+lock 통합, 속도 수십 배(확인 필요: 최신 벤치마크). `uv venv` / `uv pip install` / `uv lock` |
| poetry/pdm | 기존 채택 프로젝트만 | 신규 도입은 uv에 밀린 추세 (2026-06 기준) |

escape hatch: 회사·프로젝트가 이미 다른 도구를 쓰면 그것이 이긴다 (우선순위 사다리).

- venv는 **프로젝트당 1개, 프로젝트 안에**(`.venv/`) — 전역 site-packages에 설치 금지. `ModuleNotFoundError` 1차 점검: ① 어느 python이 실행됐나(`where python` / `Get-Command python`) ② 그 python의 venv에 설치됐나.
- Windows 활성화: `.\.venv\Scripts\Activate.ps1`. cron/스케줄러/서비스에서는 활성화 대신 **venv의 python 절대경로**로 직접 실행 — 활성화는 셸 세션 개념이라 데몬엔 없다.

## ruff·mypy 도입 사다리 (기존 코드베이스)

일괄 strict는 실패 패턴 — 수백 에러에 압도되어 도구 자체를 끈다. 단계로:

1. `ruff check --select E,F` (문법·명백 오류만) → CI 게이트
2. `ruff format` 일괄 1커밋 (포맷만, 로직 0 — 리뷰 부담 제거)
3. ruff 룰 확대 (`B`(bugbear: 가변 기본 인자 검출!), `UP`(구식 문법), `I`(import 정렬))
4. mypy는 **신규·수정 파일만** strict (`# mypy: strict` 파일 지시자 또는 모듈별 override)
5. 전 모듈 strict는 마지막 — Dropbox도 4M 라인을 수년에 걸쳐 점진 적용 (`evidence.md`)

## 검증 명령 모음 (copy-paste)

```
python -m venv .venv ; .\.venv\Scripts\Activate.ps1     # Windows
pip install -e ".[dev]"
ruff check . ; ruff format --check .
mypy src/
python -m pytest -x -q
python -m build                                          # 배포물 빌드 검증 (배포 시)
```
