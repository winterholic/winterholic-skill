"""alert_lint.py - alerting/metric smell detector (stdlib only, regex heuristic).

Detects (matching dev-monitoring SKILL.md antipattern catalog):
  [O1] alert expression on a cause metric (cpu/memory/disk usage) - prefer symptom alerts
  [O5] high-cardinality label (user_id/request_id/email/uuid/timestamp) in a metric
  [O4] alert on avg()/mean without a percentile - tail hidden

Scans Prometheus rule .yml/.yaml and metric-definition text.

Usage:
  python alert_lint.py <file_or_dir> [...]
  python alert_lint.py            (no args: self-demo)

Exit code: 0 = clean, 1 = findings, 2 = usage error.
Silence a line with '# alert-ok: <reason>'.
Output is ASCII-only (Windows cp949 console safe).
"""
from __future__ import annotations

import os
import re
import sys

CAUSE_METRIC = re.compile(r"(?i)(cpu|memory|mem_|disk|ram)_?(usage|percent|util|used)?\b")
HIGH_CARD = re.compile(r"(?i)\b(user_?id|request_?id|email|uuid|trace_?id|session_?id|timestamp)\b")
AVG_ALERT = re.compile(r"(?i)\b(avg|mean|average)\s*\(")
PERCENTILE = re.compile(r"(?i)(quantile|histogram_quantile|p50|p95|p99|percentile)")
EXPR_LINE = re.compile(r"(?i)^\s*(expr|alert)\s*:")


def scan_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    lines = text.splitlines()
    in_alert_block = "alert:" in text or "expr:" in text  # prometheus rule heuristic

    for i, line in enumerate(lines):
        ln = i + 1
        if "alert-ok:" in line:
            continue
        is_expr = bool(EXPR_LINE.search(line))
        # O1: cause metric inside an expr line
        if is_expr and CAUSE_METRIC.search(line) and not PERCENTILE.search(line):
            findings.append(f"{label}:{ln}: [O1] alert on a cause metric (cpu/mem/disk) - "
                            "alert on symptoms (SLO/error/latency); keep cause on dashboards")
        # O4: avg without percentile in an expr line
        if is_expr and AVG_ALERT.search(line) and not PERCENTILE.search(line):
            findings.append(f"{label}:{ln}: [O4] alert on avg/mean - the tail is hidden; use p95/p99")
        # O5: high-cardinality label anywhere in metric/label context
        if HIGH_CARD.search(line) and ("label" in line.lower() or "{" in line or is_expr):
            findings.append(f"{label}:{ln}: [O5] high-cardinality label - series explosion; "
                            "ids belong in logs/traces, not metric labels")
    return sorted(set(findings))


DEMO = """\
groups:
  - name: example
    rules:
      - alert: HighCPU
        expr: cpu_usage > 0.8
      - alert: SlowAvg
        expr: avg(http_request_duration_seconds) > 0.3
      - alert: PerUser
        expr: sum(requests_total{user_id="x"}) > 100
      - alert: GoodLatency
        expr: histogram_quantile(0.95, http_req) > 0.3
"""


def main(argv: list[str]) -> int:
    if not argv:
        print("demo mode (no files given) - scanning built-in sample:")
        for ln in scan_text(DEMO, "<rules.yml>"):
            print("  " + ln)
        print("Usage: python alert_lint.py <file_or_dir> ...")
        return 0

    total = 0
    paths: list[str] = []
    for p in argv:
        if os.path.isdir(p):
            for root, _dirs, fs in os.walk(p):
                paths.extend(os.path.join(root, f) for f in fs if f.endswith((".yml", ".yaml")))
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
