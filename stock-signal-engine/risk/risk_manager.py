from typing import Optional


def calculate_regime_risk_pct(
    psi: Optional[float] = None,
    bayesian_confidence: Optional[float] = None,
    regime: Optional[str] = None,
    base_risk_pct: float = 0.02,
) -> float:
    """
    Tiered Regime-Adaptive Position Sizing (Upgrade 4).
    Dynamically scales the portfolio risk percentage based on market stability and model conviction:

    | Conviction / PSI | Regime | Risk % |
    |---|---|---|
    | Confidence >= 70% & PSI >= 65 | LAMINAR_TREND / BULL | 3.0% (aggressive on pristine trends) |
    | Confidence 55-70% & PSI 45-65| CALM_RANGING / CHOP  | 2.0% (standard baseline) |
    | PSI < 45 or Confidence < 55% | ERRATIC_NOISE / BEAR | 1.0% (defensive capital preservation) |
    | PSI < 30 or Confidence < 45% | CHAOTIC / UNCERTAIN  | 0.0% (no entry) |
    """
    if psi is None and bayesian_confidence is None and regime is None:
        return base_risk_pct

    psi_val = float(psi) if psi is not None else 50.0
    conf_val = float(bayesian_confidence) if bayesian_confidence is not None else 60.0
    regime_upper = (regime or "").upper()

    # Reject high chaos / extreme noise setups or Macro Bear crashes
    if regime_upper in ("MACRO_BEAR", "BEAR", "PANIC", "DEATH_CROSS") or psi_val < 30.0 or conf_val < 45.0:
        return 0.0

    # Pristine laminar trend with high conviction
    if (regime_upper in ("LAMINAR_TREND", "BULL", "BULL_EXPANSION") or psi_val >= 65.0) and conf_val >= 70.0:
        return 0.030

    # Erratic noise or low conviction -> reduce exposure to 1.0%
    if regime_upper in ("ERRATIC_NOISE", "BEAR_VOLATILITY") or psi_val < 45.0 or conf_val < 55.0:
        return 0.010

    # Calm ranging / standard setup
    return 0.020


def calculate_streak_compounding_factor(journal_instance=None) -> float:
    """
    Winner reinvestment & streak compounding factor (Upgrade 5).
    - If in a losing streak (streak <= -2): reduce position size by 25% (defensive capital preservation).
    - If in a winning streak (streak >= 3): scale up size conservatively (up to 1.30x) ONLY IF
      average realized PnL in the journal is positive. If expectancy is negative, holds at 1.0x.
    """
    try:
        if journal_instance is not None:
            j = journal_instance
        else:
            from execution.trade_journal import journal as default_journal
            j = default_journal
        streak = j.get_current_streak()
        stats = j.stats()
        avg_pnl = float(stats.get("avg_pnl", 0.0) or 0.0)

        # Drawdown protection: scale down during cold streaks
        if streak <= -2:
            penalty = min(0.50, abs(streak + 1) * 0.15)
            return max(0.50, round(1.0 - penalty, 2))

        # Reinvestment: only reward winning streaks if expectancy is verified positive
        if streak >= 3 and avg_pnl > 0:
            boost = (streak - 2) * 0.10
            return min(1.30, round(1.0 + boost, 2))

        return 1.0
    except Exception as e:
        return 1.0


def calculate_position_size(
    portfolio_value: float, 
    current_price: float,
    confidence: float,
    max_risk_pct: float = 0.02,
    stop_loss_pct: float = 0.03,
    atr: float = None,
    psi: float = None,
    regime: str = None,
    bayesian_confidence: float = None,
    streak_compounding: bool = True,
) -> dict:
    try:
        if portfolio_value <= 0 or current_price <= 0 or confidence <= 0:
            return {"shares": 0, "position_value": 0.0, "stop_loss_price": 0.0}

        # Dynamic regime-adaptive risk percentage (Upgrade 4)
        if psi is not None or bayesian_confidence is not None or regime is not None:
            bayes_conf = bayesian_confidence if bayesian_confidence is not None else (
                confidence * 100.0 if confidence <= 1.0 else confidence
            )
            effective_risk_pct = calculate_regime_risk_pct(
                psi=psi,
                bayesian_confidence=bayes_conf,
                regime=regime,
                base_risk_pct=max_risk_pct,
            )
            if effective_risk_pct <= 0.0:
                return {
                    "shares": 0, "position_value": 0.0, "stop_loss_price": 0.0,
                    "reason": "Regime/conviction risk gate rejected (insufficient stability or confidence)"
                }
        else:
            effective_risk_pct = max_risk_pct

        max_risk_dollars = portfolio_value * effective_risk_pct

        # Streak compounding factor (Upgrade 5)
        streak_factor = 1.0
        if streak_compounding and (psi is not None or regime is not None):
            streak_factor = calculate_streak_compounding_factor()
            max_risk_dollars *= streak_factor
        
        # --- DYNAMIC STOP LOSS LOGIC (Upgrade 1 adaptive geometry) ---
        regime_applied = "FIXED_PCT"
        if atr and atr > 0:
            if psi is not None or regime is not None:
                from risk.hedging_engine import get_adaptive_exit_geometry
                geo = get_adaptive_exit_geometry(psi=psi, regime=regime)
                stop_mult = geo.get("stop_mult", 2.0)
                regime_applied = geo.get("regime_applied", "STATIC_BASELINE")
            else:
                stop_mult = 2.0
                regime_applied = "DEFAULT_2ATR"
            stop_loss_distance = atr * stop_mult
        else:
            # Fallback to fixed percentage if ATR is missing
            stop_loss_distance = current_price * stop_loss_pct
            
        if stop_loss_distance <= 0:
            return {"shares": 0, "position_value": 0.0, "stop_loss_price": 0.0}

        # Calculate shares and scale by model confidence
        base_shares        = max_risk_dollars / stop_loss_distance
        
        # Prevent confidence from pushing risk over 100% (max 1.0 multiplier)
        shares             = int(base_shares * min(confidence, 1.0))
        
        stop_loss_price    = current_price - stop_loss_distance
        position_value     = shares * current_price

        return {
            "shares":           shares,
            "position_value":   round(position_value, 2),
            "stop_loss_price":  round(stop_loss_price, 2),
            "risk_pct_used":    round(effective_risk_pct, 4),
            "streak_factor":    round(streak_factor, 2),
            "regime_applied":   regime_applied,
            "used_atr":         bool(atr)
        }

    except Exception as e:
        print(f"[calculate_position_size] Error: {e}")
        return {"shares": 0, "position_value": 0.0, "stop_loss_price": 0.0}


