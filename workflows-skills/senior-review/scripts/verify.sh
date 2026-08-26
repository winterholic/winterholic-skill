#!/usr/bin/env bash
# pr-review 산출물 자체검증 — append/갱신 후 "제대로 들어갔는지" 자동 점검.
# SKILL.md 6단계(작성)·7단계(append) 직후 실행. Edit 성공 ≠ 올바른 삽입이므로 필수.
#
# 사용법: bash verify.sh <리뷰_HTML_경로>
# 종료코드: 0 = 전부 통과, 1 = 하나라도 실패(상세는 stdout)

set -uo pipefail

F="${1:-}"
if [[ -z "$F" || ! -f "$F" ]]; then
  echo "usage: bash verify.sh <review-html-path>" >&2
  exit 2
fi

fail=0
note() { printf '  %s\n' "$1"; }
ok()   { printf 'OK   %s\n' "$1"; }
bad()  { printf 'FAIL %s\n' "$1"; fail=1; }
warn() { printf 'WARN %s\n' "$1"; }  # 오탐 가능 항목 — 종료코드에 반영 안 함(육안 확인용)

# 1) 실제 삽입 마커 정확히 1개 (다음 라운드 기준점) ----------------------------
#    template은 설명 주석 헤더(<!-- ROUND-INSERT-MARKER ───)와 실제 마커
#    (<!-- ROUND-INSERT-MARKER -->) 2종을 갖는다. 단독 닫힌 마커만 카운트.
marker_count=$(grep -cE '<!-- ROUND-INSERT-MARKER -->' "$F")
if [[ "$marker_count" == "1" ]]; then
  ok "실제 삽입 마커(<!-- ROUND-INSERT-MARKER -->) 1개 보존"
else
  bad "삽입 마커 개수=$marker_count (1이어야 함 — 삭제·중복·이동 의심)"
fi

# 2) 미치환 placeholder 탐지 ({NUMBER},{PR_TITLE},{SHA},{REPO_URL} 등 대문자 토큰)
#    CSS 중괄호와 구분 위해 {ALL_CAPS} 패턴만. 코드박스의 의도적 리터럴({ENV} 등)은
#    오탐 가능 → WARN(육안 확인)으로만, 종료코드엔 반영 안 함.
slots=$(grep -oE '\{[A-Z][A-Z0-9_]+\}' "$F" | sort -u)
if [[ -z "$slots" ]]; then
  ok "미치환 placeholder 없음"
else
  warn "미치환 의심 placeholder (코드박스 리터럴이면 무시):"; echo "$slots" | while read -r s; do note "$s"; done
fi

# 3) TOC/본문 anchor 정합 — href="#id" 가 가리키는 id가 실제 존재하는가 -----------
#    내부 anchor(#로 시작)만 대상. 외부 링크·빈 href 제외.
hrefs=$(grep -oE 'href="#[A-Za-z0-9_-]+"' "$F" | sed -E 's/href="#(.*)"/\1/' | sort -u)
ids=$(grep -oE 'id="[A-Za-z0-9_-]+"' "$F" | sed -E 's/id="(.*)"/\1/' | sort -u)
dangling=""
while read -r h; do
  [[ -z "$h" ]] && continue
  if ! grep -qxF "$h" <<<"$ids"; then
    dangling+="$h"$'\n'
  fi
done <<<"$hrefs"
if [[ -z "${dangling//[$'\n']/}" ]]; then
  ok "내부 anchor 전부 실제 id로 해결됨"
else
  bad "깨진 anchor(가리키는 id 없음):"; echo "$dangling" | sed '/^$/d' | while read -r d; do note "#$d"; done
fi

# 3.5) <p> 안의 블록 요소 (브라우저가 <p>를 자동 종료 → stray </p> → DOM 틀어짐) ----
#      휴리스틱: 한 줄에서 <p 이후에 </p>보다 <div 가 먼저 등장하면 위반.
p_block=$(awk 'match($0, /<p[ >]/) { s = substr($0, RSTART); d = index(s, "<div"); c = index(s, "</p>"); if (d && (!c || d < c)) print NR ": " substr($0, 1, 140) }' "$F" | head -5)
if [[ -z "$p_block" ]]; then
  ok "<p> 안에 블록(div) 요소 없음"
