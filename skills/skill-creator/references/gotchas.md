# Gotchas — 이 하네스에서 실제로 터진 것들

전부 실측이거나 실사고다. 추측으로 채우지 않는다. 새 함정이 나오면 여기 덧붙인다.

---

## 1. frontmatter `name` 이 디렉터리명과 다르면 스킬이 두 이름으로 등록된다

**증상**: `skills/skill-creator/SKILL.md` 의 frontmatter 가 `name: claude-code-skill-optimizer` 였다. 그 결과 등록 경로 둘이 서로 다른 이름을 썼다.

- 세션의 available-skills 목록 → `skill-creator` (디렉터리명)
- `/context` 의 Skills 표 → `claude-code-skill-optimizer` (frontmatter)

**경과**: 2026-08-26 에 처음 관측하고 available-skills 목록만 보고 "문제 없음"으로 판정했다. **그 판정이 성급했다.** 08-27 재관측에서 두 경로가 갈린다는 게 확인돼 판정을 정정했다. 그 뒤 5회에 걸쳐 수정을 제안했고 2026-08-29 `/doctor` 정리에서 고쳤다.

**교훈**: 한쪽 표시 경로만 보고 "괜찮다"고 결론짓지 말 것. `check-skill.py` 가 이 항목을 FAIL 로 잡는다.

---

## 2. 빼기와 「다른 경로로 배달하기」는 다르다 — 도달 경로가 없으면 안 읽힌다

**증상**: `harness-engineering` 라이브러리를 `skills-manual/` 아래 두었다. 그 폴더는 스캔 대상이 아니라 **로드도 자동 트리거도 되지 않았다.** 실제 Read 는 **0~1회**였다. 그 상태에서 references 만 55 → 72개로 늘렸다.

**조치**: `skills/harness-engineering` → `skills-manual/harness-engineering` 심링크를 걸어 스킬로 등록했다. description 만 매 세션 로드되고 본문은 트리거될 때 열린다.

**교훈**: **이득은 산문이 아니라 구조에서 온다.** CLAUDE.md 의 포인터 문장을 다듬는 것보다 등록 위치를 바꾸는 것이 도달률을 바꾼다. 새 스킬을 만들 때는 **어떻게 그 스킬에 도달하는지**를 같이 설계한다. 폴더만 만들고 끝내면 아무도 안 읽는다.

---

## 3. `sub-skills/`·`workflows-skills/`·`imported-sub-skills/` 는 자동 트리거되지 않는다

`skills/` 직속만 description 이 컨텍스트에 올라간다. 나머지 폴더에 둔 스킬은 **이름으로 호출하거나 경로에서 `SKILL.md` 를 직접 읽어야** 한다.

새 스킬을 어디 둘지는 **상시 비용을 낼 값어치가 있는가**로 정한다.

| 둘 곳 | 비용 | 조건 |
|---|---|---|
| `skills/` | 스킬당 ~100토큰 상시 | 트리거가 자동으로 걸려야 하는 것 |
| `sub-skills/` 등 | 0 | 이름을 알고 부를 때만 쓰는 것 |

디스패처(`dev-experts`·`biz-experts`·`life-experts`·`stock-experts`) 뒤에 두는 전문가 팩은 후자다. 팩 멤버 하나하나를 `skills/` 에 올리면 description 만으로 컨텍스트가 터진다.

---

## 4. 스킬을 늘리면 `skill-list.md` 가 곧 거짓말이 된다

**증상**: 회사 환경에서 이 갱신 규칙이 없어 **주력 스킬 6개가 누락되고 이미 지운 스킬이 목록에 남아** 양방향으로 어긋난 전례가 있다.

**규칙**: 스킬을 만들거나 지우거나 옮기면 **같은 작업에서** `~/.claude\skill-list.md` 를 고친다. 표의 행뿐 아니라 **상단 개수**도 같이 고친다. 지도가 낡으면 이후 스킬 선택이 전부 틀어진다.

권위의 원천은 이 파일이 아니라 **세션이 실제로 로드한 스킬 목록**이다. 둘이 어긋나면 세션을 믿고 파일을 고친다.

---

## 5. 서브에이전트 안에서 스킬을 호출하면 조용히 no-op 이 될 수 있다

역할만 인라인으로 연기되고 실제 스킬은 안 열린다. 그러면 "검증했다"가 **검증 라벨을 단 자기확인**이 된다.

스킬이 서브에이전트에 의존하는 설계라면, 에이전트의 *스킬을 돌렸다*는 주장을 산출물이 증명하기 전까지 미검증으로 취급한다.

출처: `skills/agent-delegation/SKILL.md`

---

## 6. 저자 세션의 "잘 되는데요"는 증거가 아니다

스킬을 작성한 세션은 의도를 컨텍스트에 갖고 있어 description 이 부실해도 알아서 트리거하고 본문의 모호함을 메워 읽는다. 트리거 검증은 **반드시 fresh 세션**에서 한다.

---

## 7. `sub-skills/writer` 는 공개 금지

이걸 어겨 공개 레포에 푸시했고, force push 로도 SHA 조회가 남아 **레포를 삭제·재생성**했다(2026-08-26 실사고).

2026-09-03에 자동 트리거 경합을 없애려고 `skills/writer`에서 `sub-skills/writer`로 옮겼다. 위치가 바뀌어도 공개 금지는 그대로다.

공개 미러(`C:\opensource\winterholic-skill\`)로 나가는 것은 **오직** `scripts\sync-winterholic-skill.py` 로만 동기화한다. 손으로도 임시 스크립트로도 복사하지 않는다. exit code 가 0이 아니면 커밋하지 않는다.

새 스킬을 만들 때 **공개 가능 여부를 그 자리에서 판정**하고, 비공개면 그 사실을 스킬 안에 적는다.

---

## 8. Windows 콘솔은 cp949 다

스킬에 파이썬 스크립트를 번들할 때, 한글을 출력하면 `UnicodeEncodeError` 로 죽는다. 첫머리에 넣는다.

```python
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
```

경로에 Windows 절대경로를 쓸 때는 `\U`·`\n` 이스케이프를 조심한다. heredoc 안에서 특히 잘 터진다.

---

## 9. 검사기가 타 스킬 번들 참조를 죽은 참조로 오탐했다 (2026-09-03 발견·수정)

**증상**: `check-skill.py` 가 `SKILL.md` 의 `references/batch-evaluation.md` 를 "아직 없는 번들"로 WARN 했다. 그 문장은 skills-estimate 의 번들을 "그쪽"으로 받아 가리키고 있었고, 파일은 `skills/skills-estimate/references/` 에 **실재했다.** 검사기가 모든 번들 참조를 자기 폴더 기준으로만 풀어서 난 오탐이다.

**조치**: 문맥(220자)에 이름이 나온 형제 스킬 폴더에서 풀리면 실참조로 인정한다. 동시에 self-test 에 `dead-bundle-ref-cross` 를 넣어 **오탐 수정이 미탐으로 뒤집히지 않는지**를 붙박이로 검증한다.

**교훈**: 검사 결과가 이상하면 **대상보다 검사기를 먼저 의심한다.** 그리고 오탐을 없앨 때는 반대 방향 테스트를 같이 넣는다. 안 그러면 다음 라운드에 진짜 죽은 참조가 조용히 통과한다. WARN 을 무시하는 습관이 붙으면 검사기는 있으나 마나다.
