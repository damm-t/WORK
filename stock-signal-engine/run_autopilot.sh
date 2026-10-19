#!/bin/bash
# ============================================================
# Overnight Autopilot Launcher (Alpaca PAPER trading)
# Keeps the bot alive in the background and prevents macOS
# from sleeping while it runs (caffeinate).
#
# Start:   ./run_autopilot.sh --interval 900 --watchlist NVDA,AAPL,TSLA
# Stop:    kill $(cat logs/autopilot.pid)
# Monitor: tail -f logs/autopilot_$(date +%Y%m%d).log
# ============================================================
set -u
cd "$(dirname "$0")"

export USE_LGBM_RUNTIME=0          # stable ensemble fallback (LGBM OpenMP hangs on macOS)
export OMP_NUM_THREADS=1
export TOKENIZERS_PARALLELISM=false
export HF_HUB_OFFLINE=1            # FinBERT model is fully cached locally
export TRANSFORMERS_OFFLINE=1
export PYTHONUNBUFFERED=1          # real-time log lines

LOG_DIR="logs"; mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/autopilot_$(date +%Y%m%d).log"

if [ -f "$LOG_DIR/autopilot.pid" ] && kill -0 "$(cat "$LOG_DIR/autopilot.pid")" 2>/dev/null; then
    echo "Autopilot already running (PID $(cat "$LOG_DIR/autopilot.pid")). Stop it first:"
    echo "  kill \$(cat $LOG_DIR/autopilot.pid)"
    exit 1
fi

if [ -f ".venv/Scripts/python.exe" ]; then
    PY=".venv/Scripts/python.exe"
elif [ -f ".venv/bin/python" ]; then
    PY=".venv/bin/python"
else
    PY="python3"
fi

# caffeinate -is: prevents idle/system sleep while the bot runs on macOS
if command -v caffeinate >/dev/null 2>&1; then
    nohup caffeinate -is "$PY" -m execution.autopilot "$@" >> "$LOG_FILE" 2>&1 &
else
    nohup "$PY" -m execution.autopilot "$@" >> "$LOG_FILE" 2>&1 &
fi
echo $! > "$LOG_DIR/autopilot.pid"
sleep 2

if kill -0 "$(cat "$LOG_DIR/autopilot.pid")" 2>/dev/null; then
    echo "✅ Autopilot running (PID $(cat "$LOG_DIR/autopilot.pid"))"
    echo "   Monitor : tail -f $LOG_FILE"
    echo "   Stop    : kill \$(cat $LOG_DIR/autopilot.pid)"
else
    echo "❌ Failed to start — check $LOG_FILE"
    exit 1
fi