#!/usr/bin/env python3
"""token_lint.py — CSS 값 난립·토큰 누락 검출기 (의존성 없음)

왜 있나: 실사용 감사에서 컨테이너 `max-width` 가 40종 가까이 난립했고(680·699·720·780·800·
860·920·1040·1056·1152·1536px + 34/46/48/52/58/60ch), `font-size` 는 선언 515개에 종류 24가지였다.
"토큰을 도입하자"는 권고는 늘 옳게 들리는데, **어디에 몇 개가 흩어져 있는지 세지 않으면**
착수 규모를 모르고 시작해 중간에 멈춘다. 이 도구는 그 숫자를 먼저 만든다.

또 하나: `@media (max-width: 860px)` 처럼 `screen and` 없이 쓴 쿼리에 **인쇄(A4 ≈ 794px)** 가
걸리는 사고를 한 세션에서 네 번 밟았다. 그 패턴을 따로 뽑는다.

쓰는 법
  python token_lint.py <디렉터리> [--ext css,scss] [--top 15] [--json]
  python token_lint.py src/ --prop max-width,font-size
  python token_lint.py --self-test

읽는 법
  값 종류 수가 토큰 수보다 훨씬 많으면 그 속성은 토큰화 대상이다.
  `nearDuplicates` 는 1~2px 차이로 갈린 값들이다 — 대개 의도가 아니라 표류다.
  이 도구는 **정적 텍스트 분석**이라 런타임 계산값(clamp·calc 결과)은 못 본다. 그 사실을 그대로 보고한다.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_PROPS = [
    "font-size", "line-height", "max-width", "min-width", "width", "height",
    "padding", "margin", "gap", "border-radius", "z-index", "box-shadow", "color",
]
DEFAULT_EXT = ["css", "scss", "sass", "less"]

DECL_RE = re.compile(r"(?P<prop>[-a-zA-Z]+)\s*:\s*(?P<value>[^;{}]+)\s*;")
TOKEN_DEF_RE = re.compile(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;{}]+);")
TOKEN_USE_RE = re.compile(r"var\(\s*(--[a-zA-Z0-9_-]+)")
MEDIA_RE = re.compile(r"@media([^{]+)\{")
THEME_RE = re.compile(r"@theme[^{]*\{")
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
LENGTH_RE = re.compile(r"^-?\d*\.?\d+(px|rem|em|ch|vh|vw|dvh|%)$")


def strip_comments(text: str) -> str:
    return COMMENT_RE.sub(" ", text)


def theme_blocks(text: str) -> list[str]:
    """`@theme { ... }` 블록 본문을 중괄호 짝을 세어 뽑는다.

    Tailwind v4 는 이 블록의 토큰을 `var()` 가 아니라 **유틸리티 클래스 생성**으로 소비한다.
    정적 `var()` 스캔만으로 미사용 판정을 내리면 실제로 쓰이는 토큰을 지우게 된다.
    """
    out: list[str] = []
    for m in THEME_RE.finditer(text):
        depth, i = 1, m.end()
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        out.append(text[m.end():i - 1])
    return out


def collect(root: Path, exts: list[str]) -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = []
    for ext in exts:
        for p in sorted(root.rglob(f"*.{ext}")):
            if any(part in {"node_modules", ".next", "dist", "build", ".git"} for part in p.parts):
                continue
            try:
                files.append((p, strip_comments(p.read_text(encoding="utf-8", errors="replace"))))
            except OSError:
                continue
    return files


def analyze(files: list[tuple[Path, str]], props: list[str], top: int) -> dict:
    values: dict[str, Counter] = defaultdict(Counter)
    literal_where: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    token_defs: dict[str, list[str]] = defaultdict(list)
    token_uses: Counter = Counter()
    media_queries: Counter = Counter()
    risky_media: list[dict] = []
    total_decls = 0

    theme_tokens: set[str] = set()
    for path, text in files:
        for block in theme_blocks(text):
            for m in TOKEN_DEF_RE.finditer(block):
                theme_tokens.add(m.group(1))
        for m in TOKEN_DEF_RE.finditer(text):
            token_defs[m.group(1)].append(m.group(2).strip())
        for m in TOKEN_USE_RE.finditer(text):
            token_uses[m.group(1)] += 1
        for m in MEDIA_RE.finditer(text):
            cond = " ".join(m.group(1).split())
            media_queries[cond] += 1
            # `screen and` 없이 max-width 만 쓰면 인쇄(A4 ≈ 794px)에도 걸린다.
            if "max-width" in cond and "screen" not in cond and "print" not in cond:
                risky_media.append({"query": cond, "file": str(path)})
        for m in DECL_RE.finditer(text):
            prop, value = m.group("prop").strip().lower(), " ".join(m.group("value").split())
            if prop.startswith("--"):
                continue
            total_decls += 1
            if prop not in props:
                continue
            if "var(" in value:
                continue  # 토큰을 쓰고 있으면 난립이 아니다
            values[prop][value] += 1
            if len(literal_where[prop][value]) < 3:
                literal_where[prop][value].append(str(path))

    near_dups: dict[str, list[list[str]]] = {}
    for prop, counter in values.items():
        nums: list[tuple[float, str, str]] = []
        for v in counter:
            # 단축 표기(`4px 0 0`)는 근접 중복 판정에서 뺀다 — 첫 값만 보면 서로 다른
            # 의도가 같은 값으로 묶여 오탐이 된다. 단일 길이값만 비교 대상이다.
            mm = re.fullmatch(r"(-?\d*\.?\d+)(px|rem|em|ch)", v.strip())
            if mm:
                nums.append((float(mm.group(1)), mm.group(2), v))
        groups: list[list[str]] = []
        for unit in {u for _, u, _ in nums}:
            same = sorted([n for n in nums if n[1] == unit])
            i = 0
            while i < len(same):
                bucket = [same[i][2]]
                j = i + 1
                # 간격 계열은 1~2px 표류가 실제로 잦지만, font-size·line-height 는
                # 1px 단위 스케일이 의도인 경우가 흔하다. 같은 잣대로 재면 의도된
                # 스케일 전체가 "표류"로 보고돼 통합을 유도한다.
                scale_like = prop in {"font-size", "line-height"}
                tol = (0.6 if scale_like else 2.0) if unit == "px" else (0.05 if scale_like else 0.13)
                while j < len(same) and same[j][0] - same[i][0] <= tol:
                    bucket.append(same[j][2])
                    j += 1
                if len(bucket) > 1:
                    groups.append(bucket)
                i = j if j > i + 1 else i + 1
        if groups:
            near_dups[prop] = groups

    # @theme 토큰은 사용 여부를 정적으로 판정할 수 없으므로 미사용 목록에서 뺀다.
    unused = sorted(t for t in token_defs if token_uses[t] == 0 and t not in theme_tokens)
    theme_undetermined = sorted(t for t in theme_tokens if token_uses[t] == 0)
    dup_value_tokens: dict[str, list[str]] = defaultdict(list)
    for name, defs in token_defs.items():
        if len(set(defs)) == 1:
            dup_value_tokens[defs[0].strip()].append(name)
    same_value_tokens = {v: names for v, names in dup_value_tokens.items() if len(names) > 1}

    return {
        "files": len(files),
        "declarations": total_decls,
        "tokensDefined": len(token_defs),
        "tokenUses": sum(token_uses.values()),
        "byProp": {
            prop: {
                "distinctValues": len(counter),
                "declarations": sum(counter.values()),
                "top": [{"value": v, "count": c, "files": literal_where[prop][v]}
                        for v, c in counter.most_common(top)],
            }
            for prop, counter in sorted(values.items(), key=lambda kv: -len(kv[1]))
        },
        "nearDuplicates": near_dups,
        "unusedTokens": unused,
        "themeTokensUndetermined": theme_undetermined,
        "tokensWithSameValue": same_value_tokens,
        "mediaQueries": media_queries.most_common(20),
        "riskyMediaQueries": risky_media[:20],
        "unmeasured": [
            "런타임 계산값(clamp·calc·CSS-in-JS·인라인 style)은 정적 분석으로 못 본다 — 확인 못함",
            "이 도구는 특이도·캐스케이드 승패를 판정하지 않는다 — 확인 못함",
            "토큰이 CSS 밖(JS·Tailwind 유틸리티·인라인 style)에서 소비되면 사용 여부를 못 본다 — 확인 못함",
        ],
    }


def render(r: dict, top: int) -> str:
    L = [f"파일 {r['files']}개 · 선언 {r['declarations']}개 · 토큰 정의 {r['tokensDefined']}개 · var() 사용 {r['tokenUses']}회", ""]
    L.append("[속성별 값 난립]  종류가 많을수록 토큰화 우선순위가 높다")
    L.append(f"  {'속성':<16}{'종류':>6}{'선언':>7}   상위 값")
    for prop, d in r["byProp"].items():
        head = ", ".join(f"{t['value']}({t['count']})" for t in d["top"][:4])
        L.append(f"  {prop:<16}{d['distinctValues']:>6}{d['declarations']:>7}   {head}")
    if r["nearDuplicates"]:
        L.append("")
        L.append("[근접 중복]  1~2px 차이로 갈린 값 — 대개 의도가 아니라 표류다 (font-size·line-height 는 더 엄격한 기준을 쓴다)")
        for prop, groups in r["nearDuplicates"].items():
            for g in groups[:6]:
                L.append(f"  {prop}: {' / '.join(g)}")
    if r["riskyMediaQueries"]:
        L.append("")
        L.append("[위험한 미디어쿼리]  `screen and` 가 없어 인쇄(A4 ≈ 794px)에도 걸린다")
        for q in r["riskyMediaQueries"][:10]:
            L.append(f"  @media {q['query']}   ← {q['file']}")
    if r["unusedTokens"]:
        L.append("")
        L.append(f"[미사용 토큰 {len(r['unusedTokens'])}개] " + ", ".join(r["unusedTokens"][:12]))
    if r.get("themeTokensUndetermined"):
        L.append("")
        L.append(f"[@theme 토큰 {len(r['themeTokensUndetermined'])}개 — 사용 여부 판정 불가] "
                 + ", ".join(r["themeTokensUndetermined"][:12]))
        L.append("  Tailwind 가 유틸리티 클래스로 소비한다. 미사용으로 읽고 지우면 안 된다.")
    if r["tokensWithSameValue"]:
        L.append("")
        L.append("[같은 값을 가진 토큰]  이름만 다른 중복일 수 있다")
        for v, names in list(r["tokensWithSameValue"].items())[:8]:
            L.append(f"  {v}: {', '.join(names)}")
    L.append("")
    L.append("확인 못함:")
    for u in r["unmeasured"]:
        L.append(f"  - {u}")
    return "\n".join(L)


def self_test() -> int:
    """negative control 먼저 — 결함이 심어진 입력을 실제로 잡아내는지 본다."""
    failures: list[str] = []
    sample = """
    /* 주석 안의 font-size: 99px; 는 세면 안 된다 */
    :root { --fs-body: 14px; --fs-alias: 14px; --unused-one: 4px; }
    .a { font-size: 12px; max-width: 699px; }
    .b { font-size: 13px; max-width: 700px; }
    .c { font-size: var(--fs-body); }
    @media (max-width: 860px) { .d { font-size: 11px; } }
    @media screen and (max-width: 640px) { .e { font-size: 10px; } }
    """
    r = analyze([(Path("sample.css"), strip_comments(sample))], DEFAULT_PROPS, 10)

    if r["byProp"].get("font-size", {}).get("distinctValues") != 4:
        failures.append(f"font-size 종류 오집계: {r['byProp'].get('font-size', {}).get('distinctValues')} != 4 (12/13/11/10, var()는 제외)")
    if any(t["value"] == "99px" for t in r["byProp"].get("font-size", {}).get("top", [])):
        failures.append("주석 안의 값을 셌다")
    if "max-width" not in r["nearDuplicates"]:
        failures.append("근접 중복(699px/700px)을 못 잡았다")
    if len(r["riskyMediaQueries"]) != 1:
        failures.append(f"위험 미디어쿼리 오집계: {len(r['riskyMediaQueries'])} != 1 (screen and 는 제외돼야 한다)")
    if "--unused-one" not in r["unusedTokens"]:
        failures.append("미사용 토큰을 못 잡았다")
    if "--fs-body" in r["unusedTokens"]:
        failures.append("사용 중인 토큰을 미사용으로 잘못 표시했다")
    if not any(set(names) == {"--fs-body", "--fs-alias"} for names in r["tokensWithSameValue"].values()):
        failures.append("같은 값 토큰 쌍을 못 잡았다")

    shorthand = ".p { margin: 4px 0 0; } .q { margin: 5px 10px 4px; }"
    r3 = analyze([(Path("s.css"), shorthand)], DEFAULT_PROPS, 10)
    if "margin" in r3["nearDuplicates"]:
        failures.append("단축 표기를 근접 중복으로 잘못 묶었다 (오탐)")

    theme = """
    @theme inline { --color-background: #fff; --font-sans: Inter, sans-serif; }
    :root { --dead: 1px; }
    .a { color: #000; }
    """
    r4 = analyze([(Path("t.css"), theme)], DEFAULT_PROPS, 10)
    if "--color-background" in r4["unusedTokens"]:
        failures.append("@theme 토큰을 미사용으로 오탐했다 (Tailwind 가 유틸리티로 소비한다)")
    if "--dead" not in r4["unusedTokens"]:
        failures.append("@theme 밖의 진짜 미사용 토큰을 놓쳤다")
    if "--color-background" not in r4.get("themeTokensUndetermined", []):
        failures.append("@theme 토큰을 판정 불가 목록에 남기지 않았다")

    scale = ".a { font-size: 13px; } .b { font-size: 14px; } .c { padding: 13px; } .d { padding: 14px; }"
    r5 = analyze([(Path("sc.css"), scale)], DEFAULT_PROPS, 10)
    if "font-size" in r5["nearDuplicates"]:
        failures.append("font-size 1px 스케일을 표류로 오탐했다")
    if "padding" not in r5["nearDuplicates"]:
        failures.append("간격 계열의 1px 표류를 놓쳤다")

    clean = ":root { --a: 4px; }\n.x { padding: var(--a); }"
    r2 = analyze([(Path("clean.css"), clean)], DEFAULT_PROPS, 10)
    if r2["byProp"]:
        failures.append("깨끗한 입력에서 지적이 나왔다 (오탐)")

    print("SELF-TEST PASS" if not failures else "SELF-TEST FAIL")
    for f in failures:
        print("ERROR:", f)
    return 1 if failures else 0


def main() -> int:
    p = argparse.ArgumentParser(description="CSS 값 난립·토큰 누락 검출기")
    p.add_argument("path", nargs="?", help="스캔할 디렉터리")
    p.add_argument("--ext", default=",".join(DEFAULT_EXT))
    p.add_argument("--prop", help="쉼표로 구분한 속성 목록(기본: 주요 13종)")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--json", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()

    if a.self_test:
        return self_test()
    if not a.path:
        p.error("스캔할 디렉터리가 필요하다. 예: python token_lint.py src/")

    root = Path(a.path)
    if not root.is_dir():
        p.error(f"디렉터리가 아니다: {root}")

    props = [s.strip().lower() for s in a.prop.split(",")] if a.prop else DEFAULT_PROPS
    files = collect(root, [e.strip().lstrip(".") for e in a.ext.split(",")])
    if not files:
        print(f"대상 파일 0개 — 확인 못함: {root} 아래에 {a.ext} 파일이 없다")
        return 1

    r = analyze(files, props, a.top)
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.json else render(r, a.top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
