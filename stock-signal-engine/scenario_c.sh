#!/bin/bash
# ============================================================
# SCENARIO C LAUNCHER — Hyper-bold configuration
#   • 10% risk per trade      (vs 2% default)
#   • Heat cap 90%            (multiple concurrent positions)
#   • Grade gate raised to 65 (aggression funded by selectivity)
#   • Auto-select top picks, news memory ON
#
# Start:  ./scenario_c.sh [--once] [--dry-run] [--watchlist ...]
# Stop:   kill \$(cat logs/autopilot.pid)
# Review: python -m execution.trade_journal --stats  (see below)
# ============================================================
set -u
cd "$(dirname "$0")"

export RISK_PCT=0.10
export MAX_PORTFOLIO_HEAT=0.90
export MAX_POSITION_NOTIONAL_PCT=0.30
export MIN_TRADE_SCORE=65
export MIN_AUTO_SCORE=65
export NEWS_MEMORY=1
export USE_LGBM_RUNTIME=0 OMP_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1

echo "=== SCENARIO C CONFIG ==="
echo "  risk/trade : ${RISK_PCT}   | heat cap: ${MAX_PORTFOLIO_HEAT}"
echo "  min score  : ${MIN_TRADE_SCORE} | auto-select min: ${MIN_AUTO_SCORE}"
exec ./run_autopilot.sh "$@"