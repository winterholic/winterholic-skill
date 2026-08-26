"""api_lint.py - OpenAPI contract convention linter (stdlib only).

Detects (matching dev-rest-api-design SKILL.md antipattern catalog):
  [R1] verb-looking path segment (get/create/delete/update/list...)
  [R4] GET returning bare array (no pagination envelope)         (heuristic)
  [R4b] list-ish GET without limit parameter
  [R3] 4xx/5xx response without declared schema

Input: an OpenAPI 3.x JSON file (e.g. FastAPI's /openapi.json saved to disk).

Usage:
  python api_lint.py <openapi.json> [...]
  python api_lint.py              (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage/parse error.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import json
import sys

VERBS = {"get", "create", "delete", "update", "list", "fetch", "set", "add",
         "remove", "make", "do", "run", "exec", "process"}
LISTY = ("s", "list", "history", "items")


def lint_spec(spec: dict, label: str) -> list[str]:
    findings: list[str] = []
    paths = spec.get("paths", {})
    for path, ops in paths.items():
        segs = [s for s in path.strip("/").split("/") if s and not s.startswith("{")]
        for seg in segs:
            low = seg.lower()
            # match verb prefix in snake/kebab/camelCase: get_users, get-users, getUsers
            if any(low == v or low.startswith(v + "_") or low.startswith(v + "-") or
                   (low.startswith(v) and len(seg) > len(v) and seg[len(v)].isupper())
                   for v in VERBS):
                findings.append(f"{label}: {path}: [R1] verb '{seg}' in path - resource nouns + HTTP method")
        for method, op in ops.items():
            if not isinstance(op, dict):
                continue
            responses = op.get("responses", {})
            # R3: error responses without schema
            for code, resp in responses.items():
                if code.startswith(("4", "5")):
                    content = (resp or {}).get("content", {})
                    if not content:
                        findings.append(
                            f"{label}: {method.upper()} {path} {code}: [R3] error response without schema - "
                            "errors are contract too")
            if method.lower() == "get":
                ok = responses.get("200", {})
                schema = (ok.get("content", {}).get("application/json", {}) or {}).get("schema", {})
                if schema.get("type") == "array":
                    findings.append(
                        f"{label}: GET {path}: [R4] bare array response - "
                        "use envelope {data, next_cursor} for evolvability")
                # list-ish path without limit param
                last = path.strip("/").split("/")[-1]
                looks_list = not last.startswith("{") and (last.endswith(LISTY) or schema.get("type") == "array")
                if looks_list:
                    params = {p.get("name") for p in op.get("parameters", [])}
                    if "limit" not in params:
                        findings.append(
                            f"{label}: GET {path}: [R4b] list endpoint without 'limit' param - unbounded growth")
    return sorted(set(findings))


DEMO_SPEC = {
    "paths": {
        "/getUsers": {"get": {"responses": {"200": {"content": {"application/json": {"schema": {"type": "array"}}}}}}},
        "/v1/stocks/{code}/candles": {
            "get": {
                "parameters": [{"name": "limit"}, {"name": "cursor"}],
                "responses": {
                    "200": {"content": {"application/json": {"schema": {"type": "object"}}}},
                    "404": {"content": {"application/json": {"schema": {"$ref": "#/x"}}}},
                },
            }
        },
        "/orders": {"get": {"responses": {"200": {"content": {"application/json": {"schema": {"type": "array"}}}},
                                            "422": {}}}},
    }
}


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - linting built-in sample spec:")
        for ln in lint_spec(DEMO_SPEC, "<demo>"):
            print("  " + ln)
        print("Usage: python api_lint.py <openapi.json> ...")
        return 0

    total = 0
    for path in argv:
        try:
            with open(path, encoding="utf-8") as f:
                spec = json.load(f)
        except FileNotFoundError:
            print(f"{path}: not found - skipped")
            continue
        except json.JSONDecodeError as e:
            print(f"{path}: invalid JSON - {e}")
            return 2
        for ln in lint_spec(spec, path):
            print(ln)
            total += 1
    print(f"total: {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
