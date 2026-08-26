"""nest_check.py - NestJS source smell detector (stdlib only, regex heuristic).

Detects (matching dev-nestjs SKILL.md antipattern catalog):
  [N5] forwardRef usage (circular dependency papered over)
  [N4] Scope.REQUEST provider (contagious per-request instantiation)
  [N2] manual body validation shape in a controller (if (!body.x) throw)

Usage:
  python nest_check.py <ts_file_or_dir> [...]
  python nest_check.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '// nest-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

CHECKS = [
    ("N5", re.compile(r"\bforwardRef\s*\("),
     "forwardRef - circular dependency signal; extract shared module or break with events"),
    ("N4", re.compile(r"Scope\.REQUEST"),
     "REQUEST scope - contagious re-instantiation per request; default singleton + pass context"),
    ("N2", re.compile(r"if\s*\(\s*!\s*(?:body|dto|req\.body)\.\w+\s*\)\s*(?:\{\s*)?throw"),
     "manual body validation - declare it on the DTO; is global ValidationPipe(whitelist) on?"),
]


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()
    for code, pattern, msg in CHECKS:
        for m in pattern.finditer(text):
            ln = text.count("\n", 0, m.start()) + 1
            if 0 < ln <= len(lines) and "nest-ok:" in lines[ln - 1]:
                continue
            findings.append(f"{label}:{ln}: [{code}] {msg}")
    return sorted(set(findings))


DEMO = """\
@Injectable({ scope: Scope.REQUEST })
export class WatchService {
  constructor(@Inject(forwardRef(() => UserService)) private users: UserService) {}
}

@Controller("watch")
export class WatchController {
  @Post()
  add(@Body() body: any) {
    if (!body.code) throw new BadRequestException();
    return this.svc.add(body);
  }
}
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<demo.ts>"):
            print("  " + ln)
        print("Usage: python nest_check.py <ts_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, dirs, fs in os.walk(p):
                dirs[:] = [d for d in dirs if d != "node_modules"]
                paths.extend(os.path.join(root, f) for f in fs if f.endswith(".ts"))
        else:
            paths.append(p)
    for path in paths:
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        for ln in scan_text(text, path):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
