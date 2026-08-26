"""workflow_check.py - GitHub Actions workflow smell detector (stdlib only).

Detects (matching dev-cicd SKILL.md antipattern catalog):
  [C3a] uses: ...@master / @main (mutable ref)
  [C3b] third-party action pinned by tag, not SHA      (heuristic: not actions/* or github/*)
  [C6]  job without timeout-minutes
  [C4]  actions/cache with constant key (no hashFiles)
  [C2]  pull_request_target together with checkout of PR head (secret exposure shape)

Usage:
  python workflow_check.py <yml_file_or_dir> [...]
  python workflow_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '# ci-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

OFFICIAL_PREFIXES = ("actions/", "github/", "docker/")


def scan_workflow(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    has_prt = bool(re.search(r"^\s*pull_request_target\s*:", text, re.M)) or \
        bool(re.search(r"on:\s*\[?[^\]]*pull_request_target", text))
    checks_out_head = bool(re.search(r"ref:\s*\$\{\{\s*github\.event\.pull_request\.head", text))
    if has_prt and checks_out_head:
        findings.append(f"{label}:1: [C2] pull_request_target + PR-head checkout - "
                        "runs untrusted code with secrets; use pull_request or split jobs")

    job_indent_re = re.compile(r"^  (\w[\w-]*):\s*$")
    in_jobs = False
    current_job: str | None = None
    job_has_timeout: dict[str, bool] = {}
    job_first_line: dict[str, int] = {}
    for i, line in enumerate(lines, 1):
        if re.match(r"^jobs:\s*$", line):
            in_jobs = True
            continue
        if in_jobs and re.match(r"^\S", line):
            in_jobs = False
        if in_jobs:
            m = job_indent_re.match(line)
            if m:
                current_job = m.group(1)
                job_has_timeout[current_job] = False
                job_first_line[current_job] = i
            elif current_job and "timeout-minutes" in line:
                job_has_timeout[current_job] = True

        if "ci-ok:" in line:
            continue
        m = re.search(r"uses:\s*([^\s#]+)", line)
        if m:
            ref = m.group(1)
            if "@" in ref:
                action, ver = ref.rsplit("@", 1)
                if ver in ("master", "main"):
                    findings.append(f"{label}:{i}: [C3a] '{ref}' pinned to moving branch - pin tag or SHA")
                elif not action.startswith(OFFICIAL_PREFIXES) and not re.fullmatch(r"[0-9a-f]{40}", ver):
                    findings.append(f"{label}:{i}: [C3b] third-party '{ref}' not SHA-pinned - "
                                    "tags can be re-pointed (tj-actions 2025)")
            elif not ref.startswith("./"):
                findings.append(f"{label}:{i}: [C3a] '{ref}' has no version pin at all")
        if "actions/cache" in line:
            # look ahead a few lines for key:
            window = "\n".join(lines[i - 1:i + 6])
            keym = re.search(r"key:\s*(.+)", window)
            if keym and "hashFiles" not in keym.group(1) and "${{" not in keym.group(1):
                findings.append(f"{label}:{i}: [C4] cache key '{keym.group(1).strip()}' is constant - "
                                "stale deps forever; key on hashFiles(manifest)")

    for job, has_to in job_has_timeout.items():
        if not has_to:
            findings.append(f"{label}:{job_first_line[job]}: [C6] job '{job}' has no timeout-minutes "
                            "(default 360m hogs a runner)")
    return sorted(set(findings))


def iter_files(paths: list[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                out.extend(os.path.join(root, f) for f in files if f.endswith((".yml", ".yaml")))
        else:
            out.append(p)
    return out


DEMO = """\
on:
  pull_request_target:
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - uses: tj-actions/changed-files@v45
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-cache
      - uses: some/thing@master
  build:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_workflow(DEMO, "<demo.yml>"):
            print("  " + ln)
        print("Usage: python workflow_check.py <yml_or_dir> ...")
        return 0

    total = 0
    for path in iter_files(argv):
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"{path}: not found - skipped")
            continue
        for ln in scan_workflow(text, path):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
