"""
Multi-Broker Client Abstraction Layer
=====================================
Instantiates broker clients dynamically for each subscriber using their own
credentials. Supports Alpaca Paper, Alpaca Live, and Simulated Broker adapters.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from gateway.subscriber_registry import SubscriberProfile

logger = logging.getLogger(__name__)


class BrokerClientFactory:
    """Creates and manages authenticated broker sessions for subscribers."""

    @staticmethod
    def get_account(profile: SubscriberProfile) -> Dict[str, Any]:
        """Fetches live account equity, cash, and buying power for a subscriber."""
        if profile.broker_type in ("alpaca_paper", "alpaca_live"):
            try:
                from alpaca.trading.client import TradingClient
                is_paper = (profile.broker_type == "alpaca_paper")
                client = TradingClient(
                    api_key=profile.api_key,
                    secret_key=profile.secret_key,
                    paper=is_paper
                )
                acc = client.get_account()
                return {
                    "status": "connected",
                    "equity": float(acc.equity),
                    "cash": float(acc.cash),
                    "buying_power": float(acc.buying_power),
                    "currency": acc.currency,
                    "trading_blocked": acc.trading_blocked,
                }
            except Exception as e:
                logger.warning(f"[broker_client] Alpaca connection error for {profile.user_id}: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "equity": profile.last_equity or 25000.0,
                    "cash": 10000.0,
                    "buying_power": 50000.0,
                }

        # Simulated / Webhook Broker fallback
        eq = float(profile.last_equity or 50000.0)
        return {
            "status": "connected_simulated",
            "equity": eq,
            "cash": eq * 0.8,
            "buying_power": eq * 2.0,
            "currency": "USD",
            "trading_blocked": False,
        }

    @staticmethod
    def submit_bracket_order(
        profile: SubscriberProfile,
        ticker: str,
        qty: int,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        side: str = "buy"
    ) -> Dict[str, Any]:
        """
        Transmits bracket order (Entry + Stop Loss + Take Profit) to the subscriber's broker.
        """
        ticker = ticker.upper().strip()
        if qty <= 0:
            return {"status": "skipped", "reason": "Quantity must be > 0"}

        if profile.broker_type in ("alpaca_paper", "alpaca_live"):
            try:
                from alpaca.trading.client import TradingClient
                from alpaca.trading.requests import MarketOrderRequest, TakeProfitRequest, StopLossRequest
                from alpaca.trading.enums import OrderSide, TimeInForce

                is_paper = (profile.broker_type == "alpaca_paper")
                client = TradingClient(
                    api_key=profile.api_key,
                    secret_key=profile.secret_key,
                    paper=is_paper
                )

                tp_req = TakeProfitRequest(limit_price=round(take_profit, 2)) if take_profit > 0 else None
                sl_req = StopLossRequest(stop_price=round(stop_loss, 2)) if stop_loss > 0 else None

                req = MarketOrderRequest(
                    symbol=ticker,
                    qty=qty,
                    side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
                    time_in_force=TimeInForce.GTC,
                    take_profit=tp_req,
                    stop_loss=sl_req,
                )

                order = client.submit_order(req)
                return {
                    "status": "submitted",
                    "order_id": str(order.id),
                    "symbol": ticker,
                    "qty": qty,
                    "broker": profile.broker_type,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                }
            except Exception as e:
                logger.error(f"[broker_client] Order submission failed for {profile.user_id}: {e}")
                return {"status": "error", "error": str(e), "user_id": profile.user_id}

        # Simulated Mirror Execution
        return {
            "status": "simulated_filled",
            "order_id": f"sim_{profile.user_id}_{ticker}_{int(qty)}",
            "symbol": ticker,
            "qty": qty,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "broker": "simulated_gateway",
        }


broker_factory = BrokerClientFactory()
