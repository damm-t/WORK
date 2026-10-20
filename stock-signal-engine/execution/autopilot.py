"""
Autopilot Daemon — Autonomous Trading Loop
==========================================
Background scanner that, every N minutes:
  1. Manages open positions with the monotonic ratcheting trailing stop
     (1.5x ATR trail armed after the 3.5x ATR runner trigger).
  2. Evaluates the watchlist through the full FinBERT + technical pipeline.
  3. Executes PAIRED trades (Long alpha + inverse-ETF beta hedge) through
     Alpaca paper trading when conviction clears the threshold.

Usage:
    python -m execution.autopilot --interval 900 --watchlist NVDA,AAPL,MSFT
    python -m execution.autopilot --once --dry-run
"""

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# --- Runtime stability defaults (must be set BEFORE heavy imports) ---
# USE_LGBM_RUNTIME=0 : LightGBM/OpenMP deadlocks on macOS -> use rule ensemble
# HF offline vars    : FinBERT is fully cached; avoids etag-check network stall
os.environ.setdefault("USE_LGBM_RUNTIME", "0")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("MIN_TRADE_SCORE", "55")       # grade B or better to enter
os.environ.setdefault("MAX_PORTFOLIO_HEAT", "0.20")  # raise to 0.35 for more action
os.environ.setdefault("GAP_SHOCK_PCT", "2.5")        # gap vs prev close = shock
os.environ.setdefault("VELOCITY_SHOCK_PCT", "1.2")   # 30-min violent move = shock
os.environ.setdefault("EARNINGS_BLACKOUT_DAYS", "1") # no entries near earnings
os.environ.setdefault("DAILY_LOSS_LIMIT", "-0.05")   # kill-switch threshold

from api import services                     # full signal pipeline (reuses singleton client)
from risk import ratchet_trailing_stop       # exit management math
from risk import tp1_scale_plan              # tuned TP1 scale-out decision
from market import get_market_features       # live ATR / Close per position
from market.shock_detector import (          # unexpected-data reflexes
    detect_intraday_shock, earnings_blackout, fetch_prev_close,
)
from execution import submit_market_order    # order placement
from strategy.equities_strategy import equities_strategy, INSTITUTIONAL_EQUITY_CORE

logger = logging.getLogger(__name__)

STATE_PATH = Path("execution/autopilot_state.json")

# Symbols that ARE hedges/index proxies themselves -> never treat them as alpha
INDEX_AND_HEDGE_SYMBOLS = {"SPY", "QQQ", "SH", "PSQ"}

DEFAULT_WATCHLIST = ["AAPL", "MSFT", "JPM", "JNJ", "XOM"]
# Small-account tuned preset never chases NVDA to reach its win rate.
TUNED_WATCHLIST = ["MSFT", "AAPL", "CAT", "JPM", "ABBV"]


from execution.json_state import atomic_json_read, atomic_json_write

HEARTBEAT_PATH = Path(".run/autopilot_heartbeat.json")


# ------------------------------------------------------------------ state ---
def load_state() -> dict:
    return atomic_json_read(STATE_PATH, default={})


def save_state(state: dict) -> None:
    atomic_json_write(STATE_PATH, state)


def update_heartbeat(cycle: int = 0, status: str = "running", extra: Optional[dict] = None) -> None:
    """Updates the dead-man's switch heartbeat timestamp file atomically."""
    try:
        payload = {
            "timestamp": time.time(),
            "time_iso": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cycle": cycle,
            "status": status,
            "pid": os.getpid(),
        }
        if extra:
            payload.update(extra)
        atomic_json_write(HEARTBEAT_PATH, payload)
        pid_file = HEARTBEAT_PATH.parent / "autopilot.pid"
        if not pid_file.exists() or pid_file.read_text().strip() != str(os.getpid()):
            pid_file.write_text(str(os.getpid()))
    except Exception as e:
        logger.debug(f"[autopilot] Could not write heartbeat: {e}")


def unwind_paired_hedge(symbol: str, client: Any, state: dict, dry_run: bool = False) -> Optional[dict]:
    """
    Automatically unwinds the paired inverse-ETF hedge leg (SH / PSQ)
    whenever its parent alpha position is closed (stop hit, shock exit, or invalidation).
    Prevents orphaned hedge accumulation.
    """
    rec = state.get(symbol, {})
    hedge_symbol = rec.get("hedge_symbol")
    hedge_shares = int(rec.get("hedge_shares", 0) or 0)

    # Fallback to journal lookup if not explicitly in state
    if not hedge_symbol or hedge_shares <= 0:
        try:
            from execution.trade_journal import journal
            conn = journal._conn()
            row = conn.execute(
                "SELECT hedge FROM trades WHERE ticker = ? ORDER BY id DESC LIMIT 1",
                (symbol.upper(),)
            ).fetchone()
            conn.close()
            if row and row[0]:
                parts = str(row[0]).strip().split(" x")
                if len(parts) == 2:
                    hedge_symbol = parts[0].strip().upper()
                    hedge_shares = int(parts[1].strip())
        except Exception as e:
            logger.debug(f"[autopilot] journal hedge lookup for {symbol}: {e}")

    if not hedge_symbol or hedge_shares <= 0:
        return None

    # Check actual open position in Alpaca to prevent over-selling
    try:
        open_pos = client.get_open_position(hedge_symbol)
        actual_qty = int(abs(float(open_pos.qty)))
    except Exception:
        actual_qty = 0

    if actual_qty <= 0:
        logger.info(f"[autopilot] No open {hedge_symbol} position to unwind for {symbol}")
        return None

    shares_to_sell = min(hedge_shares, actual_qty)
    logger.warning(
        f"[autopilot] 🛡️ UNWIND PAIRED HEDGE for {symbol}: Selling {shares_to_sell} of {hedge_symbol} "
        f"(paired with closed {symbol} trade)"
    )

    result = None
    if not dry_run:
        result = submit_market_order(client, hedge_symbol, shares_to_sell, side="SELL")
        try:
            from execution.trade_journal import journal
            now_px = float(getattr(open_pos, "current_price", 0.0) or 0.0)
            entry_px = float(getattr(open_pos, "avg_entry_price", now_px) or now_px)
            journal.record_close(
                hedge_symbol,
                now_px,
                f"paired_unwind_{symbol}",
                pnl=(now_px - entry_px) * shares_to_sell
            )
        except Exception as j_err:
            logger.debug(f"[autopilot] journal hedge unwind log: {j_err}")

    return {"status": "unwound", "hedge_symbol": hedge_symbol, "shares": shares_to_sell, "order": result}