else
  bad "<p> 안에 <div> 발견 — <p>설명</p> 닫은 뒤 형제로 옮길 것:"
  echo "$p_block" | while IFS= read -r l; do note "${l:0:140}"; done
fi

# 3.6) codebox 본문이 bare <pre> (코드가 다크 배경에 묻혀 안 보임 — SR-8 2차 실측) --
#      .codebox-body 바로 안에 <pre>가 오면 .codebox-code 셀렉터(색·줄·하이라이트)가
#      안 걸린다. 본문은 반드시 <div class="codebox-code">에 넣어야 한다.
pre_box=$(grep -nE '<div class="codebox-body"[^>]*>[[:space:]]*<pre' "$F" | head -5)
if [[ -z "$pre_box" ]]; then
  ok "codebox 본문에 bare <pre> 없음 (.codebox-code 사용)"
else
  bad "codebox-body 안에 bare <pre> — 코드가 안 보인다. <div class=\"codebox-code\">로 감쌀 것:"
  echo "$pre_box" | while IFS= read -r l; do note "${l:0:140}"; done
fi

# 3.7) codebox-gutter 안에 <span> (줄번호가 한 줄로 뭉쳐 코드와 어긋남 — SR-15 실측) --
#       gutter는 줄바꿈 구분 순수 숫자여야 한다. <span>으로 감싸면 inline이라 번호가 붙는다.
#       (템플릿 CSS에 .codebox-gutter .ln{display:block} 방어가 있어 치명적이진 않으므로 WARN.)
gutter_span=$(grep -nE '<div class="codebox-gutter"[^>]*>[^<]*<span' "$F" | head -5)
if [[ -z "$gutter_span" ]]; then
  ok "codebox-gutter가 순수 줄번호 (span 없음)"
else
  warn "codebox-gutter 안에 <span> — 줄번호를 줄바꿈 구분 순수 숫자로 둘 것(span 제거):"
  echo "$gutter_span" | while IFS= read -r l; do note "${l:0:140}"; done
fi

# 3.8) #background 카드 본문이 영어 (출력 언어 한국어 위반 — SR-15 실측) -------------
#       한글이 한 글자도 없는데 라틴 알파벳이 다수면 영어로 채워졌을 가능성.
if command -v python3 >/dev/null 2>&1; then
  bg_lang=$(python3 - "$F" <<'PY'
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r'id="background".*?</section>', s, re.S)
if not m:
    print("OK"); sys.exit()
sec = m.group(0)
# 배경 카드의 각 <p> 단락을 개별 검사 — 한 단락이라도 라틴 다수·한글 희소면 영어 본문.
bad_paras = 0
for p in re.findall(r'<p\b[^>]*>(.*?)</p>', sec, re.S):
    txt = re.sub(r'<[^>]+>', ' ', p)                 # 인라인 태그 제거
    txt = re.sub(r'&[a-z#0-9]+;', ' ', txt)          # 엔티티 제거
    hangul = len(re.findall(r'[가-힣]', txt))
    latin  = len(re.findall(r'[A-Za-z]', txt))
    if latin > 120 and hangul < 10:                  # 긴 영어 단락
        bad_paras += 1
print("FAIL" if bad_paras else "OK")
PY
)
  if [[ "$bg_lang" == "FAIL" ]]; then
    bad "#background 카드가 영어로 채워진 듯 — 한국어로 옮겨 쓸 것(context 필드 값 번역)."
  else
    ok "#background 카드 한국어"
  fi
fi

