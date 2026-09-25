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
export BACKROW_HOST=0.0.0.0
export PORT="${PORT:-8080}"
echo "Starting BACKROW field-validation LAN mode on port $PORT (trusted local network only)."
echo "Main product:        http://127.0.0.1:$PORT/"
echo "Validation console: http://127.0.0.1:$PORT/validate.html"
python - <<PY >/dev/null 2>&1 &
import time, webbrowser
time.sleep(1.2)
webbrowser.open('http://127.0.0.1:${PORT}/')
webbrowser.open('http://127.0.0.1:${PORT}/validate.html')
PY
python server.py
