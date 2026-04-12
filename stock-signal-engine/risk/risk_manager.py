def calculate_position_size(portfolio_value: float, current_price: float,
                             confidence: float,
                             max_risk_pct: float = 0.02,
                             stop_loss_pct: float = 0.03) -> dict:
    """
    Calculate safe position size based on portfolio and risk limits.
    """
    try:
        max_risk_dollars   = portfolio_value * max_risk_pct
        stop_loss_distance = current_price * stop_loss_pct
        base_shares        = max_risk_dollars / stop_loss_distance
        shares             = int(base_shares * confidence)
        stop_loss_price    = current_price * (1 - stop_loss_pct)
        position_value     = shares * current_price

        # ✅ named dict — not a tuple
        return {
            "shares":           shares,
            "position_value":   round(position_value, 2),
            "stop_loss_price":  round(stop_loss_price, 2)
        }

    except Exception as e:
        print(f"[calculate_position_size] Error: {e}")
        return {"shares": 0, "position_value": 0.0, "stop_loss_price": 0.0}


def check_portfolio_heat(current_exposure: float, portfolio_value: float,
                          new_position_value: float,
                          max_heat: float = 0.20) -> dict:
    """
    Check if adding a new position would exceed portfolio heat limit.
    """
    try:
        # Step 1: current heat as percentage
        current_heat = current_exposure / portfolio_value

        # Step 2: heat AFTER adding new position
        new_heat = (current_exposure + new_position_value) / portfolio_value

        # Step 3: approve or reject
        approved = True if new_heat <= max_heat else False

        # Step 4: reason string — :.1% formats 0.25 → "25.0%" automatically
        if approved:
            reason = f"Trade approved. Heat: {new_heat:.1%}"
        else:
            reason = f"Trade rejected. Heat would be {new_heat:.1%}, limit {max_heat:.1%}"

        # Step 5: return named dict
        return {
            "approved":     approved,
            "current_heat": round(current_heat, 4),
            "reason":       reason
        }

    except Exception as e:
        print(f"[check_portfolio_heat] Error: {e}")
        return {"approved": False, "current_heat": 0.0, "reason": "error"}