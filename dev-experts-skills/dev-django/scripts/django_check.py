"""django_check.py - Django project smell detector (stdlib only).

Detects (matching dev-django SKILL.md antipattern catalog):
  [D4a] DEBUG = True in a settings file
  [D4b] hardcoded SECRET_KEY literal in settings
  [D1]  attribute access on FK inside a for loop over .objects (N+1 shape, heuristic)
  [D2]  `if queryset:` / len(queryset) shapes where .exists()/.count() fit (heuristic)

Usage:
  python django_check.py <py_file_or_dir> [...]
  python django_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '# django-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

RE_DEBUG = re.compile(r"^\s*DEBUG\s*=\s*True\b", re.M)
RE_SECRET = re.compile(r"^\s*SECRET_KEY\s*=\s*['\"][^'\"]{10,}['\"]", re.M)
RE_LOOP_FK = re.compile(
    r"for\s+(\w+)\s+in\s+\w+\.objects\.(?:all|filter)\([^)]*\)\s*:\s*\n"
    r"(?:.*\n){0,5}?\s*.*\b\1\.(\w+)\.(\w+)", re.M)
RE_IF_QS = re.compile(r"\b(?:if|while)\s+\w*(?:qs|queryset)\w*\s*:", re.I)
RE_LEN_QS = re.compile(r"\blen\(\s*\w*(?:qs|queryset)\w*\s*\)", re.I)


def scan_text(text: str, label: str, is_settings: bool) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def line_of(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    def silenced(ln: int) -> bool:
        return 0 < ln <= len(lines) and "django-ok:" in lines[ln - 1]

    if is_settings:
        for pattern, code, msg in (
            (RE_DEBUG, "D4a", "DEBUG=True - must come from env; prod True leaks settings via debug page"),
            (RE_SECRET, "D4b", "hardcoded SECRET_KEY - read from env; rotate if ever committed"),
        ):
            m = pattern.search(text)
            if m and not silenced(line_of(m.start())):
                findings.append(f"{label}:{line_of(m.start())}: [{code}] {msg}")

    for m in RE_LOOP_FK.finditer(text):
        ln = line_of(m.start())
        if not silenced(ln):
            findings.append(f"{label}:{ln}: [D1] FK attribute access in loop over .objects - "
                            "N+1 shape; add select_related/prefetch_related")
    for pattern in (RE_IF_QS, RE_LEN_QS):
        for m in pattern.finditer(text):
            ln = line_of(m.start())
            if not silenced(ln):
                findings.append(f"{label}:{ln}: [D2] truthiness/len on queryset - "
                                "evaluates all rows; use .exists() / .count()")
    return sorted(set(findings))


DEMO_SETTINGS = """\
DEBUG = True
SECRET_KEY = 'django-insecure-abc123def456'
"""

DEMO_VIEW = """\
def order_list(request):
    qs = Order.objects.filter(user=request.user)
    if qs:
        for o in Order.objects.all():
            print(o.member.name)
    return render(request, "list.html", {"orders": list(qs)})
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode - settings sample:")
        for ln in scan_text(DEMO_SETTINGS, "<settings.py>", True):
            print("  " + ln)
        print("demo mode - view sample:")
        for ln in scan_text(DEMO_VIEW, "<views.py>", False):
            print("  " + ln)
        print("Usage: python django_check.py <py_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, _dirs, fs in os.walk(p):
                paths.extend(os.path.join(root, f) for f in fs if f.endswith(".py"))
        else:
            paths.append(p)
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        is_settings = "settings" in os.path.basename(path) or "settings" in path.replace("\\", "/").split("/")[-2:][0]
        for ln in scan_text(text, path, is_settings):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