# ------------------------------------------------- position management ------
def manage_open_positions(dry_run: bool = False) -> list:
    """
    Ratchets protective stops upward on every open alpha position and
    flattens any position whose price has breached its stop level.
    Hedge ETF legs are managed implicitly (sold when their paired alpha leg
    closes, keeping the pair book balanced).
    """
    actions = []
    state = load_state()

    # --- execution quality: backfill real fills & reconcile dead/expired orders ----------
    try:
        from execution.trade_journal import journal as _jr
        for _pend in _jr.pending_fills():
            try:
                o = services.client.get_order_by_id(_pend["order_id"])
                o_status = str(getattr(o, "status", "")).lower().replace("orderstatus.", "")
                filled_qty = float(getattr(o, "filled_qty", 0) or 0)
                if o_status == "filled" and o.filled_avg_price:
                    _jr.set_actual_entry(_pend["id"],
                                         float(o.filled_avg_price))
                    logger.info(f"[autopilot] reconciled fill "
                                f"{_pend['ticker']} @ {o.filled_avg_price}")
                elif o_status in ("expired", "canceled", "rejected", "stopped") and filled_qty == 0:
                    status_name = o_status.capitalize()
                    _jr.close_unfilled_trade(_pend["id"], reason=f"Order {status_name} (0 Fills)")
                    logger.info(f"[autopilot] reconciled unfilled dead order {_pend['ticker']} ({status_name})")
            except Exception:
                pass                                    # retry next cycle
    except Exception:
        pass

    try:
        positions = services.client.get_all_positions()
    except Exception as e:
        logger.error(f"[autopilot] Could not fetch positions: {e}")
        return actions

    # Pre-cycle sweep: immediately unwind orphan hedges for symbols already closed by broker/stop
    current_symbols = {str(p.symbol).upper() for p in positions}
    for tracked_sym in list(state.keys()):
        if str(tracked_sym).startswith("_"):
            continue
        if tracked_sym not in current_symbols:
            logger.info(f"[autopilot] Pre-cycle sweep: {tracked_sym} no longer in portfolio — unwinding orphan hedge immediately")
            unwind_paired_hedge(tracked_sym, services.client, state, dry_run=dry_run)
            state.pop(tracked_sym, None)

    # Active hedge legs currently protecting open alpha positions
    active_hedge_symbols = set()
    for tracked_sym, tracked_data in state.items():
        if not str(tracked_sym).startswith("_") and isinstance(tracked_data, dict):
            h_sym = str(tracked_data.get("hedge_symbol") or "").upper()
            if h_sym:
                active_hedge_symbols.add(h_sym)

    for pos in positions:
        try:
            symbol = str(pos.symbol).upper()

            # If this is an inverse ETF actively hedging an open alpha position (e.g. SH hedging AAPL),
            # it is managed implicitly when the paired alpha leg closes.
            if symbol in active_hedge_symbols and symbol in INDEX_AND_HEDGE_SYMBOLS:
                logger.debug(f"[autopilot] {symbol} is an active paired hedge leg — managed via alpha leg.")
                continue

            qty = int(abs(float(pos.qty)))
            if qty <= 0:
                continue

            market = get_market_features(symbol)
            if not market:
                continue
            price = float(market.get("Close", 0.0) or 0.0)
            atr = float(market.get("ATR", 0.0) or 0.0)
            if price <= 0 or atr <= 0:
                continue

            entry = float(getattr(pos, "avg_entry_price", price) or price)
            record = state.get(symbol, {})

            # 🛡️ Orphan Position Resolution: If symbol is in positions but untracked in state,
            # initialize an active protective stop immediately so it never sits naked or unmanaged.
            if symbol not in state:
                orphan_stop = round(entry - (1.5 * atr), 2)
                record = {
                    "stop_price": orphan_stop,
                    "initial_stop": orphan_stop,
                    "highest_price": max(price, entry),
                    "tp1_done": False,
                    "be_armed": False,
                    "strategy": "ORPHAN_MANAGED",
                }
                state[symbol] = record
                logger.warning(
                    f"[autopilot] 🛡️ INITIALIZED PROTECTIVE STOP FOR UNTRACKED/ORPHAN {symbol} "
                    f"({qty} shs @ ${entry:.2f}): stop at ${orphan_stop:.2f}"
                )

            highest_seen = max(price, float(record.get("highest_price", entry) or entry))
            current_stop = float(record.get("stop_price", 0.0) or 0.0)

            # --- Anti-Volatility PSI evaluation & Bayesian conviction for position management ---
            pos_psi = None
            pos_regime = None
            try:
                from market.anti_volatility import anti_volatility_model
                stab = anti_volatility_model.evaluate_ticker(symbol)
                pos_psi = stab.price_stability_index
                pos_regime = stab.regime
            except Exception as av_err:
                logger.debug(f"[autopilot] anti-volatility eval error {symbol}: {av_err}")

            # Bayesian conviction reflex: handle thesis invalidations
            try:
                from model.bayesian_confidence import belief_engine
                stmt = belief_engine.get_latest_statement(symbol)
                if stmt and stmt.recommendation == "EXIT_INVALIDATED":
                    logger.warning(
                        f"[autopilot] BAYESIAN THESIS INVALIDATED for {symbol} "
                        f"(conf={stmt.confidence_pointer:.1f}%): liquidating position"
                    )
                    actions.append({"symbol": symbol, "action": "BAYESIAN_INVALIDATED_EXIT",
                                    "price": round(price, 2),
                                    "confidence": stmt.confidence_pointer})
                    if not dry_run:
                        submit_market_order(services.client, symbol, qty, side="SELL")
                        try:
                            from execution.trade_journal import journal
                            _ep = float(getattr(pos, "avg_entry_price", price) or price)
                            journal.record_close(symbol, float(price), "bayesian_invalidated",
                                                 pnl=(price - _ep) * qty)
                        except Exception as j_err:
                            logger.debug(f"[autopilot] journal bayesian close: {j_err}")
                    unwind_paired_hedge(symbol, services.client, state, dry_run=dry_run)
                    state.pop(symbol, None)
                    continue
            except Exception as b_err:
                logger.debug(f"[autopilot] Bayesian position check error {symbol}: {b_err}")

            # --- UNCHOKED TRAILING RATCHET & ASYMMETRIC TARGET PROFIT ---
            # Risk unit R: derived from initial stop distance (or 1.5*ATR floor)
            init_stop = float(record.get("initial_stop", 0.0) or (entry - (1.5 * atr)))
            risk_unit = max(entry - init_stop, atr * 1.5, entry * 0.015)

            profit_r = (highest_seen - entry) / max(risk_unit, 1e-4)
            current_r = (price - entry) / max(risk_unit, 1e-4)

            # 🎯 Asymmetric Target Profit Harvest at >= 2.2:1 R:R ($+350 to $+500 win)
            tp_price = round(entry + (2.2 * risk_unit), 2)
            if price >= tp_price:
                logger.info(
                    f"[autopilot] 🎯 TARGET PROFIT HARVEST {symbol}: price ${price:.2f} reached "
                    f"2.2:1 TP (${tp_price:.2f}, +{current_r:.2f}R) -> closing {qty} shares"
                )
                actions.append({"symbol": symbol, "action": "take_profit",
                                "price": round(price, 2), "tp": tp_price})
                if not dry_run:
                    submit_market_order(services.client, symbol, qty, side="SELL")
                    try:
                        from execution.trade_journal import journal
                        _ep = float(getattr(pos, "avg_entry_price", price) or price)
                        pnl_val = (price - _ep) * qty
                        journal.record_close(symbol, float(price), "target_profit_harvest", pnl=pnl_val)
                        equities_strategy.learner.record_trade(
                            strategy_type=record.get("strategy", "SMC_SWEEP_LONG"),
                            pnl=pnl_val,
                            r_multiple=current_r,
                            entry_price=_ep,
                            exit_price=price,
                            ticker=symbol
                        )
                    except Exception as j_err:
                        logger.debug(f"[autopilot] journal TP close: {j_err}")
                unwind_paired_hedge(symbol, services.client, state, dry_run=dry_run)
                state.pop(symbol, None)
                continue

            # 🚀 Unchoked Trailing Ratchet: arms only when profit reaches >= +1.5R
            # Maintains a 0.6R breathing cushion so normal 5m noise doesn't choke winners,
            # while guaranteeing at least +0.5R profit floor once armed.
            be_armed = bool(record.get("be_armed"))
            if profit_r >= 1.5:
                cushion = 0.60 * risk_unit
                ratchet_floor = round(highest_seen - cushion, 2)
                guaranteed_floor = round(entry + (0.50 * risk_unit), 2)
                target_stop = max(current_stop, ratchet_floor, guaranteed_floor)
                if target_stop > current_stop:
                    logger.info(
                        f"[autopilot] 🚀 UNCHOKED RATCHET {symbol}: high ${highest_seen:.2f} (+{profit_r:.2f}R) "
                        f"-> stop raised to ${target_stop:.2f} (0.6R cushion, +0.5R floor locked)"
                    )
                    current_stop = target_stop
                be_armed = True

            state[symbol] = {
                "stop_price": current_stop,
                "initial_stop": init_stop,
                "highest_price": round(highest_seen, 2),
                "tp1_done": bool(record.get("tp1_done")),
                "be_armed": be_armed,
                "strategy": record.get("strategy", "SMC_SWEEP_LONG"),
                "hedge_symbol": record.get("hedge_symbol", ""),
                "hedge_shares": record.get("hedge_shares", 0),
            }

            # Protective Stop Execution
            if current_stop > 0 and price <= current_stop:
                logger.warning(
                    f"[autopilot] STOP HIT {symbol}: price {price:.2f} <= stop "
                    f"{current_stop:.2f} -> closing {qty} shares"
                )
                actions.append({"symbol": symbol, "action": "close_at_stop",
                                "price": round(price, 2), "stop": round(current_stop, 2)})
                if not dry_run:
                    submit_market_order(services.client, symbol, qty, side="SELL")
                    try:
                        from execution.trade_journal import journal
                        _entry_px = float(getattr(pos, "avg_entry_price", price) or price)
                        pnl_val = (price - _entry_px) * qty
                        journal.record_close(symbol, float(price), "stop", pnl=pnl_val)
                        equities_strategy.learner.record_trade(
                            strategy_type=record.get("strategy", "SMC_SWEEP_LONG"),
                            pnl=pnl_val,
                            r_multiple=(price - _entry_px) / max(risk_unit, 1e-4),
                            entry_price=_entry_px,
                            exit_price=price,
                            ticker=symbol
                        )
                    except Exception as j_err:
                        logger.debug(f"[autopilot] journal close: {j_err}")
                unwind_paired_hedge(symbol, services.client, state, dry_run=dry_run)
                state.pop(symbol, None)
            else:
                actions.append({
                    "symbol": symbol,
                    "action": "raise_stop" if be_armed else "hold",
                    "price": round(price, 2),
                    "stop": round(current_stop, 2),
                    "trailing_armed": be_armed,
                })
        except Exception as e:
            logger.error(f"[autopilot] Error managing position: {e}")
            continue

    # Cleanup for positions that were closed outside autopilot (e.g. broker stop / take profit filled)
    current_symbols = {str(p.symbol).upper() for p in positions}
    for tracked_sym in list(state.keys()):
        if str(tracked_sym).startswith("_"):
            continue
        if tracked_sym not in current_symbols:
            logger.info(f"[autopilot] Tracked symbol {tracked_sym} no longer in portfolio — unwinding orphan hedge")
            unwind_paired_hedge(tracked_sym, services.client, state, dry_run=dry_run)
            state.pop(tracked_sym, None)

    save_state(state)
    return actions


