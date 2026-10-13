import os

from .hedging_engine import (
    NVDA_BAN,
    SMALL_ACCOUNT_PRESETS,
    TUNED_ENTRY_RULES,
    TUNED_EXIT_GEOMETRY,
    banned_ticker,
    calculate_exit_levels,
    calculate_hedge_pair,
    compute_book_exposure,
    get_exit_geometry,
    ratchet_trailing_stop,
    tp1_scale_plan,
    without_banned,
)

from .risk_manager import (
    calculate_position_size,
    check_portfolio_heat,
    calculate_regime_risk_pct,
    calculate_streak_compounding_factor,
)
from .book_allocator import (
    classify_position_book,
    get_book_allocations,
    get_split_ratios,
)
from .convex_tail import (
    ConvexTailEngine,
    convex_tail_engine,
)


def evaluate_trade(signal: dict, current_price: float,
                   portfolio_value: float, current_exposure: float,
                   atr: float = None,
                   psi: float = None,
                   regime: str = None,
                   bayesian_confidence: float = None) -> dict:
    try:
        if signal.get("action") != "BUY":
            return {"approved": False, "reason": "No signal"}

        confidence = float(signal.get("confidence", 0.0) or 0.0)
        risk_pct = float(os.getenv("RISK_PCT", "0.02"))
        position = calculate_position_size(
            portfolio_value, current_price,
            confidence,
            max_risk_pct=risk_pct,
            atr=atr,
            psi=psi,
            regime=regime,
            bayesian_confidence=bayesian_confidence,
        )
        if not position or position.get("shares", 0) <= 0:
            return {
                "approved": False,
                "reason": position.get("reason", "Position sizing failed (risk budget too small or gate rejected)")
            }

        # Per-position notional cap: aggressive risk budgets must not create
        # absurd single-position leverage (e.g. 10% risk on low ATR names).
        try:
            max_notional = portfolio_value * float(
                os.getenv("MAX_POSITION_NOTIONAL_PCT", "1.00"))
            pos_val = float(position.get("position_value", 0.0) or 0.0)
            if pos_val > max_notional > 0 and pos_val > 0:
                scale = max_notional / pos_val
                position["shares"] = int(float(position.get("shares", 0)) * scale)
                position["position_value"] = round(pos_val * scale, 2)
                position["notional_capped"] = True
        except Exception as cap_err:
            print(f"[evaluate_trade] notional cap skipped: {cap_err}")

        # Heat budget cap: scale position down to fit available heat instead of rejecting outright
        max_heat = float(os.getenv("MAX_PORTFOLIO_HEAT", "0.20"))
        try:
            available_heat = max(0.0, (max_heat * portfolio_value) - current_exposure)
            pos_val = float(position.get("position_value", 0.0) or 0.0)
            if pos_val > available_heat and available_heat >= current_price:
                scale = available_heat / pos_val
                position["shares"] = int(float(position.get("shares", 0)) * scale)
                position["position_value"] = round(float(position["shares"]) * current_price, 2)
                position["heat_capped"] = True
        except Exception as heat_cap_err:
            print(f"[evaluate_trade] heat cap skipped: {heat_cap_err}")

        heat = check_portfolio_heat(
            current_exposure,
            portfolio_value,
            float(position.get("position_value", 0.0) or 0.0),
            max_heat=max_heat
        )
        if not heat.get("approved", False):
            return {"approved": False, "reason": heat.get("reason", "Portfolio heat exceeded")}

        return {
            "approved":        True,
            "shares":          int(position.get("shares", 0) or 0),
            "position_value":  float(position.get("position_value", 0.0) or 0.0),
            "stop_loss_price": float(position.get("stop_loss_price", 0.0) or 0.0),
            "risk_pct_used":   position.get("risk_pct_used"),
            "streak_factor":   position.get("streak_factor"),
            "regime_applied":  position.get("regime_applied"),
            "reason":          signal.get("reason", "")
        }
    except Exception as e:
        print(f"[evaluate_trade] Error: {e}")
        return {"approved": False, "reason": "error"}
