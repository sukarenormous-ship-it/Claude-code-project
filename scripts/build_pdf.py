#!/usr/bin/env python3
"""
Build PDF for Python for Quant Traders book.
Pipeline: HTML → KaTeX pre-render (Node.js) → WeasyPrint → PDF → merge
"""
import subprocess, sys, os
from pathlib import Path

BASE  = Path('/home/user/Claude-code-project')
DOCS  = BASE / 'docs'
OUT   = BASE / 'pdf'
TMP   = BASE / 'pdf/tmp'
OUT.mkdir(exist_ok=True)
TMP.mkdir(exist_ok=True)

PARTS = [f'python-part{i}.html' for i in range(7)]

# Font path — absolute so WeasyPrint finds it regardless of working dir
FONT_DIR = DOCS / 'vendor/fonts'

PRINT_CSS = f"""
<style>
/* ---- Embed Sarabun font with absolute path ---- */
@font-face {{
  font-family: "Sarabun";
  src: url("file://{FONT_DIR}/Sarabun-Regular.ttf") format("truetype");
  font-weight: 400;
}}
@font-face {{
  font-family: "Sarabun";
  src: url("file://{FONT_DIR}/Sarabun-SemiBold.ttf") format("truetype");
  font-weight: 600;
}}
@font-face {{
  font-family: "Sarabun";
  src: url("file://{FONT_DIR}/Sarabun-Bold.ttf") format("truetype");
  font-weight: 700;
}}
@font-face {{
  font-family: "Sarabun";
  src: url("file://{FONT_DIR}/Sarabun-ExtraBold.ttf") format("truetype");
  font-weight: 800;
}}

/* ---- Page layout ---- */
@page {{ size: A4; margin: 2cm 2.5cm 2.2cm 2.5cm; }}
body {{
  font-family: "Sarabun", sans-serif !important;
  font-size: 11pt;
  line-height: 1.7;
  color: #1f2937;
  background: #fff;
  max-width: none !important;
  padding: 0 !important;
}}

/* ---- Cover page ---- */
.cover {{
  text-align: center;
  padding: 60px 30px 50px;
  border-bottom: 3px solid #0d9488;
  margin-bottom: 30px;
  page-break-after: always;
}}
.cover .ch-num {{ color: #0d9488; font-size: 1em; font-weight: 700; }}
.cover h1 {{ font-size: 2em; font-weight: 800; color: #111827; margin: 8px 0; }}
.cover .sub {{ color: #64748b; font-size: 1em; }}

/* ---- Headings ---- */
h1 {{ page-break-before: always; }}
.cover h1 {{ page-break-before: avoid; }}
h2 {{ font-size: 1.4em; page-break-after: avoid; }}
h3 {{ font-size: 1.15em; page-break-after: avoid; }}

/* ---- Light code blocks for print ---- */
.fm {{
  background: #f8f9fa !important;
  color: #1a1a1a !important;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 12px 16px;
  font-size: 8.5pt;
  line-height: 1.5;
  page-break-inside: avoid;
  white-space: pre-wrap;
  word-break: break-word;
}}
.fm .c  {{ color: #6c757d !important; }}
.fm .k  {{ color: #0055aa !important; font-weight: bold; }}
.fm .s  {{ color: #007700 !important; }}
.fm .n  {{ color: #aa0000 !important; }}

.output {{
  background: #f0f4f8 !important;
  color: #1a1a1a !important;
  border: 1px solid #c8d6e5;
  font-size: 8.5pt;
  page-break-inside: avoid;
}}
.output::before {{ color: #495057 !important; }}

/* ---- Boxes ---- */
.bx, .key-idea, .running-ex, .bx.bg, .bx.br, .bx.bb, .bx.ba, .bx.bi, .bx.bk, .bx.bd {{
  page-break-inside: avoid;
}}

/* ---- Tables ---- */
table {{ page-break-inside: avoid; font-size: 9pt; }}

/* ---- Exercises ---- */
details {{ page-break-inside: avoid; }}
details[open] {{ page-break-inside: auto; }}

/* ---- AI decode ---- */
.ai-decode {{ page-break-inside: avoid; font-size: 9.5pt; }}

/* ---- Hide nav ---- */
.nav, nav {{ display: none !important; }}

/* ---- No orphans/widows ---- */
p {{ orphans: 3; widows: 3; }}
</style>
"""

COVER_HTML = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<style>
@font-face {{
  font-family: "Sarabun";
  src: url("file://{font_dir}/Sarabun-Regular.ttf") format("truetype");
  font-weight: 400;
}}
@font-face {{
  font-family: "Sarabun";
  src: url("file://{font_dir}/Sarabun-Bold.ttf") format("truetype");
  font-weight: 700;
}}
@font-face {{
  font-family: "Sarabun";
  src: url("file://{font_dir}/Sarabun-ExtraBold.ttf") format("truetype");
  font-weight: 800;
}}
@page {{ size: A4; margin: 0; }}
body {{
  font-family: "Sarabun", sans-serif;
  margin: 0; padding: 0;
  background: #fff;
  height: 297mm;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}}
