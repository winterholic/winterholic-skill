---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Cross-Browser Testing (Chrome vs Safari)

Frontends often render or behave differently between Chrome (Blink) and Safari (WebKit) — layout shifts, flexbox/grid quirks, date inputs, JS API gaps. **When the task is "does this work in both Chrome and Safari" or any cross-browser concern, run the SAME script against both engines and diff the results** (screenshots + console errors + DOM assertions). Don't test one engine and assume the other matches.

Playwright bundles the **WebKit** engine — the same engine Safari uses — so cross-browser layout/JS differences are reproducible without a real Safari install. For the Chrome side, prefer `channel="chrome"` to drive the **real installed Google Chrome** rather than bundled Chromium (closer to what users run); it falls back to Chromium-via-bundle only if you omit the channel.

```python
from playwright.sync_api import sync_playwright

# Same flow, both engines. chromium uses real Chrome via channel="chrome".
ENGINES = [
    ("chrome",  lambda p: p.chromium.launch(headless=True, channel="chrome")),
    ("webkit",  lambda p: p.webkit.launch(headless=True)),  # Safari's engine
]

with sync_playwright() as p:
    for name, launch in ENGINES:
        browser = launch(p)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto("http://localhost:5173")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=f"/tmp/cross-{name}.png", full_page=True)
        print(f"[{name}] console errors: {errors}")
        # ... add DOM/layout assertions here; compare per engine
        browser.close()
```

Then compare `/tmp/cross-chrome.png` vs `/tmp/cross-webkit.png` (Read the PNGs) and the console-error output side by side. Report concrete differences, not "looks fine".

**Limitation — bundled WebKit ≠ real Safari.** The WebKit bundle catches most rendering/JS differences, but NOT Safari-only behaviors: ITP cookie policy, IndexedDB quirks, PWA/push, `-webkit-` edge cases, and iOS Safari specifics. If a bug reproduces only in actual Safari, the bundle won't show it — that needs `safaridriver` (Apple's WebDriver: `safaridriver --enable` once; single session, no headless), which is outside Playwright. Flag this to the user when the symptom smells Safari-specific rather than generic WebKit.

If `channel="chrome"` errors with "Chromium distribution 'chrome' is not found", real Chrome isn't installed — drop the `channel` arg to use bundled Chromium, and tell the user the Chrome pass used Chromium instead.

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Use `--help` to see usage, then invoke directly. 
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation