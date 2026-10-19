"""
Beta Hedging Engine
===================
Pairs every high-conviction Long signal with a dynamically sized market hedge,
tracks net dollar / net-beta exposure across the book, and manages asymmetric
exit levels (hard stop -> TP1 scale-out -> trailing runner).

Mathematical formulations (see implementation_plan.md):
    Hedge Dollars = Long Dollars x Asset Beta x Regime Multiplier
    Hard Stop     = Entry - 1.5 x ATR
    TP1 (sell 50%)= Entry + 2.0 x ATR
    TP2 Trigger   = Entry + 3.5 x ATR  -> arms a 1.5 x ATR trailing stop
"""

import logging
import math
import os
from typing import Any, Dict, List, Optional

from market.beta_calculator import (
    BENCHMARK_SPY,
    calculate_asset_beta,
    detect_market_regime,
)
from market.price_fetcher import fetch_prices
from .cost_model import days_to_target, expected_move_pct

logger = logging.getLogger(__name__)

# Symbols strictly excluded from candidate pools:
# User constraint: Exclude NVDA, MSFT, TSLA, crazy hot mega-cap bubble stocks, and SPCX/SPX index chasing.
# Edge must come from systematic risk management & non-bubble compounders.
HOT_STOCKS_BAN = frozenset({
    "NVDA", "MSFT", "TSLA", "AAPL", "AMZN", "META", "GOOGL", "GOOG", "SPCX", "SPX"
})
NVDA_BAN = frozenset({"NVDA"})

# Tuned small-account strategy preset (crisis-tested, 2026-09-19):
# 49.11% OOS win rate · +16.15% return · +0.247 expectancy.
TUNED_EXIT_GEOMETRY = {
    "STOP_ATR_MULT": 1.5,
    "TP1_ATR_MULT": 2.0,
    "TP2_TRIGGER_ATR_MULT": 3.0,
    "TRAIL_ATR_MULT": 2.5,
    "TP1_SCALE_OUT_PCT": 0.50,
}
TUNED_ENTRY_RULES = {
    "rsi_min": 35.0,
    "rsi_max": 65.0,
    "require_sma50_above_sma200": True,
    "breakeven_after_tp1": True,
    "hedge_enabled": True,
}
SMALL_ACCOUNT_PRESETS = {
    1_000.0: {"min_score": 70, "fractional": True,
              "note": "worst case — whole shares collapse WR to ~20%; "
                      "fractional keeps 49% OOS"},
    5_000.0: {"min_score": 65, "fractional": True, "note": "base case"},
    10_000.0: {"min_score": 65, "fractional": True, "note": "comfortable case"},
}


def banned_ticker(ticker: str, include_all_hot: bool = False) -> bool:
    """True when a symbol is excluded from candidate pools."""
    sym = str(ticker or "").strip().upper()
    if include_all_hot:
        return sym in HOT_STOCKS_BAN
    return sym in NVDA_BAN


def is_hot_banned(ticker: str) -> bool:
    """True when a symbol is excluded under the strict no-hot-stocks constraint."""
    return str(ticker or "").strip().upper() in HOT_STOCKS_BAN


def without_banned(tickers) -> list:
    """Drop banned symbols while preserving order."""
    return [t for t in (tickers or []) if not banned_ticker(t)]


# --- Tradable hedge proxies: benchmark -> inverse ETF we simply BUY (no borrow needed) ---
HEDGE_INSTRUMENTS: Dict[str, str] = {
    BENCHMARK_SPY.upper(): "SH",   # ProShares Short S&P500  (~ -1x SPY)
    "QQQ": "PSQ",                  # ProShares Short QQQ     (~ -1x QQQ)
}

# Definitionally-known betas so we never waste API calls recomputing them
BETA_OVERRIDES: Dict[str, float] = {
    "SPY": 1.0,
    "QQQ": 1.0,
    "SH": -1.0,
    "PSQ": -1.0,
}

STOP_ATR_MULT = 1.5            # hard stop distance below entry
TP1_ATR_MULT = 2.0             # first profit target -> scale out 50%
TP2_TRIGGER_ATR_MULT = 3.5     # runner activation level
TRAIL_ATR_MULT = 1.5           # trailing-stop distance once runner is armed
TP1_SCALE_OUT_PCT = 0.50       # fraction of shares sold at TP1


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def get_exit_geometry() -> dict:
    """Exit geometry with tuned-profile environment overrides."""
    stop_mult = _env_float("STOP_ATR_MULT", STOP_ATR_MULT)
    tp1_mult = _env_float("TP1_ATR_MULT", TP1_ATR_MULT)
    trail_mult = _env_float("TRAIL_ATR_MULT", TRAIL_ATR_MULT)
    tp2_mult = _env_float("TP2_TRIGGER_ATR_MULT", TP2_TRIGGER_ATR_MULT)
    # Trail arming threshold: the tuned profile arms the trail right after
    # TP1 (2.0 ATR); legacy behaviour only arms at the TP2 trigger (3.5 ATR).
    trail_arm_mult = _env_float("TRAIL_ARM_ATR_MULT", tp2_mult)
    try:
        tp1_scale = float(os.getenv("TP1_SCALE_OUT_PCT", str(TP1_SCALE_OUT_PCT)))
    except (TypeError, ValueError):
        tp1_scale = TP1_SCALE_OUT_PCT
    return {
        "stop_mult": stop_mult,
        "tp1_mult": tp1_mult,
        "trail_mult": trail_mult,
        "tp2_mult": tp2_mult,
        "trail_arm_mult": trail_arm_mult,
        "tp1_scale": tp1_scale,
        "regime_applied": "STATIC_BASELINE",
    }


def get_adaptive_exit_geometry(
    psi: Optional[float] = None,
    regime: Optional[str] = None,
) -> dict:
    """
    Regime & PSI-adaptive exit geometry (Upgrade 1 + Quant Reel 1 & 2 AstraQuant).
    Enforces minimum 2.0:1 R:R floor across all market regimes.
    Eliminates the negative asymmetry trap where stops were 2.5 ATR vs 1.5 ATR TP.
    """
    base = get_exit_geometry()
    if psi is None and regime is None:
        return base

    regime_upper = (regime or "").upper()
    psi_val = float(psi) if psi is not None else 50.0

    # LAMINAR_TREND: high stability, clean directional flow -> let winners run (R:R 2.5:1)
    if regime_upper in ("LAMINAR_TREND", "BULL", "BULL_EXPANSION") or psi_val >= 65.0:
        return {
            "stop_mult": 1.2,
            "tp1_mult": 3.0,
            "trail_mult": 1.5,
            "tp2_mult": 5.0,
            "trail_arm_mult": 2.5,
            "tp1_scale": 0.35,
            "regime_applied": "LAMINAR_TREND",
        }
    # ERRATIC_NOISE: high chop, low stability -> tight stop (1.0 ATR), 2.0 ATR target (2.0:1 R:R floor)
    # Never widen stops in noise; that creates negative asymmetry!
    elif regime_upper in ("ERRATIC_NOISE", "BEAR_VOLATILITY") or psi_val < 45.0:
        return {
            "stop_mult": 1.0,
            "tp1_mult": 2.0,
            "trail_mult": 1.0,
            "tp2_mult": 3.0,
            "trail_arm_mult": 1.5,
            "tp1_scale": 0.35,
            "regime_applied": "ERRATIC_NOISE",
        }
    # CALM_RANGING: standard mean reversion (R:R 2.0:1)
    else:
        return {
            "stop_mult": 1.2,
            "tp1_mult": 2.4,
            "trail_mult": 1.2,
            "tp2_mult": 4.0,
            "trail_arm_mult": 2.0,
            "tp1_scale": 0.35,
            "regime_applied": "CALM_RANGING",
        }


def tp1_scale_plan(
    price: float,
    entry_price: float,
    atr: float,
    shares: int,
    tp1_done: bool = False,
    psi: Optional[float] = None,
    regime: Optional[str] = None,
) -> dict:
    """
    TP1 scale-out decision for one position (tuned-profile automation).
    Supports optional adaptive geometry via PSI and regime.

    Returns {"action": "scale_out"|"hold", "sell_qty", "tp1_price"}.
    Whole-share floor keeps the runner >= 1 share so the trail still has
    something to manage (matches the backtester's integer scale-out).
    """
    if tp1_done or shares <= 0 or atr <= 0 or entry_price <= 0:
        return {"action": "hold", "sell_qty": 0, "tp1_price": None}
    geo = get_adaptive_exit_geometry(psi=psi, regime=regime)
    tp1_price = entry_price + geo["tp1_mult"] * atr
    if price < tp1_price:
        return {"action": "hold", "sell_qty": 0,
                "tp1_price": round(tp1_price, 2),
                "regime_applied": geo.get("regime_applied")}
    sell_qty = int(math.floor(shares * geo["tp1_scale"]))
    if sell_qty <= 0 or sell_qty >= shares:
        return {"action": "hold", "sell_qty": 0,
                "tp1_price": round(tp1_price, 2),
                "regime_applied": geo.get("regime_applied")}
    return {"action": "scale_out", "sell_qty": sell_qty,
            "tp1_price": round(tp1_price, 2),
            "regime_applied": geo.get("regime_applied")}


