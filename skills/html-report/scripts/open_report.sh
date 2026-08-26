#!/usr/bin/env bash
# open_report.sh — macOS에서 작성한 HTML 보고서를 기본 브라우저로 연다.
#
# 사용:
#   ./open_report.sh                              # 가장 최근 보고서 열기
#   ./open_report.sh 2026-05-11-analysis-foo.html # 파일명 지정
#   ./open_report.sh /절대/경로/파일.html         # 절대 경로 지정

set -euo pipefail

REPORTS_DIR="${HTML_REPORT_DIR:-~/.claude\reports}"

if [[ $# -eq 0 ]]; then
  if [[ ! -d "$REPORTS_DIR" ]]; then
    echo "보고서 디렉토리가 없다: $REPORTS_DIR" >&2
    exit 1
  fi
  TARGET=$(ls -t "$REPORTS_DIR"/*.html 2>/dev/null | head -n 1 || true)
  if [[ -z "$TARGET" ]]; then
    echo "$REPORTS_DIR 안에 .html 파일이 없다." >&2
    exit 1
  fi
elif [[ "$1" = /* ]]; then
  TARGET="$1"
else
  TARGET="$REPORTS_DIR/$1"
fi

if [[ ! -f "$TARGET" ]]; then
  echo "파일을 찾을 수 없다: $TARGET" >&2
  exit 1
fi

echo "열기: $TARGET"
open "$TARGET"
