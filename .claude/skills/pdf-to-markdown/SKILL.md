---
name: pdf-to-markdown
description: >
  Convert a PDF into structured Markdown for accurate summarization/analysis.
  Uses PyMuPDF (installed from PyPI, no model download needed) to extract
  text and tables per page, then flags any page that looks scanned,
  image-heavy, or formula-dense so Claude can review that page's rendered
  image directly with vision. Use this whenever asked to read, summarize, or
  analyze a PDF that has tables, formulas, multi-column layout, or scanned
  pages.
---

# PDF to Markdown

A lightweight, fully self-contained PDF → Markdown converter. Everything —
script, venv, docs — lives in this skill's own folder; nothing here is
imported by or shared with any other part of the repo.

## Steps

1. **Install once per environment** (skip if `.venv/` in this folder already works):
   ```bash
   bash .claude/skills/pdf-to-markdown/setup.sh
   ```

2. **Run the extractor** on the target PDF:
   ```bash
   source .claude/skills/pdf-to-markdown/.venv/bin/activate
   python .claude/skills/pdf-to-markdown/convert.py <input.pdf> <output_dir>
   ```
   This writes `<output_dir>/<name>.md`, `<output_dir>/<name>.manifest.json`,
   and (only for flagged pages) rendered PNGs under `<output_dir>/pages/`.

3. **Read the manifest JSON.** For every page where `needs_vision_review` is
   `true`, use the Read tool on that page's `image` path (PyMuPDF already
   rendered it as a PNG) and transcribe/describe what you see — text,
   formulas, tables, charts — directly from the image.

4. **Merge**: replace each `<!-- NEEDS_VISION_REVIEW: ... -->` marker in the
   `.md` file with what you read from the corresponding page image. The
   result is the final structured Markdown — read this instead of the raw
   PDF for summarization/analysis.

## Why this split (library first, vision only where needed)

- PyMuPDF text/table extraction is fast, free (no tokens), and accurate for
  normal digital-text pages — no need to burn vision tokens on those.
- Claude's vision review is reserved for pages that are actually hard
  (scanned images, dense formulas, sparse text next to embedded images).

## Limitations

- Table detection (`page.find_tables()`) can be weak on very
  complex/borderless tables — spot-check flagged pages.
- Formula-to-LaTeX is not automatic; when reviewing a flagged page, describe
  formulas as LaTeX yourself if the task needs it.
