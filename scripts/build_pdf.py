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

PRINT_CSS = """
<style>
/* Print overrides */
@page { size: A4; margin: 2cm 2.5cm 2cm 2.5cm; }
body  { font-size: 11pt; line-height: 1.6; }

/* Light code blocks for print readability */
.fm   { background: #f8f9fa !important; color: #1a1a1a !important;
        border: 1px solid #dee2e6; border-radius: 6px;
        padding: 12px 16px; font-size: 9pt; line-height: 1.5; }
.fm .c  { color: #6c757d !important; }
.fm .k  { color: #0d6efd !important; }
.fm .s  { color: #198754 !important; }
.fm .n  { color: #dc3545 !important; }

.output { background: #f0f4f8 !important; color: #1a1a1a !important;
          border: 1px solid #c8d6e5; }
.output::before { color: #495057 !important; }

/* Keep colors for boxes */
.bx { page-break-inside: avoid; }
details { page-break-inside: avoid; }

/* Nav bar hidden in print */
nav, .nav, header { display: none !important; }

/* Page breaks before major sections */
h1 { page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
</style>
"""

def prerender(src: Path, dst: Path):
    """Pre-render KaTeX and inject print CSS."""
    result = subprocess.run(
        ['node', str(BASE / 'scripts/prerender_katex.js'), str(src), str(dst)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f'  KaTeX error: {result.stderr}', file=sys.stderr)
        return False
    # Inject print CSS
    html = dst.read_text('utf8')
    html = html.replace('</head>', PRINT_CSS + '\n</head>')
    dst.write_text(html, 'utf8')
    return True

def to_pdf(src: Path, dst: Path):
    """Convert HTML to PDF with WeasyPrint."""
    from weasyprint import HTML, CSS
    print(f'  WeasyPrint → {dst.name}')
    HTML(filename=str(src)).write_pdf(str(dst))

def merge_pdfs(parts: list, output: Path):
    """Merge all part PDFs into one."""
    from pypdf import PdfWriter
    writer = PdfWriter()
    for p in parts:
        writer.append(str(p))
    with open(str(output), 'wb') as f:
        writer.write(f)
    print(f'Merged → {output.name} ({output.stat().st_size // 1024} KB)')

if __name__ == '__main__':
    pdf_parts = []

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
            print(f'  OK ({pdf.stat().st_size // 1024} KB)')
        except Exception as e:
            print(f'  PDF error: {e}', file=sys.stderr)

    if len(pdf_parts) > 1:
        print('\nMerging all parts...')
        merge_pdfs(pdf_parts, OUT / 'python-for-quant-traders-complete.pdf')

    print('\nDone!')
