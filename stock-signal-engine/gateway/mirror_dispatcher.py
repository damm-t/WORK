"""
Multi-Broker Trade Mirror Dispatcher
====================================
Replicates master engine signals across all enrolled premium subscribers,
scaling position sizing proportionally to each user's account equity and
custom Kelly risk parameters.

Features:
  - Personalized Proportional Sizing (Shares = (Equity * RiskPct) / StopDistance)
  - Subscriber-level Risk Isolation & Compliance Protection
  - Full Execution Ledger in SQLite (`execution/mirror_audit.db`)
  - Sub-second fan-out dispatch to Alpaca Live, Alpaca Paper & API brokers
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from gateway.broker_client import broker_factory
from gateway.subscriber_registry import SubscriberProfile, subscriber_registry

logger = logging.getLogger(__name__)

MIRROR_DB = Path("execution/mirror_audit.db")
NY_TZ = ZoneInfo("America/New_York")


@dataclass
class MirrorTradeSignal:
    """Master signal dispatched to subscribers for automated mirroring."""
    ticker: str
    side: str                             # "buy" or "sell"
    entry_price: float
    stop_loss: float
    take_profit: float
    strategy_name: str                    # "jev_scooper", "ross_momentum", "core_swing"
    grade: str = "A"
    rationale: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class ReplicationSummary:
    """Consolidated report across all mirrored accounts for a single master trade."""
    signal_ticker: str
    timestamp: float
    total_subscribers: int
    executed_count: int
    skipped_count: int
    total_capital_mirrored: float
    subscribers_report: List[Dict[str, Any]] = field(default_factory=list)


class MirrorDispatcher:
    """
    Executes proportional copy-trading fan-out across connected premium accounts.
    """

    def __init__(self, db_path: Path = MIRROR_DB):
        self.db_path = Path(db_path)
        self.registry = subscriber_registry
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS replicated_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_ticker TEXT,
                user_id TEXT,
                broker_type TEXT,
                shares INTEGER,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                status TEXT,
                order_id TEXT,
                capital_allocated REAL,
                error TEXT,
                timestamp REAL
            )
        """)
        conn.commit()
        conn.close()

    def replicate_signal(self, signal: MirrorTradeSignal) -> ReplicationSummary:
        """
        Fans out a trade signal to all active subscribers, sizing orders
        according to their personal capital and Kelly risk settings.
        """
        subscribers = self.registry.list_all(active_only=True)
        reports = []
        executed = 0
        skipped = 0
        total_capital = 0.0

        ticker = signal.ticker.upper().strip()
        stop_dist = abs(signal.entry_price - signal.stop_loss)
        if stop_dist <= 0:
            stop_dist = max(signal.entry_price * 0.02, 0.50)  # 2% default stop distance if 0

        for sub in subscribers:
            try:
                # 1. Fetch live subscriber account balance
                acc = broker_factory.get_account(sub)
                equity = float(acc.get("equity", sub.last_equity or 25000.0))
                bp = float(acc.get("buying_power", sub.last_buying_power or 50000.0))
                cash = float(acc.get("cash", 10000.0))

                # Update telemetry in registry
                self.registry.update_telemetry(sub.user_id, equity, bp)

                # 2. Check subscriber safety boundaries
                current_heat = max(0.0, 1.0 - (cash / max(equity, 1.0)))
                if current_heat >= sub.max_portfolio_heat:
                    reports.append({
                        "user_id": sub.user_id, "status": "skipped",
                        "reason": f"Heat limit ({current_heat:.1%}) exceeded cap ({sub.max_portfolio_heat:.1%})"
                    })
                    skipped += 1
                    self._record_order(signal.ticker, sub.user_id, sub.broker_type, 0, signal.entry_price, signal.stop_loss, signal.take_profit, "skipped_heat", "", 0.0, "Heat cap breached")
                    continue

                # 3. Proportional Risk Sizing
                risk_dollars = equity * sub.risk_pct_per_trade
                shares = int(risk_dollars / stop_dist)

                # Cap size to buying power
                cost = shares * signal.entry_price
                if cost > bp:
                    shares = int(bp / signal.entry_price)

                if shares <= 0:
                    reports.append({
                        "user_id": sub.user_id, "status": "skipped",
                        "reason": "Calculated shares = 0 (insufficient capital or tight risk)"
                    })
                    skipped += 1
                    self._record_order(signal.ticker, sub.user_id, sub.broker_type, 0, signal.entry_price, signal.stop_loss, signal.take_profit, "skipped_capital", "", 0.0, "Zero shares calculated")
                    continue

                # 4. Transmit order to subscriber broker
                res = broker_factory.submit_bracket_order(
                    profile=sub,
                    ticker=ticker,
                    qty=shares,
                    entry_price=signal.entry_price,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit,
                    side=signal.side,
                )

                status = res.get("status", "error")
                order_id = res.get("order_id", "")
                capital_used = round(shares * signal.entry_price, 2)

                if "submitted" in status or "filled" in status:
                    executed += 1
                    total_capital += capital_used
                    reports.append({
                        "user_id": sub.user_id,
                        "status": "mirrored",
                        "shares": shares,
                        "capital_allocated": capital_used,
                        "order_id": order_id,
                        "broker": sub.broker_type,
                    })
                else:
                    skipped += 1
                    reports.append({
                        "user_id": sub.user_id,
                        "status": "error",
                        "error": res.get("error", "Unknown broker error")
                    })

                self._record_order(
                    signal_ticker=ticker,
                    user_id=sub.user_id,
                    broker_type=sub.broker_type,
                    shares=shares,
                    entry_price=signal.entry_price,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit,
                    status=status,
                    order_id=order_id,
                    capital_allocated=capital_used,
                    error=res.get("error", "")
                )

            except Exception as e:
                logger.error(f"[mirror_dispatcher] Exception dispatching for {sub.user_id}: {e}")
                reports.append({"user_id": sub.user_id, "status": "error", "error": str(e)})
                skipped += 1

        return ReplicationSummary(
            signal_ticker=ticker,
            timestamp=time.time(),
            total_subscribers=len(subscribers),
            executed_count=executed,
            skipped_count=skipped,
            total_capital_mirrored=round(total_capital, 2),
            subscribers_report=reports,
        )

    def _record_order(
        self,
        signal_ticker: str,
        user_id: str,
        broker_type: str,
        shares: int,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        status: str,
        order_id: str,
        capital_allocated: float,
        error: str = ""
    ) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO replicated_orders (
                signal_ticker, user_id, broker_type, shares, entry_price,
                stop_loss, take_profit, status, order_id, capital_allocated,
                error, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            signal_ticker, user_id, broker_type, shares, entry_price,
            stop_loss, take_profit, status, order_id, capital_allocated,
            error, time.time()
        ))
        conn.commit()
        conn.close()

    def get_recent_replications(self, limit: int = 25) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("""
            SELECT id, signal_ticker, user_id, broker_type, shares,
                   entry_price, stop_loss, take_profit, status, order_id,
                   capital_allocated, error, timestamp
            FROM replicated_orders ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
        conn.close()

        return [{
            "id": r[0], "signal_ticker": r[1], "user_id": r[2], "broker_type": r[3],
            "shares": r[4], "entry_price": r[5], "stop_loss": r[6], "take_profit": r[7],
            "status": r[8], "order_id": r[9], "capital_allocated": r[10], "error": r[11],
            "timestamp": r[12],
            "formatted_time": datetime.fromtimestamp(r[12], tz=NY_TZ).strftime("%Y-%m-%d %H:%M:%S ET")
        } for r in rows]


mirror_dispatcher = MirrorDispatcher()
