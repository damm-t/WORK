"""
Episodic Failure Memory & Regret Minimization Engine
===================================================
Inspired by the core principle: "Data showing where AI fails is the most valuable asset."

Tracks, clusters, and learns from every adverse trade outcome, stop-out, and execution
slippage across all 4 desks (Stocks, Crypto, CME Futures, Forex).

When an agent desk or the Agent Council evaluates a trade proposal, the Failure Memory
queries historical episodes under matching market conditions (regime, session hour,
volatility compression, indicator posture) and issues proactive defense actions
(VETO, SIZING_DISCOUNT, or SPREAD_GUARD) before live capital is risked.
"""

from __future__ import annotations

import datetime
import json
import logging
import math
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_DB_PATH = _BASE_DIR / "execution" / "failure_memory.db"


@dataclass
class FailureEpisode:
    id: Optional[int]
    timestamp: float
    desk: str                      # 'stocks', 'crypto', 'cme', 'forex'
    symbol: str
    strategy: str
    side: str                      # 'LONG', 'SHORT'
    entry_price: float
    exit_price: float
    pnl: float
    loss_pct: float
    reason: str
    rsi: Optional[float] = None
    adx: Optional[float] = None
    bb_status: str = "NORMAL"      # 'COMPRESSED', 'EXPANDED', 'NORMAL'
    session_hour: int = 12         # UTC hour
    regime: str = "UNKNOWN"        # 'CHOP', 'TREND', 'SHOCK', 'DEAD_ZONE'
    lesson_learned: str = ""


@dataclass
class FailureRiskAssessment:
    risk_level: str                # 'LOW', 'MODERATE', 'HIGH', 'CRITICAL'
    failure_probability: float     # 0.0 to 1.0
    matching_episodes_count: int
    primary_vulnerability: str
    recommended_action: str        # 'PROCEED', 'REDUCE_SIZE_50', 'WIDEN_STOP_25', 'VETO'
    defense_rule: str
    similar_episodes: List[Dict[str, Any]] = field(default_factory=list)


