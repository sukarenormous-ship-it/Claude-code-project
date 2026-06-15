# Review Book

Screenshot-review any book's HTML parts at A4-equivalent viewport to catch rendering issues before building the PDF.

**Usage:** `/review-book <prefix> [part-suffix]`

Examples:
- `/review-book playground` — review 3 sampled parts from The Playground
- `/review-book playground part1` — review playground-part1.html only
- `/review-book vol part3` — review vol-part3.html only

## Steps

The argument is: $ARGUMENTS

Parse: first word = prefix, second word (optional) = part suffix (e.g. `part1`, `ch3`, `appendix`).

### Setup (inline Python via Bash)

Use this Playwright snippet for every screenshot:
```python
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

DOCS_DIR = Path("/home/user/Claude-code-project/docs")
PRINT_CSS = """
<style>
.fm { font-family:'Sarabun','Courier New',monospace !important; font-size:10px !important;
      line-height:1.6 !important; white-space:pre-wrap !important;
      overflow-wrap:break-word !important; word-break:normal !important;
      background:#f3f4f6 !important; padding:10px 12px !important; border-radius:6px !important; }
body { font-family:'Sarabun',sans-serif !important; font-size:15px !important; }
nav[data-libnav] { display:none !important; }
</style>"""

async def snap(filename, out_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
                                          args=["--no-sandbox"])
        page = await browser.new_page(viewport={"width": 703, "height": 5000},
                                      device_scale_factor=2)
        await page.goto(f"file://{DOCS_DIR}/{filename}", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)
        await page.add_style_tag(content=PRINT_CSS.strip())
        await page.wait_for_timeout(500)
        await page.screenshot(path=out_path, full_page=True)
        await browser.close()
```

### If a specific part is given:
1. Screenshot `{prefix}-{part-suffix}.html` → `/tmp/review_{prefix}_{part}.png`
2. Read the screenshot image and check for:
   - **Formula wrap**: any `.fm` line that ends with `=` alone or `×` alone (formula split)
   - **Chart clipping**: chart labels cut off at left or right edge
   - **Text/chart overlap**: text rendered over a canvas/chart area
   - **Nav visible**: navigation bar showing in print view (should be hidden)
3. Report findings per issue type: ✓ OK or ✗ + description

### If no part specified (full book sample):
1. List all `{prefix}-*.html` files in docs/
2. Pick: first part, one middle part, last part (3 total)
3. Screenshot each
4. Run the 4 checks on each
5. Report a table: filename × check = ✓/✗

### Output format
```
Review: {prefix} — {datetime}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Part              Formula  Charts  Overlap  Nav
{prefix}-part1    ✓        ✓       ✓        ✓
{prefix}-part5    ✗ [desc] ✓       ✓        ✓
...
```

If issues found, describe the exact element and page location.
