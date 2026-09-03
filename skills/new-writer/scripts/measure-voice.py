#!/usr/bin/env python
"""대화 기록에서 사용자 말투를 실측한다 — `references/voice-profile.md` 재생성용.

**이 스크립트가 번들로 들어온 이유는 필터 때문이다.** 손으로 다시 짜면 거의 확실히 틀린다.
1차 측정에서 em 대시가 사용자 쪽에 100발화당 138회로 나왔는데, 사용자가 붙여넣은
내 출력과 파일 내용이 「사용자 발화」로 잡혀서였다. 걸러내니 893건 중 464건만 남았다.
**절반이 사람이 친 것이 아니었다.**

사용법:
    python measure-voice.py                 # 사람 말투만
    python measure-voice.py --compare       # 사람 vs 클로드 대조표까지
    python measure-voice.py --samples 15    # 실제 발화 표본도 출력
    python measure-voice.py --self-test     # 필터가 제대로 거르는지 양방향 검증

종료 코드: 0 = 정상, 2 = 입력·환경 오류(기록을 못 찾은 경우 포함 — 빈 결과를 성공으로 넘기지 않는다)
"""
import json
import os
import random
import re
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.join(os.path.expanduser("~"), ".claude", "projects")

# 사람이 친 것이 아닌 것 — 이걸 안 걷으면 측정이 통째로 틀린다
NOT_HUMAN = re.compile(
    r"<system-reminder>|<local-command|<command-name>|<command-message>|"
    r"tool_use_id|Caveat: The messages below|\[SYSTEM NOTIFICATION|<task-notification>",
    re.I,
)
BACKSLASH = chr(92)

MARKS = {
    "em 대시 —": r"—",
    "괄호 (": r"\(",
    "쉼표 ,": r",",
    "물결 ~": r"~",
    "물음표 ?": r"\?",
    "세미콜론 ;": r";",
    "말줄임 ..": r"\.\.",
    "ㅋㅋ/ㅎㅎ": r"[ㅋㅎ]{2,}",
}


def is_typed(t):
    """사람이 직접 친 문장인가. 붙여넣기·인용을 걷어낸다."""
    if not t or len(t) > 400:
        return False
    if NOT_HUMAN.search(t):
        return False
    if "```" in t or "|" in t:
        return False
    if ("C:" + BACKSLASH) in t or "/c/" in t:
        return False
    if re.search(r"^\s*#{1,6}\s", t):
        return False
    if t.count("\n") > 6:
        return False
    if len(re.findall(r"[A-Za-z]", t)) > len(t) * 0.5:
        return False
    return True


def blocks(rec_type, rec):
    if rec.get("type") != rec_type:
        return []
    content = (rec.get("message") or {}).get("content")
    if isinstance(content, str):
        return [content]
    if isinstance(content, list):
        return [c.get("text", "") for c in content
                if isinstance(c, dict) and c.get("type") == "text"]
    return []


