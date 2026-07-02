# pdf-to-markdown

A lightweight PDF → Markdown converter (PyMuPDF-based, PyPI-only, no ML
model download). The Claude Code skill definition is `SKILL.md` in this same
folder; this README just covers manual/standalone use.

## Install

```bash
bash .claude/skills/pdf-to-markdown/setup.sh
```

Creates `.venv/` (git-ignored) in this folder and installs `pymupdf`.

## Use

```bash
source .claude/skills/pdf-to-markdown/.venv/bin/activate
python .claude/skills/pdf-to-markdown/convert.py <input.pdf> <output_dir>
```

Writes `<output_dir>/<name>.md`, `<output_dir>/<name>.manifest.json`, and
(only for pages flagged `needs_vision_review`) rendered PNGs under
`<output_dir>/pages/`. See `SKILL.md` for how Claude should merge in a
vision-based review of flagged pages.
