import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

load_dotenv()

ALPACA_API_KEY  = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET   = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")


def get_client():
    """
    Create and return Alpaca API client.
    """
    try:
        client = tradeapi.REST(          # ✅ save to variable
            ALPACA_API_KEY,              # ✅ use constants not undefined names
            ALPACA_SECRET,
            ALPACA_BASE_URL,
            api_version="v2"
        )
        return client                    # ✅ return it

    except Exception as e:
        print(f"[get_client] Error: {e}")
        return None


def get_portfolio_value(client) -> float:
    """
    Get current total portfolio value from Alpaca.
    """
    try:
        account = client.get_account()
        return float(account.portfolio_value)  # ✅ always wrap in float()

    except Exception as e:
        print(f"[get_portfolio_value] Error: {e}")
        return 0.0


def get_current_exposure(client) -> float:
    """
    Get total dollar value of all open positions.
    """
    try:
        positions = client.list_positions()

        # list comprehension — float() each market_value, then sum
        return sum([float(p.market_value) for p in positions])  # ✅ Python style

    except Exception as e:                          # ✅ fixed typo: excpet → except
        print(f"[get_current_exposure] Error: {e}")
        return 0.0


def submit_order(client, ticker: str, shares: int,
                 stop_loss_price: float) -> dict:
    """
    Submit market buy order + stop loss to Alpaca.
    """
    try:
        # Step 1: market buy order — save to variable to get order id
        buy_order = client.submit_order(     # ✅ saved to buy_order
            symbol=ticker,
            qty=shares,
            side="buy",
            type="market",
            time_in_force="day"
        )

        # Step 2: stop loss order — triggers automatically if price drops
        stop_order = client.submit_order(    # ✅ saved to stop_order
            symbol=ticker,
            qty=shares,
            side="sell",
            type="stop",
            time_in_force="day",
            stop_price=round(stop_loss_price, 2)
        )

        # Step 3: return confirmation — proper dict syntax
        return {
            "ticker":          ticker,
            "shares":          shares,
            "status":          "submitted",
            "order_id":        str(buy_order.id),   # ✅ buy_order exists now
            "stop_order_id":   str(stop_order.id),
            "stop_loss_price": stop_loss_price
        }

    except Exception as e:
        return {"status": "failed", "reason": str(e)}