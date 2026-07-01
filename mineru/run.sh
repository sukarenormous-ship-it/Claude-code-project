#!/usr/bin/env bash
#
# Convenience wrapper to run MinerU on a document.
#
# Usage:
#   bash mineru/run.sh <input.pdf|dir> [output_dir]
#
# Examples:
#   bash mineru/run.sh mydoc.pdf
#   bash mineru/run.sh mydoc.pdf mineru/output
#
# Notes:
#   * On a CPU-only machine, use the "pipeline" backend (this script's default).
#   * The first run downloads model weights (a few GB) into the HF/ModelScope cache.
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$HERE/.venv"

if [ ! -d "$VENV" ]; then
  echo "MinerU is not installed yet. Run:  bash mineru/setup.sh" >&2
  exit 1
fi

INPUT="${1:?Usage: bash mineru/run.sh <input.pdf|dir> [output_dir]}"
OUTPUT="${2:-$HERE/output}"

# shellcheck disable=SC1091
source "$VENV/bin/activate"

mkdir -p "$OUTPUT"
# -b pipeline works without a GPU. Drop it to use the default hybrid engine on GPU boxes.
mineru -p "$INPUT" -o "$OUTPUT" -b pipeline
echo ">> Output written to: $OUTPUT"