class FailureMemoryEngine:
    """Persistent episodic failure memory and pre-trade guard."""

    def __init__(self, db_path: Path = MEMORY_DB_PATH):
        self.db_path = Path(db_path)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS failure_episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    desk TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL,
                    exit_price REAL,
                    pnl REAL NOT NULL,
                    loss_pct REAL,
                    reason TEXT NOT NULL,
                    rsi REAL,
                    adx REAL,
                    bb_status TEXT,
                    session_hour INTEGER,
                    regime TEXT,
                    lesson_learned TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_failure_strat_desk
                ON failure_episodes (strategy, desk, side)
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learned_defenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at REAL NOT NULL,
                    pattern_key TEXT UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    action TEXT NOT NULL,
                    times_triggered INTEGER DEFAULT 0,
                    capital_saved_estimate REAL DEFAULT 0.0
                )
            """)
            conn.commit()

    def record_failure(
        self,
        desk: str,
        symbol: str,
        strategy: str,
        side: str,
        pnl: float,
        reason: str,
        entry_price: float = 0.0,
        exit_price: float = 0.0,
        rsi: Optional[float] = None,
        adx: Optional[float] = None,
        bb_status: str = "NORMAL",
        session_hour: Optional[int] = None,
        regime: str = "UNKNOWN",
        timestamp: Optional[float] = None,
    ) -> int:
        """Records an adverse outcome / trade loss into the episodic memory."""
        if pnl >= 0 and "breakeven" not in reason.lower() and "floor" not in reason.lower():
            return -1  # Only adverse or pseudo-breakeven drag outcomes tracked

        ts = timestamp or time.time()
        hour = session_hour if session_hour is not None else datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).hour
        loss_pct = 0.0
        if entry_price > 0 and exit_price > 0:
            if side.upper() == "LONG":
                loss_pct = (exit_price - entry_price) / entry_price * 100.0
            else:
                loss_pct = (entry_price - exit_price) / entry_price * 100.0

        # Formulate deterministic lesson learned
        lesson = self._synthesize_lesson(strategy, side, reason, rsi, adx, bb_status, pnl)

        with self._conn() as conn:
            cur = conn.execute(
                """INSERT INTO failure_episodes
                   (timestamp, desk, symbol, strategy, side, entry_price, exit_price,
                    pnl, loss_pct, reason, rsi, adx, bb_status, session_hour, regime, lesson_learned)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    ts,
                    desk.lower(),
                    symbol.upper(),
                    strategy.upper(),
                    side.upper(),
                    float(entry_price),
                    float(exit_price),
                    float(pnl),
                    float(loss_pct),
                    str(reason),
                    float(rsi) if rsi is not None else None,
                    float(adx) if adx is not None else None,
                    str(bb_status).upper(),
                    int(hour),
                    str(regime).upper(),
                    lesson,
                ),
            )
            episode_id = cur.lastrowid
            conn.commit()

        # Update pattern defense rule
        self._reinforce_defense_rule(strategy, side, reason, bb_status)
        return episode_id or 0

    def query_failure_risk(
        self,
        strategy: str,
        side: str,
        desk: Optional[str] = None,
        rsi: Optional[float] = None,
        adx: Optional[float] = None,
        bb_status: Optional[str] = None,
        session_hour: Optional[int] = None,
    ) -> FailureRiskAssessment:
        """Evaluates whether current proposal matches historically vulnerable failure clusters."""
        strat = (strategy or "").upper().strip()
        s_side = (side or "").upper().strip()
        hour = session_hour if session_hour is not None else datetime.datetime.now(datetime.timezone.utc).hour

        with self._conn() as conn:
            # Match on strategy and side
            rows = conn.execute(
                """SELECT * FROM failure_episodes
                   WHERE strategy = ? OR desk = ?
                   ORDER BY timestamp DESC LIMIT 150""",
                (strat, (desk or "").lower()),
            ).fetchall()

        if not rows:
            return FailureRiskAssessment(
                risk_level="LOW",
                failure_probability=0.15,
                matching_episodes_count=0,
                primary_vulnerability="No matching failure clusters recorded for this strategy.",
                recommended_action="PROCEED",
                defense_rule="STANDARD_RISK_GATES",
                similar_episodes=[],
            )

        # Score similarity
        scored_episodes = []
        for r in rows:
            sim_score = 1.0  # Base match on strategy/desk
            if r["side"] == s_side:
                sim_score += 1.5
            if session_hour is not None and abs(r["session_hour"] - hour) <= 2:
                sim_score += 1.0
            if bb_status and r["bb_status"] and r["bb_status"].upper() == bb_status.upper():
                sim_score += 1.5
            if rsi is not None and r["rsi"] is not None and abs(r["rsi"] - rsi) <= 10:
                sim_score += 1.0

            scored_episodes.append((sim_score, dict(r)))

        # Sort by similarity
        scored_episodes.sort(key=lambda x: x[0], reverse=True)
        top_matches = [ep for score, ep in scored_episodes if score >= 2.5][:8]

        count = len(top_matches)
        if count == 0:
            return FailureRiskAssessment(
                risk_level="LOW",
                failure_probability=0.20,
                matching_episodes_count=0,
                primary_vulnerability="Strategy cleared episodic defense audit.",
                recommended_action="PROCEED",
                defense_rule="STANDARD_RISK_GATES",
                similar_episodes=[],
            )

        # Calculate empirical severity
        total_pnl = sum(ep["pnl"] for ep in top_matches)
        stop_hits = sum(1 for ep in top_matches if "stop" in ep["reason"].lower() or "spike" in ep["reason"].lower())
        stop_ratio = stop_hits / count

        # Determine risk level and defense action
        if count >= 4 and stop_ratio >= 0.60:
            risk_level = "CRITICAL"
            failure_prob = min(0.92, 0.50 + (stop_ratio * 0.40))
            action = "VETO"
            vulnerability = f"Severe cluster match: {count} historical failures with {stop_ratio*100:.0f}% stop-out rate (Cumulative loss: ${abs(total_pnl):,.2f})."
            rule = f"QUARANTINE_{strat}_UNDER_CURRENT_REGIME"
        elif count >= 3 or stop_ratio >= 0.50:
            risk_level = "HIGH"
            failure_prob = 0.65
            action = "REDUCE_SIZE_50"
            vulnerability = f"Vulnerability detected: {count} historical stop runs under similar volatility profile."
            rule = "HALVE_NOTIONAL_ALLOCATION"
        elif count >= 1:
            risk_level = "MODERATE"
            failure_prob = 0.40
            action = "WIDEN_STOP_25"
            vulnerability = f"Minor cluster match: {count} past drawdowns noted."
            rule = "ENFORCE_WIDE_ATR_BUFFER"
        else:
            risk_level = "LOW"
            failure_prob = 0.20
            action = "PROCEED"
            vulnerability = "Within normal operating parameters."
            rule = "STANDARD_RISK_GATES"

        clean_matches = [
            {
                "symbol": ep["symbol"],
                "strategy": ep["strategy"],
                "pnl": ep["pnl"],
                "reason": ep["reason"],
                "lesson": ep["lesson_learned"],
                "date": datetime.datetime.fromtimestamp(ep["timestamp"], datetime.timezone.utc).strftime("%Y-%m-%d"),
            }
            for ep in top_matches[:5]
        ]

        return FailureRiskAssessment(
            risk_level=risk_level,
            failure_probability=round(failure_prob, 2),
            matching_episodes_count=count,
            primary_vulnerability=vulnerability,
            recommended_action=action,
            defense_rule=rule,
            similar_episodes=clean_matches,
        )

    def _synthesize_lesson(
        self,
        strategy: str,
        side: str,
        reason: str,
        rsi: Optional[float],
        adx: Optional[float],
        bb_status: str,
        pnl: float,
    ) -> str:
        r_low = reason.lower()
        if "breakeven" in r_low or "green floor" in r_low:
            return f"Breakeven slippage trap: Trade hit ratchet floor but incurred ${abs(pnl):.2f} friction. Enforce +0.25 ATR profit buffer."
        if "disconnect" in r_low or "gap" in r_low:
            return "Feed latency cut: Loss incurred during feed dislocation/disconnect gap. Require multi-feed redundant heartbeat."
        if "pip spike" in r_low or "central bank" in r_low:
            return "Adverse macroeconomic dislocation: Flash ATR expansion exceeded stop distance. Gate against central bank calendar."
        if "stop" in r_low:
            if bb_status == "COMPRESSED":
                return f"{strategy} {side} chopped out inside Bollinger squeeze. Squeeze breakdowns frequently false-break."
            return f"{strategy} {side} momentum exhaustion. Stop-loss breached before target expansion."
        return f"Adverse exit ({reason}) resulting in ${pnl:.2f} loss."

    def _reinforce_defense_rule(self, strategy: str, side: str, reason: str, bb_status: str) -> None:
        pattern_key = f"{strategy}_{side}_{bb_status}".upper()
        desc = f"Defensive guard against {strategy} {side} failures in {bb_status} volatility."
        action = "REDUCE_SIZE_50" if "stop" in reason.lower() else "WIDEN_BUFFER"

        with self._conn() as conn:
            conn.execute(
                """INSERT INTO learned_defenses (created_at, pattern_key, description, action, times_triggered)
                   VALUES (?, ?, ?, ?, 1)
                   ON CONFLICT(pattern_key) DO UPDATE SET
                   times_triggered = times_triggered + 1""",
                (time.time(), pattern_key, desc, action),
            )
            conn.commit()

    def bootstrap_from_existing_history(self) -> Dict[str, int]:
        """Scans all historical state files and trade journals to backfill failure episodes."""
        counts = {"crypto": 0, "cme": 0, "forex": 0, "stocks": 0}

        # 1. Crypto Futures
        crypto_path = _BASE_DIR / "execution" / "crypto_futures_state.json"
        if crypto_path.exists():
            try:
                with open(crypto_path) as f:
                    cdata = json.load(f)
                for t in cdata.get("closed_trades", []):
                    pnl = float(t.get("pnl", 0))
                    r = t.get("reason", "")
                    if pnl < 0 or "breakeven" in r.lower():
                        self.record_failure(
                            desk="crypto",
                            symbol=t.get("symbol", "CRYPTO"),
                            strategy=t.get("strategy", "CRYPTO_AUTOPILOT"),
                            side=t.get("side", "LONG"),
                            pnl=pnl,
                            reason=r,
                            entry_price=float(t.get("entry_price", 0)),
                            exit_price=float(t.get("exit_price", 0)),
                            timestamp=float(t.get("closed_at", time.time())),
                        )
                        counts["crypto"] += 1
            except Exception as e:
                logger.warning(f"Error bootstrapping crypto failures: {e}")

        # 2. CME Futures
        cme_path = _BASE_DIR / "execution" / "cme_futures_state.json"
        if cme_path.exists():
            try:
                with open(cme_path) as f:
                    cdata = json.load(f)
                for t in cdata.get("closed_trades", []):
                    pnl = float(t.get("pnl", 0))
                    r = t.get("reason", "")
                    if pnl < 0:
                        self.record_failure(
                            desk="cme",
                            symbol=t.get("symbol", "FUTURES"),
                            strategy=t.get("strategy", "CME_AUTOPILOT"),
                            side=t.get("side", "LONG"),
                            pnl=pnl,
                            reason=r,
                            entry_price=float(t.get("entry_price", 0)),
                            exit_price=float(t.get("exit_price", 0)),
                            timestamp=float(t.get("closed_at", time.time())),
                        )
                        counts["cme"] += 1
            except Exception as e:
                logger.warning(f"Error bootstrapping CME failures: {e}")

        # 3. Forex
        forex_path = _BASE_DIR / "execution" / "forex_state.json"
        if forex_path.exists():
            try:
                with open(forex_path) as f:
                    fdata = json.load(f)
                for t in fdata.get("closed_trades", []):
                    pnl = float(t.get("pnl", 0))
                    r = t.get("reason", "")
                    if pnl < 0 or "breakeven" in r.lower():
                        self.record_failure(
                            desk="forex",
                            symbol=t.get("symbol", "FOREX"),
                            strategy=t.get("strategy", "FOREX_AUTOPILOT"),
                            side=t.get("side", "LONG"),
                            pnl=pnl,
                            reason=r,
                            entry_price=float(t.get("entry_price", 0)),
                            exit_price=float(t.get("exit_price", 0)),
                            timestamp=float(t.get("closed_at", time.time())),
                        )
                        counts["forex"] += 1
            except Exception as e:
                logger.warning(f"Error bootstrapping Forex failures: {e}")

        # 4. Stock Equity DB
        stock_db_path = _BASE_DIR / "execution" / "trade_journal.db"
        if stock_db_path.exists():
            try:
                conn = sqlite3.connect(stock_db_path)
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT * FROM trades WHERE closed_at IS NOT NULL AND pnl < 0"
                ).fetchall()
                for r in rows:
                    self.record_failure(
                        desk="stocks",
                        symbol=r["ticker"],
                        strategy=r["style"] or "STOCK_SWING",
                        side="LONG",
                        pnl=float(r["pnl"]),
                        reason=r["reason"] or "stop",
                        entry_price=float(r["entry"] or 0),
                        exit_price=float(r["exit"] or 0),
                        timestamp=float(r["closed_at"] or time.time()),
                    )
                    counts["stocks"] += 1
                conn.close()
            except Exception as e:
                logger.warning(f"Error bootstrapping stock failures: {e}")

        return counts

    def get_summary(self) -> Dict[str, Any]:
        """Returns high-level statistics and top vulnerability clusters."""
        with self._conn() as conn:
            total_episodes = conn.execute("SELECT count(*) FROM failure_episodes").fetchone()[0]
            total_drawdown_indexed = conn.execute("SELECT COALESCE(sum(pnl), 0) FROM failure_episodes").fetchone()[0]
            top_vulns = conn.execute(
                """SELECT strategy, desk, count(*) as fails, sum(pnl) as loss,
                          reason as primary_cause
                   FROM failure_episodes
                   GROUP BY strategy, desk
                   ORDER BY fails DESC LIMIT 5"""
            ).fetchall()
            defenses = conn.execute("SELECT count(*) FROM learned_defenses").fetchone()[0]

            return {
                "total_failure_episodes_indexed": total_episodes,
                "total_loss_indexed_usd": round(float(total_drawdown_indexed), 2),
                "active_defense_rules_count": defenses,
                "top_vulnerable_clusters": [
                    {
                        "strategy": r["strategy"],
                        "desk": r["desk"],
                        "failures_count": r["fails"],
                        "total_loss_usd": round(float(r["loss"]), 2),
                        "primary_cause": r["primary_cause"],
                    }
                    for r in top_vulns
                ],
            }


# Singleton instance
failure_memory = FailureMemoryEngine()
