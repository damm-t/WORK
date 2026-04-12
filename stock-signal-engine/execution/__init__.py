from .alpaca_client import (get_client, get_portfolio_value,
                             get_current_exposure, submit_order)

# Create client once at startup — singleton pattern
client = get_client()


def execute_trade(trade_decision: dict, ticker: str) -> dict:
    """
    Execute an approved trade decision from the risk layer.

    trade_decision: output from risk.evaluate_trade()
    {
        "approved": True,
        "shares": 39,
        "position_value": 6630.0,
        "stop_loss_price": 164.90
    }
    """
    try: 
        # Step 1: only execute if approved
        if not trade_decision.get("approved"):
                return {"status": "skipped", "reason": "Trade not approved"}

        # Step 2: extract shares and stop_loss_price from trade_decision
        shares = trade_decision.get("shares", 0)
        stop_loss_price = trade_decision.get("stop_loss_price", 0.0)

        # Step 3: safety check — never submit 0 shares
        if shares <= 0: return {"status": "skipped", "reason": "Zero shares"}

        # Step 4: submit the order
        result = submit_order(client, ticker, shares, stop_loss_price)

        return result

    except Exception as e: 
        return {"status": "failed", "reason": str(e)}

  