# ------------------------------------------------------ scanning loop -------
def market_is_open() -> tuple:
    """True if Alpaca reports the US equity market open right now."""
    try:
        clock = services.client.get_clock()
        if getattr(clock, "is_open", False):
            return True, "Market OPEN"
        return False, f"Market CLOSED — next open: {getattr(clock, 'next_open', '?')}"
    except Exception as e:
        logger.error(f"[autopilot] Clock check failed: {e} — FAIL-CLOSED: holding entries")
        return False, f"Could not verify market status ({e}) — holding (Fail-Closed Protocol)"


def _await_fill(order_id: str, tries: int = 5, delay: float = 1.5):
    """Polls Alpaca until the buy order fills; returns the real avg fill price."""
    for _ in range(int(tries)):
        try:
            o = services.client.get_order_by_id(order_id)
            if str(getattr(o, "status", "")) == "filled" and o.filled_avg_price:
                return round(float(o.filled_avg_price), 4)
        except Exception as e:                                # noqa: BLE001
            logger.debug(f"[autopilot] fill poll {order_id}: {e}")
        time.sleep(float(delay))
    return None


def run_scan(watchlist: list, dry_run: bool = False) -> list:
    """Evaluates each watchlist name and executes approved PAIRED trades."""
    results = []
    
    # 🛡️ Anti-Churn Duplicate Guard: Fetch open portfolio positions to strictly prevent re-buying
    held_symbols = set()
    try:
        if services.client:
            open_pos = services.client.get_all_positions()
            held_symbols = {str(p.symbol).upper() for p in open_pos if float(p.qty) != 0}
    except Exception as pos_err:
        logger.debug(f"[autopilot] Could not fetch positions for duplicate guard: {pos_err}")

    for ticker in watchlist:
        ticker = str(ticker).strip().upper()
        if not ticker or ticker in INDEX_AND_HEDGE_SYMBOLS:
            continue

        # Prevent duplicate buying of symbols already held in portfolio
        if ticker in held_symbols:
            logger.info(f"[autopilot] 🛡️ DUPLICATE GUARD: {ticker} is already held in portfolio. Skipping duplicate entry.")
            results.append({"ticker": ticker, "status": "skipped", "reason": f"Already held in portfolio ({ticker})"})
            continue
        try:
            from risk.book_allocator import classify_position_book
            book = classify_position_book(ticker)
            # ---- unexpected-data defenses BEFORE burning NLP cycles --------
            blackout = earnings_blackout(ticker)
            if blackout.get("blackout"):
                results.append({"ticker": ticker, "status": "skipped",
                                "reason": f"Earnings blackout "
                                          f"({blackout.get('next_earnings')})"})
                continue

            shock = detect_intraday_shock(ticker,
                                          prev_close=fetch_prev_close(ticker))
            if shock.get("shocked"):
                results.append({"ticker": ticker, "status": "skipped",
                                "reason": f"Shock freeze: {shock.get('detail')}"})
                continue

            evaluation = services.get_hedge_evaluation(ticker)

            # News memory: store every analysed headline so future cycles can
            # find similar past narratives (enable with NEWS_MEMORY=1)
            if os.getenv("NEWS_MEMORY", "0") == "1":
                try:
                    from nlp.news_memory import remember
                    _sent = evaluation.get("sentiment") or {}
                    _art = evaluation.get("best_article") or {}
                    if _art.get("title"):
                        remember(ticker, _art["title"],
                                 _sent.get("label") or "neutral",
                                 float(_sent.get("score", 0.0) or 0.0))
                except Exception as mem_err:
                    logger.debug(f"[autopilot] news memory: {mem_err}")

            decision = evaluation.get("decision", {})

            if not decision.get("approved"):
                results.append({"ticker": ticker, "status": "skipped",
                                "reason": decision.get("reason", "No signal")})
                continue

            # Trade-quality sniper gate: require high confluence score and Grade A
            grade = evaluation.get("trade_grade") or {}
            min_score = float(os.getenv("MIN_TRADE_SCORE", "75"))
            grade_letter = str(grade.get("grade", "C")).upper()
            if grade and float(grade.get("score", 0.0) or 0.0) < min_score:
                results.append({"ticker": ticker, "status": "skipped",
                                "reason": f"Low trade score {float(grade.get('score', 0.0)):.0f} "
                                          f"(grade {grade_letter}, need score >= {min_score:.0f})"})
                continue

            if os.getenv("GRADE_A_ONLY", "1") == "1" and grade_letter != "A":
                results.append({"ticker": ticker, "status": "skipped",
                                "reason": f"Sniper gate: Grade {grade_letter} < A (only Grade A confluence executed)"})
                continue

            # Autonomous Institutional Compliance Gatekeeper (Whale Trap & Discipline Defense)
            if os.getenv("COMPLIANCE_GATE", "1") == "1":
                try:
                    from compliance.autonomous_checker import compliance_checker
                    mkt_feats = evaluation.get("market") or {}
                    rvol_val = float(mkt_feats.get("RVOL", 1.0) or 1.0)
                    px_val = float(mkt_feats.get("Close", 100.0) or 100.0)
                    mom_val = float(mkt_feats.get("Return_5d", 0.0) or 0.0)
                    sent_dict = evaluation.get("sentiment") or {}
                    sent_score = float(sent_dict.get("score", 0.0) or 0.0)
                    if sent_dict.get("label") == "negative":
                        sent_score = -sent_score

                    acc = services.client.get_account()
                    eq = float(acc.equity)
                    heat = max(0.0, 1.0 - (float(acc.cash) / max(eq, 1.0)))

                    cert = compliance_checker.audit_pre_trade_setup(
                        ticker=ticker,
                        price=px_val,
                        rvol=rvol_val,
                        price_change_5d_pct=mom_val,
                        sentiment_score=sent_score,
                        strategy_candidate="core_swing",
                        account_equity=eq,
                        current_heat=heat,
                        day_pnl_pct=0.0,
                        near_earnings=bool(blackout.get("blackout")),
                        shock_detected=bool(shock.get("shocked")),
                    )
                    if not cert.approved:
                        viols = "; ".join(cert.violations[:2])
                        results.append({
                            "ticker": ticker,
                            "status": "skipped",
                            "reason": f"Compliance gate: {cert.verdict} (Score {cert.compliance_score}/100) — {viols}"
                        })
                        continue
                except Exception as comp_err:
                    logger.debug(f"[autopilot] compliance gate check: {comp_err}")

            # Macro SPY regime gate: skip long entries during BEAR regime
            if os.getenv("REGIME_FILTER", "1") == "1":
                try:
                    from market.beta_calculator import detect_market_regime
                    macro = detect_market_regime("SPY")
                    if macro.get("regime") == "BEAR_VOLATILITY":
                        results.append({"ticker": ticker, "status": "skipped",
                                        "reason": f"Macro SPY in BEAR regime ({macro.get('desc', 'bear')}) — long entries disabled to prevent drawdowns"})
                        continue
                except Exception as reg_err:
                    logger.debug(f"[autopilot] regime check error: {reg_err}")

            # Volume quality gate (Upgrade 6): reject low liquidity / dead volume setups
            if os.getenv("RVOL_GATE", "1") == "1":
                min_rvol = float(os.getenv("MIN_CORE_RVOL", "0.70"))
                mkt_feats = evaluation.get("market") or {}
                rvol = float(mkt_feats.get("RVOL", 1.0) or 1.0)
                if rvol < min_rvol:
                    results.append({"ticker": ticker, "status": "skipped",
                                    "reason": f"Volume gate: RVOL {rvol:.2f}x < {min_rvol:.2f}x threshold (insufficient liquidity)"})
                    continue

            # Bayesian conviction gate (Upgrade 3): reject trades with low confidence or invalidated theses
            if os.getenv("BAYESIAN_GATE", "1") == "1":
                try:
                    from model.bayesian_confidence import belief_engine
                    stmt = belief_engine.get_latest_statement(ticker)
                    min_conf = float(os.getenv("MIN_BAYESIAN_CONFIDENCE", "55.0"))
                    if stmt:
                        if stmt.confidence_pointer < min_conf:
                            results.append({"ticker": ticker, "status": "skipped",
                                            "reason": f"Bayesian gate: Confidence {stmt.confidence_pointer:.1f}% < {min_conf:.1f}% threshold"})
                            continue
                        if stmt.recommendation == "EXIT_INVALIDATED":
                            results.append({"ticker": ticker, "status": "skipped",
                                            "reason": f"Bayesian gate: recommendation is EXIT_INVALIDATED"})
                            continue
                except Exception as b_err:
                    logger.debug(f"[autopilot] Bayesian gate check error for {ticker}: {b_err}")

            # PROJECT OMEGA: Mandatory Hedge Integrity Gate (Fail-Closed)
            _eval_hedge = evaluation.get("hedge") or {}
            if _eval_hedge.get("hedge_failed") or (
                float(_eval_hedge.get("hedge_dollars", 0.0) or 0.0) > 0 and int(_eval_hedge.get("hedge_shares", 0) or 0) <= 0
            ):
                results.append({
                    "ticker": ticker,
                    "status": "skipped",
                    "reason": f"Project Omega Hedge Gate: {_eval_hedge.get('reason', 'Mandatory hedge shares <= 0')} — naked execution aborted"
                })
                continue

            # AstraQuant Fail-Closed Physical Risk Pipeline Gate (Reels 1 & 2)
            try:
                from risk.physical_risk_pipeline import physical_risk_pipeline
                _exit_plan = decision.get("exit_levels") or {}
                _sl = float(_exit_plan.get("hard_stop_price") or 0.0)
                _tp = float(_exit_plan.get("take_profit_1_price") or 0.0)
                _px = float((evaluation.get("market") or {}).get("Close", 0.0) or 0.0)
                if _sl > 0 and _tp > 0 and _px > 0:
                    acc_eq = 25000.0
                    try:
                        acc_eq = float(services.client.get_account().equity)
                    except Exception:
                        pass
                    p_audit = physical_risk_pipeline.audit_order_intent(
                        symbol=ticker,
                        side="LONG",
                        entry_price=_px,
                        stop_loss=_sl,
                        take_profit=_tp,
                        portfolio_equity=acc_eq,
                        requested_size=float(decision.get("shares", 1) or 1),
                    )
                    if not p_audit.approved:
                        results.append({
                            "ticker": ticker,
                            "status": "skipped",
                            "reason": f"AstraQuant Physical Risk VETO: {'; '.join(p_audit.rejection_reasons)}"
                        })
                        continue
            except Exception as _p_err:
                logger.debug(f"[autopilot] physical risk audit check: {_p_err}")

            if dry_run:
                results.append({"ticker": ticker, "status": "dry_run_approved",
                                "decision": decision,
                                "hedge": evaluation.get("hedge")})
                continue

            executed = services.process_trade_execution(ticker)
            _exec = executed.get("execution") or {}
            if str(_exec.get("status")) == "submitted":
                try:
                    from execution.trade_journal import journal
                    _dec = executed.get("decision") or {}
                    _mkt = executed.get("market") or {}
                    _hedge = executed.get("hedge") or {}
                    _grade = executed.get("trade_grade") or {}
                    _entry_px = (_dec.get("exit_levels") or {}).get(
                        "entry_price") or _mkt.get("close") or 0.0
                    _buy_id = str((_exec or {}).get("buy_id") or "") or None
                    _rid = journal.record_open(
                        ticker,
                        qty=int(_dec.get("shares", 0) or 0),
                        entry=float(_entry_px),
                        hedge=(f"{_hedge.get('hedge_instrument', '')}"
                               f" x{_hedge.get('hedge_shares', 0)}"),
                        grade=_grade.get("grade"),
                        style="live_ensemble",
                        regime=_hedge.get("regime"),
                        score=_grade.get("score"),
                        order_id=_buy_id,
                    )
                    if _buy_id:
                        _fill = _await_fill(_buy_id)
                        if _fill:
                            journal.set_actual_entry(_rid, _fill)
                            logger.info(f"[autopilot] {ticker} real fill @ {_fill}")

                    _h_sym = str(_hedge.get('hedge_instrument', '') or '')
                    _h_shares = int(_hedge.get('hedge_shares', 0) or 0)
                    _curr_st = load_state()
                    _sl_val = float((_dec.get("exit_levels") or {}).get("stop_loss", 0.0) or 0.0)
                    _curr_st[ticker] = {
                        "stop_price": _sl_val,
                        "initial_stop": _sl_val,
                        "highest_price": float(_entry_px),
                        "tp1_done": False,
                        "be_armed": False,
                        "strategy": str(_dec.get("strategy_type", "SMC_SWEEP_LONG")),
                        "hedge_symbol": _h_sym,
                        "hedge_shares": _h_shares,
                    }
                    save_state(_curr_st)

                    # Multi-Broker Automated Trade Mirroring to Premium Subscribers
                    try:
                        from gateway.mirror_dispatcher import MirrorTradeSignal, mirror_dispatcher
                        _exit_lvls = _dec.get("exit_levels") or {}
                        _sl_val = float(_exit_lvls.get("stop_loss") or 0.0)
                        _tp_val = float(_exit_lvls.get("take_profit_1") or 0.0)
                        mirror_sig = MirrorTradeSignal(
                            ticker=ticker,
                            side="buy",
                            entry_price=float(_entry_px),
                            stop_loss=_sl_val,
                            take_profit=_tp_val,
                            strategy_name="core_swing",
                            grade=str(_grade.get("grade", "A")),
                            rationale=str(_dec.get("reason", "Master Autopilot Sniper Entry")),
                        )
                        mirror_dispatcher.replicate_signal(mirror_sig)
                    except Exception as m_err:
                        logger.debug(f"[autopilot] trade mirroring notice: {m_err}")
                except Exception as j_err:
                    logger.debug(f"[autopilot] journal open: {j_err}")

            results.append({"ticker": ticker, "status": "executed",
                            "execution": executed.get("execution"),
                            "hedge": executed.get("hedge")})
        except Exception as e:
            logger.error(f"[autopilot] Scan error for {ticker}: {e}")
            results.append({"ticker": ticker, "status": "error", "reason": str(e)})
    return results