def harvest(root):
    """사용자 발화(필터 통과분)와 어시스턴트 산문 문단을 모은다."""
    human, claude, files = [], [], 0
    for dp, _, names in os.walk(root):
        for n in names:
            if not n.endswith(".jsonl"):
                continue
            files += 1
            try:
                with open(os.path.join(dp, n), encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if '"user"' not in line and '"assistant"' not in line:
                            continue
                        try:
                            rec = json.loads(line)
                        except Exception:
                            continue
                        for t in blocks("user", rec):
                            t = (t or "").strip()
                            if is_typed(t):
                                human.append(t)
                        for t in blocks("assistant", rec):
                            for blk in (t or "").split("\n\n"):
                                blk = blk.strip()
                                if not blk or "|" in blk or "```" in blk:
                                    continue
                                if re.search(r"^\s*#{1,6}\s", blk):
                                    continue
                                if not 20 <= len(blk) <= 600:
                                    continue
                                if len(re.findall(r"[가-힣]", blk)) < len(blk) * 0.3:
                                    continue
                                claude.append(blk)
            except Exception as e:
                print(f"  건너뜀 {n}: {e}")
    # 중복 제거 — 재개 세션에 같은 발화가 여러 번 실린다
    def dedup(xs):
        seen, out = set(), []
        for x in xs:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out
    return dedup(human), dedup(claude), files


def density(rows):
    return {k: sum(len(re.findall(p, t)) for t in rows) / len(rows) * 100
            for k, p in MARKS.items()}


def report(human, claude, files, compare, n_samples):
    print(f"기록 파일 {files}개 / 사람이 친 발화 {len(human)}건")
    if compare:
        print(f"클로드 산문 문단 {len(claude)}건")
    lens = sorted(len(t) for t in human)
    print(f"길이: 중앙값 {lens[len(lens)//2]}자 / 30자 이하 {sum(1 for x in lens if x<=30)}건")

    hd = density(human)
    print("\n## 표식 밀도 (100단위당)")
    if compare and claude:
        cd = density(claude)
        print(f"{'표식':12s} {'사람':>8s} {'클로드':>8s} {'배율':>8s}")
        for k in MARKS:
            r = cd[k] / hd[k] if hd[k] else float("inf")
            print(f"{k:12s} {hd[k]:8.1f} {cd[k]:8.1f} {r:7.1f}x")
    else:
        for k in MARKS:
            print(f"  {k:12s} {hd[k]:8.1f}")

    end = Counter()
    for t in human:
        for s in re.split(r"[.!?\n]", t):
            s = s.strip()
            if len(s) >= 3 and re.search(r"[가-힣]$", s):
                end[s[-3:]] += 1
    print("\n## 자주 쓰는 문장 끝 (상위 15)")
    print("  " + " · ".join(e.strip() for e, _ in end.most_common(15)))

    if n_samples:
        pool = [t for t in human if 20 <= len(t) <= 90]
        random.seed(7)
        print(f"\n## 실제 발화 표본 {min(n_samples, len(pool))}건")
        for s in random.sample(pool, min(n_samples, len(pool))):
            print("  · " + s.replace("\n", " "))


def self_test():
    """필터를 양방향으로 검증한다. 사람 문장은 통과하고 붙여넣기는 걸러야 한다.
    한쪽만 맞으면 필터가 고장난 것이다."""
    keep = [
        "야 근데 이거 좀 이상한데? 다시 봐줄래",
        "응 그렇게 해줘",
        "아 그르네 그냥 두자 어차피 안 쓰잖아",
    ]
    drop = [
        "| 카테고리 | 점수 |",                      # 표
        "```python\nprint(1)\n```",                 # 코드펜스
        "C:" + BACKSLASH + "Users" + BACKSLASH + "user",   # 경로
        "## 제목입니다",                             # 헤더
        "<system-reminder>뭔가</system-reminder>",   # 시스템
        "The quick brown fox jumps over the lazy dog again and again",  # 영문
        "가" * 500,                                  # 400자 초과
    ]
    ok = True
    for t in keep:
        good = is_typed(t)
        print(f"  {'OK  ' if good else 'FAIL'} 사람 문장 통과: {t[:24]}")
        ok &= good
    for t in drop:
        good = not is_typed(t)
        label = t[:24].replace("\n", " ")
        print(f"  {'OK  ' if good else 'FAIL'} 붙여넣기 차단: {label}")
        ok &= good
    print("\nself-test:", "PASS" if ok else "FAILED — 필터를 먼저 고쳐라")
    return 0 if ok else 2


def main(argv):
    if "--self-test" in argv:
        return self_test()
    compare = "--compare" in argv
    n = 0
    if "--samples" in argv:
        i = argv.index("--samples")
        n = int(argv[i + 1]) if i + 1 < len(argv) else 12

    if not os.path.isdir(ROOT):
        print(f"실패: 대화 기록 폴더를 못 찾았다 — {ROOT}")
        return 2
    human, claude, files = harvest(ROOT)
    if not human:
        # 빈 결과를 성공으로 넘기면 "말투가 이렇다"는 거짓 결론이 나온다
        print("실패: 필터를 통과한 사용자 발화가 0건이다. 필터나 경로를 의심하라.")
        return 2
    report(human, claude, files, compare, n)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
