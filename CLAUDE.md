# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project layout

This repo has three unrelated parts — keep them separate, never mix files
between them, and never let one import/reference another:

- **Root / `js/` / `css/` / `docs/`** — a static options-trading education site
  (payoff builder, greeks, arbitrage/PM lessons). `docs/` holds the lesson
  PDFs/HTML themselves; these are content, not tooling.
- **`.claude/skills/pdf-to-markdown/`** — a self-contained Claude Code skill
  that converts PDFs to structured Markdown. Everything it needs — script,
  venv, docs — lives inside this one folder (standard skill layout: one
  skill = one self-contained folder).
- **`.claude/skills/the-trading-dev-kit/`** — a self-contained Claude Code
  skill that scaffolds a personal, rule-based trading system (unrelated to
  the education site's content). Vendored verbatim from
  [nutdnuy/the-trading-dev-kit](https://github.com/nutdnuy/the-trading-dev-kit)
  (MIT). See `.claude/skills/the-trading-dev-kit/README.md`.

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

## the-trading-dev-kit usage rules

1. **Location**: everything lives under `.claude/skills/the-trading-dev-kit/`
   — `SKILL.md` (router) + `references/layer1-memory.md` through
   `layer5-plugins.md` (templates, scripts, worked examples). Don't rewrite
   these from scratch; read the matching reference file in full before
   responding, per `SKILL.md`'s own routing table.

2. **What it produces lives outside this folder**: using the skill generates
   real project files — a trading `CLAUDE.md`/`Risk.md`, `.claude/agents/*`
   subagent definitions, `.claude/hooks/*` scripts, and trade logs. These are
   this user's personal trading system, unrelated to the options-education
   site — do not let them reference or get referenced by `js/`/`css/`/`docs/`.

3. **Never commit private trading data**: `Risk.local.md`, `logs/`,
   `trades.log`, `*.log` (already in `.gitignore`) — these can contain real
   account/financial data.
