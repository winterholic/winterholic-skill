"""docker_check.py - Dockerfile / compose smell detector (stdlib only).

Detects (matching dev-docker SKILL.md antipattern catalog):
  [D1] :latest tag or untagged image            (catalog #1)
  [D2] COPY . . before dependency install       (catalog #2)
  [D4] secret-looking value in ENV/environment  (catalog #4)
  [D7] compose service without logging limits   (catalog #7, compose only)

Usage:
  python docker_check.py <Dockerfile|compose.yml|dir> [...]
  python docker_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with comment '# docker-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

SECRET_RE = re.compile(
    r"(api[_-]?key|secret|token|passwd|password|credential)\s*[=:]\s*\S+", re.I
)
IMAGE_LINE_RE = re.compile(r"^\s*(?:image:|FROM)\s+([^\s#]+)", re.I)
DEP_INSTALL_RE = re.compile(r"\b(pip install|npm ci|npm install|poetry install|uv pip|apt-get install)\b")


def scan_dockerfile(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()
    copy_all_line = None
    dep_install_line = None
    for i, line in enumerate(lines, 1):
        if "docker-ok:" in line:
            continue
        m = IMAGE_LINE_RE.match(line)
        if m and line.strip().upper().startswith("FROM"):
            img = m.group(1)
            if img.endswith(":latest") or (":" not in img and "@" not in img and img != "scratch"):
                findings.append(f"{label}:{i}: [D1] base image '{img}' unpinned/latest - pin major.minor")
        if re.match(r"^\s*COPY\s+\.\s+", line) and copy_all_line is None:
            copy_all_line = i
        if DEP_INSTALL_RE.search(line) and dep_install_line is None:
            dep_install_line = i
        if re.match(r"^\s*ENV\s+", line) and SECRET_RE.search(line):
            findings.append(f"{label}:{i}: [D4] secret-looking ENV baked into image - inject at runtime")
    if copy_all_line and dep_install_line and copy_all_line < dep_install_line:
        findings.append(
            f"{label}:{copy_all_line}: [D2] 'COPY . .' before dependency install "
            f"(line {dep_install_line}) - cache busted on every code change; copy manifest first"
        )
    return findings


def scan_compose(text: str, label: str) -> list[str]:
    """Line-based YAML heuristic - no yaml module dependency assumptions kept minimal."""
    findings: list[str] = []
    lines = text.splitlines()
    # crude service blocks: two-space indented keys under 'services:'
    in_services = False
    current: str | None = None
    svc_lines: dict[str, list[tuple[int, str]]] = {}
    for i, line in enumerate(lines, 1):
        if re.match(r"^services:\s*$", line):
            in_services = True
            continue
        if in_services and re.match(r"^\S", line):  # left col key ends services block
            in_services = False
        if in_services:
            m = re.match(r"^  (\w[\w-]*):\s*$", line)
            if m:
                current = m.group(1)
                svc_lines[current] = []
            elif current:
                svc_lines[current].append((i, line))
    for svc, body in svc_lines.items():
        text_body = "\n".join(l for _, l in body)
        first = body[0][0] if body else 1
        for i, line in body:
            if "docker-ok:" in line:
                continue
            m = re.search(r"image:\s*([^\s#]+)", line)
            if m:
                img = m.group(1)
                if img.endswith(":latest") or ":" not in img:
                    findings.append(f"{label}:{i}: [D1] service '{svc}' image '{img}' unpinned/latest")
            if SECRET_RE.search(line) and "environment" not in line and "env_file" not in line:
                if re.search(r"^\s*-?\s*\w*(KEY|SECRET|TOKEN|PASSWORD)\w*\s*[=:]\s*\S{8,}", line, re.I):
                    findings.append(f"{label}:{i}: [D4] inline secret value in compose - use env_file outside repo")
        if "logging" not in text_body and "docker-ok" not in text_body:
            findings.append(f"{label}:{first}: [D7] service '{svc}' has no logging limits - json-file grows unbounded")
    return findings


def scan_file(path: str) -> list[str]:
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return [f"{path}: not found - skipped"]
    except UnicodeDecodeError:
        with open(path, encoding="cp949", errors="replace") as f:
            text = f.read()
    name = os.path.basename(path).lower()
    if "dockerfile" in name:
        return scan_dockerfile(text, path)
    if name.endswith((".yml", ".yaml")):
        return scan_compose(text, path)
    return []


def iter_files(paths: list[str]) -> list[str]:
    out: list[str] = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for f in files:
                    fl = f.lower()
                    if "dockerfile" in fl or fl in ("compose.yml", "compose.yaml",
                                                    "docker-compose.yml", "docker-compose.yaml"):
                        out.append(os.path.join(root, f))
        else:
            out.append(p)
    return out


DEMO_DOCKERFILE = """\
FROM python:latest
ENV API_KEY=sk-abcdef123456
COPY . .
RUN pip install -r requirements.txt
"""

DEMO_COMPOSE = """\
services:
  db:
    image: postgres:latest
    volumes:
      - pgdata:/var/lib/postgresql/data
  api:
    image: myapp:0.3
    logging:
      driver: json-file
      options: {max-size: "10m", max-file: "3"}
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode - scanning built-in Dockerfile sample:")
        for ln in scan_dockerfile(DEMO_DOCKERFILE, "<Dockerfile>"):
            print("  " + ln)
        print("demo mode - scanning built-in compose sample:")
        for ln in scan_compose(DEMO_COMPOSE, "<compose>"):
            print("  " + ln)
        print("Usage: python docker_check.py <Dockerfile|compose.yml|dir> ...")
        return 0

    total = 0
    for path in iter_files(argv):
        for ln in scan_file(path):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
