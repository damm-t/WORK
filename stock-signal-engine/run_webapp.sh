#!/bin/bash
# Quant Desk Live Web App launcher (http://localhost:8081)
set -u
cd "$(dirname "$0")"

export USE_LGBM_RUNTIME=1 OMP_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1

PORT="${WEBAPP_PORT:-8080}"
echo "Starting Quant Desk Live on http://localhost:${PORT}"

exec .venv/bin/uvicorn webapp.app:app --host 0.0.0.0 --port "$PORT" --workers 1