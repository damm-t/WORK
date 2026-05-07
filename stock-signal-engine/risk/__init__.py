from .risk_manager import calculate_position_size, check_portfolio_heat


def evaluate_trade(signal: dict, current_price: float,
                   portfolio_value: float, current_exposure: float) -> dict:
    try:
        if signal.get("action") != "BUY":
            return {"approved": False, "reason": "No signal"}

        confidence = float(signal.get("confidence", 0.0) or 0.0)
        position = calculate_position_size(portfolio_value, current_price, confidence)
        if not position:
            return {"approved": False, "reason": "Position sizing failed"}

        heat = check_portfolio_heat(
            current_exposure,
            portfolio_value,
            float(position.get("position_value", 0.0) or 0.0)
        )
        if not heat.get("approved", False):
            return {"approved": False, "reason": heat.get("reason", "Portfolio heat exceeded")}

        return {
            "approved":        True,
            "shares":          int(position.get("shares", 0) or 0),
            "position_value":  float(position.get("position_value", 0.0) or 0.0),
            "stop_loss_price": float(position.get("stop_loss_price", 0.0) or 0.0),
            "reason":          signal.get("reason", "")
        }
    except Exception as e:
        print(f"[evaluate_trade] Error: {e}")
        return {"approved": False, "reason": "error"}
