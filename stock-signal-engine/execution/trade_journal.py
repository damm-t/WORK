"""
Trade Journal v2 — context-rich ledger + auto-suggestions
=========================================================
Every opened trade stores CONTEXT (grade, regime, session hour, score) so
analytics can answer: "WHERE does my edge live, and where does it bleed?"

    python -m execution.trade_journal --stats        # quick scoreboard
    python -m execution.trade_journal --analytics    # breakdown + tuning tips
"""

import argparse
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

DB_PATH = Path("execution/trade_journal.db")
NY_TZ = ZoneInfo("America/New_York")

_SCHEMA_EXTRA = [
    ("grade", "TEXT"), ("style", "TEXT"),
    ("session_hour", "INTEGER"), ("regime", "TEXT"), ("score", "REAL"),
    # --- v3: execution-quality tracking ---
    ("actual_entry", "REAL"),      # real avg fill price from Alpaca
    ("slippage_bps", "REAL"),      # (actual - theoretical) / theoretical x 1e4
    ("order_id", "TEXT"),          # Alpaca buy-order id for reconciliation
    ("rationale", "TEXT"),         # Full purchase rationale & indicator breakdown
    ("book", "TEXT"),              # 'core' (95%) vs 'momentum' (5%)
]


class TradeJournal:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)

    # ------------------------------------------------------------- storage ---
    def _conn(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""CREATE TABLE IF NOT EXISTS trades (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ticker TEXT, opened_at REAL, closed_at REAL,
                            qty REAL, entry REAL, exit REAL,
                            reason TEXT, pnl REAL, hedge TEXT)""")
        for col, ddl in _SCHEMA_EXTRA:                    # v2 migration
            try:
                conn.execute(f"ALTER TABLE trades ADD COLUMN {col} {ddl}")
            except sqlite3.OperationalError:
                pass                                      # column exists
        return conn

    @staticmethod
    def _ny_hour(ts: float) -> int:
        return datetime.fromtimestamp(ts, tz=NY_TZ).hour

    def record_open(self, ticker: str, qty: float, entry: float,
                    hedge: str = "", grade: str = None, style: str = None,
                    regime: str = None, score: float = None,
                    order_id: str = None, rationale: str = None,
                    opened_at: float = None, book: str = None) -> int:
        conn = self._conn()
        resolved_book = book or ("momentum" if style == "ross_momentum" else "core")
        cur = conn.execute(
            """INSERT INTO trades (ticker, opened_at, qty, entry, hedge,
                                   grade, style, session_hour, regime, score,
                                   order_id, rationale, reason, book)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ticker.upper(), opened_at or time.time(), float(qty), float(entry), str(hedge),
             grade, style, self._ny_hour(opened_at or time.time()), regime, score,
             order_id, rationale, rationale, resolved_book))
        conn.commit()
        row_id = cur.lastrowid
        conn.close()
        return row_id

    def pending_fills(self) -> list:
        """Open trades that still lack a confirmed actual fill price."""
        conn = self._conn()
        rows = conn.execute(
            """SELECT id, ticker, order_id, entry FROM trades
               WHERE closed_at IS NULL AND order_id IS NOT NULL
                 AND actual_entry IS NULL""").fetchall()
        conn.close()
        return [{"id": r[0], "ticker": r[1], "order_id": r[2],
                 "theoretical_entry": r[3]} for r in rows]

    def set_actual_entry(self, trade_id: int, fill_price: float) -> None:
        """Records the real fill and derives slippage vs theoretical entry."""
        conn = self._conn()
        row = conn.execute(
            "SELECT entry FROM trades WHERE id = ?", (trade_id,)).fetchone()
        if not row:
            conn.close()
            return
        theo = float(row[0])
        slip_bps = ((float(fill_price) - theo) / theo * 1e4) if theo else 0.0
        conn.execute("UPDATE trades SET actual_entry = ?, slippage_bps = ? "
                     "WHERE id = ?", (round(float(fill_price), 4),
                                      round(slip_bps, 1), trade_id))
        conn.commit()
        conn.close()

    def close_unfilled_trade(self, trade_id: int, reason: str = "order_expired_unfilled") -> None:
        """Marks an open trade whose broker order expired/canceled/rejected with 0 fills as closed with zero PnL."""
        conn = self._conn()
        row = conn.execute("SELECT entry FROM trades WHERE id = ?", (trade_id,)).fetchone()
        entry_px = float(row[0]) if row and row[0] is not None else 0.0
        now = time.time()
        conn.execute(
            "UPDATE trades SET closed_at = ?, exit = ?, reason = ?, pnl = 0.0 WHERE id = ?",
            (now, entry_px, reason, trade_id),
        )
        conn.commit()
        conn.close()

    def record_partial(self, ticker: str, exit_price: float, qty_sold: float,
                       pnl: float = 0.0, reason: str = "partial",
                       grade: str = None, style: str = None, score: float = None) -> None:
        """
        Realised clip from a PARTIAL exit (e.g. TP1 scale-out).

        Inserts a NEW closed row for the sold clip only.
        Decrements the open trade's qty so the open runner reflects remaining shares.
        Inherits grade, style, score, session_hour, regime from the parent trade.
        """
        try:
            conn = self._conn()
            row = conn.execute(
                """SELECT id, qty, COALESCE(actual_entry, entry), grade, style, session_hour, regime, score, book
                   FROM trades
                   WHERE ticker=? AND closed_at IS NULL
                   ORDER BY id DESC LIMIT 1""", (ticker.upper(),)).fetchone()
            if row:
                parent_id, current_qty, entry, p_grade, p_style, p_hour, p_regime, p_score, p_book = row
                entry_px = float(entry or 0.0)
                use_grade = grade or p_grade
                use_style = style or p_style
                use_score = score or p_score
                use_hour = p_hour
                use_regime = p_regime
                use_book = p_book or ("momentum" if use_style == "ross_momentum" else "core")

                # Decrement the open trade's qty so runner is sized accurately
                rem_qty = max(0.0, float(current_qty or 0.0) - float(qty_sold))
                conn.execute("UPDATE trades SET qty = ? WHERE id = ?", (rem_qty, parent_id))
            else:
                entry_px = 0.0
                use_grade, use_style, use_score, use_hour, use_regime = grade, style, score, None, None
                use_book = "momentum" if style == "ross_momentum" else "core"

            now = time.time()
            conn.execute(
                """INSERT INTO trades (ticker, opened_at, closed_at, qty,
                                       entry, exit, reason, pnl, grade, style,
                                       session_hour, regime, score, book)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (ticker.upper(), now, now, float(qty_sold),
                 entry_px, float(exit_price), str(reason), round(float(pnl), 2),
                 use_grade, use_style, use_hour, use_regime, use_score, use_book))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[trade_journal] record_partial error: {e}")

    def purge_mock_trades(self) -> int:
        """
        Removes simulated/mock trades from SQLite DB so mock sessions
        do not contaminate the live/paper trading ledger and overall metrics.
        Cleans up test artifacts and mock runner sessions.
        """
        conn = self._conn()
        cur = conn.execute(
            """DELETE FROM trades
               WHERE (
                  ticker = 'TEST'
                  OR order_id = 'test-order-123'
                  OR ticker LIKE 'MOCK%'
                  OR (
                     order_id IS NULL AND (
                        style = 'ross_momentum'
                        OR reason LIKE '%TP1 HOD Scale-Out%'
                        OR reason LIKE '%Topping Tail Reversal Candle%'
                        OR reason LIKE '%Volume Divergence%'
                        OR reason LIKE '%Hard Stop Hit (Pullback Low breached)%'
                        OR reason LIKE '%10:00 AM Trading Window Expired%'
                     )
                  )
               )"""
        )
        deleted = cur.rowcount
        conn.commit()
        conn.close()
        return deleted

    def reconcile_with_broker(self, client: Any = None) -> dict:
        """
        Comprehensive broker reconciliation between SQLite Trade Journal and Alpaca:
          - Automatically closes unfilled dead orders (expired/canceled/rejected with 0 fills) with $0.00 PnL
          - Backfills actual_entry for filled orders
          - Detects closed positions in Alpaca and closes them in the journal with real executed exit and P&L
          - Purges test/mock artifacts
        """
        if client is None:
            from execution import client as default_client
            client = default_client

        reconciled_unfilled = 0
        reconciled_fills = 0
        reconciled_closed_positions = 0

        # 1. Fetch Alpaca live positions
        broker_positions = {}
        try:
            positions = client.get_all_positions()
            broker_positions = {str(p.symbol).upper(): p for p in positions}
        except Exception as pe:
            logger.warning(f"[trade_journal] get_all_positions failed during reconciliation: {pe}")

        # 2. Inspect all open trades
        conn = self._conn()
        open_rows = conn.execute(
            """SELECT id, ticker, order_id, entry, qty, actual_entry
               FROM trades
               WHERE closed_at IS NULL"""
        ).fetchall()
        conn.close()

        for row in open_rows:
            trade_id, ticker, order_id, theo_entry, qty, actual_entry = row
            ticker_clean = str(ticker).upper()

            if ticker_clean == "TEST" or order_id == "test-order-123":
                self.close_unfilled_trade(trade_id, reason="Test Artifact Removed")
                continue

            if not order_id:
                if ticker_clean not in broker_positions:
                    self.close_unfilled_trade(trade_id, reason="Manual/Mock Position Cleared")
                continue

            try:
                order = client.get_order_by_id(order_id)
                o_status = str(getattr(order, "status", "")).lower().replace("orderstatus.", "")
                filled_qty = float(getattr(order, "filled_qty", 0) or 0)
                filled_avg_px = getattr(order, "filled_avg_price", None)

                if o_status in ("expired", "canceled", "rejected", "stopped") and filled_qty == 0:
                    status_name = o_status.capitalize()
                    self.close_unfilled_trade(trade_id, reason=f"Order {status_name} (0 Fills)")
                    reconciled_unfilled += 1
                    continue

                if o_status == "filled" and filled_avg_px:
                    if not actual_entry:
                        self.set_actual_entry(trade_id, float(filled_avg_px))
                        actual_entry = float(filled_avg_px)
                        reconciled_fills += 1

                # If the order filled (or partially filled) but ticker has 0 position in Alpaca:
                # Alpaca position is closed!
                if ticker_clean not in broker_positions and (o_status == "filled" or filled_qty > 0):
                    cost_basis = float(actual_entry or theo_entry or 0.0)
                    exit_px = cost_basis
                    exit_reason = "Closed by Broker"
                    try:
                        from alpaca.trading.requests import GetOrdersRequest
                        from alpaca.trading.enums import QueryOrderStatus
                        req = GetOrdersRequest(status=QueryOrderStatus.CLOSED, symbols=[ticker_clean], limit=5)
                        closed_orders = client.get_orders(req)
                        sell_orders = [co for co in closed_orders if str(co.side).lower().endswith("sell") and str(co.status).lower().endswith("filled")]
                        if sell_orders:
                            last_sell = sell_orders[0]
                            if last_sell.filled_avg_price:
                                exit_px = float(last_sell.filled_avg_price)
                                exit_reason = "Broker Bracket Exit"
                    except Exception as co_err:
                        logger.debug(f"[trade_journal] finding closing order for {ticker_clean}: {co_err}")

                    shares_closed = filled_qty if filled_qty > 0 else float(qty or 0.0)
                    realized_pnl = round((exit_px - cost_basis) * shares_closed, 2)
                    now = time.time()
                    conn = self._conn()
                    conn.execute(
                        "UPDATE trades SET closed_at = ?, exit = ?, pnl = ?, reason = ? WHERE id = ?",
                        (now, exit_px, realized_pnl, exit_reason, trade_id)
                    )
                    conn.commit()
                    conn.close()
                    reconciled_closed_positions += 1
            except Exception as oe:
                logger.debug(f"[trade_journal] order reconcile {order_id}: {oe}")

        return {
            "reconciled_unfilled": reconciled_unfilled,
            "reconciled_fills": reconciled_fills,
            "reconciled_closed_positions": reconciled_closed_positions,
            "active_positions_in_broker": list(broker_positions.keys()),
        }

    def record_close(self, ticker: str, exit_price: float, reason: str,
                     pnl: float = 0.0) -> None:
        conn = self._conn()
        # Cost basis prefers the REAL fill when reconciliation has landed,
        # so realised P&L reflects what was actually paid.
        row = conn.execute(
            """SELECT id, qty, COALESCE(actual_entry, entry), style, book, opened_at, COALESCE(slippage_bps, 0.0)
               FROM trades
               WHERE ticker=? AND closed_at IS NULL
               ORDER BY id DESC LIMIT 1""", (ticker.upper(),)).fetchone()
        if not row:
            conn.close()
            return
        trade_id, qty, entry, style, book, opened_at, slip_bps = row
        pnl = pnl if pnl else (float(exit_price) - float(entry)) * float(qty)
        close_ts = time.time()
        conn.execute("UPDATE trades SET closed_at=?, exit=?, reason=?, pnl=? "
                     "WHERE id=?", (close_ts, float(exit_price), reason,
                                    round(pnl, 2), trade_id))
        conn.commit()
        conn.close()

        # Trigger Autonomous Praise/Punish Feedback Loop
        try:
            from compliance.autonomous_checker import compliance_checker
            hold_hrs = max(0.0, (close_ts - float(opened_at or close_ts)) / 3600.0)
            strat_name = style or book or "core_swing"
            compliance_checker.audit_closed_trade(
                trade_id=trade_id,
                ticker=ticker.upper(),
                strategy_name=strat_name,
                pnl=round(float(pnl), 2),
                entry_price=float(entry or 0.0),
                exit_price=float(exit_price),
                holding_time_hours=round(hold_hrs, 2),
                reason=str(reason),
                slippage_bps=float(slip_bps or 0.0),
            )
        except Exception as ce:
            print(f"[trade_journal] autonomous compliance audit warning: {ce}")

    def get_exits(self, limit: int = 50) -> list:
        """Returns all exit events (both TP1 partial scale-outs and final closes) from the DB."""
        conn = self._conn()
        rows = conn.execute(
            """SELECT id, ticker, opened_at, closed_at, qty, entry, exit,
                      reason, pnl, grade, score
               FROM trades
               WHERE exit IS NOT NULL OR closed_at IS NOT NULL
               ORDER BY id DESC LIMIT ?""", (int(limit),)).fetchall()
        conn.close()
        exits = []
        for r in rows:
            trade_id, ticker, opened_at, closed_at, qty, entry, exit_px, reason, pnl, grade, score = r
            entry_f = float(entry or 0.0)
            exit_f = float(exit_px or 0.0)
            pnl_f = float(pnl or 0.0)
            pnl_pct = round(((exit_f / entry_f) - 1.0) * 100.0, 2) if entry_f > 0 else 0.0
            is_partial = "partial" in str(reason).lower() or "tp1" in str(reason).lower()
            exits.append({
                "id": trade_id,
                "ticker": ticker,
                "opened_at": opened_at,
                "closed_at": closed_at or opened_at,
                "type": "PARTIAL TP1" if is_partial else "FULL EXIT",
                "qty": float(qty or 0.0),
                "entry": round(entry_f, 2),
                "exit": round(exit_f, 2),
                "pnl": round(pnl_f, 2),
                "pnl_pct": pnl_pct,
                "reason": str(reason or ""),
                "grade": grade,
                "score": score,
            })
        return exits

    def print_exits_ledger(self, limit: int = 50) -> None:
        """Prints a human-readable ledger of all exits stored in SQLite DB."""
        exits = self.get_exits(limit=limit)
        print("=" * 96)
        print("   📒 QUANT DESK — REALISED EXITS & SCALE-OUT DATABASE (SQLite)")
        print("=" * 96)
        if not exits:
            print("  No exits recorded in database yet.")
            print("=" * 96)
            return

        hdr = f"{'ID':<4} {'Date / Time (ET)':<18} {'Ticker':<7} {'Type':<13} {'Qty':>6} {'Entry $':>9} {'Exit $':>9} {'Realized PnL':>17}  {'Reason'}"
        print(hdr)
        print("-" * len(hdr))

        for x in exits:
            ts = x.get("closed_at") or x.get("opened_at")
            dt_str = datetime.fromtimestamp(float(ts), tz=NY_TZ).strftime("%Y-%m-%d %H:%M") if ts else "—"
            pnl_str = f"{x['pnl']:+,.2f} ({x['pnl_pct']:+.1f}%)"
            print(f"{x['id']:<4} {dt_str:<18} {x['ticker']:<7} {x['type']:<13} {x['qty']:>6.1f} {x['entry']:>9.2f} {x['exit']:>9.2f} {pnl_str:>17}  {x['reason']}")

        print("-" * len(hdr))
        st = self.stats()
        print(f"  Total Realized P&L: ${st.get('total', 0.0):+,.2f} | Win Rate: {st.get('win_rate', 0.0)}% over {st.get('n', 0)} closed clips | Open Trades: {st.get('open_trades', 0)}")
        print("=" * 96)

    def stats(self, book: Optional[str] = None) -> dict:
        conn = self._conn()
        if book:
            rows = conn.execute(
                "SELECT pnl FROM trades WHERE closed_at IS NOT NULL AND book = ?", (str(book).lower(),)
            ).fetchall()
            open_n = conn.execute(
                "SELECT COUNT(*) FROM trades WHERE closed_at IS NULL AND book = ?", (str(book).lower(),)
            ).fetchone()[0]
        else:
            rows = conn.execute(
                "SELECT pnl FROM trades WHERE closed_at IS NOT NULL").fetchall()
            open_n = conn.execute(
                "SELECT COUNT(*) FROM trades WHERE closed_at IS NULL").fetchone()[0]
        conn.close()
        out = self._wr([r[0] for r in rows]) if rows else {"closed_trades": 0}
        out["open_trades"] = open_n
        if book:
            out["book"] = str(book).lower()
        return out

    def get_current_streak(self) -> int:
        """
        Returns consecutive win (+) or loss (-) count for closed trades (Upgrade 5).
        +3 means 3 consecutive wins; -2 means 2 consecutive losses.
        """
        conn = self._conn()
        rows = conn.execute(
            "SELECT pnl FROM trades WHERE closed_at IS NOT NULL ORDER BY closed_at DESC, id DESC LIMIT 20"
        ).fetchall()
        conn.close()
        if not rows:
            return 0
        streak = 0
        first_pnl = float(rows[0][0] or 0.0)
        if first_pnl == 0.0:
            return 0
        is_win = first_pnl > 0
        for r in rows:
            pnl = float(r[0] or 0.0)
            if pnl == 0.0:
                continue
            if (pnl > 0) == is_win:
                streak += 1 if is_win else -1
            else:
                break
        return streak

    # ------------------------------------------------------------ analytics --
    @staticmethod
    def _wr(pnls: list) -> dict:
        if not pnls:
            return {"n": 0, "win_rate": None, "avg_pnl": 0.0, "total": 0.0}
        wins = [p for p in pnls if p > 0]
        return {"n": len(pnls),
                "win_rate": round(100.0 * len(wins) / len(pnls), 1),
                "avg_pnl": round(sum(pnls) / len(pnls), 2),
                "total": round(sum(pnls), 2)}

    @staticmethod
    def _bucket(hour) -> str:
        if hour is None:
            return "unknown"
        if hour < 10:
            return "pre_10am"
        if hour <= 14:
            return "core_10_15"
        return "late_after_15"

    def analytics(self) -> dict:
        """Breaks realised trades down by grade & session, then proposes
        tiny adjustments (the 'balance' step after each live session)."""
        conn = self._conn()
        rows = conn.execute(
            """SELECT ticker, pnl, closed_at, opened_at,
                      grade, style, session_hour, regime, score
               FROM trades WHERE closed_at IS NOT NULL""").fetchall()
        slip_rows = conn.execute(
            """SELECT slippage_bps FROM trades
               WHERE closed_at IS NOT NULL AND slippage_bps IS NOT NULL"""
        ).fetchall()
        conn.close()

        overall = self._wr([r[1] for r in rows])
        avg_slippage_bps = (round(sum(r[0] for r in slip_rows) / len(slip_rows), 1)
                            if slip_rows else None)
        by_grade: dict = {}
        by_session: dict = {}
        suggestions: list = []

        for ticker, pnl, closed_at, opened_at, grade, style, hour, regime, \
                score in rows:
            by_grade.setdefault(grade or "unknown", []).append(pnl)
            by_session.setdefault(self._bucket(hour), []).append(pnl)

        for g in sorted(by_grade):
            st = self._wr(by_grade[g])
            if st["n"] >= 5 and st["win_rate"] is not None and st["win_rate"] < 40.0:
                suggestions.append(
                    f"Grade {g} bleeding: WR {st['win_rate']}% over {st['n']} "
                    f"trades -> consider raising MIN_TRADE_SCORE")

        for b in ("pre_10am", "core_10_15", "late_after_15"):
            st = self._wr(by_session.get(b, []))
            if st["n"] >= 8 and st["win_rate"] is not None and st["win_rate"] < 35.0:
                suggestions.append(
                    f"{b} session bleeding: WR {st['win_rate']}% over "
                    f"{st['n']} trades -> restrict entries to core hours")

        reward_risk = None
        if overall["n"] >= 5:
            pnls = [r[1] for r in rows]
            wins = [p for p in pnls if p > 0]
            losses = [p for p in pnls if p <= 0]
            aw = sum(wins) / len(wins) if wins else 0.0
            al = abs(sum(losses) / len(losses)) if losses else 0.0
            reward_risk = round(aw / al, 2) if al else None
            if reward_risk is not None and reward_risk < 1.0:
                suggestions.append("Avg win < avg loss — review exits "
                                   "(earlier scale-out or stop placement)")

        if avg_slippage_bps is not None and len(slip_rows) >= 3 \
                and avg_slippage_bps > 25:
            suggestions.append(
                f"Slippage averaging {avg_slippage_bps:.0f} bps over "
                f"{len(slip_rows)} fills -> consider limit orders or "
                f"smaller entry clips")

        return {
            "overall": overall,
            "reward_risk": reward_risk,
            "avg_slippage_bps": avg_slippage_bps,
            "by_grade": {g: self._wr(v) for g, v in sorted(by_grade.items())},
            "by_session": {b: self._wr(v) for b, v in sorted(by_session.items())},
            "suggestions": suggestions,
        }

    def equity_curve(self) -> list:
        """Cumulative realised P&L over closed trades (chronological)."""
        conn = self._conn()
        rows = conn.execute(
            """SELECT closed_at, pnl, ticker, reason, qty, entry, exit, grade, score FROM trades
               WHERE closed_at IS NOT NULL ORDER BY closed_at""").fetchall()
        conn.close()
        cum = 0.0
        points = []
        for ts, pnl, sym, reason, qty, entry, exit_px, grade, score in rows:
            pnl_f = float(pnl or 0.0)
            cum += pnl_f
            ts_f = float(ts or 0.0)
            points.append({
                "t": datetime.fromtimestamp(ts_f).strftime("%d/%m %H:%M") if ts_f > 0 else "—",
                "ts": ts_f,
                "ticker": sym or "UNKNOWN",
                "pnl": round(pnl_f, 2),
                "cum_pnl": round(cum, 2),
                "reason": str(reason or ""),
                "qty": float(qty or 0),
                "entry": round(float(entry or 0), 2),
                "exit": round(float(exit_px or 0), 2),
                "grade": grade or "?",
            })
        return points


journal = TradeJournal()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Trade Journal v2")
    p.add_argument("--stats", action="store_true")
    p.add_argument("--exits", action="store_true",
                   help="display database table of all partial & full exits")
    p.add_argument("--analytics", action="store_true",
                   help="grade/session breakdown + tuning suggestions")
    p.add_argument("--reset", action="store_true")
    p.add_argument("--limit", type=int, default=50, help="max rows to display")
    a = p.parse_args()

    if a.reset:
        if DB_PATH.exists():
            DB_PATH.unlink()
        print("journal reset")
    elif a.exits:
        journal.print_exits_ledger(limit=a.limit)
    elif a.analytics:
        print(json.dumps(journal.analytics(), indent=2))
    else:
        print(json.dumps(journal.stats(), indent=2))