#!/bin/bash
# ============================================================
# SCENARIO SNIPER LAUNCHER — Quality-First Single Setup Engine
# ============================================================
# Binds all strategy layers into ONE high-conviction decision:
#   1. Macro SPY Regime & Volatility Check (Bull / Chop / Bear)
#   2. Sector ETF Tailwind Check (Relative Strength)
#   3. SEC Fundamental Quality (GAAP Profitability & Balance Sheet)
#   4. Technical Pullback Sanity (RSI 35-65 sweet spot, rejects >68)
#   5. Tuned Exit Bracket: 2.0xATR Stop, 2.0xATR TP1 (scale 50%), 1.5xATR Trail
#   6. Inverse ETF Hedge (SH paired by beta x regime multiplier)
#
# Rule: "Find the potential one, enter before the day, then just wait."
#
# Usage:
#   ./scenario_sniper.sh                 # Full automation (scans, buys top pick, manages)
#   ./scenario_sniper.sh --dry-run       # Dry-run: evaluates and prints without live orders
#   ./scenario_sniper.sh --once          # Execute today's entry and exit immediately
#   CAPITAL=5000 ./scenario_sniper.sh    # Custom capital (e.g. $5,000)
#
# Stop:    kill $(cat logs/autopilot.pid)
# Review:  python -m execution.trade_journal --stats
# ============================================================
set -u
cd "$(dirname "$0")"

CAPITAL="${CAPITAL:-10000}"
FRACTIONAL="1"
MIN_SCORE=65
case "$CAPITAL" in
  1000) FRACTIONAL="1"; MIN_SCORE=70 ;;
  5000) FRACTIONAL="1"; MIN_SCORE=65 ;;
  10000) FRACTIONAL="1"; MIN_SCORE=65 ;;
esac

echo "==========================================================================="
echo "   🎯 RUNNING PRE-MARKET QUALITY SNIPER SCAN..."
echo "==========================================================================="

# 1. Run the Daily Sniper Scanner and show the complete trade card
.venv/bin/python backtest/daily_sniper.py --capital "${CAPITAL}"

# 2. Extract the winning ticker symbol from the saved setup state
SETUP_FILE="data/sniper_setup.json"
if [ -f "$SETUP_FILE" ]; then
    SNIPER_TICKER=$(.venv/bin/python -c 'import json; print(json.load(open("data/sniper_setup.json")).get("ticker", "NONE"))')
else
    SNIPER_TICKER="NONE"
fi

if [ -z "$SNIPER_TICKER" ] || [ "$SNIPER_TICKER" = "NONE" ]; then
    echo "==========================================================================="
    echo "  🛡️  DEFENSIVE CAPITAL PRESERVATION:"
    echo "  No Grade A candidate cleared all quality, macro & technical gates today."
    echo "  Remaining 100% in CASH. Patience is an edge — do not force trades."
    echo "==========================================================================="
    exit 0
fi

echo "🎯 Selected Sniper Candidate: $SNIPER_TICKER"
echo "Arming bracket automation: 2.0xATR Stop / 2.0xATR TP1 / 1.5xATR Trail / SH Hedge..."

# Tuned Exit Geometry
export STOP_ATR_MULT="${STOP_ATR_MULT:-2.0}"
export TP1_ATR_MULT="${TP1_ATR_MULT:-2.0}"
export TP2_TRIGGER_ATR_MULT="${TP2_TRIGGER_ATR_MULT:-3.5}"
export TRAIL_ARM_ATR_MULT="${TRAIL_ARM_ATR_MULT:-2.0}"
export TRAIL_ATR_MULT="${TRAIL_ATR_MULT:-1.5}"
export TP1_SCALE_OUT_PCT="${TP1_SCALE_OUT_PCT:-0.50}"
export TP1_AUTOMATION="${TP1_AUTOMATION:-1}"
export REQUIRE_SMA50_ABOVE_SMA200="${REQUIRE_SMA50_ABOVE_SMA200:-1}"
export TUNED_RSI_MAX="${TUNED_RSI_MAX:-65}"

# Focused single-trade risk controls (no multi-trade sprawl)
export RISK_PCT="${RISK_PCT:-0.02}"
export MAX_PORTFOLIO_HEAT="${MAX_PORTFOLIO_HEAT:-0.30}"
export MAX_POSITION_NOTIONAL_PCT="${MAX_POSITION_NOTIONAL_PCT:-0.30}"
export MIN_TRADE_SCORE="${MIN_TRADE_SCORE:-${MIN_SCORE}}"
export MIN_AUTO_SCORE="${MIN_AUTO_SCORE:-${MIN_SCORE}}"
export SMALL_ACCOUNT_FRACTIONAL=${FRACTIONAL}
export SMALL_ACCOUNT_CAPITAL=${CAPITAL}
export NEWS_MEMORY=1
export USE_LGBM_RUNTIME=0 OMP_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1

# Launch autopilot locked strictly onto the single Quality Sniper pick
exec ./run_autopilot.sh --watchlist "${SNIPER_TICKER}" "$@"
