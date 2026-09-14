#!/usr/bin/env python3
"""viewport_budget.py — 세로 공간 예산 계산기 (의존성 없음)

왜 있나: "한 화면에 담아라"류 요구를 설계부터 시작하면, 안 맞을 때 줄일 곳이 성역밖에 안 남는다.
실사고 두 건이 그렇게 롤백됐고, 남는 px 를 먼저 확정한 뒤에야 한 번에 통과했다.
또 하나의 실사고는 **기기 해상도로 쟀다는 것**이다. 사파리 하단 바·안드로이드 내비가
100px 안팎을 먹어서 데스크톱 브라우저에서는 "딱 맞는다"가 나오고 실제 폰에서는 잘렸다.

쓰는 법
  python viewport_budget.py --fixed 359:카드 19:안내문구 48:셸패딩 --gaps 12x3
  python viewport_budget.py --fixed 359:카드 --gaps 12x3 --device iphone14 --worst 60:설명2문단
  python viewport_budget.py --list-devices
  python viewport_budget.py --self-test

출력: 기기별 남는 px. 음수면 그 기기에서 잘린다.
주의: 이 표는 실측 관례값이고 브라우저·OS 버전에 따라 달라진다("확인 필요").
      확정이 필요하면 실기기에서 window.innerHeight 를 읽어 --viewport 로 직접 넣는다.
"""

from __future__ import annotations

import argparse
import sys

# Windows 콘솔(cp949)에서 한국어가 깨지지 않게. 파일 자체는 항상 UTF-8이다.
# Windows 콘솔(cp949)에서 한국어가 깨지지 않게. **stderr 도 같이** 건다 —
# argparse 의 오류 메시지는 stderr 로 나가므로, stdout 만 고치면 정상 출력은 멀쩡한데
# 정작 읽어야 할 에러 문구가 깨진다. 파일 자체는 항상 UTF-8이다.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

# 기기 해상도가 아니라 **실제 웹 뷰포트**(주소창·하단바 제외). 세로 예산은 이 값으로 잡는다.
DEVICES: dict[str, tuple[int, int, str]] = {
    "iphone-se":   (375, 553, "iPhone SE — 가장 빡빡한 기준선"),
    "galaxy-mid":  (360, 620, "갤럭시 보급형 — 하단바 상시"),
    "iphone14":    (390, 664, "iPhone 14 — 사파리 하단 바"),
    "pixel":       (393, 680, "Pixel"),
    "galaxy-s23":  (412, 740, "갤럭시 S23"),
}


def parse_items(values: list[str] | None) -> list[tuple[float, str]]:
    """'359:카드' 또는 '359' 형태를 (값, 라벨)로. '12x3' 은 12px 간격 3개."""
    out: list[tuple[float, str]] = []
    for raw in values or []:
        item, _, label = raw.partition(":")
        item = item.strip()
        if "x" in item:
            size, _, count = item.partition("x")
            try:
                size_f, count_i = float(size), int(count)
            except ValueError:
                raise SystemExit(f"간격 표기를 읽지 못했다: {raw!r} (예: 12x3)")
            out.append((size_f * count_i, label or f"간격 {size}px × {count}"))
        else:
            try:
                out.append((float(item), label or "이름 없음"))
            except ValueError:
                raise SystemExit(f"숫자를 읽지 못했다: {raw!r} (예: 359:카드)")
    return out


def budget(viewport_h: float, fixed: list[tuple[float, str]],
           gaps: list[tuple[float, str]], worst: list[tuple[float, str]]) -> dict:
    used_fixed = sum(v for v, _ in fixed)
    used_gaps = sum(v for v, _ in gaps)
    used_worst = sum(v for v, _ in worst)
    return {
        "viewport": viewport_h,
        "fixed": used_fixed,
        "gaps": used_gaps,
        "worst": used_worst,
        "remaining": viewport_h - used_fixed - used_gaps,
        "remaining_worst": viewport_h - used_fixed - used_gaps - used_worst,
    }


