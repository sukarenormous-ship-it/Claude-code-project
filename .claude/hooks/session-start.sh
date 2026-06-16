#!/bin/bash
set -euo pipefail

# Only run extra setup in remote Claude Code web sessions
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  # Still show the knowledge base summary locally
  bash "${CLAUDE_PROJECT_DIR:-/home/user/Claude-code-project}/.claude/session-start.sh" 2>/dev/null || true
  exit 0
fi

# ── Install Node.js dependencies ─────────────────────────────────────────────
cd "${CLAUDE_PROJECT_DIR:-/home/user/Claude-code-project}"

if [ ! -d "node_modules" ]; then
  echo "[session-start] Installing npm dependencies..."
  npm install --prefer-offline --no-audit --no-fund 2>&1 | tail -3
else
  echo "[session-start] npm deps already installed"
fi

# ── Verify Python PDF builder dependencies ───────────────────────────────────
python3 -c "
import sys
missing = []
for mod in ['pypdf', 'playwright']:
    try:
        __import__(mod)
    except ImportError:
        missing.append(mod)
if missing:
    print(f'[session-start] Installing Python deps: {missing}')
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet'] + missing)
else:
    print('[session-start] Python deps ok (pypdf, playwright)')
"

# ── Display knowledge base context ───────────────────────────────────────────
bash "${CLAUDE_PROJECT_DIR:-/home/user/Claude-code-project}/.claude/session-start.sh" 2>/dev/null || true
