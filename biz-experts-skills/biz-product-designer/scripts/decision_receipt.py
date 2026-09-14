#!/usr/bin/env python3
"""decision_receipt.py — 되돌리기 어려운 결정의 영수증 발행·만기 점검 (의존성 없음)

왜 있나: 이 스킬군의 공통 규칙 4번은 *"모든 산출물에 가설 · 성공지표 · 언제 확인할지 ·
뒤집을 조건을 명시한다"* 이고, README 는 그 표 형식까지 정해뒀다. 그런데 **그 표를 다루는
도구가 팩 전체에 없었다.** 그래서 확인 시점이 지나도 아무도 돌아오지 않는다 — 코드와 달리
제품·디자인 결정은 결과가 수주 뒤에 오고, 그때 이 대화는 이미 없다.

이 도구는 세 가지만 한다.
  1. `new`   — 필드가 빠지면 **발행을 거부한다.** 빈칸을 채운 영수증은 영수증이 아니다.
  2. `due`   — 확인 시점이 지났는데 결과가 빈 항목을 뽑는다. 세션 시작 때 한 번 돌린다.
  3. `check` — 표 자체의 형식·결측을 점검한다.

쓰는 법
  python decision_receipt.py new --file docs/decisions.md \\
      --area "카드 상세" --decision "카드 크기를 결과 화면과 동일 고정" \\
      --hypothesis "카드가 작아 보인다는 불만이 사라진다" \\
      --metric "오너 재지적 0건" --check-at 2026-09-15 \\
      --reverse-if "정보 상자가 최악 조건에서 넘침" --rollback "커밋 db634c2 로 되돌림"
  python decision_receipt.py due --file docs/decisions.md
  python decision_receipt.py check --file docs/decisions.md
  python decision_receipt.py --self-test

주의: 결정을 대신 내려주지 않는다. **덜 적힌 결정을 통과시키지 않을 뿐이다.**
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

HEADER = "| 날짜 | 영역 | 결정 | 가설 | 성공지표 | 확인 시점 | 뒤집을 조건 | 롤백 | 결과 |"
SEP = "|---|---|---|---|---|---|---|---|---|"
COLS = 9
TITLE = "## 결정 영수증 (사후 채점용 — 지우지 않는다)"

REQUIRED = {
    "area": "--area (영역)",
    "decision": "--decision (무엇을 정했나)",
    "hypothesis": "--hypothesis (이게 맞다면 무엇이 참인가)",
    "metric": "--metric (무엇으로 확인하나)",
    "check_at": "--check-at (언제 확인하나, YYYY-MM-DD)",
    "reverse_if": "--reverse-if (무엇이 보이면 뒤집나)",
}


def esc(s: str) -> str:
    """표를 깨뜨리는 문자만 중화한다. 줄바꿈은 표 안에서 행을 쪼개므로 반드시 없앤다."""
    return " ".join(str(s).replace("|", "／").split())


def parse_table(text: str) -> tuple[list[dict], list[str]]:
    """(정상 행, 형식이 깨진 행) 을 함께 돌려준다.

    깨진 행을 조용히 버리면 이 도구의 존재 이유가 그 경로에서 무너진다 — 손으로 파이프
    하나를 빠뜨린 영수증이 만기 목록에서 통째로 사라지고, 아무도 그 사실을 모른다.
    """
    rows: list[dict] = []
    malformed: list[str] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and (cells[0] in {"날짜", "---"} or set(cells[0]) <= {"-", ":"}):
            continue
        if len(cells) != COLS:
            malformed.append(line.strip())
            continue
        rows.append({
            "date": cells[0], "area": cells[1], "decision": cells[2], "hypothesis": cells[3],
            "metric": cells[4], "check_at": cells[5], "reverse_if": cells[6],
            "rollback": cells[7], "result": cells[8], "raw": line,
        })
    return rows, malformed


def is_empty(v: str) -> bool:
    return v.strip() in {"", "-", "—", "TBD", "미정"}


def cmd_new(a: argparse.Namespace) -> int:
    missing = [flag for key, flag in REQUIRED.items() if is_empty(getattr(a, key) or "")]
    if missing:
        print("발행 거부 — 아래가 비었다. 빈칸을 채운 영수증은 영수증이 아니다:")
        for m in missing:
            print("  -", m)
        print("\n정말 모르는 항목이면 그 사실을 값으로 적어라. 예: --metric \"확인 못함: 지표 미정, 오너 판단 대기\"")
        return 2
    try:
        checked = datetime.strptime(a.check_at, "%Y-%m-%d").date()
    except ValueError:
        print(f"--check-at 형식 오류: {a.check_at!r} (YYYY-MM-DD)")
        return 2
    today = date.today()
    if checked < today:
        print(f"경고: 확인 시점 {checked} 이 이미 지났다. 의도한 것인가?")

    path = Path(a.file)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if HEADER not in existing:
        existing = (existing.rstrip() + "\n\n" if existing.strip() else "") + f"{TITLE}\n\n{HEADER}\n{SEP}\n"
    row = "| " + " | ".join(esc(x) for x in [
        today.isoformat(), a.area, a.decision, a.hypothesis, a.metric,
        a.check_at, a.reverse_if, a.rollback or "미정", a.result or "",
    ]) + " |"
    path.write_text(existing.rstrip() + "\n" + row + "\n", encoding="utf-8")
    print(f"발행: {path}")
    print(row)
    if is_empty(a.rollback or ""):
        print("확인 필요: --rollback 이 비었다. 되돌릴 방법을 모르는 결정은 되돌릴 수 없다.")
    return 0


def cmd_due(a: argparse.Namespace) -> int:
    path = Path(a.file)
    if not path.exists():
        print(f"확인 못함: 파일이 없다 — {path}")
        return 1
    rows, malformed = parse_table(path.read_text(encoding="utf-8"))
    today = a.today or date.today()
    due, broken = [], []
    for r in rows:
        try:
            when = datetime.strptime(r["check_at"], "%Y-%m-%d").date()
        except ValueError:
            broken.append(r)
            continue
        if when <= today and is_empty(r["result"]):
            due.append((when, r))
    if not rows and not malformed:
        print(f"영수증 0건 — 확인 못함: {path} 에 표 형식({COLS}열) 행이 없다")
        return 1
    print(f"영수증 {len(rows)}건 · 기준일 {today}")
    if malformed:
        print(f"\n⚠ 형식이 깨진 줄 {len(malformed)}개 — **이 줄들은 만기 판정에서 빠졌다**(확인 못함)")
        for line in malformed[:5]:
            print("  ", line[:120])
    if due:
        print(f"\n[확인 시점이 지났는데 결과가 빈 것 {len(due)}건] — 지금 채워야 사후 채점이 성립한다")
        for when, r in sorted(due):
            print(f"  {when}  [{r['area']}] {r['decision']}")
            print(f"           가설: {r['hypothesis']}  /  지표: {r['metric']}")
            print(f"           뒤집을 조건: {r['reverse_if']}")
    else:
        print("\n만기 지난 미기입 없음.")
    if broken:
        print(f"\n[날짜를 못 읽은 행 {len(broken)}건]")
        for r in broken:
            print("  ", r["raw"][:120])
    return 1 if due or broken else 0


def cmd_check(a: argparse.Namespace) -> int:
    path = Path(a.file)
    if not path.exists():
        print(f"확인 못함: 파일이 없다 — {path}")
        return 1
    text = path.read_text(encoding="utf-8")
    rows, malformed = parse_table(text)
    problems: list[str] = []
    for line in malformed:
        problems.append(f"표 형식이 깨진 줄({COLS}열이 아님) — 만기 점검에서 빠진다: {line[:80]}")
    if HEADER not in text:
        problems.append("표 머리글이 README 규정 형식과 다르다")
    for r in rows:
        for key, label in [("hypothesis", "가설"), ("metric", "성공지표"), ("reverse_if", "뒤집을 조건")]:
            if is_empty(r[key]):
                problems.append(f"[{r['area']}] {r['decision'][:30]} — {label} 없음")
        if is_empty(r["rollback"]):
            problems.append(f"[{r['area']}] {r['decision'][:30]} — 롤백 방법 없음")
    print(f"영수증 {len(rows)}건 · 결함 {len(problems)}건")
    for p in problems:
        print("  -", p)
    return 1 if problems else 0


def self_test() -> int:
    """negative control 먼저 — 결함이 있는 입력을 실제로 거부·검출하는지 본다."""
    import tempfile
    failures: list[str] = []

    ns = argparse.Namespace(file="x.md", area="A", decision="D", hypothesis="",
                            metric="M", check_at="2026-09-15", reverse_if="R",
                            rollback=None, result=None)
    if cmd_new(ns) != 2:
        failures.append("필수 항목이 비었는데 발행을 통과시켰다 (negative control 실패)")

    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "dec.md"
        ok = argparse.Namespace(file=str(f), area="카드", decision="크기 고정",
                                hypothesis="불만이 사라진다", metric="재지적 0건",
                                check_at="2026-09-15", reverse_if="넘침 발생",
                                rollback="db634c2", result=None)
        if cmd_new(ok) != 0:
            failures.append("정상 입력을 거부했다")
        rows, _ = parse_table(f.read_text(encoding="utf-8"))
        if len(rows) != 1:
            failures.append(f"행 파싱 오류: {len(rows)} != 1")
        elif rows[0]["decision"] != "크기 고정":
            failures.append("행 내용이 어긋났다")

        if cmd_due(argparse.Namespace(file=str(f), today=date(2026, 9, 20))) != 1:
            failures.append("만기 지난 미기입을 못 잡았다")
        if cmd_due(argparse.Namespace(file=str(f), today=date(2026, 9, 1))) != 0:
            failures.append("아직 만기 전인데 만기로 보고했다 (오탐)")

        bad = argparse.Namespace(file=str(f), area="B", decision="D2", hypothesis="H",
                                 metric="M", check_at="2026-10-01", reverse_if="R",
                                 rollback="", result=None)
        cmd_new(bad)
        if cmd_check(argparse.Namespace(file=str(f))) != 1:
            failures.append("롤백 없는 행을 결함으로 잡지 못했다")

        # 표를 깨는 입력이 실제로 중화되는지
        pipe = argparse.Namespace(file=str(f), area="C|D", decision="a\nb", hypothesis="H",
                                  metric="M", check_at="2026-10-02", reverse_if="R",
                                  rollback="rb", result=None)
        cmd_new(pipe)
        if len(parse_table(f.read_text(encoding="utf-8"))[0]) != 3:
            failures.append("파이프·줄바꿈이 표를 깨뜨렸다")

        # 손상 행이 조용히 사라지지 않는지 (critic 2차 지적)
        with f.open("a", encoding="utf-8") as fh:
            fh.write("| 2026-09-04 | 손상 | 열이 모자람 | H | M |\n")
        rows2, malformed = parse_table(f.read_text(encoding="utf-8"))
        if len(malformed) != 1:
            failures.append("열 개수가 틀린 행을 형식 오류로 잡지 못했다 (침묵 삭제)")
        if cmd_check(argparse.Namespace(file=str(f))) != 1:
            failures.append("손상 행이 check 결함으로 보고되지 않았다")

    print("SELF-TEST PASS" if not failures else "SELF-TEST FAIL")
    for f2 in failures:
        print("ERROR:", f2)
    return 1 if failures else 0


def main() -> int:
    p = argparse.ArgumentParser(description="결정 영수증 발행·만기 점검")
    p.add_argument("--self-test", action="store_true")
    sub = p.add_subparsers(dest="cmd")

    n = sub.add_parser("new", help="영수증 발행 (필드가 빠지면 거부)")
    n.add_argument("--file", required=True)
    for key in REQUIRED:
        n.add_argument("--" + key.replace("_", "-"), dest=key)
    n.add_argument("--rollback", help="되돌리는 방법(커밋·플래그·절차)")
    n.add_argument("--result", help="이미 아는 결과가 있으면")

    d = sub.add_parser("due", help="확인 시점이 지난 미기입 목록")
    d.add_argument("--file", required=True)
    d.add_argument("--today", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date())

    c = sub.add_parser("check", help="표 형식·결측 점검")
    c.add_argument("--file", required=True)

    a = p.parse_args()
    if a.self_test:
        return self_test()
    if a.cmd == "new":
        return cmd_new(a)
    if a.cmd == "due":
        return cmd_due(a)
    if a.cmd == "check":
        return cmd_check(a)
    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