# 4) 닫는 태그 존재 (append가 </body></html> 뒤로 새지 않았는지 최소 확인) --------
if grep -q '</body>' "$F" && grep -q '</html>' "$F"; then
  # </html> 뒤에 비공백 내용이 있으면 경고
  after=$(awk 'f{print} /<\/html>/{f=1}' "$F" | tr -d '[:space:]')
  if [[ -z "$after" ]]; then
    ok "</body></html> 정상 종료, 뒤 잔여 내용 없음"
  else
    bad "</html> 뒤에 내용이 있음 — append가 문서 밖으로 샜을 가능성"
  fi
else
  bad "</body> 또는 </html> 누락"
fi

# 5) 디자인 시스템 정합 — 정의 안 된 CSS 변수/클래스 사용, 컴포넌트 래퍼 누락 ------
#    append 라운드가 디자인 시스템에서 이탈하는 전형(SR-7 3차 실측: --muted-foreground
#    미정의·.rp-content 래퍼 누락·.priority 모디파이어 누락)을 잡는다.
if command -v python3 >/dev/null 2>&1; then
  css_report=$(python3 - "$F" <<'PY'
import re, sys
s = open(sys.argv[1], encoding="utf-8").read()
problems = []

# (a) 정의 안 된 CSS 변수: var(--x) 사용분이 --x: 정의에 다 있어야
used = set(re.findall(r'var\(\s*(--[A-Za-z0-9-]+)', s))
defined = set(re.findall(r'(--[A-Za-z0-9-]+)\s*:', s))
for v in sorted(used - defined):
    problems.append(f"정의 안 된 CSS 변수 사용: var({v}) — :root에 정의 없음")

# (b) review-point(details)마다 .rp-content 래퍼가 있어야 (없으면 padding/구분선 깨짐)
for m in re.finditer(r'<details\b[^>]*class="[^"]*\breview-point\b[^"]*"[^>]*>', s):
    start = m.end()
    end = s.find('</details>', start)
    body = s[start:end if end != -1 else len(s)]
    if 'class="rp-content"' not in body:
        snippet = re.sub(r'\s+', ' ', body[:90])
        problems.append(f"review-point에 .rp-content 래퍼 누락 → 본문 padding/구분선 깨짐: …{snippet}…")

# (c) 모디파이어가 있어야 색이 붙는 클래스를 단독(bare)으로 사용
#     priority/action-tag/severity-tag 는 base만으론 색/배경이 없다.
mods = {
    'priority':    {'required','recommended','optional','fyi'},
    'action-tag':  {'required','recommended','optional','out-of-scope'},
    'severity-tag':{'critical','medium','minor','info','good','check'},
}
for m in re.finditer(r'class="([^"]*)"', s):
    classes = m.group(1).split()
    for base, valid in mods.items():
        if base in classes and not (set(classes) & valid):
            problems.append(f'.{base} 를 모디파이어 없이 단독 사용 (색 안 붙음) — class="{m.group(1)}"; 유효: {sorted(valid)}')

# 중복 제거(같은 메시지 여러 번)
seen, out = set(), []
for p in problems:
    if p not in seen:
        seen.add(p); out.append(p)
if out:
    print("FAIL")
    for p in out[:20]:
        print(p)
    if len(out) > 20:
        print(f"... 외 {len(out)-20}건")
else:
    print("OK")
PY
)
  if [[ "${css_report%%$'\n'*}" == "OK" ]]; then
    ok "디자인 시스템 정합 (CSS 변수·클래스·컴포넌트 래퍼)"
  else
    bad "디자인 시스템 이탈 — template 정의 밖 CSS 사용/래퍼 누락:"
    echo "$css_report" | tail -n +2 | while IFS= read -r l; do note "$l"; done
  fi
else
  warn "python3 없음 — 디자인 시스템 정합(CSS 변수·클래스) 검사 생략, 육안 확인 필요"
fi

echo
if [[ "$fail" == "0" ]]; then
  echo "== 전부 통과 =="
else
  echo "== 실패 항목 있음 — 위 FAIL 확인 후 수정 =="
fi
exit "$fail"