def render(rows: list[tuple[str, str, dict]], worst_labels: list[str]) -> str:
    lines = []
    w = max((len(name) for name, _, _ in rows), default=8)
    lines.append(f"{'기기'.ljust(w)}  {'뷰포트':>7}  {'고정합':>7}  {'남는 세로':>9}  {'최악조건':>9}")
    lines.append("-" * (w + 40))
    for name, note, b in rows:
        flag = "" if b["remaining_worst"] >= 0 else "   ← 잘림"
        lines.append(
            f"{name.ljust(w)}  {b['viewport']:>7.0f}  "
            f"{b['fixed'] + b['gaps']:>7.0f}  {b['remaining']:>9.0f}  "
            f"{b['remaining_worst']:>9.0f}{flag}"
        )
    lines.append("")
    if worst_labels:
        lines.append("최악 조건: " + ", ".join(worst_labels))
    lines.append("규칙: 이 남는 px 안에 들어가도록 설계한다. 설계부터 하고 나중에 줄이면 성역이 깎인다.")
    lines.append("확인 필요: 뷰포트 값은 관례 실측치다. 확정하려면 실기기에서 window.innerHeight 를 읽어 --viewport 로 넣는다.")
    return "\n".join(lines)


def self_test() -> int:
    """검사가 실패할 수 있는지부터 확인한다(negative control)."""
    failures: list[str] = []

    b = budget(664, [(359.0, "카드"), (19.0, "문구")], [(36.0, "간격")], [])
    if b["remaining"] != 250.0:
        failures.append(f"기본 계산 오류: {b['remaining']} != 250.0")

    b2 = budget(553, [(500.0, "카드")], [(60.0, "간격")], [])
    if b2["remaining"] >= 0:
        failures.append("음수 예산을 음수로 보고하지 못했다")

    if parse_items(["12x3"])[0][0] != 36.0:
        failures.append("간격 표기 12x3 파싱 오류")
    if parse_items(["359:카드"])[0] != (359.0, "카드"):
        failures.append("라벨 파싱 오류")

    try:
        parse_items(["abc"])
        failures.append("잘못된 입력이 통과했다 (negative control 실패)")
    except SystemExit:
        pass

    if not DEVICES or any(h >= 700 for _, (_, h, _) in list(DEVICES.items())[:3]):
        failures.append("기기 표가 기기 해상도로 오염됐다 (실제 웹 뷰포트여야 한다)")

    print("SELF-TEST PASS" if not failures else "SELF-TEST FAIL")
    for f in failures:
        print("ERROR:", f)
    return 1 if failures else 0


def main() -> int:
    p = argparse.ArgumentParser(description="세로 공간 예산 계산기")
    p.add_argument("--fixed", nargs="*", help="고정 요소. '359:카드' 형식")
    p.add_argument("--gaps", nargs="*", help="간격. '12x3' = 12px 3개")
    p.add_argument("--worst", nargs="*", help="최악 조건 추가분. '60:설명 2문단'")
    p.add_argument("--device", help="특정 기기만 (기본: 전체)")
    p.add_argument("--viewport", type=float, help="실측 뷰포트 높이를 직접 지정")
    p.add_argument("--list-devices", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()

    if a.self_test:
        return self_test()
    if a.list_devices:
        for k, (w, h, note) in DEVICES.items():
            print(f"{k:<12} {w}x{h}  {note}")
        return 0

    fixed, gaps, worst = parse_items(a.fixed), parse_items(a.gaps), parse_items(a.worst)
    if not fixed and not gaps:
        p.error("--fixed 나 --gaps 중 하나는 필요하다. 예: --fixed 359:카드 --gaps 12x3")

    # 둘 다 오면 어느 쪽이 이겼는지 사용자가 알 수 없다. 침묵 무시가 이 도구의 존재
    # 이유(잰 줄 알았던 것과 실제로 잰 것이 다름)를 그대로 재현하므로 거부한다.
    if a.viewport and a.device:
        p.error("--viewport 와 --device 는 함께 쓸 수 없다. 실측값을 쓰려면 --viewport 만, 기기 표를 쓰려면 --device 만 넘긴다.")

    rows: list[tuple[str, str, dict]] = []
    if a.viewport:
        rows.append(("실측", "직접 지정", budget(a.viewport, fixed, gaps, worst)))
    else:
        items = DEVICES.items() if not a.device else [(a.device, DEVICES[a.device])] if a.device in DEVICES else []
        if not items:
            p.error(f"모르는 기기: {a.device}. --list-devices 로 확인한다.")
        for name, (_, h, note) in items:
            rows.append((name, note, budget(h, fixed, gaps, worst)))

    print(render(rows, [lbl for _, lbl in worst]))
    tight = [n for n, _, b in rows if b["remaining_worst"] < 0]
    return 1 if tight else 0


if __name__ == "__main__":
    sys.exit(main())
