#!/usr/bin/env sh
PORT=${PORT:-8080} python3 server.py &
PID=$!
sleep 2
URL="http://127.0.0.1:${PORT}/present.html"
if command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then open "$URL" || true
else echo "$URL"
fi
wait "$PID"
