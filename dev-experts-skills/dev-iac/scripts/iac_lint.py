"""iac_lint.py - Infrastructure-as-Code smell detector (stdlib only, regex heuristic).

Detects (matching dev-iac SKILL.md antipattern catalog):
  [I4] hardcoded secret in .tf / .yml (password/token/key = "literal")
  [I6] terraform apply -auto-approve in a script
  [I2] Ansible raw command/shell without creates/when (non-idempotent)
  [I3] local-only terraform state hint (no backend block / path to terraform.tfstate)

Scans .tf / .yml / .yaml / .sh sources.

Usage:
  python iac_lint.py <file_or_dir> [...]
  python iac_lint.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with 'iac-ok:' comment.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

RE_SECRET = re.compile(r"""(?i)(password|secret|token|api[_-]?key|access[_-]?key)\s*[=:]\s*["'][^"'$]{8,}["']""")
RE_AUTO_APPROVE = re.compile(r"terraform\s+apply.*-auto-approve|-auto-approve")
RE_ANSIBLE_CMD = re.compile(r"^\s*(- )?(ansible\.builtin\.)?(command|shell)\s*:", re.I)


def scan_text(text: str, label: str, ext: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()

    def add(ln: int, code: str, msg: str):
        if 0 < ln <= len(lines) and "iac-ok:" in lines[ln - 1]:
            return
        findings.append(f"{label}:{ln}: [{code}] {msg}")

    for m in RE_SECRET.finditer(text):
        # allow obvious variable references (var., env, vault) - those don't match the literal pattern anyway
        add(text.count("\n", 0, m.start()) + 1, "I4",
            "hardcoded secret in IaC - code goes to git + state is plaintext; use a secret manager/vault ref")

    for m in RE_AUTO_APPROVE.finditer(text):
        add(text.count("\n", 0, m.start()) + 1, "I6",
            "terraform apply -auto-approve - read the plan first (destroy/replace = data loss); CI-verified paths only")

    # Ansible idempotency: command/shell block without creates/when in the next few lines
    for i, line in enumerate(lines):
        if RE_ANSIBLE_CMD.search(line):
            # window = current task only: stop at the next list item ('- ') or blank line
            window = [line]
            for nxt in lines[i + 1:i + 8]:
                if re.match(r"\s*- ", nxt) or not nxt.strip():
                    break
                window.append(nxt)
            block = "\n".join(window)
            if not re.search(r"\b(creates|removes|when)\s*:", block):
                add(i + 1, "I2", "raw command/shell without creates/when - non-idempotent; "
                    "use a module (apt/copy/template) or add a guard")

    # local state hint (terraform with no backend - heuristic: tfstate path mentioned, or .tf without backend)
    if ext == ".tf" and "backend" not in text and "terraform.tfstate" in text:
        add(1, "I3", "local terraform state - use a remote backend with locking (state is the source of truth)")
    return findings


DEMO_TF = '''\
resource "x" "y" {
  password = "supersecret123"
}
'''
DEMO_YML = '''\
- name: install
  command: apt-get install -y nginx
- name: copy with guard
  shell: ./setup.sh
  args:
    creates: /opt/done
'''
DEMO_SH = "terraform apply -auto-approve\n"


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files) - tf sample:")
        for ln in scan_text(DEMO_TF, "<main.tf>", ".tf"):
            print("  " + ln)
        print("demo mode - ansible sample:")
        for ln in scan_text(DEMO_YML, "<play.yml>", ".yml"):
            print("  " + ln)
        print("demo mode - shell sample:")
        for ln in scan_text(DEMO_SH, "<deploy.sh>", ".sh"):
            print("  " + ln)
        print("Usage: python iac_lint.py <file_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, _dirs, fs in os.walk(p):
                paths.extend(os.path.join(root, f) for f in fs
                             if f.endswith((".tf", ".yml", ".yaml", ".sh")))
        else:
            paths.append(p)
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        for ln in scan_text(text, path, os.path.splitext(path)[1]):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
