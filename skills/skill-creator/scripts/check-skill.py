#!/usr/bin/env python
"""스킬 폴더 기계 검사기.

skill-creator 가 스킬을 넘기기 전에 돌린다. 사람이 눈으로 못 잡는 것만 본다.
판정이 애매한 것(문장 품질·트리거 정확도)은 여기서 다루지 않는다. 그건 SKILL.md 의 게이트와
skills-estimate 가 한다.

원칙: **대상을 못 찾으면 PASS 가 아니라 FAIL 이다.** "not found" 가 "위반 없음"으로 흘러내리면
검사가 죽은 채로 green 을 보고한다.

사용법:
    python check-skill.py <스킬폴더 또는 SKILL.md 경로>
    python check-skill.py --all <스킬들이 있는 상위 폴더>
    python check-skill.py --self-test          # 검사기 자체를 양방향 검증

종료 코드: 0 = 전부 통과, 1 = FAIL 있음, 2 = 검사기 자체 오류(대상 못 찾음 포함)
"""
import os
import re
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DESC_LIMIT = 1024          # Anthropic 공식 hard limit
BODY_SOFT_LIMIT_CHARS = 20000   # SKILL.md 본문 권고 상한의 문자 환산(≈5k 토큰). 초과는 WARN.

# When-NOT 신호. description 에 경계가 하나도 없으면 오발동을 막을 방법이 없다.
# "않"은 한국어 부정 어형(않는다/않으며/않음/않고)을 한 글자로 덮는다. 어미별로 나열하면
# "발동하지 않으며" 같은 실제 문장을 놓친다 — 실측으로 확인된 오탐 원인이다.
WHEN_NOT_MARKERS = [
    "않", "금지", "제외", "아니", "말 것", "해당 없",
    "skip", "when not", "do not use", "not for",
]
# 반복적으로 비어 있던 항목들(work-history 의 skills-estimate 채점 이력에서 추출)
BODY_SIGNALS = {
    "출력 형식(C1/C3)": ["출력", "결과물", "형식", "템플릿", "output"],
    "예시(C2)": ["예시", "example", "```"],
    "실패·거부 fallback(D1/D2)": ["실패", "안 되면", "불가", "fallback", "폴백", "대안", "에러"],
}


class Result:
    def __init__(self):
        self.rows = []          # (level, code, message)

    def add(self, level, code, msg):
        self.rows.append((level, code, msg))

    @property
    def failed(self):
        return any(l == "FAIL" for l, _, _ in self.rows)

    def render(self, title):
        icon = {"FAIL": "FAIL", "WARN": "WARN", "OK": "OK  "}
        out = [f"== {title}"]
        for level, code, msg in self.rows:
            out.append(f"   {icon[level]} [{code}] {msg}")
        return "\n".join(out)


def parse_frontmatter(text):
    """앞머리 YAML 을 통째로 돌려준다. 없으면 None."""
    m = re.match(r"---\r?\n(.*?)\r?\n---", text, re.S)
    return m.group(1) if m else None