def calculate_dynamic_hedge_ratio(
    psi: Optional[float] = None,
    bayesian_confidence: Optional[float] = None,
    regime: Optional[str] = None,
) -> float:
    """
    Right-sizes hedge ratio based on market stability and model conviction (Upgrade 2).
    Prevents portfolio from becoming net-short in bullish/calm conditions.
    Enforces a strict ceiling of 0.65 to eliminate oversized hedge drag.
    """
    regime_upper = (regime or "CHOP_NEUTRAL").upper()
    if "BULL" in regime_upper or regime_upper == "LAMINAR_TREND":
        base = 0.15
    elif "BEAR" in regime_upper or regime_upper == "ERRATIC_NOISE":
        base = 0.60
    else:
        base = 0.35

    # Adjust for PSI (Price Stability Index)
    psi_adj = 0.0
    if psi is not None:
        psi_adj = (float(psi) - 50.0) / 200.0

    # Adjust for Bayesian Confidence
    conf_adj = 0.0
    if bayesian_confidence is not None:
        conf_adj = (float(bayesian_confidence) - 50.0) / 200.0

    ratio = base - psi_adj - conf_adj
    # Enforce safe bounds: minimum 10% tail hedge, maximum 65% hedge
    return round(max(0.10, min(0.65, ratio)), 3)


def resolve_hedge_instrument(benchmark_ticker: str = BENCHMARK_SPY) -> Optional[str]:
    """Returns the inverse-ETF proxy for a benchmark index (e.g. SPY -> SH)."""
    return HEDGE_INSTRUMENTS.get(str(benchmark_ticker).upper().strip())


def _latest_close(ticker: str, period: str = "5d") -> float:
    """Best-effort latest closing price for any ticker (returns 0.0 on failure)."""
    try:
        df = fetch_prices(ticker.upper(), period=period, interval="1d")
        if df.empty:
            return 0.0
        return round(float(df["Close"].iloc[-1]), 2)
    except Exception as e:
        logger.error(f"[hedging_engine] Could not price {ticker}: {e}")
        return 0.0


