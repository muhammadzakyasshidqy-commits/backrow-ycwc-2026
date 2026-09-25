#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v tesseract >/dev/null 2>&1; then
  echo "Tesseract OCR is required. Install it with your OS package manager, then rerun." >&2
  exit 20
fi
if [ ! -d .venv ]; then python3 -m venv .venv; fi
source .venv/bin/activate
python -m pip install -r requirements.txt
BACKROW_HOST=127.0.0.1 PORT="${PORT:-8080}" python server.py
