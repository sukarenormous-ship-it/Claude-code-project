---
name: pdf-to-markdown
description: >
  Convert a PDF into structured Markdown without needing MinerU's blocked
  model downloads. Uses PyMuPDF (installed from PyPI, no huggingface.co /
  modelscope.cn access needed) to extract text and tables per page, then
  flags any page that looks scanned, image-heavy, or formula-dense so Claude
  can review that page's rendered image directly with vision. Use this when
  asked to read/summarize/analyze a PDF and MinerU (mineru/run.sh) is
  unavailable or fails due to network policy blocking model downloads.
---

# PDF to Markdown (network-independent fallback for MinerU)

This repo's `mineru/` install requires downloading model weights from
`huggingface.co` / `modelscope.cn` / `hf-mirror.com`. In environments where
the network policy blocks those hosts, `mineru/run.sh` fails. This skill is
the fallback: it gets most of MinerU's practical benefit (structured
Markdown, tables, and vision-quality reading of hard pages) using only
PyPI-installable dependencies.

## Steps

1. **Install once per environment** (skip if `.claude/skills/pdf-to-markdown/.venv/` already works):
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
   result is the final structured Markdown — use it for summarization
   instead of the raw PDF, same as MinerU's output would be used.

## Why this split (library first, vision only where needed)

- PyMuPDF text/table extraction is fast, free (no tokens), and accurate for
  normal digital-text pages — no need to burn vision tokens on those.
- Claude's vision review is reserved for pages that are actually hard
  (scanned images, dense formulas, sparse text next to embedded images) —
  the same class of page MinerU's OCR/layout models would normally handle.
- Net effect: similar output quality to MinerU for the pages that matter,
  without needing the blocked model downloads.

## Limitations vs. MinerU

- Table detection (`page.find_tables()`) is weaker than MinerU's dedicated
  table-recognition model on very complex/borderless tables — spot-check
  flagged pages.
- Formula-to-LaTeX is not automatic; when reviewing a flagged page, describe
  formulas as LaTeX yourself if the task needs it.
- If network access to huggingface.co/modelscope.cn/hf-mirror.com is ever
  unblocked in this environment, prefer `mineru/run.sh` again — it is more
  thorough end-to-end.