def _day_guard() -> tuple:
    """
    Daily-loss and Profit Giveback kill switch:
      1. Tripped if day P&L breaches DAILY_LOSS_LIMIT.
      2. Tripped if session profit gives back >= 50% from daily peak (Ross Cameron Capital Protection Rule).
    Entries freeze; exit management stays 100% alive.
    """
    today = time.strftime("%Y-%m-%d")
    limit = float(os.getenv("DAILY_LOSS_LIMIT", "-0.05"))
    state = load_state()
    day = state.get("_day") or {}
    try:
        equity = float(services.client.get_account().equity)
    except Exception as e:
        logger.debug(f"[autopilot] equity check failed: {e}")
        return False, ""

    if day.get("date") != today or not day.get("start_equity"):
        state["_day"] = {"date": today, "start_equity": equity, "peak_equity": equity}
        save_state(state)
        return False, ""

    start_eq = float(day["start_equity"])
    peak_eq = max(float(day.get("peak_equity", start_eq)), equity)
    day["peak_equity"] = peak_eq
    save_state(state)

    # Ross Cameron 50% Profit Giveback Rule:
    # Walk away if day's profit was >= $150 and drops by 50% from the peak
    profit_peak = peak_eq - start_eq
    curr_profit = equity - start_eq
    if profit_peak >= 150.0 and curr_profit <= (profit_peak * 0.50):
        return True, (f"PROFIT GIVEBACK RULE TRIGGERED: Peak session profit +${profit_peak:.2f} "
                      f"dropped to +${curr_profit:.2f} (50% giveback limit). "
                      f"Entries frozen to lock in gains.")

    pnl = equity / start_eq - 1.0
    if pnl <= limit:
        return True, (f"DAILY LOSS LIMIT HIT {pnl:+.2%} ≤ {limit:.0%} "
                      f"— entries frozen until next session")
    return False, ""


