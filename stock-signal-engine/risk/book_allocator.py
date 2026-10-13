"""
Book Allocator — 95% Core Book + 5% Momentum Satellite Architecture
=====================================================================
Divides total portfolio equity between:
  1. 95% Core Book:
     - Sector mega-caps / liquid leaders (MSFT, META, AAPL, CAT, etc.)
     - Paired inverse-ETF beta hedges (SH, PSQ)
     - Asymmetric 2.0x ATR exit geometry & trailing ratchets
     - 2% Kelly risk and 20% max heat bounds of Core capital
  2. 5% Satellite Momentum Sandbox:
     - Ross Cameron low-float runners (<20M float, <$10, high RVOL)
     - Morning window (07:00-10:00 ET) micro-pullback breakouts
     - Strict $50-$100 fixed dollar risk per setup
     - Zero market beta hedge (micro-caps have beta ~ 0)
     - Hard capital ring-fence (max notional capped at 5% of account)
"""

import logging
import os
from typing import Any, Dict, List, Optional

from config import get_settings

logger = logging.getLogger(__name__)


def get_split_ratios() -> Dict[str, float]:
    """Returns normalized core and momentum split ratios from config/env."""
    settings = get_settings()
    try:
        core_pct = float(os.getenv("CORE_CAPITAL_PCT", str(settings.CORE_CAPITAL_PCT)))
    except (TypeError, ValueError):
        core_pct = 0.95

    try:
        mom_pct = float(os.getenv("MOMENTUM_CAPITAL_PCT", str(settings.MOMENTUM_CAPITAL_PCT)))
    except (TypeError, ValueError):
        mom_pct = 0.05

    tot = core_pct + mom_pct
    if tot <= 0:
        return {"core_pct": 0.95, "momentum_pct": 0.05}
    return {
        "core_pct": round(core_pct / tot, 4),
        "momentum_pct": round(mom_pct / tot, 4),
    }


def classify_position_book(symbol: str, known_momentum_symbols: Optional[set] = None) -> str:
    """Classifies a symbol into 'core' vs 'momentum'."""
    sym = symbol.upper().strip()
    from market.low_float_scanner import MOMENTUM_WATCHLIST
    mom_set = set(MOMENTUM_WATCHLIST)
    if known_momentum_symbols:
        mom_set.update(s.upper() for s in known_momentum_symbols)

    if sym in mom_set:
        return "momentum"

    # Dynamic check: look up recent/active trades in journal
    try:
        from execution.trade_journal import journal
        conn = journal._conn()
        row = conn.execute(
            """SELECT book, style FROM trades
               WHERE ticker = ?
               ORDER BY id DESC LIMIT 1""",
            (sym,)
        ).fetchone()
        conn.close()
        if row and (row[0] == "momentum" or row[1] == "ross_momentum"):
            return "momentum"
    except Exception:
        pass

    return "core"


