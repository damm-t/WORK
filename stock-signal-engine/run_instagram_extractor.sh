#!/bin/bash
# Instagram Content Extractor & Quant Intelligence Web App Launcher
# Port default: 8095 (http://localhost:8095)
set -euo pipefail
cd "$(dirname "$0")"

PORT="${EXTRACTOR_PORT:-8095}"
echo "==================================================================="
echo "  Instagram Quant Extractor & Abstraction Engine"
echo "  Target Port: http://localhost:${PORT}"
echo "==================================================================="

# If already running on this port, terminate previous instance to avoid Address in use error
EXISTING_PID=$(lsof -t -i :"$PORT" 2>/dev/null || true)
if [ -n "$EXISTING_PID" ]; then
  echo "Stopping previous instance (PID: $EXISTING_PID)..."
  kill -9 $EXISTING_PID 2>/dev/null || true
  sleep 1
fi

echo "Starting server on http://localhost:${PORT}..."
exec .venv/bin/python -m uvicorn instagram_extractor.web_server:app --host 0.0.0.0 --port "$PORT"
