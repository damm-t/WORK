"""
Multi-Broker Subscriber Registry
================================
Secure registry managing premium user broker credentials, personalized
risk limits, and automated trade replication profiles.

Stores subscriber configurations in SQLite (`execution/subscribers.db`).
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

logger = logging.getLogger(__name__)

SUBSCRIBERS_DB = Path("execution/subscribers.db")
NY_TZ = ZoneInfo("America/New_York")


@dataclass
class SubscriberProfile:
    """User account profile for automated trade mirroring."""
    user_id: str
    tier: str                             # "PREMIUM_VIP", "INSTITUTIONAL", "PRO_TRADER"
    broker_type: str                      # "alpaca_paper", "alpaca_live", "ibkr_webhook"
    api_key: str
    secret_key: str
    base_url: str = "https://paper-api.alpaca.markets"
    risk_pct_per_trade: float = 0.015    # 1.5% Kelly risk default
    max_portfolio_heat: float = 0.45      # 45% strict heat cap
    max_daily_loss_pct: float = -0.03     # -3% daily loss kill-switch
    is_active: bool = True
    notes: str = ""
    registered_at: float = field(default_factory=time.time)
    last_sync_at: Optional[float] = None
    last_equity: float = 0.0
    last_buying_power: float = 0.0


class SubscriberRegistry:
    """
    Manages subscriber broker connectivity, risk controls, and state.
    """

    def __init__(self, db_path: Path = SUBSCRIBERS_DB):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id TEXT PRIMARY KEY,
                tier TEXT,
                broker_type TEXT,
                api_key TEXT,
                secret_key TEXT,
                base_url TEXT,
                risk_pct REAL,
                max_heat REAL,
                max_daily_loss REAL,
                is_active INTEGER,
                notes TEXT,
                registered_at REAL,
                last_sync_at REAL,
                last_equity REAL,
                last_buying_power REAL
            )
        """)
        conn.commit()
        conn.close()

    def register_or_update(self, profile: SubscriberProfile) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO subscribers (
                user_id, tier, broker_type, api_key, secret_key, base_url,
                risk_pct, max_heat, max_daily_loss, is_active, notes,
                registered_at, last_sync_at, last_equity, last_buying_power
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.user_id, profile.tier, profile.broker_type,
            profile.api_key, profile.secret_key, profile.base_url,
            profile.risk_pct_per_trade, profile.max_portfolio_heat,
            profile.max_daily_loss_pct, 1 if profile.is_active else 0,
            profile.notes, profile.registered_at, profile.last_sync_at,
            profile.last_equity, profile.last_buying_power
        ))
        conn.commit()
        conn.close()

    def get_subscriber(self, user_id: str) -> Optional[SubscriberProfile]:
        conn = sqlite3.connect(self.db_path)
        row = conn.execute("SELECT * FROM subscribers WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return self._row_to_profile(row)

    def list_all(self, active_only: bool = False) -> List[SubscriberProfile]:
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM subscribers WHERE is_active = 1" if active_only else "SELECT * FROM subscribers"
        rows = conn.execute(query).fetchall()
        conn.close()
        return [self._row_to_profile(r) for r in rows]

    def set_active_status(self, user_id: str, is_active: bool) -> bool:
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("UPDATE subscribers SET is_active = ? WHERE user_id = ?", (1 if is_active else 0, user_id))
        conn.commit()
        updated = cur.rowcount > 0
        conn.close()
        return updated

    def update_telemetry(self, user_id: str, equity: float, buying_power: float) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE subscribers
            SET last_equity = ?, last_buying_power = ?, last_sync_at = ?
            WHERE user_id = ?
        """, (equity, buying_power, time.time(), user_id))
        conn.commit()
        conn.close()

    def _row_to_profile(self, r: tuple) -> SubscriberProfile:
        return SubscriberProfile(
            user_id=r[0],
            tier=r[1],
            broker_type=r[2],
            api_key=r[3],
            secret_key=r[4],
            base_url=r[5],
            risk_pct_per_trade=float(r[6]),
            max_portfolio_heat=float(r[7]),
            max_daily_loss_pct=float(r[8]),
            is_active=bool(r[9]),
            notes=r[10] or "",
            registered_at=float(r[11] or time.time()),
            last_sync_at=float(r[12]) if r[12] else None,
            last_equity=float(r[13] or 0.0),
            last_buying_power=float(r[14] or 0.0),
        )


subscriber_registry = SubscriberRegistry()