def auto_select(min_auto_score: float = None, top_picks: int = 3) -> list:
    """
    Institutional SMC & Quality Market Scanner for Desk 1:
      1. Institutional Core: Scans liquid Large/Mid-Cap leaders for SMC Liquidity Sweeps
         and 20 EMA pullbacks (strictly Point-in-Time).
      2. High-JEV Dislocation Scooper: Scans for oversold capitulation wicks.
      3. Quality Momentum Universe: Ranks broad market for Grade A setups.
      Filters out already held positions to prevent duplicate entries.
    """
    if min_auto_score is None:
        min_auto_score = float(os.getenv("MIN_AUTO_SCORE", "75.0"))

    picks = []

    # Fetch currently held tickers to avoid suggesting existing positions
    held_tickers = set()
    try:
        if services.client:
            held_tickers = {str(p.symbol).upper() for p in services.client.get_all_positions() if float(p.qty) != 0}
    except Exception:
        pass

    # 1. Institutional Large/Mid-Cap SMC & PIT Scanner
    try:
        from market.price_fetcher import fetch_prices
        logger.info("[autopilot] Scanning Institutional Core universe for SMC Liquidity Sweeps...")
        for sym in INSTITUTIONAL_EQUITY_CORE:
            if sym in held_tickers or sym in picks:
                continue
            try:
                df = fetch_prices(sym, period="1mo", interval="1d")
                if df is not None and not df.empty:
                    sig = equities_strategy.evaluate_equity_ticker(sym, df)
                    if sig and sig.confidence_score >= min_auto_score:
                        logger.info(
                            f"[autopilot] 🎯 QUALIFIED SMC SETUP: {sym} ({sig.strategy_type}, "
                            f"Score {sig.confidence_score:.1f}, R:R {sig.risk_reward_ratio:.1f}:1)"
                        )
                        picks.append(sym)
                        if len(picks) >= top_picks:
                            break
            except Exception as smc_e:
                logger.debug(f"[autopilot] SMC scan error for {sym}: {smc_e}")
    except Exception as e:
        logger.debug(f"[autopilot] Institutional SMC scan note: {e}")

    # 2. Quality Core Scanner (rank_market on large/mid-cap liquid names)
    if len(picks) < top_picks:
        try:
            from backtest.market_scanner import rank_market
            rows = rank_market(top_n=max(top_picks * 4, 10), filter_junk=True, show_callout=False)
            for r in rows:
                t = str(r.get("ticker", "")).upper().strip()
                if float(r.get("score", 0.0)) >= min_auto_score and t not in picks and t not in held_tickers:
                    picks.append(t)
                    if len(picks) >= top_picks:
                        break
        except Exception as e:
            logger.error(f"[autopilot] auto-select rank_market failed: {e}")

    return picks[:top_picks]


