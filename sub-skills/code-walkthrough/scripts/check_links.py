#!/usr/bin/env python3
"""code-walkthrough HTML 산출물의 링크 정합성 검사.

깨진 점프(xref가 없는 id를 가리킴)와 모달 모드의 라인↔노트 불일치
(data-notes ↔ data-for)를 잡는다. 둘 다 "클릭해도 안 가는/안 뜨는"
죽은 UI를 만드므로 보고서 가치를 직접 떨어뜨린다.

사용: python3 check_links.py <산출물.html>
종료 코드: 문제 없으면 0, 있으면 1.
"""
import re
import sys


def check(path: str) -> int:
    html = open(path, encoding="utf-8").read()

    ids = set(re.findall(r'id="(L-[\w-]+)"', html))
    file_ids = set(re.findall(r'id="(file-[\w-]+)"', html))
    xref = set(re.findall(r'href="#(L-[\w-]+)"', html))
    file_links = set(re.findall(r'href="#(file-[\w-]+)"', html))
    data_notes = set(re.findall(r'data-notes="(L-[\w-]+)"', html))
    data_for = set(re.findall(r'data-for="(L-[\w-]+)"', html))
    slots = re.findall(r"\{\{[^}]+\}\}", html)

    problems = []
    dead = xref - ids
    if dead:
        problems.append(f"깨진 xref 점프(타깃 id 없음): {sorted(dead)}")
    dead_file = file_links - file_ids
    if dead_file:
        problems.append(f"깨진 파일 점프 링크: {sorted(dead_file)}")
    # 모달 모드일 때만 의미 있음 (data-notes가 있을 때)
    if data_notes or data_for:
        no_store = data_notes - data_for
        if no_store:
            problems.append(f"클릭 라인에 대응 노트 없음(data-for 누락): {sorted(no_store)}")
        orphan = data_for - data_notes
        if orphan:
            problems.append(f"노트만 있고 클릭 라인 없음(data-notes 누락): {sorted(orphan)}")
        missing_line = data_notes - ids
        if missing_line:
            problems.append(f"data-notes가 실제 라인 id에 없음: {sorted(missing_line)}")
    if slots:
        problems.append(f"미치환 슬롯 {len(slots)}개 남음: {slots[:5]}{' …' if len(slots) > 5 else ''}")

    if problems:
        print(f"[FAIL] {path}")
        for p in problems:
            print("  - " + p)
        return 1
    print(f"[OK] {path} — xref {len(xref)} / 라인 {len(ids)} / 파일 {len(file_ids)} 정합")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용: python3 check_links.py <산출물.html>")
        sys.exit(2)
    sys.exit(check(sys.argv[1]))