def field(fm, key):
    """단순 스칼라/블록 필드 하나를 뽑는다. 다음 최상위 키 전까지가 값이다."""
    m = re.search(rf"^{key}:\s*(.*?)(?=^[A-Za-z_-]+:|\Z)", fm, re.S | re.M)
    if not m:
        return None
    v = m.group(1).strip()
    if v[:1] in ("|", ">"):          # 블록 스칼라
        v = v[1:].strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def check_skill(skill_dir):
    r = Result()
    md = os.path.join(skill_dir, "SKILL.md")

    if not os.path.isfile(md):
        r.add("FAIL", "no-skill-md", f"SKILL.md 없음: {md}")
        return r                     # 대상 부재는 통과가 아니라 실패다

    text = open(md, encoding="utf-8", errors="replace").read()
    fm = parse_frontmatter(text)
    if fm is None:
        r.add("FAIL", "no-frontmatter", "앞머리 YAML(---) 이 없다. 스킬로 등록되지 않는다")
        return r
    body = text[text.index("---", 3) + 3:]

    name = field(fm, "name")
    desc = field(fm, "description")
    dirname = os.path.basename(os.path.normpath(skill_dir))

    # 1. name
    if not name:
        r.add("FAIL", "name-missing", "frontmatter 에 name 이 없다")
    elif name != dirname:
        r.add("FAIL", "name-dir-mismatch",
              f"name({name}) != 디렉터리명({dirname}). 두 등록 경로가 서로 다른 이름을 쓴다")
    else:
        r.add("OK", "name", f"name == 디렉터리명 ({name})")

    # 2. description
    if not desc:
        r.add("FAIL", "desc-missing", "description 이 비어 있다. 트리거가 영영 안 걸린다")
    else:
        n = len(desc)
        if n > DESC_LIMIT:
            r.add("FAIL", "desc-too-long", f"description {n}자 > {DESC_LIMIT}자 hard limit")
        elif n > DESC_LIMIT * 0.9:
            r.add("WARN", "desc-near-limit", f"description {n}자 — 한계의 {n/DESC_LIMIT:.0%}")
        else:
            r.add("OK", "desc-len", f"description {n}자 (한계 {DESC_LIMIT})")

        if re.search(r"<[A-Za-z/][^>]*>", desc):
            r.add("FAIL", "desc-xml", "description 에 XML/HTML 태그가 있다. 공식 제약 위반")

        low = desc.lower()
        if not any(k in low for k in WHEN_NOT_MARKERS):
            r.add("WARN", "desc-no-when-not",
                  "description 에 When-NOT(경계·SKIP) 신호가 없다. 오발동을 막을 장치가 없다")
        else:
            r.add("OK", "desc-when-not", "When-NOT 경계 있음")

    # 3. 본문 분량
    n_body = len(body)
    if n_body > BODY_SOFT_LIMIT_CHARS:
        r.add("WARN", "body-large",
              f"본문 {n_body}자 — 권고 상한(≈{BODY_SOFT_LIMIT_CHARS}자) 초과. references/ 로 쪼갤 것")
    else:
        r.add("OK", "body-size", f"본문 {n_body}자")

    # 4. 죽은 번들 참조 — 본문이 가리키는 로컬 파일이 실제로 있는가
    # 펜스 코드 블록은 예시다. 거기 적힌 경로를 실제 참조로 세면 오탐이 난다(실측 3건).
    scan = re.sub(r"```.*?```", "", body, flags=re.S)
    scan = re.sub(r"^(?: {4}|	).*$", "", scan, flags=re.M)   # 들여쓰기 코드 블록
    # 읽으라고 시키는 경로만 실참조로 본다. "앞으로 추가하면 좋을 것" 목록까지 FAIL 로 세면
    # 계획을 적어둔 스킬이 전부 빨간불이 된다(실측 1건).
    READ_VERBS = ("참조", "읽", "실행", "사용", "열", "따른다", "see ", "read ", "run ", "load ")
    dead, planned = [], []
    parent = os.path.dirname(os.path.abspath(skill_dir))
    for m in re.finditer(r"(?:references|scripts|assets)/[\w./-]+\.\w+", scan):
        rel = m.group(0)
        if os.path.exists(os.path.join(skill_dir, rel)):
            continue
        ctx = scan[max(0, m.start() - 60): m.end() + 60]
        # 타 스킬의 번들을 가리키는 문장이 있다(예: "그쪽 references/batch-evaluation.md").
        # 자기 폴더 기준으로만 풀면 실재하는 파일을 죽은 참조로 오탐한다(실측 1건: skill-creator:133).
        # 문맥에 이름이 나온 형제 스킬 폴더에서 풀리면 실참조로 인정한다.
        # 스킬 이름은 같은 문단 앞쪽에서 한 번만 나오고 그다음은 "그쪽"으로 받는 일이 흔하다.
        # 그래서 형제 스킬 탐색 창은 READ_VERBS 창(60자)보다 넓게 잡는다.
        wide = scan[max(0, m.start() - 220): m.end() + 60]
        if any(os.path.exists(os.path.join(parent, sib, rel))
               for sib in set(re.findall(r"[a-z][a-z0-9-]{2,}", wide))):
            continue
        (dead if any(v in ctx for v in READ_VERBS) else planned).append(rel)
    if dead:
        r.add("FAIL", "dead-bundle-ref",
              "읽으라고 지시한 번들 파일이 없다: " + ", ".join(sorted(set(dead))[:5]))
    if planned:
        r.add("WARN", "planned-bundle-ref",
              "아직 없는 번들 파일을 언급한다(계획으로 보임): " + ", ".join(sorted(set(planned))[:5]))
    if not dead and not planned:
        r.add("OK", "bundle-refs", "번들 참조 전부 실재")

    # 5. 반복적으로 비어 있던 항목
    lowbody = body.lower()
    for label, keys in BODY_SIGNALS.items():
        if not any(k.lower() in lowbody for k in keys):
            r.add("WARN", "missing-section", f"{label} 에 해당하는 내용이 안 보인다")

    return r


def iter_skill_dirs(root):
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d)
        if os.path.isdir(p) and os.path.isfile(os.path.join(p, "SKILL.md")):
            yield p


