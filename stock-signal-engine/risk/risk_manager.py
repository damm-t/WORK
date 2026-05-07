def calculate_position_size(portfolio_value: float, current_price: float,
                             confidence: float,
                             max_risk_pct: float = 0.02,
                             stop_loss_pct: float = 0.03) -> dict:
    try:
        if portfolio_value <= 0 or current_price <= 0 or confidence <= 0:
            return {"shares": 0, "position_value": 0.0, "stop_loss_price": 0.0}

        max_risk_dollars   = portfolio_value * max_risk_pct
        stop_loss_distance = current_price * stop_loss_pct
        if stop_loss_distance <= 0:
            return {"shares": 0, "position_value": 0.0, "stop_loss_price": 0.0}

        base_shares        = max_risk_dollars / stop_loss_distance
        shares             = int(base_shares * confidence)
        stop_loss_price    = current_price * (1 - stop_loss_pct)
        position_value     = shares * current_price

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
    try:
        if portfolio_value <= 0:
            return {"approved": False, "current_heat": 0.0, "reason": "invalid portfolio value"}

        current_heat = current_exposure / portfolio_value
        new_heat = (current_exposure + new_position_value) / portfolio_value
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
