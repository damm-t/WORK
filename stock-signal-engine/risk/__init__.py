from .risk_manager import calculate_position_size, check_portfolio_heat


def evaluate_trade(signal: dict, current_price: float,
                   portfolio_value: float, current_exposure: float) -> dict:
    """
    Full risk evaluation for a potential trade.
    Returns final trade decision with position sizing.
    """

    # Step 1: skip risk checks if no BUY signal
    if signal.get("action") != "BUY":
        return {"approved": False, "reason": "No signal"}

    # Step 2: get confidence FIRST — then use it
    confidence = signal.get("confidence", 0.0)        # ✅ defined before use
    position   = calculate_position_size(             # ✅ now confidence exists
        portfolio_value, current_price, confidence
    )

    # Step 3: check portfolio heat
    heat = check_portfolio_heat(
        current_exposure, portfolio_value, position["position_value"]
    )

    # Step 4: reject if too hot
    if not heat["approved"]:
        return {"approved": False, "reason": heat["reason"]}

    # Step 5: full approval with position details
    return {
        "approved":        True,
        "shares":          position["shares"],
        "position_value":  position["position_value"],
        "stop_loss_price": position["stop_loss_price"],
        "reason":          signal["reason"]
    }