"""
Grid Trading Mastery — PDF Builder v2
Fixes:
  - Canvas charts converted to PNG images before print (eliminates text-overlap)
  - Code boxes use Liberation Mono at 12px for readability
  - device_scale_factor=2 for crisp text (2× DPI)
  - Viewport 1440px wide so charts render with full room
"""
import asyncio
import sys
from pathlib import Path
import pypdf
from playwright.async_api import async_playwright

DOCS_DIR  = Path("/home/user/Claude-code-project/docs")
OUTPUT_DIR = Path("/home/user/Claude-code-project/pdf")

PARTS = [
    "grid-index.html",
    "grid-part0.html",
    "grid-part1a.html",
    "grid-part1b.html",
    "grid-part1c.html",
    "grid-part2.html",
    "grid-part3.html",
    "grid-part3b.html",
    "grid-part4.html",
    "grid-part5.html",
    "grid-part6.html",
    "grid-part6b.html",
    "grid-part7.html",
    "grid-part7b.html",
    "grid-part8.html",
    "grid-part9.html",
    "grid-appendix.html",
]

PDF_OPTIONS = dict(
    format="A4",
    margin={"top": "18mm", "bottom": "18mm", "left": "18mm", "right": "18mm"},
    print_background=True,
)

# Injected before PDF generation:
# 1. Better code-box font + size  2. Chart caption size  3. Canvas safety
PRINT_CSS = """
<style>
/* ── Code boxes ─────────────────────────────────────────────────── */
.fm {
    font-family: 'Liberation Mono', 'DejaVu Sans Mono', 'Courier New', monospace !important;
    font-size: 11.5px !important;
    line-height: 1.55 !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
    background: #f3f4f6 !important;
    padding: 12px 14px !important;
    border-radius: 6px !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}

/* ── Body text ──────────────────────────────────────────────────── */
body {
    font-size: 15px !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}

/* ── Canvas/chart containers: give them room ────────────────────── */
canvas.chart, img.chart-img {
    display: block !important;
    max-width: 100% !important;
    height: auto !important;
    page-break-inside: avoid !important;
}

/* ── Captions ───────────────────────────────────────────────────── */
p.caption {
    font-size: 12px !important;
    color: #475569 !important;
    margin-top: 6px !important;
}

/* ── Tables ─────────────────────────────────────────────────────── */
table { page-break-inside: avoid !important; }
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
        } catch(e) { /* tainted canvas - skip */ }
    });
}
"""


async def render_part(browser, filename: str, output_path: Path) -> int:
    url  = f"file://{DOCS_DIR / filename}"
    page = await browser.new_page(
        viewport={"width": 1440, "height": 900},
        device_scale_factor=2,          # 2× DPI — crisp text & canvas
    )
    try:
        await page.goto(url, wait_until="networkidle", timeout=30_000)

        # Let KaTeX + MiniChart finish
        await page.wait_for_timeout(3000)

        # Inject print-quality CSS
        await page.add_style_tag(content=PRINT_CSS.strip())

        # Convert canvas elements → PNG img tags (avoids PDF canvas quality issues)
        await page.evaluate(CANVAS_TO_IMG_JS)

        # Short settle after DOM change
        await page.wait_for_timeout(500)

        await page.pdf(path=str(output_path), **PDF_OPTIONS)
        reader = pypdf.PdfReader(str(output_path))
        return len(reader.pages)
    finally:
        await page.close()


async def build_pdf():
    OUTPUT_DIR.mkdir(exist_ok=True)
    pdf_paths = []

    print("Grid Trading Mastery — PDF Builder v2")
    print("=" * 50)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/opt/pw-browsers/chromium",
            args=["--no-sandbox", "--disable-setuid-sandbox",
                  "--font-render-hinting=medium"],
        )

        for i, filename in enumerate(PARTS, 1):
            out = OUTPUT_DIR / filename.replace(".html", ".pdf")
            print(f"[{i:2d}/{len(PARTS)}] {filename}", end=" ... ", flush=True)
            try:
                pages = await render_part(browser, filename, out)
                pdf_paths.append(out)
                print(f"{pages} pages ✓")
            except Exception as e:
                print(f"ERROR: {e}", file=sys.stderr)

        await browser.close()

    # ── Merge ──────────────────────────────────────────────────────────
    print("\nMerging into single book PDF ...")
    writer = pypdf.PdfWriter()
    total  = 0
    for path in pdf_paths:
        reader = pypdf.PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
        total += len(reader.pages)

    combined = OUTPUT_DIR / "Grid-Trading-Mastery.pdf"
    with open(combined, "wb") as f:
        writer.write(f)

    size_mb = combined.stat().st_size / 1_048_576
    print(f"\n✓ Done!")
    print(f"  Output : {combined}")
    print(f"  Pages  : {total}")
    print(f"  Size   : {size_mb:.1f} MB")


asyncio.run(build_pdf())
