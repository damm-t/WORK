"""
Ross Momentum Execution Engine — Alpaca Live/Paper Bracket Execution
=====================================================================
Executes Ross Cameron Low-Float Setups within the 5% Satellite Momentum Sandbox:
  - Verifies 5-Pillar criteria (RVOL, float, catalyst, price, change %)
  - Enforces strict capital boundary: total momentum position notional <= 5% of account
  - Sizes by fixed risk per trade (default $50.00)
  - Submits Alpaca atomic bracket order:
      * Entry limit order at breakout price
      * Hard stop loss at pullback low
      * Take profit 1 limit at High of Day (HOD)
  - Logs execution to SQLite Trade Journal under book='momentum'
"""

import logging
import os
from typing import Any, Dict, Optional

from config import get_settings
from execution import client, submit_bracket_buy
from execution.trade_journal import journal
from market.low_float_scanner import check_trading_window, evaluate_five_pillars
from market.price_fetcher import fetch_prices
from risk.book_allocator import get_book_allocations

logger = logging.getLogger(__name__)


def execute_ross_bracket_trade(
    ticker: str,
    entry_price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    hod_target: Optional[float] = None,
    max_risk: Optional[float] = None,
    dry_run: bool = False,
    client_instance: Any = None,
) -> Dict[str, Any]:
    """
    Executes a vetted Ross Cameron low-float runner setup onto Alpaca Paper/Live
    within the 5% Satellite Momentum Sandbox.
    """
    settings = get_settings()
    cl = client_instance or client
    ticker_clean = str(ticker).strip().upper()

    # 1. Trading Window & Pillar Check
    win_info = check_trading_window()
    pillar_info = evaluate_five_pillars(ticker_clean)

    # Ross Cameron Quality Gate: Grade A (5/5) or Grade B (4/5) strictly required
    grade = str(pillar_info.get("grade", "C")).upper()
    pillars_raw = pillar_info.get("pillars_passed", "0/5")
    try:
        passed_count = int(str(pillars_raw).split("/")[0])
    except Exception:
        passed_count = 0

    if grade == "C" or passed_count < 4:
        logger.warning(
            f"[ross_execution] REJECTED {ticker_clean}: Grade {grade} ({passed_count}/5 pillars). "
            f"Ross Cameron rules require Grade A or B (>=4/5 pillars passed)."
        )
        return {
            "status": "rejected",
            "ticker": ticker_clean,
            "message": (
                f"Setup disqualified: Grade {grade} with {passed_count}/5 pillars passed. "
                f"Ross Cameron rules strictly require Grade A or B (min 4/5 pillars passed)."
            ),
            "grade": grade,
            "pillars_passed": str(pillars_raw),
            "book": "momentum",
        }

    # 2. Price & Geometry Resolution
    if entry_price is None or entry_price <= 0:
        entry_price = float(pillar_info.get("price", 0.0) or 0.0)
        if entry_price <= 0:
            df = fetch_prices(ticker_clean, period="5d", interval="1m")
            if df is not None and not df.empty:
                entry_price = float(df["Close"].iloc[-1])

    if entry_price <= 0:
        return {"status": "error", "ticker": ticker_clean, "message": f"Could not determine market price for {ticker_clean}"}

    if stop_loss is None or stop_loss <= 0 or stop_loss >= entry_price:
        # Default pullback stop: 4% below entry or 0.15c minimum
        stop_dist = max(0.15, entry_price * 0.04)
        stop_loss = round(entry_price - stop_dist, 2)

    risk_per_share = round(entry_price - stop_loss, 2)
    if risk_per_share <= 0.01:
        risk_per_share = 0.05
        stop_loss = round(entry_price - risk_per_share, 2)

    if hod_target is None or hod_target <= entry_price:
        # Default target: 1.5x R:R to High of Day
        hod_target = round(entry_price + (risk_per_share * 1.5), 2)

    reward_per_share = round(hod_target - entry_price, 2)
    rr_ratio = round(reward_per_share / risk_per_share, 2) if risk_per_share > 0 else 0.0

    # 3. 5% Satellite Capital Allocation & Risk Sizing
    alloc = get_book_allocations(client=cl)
    momentum_info = alloc.get("momentum", {})
    available_budget = float(momentum_info.get("available_budget", 0.0))
    momentum_budget = float(momentum_info.get("budget", 4800.0))

    if max_risk is None or max_risk <= 0:
        max_risk = float(momentum_info.get("max_trade_risk", 50.0))

    # Size shares by fixed dollar risk: shares = risk_dollars / risk_per_share
    shares_by_risk = int(max_risk / risk_per_share)

    # Cap position value by remaining available momentum sandbox budget
    max_shares_by_budget = int(available_budget / entry_price) if entry_price > 0 else 0

    if max_shares_by_budget <= 0 and available_budget < 50.0:
        return {
            "status": "rejected",
            "ticker": ticker_clean,
            "message": f"5% Momentum Sandbox Budget Exhausted: Available ${available_budget:.2f} of ${momentum_budget:.2f} limit. Close existing momentum positions to free budget.",
            "book": "momentum",
            "available_budget": available_budget,
            "momentum_budget": momentum_budget,
        }

    shares = min(shares_by_risk, max_shares_by_budget)
    if grade == "B":
        # Ross Cameron sizing rule: Grade B (4/5 pillars, e.g. lack of news catalyst) trades at 50% sizing
        shares = max(1, shares // 2)

    shares = max(shares, 1)  # At least 1 share
    position_notional = round(shares * entry_price, 2)
    actual_risk_dollars = round(shares * risk_per_share, 2)

    # 4. Dry-run Check
    if dry_run:
        return {
            "status": "dry_run_approved",
            "ticker": ticker_clean,
            "grade": pillar_info.get("grade", "A"),
            "score": pillar_info.get("score", 85.0),
            "shares": shares,
            "entry_price": round(entry_price, 2),
            "stop_loss": round(stop_loss, 2),
            "hod_target": round(hod_target, 2),
            "risk_per_share": risk_per_share,
            "actual_risk_dollars": actual_risk_dollars,
            "position_notional": position_notional,
            "rr_ratio": rr_ratio,
            "book": "momentum",
            "available_budget": available_budget,
            "window": win_info,
            "pillars_passed": pillar_info.get("pillars_passed", "5/5"),
        }

    # 5. Order Placement (Alpaca Paper Bracket Order)
    order_result = None
    try:
        order_result = submit_bracket_buy(
            client=cl,
            ticker=ticker_clean,
            qty=shares,
            limit_price=entry_price,
            take_profit=hod_target,
            stop_price=stop_loss,
            tif="day",
        )
        order_id = str(order_result.get("order_id") or "")
    except Exception as e:
        logger.error(f"[ross_execution] Alpaca bracket order failed for {ticker_clean}: {e}")
        return {
            "status": "error",
            "ticker": ticker_clean,
            "message": f"Alpaca order execution failed: {e}",
            "book": "momentum",
        }

    # 6. Record to Trade Journal under book='momentum'
    journal_id = None
    try:
        rationale = (
            f"⚡ Ross Cameron 5-Pillar Breakout: {pillar_info.get('pillars_passed', '5/5')} passed. "
            f"Entry ${entry_price:.2f}, Stop ${stop_loss:.2f}, HOD ${hod_target:.2f}, "
            f"R:R {rr_ratio}:1, Risk ${actual_risk_dollars:.2f} (5% Sandbox)"
        )
        journal_id = journal.record_open(
            ticker=ticker_clean,
            qty=shares,
            entry=entry_price,
            hedge="",  # No market beta hedge for micro-caps
            grade=pillar_info.get("grade", "A"),
            style="ross_momentum",
            score=pillar_info.get("score", 85.0),
            order_id=order_id,
            rationale=rationale,
            book="momentum",
        )
    except Exception as je:
        logger.debug(f"[ross_execution] journal open note: {je}")

    logger.info(
        f"[ross_execution] SUBMITTED BRACKET {ticker_clean}: {shares} shares @ ${entry_price:.2f} "
        f"[SL: ${stop_loss:.2f} | TP: ${hod_target:.2f} | Risk: ${actual_risk_dollars:.2f}] Order ID: {order_id}"
    )

    return {
        "status": "submitted",
        "ticker": ticker_clean,
        "shares": shares,
        "entry_price": round(entry_price, 2),
        "stop_loss": round(stop_loss, 2),
        "hod_target": round(hod_target, 2),
        "risk_per_share": risk_per_share,
        "actual_risk_dollars": actual_risk_dollars,
        "position_notional": position_notional,
        "rr_ratio": rr_ratio,
        "order_id": order_id,
        "journal_id": journal_id,
        "book": "momentum",
        "satellite_budget_used": position_notional,
        "satellite_budget_remaining": max(0.0, round(available_budget - position_notional, 2)),
        "order_details": order_result,
        "grade": pillar_info.get("grade", "A"),
        "pillars_passed": pillar_info.get("pillars_passed", "5/5"),
    }