def get_book_allocations(total_equity: Optional[float] = None, client: Any = None) -> Dict[str, Any]:
    """
    Computes real-time 95% Core and 5% Momentum allocation breakdown,
    open position segregation, and remaining risk budget.
    """
    settings = get_settings()
    ratios = get_split_ratios()
    core_pct = ratios["core_pct"]
    mom_pct = ratios["momentum_pct"]

    # 1. Resolve Total Equity
    if total_equity is None or total_equity <= 0:
        if client is not None:
            try:
                acct = client.get_account()
                total_equity = float(acct.equity)
            except Exception as e:
                logger.debug(f"[book_allocator] get_account failed: {e}")
        if total_equity is None or total_equity <= 0:
            # Fallback default detected capital
            total_equity = 96700.0

    core_budget = round(total_equity * core_pct, 2)
    momentum_budget = round(total_equity * mom_pct, 2)

    # 2. Inspect Open Positions and Journal Context
    core_positions: List[Dict[str, Any]] = []
    momentum_positions: List[Dict[str, Any]] = []
    core_market_value = 0.0
    momentum_market_value = 0.0
    core_unrealized_pl = 0.0
    momentum_unrealized_pl = 0.0

    known_momentum_symbols = set()
    try:
        from execution.trade_journal import journal
        conn = journal._conn()
        rows = conn.execute(
            "SELECT DISTINCT ticker FROM trades WHERE closed_at IS NULL AND (style = 'ross_momentum' OR book = 'momentum')"
        ).fetchall()
        conn.close()
        for r in rows:
            if r and r[0]:
                known_momentum_symbols.add(str(r[0]).upper())
    except Exception as e:
        logger.debug(f"[book_allocator] journal open check note: {e}")

    positions_list = []
    if client is not None:
        try:
            positions_list = client.get_all_positions()
        except Exception as e:
            logger.debug(f"[book_allocator] get_all_positions failed: {e}")

    for p in positions_list:
        symbol = str(getattr(p, "symbol", "")).upper()
        qty = abs(float(getattr(p, "qty", 0.0)))
        entry = float(getattr(p, "avg_entry_price", 0.0) or 0.0)
        now_px = float(getattr(p, "current_price", 0.0) or entry)
        mkt_val = float(getattr(p, "market_value", 0.0) or (qty * now_px))
        unrealized = float(getattr(p, "unrealized_pl", 0.0) or 0.0)
        unrealized_pct = float(getattr(p, "unrealized_plpc", 0.0) or 0.0) * 100.0

        b = classify_position_book(symbol, known_momentum_symbols)
        item = {
            "symbol": symbol,
            "book": b,
            "qty": qty,
            "avg_entry": round(entry, 2),
            "now": round(now_px, 2),
            "market_value": round(mkt_val, 2),
            "pnl_dollars": round(unrealized, 2),
            "pnl_pct": round(unrealized_pct, 2),
        }

        if b == "momentum":
            momentum_positions.append(item)
            momentum_market_value += mkt_val
            momentum_unrealized_pl += unrealized
        else:
            core_positions.append(item)
            core_market_value += mkt_val
            core_unrealized_pl += unrealized

    mom_available = max(0.0, round(momentum_budget - momentum_market_value, 2))
    core_available = max(0.0, round(core_budget - core_market_value, 2))

    max_trade_risk = float(os.getenv("MOMENTUM_MAX_TRADE_RISK", str(settings.MOMENTUM_MAX_TRADE_RISK)))

    return {
        "total_equity": round(total_equity, 2),
        "split_ratio": {
            "core_pct": round(core_pct * 100.0, 1),
            "momentum_pct": round(mom_pct * 100.0, 1),
        },
        "core": {
            "name": "Core Swing Book",
            "target_pct": round(core_pct * 100.0, 1),
            "budget": core_budget,
            "market_value": round(core_market_value, 2),
            "available_budget": core_available,
            "utilization_pct": round((core_market_value / core_budget) * 100.0, 1) if core_budget > 0 else 0.0,
            "unrealized_pl": round(core_unrealized_pl, 2),
            "positions_count": len(core_positions),
            "positions": core_positions,
            "hedged": any(p["symbol"] in {"SH", "PSQ"} for p in core_positions),
            "strategy": "Sector Leaders Swing + Inverse-ETF Hedge (2.0x ATR)",
        },
        "momentum": {
            "name": "Ross Momentum Satellite",
            "target_pct": round(mom_pct * 100.0, 1),
            "budget": momentum_budget,
            "market_value": round(momentum_market_value, 2),
            "available_budget": mom_available,
            "utilization_pct": round((momentum_market_value / momentum_budget) * 100.0, 1) if momentum_budget > 0 else 0.0,
            "unrealized_pl": round(momentum_unrealized_pl, 2),
            "positions_count": len(momentum_positions),
            "positions": momentum_positions,
            "max_trade_risk": max_trade_risk,
            "strategy": "Low-Float Runners (<20M float, <$10, 5-Pillar Pullbacks, $50 Risk)",
        },
    }
