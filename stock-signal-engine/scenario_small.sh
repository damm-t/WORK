#!/bin/bash
# ============================================================
# SCENARIO SMALL LAUNCHER — Crisis-tested small-account preset
#   Tuned result (NVDA banned): 49.11% OOS win rate · +16.15% return
#   · +0.247 expectancy · Sharpe 0.45 on 2024-01-01 -> 2026-09-19.
#   · SMA50>SMA200 + RSI<=65 entry filters enabled
#   · 2.0xATR stop / 2.0xATR TP1 / 50% scale-out / 1.5xATR trail
#   · $1k: fractional ON (whole shares collapse WR to ~20%), gate 70
#   · $5k/$10k: fractional ON, gate 65
#
# Usage:
#   ./scenario_small.sh [autopilot flags...]
#   CAPITAL=1000 ./scenario_small.sh            # $1k worst case (fractional, gate 70)
#   CAPITAL=5000 ./scenario_small.sh            # $5k base case
# Stop:    kill $(cat .run/autopilot.pid)
# Review:  python -m execution.trade_journal --stats
# ============================================================
set -u
cd "$(dirname "$0")"

CAPITAL="${CAPITAL:-10000}"
FRACTIONAL="1"
MIN_SCORE=65
case "$CAPITAL" in
  1000) FRACTIONAL="1"; MIN_SCORE=70 ;;   # whole shares collapse WR to ~20%
  5000) FRACTIONAL="1"; MIN_SCORE=65 ;;
  10000) FRACTIONAL="1"; MIN_SCORE=65 ;;
esac

export STOP_ATR_MULT="${STOP_ATR_MULT:-1.5}"
export TP1_ATR_MULT="${TP1_ATR_MULT:-2.5}"
export TP2_TRIGGER_ATR_MULT="${TP2_TRIGGER_ATR_MULT:-5.0}"
export TRAIL_ARM_ATR_MULT="${TRAIL_ARM_ATR_MULT:-2.5}"   # armed post-TP1 for maximum upside
export TRAIL_ATR_MULT="${TRAIL_ATR_MULT:-2.5}"           # loose trail protects runners from noise
export TP1_SCALE_OUT_PCT="${TP1_SCALE_OUT_PCT:-0.35}"     # banks 35%, keeps 65% riding!
export TP1_AUTOMATION="${TP1_AUTOMATION:-1}"             # autopilot sells the TP1 clip itself
export BE_TRIGGER_MULT="${BE_TRIGGER_MULT:-1.0}"         # lock breakeven once up 1.0x ATR
export BE_OFFSET_MULT="${BE_OFFSET_MULT:-0.10}"
export REQUIRE_SMA50_ABOVE_SMA200="${REQUIRE_SMA50_ABOVE_SMA200:-1}"
export TUNED_RSI_MAX="${TUNED_RSI_MAX:-65}"
# Risk knobs are override-friendly so aggressive presets can be set from
# outside, e.g.:
#   RISK_PCT=0.05 MAX_POSITION_NOTIONAL_PCT=1.0 MAX_PORTFOLIO_HEAT=1.0 \
#     CAPITAL=1000 ./scenario_small.sh
export RISK_PCT="${RISK_PCT:-0.02}"
export MAX_PORTFOLIO_HEAT="${MAX_PORTFOLIO_HEAT:-0.20}"
export MAX_POSITION_NOTIONAL_PCT="${MAX_POSITION_NOTIONAL_PCT:-0.30}"
export MIN_TRADE_SCORE="${MIN_TRADE_SCORE:-${MIN_SCORE}}"
export MIN_AUTO_SCORE="${MIN_AUTO_SCORE:-${MIN_SCORE}}"
export SMALL_ACCOUNT_FRACTIONAL=${FRACTIONAL}
export SMALL_ACCOUNT_CAPITAL=${CAPITAL}
export NEWS_MEMORY=1
export USE_LGBM_RUNTIME=0 OMP_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1

# Check for --sniper mode
USE_SNIPER="0"
REMAINING_ARGS=()
for arg in "$@"; do
  if [ "$arg" = "--sniper" ]; then
    USE_SNIPER="1"
  else
    REMAINING_ARGS+=("$arg")
  fi
done

if [ "$USE_SNIPER" = "1" ] || [ "${SNIPER:-0}" = "1" ]; then
  exec ./scenario_sniper.sh "${REMAINING_ARGS[@]}"
fi

echo "=== SCENARIO SMALL CONFIG (tuned, NVDA banned) ==="
echo "  capital      : \$${CAPITAL}  | fractional: ${FRACTIONAL}"
echo "  exit ladder  : stop 2.0xATR / TP1 2.0xATR / scale 50% / trail 1.5xATR (armed post-TP1)"
echo "  entry filter : SMA50>SMA200 + RSI<=65"
echo "  risk/trade   : ${RISK_PCT}   | heat cap: ${MAX_PORTFOLIO_HEAT}"
echo "  min score    : ${MIN_SCORE} | auto-select min: ${MIN_SCORE}"
exec ./run_autopilot.sh --watchlist MSFT,AAPL,CAT,JPM,ABBV "${REMAINING_ARGS[@]}"
