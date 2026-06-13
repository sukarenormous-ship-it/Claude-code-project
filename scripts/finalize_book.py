#!/usr/bin/env python3
"""
Finalize the book PDF: TOC + page numbers + bookmarks + Thai CMap fix.

Pipeline (run AFTER build_pdf.py):
  1. Parse part HTML files → part titles + chapter titles
  2. Scan part PDFs → page where each chapter starts
  3. Generate TOC PDF (WeasyPrint, iterate until TOC page count stabilizes)
  4. Merge: cover + TOC + all parts
  5. Stamp page numbers (skip cover + TOC; content starts at 1)
  6. Add PDF bookmarks (Part level + Chapter level)
  7. Apply Thai sara-a/sara-am CMap fix
"""
import re
import io
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

BASE = Path('/home/user/Claude-code-project')
DOCS = BASE / 'docs'
PDF  = BASE / 'pdf'
TMP  = PDF / 'tmp'
FONT_DIR = DOCS / 'vendor/fonts'

PART_LABELS = ['Part 0', 'Part I', 'Part II', 'Part III', 'Part IV', 'Part V', 'Part VI']


def strip_tags(s: str) -> str:
    s = re.sub(r'<[^>]+>', '', s)
    s = s.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return s.strip()


def parse_structure():
    """Return [(part_label, part_title, [chapter_titles])]."""
    structure = []
    for i in range(7):
        html = (DOCS / f'python-part{i}.html').read_text('utf8')
        cover = re.search(r'<div class="cover">.*?<h1>(.*?)</h1>', html, re.S)
        part_title = strip_tags(cover.group(1)) if cover else f'Part {i}'
        chapters = []
        for h in re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.S):
            t = strip_tags(h)
            if t.startswith('บทที่'):
                chapters.append(t)
        structure.append((PART_LABELS[i], part_title, chapters))
    return structure


def find_chapter_pages(part_pdf: Path, chapters: list) -> dict:
    """Map chapter title → 0-based page index within this part PDF."""
    reader = PdfReader(str(part_pdf))
    pages_text = [(p.extract_text() or '')[:80] for p in reader.pages]
    result = {}
    for ch in chapters:
        # Match "บทที่ N" at the start of a page (chapter h2 forces page break)
        m = re.match(r'(บทที่\s*\d+)', ch)
        if not m:
            continue
        needle = re.sub(r'\s+', '', m.group(1))
        for idx, txt in enumerate(pages_text):
            head = re.sub(r'\s+', '', txt)
            if head.startswith(needle):
                result[ch] = idx
                break
    return result, len(reader.pages)


def build_toc_html(entries: list) -> str:
    """entries: list of dicts {kind: part|chapter, label, title, page}"""
    rows = []
    for e in entries:
        if e['kind'] == 'part':
            rows.append(
                f'<div class="row part"><span class="lbl">{e["label"]}</span>'
                f'<span class="ttl">{e["title"]}</span>'
                f'<span class="dots"></span><span class="pg">{e["page"]}</span></div>'
            )
        else:
            rows.append(
                f'<div class="row ch"><span class="ttl">{e["title"]}</span>'
                f'<span class="dots"></span><span class="pg">{e["page"]}</span></div>'
            )
    body = '\n'.join(rows)
    return f"""<!DOCTYPE html>
<html lang="th"><head><meta charset="UTF-8">
<style>
@font-face {{ font-family:"Sarabun"; src:url("file://{FONT_DIR}/Sarabun-Regular.ttf"); font-weight:400; }}
@font-face {{ font-family:"Sarabun"; src:url("file://{FONT_DIR}/Sarabun-Bold.ttf"); font-weight:700; }}
@font-face {{ font-family:"Sarabun"; src:url("file://{FONT_DIR}/Sarabun-ExtraBold.ttf"); font-weight:800; }}
@page {{ size: A4; margin: 2.2cm 2.5cm; }}
body {{ font-family:"Sarabun",sans-serif; color:#1f2937; font-size:11pt; }}
h1 {{ font-size:22pt; font-weight:800; color:#111827; margin-bottom:4mm;
     padding-bottom:3mm; border-bottom:3px solid #0d9488; }}
.row {{ display:flex; align-items:baseline; }}
.row.part {{ margin-top:6mm; font-weight:700; font-size:11.5pt; color:#0d9488; }}
.row.ch {{ margin-left:10mm; margin-top:1.2mm; font-size:10.5pt; }}
.lbl {{ min-width:18mm; }}
.ttl {{ white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:118mm; }}
.dots {{ flex:1; border-bottom:1px dotted #9ca3af; margin:0 2mm 1mm; min-width:6mm; }}
.pg {{ font-weight:600; color:#374151; min-width:8mm; text-align:right; }}
</style></head><body>
<h1>สารบัญ</h1>
{body}
</body></html>"""


def render_toc(entries: list, out_pdf: Path) -> int:
    from weasyprint import HTML
    html_path = TMP / 'toc.html'
    html_path.write_text(build_toc_html(entries), 'utf8')
    HTML(filename=str(html_path)).write_pdf(str(out_pdf))
    return len(PdfReader(str(out_pdf)).pages)


