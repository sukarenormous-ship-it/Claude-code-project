#!/usr/bin/env python3
"""
Fast local PDF -> Markdown extraction (text + tables) via PyMuPDF, plus
page-image rendering for any page that looks scanned/image-heavy/sparse so
Claude's vision can review it afterwards.

No ML model download required (unlike MinerU) — works fully offline once
PyMuPDF is installed from PyPI.
"""
import argparse
import json
import os

import fitz  # PyMuPDF

LOW_TEXT_CHARS_PER_PAGE = 40
SPARSE_TEXT_WITH_IMAGE_CHARS = 300


def page_needs_vision(page, text):
    text_len = len(text.strip())
    if text_len < LOW_TEXT_CHARS_PER_PAGE:
        return True, "very little extractable text (likely scanned image)"
    if page.get_images(full=True) and text_len < SPARSE_TEXT_WITH_IMAGE_CHARS:
        return True, "contains embedded image(s) with sparse surrounding text"
    return False, None


def extract_tables_markdown(page):
    tables_md = []
    try:
        finder = page.find_tables()
    except Exception:
        return tables_md
    for tbl in finder.tables:
        rows = tbl.extract()
        if not rows or not rows[0]:
            continue
        header = [str(c or "").replace("\n", " ").strip() for c in rows[0]]
        lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
        for row in rows[1:]:
            cells = [str(c or "").replace("\n", " ").strip() for c in row]
            lines.append("| " + " | ".join(cells) + " |")
        tables_md.append("\n".join(lines))
    return tables_md


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", help="Path to the input PDF")
    ap.add_argument("output_dir", help="Directory to write markdown/manifest/page-images into")
    ap.add_argument("--dpi", type=int, default=150, help="DPI for rendered page images (default 150)")
    args = ap.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    pages_dir = os.path.join(args.output_dir, "pages")

    doc = fitz.open(args.input)
    base_name = os.path.splitext(os.path.basename(args.input))[0]
    md_parts = []
    manifest = {"source": args.input, "pages": []}

    for i, page in enumerate(doc, start=1):
        text = page.get_text("text")
        needs_vision, reason = page_needs_vision(page, text)
        tables_md = extract_tables_markdown(page)

        image_rel_path = None
        if needs_vision:
            os.makedirs(pages_dir, exist_ok=True)
            pix = page.get_pixmap(dpi=args.dpi)
            image_path = os.path.join(pages_dir, f"page-{i}.png")
            pix.save(image_path)
            image_rel_path = os.path.relpath(image_path, args.output_dir)

        md_parts.append(f"\n\n<!-- PAGE {i} -->")
        if needs_vision:
            md_parts.append(f"<!-- NEEDS_VISION_REVIEW: {reason}. See {image_rel_path} -->")
        md_parts.append(text.strip())
        md_parts.extend("\n" + t for t in tables_md)

        manifest["pages"].append({
            "page": i,
            "char_count": len(text.strip()),
            "table_count": len(tables_md),
            "needs_vision_review": needs_vision,
            "reason": reason,
            "image": image_rel_path,
        })

    md_path = os.path.join(args.output_dir, f"{base_name}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_parts).strip() + "\n")

    manifest_path = os.path.join(args.output_dir, f"{base_name}.manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    flagged = [p["page"] for p in manifest["pages"] if p["needs_vision_review"]]
    print(f"Wrote {md_path}")
    print(f"Wrote {manifest_path}")
    print(f"Pages needing vision review: {flagged}" if flagged else "No pages flagged for vision review.")


if __name__ == "__main__":
    main()
