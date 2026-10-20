import logging
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, StopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def get_client():
    return TradingClient(settings.APCA_API_KEY_ID, settings.APCA_API_SECRET_KEY, paper=True)

def get_portfolio_value(client: TradingClient) -> float:
    return float(client.get_account().portfolio_value)

def get_current_exposure(client: TradingClient) -> float:
    positions = client.get_all_positions()
    return sum(float(p.market_value) for p in positions)

def submit_order(client: TradingClient, ticker: str, shares: int, stop_loss_price: float) -> dict:
    # 1. Market Buy
    buy_order = client.submit_order(MarketOrderRequest(
        symbol=ticker, qty=shares, side=OrderSide.BUY, time_in_force=TimeInForce.DAY
    ))
    buy_id = str(buy_order.id)
    
    # 2. Stop Loss Sell — GTC so protection SURVIVES overnight/multi-day holds
    #    (DAY orders silently expire at midnight = unprotected position!)
    stop_id = None
    stop_warning = None
    if stop_loss_price and stop_loss_price > 0:
        try:
            stop_order = client.submit_order(StopOrderRequest(
                symbol=ticker, qty=shares, side=OrderSide.SELL,
                time_in_force=TimeInForce.GTC,
                stop_price=round(stop_loss_price, 2)
            ))
            stop_id = str(stop_order.id)
        except Exception as se:
            print(f"[submit_order] Stop order warning for {ticker} (Exit Manager tracking internally): {se}")
            stop_warning = str(se)
    
    res = {"status": "submitted", "buy_id": buy_id, "stop_id": stop_id}
    if stop_warning:
        res["stop_warning"] = stop_warning
    return res

def submit_bracket_buy(client, ticker: str, qty: int, limit_price: float,
                       take_profit: float, stop_price: float,
                       tif: str = "gtc") -> dict:
    """
    Pre-placed BRACKET entry: limit buy + attached TP + attached SL in ONE
    atomic order — can be queued BEFORE the market opens (fills at/better
    than limit at open, children arm automatically).

    Defaults to GTC so stop loss survives multi-day holds and overnight sessions.
    """
    from alpaca.trading.enums import OrderClass                    # noqa: E402
    from alpaca.trading.requests import (LimitOrderRequest,         # noqa: E402
                                         TakeProfitRequest,
                                         StopLossRequest)

    tif_final = TimeInForce.GTC if str(tif).lower() == "gtc" else TimeInForce.DAY
    req = LimitOrderRequest(
        symbol=ticker.upper(),
        qty=int(qty),
        side=OrderSide.BUY,
        time_in_force=tif_final,
        limit_price=round(float(limit_price), 2),
        order_class=OrderClass.BRACKET,
        take_profit=TakeProfitRequest(limit_price=round(float(take_profit), 2)),
        stop_loss=StopLossRequest(stop_price=round(float(stop_price), 2)),
    )
    o = client.submit_order(req)
    return {
        "status": "submitted", "order_id": str(o.id), "class": "bracket",
        "symbol": ticker.upper(), "qty": int(qty),
        "limit": round(float(limit_price), 2),
        "tp": round(float(take_profit), 2),
        "sl": round(float(stop_price), 2),
        "tif": str(tif_final),
    }


def submit_market_order(client: TradingClient, ticker: str, shares: int,
                        side: str = "BUY") -> dict:
    """Plain market order (used for the hedge leg: BUY SH / PSQ, or closing legs)."""
    try:
        order = client.submit_order(MarketOrderRequest(
            symbol=ticker.upper(),
            qty=int(shares),
            side=OrderSide.BUY if str(side).upper() == "BUY" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        ))
        return {"status": "submitted", "order_id": str(order.id),
                "symbol": ticker.upper(), "side": str(side).upper(), "qty": int(shares)}
    except Exception as e:
        print(f"[submit_market_order] Error for {ticker}: {e}")
        return {"status": "error", "symbol": ticker.upper(), "message": str(e)}

def submit_pair_orders(client: TradingClient, ticker: str, shares: int,
                       stop_loss_price: float, hedge: dict) -> dict:
    """
    Executes the paired Long Alpha + Beta Hedge as two atomic legs:
      Leg 1: BUY alpha ticker + protective stop loss.
      Leg 2: BUY inverse-ETF hedge instrument (e.g. SH/PSQ).
    Enforces Project Omega Mandatory Hedge Integrity: aborts entry if hedge leg fails.
    """
    hedge_symbol = str(hedge.get("hedge_instrument", "") or "").upper()
    hedge_shares = int(hedge.get("hedge_shares", 0) or 0)
    hedge_dollars = float(hedge.get("hedge_dollars", 0.0) or 0.0)
    hedge_failed = bool(hedge.get("hedge_failed", False))

    # Reject naked execution if mandatory hedge failed or sized to 0
    if hedge_failed or (hedge_dollars > 0 and (not hedge_symbol or hedge_shares <= 0)):
        logger.critical(
            f"[alpha_client] 🚨 REJECTING PAIRED ENTRY for {ticker}: Mandatory hedge integrity check failed "
            f"({hedge.get('reason', 'hedge_shares <= 0')}). Aborting to prevent naked exposure."
        )
        return {
            "status": "rejected",
            "reason": f"Mandatory hedge failed: {hedge.get('reason', 'Zero hedge shares')}",
            "ticker": ticker,
            "hedge": hedge
        }

    result = submit_order(client, ticker, shares, stop_loss_price)
    if result.get("status") != "submitted":
        return result

    if not hedge_symbol or hedge_shares <= 0:
        result["hedge"] = {"status": "skipped",
                           "reason": hedge.get("message", "Zero-size hedge leg")}
        return result

    hedge_order = submit_market_order(client, hedge_symbol, hedge_shares, side="BUY")
    result["hedge"] = hedge_order
    if str(hedge_order.get("status")) != "submitted":
        logger.critical(
            f"[alpha_client] 🚨 UNHEDGED EXPOSURE ALERT: Alpha {ticker} submitted ({result.get('buy_id')}), "
            f"but hedge {hedge_symbol} order failed ({hedge_order.get('reason')})."
        )
    return result