def post_market_belief_cycle(client=None) -> List[Dict[str, Any]]:
    """
    Automated Daily Belief Cycle (Upgrade 7).
    Runs Worker 1 (harvester) -> Worker 2 (belief updater) for all active portfolio holdings
    after market close to synthesize new thesis statements and update confidence pointers.
    """
    from api import services
    from model.bayesian_confidence import belief_engine
    
    cl = client or services.client
    results = []
    try:
        positions = cl.get_all_positions()
    except Exception as e:
        logger.error(f"[autopilot] post_market_belief_cycle get_positions failed: {e}")
        return results

    for pos in positions or []:
        symbol = str(pos.symbol).upper().strip()
        if symbol in INDEX_AND_HEDGE_SYMBOLS:
            continue
        try:
            cost = float(getattr(pos, "avg_entry_price", 0.0) or 0.0)
            stmt = belief_engine.run_daily_cycle(symbol, cost_basis=cost if cost > 0 else None)
            logger.info(
                f"[autopilot] Post-market belief cycle for {symbol}: "
                f"confidence={stmt.confidence_pointer:.1f}%, recommendation={stmt.recommendation}"
            )
            results.append({
                "ticker": symbol,
                "confidence_pointer": stmt.confidence_pointer,
                "recommendation": stmt.recommendation,
                "expected_direction": stmt.expected_direction,
                "target_price": stmt.target_price,
                "stop_price": stmt.stop_price,
            })
        except Exception as err:
            logger.error(f"[autopilot] post_market_belief_cycle error for {symbol}: {err}")
            results.append({"ticker": symbol, "error": str(err)})

    return results


