#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import geometry_check
import self_check


try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def self_check_code(message: str) -> str:
    lowered = message.casefold()
    if "duplicate id" in lowered:
        return "document/duplicate-id"
    if "unresolved fragment" in lowered:
        return "document/unresolved-fragment"
    if "svg" in lowered or "aria" in lowered or "title" in lowered or "desc" in lowered:
        return "accessibility/svg-contract"
    if "motion" in lowered or "step" in lowered or "controller" in lowered:
        return "motion/contract"
    if "remote" in lowered or "executable" in lowered or "not allowed" in lowered:
        return "safety/single-file-contract"
    return "self-check/violation"


def structured_self_check(path: Path) -> list[dict[str, Any]]:
    return [
        {
            "code": self_check_code(message),
            "subject": "$document",
            "message": message,
            "evidence": {"checker": "self_check.py", "finding": message},
            "supported_fixes": ["repair the named contract violation and validate again"],
        }
        for message in self_check.verify(path)
    ]


def validation_receipt(path: Path) -> dict[str, Any]:
    try:
        read_failed = False
        data = path.read_bytes()
        self_diagnostics = structured_self_check(path)
        geometry = geometry_check.verify(path)
        diagnostics = self_diagnostics + geometry
    except (OSError, UnicodeError) as exc:
        read_failed = True
        data = b""
        self_diagnostics = []
        diagnostics = [
            {
                "code": "input/read-failed",
                "subject": str(path),
                "message": str(exc),
                "evidence": {},
                "supported_fixes": ["check that the UTF-8 HTML file exists and is readable"],
            }
        ]
        geometry = []
    return {
        "status": "fail" if diagnostics else "pass",
        "artifact_validation": "failed" if diagnostics else "passed",
        "browser_evidence": "not_run",
        "visual_review": "not_run",
        "candidate": {
            "path": str(path.resolve()),
            "sha256": sha256(data),
            "bytes": len(data),
        },
        "checks": {
            "self_check": "not_run" if read_failed else ("fail" if self_diagnostics else "pass"),
            "geometry": "not_run" if read_failed else ("fail" if geometry else "pass"),
        },
        "diagnostics": diagnostics,
    }


def deliver(candidate: Path, output: Path) -> dict[str, Any]:
    receipt = validation_receipt(candidate)
    receipt["output"] = str(output.resolve())
    if output.suffix.casefold() != ".html":
        receipt["status"] = "fail"
        receipt["artifact_validation"] = "failed"
        receipt["diagnostics"].append(
            {
                "code": "output/extension",
                "subject": str(output),
                "message": "Delivered diagram output must end in .html.",
                "evidence": {"suffix": output.suffix},
                "supported_fixes": ["choose an output path ending in .html"],
            }
        )
        return receipt
    if receipt["diagnostics"]:
        return receipt

    data = candidate.read_bytes()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{output.name}.",
            suffix=".candidate",
            dir=output.parent,
            delete=False,
        ) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.replace(temporary, output)
        temporary = None
    except OSError as exc:
        receipt["status"] = "fail"
        receipt["artifact_validation"] = "failed"
        receipt["diagnostics"].append(
            {
                "code": "delivery/commit-failed",
                "subject": str(output),
                "message": str(exc),
                "evidence": {},
                "supported_fixes": ["repair the output directory permissions and retry delivery"],
            }
        )
        return receipt
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

    artifact = output.read_bytes()
    receipt["artifact"] = {
        "path": str(output.resolve()),
        "sha256": sha256(artifact),
        "bytes": len(artifact),
    }
    return receipt


def print_receipt(receipt: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return
    label = "OK" if receipt["status"] == "pass" else "FAIL"
    print(f"{label} {receipt.get('output', receipt['candidate']['path'])}")
    for item in receipt["diagnostics"]:
        print(f"  - [{item['code']}] {item['subject']}: {item['message']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and atomically deliver diagram HTML.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("candidate", type=Path)
    validate_parser.add_argument("--json", action="store_true", dest="as_json")

    deliver_parser = subparsers.add_parser("deliver")
    deliver_parser.add_argument("candidate", type=Path)
    deliver_parser.add_argument("output", type=Path)
    deliver_parser.add_argument("--json", action="store_true", dest="as_json")

    args = parser.parse_args()
    receipt = (
        validation_receipt(args.candidate)
        if args.command == "validate"
        else deliver(args.candidate, args.output)
    )
    print_receipt(receipt, args.as_json)
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