def calculate_hedge_pair(
    ticker: str,
    long_dollars: float,
    benchmark_ticker: str = BENCHMARK_SPY,
    psi: Optional[float] = None,
    bayesian_confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Computes the complete hedge leg for a planned Long position.
    Supports dynamic hedge sizing via PSI and Bayesian confidence (Upgrade 2).

    Returns asset beta, detected regime + multiplier, the hedge instrument,
    required hedge dollars/shares, and resulting net beta exposure.
    """
    ticker_clean = ticker.upper().strip()
    benchmark_clean = benchmark_ticker.upper().strip()

    if long_dollars <= 0:
        return {"status": "error", "message": "long_dollars must be positive"}

    hedge_symbol = resolve_hedge_instrument(benchmark_clean)
    if not hedge_symbol:
        return {
            "status": "error",
            "message": f"No hedge instrument mapped for benchmark {benchmark_clean}",
        }

    # 1. Asset beta vs the benchmark (Project Omega: use effective_beta if correlation_break)
    beta_info = calculate_asset_beta(ticker_clean, benchmark_clean)
    beta = float(beta_info.get("effective_beta") or beta_info.get("beta", 1.0) or 1.0)
    correlation_break = bool(beta_info.get("correlation_break", False))

    # 2. Market regime -> hedge aggressiveness multiplier
    regime_info = detect_market_regime(benchmark_clean)
    base_regime_mult = float(regime_info.get("hedge_multiplier", 0.50) or 0.50)

    if correlation_break:
        # PROJECT OMEGA: Crisis Correlation Break escalates hedge directly to max safety cap
        regime_multiplier = 0.65
        logger.warning(
            f"[hedging_engine] 🚨 CORRELATION BREAK detected for {ticker_clean}! "
            f"Escalating hedge multiplier to {regime_multiplier:.2f} using effective beta {beta:.2f}"
        )
    elif psi is not None or bayesian_confidence is not None:
        regime_multiplier = calculate_dynamic_hedge_ratio(
            psi=psi,
            bayesian_confidence=bayesian_confidence,
            regime=regime_info.get("regime", "CHOP_NEUTRAL"),
        )
    else:
        # Enforce maximum safety cap of 0.65 to prevent over-hedging (e.g. 1.25x net-short drag)
        regime_multiplier = min(0.65, base_regime_mult)

    # 3. Required hedge value: V_hedge = V_long x beta x regime_multiplier
    # Hard cap total hedge dollars to long_dollars * 0.65 to prevent inverted net-short books
    raw_hedge_dollars = long_dollars * abs(beta) * regime_multiplier
    hedge_dollars = min(long_dollars * 0.65, raw_hedge_dollars)
    hedge_price = _latest_close(hedge_symbol)

    hedge_shares = int(math.floor(hedge_dollars / hedge_price)) if hedge_price > 0 else 0

    # PROJECT OMEGA: Mandatory Hedge Integrity Gate (HIGH-1 Remediation)
    hedge_failed = False
    failure_reason = None
    if hedge_dollars > 0 and (hedge_price <= 0 or hedge_shares <= 0):
        hedge_failed = True
        failure_reason = (
            f"Mandatory hedge pricing/shares failed: required ${hedge_dollars:.2f} of {hedge_symbol}, "
            f"price={hedge_price}, shares={hedge_shares}. Trade entry cannot proceed unhedged."
        )
        logger.critical(f"[hedging_engine] 🚨 {failure_reason}")

    # Net beta exposure after pairing (>0 means still net-long the market)
    net_beta_exposure = (long_dollars * beta) - (hedge_shares * hedge_price * abs(beta))

    return {
        "status": "hedge_pricing_failed" if hedge_failed else "success",
        "ticker": ticker_clean,
        "benchmark": benchmark_clean,
        "asset_beta": round(beta, 3),
        "correlation": beta_info.get("correlation"),
        "correlation_break": correlation_break,
        "realized_beta_5d": beta_info.get("realized_beta_5d"),
        "regime": regime_info.get("regime", "CHOP_NEUTRAL"),
        "regime_multiplier": round(regime_multiplier, 2),
        "long_dollars": round(long_dollars, 2),
        "hedge_instrument": hedge_symbol,
        "hedge_price": hedge_price,
        "hedge_dollars": round(hedge_dollars, 2),
        "hedge_shares": hedge_shares,
        "hedge_ratio": round((hedge_dollars / long_dollars), 3) if long_dollars else 0.0,
        "hedge_failed": hedge_failed,
        "hedge_integrity": not hedge_failed,
        "net_beta_exposure": round(net_beta_exposure, 2),
        "reason": failure_reason or (
            f"{regime_info.get('regime', 'CHOP_NEUTRAL')} regime "
            f"(x{regime_multiplier:.2f}) x beta {beta:.2f} -> "
            f"${hedge_dollars:,.0f} of {hedge_symbol} vs ${long_dollars:,.0f} long"
        ),
    }


def calculate_exit_levels(
    entry_price: float,
    atr: float,
    psi: Optional[float] = None,
    regime: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Builds the full asymmetric exit ladder for a fresh Long position.
    Risk : Reward adapts to regime via PSI (1.5 ATR risk vs 2.0 / 3.0 / 4.5 ATR rewards).

    Also reports FEASIBILITY: how many trading days until each target is
    plausibly reached (random-walk sqrt-time scaling), and the statistically
    expected absolute move over the next 5 sessions.
    """
    if entry_price <= 0 or atr <= 0:
        return {}

    geo = get_adaptive_exit_geometry(psi=psi, regime=regime)
    levels = {
        "entry_price": round(entry_price, 2),
        "hard_stop_price": round(entry_price - (geo["stop_mult"] * atr), 2),
        "take_profit_1_price": round(entry_price + (geo["tp1_mult"] * atr), 2),
        "tp1_scale_out_pct": geo["tp1_scale"],
        "take_profit_2_trigger": round(entry_price + (geo["tp2_mult"] * atr), 2),
        "trailing_stop_distance": round(geo["trail_mult"] * atr, 2),
        "regime_applied": geo.get("regime_applied", "STATIC_BASELINE"),
    }

    # --- Target feasibility diagnostics ---
    levels["daily_atr_pct"] = round(atr / entry_price * 100.0, 2)
    levels["expected_move_5d_pct"] = round(expected_move_pct(atr, entry_price, days=5), 2)
    levels["tp1_days_median"] = days_to_target(
        entry_price, levels["take_profit_1_price"], atr)
    levels["tp2_days_median"] = days_to_target(
        entry_price, levels["take_profit_2_trigger"], atr)
    levels["tp2_feasible_5d"] = bool(
        levels["tp2_days_median"] is not None and levels["tp2_days_median"] <= 5.0)

    return levels


def ratchet_trailing_stop(
    entry_price: float,
    atr: float,
    highest_price_seen: float,
    current_stop_price: float = 0.0,
    psi: Optional[float] = None,
    regime: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Monotonic 'ratchet' stop management. The stop may only ever move UP.
    Adapts arm trigger and trailing distance based on PSI/regime.

    - Below the TP2 trigger: keep the hard stop at entry - stop_mult x ATR.
    - At/above the TP2 trigger: arm the trailing stop at highest - trail_mult x ATR,
      locked to never fall below the previous stop level.
    """
    if entry_price <= 0 or atr <= 0:
        return {"stop_price": current_stop_price, "trailing_armed": False, "action": "hold"}

    geo = get_adaptive_exit_geometry(psi=psi, regime=regime)
    hard_stop = entry_price - (geo["stop_mult"] * atr)
    arm_trigger = entry_price + (geo["trail_arm_mult"] * atr)
    tp2_trigger = entry_price + (geo["tp2_mult"] * atr)
    floor_stop = max(hard_stop, float(current_stop_price or 0.0))

    if highest_price_seen < arm_trigger:
        return {
            "stop_price": round(floor_stop, 2),
            "trailing_armed": False,
            "action": "hold",
            "progress_to_tp2": round(max(0.0, (highest_price_seen - entry_price) /
                                         max(tp2_trigger - entry_price, 1e-9)), 3),
            "regime_applied": geo.get("regime_applied"),
        }

    candidate_trail = highest_price_seen - (geo["trail_mult"] * atr)
    new_stop = max(floor_stop, candidate_trail)

    return {
        "stop_price": round(new_stop, 2),
        "trailing_armed": True,
        "action": "raise_stop" if new_stop > floor_stop else "hold",
        "progress_to_tp2": 1.0,
        "regime_applied": geo.get("regime_applied"),
    }


def compute_book_exposure(
    positions: List[Any],
    betas: Optional[Dict[str, float]] = None,
    benchmark_ticker: str = BENCHMARK_SPY,
) -> Dict[str, Any]:
    """
    Aggregates live positions into portfolio-level risk diagnostics.

    Accepts Alpaca Position objects OR plain dicts shaped like
    {"symbol": ..., "market_value": ...}. Betas come from BETA_OVERRIDES
    first, then an optional caller-supplied map, else default 1.0.
    """
    overrides = dict(BETA_OVERRIDES)
    if betas:
        overrides.update({str(k).upper(): float(v) for k, v in betas.items()})

    net_dollar_exposure = 0.0
    gross_exposure = 0.0
    net_beta_exposure = 0.0
    breakdown: List[Dict[str, Any]] = []

    for pos in positions or []:
        try:
            if isinstance(pos, dict):
                symbol = str(pos.get("symbol", "")).upper()
                market_value = float(pos.get("market_value", 0.0) or 0.0)
            else:
                symbol = str(getattr(pos, "symbol", "")).upper()
                market_value = float(getattr(pos, "market_value", 0.0) or 0.0)
        except Exception as e:
            logger.warning(f"[compute_book_exposure] Skipping malformed position: {e}")
            continue

        beta = overrides.get(symbol, 1.0)
        net_dollar_exposure += market_value
        gross_exposure += abs(market_value)
        net_beta_exposure += market_value * beta
        breakdown.append({
            "symbol": symbol,
            "market_value": round(market_value, 2),
            "assumed_beta": beta,
            "beta_weighted": round(market_value * beta, 2),
        })

    return {
        "positions": breakdown,
        "gross_exposure": round(gross_exposure, 2),
        "net_dollar_exposure": round(net_dollar_exposure, 2),
        "net_beta_exposure": round(net_beta_exposure, 2),
        "benchmark": benchmark_ticker,
    }