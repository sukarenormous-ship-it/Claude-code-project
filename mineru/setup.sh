#!/usr/bin/env bash
#
# Reproducible installer for MinerU (https://github.com/opendatalab/MinerU)
# Everything is kept inside this `mineru/` folder so it stays fully separate
# from the JavaScript project in the repository root.
#
# Usage:
#   bash mineru/setup.sh
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$HERE/.venv"

echo ">> Installing MinerU into $VENV"

# uv is fast and reproducible; fall back to python -m venv + pip if uv is absent.
if command -v uv >/dev/null 2>&1; then
  uv venv "$VENV" --python 3.11
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
  uv pip install -U "mineru[core]"
else
  python3 -m venv "$VENV"
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
  pip install --upgrade pip
  pip install -U "mineru[core]"
fi

echo ">> Installed:"
mineru --version
echo ">> Done. Activate with:  source mineru/.venv/bin/activate"
