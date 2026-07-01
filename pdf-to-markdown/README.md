# pdf-to-markdown

A lightweight, network-independent PDF → Markdown converter. Built as a
fallback for the `mineru/` install (see repo root `CLAUDE.md`) for
environments where `huggingface.co` / `modelscope.cn` / `hf-mirror.com` are
blocked, so MinerU cannot download its models.

Self-contained like `mineru/` — nothing here is imported by or shared with
the JS site or the `mineru/` install. The Claude Code skill definition that
drives this tool lives separately at
`.claude/skills/pdf-to-markdown/SKILL.md`.

## Install

```bash
bash pdf-to-markdown/setup.sh
```

Creates `pdf-to-markdown/.venv/` (git-ignored) and installs `pymupdf` from
PyPI — no ML model download required.

## Use

```bash
source pdf-to-markdown/.venv/bin/activate
python pdf-to-markdown/convert.py <input.pdf> <output_dir>
```

Writes `<output_dir>/<name>.md`, `<output_dir>/<name>.manifest.json`, and
(only for pages flagged `needs_vision_review`) rendered PNGs under
`<output_dir>/pages/`. See the skill file for how Claude should merge in a
vision-based review of flagged pages.
