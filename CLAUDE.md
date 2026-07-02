# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project layout

This repo has two unrelated parts — keep them separate, never mix files
between them, and never let one import/reference another:

- **Root / `js/` / `css/` / `docs/`** — a static options-trading education site
  (payoff builder, greeks, arbitrage/PM lessons). `docs/` holds the lesson
  PDFs/HTML themselves; these are content, not tooling.
- **`.claude/skills/pdf-to-markdown/`** — a self-contained Claude Code skill
  that converts PDFs to structured Markdown. Everything it needs — script,
  venv, docs — lives inside this one folder (standard skill layout: one
  skill = one self-contained folder).

## pdf-to-markdown usage rules

1. **Location**: everything lives under `.claude/skills/pdf-to-markdown/` —
   `SKILL.md` (skill definition), `setup.sh` (install), `convert.py` (the
   extractor), `.venv/` (git-ignored), `README.md`. Never install Python
   packages elsewhere in the repo for this purpose.

2. **Install once per environment**:
   ```bash
   bash .claude/skills/pdf-to-markdown/setup.sh
   ```
   Skip if `.claude/skills/pdf-to-markdown/.venv/` already exists and works.

3. **Convert, don't reinvent**: to process a PDF, always call the existing
   script rather than writing new parsing code:
   ```bash
   source .claude/skills/pdf-to-markdown/.venv/bin/activate
   python .claude/skills/pdf-to-markdown/convert.py <input.pdf> <output_dir>
   ```
   It extracts text/tables locally via PyMuPDF (no ML model download, no
   tokens) and flags pages that look scanned/image-heavy/formula-dense.

4. **When to convert before summarizing/analyzing a PDF**:
   - **Do convert first** if the document has tables, mathematical formulas,
     multi-column layout, scanned/image pages, or is long (this describes
     most files in `docs/`, e.g. the `math-part*`, `pm-part*`, `arb-part*`
     lesson PDFs). Read the resulting Markdown instead of the raw PDF — it
     preserves reading order and structure, which produces more accurate
     summaries.
   - For any page the manifest flags `needs_vision_review: true`, read that
     page's rendered PNG directly (Read tool) and merge what you see into
     the Markdown in place of the `NEEDS_VISION_REVIEW` marker — see
     `.claude/skills/pdf-to-markdown/SKILL.md` for the full procedure.
   - **Skip conversion** for short, plain-text, single-column PDFs with no
     tables/formulas — reading the PDF directly is fine and faster.
   - When unsure, default to converting; the extraction step never costs LLM
     tokens and only costs local compute time.

5. **Never commit**: `.claude/skills/pdf-to-markdown/.venv/` or `.../output/`
   (already in `.gitignore`). Only commit changes to `SKILL.md`, `setup.sh`,
   `convert.py`, and `README.md` under that folder.