.accent {{ color: #0d9488; }}
.top-bar {{
  position: absolute; top: 0; left: 0; right: 0;
  height: 12mm;
  background: #0d9488;
}}
.bottom-bar {{
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 8mm;
  background: #0d9488;
}}
.content {{
  padding: 60px 80px;
}}
.series {{
  font-size: 13pt;
  color: #0d9488;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
  margin-bottom: 24px;
}}
h1 {{
  font-size: 38pt;
  font-weight: 800;
  color: #111827;
  line-height: 1.2;
  margin: 0 0 16px;
}}
.subtitle {{
  font-size: 15pt;
  color: #374151;
  margin-bottom: 40px;
  line-height: 1.6;
}}
.divider {{
  width: 80px;
  height: 4px;
  background: #0d9488;
  margin: 32px auto;
  border-radius: 2px;
}}
.parts {{
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
  margin: 24px 0;
}}
.part-tag {{
  background: #f0fdfa;
  border: 2px solid #0d9488;
  border-radius: 6px;
  padding: 6px 14px;
  font-size: 9pt;
  font-weight: 700;
  color: #0d9488;
}}
.audience {{
  font-size: 11pt;
  color: #64748b;
  margin-top: 32px;
  font-style: italic;
}}
.count {{
  font-size: 22pt;
  font-weight: 800;
  color: #0d9488;
  margin: 8px 0 4px;
}}
.count-label {{
  font-size: 11pt;
  color: #64748b;
}}
</style>
</head>
<body>
<div class="top-bar"></div>
<div class="content">
  <div class="series">Python for Quant Traders</div>
  <h1>Python<br><span class="accent">สำหรับ</span> Quant Trader</h1>
  <div class="subtitle">
    เรียน Python เพื่อวิเคราะห์ตลาดการเงิน<br>
    ตั้งแต่พื้นฐานจนถึงระบบเทรดจริง
  </div>
  <div class="divider"></div>
  <div class="parts">
    <span class="part-tag">Part 0 · รากฐาน</span>
    <span class="part-tag">Part I · Python Basics</span>
    <span class="part-tag">Part II · Math Tools</span>
    <span class="part-tag">Part III · OOP</span>
    <span class="part-tag">Part IV · Backtesting</span>
    <span class="part-tag">Part V · AI Coding</span>
    <span class="part-tag">Part VI · Live Trading</span>
  </div>
  <div class="count">35 บท</div>
  <div class="count-label">ครอบคลุม: คณิตศาสตร์ · สถิติ · OOP · Backtest · Async · WebSocket</div>
  <div class="audience">
    ออกแบบสำหรับทุกคน — หมอ ทนาย สถาปนิก นักธุรกิจ<br>
    ไม่ต้องมีพื้นฐาน Computer Science
  </div>
</div>
<div class="bottom-bar"></div>
</body>
</html>
""".format(font_dir=FONT_DIR)


def prerender(src: Path, dst: Path):
    """Pre-render KaTeX and inject print CSS."""
    result = subprocess.run(
        ['node', str(BASE / 'scripts/prerender_katex.js'), str(src), str(dst)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f'  KaTeX error: {result.stderr}', file=sys.stderr)
        return False
    # Inject print CSS (font + print overrides)
    html = dst.read_text('utf8')
    # Remove original vendor font link (we embed fonts via @font-face in PRINT_CSS)
    html = html.replace('<link href="vendor/fonts/sarabun.css" rel="stylesheet">', '')
    html = html.replace('<link href="../vendor/fonts/sarabun.css" rel="stylesheet">', '')
    html = html.replace('</head>', PRINT_CSS + '\n</head>')
    dst.write_text(html, 'utf8')
    return True


def to_pdf(src: Path, dst: Path):
    """Convert HTML to PDF with WeasyPrint."""
    from weasyprint import HTML
    HTML(filename=str(src)).write_pdf(str(dst))


def merge_pdfs(parts: list, output: Path):
    """Merge all part PDFs into one."""
    from pypdf import PdfWriter
    writer = PdfWriter()
    for p in parts:
        writer.append(str(p))
    with open(str(output), 'wb') as f:
        writer.write(f)
    size_mb = output.stat().st_size / 1024 / 1024
    print(f'Merged → {output.name} ({size_mb:.1f} MB)')


if __name__ == '__main__':
    pdf_parts = []

    # 1. Book cover page
    print('[Cover page]')
    cover_html = TMP / 'cover.html'
    cover_pdf  = OUT / 'cover.pdf'
    cover_html.write_text(COVER_HTML, 'utf8')
    try:
        to_pdf(cover_html, cover_pdf)
        pdf_parts.append(cover_pdf)
        print(f'  OK ({cover_pdf.stat().st_size // 1024} KB)')
    except Exception as e:
        print(f'  Cover error: {e}', file=sys.stderr)

    # 2. Each part
    for part_html in PARTS:
        src  = DOCS / part_html
        stem = part_html.replace('.html', '')
        pre  = TMP / f'{stem}_prerendered.html'
        pdf  = OUT / f'{stem}.pdf'

        print(f'\n[{stem}]')
        print(f'  Pre-rendering KaTeX...')
        if not prerender(src, pre):
            print(f'  SKIP (KaTeX failed)')
            continue

        print(f'  Converting to PDF...')
        try:
            to_pdf(pre, pdf)
            pdf_parts.append(pdf)
            size = pdf.stat().st_size // 1024
            print(f'  OK ({size} KB)')
        except Exception as e:
            print(f'  PDF error: {e}', file=sys.stderr)

    # 3. Merge
    if len(pdf_parts) > 1:
        print('\nMerging all parts...')
        merge_pdfs(pdf_parts, OUT / 'python-for-quant-traders-complete.pdf')

    print('\nDone!')
