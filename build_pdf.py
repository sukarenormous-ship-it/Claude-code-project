"""
Grid Trading Mastery — PDF Builder
Uses Playwright (headless Chromium) to render each HTML part with full
KaTeX math + canvas charts, then merges into one book PDF via pypdf.
"""
import asyncio
import sys
from pathlib import Path
import pypdf
from playwright.async_api import async_playwright

DOCS_DIR = Path("/home/user/Claude-code-project/docs")
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
    margin={"top": "18mm", "bottom": "18mm", "left": "16mm", "right": "16mm"},
    print_background=True,
)


async def render_part(browser, filename: str, output_path: Path) -> int:
    url = f"file://{DOCS_DIR / filename}"
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=30_000)
        # Let KaTeX + canvas charts finish rendering
        await page.wait_for_timeout(2500)
        # Extra wait if KaTeX is still working
        await page.evaluate("""() => new Promise(resolve => {
            if (window.katex || document.querySelector('.katex')) {
                setTimeout(resolve, 500);
            } else {
                resolve();
            }
        })""")
        await page.pdf(path=str(output_path), **PDF_OPTIONS)
        page_count = (await page.evaluate("document.body.scrollHeight")) // 1122 + 1
        return page_count
    finally:
        await page.close()


async def build_pdf():
    OUTPUT_DIR.mkdir(exist_ok=True)
    pdf_paths = []

    print("Grid Trading Mastery — PDF Builder")
    print("=" * 50)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/opt/pw-browsers/chromium",
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )

        for i, filename in enumerate(PARTS, 1):
            out = OUTPUT_DIR / filename.replace(".html", ".pdf")
            print(f"[{i:2d}/{len(PARTS)}] {filename}", end=" ... ", flush=True)
            try:
                await render_part(browser, filename, out)
                pdf_paths.append(out)
                reader = pypdf.PdfReader(str(out))
                print(f"{len(reader.pages)} pages ✓")
            except Exception as e:
                print(f"ERROR: {e}", file=sys.stderr)

        await browser.close()

    # Merge
    print("\nMerging into single book PDF ...")
    writer = pypdf.PdfWriter()
    total = 0
    for path in pdf_paths:
        reader = pypdf.PdfReader(str(path))
        for page in reader.pages:
            writer.add_page(page)
        total += len(reader.pages)

    combined = OUTPUT_DIR / "Grid-Trading-Mastery.pdf"
    with open(combined, "wb") as f:
        writer.write(f)

    size_mb = combined.stat().st_size / 1_048_576
    print(f"\nDone!")
    print(f"  Output : {combined}")
    print(f"  Pages  : {total}")
    print(f"  Size   : {size_mb:.1f} MB")


asyncio.run(build_pdf())