def stamp_page_numbers(reader: PdfReader, skip_front: int) -> PdfWriter:
    """Stamp content page numbers (1-based after front matter) at footer center."""
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i >= skip_front:
            num = i - skip_front + 1
            buf = io.BytesIO()
            w = float(page.mediabox.width)
            h = float(page.mediabox.height)
            c = canvas.Canvas(buf, pagesize=(w, h))
            c.setFont('Helvetica', 9)
            c.setFillColorRGB(0.42, 0.45, 0.50)
            c.drawCentredString(w / 2, 24, str(num))
            c.save()
            buf.seek(0)
            overlay = PdfReader(buf).pages[0]
            page.merge_page(overlay)
        writer.add_page(page)
    return writer


def main():
    structure = parse_structure()

    # 1. Per-part chapter page maps + page counts
    part_info = []
    for i, (label, title, chapters) in enumerate(structure):
        pdf_path = PDF / f'python-part{i}.pdf'
        ch_pages, n_pages = find_chapter_pages(pdf_path, chapters)
        part_info.append({'label': label, 'title': title, 'chapters': chapters,
                          'ch_pages': ch_pages, 'n_pages': n_pages, 'pdf': pdf_path})
        missing = [c for c in chapters if c not in ch_pages]
        if missing:
            print(f'  WARN {label}: chapters not located: {[m[:30] for m in missing]}')

    # Appendix page count (rendered by build_pdf.py)
    appendix_pdf = PDF / 'python-appendix.pdf'
    appendix_pages = len(PdfReader(str(appendix_pdf)).pages) if appendix_pdf.exists() else 0
    print(f'Appendix: {appendix_pages} page(s)')

    # 2. Build TOC entries — iterate until TOC page count stabilizes
    # Front matter: cover(1) + howto(1) + toc(N) → content starts at page 1
    howto_pages = 1
    toc_pages = 2  # initial guess
    toc_pdf = TMP / 'toc.pdf'
    for _ in range(4):
        # Content numbering: first content page = 1 (after cover + howto + TOC)
        entries = []
        offset = 0  # content page offset
        for p in part_info:
            entries.append({'kind': 'part', 'label': p['label'],
                            'title': p['title'], 'page': offset + 1})
            for ch in p['chapters']:
                if ch in p['ch_pages']:
                    entries.append({'kind': 'chapter', 'label': '', 'title': ch,
                                    'page': offset + p['ch_pages'][ch] + 1})
            offset += p['n_pages']
        if appendix_pages:
            entries.append({'kind': 'part', 'label': 'ภาคผนวก',
                            'title': 'คำศัพท์ Quant Trading', 'page': offset + 1})
        new_toc_pages = render_toc(entries, toc_pdf)
        if new_toc_pages == toc_pages:
            break
        toc_pages = new_toc_pages
    print(f'TOC: {toc_pages} page(s)')

    # 3. Merge: cover + howto + TOC + parts + appendix (back cover appended later un-numbered)
    merged = PdfWriter()
    merged.append(str(PDF / 'cover.pdf'))
    howto_pdf = PDF / 'howto.pdf'
    if howto_pdf.exists():
        merged.append(str(howto_pdf))
    else:
        howto_pages = 0
    merged.append(str(toc_pdf))
    for p in part_info:
        merged.append(str(p['pdf']))
    if appendix_pages:
        merged.append(str(appendix_pdf))

    tmp_merged = TMP / 'merged_raw.pdf'
    with open(tmp_merged, 'wb') as f:
        merged.write(f)

    # 4. Stamp page numbers (skip cover + howto + TOC pages)
    skip_front = 1 + howto_pages + toc_pages
    reader = PdfReader(str(tmp_merged))
    writer = stamp_page_numbers(reader, skip_front)

    # 5. Bookmarks: cover/howto/TOC + part + chapter levels + appendix + back cover
    writer.add_outline_item('ปก', 0)
    writer.add_outline_item('วิธีใช้หนังสือ', 1)
    writer.add_outline_item('สารบัญ', 1 + howto_pages)
    abs_offset = skip_front
    for p in part_info:
        part_item = writer.add_outline_item(f"{p['label']} — {p['title']}", abs_offset)
        for ch in p['chapters']:
            if ch in p['ch_pages']:
                writer.add_outline_item(ch, abs_offset + p['ch_pages'][ch], parent=part_item)
        abs_offset += p['n_pages']
    if appendix_pages:
        writer.add_outline_item('ภาคผนวก — คำศัพท์ Quant Trading', abs_offset)
        abs_offset += appendix_pages

    # 6. Append back cover (no page number stamped)
    back_pdf = PDF / 'backcover.pdf'
    if back_pdf.exists():
        back_reader = PdfReader(str(back_pdf))
        for page in back_reader.pages:
            writer.add_page(page)
        writer.add_outline_item('ปกหลัง', abs_offset)

    out_path = PDF / 'python-for-quant-traders-complete.pdf'
    with open(out_path, 'wb') as f:
        writer.write(f)
    total_pages = len(reader.pages) + (len(back_reader.pages) if back_pdf.exists() else 0)
    print(f'Final book: {out_path.name} ({total_pages} pages, '
          f'{out_path.stat().st_size / 1024 / 1024:.1f} MB)')

    # 7. Thai CMap fix on final
    sys.path.insert(0, str(BASE / 'scripts'))
    from fix_thai_cmap import fix_pdf
    fixed_path = PDF / 'fixed' / out_path.name
    fixed_path.parent.mkdir(exist_ok=True)
    n = fix_pdf(out_path, fixed_path)
    # Replace final with fixed version
    import shutil
    shutil.copy2(fixed_path, out_path)
    print(f'Thai CMap fix applied ({n} fixes) — final saved.')


if __name__ == '__main__':
    main()
