#!/usr/bin/env python3
"""
Fix Thai sara-a/sara-am ToUnicode CMap bug in WeasyPrint-generated PDFs.

Root cause: Sarabun-Bold and Sarabun-SemiBold embed glyph <01e8> mapped to
U+0E33 (sara-am ำ) but it should be U+0E32 (sara-a า), matching Sarabun-Regular.

Fix: scan every font's ToUnicode stream; for any Sarabun font where glyph <01e8>
maps to 0E33, swap it to 0E32.
"""
import re
import sys
import pikepdf
from pathlib import Path


SARA_A  = b'0e32'   # correct: U+0E32 า
SARA_AM = b'0e33'   # wrong:   U+0E33 ำ

# Pattern: <GLYPH_HEX> <0e33> — capture glyph hex
CMAP_SARA_AM_RE = re.compile(
    rb'(<[0-9a-fA-F]+>)\s*(<0[Ee]33>)',
)

def is_affected_font(font_obj) -> bool:
    """Return True if this font may have the sara-a/sara-am CMap bug.
    Sarabun-Bold and Sarabun-SemiBold always have it.
    FreeSerif has it in some embedded subsets (where glyph 0ABF → 0E33 wrongly).
    """
    base = str(font_obj.get('/BaseFont', ''))
    return 'Sarabun' in base or 'sarabun' in base or 'FreeSerif' in base

def fix_cmap(cmap_bytes: bytes, font_name: str) -> tuple[bytes, int]:
    """Replace sara-am entries with sara-a in a ToUnicode CMap stream.

    Strategy:
    - Sarabun: glyph <01e8> maps to 0E33 wrongly → fix to 0E32
    - FreeSerif: only fix when the font has NO glyph mapped to 0E32 (meaning
      the 0E33 glyph is actually filling in for missing sara-a, not real sara-am)
    """
    # Check if this font already has a CORRECT sara-a mapping
    has_sara_a = bool(re.search(rb'<[0-9a-fA-F]+>\s*<0[Ee]32>', cmap_bytes))

    # For FreeSerif: skip if sara-a is already correctly mapped (don't disturb
    # legitimate sara-am mappings in instances where sara-a exists separately)
    if 'FreeSerif' in font_name and has_sara_a:
        return cmap_bytes, 0

    # Find all glyph→unicode pairs in this CMap
    pairs = CMAP_SARA_AM_RE.findall(cmap_bytes)
    if not pairs:
        return cmap_bytes, 0

    count = 0
    result = cmap_bytes
    for glyph_hex, _ in pairs:
        # Replace <GLYPH> <0e33> → <GLYPH> <0e32>
        # Case-insensitive replacement
        old = glyph_hex + b' <0e33>'
        new = glyph_hex + b' <0e32>'
        old_ci = glyph_hex + b' <0E33>'
        new_ci = glyph_hex + b' <0E32>'

        before = len(result)
        result = result.replace(old, new).replace(old_ci, new_ci)
        if len(result) == before:
            # Try with varied spacing
            old2 = re.sub(rb'\s+', b' ', old)
            result = re.sub(
                glyph_hex + rb'\s+<0[Ee]33>',
                glyph_hex + b' <0e32>',
                result
            )
        count += 1

    if count:
        print(f'    Fixed {count} sara-am→sara-a mapping(s) in {font_name}')
    return result, count

def fix_pdf(input_path: Path, output_path: Path) -> int:
    pdf = pikepdf.open(input_path)
    total_fixes = 0
    seen_objgens = set()

    for page_num, page in enumerate(pdf.pages):
        if '/Resources' not in page:
            continue
        res = page['/Resources']
        if '/Font' not in res:
            continue

        for fname, font_ref in res['/Font'].items():
            try:
                font_obj = (font_ref if isinstance(font_ref, pikepdf.Dictionary)
                            else pdf.get_object(font_ref.objgen))
            except Exception:
                continue

            objgen = getattr(font_ref, 'objgen', None)
            if objgen and objgen in seen_objgens:
                continue
            if objgen:
                seen_objgens.add(objgen)

            if not is_affected_font(font_obj):
                continue
            if '/ToUnicode' not in font_obj:
                continue

            font_name = str(font_obj.get('/BaseFont', fname))
            cmap_stream = font_obj['/ToUnicode']

            # Check if this font has the sara-am bug
            original = cmap_stream.read_bytes()
            if not CMAP_SARA_AM_RE.search(original):
                continue

            fixed, n = fix_cmap(original, font_name)
            if n == 0:
                continue

            # Write fixed CMap back
            font_obj['/ToUnicode'] = pikepdf.Stream(pdf, fixed)
            total_fixes += n

    if total_fixes:
        pdf.save(output_path)
        print(f'  Saved → {output_path.name} ({total_fixes} fix(es))')
    else:
        import shutil
        shutil.copy2(input_path, output_path)
        print(f'  No fixes needed → copied {output_path.name}')

    return total_fixes


if __name__ == '__main__':
    BASE = Path('/home/user/Claude-code-project/pdf')
    FIXED = BASE / 'fixed'
    FIXED.mkdir(exist_ok=True)

    targets = sorted(BASE.glob('python-part*.pdf')) + [BASE / 'python-for-quant-traders-complete.pdf']

    grand_total = 0
    for src in targets:
        print(f'\n[{src.name}]')
        dst = FIXED / src.name
        n = fix_pdf(src, dst)
        grand_total += n

    print(f'\nTotal fixes: {grand_total}')

    # Verify: re-check sara-a vs sara-am ratio on fixed complete PDF
    print('\nVerifying fix on complete PDF...')
    from pypdf import PdfReader
    fixed_pdf = PdfReader(str(FIXED / 'python-for-quant-traders-complete.pdf'))
    bad_pages = 0
    for i, page in enumerate(fixed_pdf.pages):
        text = page.extract_text() or ''
        sara_a_count  = text.count('า')
        sara_am_count = text.count('ำ')
        if sara_am_count > 0 and sara_a_count > 0:
            ratio = sara_am_count / sara_a_count
            if ratio > 0.3:
                bad_pages += 1
    print(f'Pages with sara-am ratio >0.3: {bad_pages}/289 (was 50/289)')
