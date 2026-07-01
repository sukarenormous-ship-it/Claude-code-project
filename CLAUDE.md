# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project layout

This repo has three unrelated parts — keep them separate, never mix files
between them, and never let one import/reference another:

- **Root / `js/` / `css/` / `docs/`** — a static options-trading education site
  (payoff builder, greeks, arbitrage/PM lessons). `docs/` holds the lesson
  PDFs/HTML themselves; these are content, not tooling.
- **`mineru/`** — a self-contained MinerU install (PDF/DOCX/PPTX/XLSX/image →
  Markdown/JSON converter). Requires downloading model weights from
  `huggingface.co`/`modelscope.cn`/`hf-mirror.com`.
- **`pdf-to-markdown/`** — a self-contained, network-independent fallback for
  MinerU (PyMuPDF-based, PyPI-only). Its Claude Code skill definition lives at
  `.claude/skills/pdf-to-markdown/SKILL.md`, but the tool itself (script,
  venv) stays in this folder — `.claude/skills/` holds skill definitions only,
  never venvs or generated output.

## MinerU usage rules

1. **Location**: everything lives under `mineru/` — `setup.sh` (install),
   `run.sh` (convert), `.venv/` (git-ignored, ~5GB), `output/` (git-ignored).
   Never install Python packages elsewhere in the repo for this purpose.

2. **Install once per environment**:
   ```bash
   bash mineru/setup.sh
   ```
   Skip if `mineru/.venv/` already exists and `mineru/.venv/bin/mineru --version`
   succeeds.

3. **Convert, don't reinvent**: to process a PDF/DOCX/PPTX/XLSX, always call
   the existing wrapper rather than writing new parsing code:
   ```bash
   bash mineru/run.sh <input-file> mineru/output
   ```
   This environment has no GPU — always use the `pipeline` backend (already
   the default in `run.sh`). Do not switch to `hybrid-engine`/`vlm-engine`
   here; they require local GPU compute.

4. **When to convert before summarizing/analyzing a PDF**:
   - **Do convert first** if the document has tables, mathematical formulas,
     multi-column layout, scanned/image pages, or is long (this describes
     most files in `docs/`, e.g. the `math-part*`, `pm-part*`, `arb-part*`
     lesson PDFs). Read the resulting Markdown from `mineru/output/` instead
     of the raw PDF — it preserves reading order and turns tables/formulas
     into structured Markdown/LaTeX/HTML, which produces more accurate
     summaries.
   - **Skip conversion** for short, plain-text, single-column PDFs with no
     tables/formulas — reading the PDF directly is fine and faster.
   - When unsure, default to converting; it never costs LLM tokens (see below)
     and only costs local compute time.

5. **Cost model**: the MinerU conversion step runs entirely locally (OCR/layout
   models) — it never calls an LLM API and consumes no tokens. Only the
   subsequent summarization/analysis step (reading the output) consumes
   tokens, same as it would reading the raw PDF directly — usually fewer,
   since Claude bills PDF pages as image tokens while Markdown text is
   typically cheaper.

6. **First run per environment** downloads several GB of model weights into
   the model cache — this is expected and only happens once.

7. **Never commit**: `mineru/.venv/` or `mineru/output/` (already in
   `.gitignore`). Only commit changes to `mineru/setup.sh`, `mineru/run.sh`,
   and `mineru/README.md`.

8. **If `mineru/run.sh` fails with an empty/silent error and the network
   policy blocks `huggingface.co` / `modelscope.cn` / `hf-mirror.com`** (check
   `curl -sS http://127.0.0.1:37213/__agentproxy/status` for `403`/`connect_rejected`
   entries against those hosts): MinerU cannot download its models in this
   environment. Do not retry or try to route around the block. Instead, use
   the `pdf-to-markdown` skill (`.claude/skills/pdf-to-markdown/SKILL.md`,
   tool lives in `pdf-to-markdown/`) — it gets equivalent structured Markdown
   using only PyPI packages (no model download), falling back to Claude's own
   vision for pages it flags as scanned/image-heavy. Prefer `mineru/run.sh`
   again if that network restriction is ever lifted.

## pdf-to-markdown usage rules

Same self-contained-folder discipline as MinerU: everything lives under
`pdf-to-markdown/` — `setup.sh` (install), `convert.py` (the extractor),
`.venv/` (git-ignored), `README.md`. Never commit `pdf-to-markdown/.venv/` or
`pdf-to-markdown/output/`. Only commit `setup.sh`, `convert.py`, and
`README.md` under this folder, plus `SKILL.md` under
`.claude/skills/pdf-to-markdown/`.
