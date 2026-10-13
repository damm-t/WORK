"""
JEV Execution Engine — Alpaca Live/Paper Bracket Execution for Liquidity Scoops
================================================================================
Executes high-conviction Joint Expected Value (JEV) liquidity mean-reversion trades:
  - Sizes trades to strictly bounded dollar risk (default $50 per trade).
  - Enforces the 95% Core / 5% Momentum capital sandbox limits.
  - Submits atomic Alpaca bracket orders:
      * Entry limit order at the dislocated liquidity bid
      * Take profit limit at the Anti-Volatility Stabilized Price ($P_{\text{stab}}$)
      * Hard stop loss below the noise dislocation envelope
  - Records execution to SQLite Trade Journal under style='jev_scoop'
  - Feeds into Two-Worker Bayesian Belief & Confidence Engine
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from config import get_settings
from execution import client, submit_bracket_buy
from execution.trade_journal import journal
from market.anti_volatility import anti_volatility_model
from model.bayesian_confidence import belief_engine
from risk.book_allocator import get_book_allocations, classify_position_book
from strategy.jev_scooper import jev_scooper

logger = logging.getLogger(__name__)


def execute_jev_scoop_trade(
    ticker: str,
    entry_price: Optional[float] = None,
    take_profit: Optional[float] = None,
    stop_loss: Optional[float] = None,
    max_risk: Optional[float] = 50.0,
    dry_run: bool = False,
    client_instance: Any = None,
) -> Dict[str, Any]:
    """
    Executes a JEV liquidity scoop order onto Alpaca Paper/Live with atomic bracket protection.
    """
    settings = get_settings()
    cl = client_instance or client
    ticker_clean = str(ticker).strip().upper()

    # 1. Evaluate JEV setup
    opp = jev_scooper.evaluate_ticker(ticker_clean)

    entry = float(entry_price or opp.current_price)
    tp = float(take_profit or opp.take_profit_target)
    sl = float(stop_loss or opp.stop_loss)
    risk_budget = float(max_risk or 50.0)

    if entry <= 0:
        return {"status": "error", "ticker": ticker_clean, "message": "Invalid entry price"}

    if sl >= entry:
        sl = round(entry * 0.96, 2)
    if tp <= entry:
        tp = round(entry * 1.04, 2)

    risk_per_share = round(entry - sl, 2)
    if risk_per_share <= 0:
        return {"status": "error", "ticker": ticker_clean, "message": "Invalid stop loss geometry"}

    # 2. Position Sizing
    shares = int(risk_budget / risk_per_share)
    if shares <= 0:
        return {
            "status": "error",
            "ticker": ticker_clean,
            "message": f"Calculated 0 shares for risk budget ${risk_budget:.2f} (risk per share ${risk_per_share:.2f})",
        }

    notional = round(shares * entry, 2)
    book = classify_position_book(ticker_clean)

    # 3. Capital Sandbox Enforcement
    try:
        alloc = get_book_allocations(client=cl)
        book_info = alloc.get(book, {})
        remaining_budget = float(book_info.get("available_budget", 0.0))

        if notional > remaining_budget and not dry_run:
            original_notional = notional
            shares = int(remaining_budget / entry)
            notional = round(shares * entry, 2)
            if shares <= 0:
                return {
                    "status": "rejected",
                    "ticker": ticker_clean,
                    "message": f"Book '{book}' capacity exceeded. Remaining budget ${remaining_budget:.2f} < order ${original_notional:.2f}",
                }
    except Exception as e:
        logger.warning(f"Could not verify book capacity: {e}")

    # 4. Dry Run Mode
    if dry_run or os.getenv("DRY_RUN", "0") == "1":
        logger.info(f"[DRY RUN] JEV Scoop Bracket: BUY {shares} {ticker_clean} @ {entry} (TP: {tp}, SL: {sl}, Book: {book})")
        return {
            "status": "dry_run",
            "ticker": ticker_clean,
            "book": book,
            "shares": shares,
            "entry_price": entry,
            "take_profit": tp,
            "stop_loss": sl,
            "risk_per_share": risk_per_share,
            "total_risk_dollars": round(shares * risk_per_share, 2),
            "notional": notional,
            "jev_dollars": opp.jev_dollars,
            "jev_edge_pct": opp.jev_edge_pct,
            "win_probability_pct": opp.win_probability_pct,
            "rationale": opp.rationale,
        }

    # 5. Live/Paper Alpaca Bracket Order Submission
    try:
        order = submit_bracket_buy(
            client=cl,
            ticker=ticker_clean,
            qty=shares,
            limit_price=entry,
            take_profit=tp,
            stop_price=sl,
        )
        order_id = getattr(order, "id", None) or str(getattr(order, "client_order_id", ""))
    except Exception as e:
        logger.error(f"Alpaca bracket submission failed for {ticker_clean}: {e}")
        return {
            "status": "error",
            "ticker": ticker_clean,
            "message": f"Alpaca bracket order failed: {str(e)}",
        }

    # 6. Record to Trade Journal
    try:
        journal.record_open(
            ticker=ticker_clean,
            qty=float(shares),
            entry=entry,
            hedge="NO_HEDGE" if book == "momentum" else "CORE_MANAGED",
            grade="A" if opp.jev_edge_pct > 2.0 else "B",
            style="jev_scoop",
            regime="LIQUIDITY_DISLOCATION",
            score=round(opp.jev_edge_pct * 10.0, 1),
            actual_entry=entry,
            order_id=str(order_id),
            rationale=opp.rationale,
            book=book,
        )
    except Exception as e:
        logger.warning(f"Failed to record JEV trade to journal: {e}")

    # 7. Update Belief Engine
    try:
        belief_engine.run_daily_cycle(ticker_clean, cost_basis=entry)
    except Exception as e:
        logger.warning(f"Failed to update belief engine on execution: {e}")

    return {
        "status": "submitted",
        "ticker": ticker_clean,
        "book": book,
        "shares": shares,
        "entry_price": entry,
        "take_profit": tp,
        "stop_loss": sl,
        "notional": notional,
        "risk_budget": risk_budget,
        "order_id": str(order_id),
        "jev_edge_pct": opp.jev_edge_pct,
        "win_probability_pct": opp.win_probability_pct,
        "rationale": opp.rationale,
    }