GOOD = """---
name: {name}
description: 무언가를 한다. 사용자가 'X 해줘'라고 하면 트리거. Y 에는 사용하지 않는다.
---

# 제목

## 출력 형식
결과물은 아래 템플릿을 따른다.

## 예시
```
입력 -> 출력
```

## 실패 시
안 되면 사유를 밝히고 대안을 낸다.
"""

BAD_CASES = {
    "name-dir-mismatch": "---\nname: wrong-name\ndescription: 설명. 사용하지 않는 경우도 있다.\n---\n\n출력 형식 예시\n```x```\n실패 시 대안\n",
    "desc-too-long":     "---\nname: {name}\ndescription: " + ("가" * 1200) + " 사용하지 않는다.\n---\n\n출력 형식 예시\n```x```\n실패 시 대안\n",
    "no-frontmatter":    "# 앞머리가 없다\n",
    "dead-bundle-ref":   "---\nname: {name}\ndescription: 설명. 사용하지 않는다.\n---\n\nreferences/nope.md 를 참조하라\n출력 형식 예시\n```x```\n실패 시 대안\n",
    # 형제 스킬 이름을 대도 그 폴더에 그 파일이 없으면 여전히 잡아야 한다.
    # 위 오탐 수정이 미탐으로 뒤집히지 않는지 확인하는 자리다.
    "dead-bundle-ref-cross": "---\nname: {name}\ndescription: 설명. 사용하지 않는다.\n---\n\nskills-estimate 쪽 references/nope.md 를 읽는다\n출력 형식 예시\n```x```\n실패 시 대안\n",
}


# 키가 곧 기대 코드지만, 같은 코드를 다른 입력으로 두 번 검증할 때만 예외를 둔다.
BAD_EXPECT = {"dead-bundle-ref-cross": "dead-bundle-ref"}


def self_test():
    """검사기를 양방향으로 검증한다. 정상 입력은 통과하고, 고의로 깨뜨린 입력은
    **그 원인을 이름으로 지목하며** 실패해야 한다. 둘 중 하나라도 어긋나면 검사기가 고장난 것이다."""
    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        # (1) 정상 입력은 FAIL 이 없어야 한다
        d = os.path.join(tmp, "good-skill")
        os.makedirs(d)
        open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8").write(GOOD.format(name="good-skill"))
        res = check_skill(d)
        good_ok = not res.failed
        print(f"  {'OK  ' if good_ok else 'FAIL'} 정상 입력 통과")
        ok &= good_ok

        # (2) 각 결함은 해당 코드로 잡혀야 한다
        for code, tpl in BAD_CASES.items():
            d = os.path.join(tmp, f"bad-{code}")
            os.makedirs(d)
            open(os.path.join(d, "SKILL.md"), "w", encoding="utf-8").write(
                tpl.format(name=f"bad-{code}"))
            res = check_skill(d)
            want = BAD_EXPECT.get(code, code)
            hit = any(c == want and l == "FAIL" for l, c, _ in res.rows)
            print(f"  {'OK  ' if hit else 'FAIL'} 고의 결함 '{code}' 을 '{want}' 로 지목")
            ok &= hit

        # (3) 대상 부재는 통과가 아니라 실패여야 한다
        res = check_skill(os.path.join(tmp, "does-not-exist"))
        miss_ok = res.failed
        print(f"  {'OK  ' if miss_ok else 'FAIL'} 대상 부재를 FAIL 로 처리(통과로 흘리지 않음)")
        ok &= miss_ok
    print("\nself-test:", "PASS" if ok else "FAILED — 검사기를 먼저 고쳐라")
    return 0 if ok else 2


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--self-test":
        return self_test()

    if argv[0] == "--all":
        if len(argv) < 2 or not os.path.isdir(argv[1]):
            print("FAIL --all 에 유효한 폴더가 필요하다")
            return 2
        dirs = list(iter_skill_dirs(argv[1]))
        if not dirs:
            print(f"FAIL {argv[1]} 아래에 SKILL.md 를 가진 폴더가 하나도 없다")
            return 2
    else:
        t = argv[0]
        if os.path.isfile(t) and os.path.basename(t) == "SKILL.md":
            t = os.path.dirname(t)
        if not os.path.isdir(t):
            print(f"FAIL 경로를 못 찾았다: {argv[0]}")
            return 2
        dirs = [t]

    bad = 0
    for d in dirs:
        r = check_skill(d)
        if r.failed:
            bad += 1
        print(r.render(os.path.basename(os.path.normpath(d))))
    print(f"\n검사 {len(dirs)}개 / FAIL {bad}개")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
