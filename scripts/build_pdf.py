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
/* Override legacy @media print h2 rule — h2 should NOT force page break */
h2 {{ font-size: 1.4em; page-break-before: avoid !important; page-break-after: avoid; }}
h3 {{ font-size: 1.15em; page-break-after: avoid; }}

/* ---- Light code blocks for print ---- */
.fm {{
  background: #f8f9fa !important;
  color: #1a1a1a !important;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 12px 16px;
  /* Sarabun fallback ensures Thai comments use correct font (not FreeSerif) */
  font-family: 'Courier New', 'Sarabun', monospace !important;
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
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: "Sarabun", sans-serif;
  background: #fff;
  width: 210mm;
  height: 297mm;
  overflow: hidden;
}}

/* Top teal band */
.top-band {{
  background: #0d9488;
  height: 14mm;
  width: 100%;
}}

/* Main content area */
.main {{
  padding: 18mm 22mm 10mm;
  text-align: center;
}}

.series-label {{
  font-size: 10pt;
  font-weight: 700;
  color: #0d9488;
  letter-spacing: .15em;
  text-transform: uppercase;
  margin-bottom: 10mm;
}}

.title {{
  font-size: 42pt;
  font-weight: 800;
  color: #111827;
  line-height: 1.15;
  margin-bottom: 6mm;
}}

.title-th {{
  font-size: 28pt;
  font-weight: 700;
  color: #0d9488;
  margin-bottom: 8mm;
}}

.subtitle {{
  font-size: 12pt;
  color: #64748b;
  line-height: 1.7;
  margin-bottom: 10mm;
}}

/* Horizontal rule */
.rule {{
  width: 60mm;
  height: 3px;
  background: #0d9488;
  margin: 0 auto 10mm;
  border-radius: 2px;
}}

/* Parts table — 2 columns, clean */
.parts-table {{
  width: 130mm;
  margin: 0 auto 10mm;
  border-collapse: collapse;
}}
.parts-table td {{
  padding: 4px 10px;
  font-size: 10.5pt;
  text-align: left;
  color: #1f2937;
  border: none;
  background: none;
  line-height: 1.6;
}}
.parts-table td .num {{
  display: inline-block;
  width: 18mm;
  font-weight: 700;
  color: #0d9488;
}}
.parts-table td .name {{
  color: #374151;
}}

/* Stats row */
.stats {{
  display: table;
  margin: 0 auto 10mm;
  border-top: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
  padding: 6mm 0;
  width: 130mm;
  text-align: center;
}}
.stat-item {{
  display: table-cell;
  padding: 0 12mm;
  border-right: 1px solid #e5e7eb;
}}
.stat-item:last-child {{ border-right: none; }}
.stat-num {{
  font-size: 22pt;
  font-weight: 800;
  color: #0d9488;
  line-height: 1;
}}
.stat-label {{
  font-size: 8.5pt;
  color: #64748b;
  margin-top: 2px;
}}

.audience {{
  font-size: 10pt;
  color: #64748b;
  line-height: 1.7;
}}

/* Bottom teal band */
.bottom-band {{
  background: #0d9488;
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 10mm;
}}
</style>
</head>
<body>
<div class="top-band"></div>
<div class="main">
  <div class="series-label">Python for Quant Traders</div>

  <div class="title">Python</div>
  <div class="title-th">สำหรับ Quant Trader</div>

  <div class="subtitle">
    เรียน Python เพื่อวิเคราะห์ตลาดการเงิน<br>
    ตั้งแต่พื้นฐานจนถึงระบบเทรดสดจริง
  </div>

  <div class="rule"></div>

  <table class="parts-table">
    <tr>
      <td><span class="num">Part 0</span><span class="name">รากฐาน — คณิต · สถิติ · ตลาด</span></td>
      <td><span class="num">Part I</span><span class="name">Python Basics</span></td>
    </tr>
    <tr>
      <td><span class="num">Part II</span><span class="name">Math Tools — สถิติ · Optimization</span></td>
      <td><span class="num">Part III</span><span class="name">OOP &amp; Design Patterns</span></td>
    </tr>
    <tr>
      <td><span class="num">Part IV</span><span class="name">Backtesting</span></td>
      <td><span class="num">Part V</span><span class="name">AI-Assisted Coding</span></td>
    </tr>
    <tr>
      <td colspan="2" style="text-align:center">
        <span class="num">Part VI</span><span class="name">Async &amp; Live Trading</span>
      </td>
    </tr>
  </table>

  <div class="stats">
    <div class="stat-item">
      <div class="stat-num">35</div>
      <div class="stat-label">บท</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">7</div>
      <div class="stat-label">Parts</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">0</div>
      <div class="stat-label">พื้นฐาน CS ที่ต้องการ</div>
    </div>
  </div>

  <div class="audience">
    ออกแบบสำหรับทุกคน — หมอ ทนาย สถาปนิก นักธุรกิจ<br>
    ไม่ต้องมีพื้นฐาน Computer Science
  </div>
</div>
<div class="bottom-band"></div>
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
