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
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
        if tracked_sym == "_day":
            continue
        if tracked_sym not in current_symbols:
            logger.info(f"[autopilot] Pre-cycle sweep: {tracked_sym} no longer in portfolio — unwinding orphan hedge immediately")
            unwind_paired_hedge(tracked_sym, services.client, state, dry_run=dry_run)
            state.pop(tracked_sym, None)

    for pos in positions:
        try:
            symbol = str(pos.symbol).upper()
            if symbol in INDEX_AND_HEDGE_SYMBOLS:
                continue

            from risk.book_allocator import classify_position_book
            if classify_position_book(symbol) == "momentum":
                actions.append({"symbol": symbol, "action": "bracket_managed", "book": "momentum"})
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

            # --- unexpected-move reflex: check for shock BEFORE managing ---
            try:
                _pc = fetch_prev_close(symbol)
                _shock = detect_intraday_shock(symbol, prev_close=_pc)
            except Exception as sd_err:
                logger.debug(f"[autopilot] shock detect {symbol}: {sd_err}")
                _shock = {"shocked": False}

            if (_shock.get("shocked")
                    and _shock.get("direction") == "down"):
                _ep = float(getattr(pos, "avg_entry_price", price) or price)
                # Safeguard: do not panic-dump profitable positions during minor intraday noise
                if price > _ep and abs(float(_shock.get("velocity_pct", 0.0) or 0.0)) < 3.5:
                    logger.info(f"[autopilot] Holding {symbol}: price ${price:.2f} > entry ${_ep:.2f} despite noise")
                else:
                    logger.warning(f"[autopilot] SHOCK EXIT {symbol}: "
                                   f"{_shock.get('detail')}")
                    actions.append({"symbol": symbol, "action": "SHOCK_EXIT",
                                    "price": round(price, 2),
                                    "detail": _shock.get("detail")})
                    if not dry_run:
                        submit_market_order(services.client, symbol, qty, side="SELL")
                        try:
                            from execution.trade_journal import journal
                            journal.record_close(symbol, float(price), "shock_exit",
                                                 pnl=(price - _ep) * qty)
                        except Exception as j_err:
                            logger.debug(f"[autopilot] journal shock-close: {j_err}")
                    unwind_paired_hedge(symbol, services.client, state, dry_run=dry_run)
                    state.pop(symbol, None)              # clear ratchet memory
                    continue

            entry = float(getattr(pos, "avg_entry_price", price) or price)
            record = state.get(symbol, {})
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

            # Bayesian conviction reflex: handle invalidations and scale-outs (Upgrade 3)
            try:
                from model.bayesian_confidence import belief_engine
                stmt = belief_engine.get_latest_statement(symbol)
                if stmt:
                    if stmt.recommendation == "EXIT_INVALIDATED":
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
                    elif stmt.recommendation == "SCALE_OUT" and not record.get("tp1_done"):
                        bayes_sell_qty = max(1, qty // 2)
                        logger.info(
                            f"[autopilot] BAYESIAN SCALE-OUT for {symbol}: sell {bayes_sell_qty} "
                            f"of {qty} @ {price:.2f} (conf={stmt.confidence_pointer:.1f}%)"
                        )
                        actions.append({"symbol": symbol, "action": "bayesian_scale_out",
                                        "price": round(price, 2), "qty": bayes_sell_qty})
                        if not dry_run:
                            submit_market_order(services.client, symbol, bayes_sell_qty, side="SELL")
                            try:
                                from execution.trade_journal import journal
                                _ep = float(getattr(pos, "avg_entry_price", price) or price)
                                journal.record_partial(symbol, float(price), bayes_sell_qty,
                                                       pnl=(price - _ep) * bayes_sell_qty,
                                                       reason="bayesian_scale_out")
                            except Exception as j_err:
                                logger.debug(f"[autopilot] journal bayesian partial: {j_err}")
                        record["tp1_done"] = True
                        qty -= bayes_sell_qty
            except Exception as b_err:
                logger.debug(f"[autopilot] Bayesian position check error {symbol}: {b_err}")

            # ---- tuned-profile TP1 scale-out with adaptive PSI geometry (Upgrade 1) --
            if os.getenv("TP1_AUTOMATION", "1") == "1":
                plan = tp1_scale_plan(price, entry, atr, qty,
                                      tp1_done=bool(record.get("tp1_done")),
                                      psi=pos_psi, regime=pos_regime)
                if plan.get("action") == "scale_out":
                    sell_qty = int(plan["sell_qty"])
                    logger.info(
                        f"[autopilot] TP1 SCALE-OUT {symbol}: sell {sell_qty} "
                        f"of {qty} @ {price:.2f} (TP1 ${plan['tp1_price']}) "
                        f"[regime: {plan.get('regime_applied', 'STATIC')}]")
                    actions.append({"symbol": symbol, "action": "tp1_scale_out",
                                    "price": round(price, 2),
                                    "qty": sell_qty,
                                    "regime": plan.get("regime_applied")})
                    if not dry_run:
                        submit_market_order(services.client, symbol,
                                            sell_qty, side="SELL")
                        try:
                            from execution.trade_journal import journal
                            journal.record_partial(
                                symbol, float(price), sell_qty,
                                pnl=(price - entry) * sell_qty,
                                reason="tp1_scale_out")
                        except Exception as j_err:
                            logger.debug(f"[autopilot] journal partial: {j_err}")
                    record["tp1_done"] = True
                    qty -= sell_qty                      # runner remainder

            # Early Breakeven Ratchet: if price reaches entry + 1.0*ATR, ratchet stop floor
            # to breakeven + buffer (entry + 0.10*ATR) so winning trades never become losses
            be_trig_mult = float(os.getenv("BE_TRIGGER_MULT", "1.0"))
            be_off_mult = float(os.getenv("BE_OFFSET_MULT", "0.10"))
            be_trigger = entry + (be_trig_mult * atr)
            be_armed = bool(record.get("be_armed"))

            if highest_seen >= be_trigger:
                be_floor = round(entry + (be_off_mult * atr), 2)
                if current_stop < be_floor:
                    logger.info(f"[autopilot] BREAKEVEN RATCHET {symbol}: high ${highest_seen:.2f} >= trig ${be_trigger:.2f} -> stop floor raised to ${be_floor:.2f}")
                    current_stop = be_floor
                be_armed = True

            # Breakeven floor once TP1 has fired (tuned be_after_tp1 rule).
            if record.get("tp1_done"):
                current_stop = max(current_stop, round(entry + (0.15 * atr), 2))

            ratchet = ratchet_trailing_stop(entry, atr, highest_seen, current_stop,
                                            psi=pos_psi, regime=pos_regime)
            new_stop = float(ratchet.get("stop_price", current_stop) or current_stop)

            state[symbol] = {
                "stop_price": new_stop,
                "highest_price": round(highest_seen, 2),
                "tp1_done": bool(record.get("tp1_done")),
                "be_armed": be_armed,
            }

            if new_stop > 0 and price <= new_stop:
                logger.warning(
                    f"[autopilot] STOP HIT {symbol}: price {price:.2f} <= stop "
                    f"{new_stop:.2f} -> closing {qty} shares"
                )
                actions.append({"symbol": symbol, "action": "close_at_stop",
                                "price": round(price, 2), "stop": round(new_stop, 2)})
                if not dry_run:
                    submit_market_order(services.client, symbol, qty, side="SELL")
                    try:
                        from execution.trade_journal import journal
                        _entry_px = float(getattr(pos, "avg_entry_price", price)
                                          or price)
                        journal.record_close(symbol, float(price), "stop",
                                             pnl=(price - _entry_px) * qty)
                    except Exception as j_err:
                        logger.debug(f"[autopilot] journal close: {j_err}")
                unwind_paired_hedge(symbol, services.client, state, dry_run=dry_run)
                state.pop(symbol, None)
            else:
                actions.append({
                    "symbol": symbol,
                    "action": "raise_stop" if ratchet.get("trailing_armed") else "hold",
                    "price": round(price, 2),
                    "stop": round(new_stop, 2),
                    "trailing_armed": bool(ratchet.get("trailing_armed")),
                })
        except Exception as e:
            logger.error(f"[autopilot] Error managing position: {e}")
            continue

    # Cleanup for positions that were closed outside autopilot (e.g. broker stop / take profit filled)
    current_symbols = {str(p.symbol).upper() for p in positions}
    for tracked_sym in list(state.keys()):
        if tracked_sym == "_day":
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
    for ticker in watchlist:
        ticker = str(ticker).strip().upper()
        if not ticker or ticker in INDEX_AND_HEDGE_SYMBOLS:
            continue
        try:
            from risk.book_allocator import classify_position_book
            book = classify_position_book(ticker)

            # 1. JEV Liquidity Scooper execution (prioritized if dislocated)
            try:
                from strategy.jev_scooper import jev_scooper
                opp = jev_scooper.evaluate_ticker(ticker)
                if opp.status == "QUALIFIED_SCOOP":
                    from execution.jev_execution import execute_jev_scoop_trade
                    res = execute_jev_scoop_trade(ticker, dry_run=dry_run)
                    results.append({"ticker": ticker, "status": res.get("status", "executed"), "book": book, "details": res})
                    continue
            except Exception as je:
                logger.debug(f"[autopilot] jev_scooper error for {ticker}: {je}")

            # 2. Ross Momentum Execution (for momentum names)
            if book == "momentum":
                from execution.ross_execution import execute_ross_bracket_trade
                res = execute_ross_bracket_trade(ticker, dry_run=dry_run)
                results.append({"ticker": ticker, "status": res.get("status", "executed"), "book": "momentum", "details": res})
                continue
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
                    _curr_st[ticker] = {
                        "stop_price": float((_dec.get("exit_levels") or {}).get("stop_loss", 0.0) or 0.0),
                        "highest_price": float(_entry_px),
                        "tp1_done": False,
                        "be_armed": False,
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
    Unified multi-strategy market scanner:
      1. Morning Window (07:00-10:00 ET): Scans whole market for Ross Cameron Grade A Low-Float Runners.
      2. Regular Session: Scans for High-Volume Dips & Quality Breakouts across Core Universe.
    """
    if min_auto_score is None:
        min_auto_score = float(os.getenv("MIN_AUTO_SCORE", "75.0"))

    picks = []
    try:
        # Check if inside Ross Cameron morning momentum window
        from market.low_float_scanner import check_trading_window, scan_momentum_market
        win = check_trading_window()
        
        logger.info("[autopilot] Scanning whole market for Grade A low-float momentum runners...")
        runners = scan_momentum_market(whole_market=True, top_n=top_picks)
        for r in runners:
            # Sniper quality: only take Grade A runners
            if r.get("grade") == "A" and r["ticker"] not in picks:
                picks.append(r["ticker"])
    except Exception as e:
        logger.debug(f"[autopilot] low-float morning scan note: {e}")

    try:
        from strategy.jev_scooper import jev_scooper
        logger.info("[autopilot] Scanning for high-JEV liquidity scoops...")
        jev_opps = jev_scooper.scan_market(top_n=top_picks)
        for opp in jev_opps:
            if opp.status == "QUALIFIED_SCOOP" and opp.ticker not in picks:
                picks.append(opp.ticker)
    except Exception as e:
        logger.debug(f"[autopilot] JEV scan note: {e}")

    try:
        from backtest.market_scanner import rank_market
        rows = rank_market(top_n=max(top_picks * 4, 10), filter_junk=True, show_callout=False)
        for r in rows:
            if float(r.get("score", 0.0)) >= min_auto_score and r["ticker"] not in picks:
                picks.append(r["ticker"])
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