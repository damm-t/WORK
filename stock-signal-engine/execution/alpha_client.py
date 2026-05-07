import os
from dotenv import load_dotenv

try:
    import alpaca_trade_api as tradeapi
except Exception as e:
    tradeapi = None
    print(f"[alpha_client] Error: {e}")

load_dotenv()

APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID", "")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY", "")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")


def get_client():
    try:
        if tradeapi is None:
            return None

        if not APCA_API_KEY_ID or not APCA_API_SECRET_KEY:
            print("[get_client] Error: Missing Alpaca credentials")
            return None

        client = tradeapi.REST(
            APCA_API_KEY_ID,
            APCA_API_SECRET_KEY,
            ALPACA_BASE_URL,
            api_version="v2"
        )
        return client
    except Exception as e:
        print(f"[get_client] Error: {e}")
        return None


def get_portfolio_value(client) -> float:
    try:
        if client is None:
            return 0.0

        account = client.get_account()
        return float(account.portfolio_value)
    except Exception as e:
        print(f"[get_portfolio_value] Error: {e}")
        return 0.0


def get_current_exposure(client) -> float:
    try:
        if client is None:
            return 0.0

        positions = client.list_positions()
        return sum(float(position.market_value) for position in positions or [])
    except Exception as e:
        print(f"[get_current_exposure] Error: {e}")
        return 0.0


def submit_order(client, ticker: str, shares: int,
                 stop_loss_price: float) -> dict:
    try:
        if client is None:
            return {"status": "failed", "reason": "alpaca client unavailable"}

        buy_order = client.submit_order(
            symbol=ticker,
            qty=shares,
            side="buy",
            type="market",
            time_in_force="day"
        )
        stop_order = client.submit_order(
            symbol=ticker,
            qty=shares,
            side="sell",
            type="stop",
            time_in_force="day",
            stop_price=round(stop_loss_price, 2)
        )
        return {
            "ticker":          ticker,
            "shares":          shares,
            "status":          "submitted",
            "order_id":        str(buy_order.id),
            "stop_order_id":   str(stop_order.id),
            "stop_loss_price": stop_loss_price
        }
    except Exception as e:
        print(f"[submit_order] Error: {e}")
        return {"status": "failed", "reason": str(e)}
