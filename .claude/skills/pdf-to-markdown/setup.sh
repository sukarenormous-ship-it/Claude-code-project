#!/usr/bin/env bash
#
# Install the pdf-to-markdown skill's dependencies (PyMuPDF only — no ML
# model download, works even when huggingface.co/modelscope.cn are blocked).
#
# Usage:
#   bash .claude/skills/pdf-to-markdown/setup.sh
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$HERE/.venv"

if command -v uv >/dev/null 2>&1; then
  uv venv "$VENV" --python 3.11
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
  uv pip install pymupdf
else
  python3 -m venv "$VENV"
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
  pip install --upgrade pip
  pip install pymupdf
fi

echo ">> Installed. Activate with: source .claude/skills/pdf-to-markdown/.venv/bin/activate"
