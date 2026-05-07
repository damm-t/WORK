from .alpha_client import (get_client, get_portfolio_value,
                             get_current_exposure, submit_order)

client = get_client()


def execute_trade(trade_decision: dict, ticker: str) -> dict:
    try:
        if not isinstance(trade_decision, dict):
            return {}

        if not trade_decision.get("approved"):
            return {"status": "skipped", "reason": "Trade not approved"}

        shares = int(trade_decision.get("shares", 0) or 0)
        stop_loss_price = float(trade_decision.get("stop_loss_price", 0.0) or 0.0)
        if shares <= 0:
            return {"status": "skipped", "reason": "Zero shares"}

        return submit_order(client, ticker, shares, stop_loss_price)
    except Exception as e:
        print(f"[execute_trade] Error: {e}")
        return {}
