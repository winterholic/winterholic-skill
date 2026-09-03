#!/usr/bin/env python
"""skills-estimate 채점 계산기 — 14항목 점수를 넣으면 가중합·등급·보고서 표를 뽑는다.

산수 실수를 막는 게 목적이다. **판정은 하지 않는다.** 각 항목 몇 점인지는 평가자가
SKILL.md 를 읽고 줄 번호 근거와 함께 정한다. 이 스크립트는 그 숫자를 받아 계산만 한다.

사용법:
    python score.py --type tool --scores A1=4,A2=5,A3=3,B1=2,B2=4,B3=3,C1=4,C2=2,C3=3,D1=3,D2=2,E1=3,E2=5,F1=2
    python score.py --type hybrid --mix tool=50,design=50 --scores ...
    python score.py --type context --scores A1=na,A2=na,A3=na,B1=3,...   # Context 는 A 제외
    python score.py --self-test
    python score.py --legacy-f-excluded --type tool --scores ...   # 옛 계산(F 제외) 재현

종료 코드: 0 = 정상, 2 = 입력 오류(빠진 항목·범위 밖 점수 포함)

**기본 동작(2026-09-03~)**: F 카테고리에 5% 를 배정하고 A~E 는 공표된 값 × 0.95 로 축소해
합이 정확히 100 이 되게 한다. A~E 의 상대 비율은 그대로 보존된다. 원점수(/70)와 가중점수
(/100) 둘 다에 F 가 반영된다.

**`--legacy-f-excluded`**: 2026-09-03 이전 계산(F 는 원점수에만 들어가고 가중점수 100점에는
안 들어감, A~E 합이 그대로 100%)을 그대로 재현한다. 과거 `skill-reviews\\*.md` 보고서(F 제외
방식으로 채점된 약 200개)를 검산할 때만 쓴다. 새로 채점할 때는 쓰지 않는다.
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# 카테고리 -> 항목. SKILL.md "평가 Rubric" 절과 1:1.
CATEGORIES = [
    ("A", "트리거·경계",   ["A1", "A2", "A3"]),
    ("B", "자기완결성",     ["B1", "B2", "B3"]),
    ("C", "출력·구조",     ["C1", "C2", "C3"]),
    ("D", "에지케이스",     ["D1", "D2"]),
    ("E", "친절함",        ["E1", "E2"]),
    ("F", "메타데이터",     ["F1"]),
]
ITEMS = [i for _, _, items in CATEGORIES for i in items]

# SKILL.md "유형별 카테고리 가중치" 표에 공표된 A~E 값(합 100). 신규 계산에서는
# weights_for() 가 이 값을 × 0.95 로 축소하고 F=5 를 더해 최종 합 100 을 만든다.
WEIGHTS = {
    "tool":      {"A": 25, "B": 25, "C": 25, "D": 15, "E": 10},
    "design":    {"A": 20, "B": 20, "C": 15, "D": 15, "E": 30},
    "context":   {"A": 0,  "B": 30, "C": 20, "D": 20, "E": 30},
    "checklist": {"A": 20, "B": 15, "C": 25, "D": 20, "E": 20},
    "reference": {"A": 15, "B": 20, "C": 30, "D": 15, "E": 20},
}

# F 카테고리 최종 가중치(2026-09-03~). A~E 는 (100 - F_WEIGHT)/100 배로 축소된다.
F_WEIGHT = 5

GRADES = [(90, "A+"), (85, "A"), (80, "B+"), (70, "B"), (60, "C"), (0, "D")]
STATUS = [(90, "✅ 우수"), (75, "🟡 양호"), (60, "⚠️ 개선 권장"), (0, "❌ 미흡")]


def die(msg):
    print(f"입력 오류: {msg}")
    sys.exit(2)


def band(pct, table):
    for floor, label in table:
        if pct >= floor:
            return label
    return table[-1][1]


def parse_scores(raw):
    """'A1=4,A2=na,...' -> {'A1': 4, 'A2': None}. 빠지거나 범위 밖이면 죽는다."""
    got = {}
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            die(f"'{chunk}' 형식이 아니다. 항목=점수 로 쓴다")
        k, v = (x.strip() for x in chunk.split("=", 1))
        k = k.upper()
        if k not in ITEMS:
            die(f"'{k}' 는 14항목에 없다. 가능한 항목: {', '.join(ITEMS)}")
        if k in got:
            die(f"'{k}' 가 두 번 나왔다")
        if v.lower() in ("na", "n/a", "-"):
            got[k] = None
            continue
        try:
            n = int(v)
        except ValueError:
            die(f"{k}={v} — 점수는 0~5 정수이거나 na 다")
        if not 0 <= n <= 5:
            die(f"{k}={n} — 점수는 0~5 범위다")
        got[k] = n
    missing = [i for i in ITEMS if i not in got]
    if missing:
        die(f"빠진 항목이 있다: {', '.join(missing)}. 14개를 모두 넣는다")
    return got


def parse_mix(raw):
    mix = {}
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            die(f"--mix '{chunk}' 형식이 아니다. 유형=비율 로 쓴다")
        k, v = (x.strip().lower() for x in chunk.split("=", 1))
        if k not in WEIGHTS:
            die(f"--mix 의 '{k}' 는 알 수 없는 유형이다. {', '.join(WEIGHTS)}")
        try:
            mix[k] = float(v)
        except ValueError:
            die(f"--mix {k}={v} — 비율은 숫자다")
    if not mix:
        die("--mix 가 비었다")
    total = sum(mix.values())
    if abs(total - 100) > 0.01:
        die(f"--mix 비율 합이 {total} 이다. 100 이어야 한다")
    return mix


def raw_weights_for(stype, mix):
    """공표된 A~E 가중치(합 100). hybrid 는 매칭 비율로 가중평균한다(SKILL.md 규칙).
    F 는 포함하지 않는다 — 축소·legacy 분기는 weights_for() 가 맡는다."""
    if stype != "hybrid":
        return dict(WEIGHTS[stype])
    out = {}
    for cat in "ABCDE":
        out[cat] = sum(WEIGHTS[t][cat] * r / 100 for t, r in mix.items())
    return out


def weights_for(stype, mix, legacy=False):
    """최종 가중치. 기본은 A~E × 0.95 + F=5 (합 100, F 가 가중점수에 반영된다).
    legacy=True 면 2026-09-03 이전 계산(A~E 그대로 합 100, F 는 딕셔너리에서
    아예 빠져 compute() 에서 가중점수 미반영으로 처리된다)을 재현한다."""
    raw = raw_weights_for(stype, mix)
    if legacy:
        return raw
    scale = (100 - F_WEIGHT) / 100
    out = {k: v * scale for k, v in raw.items()}
    out["F"] = F_WEIGHT
    return out


def compute(scores, weights):
    rows, weighted_total, raw_sum, raw_max = [], 0.0, 0, 0
    for code, label, items in CATEGORIES:
        vals = [scores[i] for i in items if scores[i] is not None]
        n_na = len(items) - len(vals)
        cat_max = len(vals) * 5
        cat_raw = sum(vals)
        raw_sum += cat_raw
        raw_max += cat_max
        w = weights.get(code)          # F 는 None
        if cat_max == 0:
            rows.append((code, label, None, len(items) * 5, w, None, "— 평가 제외"))
            continue
        pct = cat_raw / cat_max * 100
        wscore = pct / 100 * w if w is not None else None
        if wscore is not None:
            weighted_total += wscore
        note = f" (na {n_na}개 제외)" if n_na else ""
        rows.append((code, label, cat_raw, cat_max, w, wscore, band(pct, STATUS) + note))
    return rows, weighted_total, raw_sum, raw_max


def render(name, stype, mix, scores, rows, weighted, raw_sum, raw_max, legacy=False):
    out = []
    tlabel = stype if stype != "hybrid" else \
        "hybrid (" + ", ".join(f"{k} {v:g}%" for k, v in mix.items()) + ")"
    out.append(f"# 채점 집계: {name}")
    out.append("")
    out.append(f"- **유형**: {tlabel}")
    mode_s = "**--legacy-f-excluded** (2026-09-03 이전 계산, F 는 가중점수 미반영)" \
        if legacy else "신규 계산 (2026-09-03~, F=5% 반영, A~E ×0.95)"
    out.append(f"- **계산 방식**: {mode_s}")
    out.append(f"- **원점수**: {raw_sum}/{raw_max} ({raw_sum/raw_max*100:.1f}%) — 항목별 진단용")
    out.append(f"- **유형별 가중점수**: {weighted:.1f}/100 — 등급의 공식 기준")
    out.append(f"- **등급**: **{band(weighted, GRADES)}**")
    out.append("")
    out.append("## 카테고리별 점수")
    out.append("")
    out.append("| 카테고리 | 원점수 | 만점 | 가중치 | 가중 점수 | 상태 |")
    out.append("|---|---|---|---|---|---|")
    for code, label, raw, mx, w, ws, status in rows:
        raw_s = "—" if raw is None else str(raw)
        w_s = "—" if w is None else f"{w:g}%"
        ws_s = "—" if ws is None else f"{ws:.1f}"
        out.append(f"| {code}. {label} | {raw_s}/{mx} | {mx} | {w_s} | {ws_s} | {status} |")
    out.append(f"| **합계** | **{raw_sum}/{raw_max}** | {raw_max} | 100% | **{weighted:.1f}/100** | — |")
    out.append("")
    if legacy:
        out.append("> `--legacy-f-excluded` 모드: F 는 원점수에는 들어가고 가중점수 100점에는 안 들어간다"
                    " (2026-09-03 이전 스펙 재현, 과거 보고서 검산용).")
    else:
        out.append("> F 는 5% 가중치로 가중점수에 반영된다. A~E 는 공표된 값 × 0.95 로 축소됐다"
                    " (2026-09-03~). 옛 방식 재현은 `--legacy-f-excluded`.")
    scored = [(i, s) for i, s in scores.items() if s is not None]
    scored.sort(key=lambda x: (x[1], ITEMS.index(x[0])))
    out.append("## 가장 낮은 3항목 (약점 후보)")
    out.append("")
    for i, s in scored[:3]:
        out.append(f"- **{i} — {s}/5**")
    out.append("")
    out.append("> 이건 점수순 정렬일 뿐이다. 약점 Top 3 의 확정과 보강안은 평가자가 줄 번호 근거와 함께 쓴다.")
    return "\n".join(out)


def self_test():
    """계산기를 양방향으로 검증한다. 손으로 계산한 값과 맞는지, 그리고 잘못된 입력을
    조용히 통과시키지 않는지 둘 다 본다. 2026-09-03 F 가중치 개선 이후: 신규 계산(F=5%
    반영)과 --legacy-f-excluded(F 제외, 옛 계산 재현) 둘 다 검증한다."""
    ok = True

    # (1) 손계산 대조 — tool 유형, 전 항목 만점이면 가중점수는 정확히 100 (새 방식에서도 성립)
    perfect = {i: 5 for i in ITEMS}
    rows, w, rs, rm = compute(perfect, weights_for("tool", None))
    c1 = abs(w - 100) < 1e-9 and rs == 70 and rm == 70
    print(f"  {'OK  ' if c1 else 'FAIL'} 만점 입력 -> 가중 100.0 / 원점수 70/70 (신규 방식, 실제 {w:.1f} / {rs}/{rm})")
    ok &= c1

    # (2) 손계산 대조 — A만 0점이고 나머지 만점인 tool 유형. A 최종 가중치는 25*0.95=23.75
    # 이므로 100 - 23.75 = 76.25
    mixed = {i: (0 if i.startswith("A") else 5) for i in ITEMS}
    rows, w, rs, rm = compute(mixed, weights_for("tool", None))
    c2 = abs(w - 76.25) < 1e-9 and rs == 55
    print(f"  {'OK  ' if c2 else 'FAIL'} A=0 나머지 만점 -> 가중 76.25 / 원점수 55 (실제 {w:.1f} / {rs})")
    ok &= c2

    # (3) F 가 이제 가중점수에 실제로 반영되는지 — F1 만 5->0 으로 떨구면 가중점수가
    # 정확히 F_WEIGHT(5.0)만큼 떨어져야 한다. 이게 이번 개선의 핵심 증거다.
    nof = dict(perfect); nof["F1"] = 0
    rows, w_nof, rs, rm = compute(nof, weights_for("tool", None))
    delta = 100.0 - w_nof
    c3 = abs(w_nof - 95.0) < 1e-9 and abs(delta - F_WEIGHT) < 1e-9 and rs == 65
    print(f"  {'OK  ' if c3 else 'FAIL'} F1=5->0 -> 가중점수 정확히 {F_WEIGHT}.0 하락 (95.0 / 원점수 65, 실제 {w_nof:.1f} / 하락폭 {delta:.1f} / {rs})")
    ok &= c3

    # (4) --legacy-f-excluded 로 옛 값이 재현되는지 — 2026-09-03 이전 self-test 그대로
    lw = weights_for("tool", None, legacy=True)
    rows, wl1, rsl1, rml1 = compute(perfect, lw)
    rows, wl2, rsl2, rml2 = compute(mixed, lw)
    rows, wl3, rsl3, rml3 = compute(nof, lw)
    c4 = (abs(wl1 - 100) < 1e-9 and abs(wl2 - 75) < 1e-9 and abs(wl3 - 100) < 1e-9
          and rsl1 == 70 and rsl2 == 55 and rsl3 == 65)
    print(f"  {'OK  ' if c4 else 'FAIL'} --legacy-f-excluded 재현: 만점 100.0 / A=0 75.0 / F1=0 100.0유지 (실제 {wl1:.1f} / {wl2:.1f} / {wl3:.1f})")
    ok &= c4

    # (5) Context 유형에서 A 를 na 로 빼면 만점 기준이 55 로 줄어야 한다 (신규 방식)
    ctx = {i: (None if i.startswith("A") else 5) for i in ITEMS}
    rows, w, rs, rm = compute(ctx, weights_for("context", None))
    c5 = rm == 55 and abs(w - 100) < 1e-9
    print(f"  {'OK  ' if c5 else 'FAIL'} Context A=na -> 만점 55 / 가중 100.0 (실제 {rm} / {w:.1f})")
    ok &= c5

    # (6) hybrid 가중평균(축소 전, 공표된 값 기준) — tool 50 + design 50 이면 A 는 (25+20)/2 = 22.5
    hw = raw_weights_for("hybrid", {"tool": 50.0, "design": 50.0})
    c6 = abs(hw["A"] - 22.5) < 1e-9 and abs(hw["E"] - 20.0) < 1e-9
    print(f"  {'OK  ' if c6 else 'FAIL'} hybrid(tool50+design50) 공표값 -> A 22.5 / E 20.0 (실제 {hw['A']} / {hw['E']})")
    ok &= c6

    # (7) 유형별 최종 가중치 합이 6개 카테고리(A~F) 전부 합쳐 100 인지 — 신규 계산 스펙의 핵심 불변식
    for t in list(WEIGHTS) + ["hybrid"]:
        fw = weights_for(t, {"tool": 50.0, "design": 50.0} if t == "hybrid" else None)
        s = sum(fw.values())  # A~E(축소) + F
        good = abs(s - 100) < 1e-9
        print(f"  {'OK  ' if good else 'FAIL'} {t} 최종 가중치(A~F) 합 {s:.2f}")
        ok &= good

    # (8) 공표된(레거시) A~E 가중치 합도 여전히 100 인지 — legacy 모드가 재현하는 기준값
    for t, w_ in WEIGHTS.items():
        s = sum(w_.values())
        good = abs(s - 100) < 1e-9
        print(f"  {'OK  ' if good else 'FAIL'} {t} 공표 A~E 가중치 합(legacy 기준) {s}")
        ok &= good

    # (9) 잘못된 입력을 조용히 통과시키지 않는지 — 죽어야 정상이다
    import subprocess
    bad_inputs = [
        ("항목 누락", "A1=5"),
        ("범위 밖 점수", ",".join(f"{i}=9" for i in ITEMS)),
        ("없는 항목", ",".join(f"{i}=3" for i in ITEMS) + ",Z9=3"),
    ]
    for label, raw in bad_inputs:
        # Windows 콘솔이 cp949 라 encoding 을 명시하지 않으면 자식 출력 디코딩에서 터진다
        r = subprocess.run([sys.executable, __file__, "--type", "tool", "--scores", raw],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        good = r.returncode == 2
        print(f"  {'OK  ' if good else 'FAIL'} 잘못된 입력 '{label}' 을 exit 2 로 거부 (실제 {r.returncode})")
        ok &= good

    print("\nself-test:", "PASS" if ok else "FAILED — 계산기를 먼저 고쳐라")
    return 0 if ok else 2


def main(argv):
    if "--self-test" in argv:
        return self_test()

    stype, raw_scores, raw_mix, name, legacy = None, None, None, "(이름 미지정)", False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--type" and i + 1 < len(argv):
            stype = argv[i + 1].lower(); i += 2
        elif a == "--scores" and i + 1 < len(argv):
            raw_scores = argv[i + 1]; i += 2
        elif a == "--mix" and i + 1 < len(argv):
            raw_mix = argv[i + 1]; i += 2
        elif a == "--name" and i + 1 < len(argv):
            name = argv[i + 1]; i += 2
        elif a == "--legacy-f-excluded":
            legacy = True; i += 1
        else:
            die(f"알 수 없는 인자: {a}")

    if not stype:
        die("--type 이 필요하다. " + ", ".join(list(WEIGHTS) + ["hybrid"]))
    if stype != "hybrid" and stype not in WEIGHTS:
        die(f"'{stype}' 는 알 수 없는 유형이다. {', '.join(list(WEIGHTS) + ['hybrid'])}")
    if not raw_scores:
        die("--scores 가 필요하다. 14항목을 모두 넣는다")

    mix = parse_mix(raw_mix) if stype == "hybrid" else None
    if stype == "hybrid" and mix is None:
        die("hybrid 는 --mix 가 필요하다 (예: --mix tool=50,design=50)")

    scores = parse_scores(raw_scores)
    weights = weights_for(stype, mix, legacy=legacy)
    rows, weighted, raw_sum, raw_max = compute(scores, weights)
    if raw_max == 0:
        die("채점된 항목이 하나도 없다(전부 na)")
    print(render(name, stype, mix, scores, rows, weighted, raw_sum, raw_max, legacy=legacy))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