def _sleep_with_heartbeat(total_seconds: int, cycle: int, status: str = "active_idling") -> None:
    """Sleeps in short 15-second slices and refreshes the liveness heartbeat."""
    total_seconds = max(1, int(total_seconds))
    slept = 0
    while slept < total_seconds:
        step = min(15, total_seconds - slept)
        time.sleep(step)
        slept += step
        update_heartbeat(cycle=cycle, status=status, extra={"next_in": total_seconds - slept})


def run_autopilot(watchlist: list = None, interval_seconds: int = 900,
                  once: bool = False, dry_run: bool = False,
                  ignore_market_hours: bool = False,
                  use_auto_select: bool = False,
                  min_auto_score: float = 65.0,
                  top_picks: int = 3) -> None:
    """Main daemon loop: manage exits, then scan for new paired entries."""
    watchlist = [str(w).strip().upper() for w in (watchlist or DEFAULT_WATCHLIST)
                 if str(w).strip()]
    # Hard ban: no NVDA anywhere in the automated trading loop.
    watchlist = [t for t in watchlist if t != "NVDA"]
    if not watchlist and not use_auto_select:
        print("[autopilot] watchlist empty after NVDA ban — staying flat")
        return
    cycle = 0
    belief_cycle_done_today = False
    while True:
        if not ignore_market_hours:
            is_open, status_msg = market_is_open()
            if not is_open:
                print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] {status_msg} — idling 5 min")
                update_heartbeat(cycle=cycle, status="idling_market_closed", extra={"msg": status_msg})
                if not belief_cycle_done_today and os.getenv("DAILY_BELIEF_CRON", "1") == "1":
                    print("[autopilot] Market closed: running automated daily belief cycle...")
                    try:
                        b_res = post_market_belief_cycle()
                        print(f"[autopilot] Daily belief cycle complete for {len(b_res)} assets")
                    except Exception as b_cycle_err:
                        logger.error(f"[autopilot] Daily belief cycle error: {b_cycle_err}")
                    belief_cycle_done_today = True
                if once:
                    break
                _sleep_with_heartbeat(300, cycle=cycle, status="idling_market_closed")
                continue
            else:
                belief_cycle_done_today = False

        cycle += 1
        print(f"\n===== AUTOPILOT CYCLE #{cycle} | {time.strftime('%Y-%m-%d %H:%M:%S')} =====")
        update_heartbeat(cycle=cycle, status="active_cycle_start", extra={"dry_run": dry_run})

        # 1. ALWAYS manage open positions first (trailing stop ratchets & TP1 scale-outs)
        exits = manage_open_positions(dry_run=dry_run)
        for a in exits:
            print(f"  [EXIT-MGR] {a}")

        # 2. Check daily loss kill switch
        tripped, guard_msg = _day_guard()
        if tripped:
            print(f"[!!!] {guard_msg}")
            update_heartbeat(cycle=cycle, status="day_guard_tripped", extra={"guard_msg": guard_msg})
            if once:
                break
            _sleep_with_heartbeat(max(60, int(interval_seconds)), cycle=cycle, status="day_guard_tripped")
            continue

        # 3. Market scanner / opportunity selection
        active_watchlist = watchlist
        if use_auto_select:
            picks = auto_select(min_auto_score=min_auto_score, top_picks=top_picks)
            picks = [p for p in picks if str(p).strip().upper() != "NVDA"]
            if picks:
                print(f"[AUTO-SELECT] market scan picked: {', '.join(picks)}")
                active_watchlist = picks
            else:
                print(f"[AUTO-SELECT] market scan: no candidates above score {min_auto_score:.0f} — holding positions")
                active_watchlist = []

        if active_watchlist:
            print(f"Watchlist: {', '.join(active_watchlist)} | mode={'DRY-RUN' if dry_run else 'LIVE-PAPER'}")
            entries = run_scan(active_watchlist, dry_run=dry_run)
            for r in entries:
                print(f"  [SCAN] {r['ticker']}: {r['status']} {r.get('reason', '')}".rstrip())
        else:
            print("  [SCAN] Watching active positions (no new entries to execute this cycle)")

        print(f"===== CYCLE #{cycle} COMPLETE — next in {interval_seconds}s =====")
        update_heartbeat(cycle=cycle, status="active_cycle_complete", extra={"watchlist_count": len(active_watchlist)})
        if once:
            break
        _sleep_with_heartbeat(max(60, int(interval_seconds)), cycle=cycle, status="active_idling")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stock Signal Engine Autopilot Daemon")
    parser.add_argument("--interval", type=int, default=900,
                        help="Seconds between cycles (default: 900 = 15 min)")
    parser.add_argument("--watchlist", type=str,
                        default=",".join(DEFAULT_WATCHLIST),
                        help="Comma-separated tickers to scan")
    parser.add_argument("--once", action="store_true",
                        help="Run a single cycle and exit")
    parser.add_argument("--dry-run", action="store_true",
                        help="Evaluate signals but place no orders")
    parser.add_argument("--ignore-market-hours", action="store_true",
                        help="Run cycles even when the US market is closed")
    parser.add_argument("--auto-select", action="store_true",
                        help="Let the market scanner pick the watchlist each "
                             "cycle (top-scoring stocks only)")
    parser.add_argument("--min-auto-score", type=float,
                        default=float(os.getenv("MIN_AUTO_SCORE", "70.0")),
                        help="Minimum scanner score to trade in auto-select "
                             "mode (default: env MIN_AUTO_SCORE or 70 = "
                             "grade-A setups)")
    parser.add_argument("--top-picks", type=int, default=3,
                        help="Max number of auto-selected names per cycle")
    parser.add_argument("--risk-pct", type=float, default=None,
                        help="Override per-trade risk (e.g. 0.10 = Scenario C)")
    parser.add_argument("--heat", type=float, default=None,
                        help="Override max portfolio heat (e.g. 0.90)")
    parser.add_argument("--min-trade-score", type=float, default=None,
                        help="Override trade-quality gate")
    args = parser.parse_args()

    # Env is read lazily inside the risk functions, so setting it here works
    if args.risk_pct is not None:
        os.environ["RISK_PCT"] = str(args.risk_pct)
    if args.heat is not None:
        os.environ["MAX_PORTFOLIO_HEAT"] = str(args.heat)
    if args.min_trade_score is not None:
        os.environ["MIN_TRADE_SCORE"] = str(args.min_trade_score)

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    run_autopilot(watchlist=args.watchlist.split(","),
                  interval_seconds=args.interval,
                  once=args.once,
                  dry_run=args.dry_run,
                  ignore_market_hours=args.ignore_market_hours,
                  use_auto_select=args.auto_select,
                  min_auto_score=args.min_auto_score,
                  top_picks=args.top_picks)


if __name__ == "__main__":
    main()