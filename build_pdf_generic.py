"""
Generic Book PDF Builder — works for any book prefix in docs/
Usage: python build_pdf_generic.py <prefix> [--title "Book Title"]

Examples:
  python build_pdf_generic.py arb
  python build_pdf_generic.py statarb
  python build_pdf_generic.py vol --title "Volatility Mastery"
"""
import asyncio
import sys
import re
import argparse
from pathlib import Path
import pypdf
from playwright.async_api import async_playwright

DOCS_DIR   = Path("/home/user/Claude-code-project/docs")
OUTPUT_DIR = Path("/home/user/Claude-code-project/pdf")

BOOK_TITLES = {
    'arb':        'Arbitrage',
    'eye':        'ตาของ Arbitrageur',
    'math':       'คณิตศาสตร์สำหรับ Options',
    'pm':         'Payoff Mastery',
    'python':     'Python for Quant Traders',
    'statarb':    'Statistical Arbitrage',
    'vol':        'Volatility Mastery',
    'vp':         'View → Payoff',
    'grid':       'Grid Trading Mastery',
    'playground': 'The Playground',
}

PRINT_CSS = """
<style>
.fm {
    font-family: 'Sarabun', 'Courier New', monospace !important;
    font-size: 10px !important;
    line-height: 1.6 !important;
    white-space: pre-wrap !important;
    overflow-wrap: break-word !important;
    word-break: normal !important;
    background: #f3f4f6 !important;
    padding: 10px 12px !important;
    border-radius: 6px !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}
body {
    font-family: 'Sarabun', sans-serif !important;
    font-size: 15px !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}
canvas.chart, img.chart-img {
    display: block !important;
    max-width: 100% !important;
    height: auto !important;
    page-break-inside: avoid !important;
}
p.caption {
    font-size: 12px !important;
    color: #475569 !important;
    margin-top: 6px !important;
}
table { page-break-inside: avoid !important; }
.game { page-break-inside: avoid !important; }
.lens-card { page-break-inside: avoid !important; }
.regime-card { page-break-inside: avoid !important; }
.crs-print { page-break-inside: avoid !important; }
.key-idea { page-break-inside: avoid !important; }
nav[data-libnav] { display: none !important; }
</style>
"""

CANVAS_TO_IMG_JS = """
() => {
    document.querySelectorAll('canvas').forEach(canvas => {
        try {
            const dataUrl = canvas.toDataURL('image/png', 1.0);
            const img = document.createElement('img');
            img.src = dataUrl;
            img.className = 'chart-img';
            img.style.width  = canvas.offsetWidth  + 'px';
            img.style.height = canvas.offsetHeight + 'px';
            img.style.maxWidth = '100%';
            img.style.display = 'block';
            canvas.parentNode.replaceChild(img, canvas);
        } catch(e) {}
    });
}
"""

PDF_OPTIONS = dict(
    format="A4",
    margin={"top": "15mm", "bottom": "15mm", "left": "12mm", "right": "12mm"},
    print_background=True,
)


def part_sort_key(path: Path, prefix: str) -> tuple:
    """Sort HTML parts in natural reading order."""
    name = path.stem[len(prefix) + 1:]  # strip "prefix-"

    if name == 'index':
        return (-2, 0)

    # Known special pages that slot between main chapters and appendices
    SPECIAL = {'bridge': 897, 'drills': 898, 'study-guide': 896,
               'chart-study-guide': 895, 'for-options-guide': 894}
    if name in SPECIAL:
        return (SPECIAL[name], 0)

    if name.startswith('appendix'):
        sub = name[8:].lstrip('-')
        return (999, {'': 0, 'formulas': 1, 'glossary': 2}.get(sub, 3))

    # part3, part3a, part3b, ch0, ch24 …
    m = re.match(r'^(?:part|ch)(\d+)([a-z]?)$', name)
    if m:
        letter = m.group(2)
        return (int(m.group(1)), ord(letter) - ord('a') + 1 if letter else 0)

    return (500, 0)


def discover_parts(prefix: str) -> list[Path]:
    files = list(DOCS_DIR.glob(f"{prefix}-*.html"))
    files.sort(key=lambda p: part_sort_key(p, prefix))
    return files


async def render_part(browser, filename: str, output_path: Path) -> int:
    url  = f"file://{DOCS_DIR / filename}"
    page = await browser.new_page(
        viewport={"width": 1440, "height": 900},
        device_scale_factor=2,
    )
    try:
        await page.goto(url, wait_until="networkidle", timeout=30_000)
        await page.wait_for_timeout(3000)
        await page.add_style_tag(content=PRINT_CSS.strip())
        await page.evaluate(CANVAS_TO_IMG_JS)
        await page.wait_for_timeout(500)
        await page.pdf(path=str(output_path), **PDF_OPTIONS)
        reader = pypdf.PdfReader(str(output_path))
        return len(reader.pages)
    finally:
        await page.close()


async def build_pdf(prefix: str, title: str):
    OUTPUT_DIR.mkdir(exist_ok=True)

    parts = discover_parts(prefix)
    if not parts:
        print(f"ERROR: No HTML files found for prefix '{prefix}'", file=sys.stderr)
        sys.exit(1)

    print(f"{title} — PDF Builder")
    print("=" * 60)
    print(f"Discovered {len(parts)} parts:")
    for p in parts:
        print(f"  {p.name}")
    print()

    pdf_paths = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/opt/pw-browsers/chromium",
            args=["--no-sandbox", "--disable-setuid-sandbox",
                  "--font-render-hinting=medium"],
        )

        for i, part in enumerate(parts, 1):
            out = OUTPUT_DIR / part.name.replace(".html", ".pdf")
            print(f"[{i:2d}/{len(parts)}] {part.name}", end=" ... ", flush=True)
            try:
                pages = await render_part(browser, part.name, out)
                pdf_paths.append(out)
                print(f"{pages} pages ✓")
            except Exception as e:
                print(f"ERROR: {e}", file=sys.stderr)

        await browser.close()

    print("\nMerging into single book PDF ...")
    writer = pypdf.PdfWriter()
    total = 0
    for path in pdf_paths:
        reader = pypdf.PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
        total += len(reader.pages)

    combined = OUTPUT_DIR / f"{prefix}-BOOK.pdf"
    with open(combined, "wb") as f:
        writer.write(f)

    size_mb = combined.stat().st_size / 1_048_576
    print(f"\n✓ Done!")
    print(f"  Output : {combined}")
    print(f"  Pages  : {total}")
    print(f"  Size   : {size_mb:.1f} MB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build any book to PDF")
    parser.add_argument("prefix", help="Book prefix, e.g. arb, vol, statarb, math")
    parser.add_argument("--title", help="Override book title")
    args = parser.parse_args()

    title = args.title or BOOK_TITLES.get(args.prefix, args.prefix.upper())
    asyncio.run(build_pdf(args.prefix, title))
