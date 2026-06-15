"""
The Playground — PDF Builder
Same approach as Grid Trading Mastery builder:
  - Canvas charts → PNG before print
  - Liberation Mono for code blocks
  - device_scale_factor=2 for crisp text
  - Viewport 1440px wide
"""
import asyncio
import sys
from pathlib import Path
import pypdf
from playwright.async_api import async_playwright

DOCS_DIR   = Path("/home/user/Claude-code-project/docs")
OUTPUT_DIR = Path("/home/user/Claude-code-project/pdf")

PARTS = [
    "playground-index.html",
    "playground-part0.html",
    "playground-part1.html",
    "playground-part2.html",
    "playground-part3.html",
    "playground-part4.html",
    "playground-part5.html",
    "playground-part6.html",
    "playground-part7.html",
    "playground-part8.html",
    "playground-part9.html",
    "playground-part10.html",
    "playground-appendix.html",
]

PDF_OPTIONS = dict(
    format="A4",
    margin={"top": "18mm", "bottom": "18mm", "left": "18mm", "right": "18mm"},
    print_background=True,
)

PRINT_CSS = """
<style>
.fm {
    font-family: 'Courier New', 'Sarabun', monospace !important;
    font-size: 11px !important;
    line-height: 1.65 !important;
    white-space: pre-wrap !important;
    overflow-wrap: break-word !important;
    word-break: normal !important;
    background: #f3f4f6 !important;
    padding: 12px 14px !important;
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
        } catch(e) { /* tainted canvas - skip */ }
    });
}
"""


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


async def build_pdf():
    OUTPUT_DIR.mkdir(exist_ok=True)
    pdf_paths = []

    print("The Playground — PDF Builder")
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

    print("\nMerging into single book PDF ...")
    writer = pypdf.PdfWriter()
    total  = 0
    for path in pdf_paths:
        reader = pypdf.PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
        total += len(reader.pages)

    combined = OUTPUT_DIR / "The-Playground.pdf"
    with open(combined, "wb") as f:
        writer.write(f)

    size_mb = combined.stat().st_size / 1_048_576
    print(f"\n✓ Done!")
    print(f"  Output : {combined}")
    print(f"  Pages  : {total}")
    print(f"  Size   : {size_mb:.1f} MB")


asyncio.run(build_pdf())