def check_portfolio_heat(current_exposure: float, portfolio_value: float,
                          new_position_value: float,
                          max_heat: float = 0.20) -> dict:
    # (Your heat logic remains unchanged, it is perfectly fine as is)
    try:
        if portfolio_value <= 0:
            return {"approved": False, "current_heat": 0.0, "reason": "invalid portfolio value"}

        current_heat = current_exposure / portfolio_value
        new_heat = (current_exposure + new_position_value) / portfolio_value
        
        # Check if we have enough available cash first
        available_cash = portfolio_value - current_exposure
        if new_position_value > available_cash:
             return {"approved": False, "current_heat": round(current_heat, 4), "reason": "Insufficient buying power"}

        approved = new_heat <= max_heat
        if approved:
            reason = f"Trade approved. Heat: {new_heat:.1%}"
        else:
            reason = f"Trade rejected. Heat would be {new_heat:.1%}, limit {max_heat:.1%}"
            
        return {
            "approved":     approved,
            "current_heat": round(current_heat, 4),
            "reason":       reason
        }

    except Exception as e:
        print(f"[check_portfolio_heat] Error: {e}")
        return {"approved": False, "current_heat": 0.0, "reason": "error"}


def calculate_compounder_size(
    portfolio_value: float,
    current_price: float,
    confidence: float,
    atr: float = None,
    max_risk_pct: float = 0.02,
    win_rate: float = 0.55,
    win_loss_ratio: float = 1.5,
    kelly_fraction: float = 0.25,
) -> dict:
    """
    Volatility-parity sizing with a fractional-Kelly capital-compounding cap.

    Kelly fraction f* = W - (1-W)/R, scaled down by kelly_fraction and then
    capped by max_risk_pct so small accounts never over-lever while still
    letting risk dollars grow automatically with equity.
    """
    try:
        kelly = win_rate - ((1.0 - win_rate) / win_loss_ratio)
        kelly_risk_pct = max(0.0, kelly) * kelly_fraction
        effective_risk_pct = min(max_risk_pct, kelly_risk_pct)

        result = calculate_position_size(
            portfolio_value, current_price, confidence,
            max_risk_pct=effective_risk_pct, atr=atr
        )
        result["risk_pct_used"] = round(effective_risk_pct, 4)
        result["sizing_model"] = "fractional_kelly_atr"
        return result
    except Exception as e:
        print(f"[calculate_compounder_size] Error: {e}")
        return {"shares": 0, "position_value": 0.0, "stop_loss_price": 0.0}


def check_tail_risk(net_beta_exposure: float, portfolio_value: float,
                    max_net_beta_ratio: float = 1.0) -> dict:
    """
    Downside tail-risk capping: total beta-weighted exposure must stay within
    a multiple of portfolio value (default 1.0x). A crash of X% therefore can
    never cost more than ~X% x max_net_beta_ratio of the account.
    """
    try:
        if portfolio_value <= 0:
            return {"approved": False, "reason": "invalid portfolio value"}

        limit = portfolio_value * max_net_beta_ratio
        approved = abs(float(net_beta_exposure)) <= limit

        return {
            "approved": approved,
            "net_beta_exposure": round(float(net_beta_exposure), 2),
            "tail_risk_limit": round(limit, 2),
            "reason": (
                f"Tail risk OK: net beta exposure ${abs(float(net_beta_exposure)):,.0f} "
                f"within ${limit:,.0f} limit"
            ) if approved else (
                f"Rejected: net beta exposure ${abs(float(net_beta_exposure)):,.0f} "
                f"exceeds ${limit:,.0f} limit"
            ),
        }
    except Exception as e:
        print(f"[check_tail_risk] Error: {e}")
        return {"approved": False, "reason": "error"}