#!/usr/bin/env python3
"""Render a URL with headless Chromium and dump text/html/screenshot.

Used by the web-browse skill to fetch JS-rendered (SPA) pages that the
built-in WebFetch tool returns empty for.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import Error as PWError
from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def _configure_windows_utf8() -> None:
    """Hermes가 서브프로세스 출력을 UTF-8로 안정적으로 읽게 한다."""
    if sys.platform != "win32":
        return
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Fetch a JS-rendered web page via headless Chromium."
    )
    p.add_argument("url")
    p.add_argument(
        "--format",
        choices=["text", "html", "title"],
        default="text",
        help="text: visible inner_text (default). html: full DOM. title: page title only.",
    )
    p.add_argument(
        "--selector",
        help="CSS selector to scope extraction (default: body). Used by text/html.",
    )
    p.add_argument(
        "--wait-for",
        help="CSS selector to wait for before extracting (in addition to networkidle).",
    )
    p.add_argument(
        "--wait-state",
        choices=["load", "domcontentloaded", "networkidle"],
        default="networkidle",
        help="Page load state to wait for (default: networkidle).",
    )
    p.add_argument("--timeout", type=int, default=30000, help="ms (default 30000)")
    p.add_argument("--screenshot", help="Path to save a full-page screenshot (PNG).")
    p.add_argument("--user-agent", default=DEFAULT_UA)
    p.add_argument(
        "--headful",
        action="store_true",
        help="Launch with a visible window (debugging).",
    )
    p.add_argument(
        "--channel",
        default="chrome",
        help=(
            "Browser channel to launch. Default 'chrome' uses the real "
            "installed Google Chrome (closest to what users actually run). "
            "Falls back to the bundled Chromium if Chrome isn't installed. "
            "Pass --channel chromium to force the bundle."
        ),
    )
    p.add_argument(
        "--max-chars",
        type=int,
        default=0,
        help="Truncate output to this many chars (0 = no truncate).",
    )
    return p.parse_args()


def run(args: argparse.Namespace) -> int:
    with sync_playwright() as pw:
        headless = not args.headful
        if args.channel == "chromium":
            browser = pw.chromium.launch(headless=headless)
        else:
            try:
                browser = pw.chromium.launch(
                    headless=headless, channel=args.channel
                )
            except PWError:
                # Real Chrome not installed → fall back to bundled Chromium.
                print(
                    f"[web-browse] channel '{args.channel}' unavailable; "
                    "falling back to bundled chromium",
                    file=sys.stderr,
                )
                browser = pw.chromium.launch(headless=headless)
        context = browser.new_context(user_agent=args.user_agent)
        page = context.new_page()
        try:
            page.goto(args.url, timeout=args.timeout, wait_until=args.wait_state)
        except PWTimeout:
            # networkidle often times out on long-polling sites; fall back to load
            print(
                f"[web-browse] {args.wait_state} timed out; continuing with current DOM",
                file=sys.stderr,
            )
        except PWError as e:
            print(f"[web-browse] navigation error: {e}", file=sys.stderr)
            browser.close()
            return 2

        if args.wait_for:
            try:
                page.wait_for_selector(args.wait_for, timeout=args.timeout)
            except PWTimeout:
                print(
                    f"[web-browse] selector {args.wait_for!r} not found in time; continuing",
                    file=sys.stderr,
                )

        if args.screenshot:
            Path(args.screenshot).parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=args.screenshot, full_page=True)
            print(f"[web-browse] screenshot saved: {args.screenshot}", file=sys.stderr)

        scope = args.selector or "body"
        out: str
        if args.format == "title":
            out = page.title()
        elif args.format == "html":
            if args.selector:
                handle = page.query_selector(scope)
                out = handle.inner_html() if handle else ""
            else:
                out = page.content()
        else:  # text
            handle = page.query_selector(scope)
            out = handle.inner_text() if handle else ""

        if args.max_chars and len(out) > args.max_chars:
            out = out[: args.max_chars] + f"\n\n[truncated at {args.max_chars} chars]"

        sys.stdout.write(out)
        if not out.endswith("\n"):
            sys.stdout.write("\n")

        browser.close()
        return 0


if __name__ == "__main__":
    _configure_windows_utf8()
    sys.exit(run(parse_args()))
