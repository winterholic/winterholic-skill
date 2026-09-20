#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from geometry_check import verify


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Check baseline SVG connector geometry.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        diagnostics = verify(args.file)
    except (OSError, UnicodeError) as exc:
        diagnostics = [
            {
                "code": "input/read-failed",
                "subject": str(args.file),
                "message": str(exc),
                "evidence": {},
                "supported_fixes": ["check that the UTF-8 HTML file exists and is readable"],
            }
        ]
    receipt = {
        "status": "fail" if diagnostics else "pass",
        "file": str(args.file.resolve()),
        "checks": {"diagonal_connector_lines": "fail" if diagnostics else "pass"},
        "diagnostics": diagnostics,
    }
    if args.as_json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    elif diagnostics:
        print(f"FAIL {args.file}")
        for item in diagnostics:
            print(f"  - [{item['code']}] {item['subject']}: {item['message']}")
    else:
        print(f"OK {args.file}")
    return 1 if diagnostics else 0


if __name__ == "__main__":
    raise SystemExit(main())
