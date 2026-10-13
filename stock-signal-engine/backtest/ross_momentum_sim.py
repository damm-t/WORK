"""
Ross Cameron Momentum Strategy Simulator & Mock Engine
======================================================
Implements Ross Cameron's Small-Account Momentum Strategy:
  1. Stock Selection: 5 Pillars (Up 10%+, RVOL 5x+, News Catalyst, $2-$20 price, <20M Float).
  2. Entry Setup:
     - Never chase green candles moving straight up.
     - Wait for the 1st pullback consolidation on 1-minute chart.
     - Enter when a new candle breaks above the previous candle's high (micro-breakout).
     - Stop-Loss: Hard stop at lowest point of the pullback.
     - Target: High of the Day (HOD) with minimum 1:1, ideal 2:1+ Risk:Reward.
     - Sizing: Fixed dollar risk per trade ($100 default). 50% size if no news catalyst.
  3. Take-Profit & Exits:
     - Scale out 50% at HOD (TP1).
     - Move hard stop to breakeven ($entry).
     - Trail runner; exit on Bearish Indicators:
       • Topping Tail candle (upper shadow >= 2x body)
       • Volume Divergence (higher price on lower volume)
       • Pullback low breakdown
  4. Capital Protection (Walk-Away Rules):
     - 50% Profit Giveback Rule: Walk away if net daily profit drops 50% from peak.
     - Daily Max Loss Rule: Stop session if loss hits max limit or 2-3 consecutive stops.
     - Trading Window: 7:00 AM - 10:00 AM ET.
  5. Persistence:
     - All partial and full exits logged to execution/trade_journal.db.
"""

import argparse
import logging
import math
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from market.price_fetcher import fetch_prices
from market.low_float_scanner import evaluate_five_pillars, check_trading_window
from execution.trade_journal import TradeJournal

logger = logging.getLogger(__name__)
NY_TZ = ZoneInfo("America/New_York")


@dataclass
class Candle:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float

    @property
    def is_green(self) -> bool:
        return self.close >= self.open

    @property
    def body_size(self) -> float:
        return abs(self.close - self.open)

    @property
    def upper_shadow(self) -> float:
        return self.high - max(self.open, self.close)

    @property
    def lower_shadow(self) -> float:
        return min(self.open, self.close) - self.low

    @property
    def is_topping_tail(self) -> bool:
        """Topping tail: upper shadow at least 2x body size with body in lower half of candle."""
        body = max(self.body_size, 0.01)
        return (self.upper_shadow >= 2.0 * body) and (self.close < (self.high - 0.5 * (self.high - self.low)))


@dataclass
class RossTrade:
    ticker: str
    entry_time: str
    entry_price: float
    initial_shares: int
    current_shares: int
    stop_loss: float
    hod_target: float
    risk_per_share: float
    rr_ratio: float
    grade: str
    has_news: bool
    status: str = "OPEN"          # OPEN, PARTIAL_TP1, CLOSED
    tp1_price: Optional[float] = None
    tp1_shares: int = 0
    final_exit_price: Optional[float] = None
    final_exit_reason: str = ""
    realized_pnl: float = 0.0
    breakeven_active: bool = False
    events: List[str] = field(default_factory=list)


class RossSessionManager:
    """Manages session-level risk and the Walk-Away / Capital Protection rules."""

    def __init__(self, max_daily_loss: float = 300.0, max_consecutive_losses: int = 3,
                 profit_giveback_pct: float = 0.50):
        self.max_daily_loss = max_daily_loss
        self.max_consecutive_losses = max_consecutive_losses
        self.profit_giveback_pct = profit_giveback_pct

        self.net_pnl = 0.0
        self.peak_pnl = 0.0
        self.consecutive_losses = 0
        self.trades_count = 0
        self.wins = 0
        self.losses = 0
        self.walk_away_triggered = False
        self.walk_away_reason = ""

    def check_walk_away(self) -> Tuple[bool, str]:
        """Evaluates whether trading must immediately cease."""
        if self.walk_away_triggered:
            return True, self.walk_away_reason

        # 1. 50% Profit Giveback Rule
        if self.peak_pnl >= 200.0:  # Only active once a meaningful profit was locked
            giveback_threshold = self.peak_pnl * (1.0 - self.profit_giveback_pct)
            if self.net_pnl <= giveback_threshold:
                self.walk_away_triggered = True
                self.walk_away_reason = (f"Profit Giveback Rule Triggered: Peak +${self.peak_pnl:.2f} "
                                         f"dropped to +${self.net_pnl:.2f} (50% giveback limit). Session halted.")
                return True, self.walk_away_reason

        # 2. Daily Max Loss Rule
        if self.net_pnl <= -self.max_daily_loss:
            self.walk_away_triggered = True
            self.walk_away_reason = (f"Daily Max Loss Hit: -${abs(self.net_pnl):.2f} "
                                     f"(limit: -${self.max_daily_loss:.2f}). Session halted.")
            return True, self.walk_away_reason

        # 3. Consecutive Stop-Outs Rule
        if self.consecutive_losses >= self.max_consecutive_losses:
            self.walk_away_triggered = True
            self.walk_away_reason = (f"Consecutive Loss Limit Hit: {self.consecutive_losses} stops in a row. "
                                     f"Market momentum hostile today. Session halted.")
            return True, self.walk_away_reason

        return False, ""

    def register_trade_result(self, pnl: float):
        self.trades_count += 1
        self.net_pnl += pnl
        if self.net_pnl > self.peak_pnl:
            self.peak_pnl = self.net_pnl

        if pnl > 0:
            self.wins += 1
            self.consecutive_losses = 0
        else:
            self.losses += 1
            self.consecutive_losses += 1

        self.check_walk_away()


def generate_synthetic_candles(ticker: str, start_price: float = 5.0,
                               scenario: str = "ideal_breakout") -> List[Candle]:
    """
    Generates realistic 1-minute micro-candles for mocking Ross Cameron setups.
    Scenarios:
      - 'ideal_breakout': Morning spike -> 3-min pullback -> breakout over prior high -> hits HOD -> topping tail exit.
      - 'failed_pullback': Morning spike -> pullback -> false breakout -> stops out below pullback low.
      - 'volume_divergence': Reaches HOD on shrinking volume -> early scale out.
    """
    candles = []
    base_time = datetime(2026, 9, 29, 9, 31, tzinfo=NY_TZ)
    px = start_price

    # Phase 1: Morning Parabolic Spike (Surging Upward - Do Not Chase)
    spike_bars = [
        (px * 1.00, px * 1.05, px * 0.99, px * 1.04, 250_000),
        (px * 1.04, px * 1.10, px * 1.03, px * 1.09, 450_000),
        (px * 1.09, px * 1.16, px * 1.08, px * 1.15, 800_000),
        (px * 1.15, px * 1.22, px * 1.14, px * 1.20, 1_200_000),  # HOD established here
    ]
    for i, (o, h, l, c, v) in enumerate(spike_bars):
        candles.append(Candle(
            timestamp=(base_time + timedelta(minutes=i)).strftime("%H:%M"),
            open=round(o, 2), high=round(h, 2), low=round(l, 2), close=round(c, 2), volume=v
        ))

    hod = max(c.high for c in candles)
    t_offset = len(candles)

    # Phase 2: First Pullback Consolidation (Waiting for downward momentum to halt)
    # 3 consecutive pullback candles setting support
    pb1 = (hod * 0.98, hod * 0.99, hod * 0.95, hod * 0.96, 320_000)
    pb2 = (hod * 0.96, hod * 0.97, hod * 0.93, hod * 0.94, 210_000)
    pb3 = (hod * 0.94, hod * 0.95, hod * 0.92, hod * 0.935, 140_000)  # Pullback Low established

    for i, (o, h, l, c, v) in enumerate([pb1, pb2, pb3]):
        candles.append(Candle(
            timestamp=(base_time + timedelta(minutes=t_offset + i)).strftime("%H:%M"),
            open=round(o, 2), high=round(h, 2), low=round(l, 2), close=round(c, 2), volume=v
        ))

    t_offset = len(candles)
    prior_high = candles[-1].high   # Entry trigger: breaking prior candle high
    pullback_low = min(c.low for c in candles[4:])

    if scenario == "ideal_breakout":
        # Entry Candle: ticks above prior_high ($5.79), surges to $5.90
        entry_c = (pb3[3], prior_high + 0.12, pb3[3] - 0.02, prior_high + 0.10, 550_000)
        # Push to HOD
        push_c = (entry_c[3], hod + 0.02, entry_c[3] - 0.01, hod, 850_000)
        # Extension
        ext_c = (hod, hod * 1.06, hod * 0.99, hod * 1.04, 1_100_000)
        # Topping Tail Candle (High surge then long upper wick, body near low)
        tt_high = hod * 1.10
        tt_c = (hod * 1.04, tt_high, hod * 1.03, hod * 1.035, 450_000)

        for i, (o, h, l, c, v) in enumerate([entry_c, push_c, ext_c, tt_c]):
            candles.append(Candle(
                timestamp=(base_time + timedelta(minutes=t_offset + i)).strftime("%H:%M"),
                open=round(o, 2), high=round(h, 2), low=round(l, 2), close=round(c, 2), volume=v
            ))

    elif scenario == "failed_pullback":
        # Triggers entry slightly above prior high, then immediately fails and flushes below pullback_low
        entry_c = (pb3[3], prior_high + 0.03, pb3[3] - 0.01, prior_high + 0.01, 200_000)
        # Flush down through stop
        flush_c = (entry_c[3], entry_c[3] + 0.01, pullback_low - 0.08, pullback_low - 0.05, 750_000)

        for i, (o, h, l, c, v) in enumerate([entry_c, flush_c]):
            candles.append(Candle(
                timestamp=(base_time + timedelta(minutes=t_offset + i)).strftime("%H:%M"),
                open=round(o, 2), high=round(h, 2), low=round(l, 2), close=round(c, 2), volume=v
            ))

    elif scenario == "volume_divergence":
        # Breakout occurs, retests HOD, but volume is 1/5th of initial surge (exhaustion)
        entry_c = (pb3[3], prior_high + 0.08, pb3[3] - 0.02, prior_high + 0.06, 310_000)
        hod_test_c = (entry_c[3], hod + 0.01, entry_c[3], hod - 0.02, 110_000)  # low volume retest
        reversal_c = (hod - 0.02, hod, pb3[2], pb3[2] + 0.02, 600_000)

        for i, (o, h, l, c, v) in enumerate([entry_c, hod_test_c, reversal_c]):
            candles.append(Candle(
                timestamp=(base_time + timedelta(minutes=t_offset + i)).strftime("%H:%M"),
                open=round(o, 2), high=round(h, 2), low=round(l, 2), close=round(c, 2), volume=v
            ))

    return candles


def run_ross_momentum_sim(ticker: str, candles: List[Candle], pillar_info: dict,
                          session: RossSessionManager,
                          account_risk_dollars: float = 100.0,
                          journal: Optional[TradeJournal] = None) -> Optional[RossTrade]:
    """
    Executes Ross Cameron's exact entry, scale-out, exit, and risk management logic
    candle-by-candle across a 1-minute intraday stream.
    """
    if len(candles) < 4:
        print(f"[{ticker}] Insufficient candle data for momentum execution.")
        return None

    # Step 0: Check Session Walk-Away conditions
    halted, reason = session.check_walk_away()
    if halted:
        print(f"  🚫 [{ticker}] Skipped: {reason}")
        return None

    # Sizing adjustment: Pillar 3 (No news catalyst -> 50% position size)
    grade = pillar_info.get("grade", "A")
    has_news = pillar_info.get("has_catalyst", True)
    effective_risk = account_risk_dollars if (grade == "A" and has_news) else (account_risk_dollars * 0.50)

    # State machine variables
    trade: Optional[RossTrade] = None
    hod = 0.0
    in_pullback = False
    pullback_low = float("inf")
    pullback_bars = 0
    trade_journal_id = None

    print(f"\n{'=' * 84}")
    print(f"  ⚡ EXECUTING ROSS CAMERON MOMENTUM PLAYBOOK: {ticker}")
    print(f"  Price: ${pillar_info.get('price', candles[0].close):.2f} | "
          f"Grade: {grade} | Float: {pillar_info.get('float_millions', 'N/A')}M | "
          f"Risk Allocation: ${effective_risk:.0f} {'(50% Size: No News)' if not has_news else '(Full Size)'}")
    print(f"{'=' * 84}")

    for idx, c in enumerate(candles):
        # 1. Update HOD
        if c.high > hod:
            hod = c.high

        # IF NOT IN A POSITION: Look for 1st Pullback Setup
        if trade is None:
            # Rule: Never chase green spikes. Check if we are pulling back from HOD.
            # A pullback occurs when price is below HOD and we get red candles or lower highs.
            if idx >= 3 and c.high < hod:
                in_pullback = True
                pullback_bars += 1
                if c.low < pullback_low:
                    pullback_low = c.low

            # Entry Trigger: Must have consolidated for at least 2 candles
            # Buy as soon as current candle ticks OVER previous candle's high
            if in_pullback and pullback_bars >= 2 and idx > 0:
                prev_c = candles[idx - 1]
                entry_trigger_price = prev_c.high + 0.01

                # Did this candle trigger above previous high?
                if c.high >= entry_trigger_price:
                    entry_px = entry_trigger_price
                    stop_px = round(pullback_low - 0.02, 2)
                    risk_per_share = round(entry_px - stop_px, 2)

                    if risk_per_share <= 0.02:
                        continue  # Too tight / invalid stop

                    # Target 1: HOD
                    reward_to_hod = round(hod - entry_px, 2)
                    rr_ratio = round(reward_to_hod / risk_per_share, 2)

                    # Ross Rule: Risk/Reward must be at least 1:1, ideally 2:1+
                    if rr_ratio < 1.0:
                        print(f"  [{c.timestamp}] Setup passed: R:R {rr_ratio}:1 below minimum 1:1 (Target HOD ${hod:.2f} too close).")
                        continue

                    # Position Sizing: Dollar Risk / Risk Per Share
                    shares = int(effective_risk / risk_per_share)
                    shares = max(shares, 10)  # minimum 10 shares

                    trade = RossTrade(
                        ticker=ticker,
                        entry_time=c.timestamp,
                        entry_price=entry_px,
                        initial_shares=shares,
                        current_shares=shares,
                        stop_loss=stop_px,
                        hod_target=hod,
                        risk_per_share=risk_per_share,
                        rr_ratio=rr_ratio,
                        grade=grade,
                        has_news=has_news
                    )

                    msg = (f"🎯 [{c.timestamp}] ENTRY TRIGGER: Bought {shares} shares @ ${entry_px:.2f} "
                           f"(Broke prior candle high ${prev_c.high:.2f}). "
                           f"Stop: ${stop_px:.2f} | HOD Target: ${hod:.2f} | R:R {rr_ratio}:1")
                    print(f"  {msg}")
                    trade.events.append(msg)

                    # Persist to SQLite journal
                    if journal:
                        try:
                            trade_journal_id = journal.record_open(
                                ticker=ticker,
                                qty=shares,
                                entry=entry_px,
                                grade=grade,
                                style="ross_momentum",
                                score=pillar_info.get("score", 85.0),
                                rationale=f"1st Pullback micro-breakout. Stop ${stop_px:.2f}, HOD ${hod:.2f}, R:R {rr_ratio}:1"
                            )
                        except Exception as e:
                            logger.debug(f"Journal record_open error: {e}")
                    continue

        # IF IN A POSITION: Manage Scale-Outs & Exits
        else:
            # 1. STOP-LOSS CHECK: If price breaches below stop_loss -> Exit immediately
            if c.low <= trade.stop_loss:
                loss_per_share = trade.stop_loss - trade.entry_price
                trade_loss = round(loss_per_share * trade.current_shares, 2)
                trade.realized_pnl += trade_loss
                trade.final_exit_price = trade.stop_loss
                trade.final_exit_reason = "Hard Stop Hit (Pullback Low breached)" if not trade.breakeven_active else "Breakeven Stop Hit"
                trade.status = "CLOSED"
                trade.current_shares = 0

                msg = (f"🛑 [{c.timestamp}] STOP-OUT: Liquidated remaining shares @ ${trade.stop_loss:.2f}. "
                       f"Reason: {trade.final_exit_reason} | Realized PnL: ${trade_loss:+.2f}")
                print(f"  {msg}")
                trade.events.append(msg)

                if journal:
                    try:
                        journal.record_close(ticker=ticker, exit_price=trade.stop_loss,
                                            reason=trade.final_exit_reason, pnl=trade.realized_pnl)
                    except Exception as e:
                        logger.debug(f"Journal record_close error: {e}")

                session.register_trade_result(trade.realized_pnl)
                break

            # 2. SCALE-OUT RULE: Sell 50% upon reaching High of the Day (HOD)
            if trade.status == "OPEN" and c.high >= trade.hod_target:
                clip_shares = trade.initial_shares // 2
                clip_pnl = round((trade.hod_target - trade.entry_price) * clip_shares, 2)
                trade.realized_pnl += clip_pnl
                trade.current_shares -= clip_shares
                trade.tp1_price = trade.hod_target
                trade.tp1_shares = clip_shares
                trade.status = "PARTIAL_TP1"
                trade.breakeven_active = True
                trade.stop_loss = trade.entry_price  # Move stop to Breakeven

                msg = (f"💰 [{c.timestamp}] SCALE-OUT TP1 (50%): Sold {clip_shares} shares @ HOD ${trade.hod_target:.2f} "
                       f"for +${clip_pnl:.2f} (+{((trade.hod_target/trade.entry_price)-1)*100:.1f}%). "
                       f"Stop moved to Breakeven (${trade.entry_price:.2f}). Remaining: {trade.current_shares} shares.")
                print(f"  {msg}")
                trade.events.append(msg)

                if journal:
                    try:
                        journal.record_partial(ticker=ticker, exit_price=trade.hod_target,
                                               qty_sold=clip_shares, pnl=clip_pnl,
                                               reason=f"TP1 HOD Scale-Out (+{((trade.hod_target/trade.entry_price)-1)*100:.1f}%)",
                                               grade=grade, style="ross_momentum", score=pillar_info.get("score"))
                    except Exception as e:
                        logger.debug(f"Journal record_partial error: {e}")

            # 3. BEARISH EXIT INDICATOR 1: Topping Tail Candle (Reversal near highs)
            if trade.current_shares > 0 and c.is_topping_tail and c.high >= trade.hod_target:
                exit_px = c.close
                runner_pnl = round((exit_px - trade.entry_price) * trade.current_shares, 2)
                trade.realized_pnl += runner_pnl
                trade.final_exit_price = exit_px
                trade.final_exit_reason = "Bearish Indicator: Topping Tail Reversal Candle"
                trade.status = "CLOSED"

                msg = (f"⚠️ [{c.timestamp}] BEARISH EXIT: Topping Tail detected (Upper wick ${c.upper_shadow:.2f} "
                       f">= 2x body ${c.body_size:.2f}). Liquidated remaining {trade.current_shares} shares @ ${exit_px:.2f}. "
                       f"Runner PnL: +${runner_pnl:.2f} | Total Trade PnL: +${trade.realized_pnl:.2f}")
                print(f"  {msg}")
                trade.events.append(msg)

                if journal:
                    try:
                        # Record only runner PnL if TP1 was already recorded to avoid double counting
                        close_pnl = runner_pnl if trade.status == "PARTIAL_TP1" else trade.realized_pnl
                        journal.record_close(ticker=ticker, exit_price=exit_px,
                                            reason=trade.final_exit_reason, pnl=close_pnl)
                    except Exception as e:
                        logger.debug(f"Journal record_close error: {e}")

                session.register_trade_result(trade.realized_pnl)
                trade.current_shares = 0
                break

            # 4. BEARISH EXIT INDICATOR 2: Volume Divergence (High price on noticeably weak volume)
            if (trade.current_shares > 0 and trade.status == "PARTIAL_TP1" and
                    c.high > trade.hod_target and c.volume < (candles[idx-1].volume * 0.40)):
                exit_px = c.close
                runner_pnl = round((exit_px - trade.entry_price) * trade.current_shares, 2)
                trade.realized_pnl += runner_pnl
                trade.final_exit_price = exit_px
                trade.final_exit_reason = "Bearish Indicator: Volume Divergence (Exhaustion at New High)"
                trade.status = "CLOSED"

                msg = (f"⚠️ [{c.timestamp}] BEARISH EXIT: Volume Divergence detected (New high with volume -60% vs breakout). "
                       f"Liquidated remaining {trade.current_shares} shares @ ${exit_px:.2f}. "
                       f"Runner PnL: +${runner_pnl:.2f} | Total Trade PnL: +${trade.realized_pnl:.2f}")
                print(f"  {msg}")
                trade.events.append(msg)

                if journal:
                    try:
                        close_pnl = runner_pnl if trade.status == "PARTIAL_TP1" else trade.realized_pnl
                        journal.record_close(ticker=ticker, exit_price=exit_px,
                                            reason=trade.final_exit_reason, pnl=close_pnl)
                    except Exception as e:
                        logger.debug(f"Journal record_close error: {e}")

                session.register_trade_result(trade.realized_pnl)
                trade.current_shares = 0
                break

    # If trade remained open at end of candle feed, close at last candle close
    if trade and trade.current_shares > 0:
        last_c = candles[-1]
        exit_px = last_c.close
        pnl = round((exit_px - trade.entry_price) * trade.current_shares, 2)
        trade.realized_pnl += pnl
        trade.final_exit_price = exit_px
        trade.final_exit_reason = "10:00 AM Trading Window Expired (Session Closed)"
        trade.status = "CLOSED"

        msg = (f"⏰ [{last_c.timestamp}] WINDOW EXPIRED: Liquidated remaining {trade.current_shares} shares @ ${exit_px:.2f}. "
               f"Total PnL: +${trade.realized_pnl:.2f}")
        print(f"  {msg}")
        trade.events.append(msg)

        if journal:
            try:
                close_pnl = pnl if trade.status == "PARTIAL_TP1" else trade.realized_pnl
                journal.record_close(ticker=ticker, exit_price=exit_px,
                                    reason=trade.final_exit_reason, pnl=close_pnl)
            except Exception as e:
                logger.debug(f"Journal record_close error: {e}")

        session.register_trade_result(trade.realized_pnl)
        trade.current_shares = 0

    return trade


def mock_ross_session(tickers: Optional[List[str]] = None,
                      scenario_override: Optional[str] = None,
                      account_risk_dollars: float = 50.0,
                      capital: Optional[float] = None,
                      persist: bool = False) -> dict:
    """
    Runs an end-to-end multi-stock session simulation demonstrating:
      - Selection using the 5 Pillars (supporting small-cap & penny runners)
      - Realistic small-account risk sizing (e.g. $25 - $50 risk per setup)
      - 1st pullback micro-breakout entries
      - 50% HOD scale-outs
      - Bearish topping tail / volume divergence exits
      - Walk-away profit giveback protection
    """
    if capital and capital > 0:
        # Small account standard: 1% to 2% max risk per trade
        effective_trade_risk = round(capital * 0.02, 2)
        max_daily_loss = round(capital * 0.05, 2)
    else:
        effective_trade_risk = float(account_risk_dollars)
        max_daily_loss = round(effective_trade_risk * 3.0, 2)

    session = RossSessionManager(max_daily_loss=max_daily_loss, max_consecutive_losses=3, profit_giveback_pct=0.50)
    journal = TradeJournal() if persist else None

    test_tickers = tickers or ["CYN", "SMFL", "BBLG", "HOLO"]
    executed_trades = []

    print("\n" + "#" * 84)
    print("   🏛️  ROSS CAMERON MOMENTUM SESSION SIMULATOR & WALK-AWAY MOCK")
    print(f"   Account Capital: ${capital:,.2f}" if capital else f"   Base Risk Per Trade: ${effective_trade_risk:.2f}")
    print(f"   Trade Risk Cap: ${effective_trade_risk:.2f} | Max Daily Loss Limit: ${session.max_daily_loss:.2f}")
    print(f"   50% Profit Giveback Protection: ACTIVE | Low-Float Penny Stock Floor: $0.50")
    print("#" * 84)

    for i, t in enumerate(test_tickers):
        # Check walk away first
        halted, reason = session.check_walk_away()
        if halted:
            print(f"\n🛑 SESSION SHUTDOWN: {reason}")
            break

        # Step 1: 5 Pillars Evaluation
        pillar_eval = evaluate_five_pillars(t)
        if pillar_eval.get("grade") == "C":
            # For demonstration in mock mode, synthesize realistic small-cap runner setup
            pillar_eval = {
                "ticker": t,
                "score": 92.0,
                "grade": "A" if i % 2 == 0 else "B",
                "price": 1.25 + (i * 0.85),
                "float_millions": 4.5 + (i * 2.0),
                "has_catalyst": (i % 2 == 0),
                "headline": "Announces FDA Fast-Track Designation for Flagship Lead Candidate",
                "pillars_passed": "5/5" if i % 2 == 0 else "4/5"
            }

        # Step 2: Candle stream (historical or synthetic)
        scenario = scenario_override or ("ideal_breakout" if i == 0 else ("failed_pullback" if i == 1 else "volume_divergence"))
        candles = generate_synthetic_candles(t, start_price=pillar_eval["price"], scenario=scenario)

        # Step 3: Run the trade with small account sizing
        res = run_ross_momentum_sim(
            ticker=t,
            candles=candles,
            pillar_info=pillar_eval,
            session=session,
            account_risk_dollars=effective_trade_risk,
            journal=journal
        )
        if res:
            executed_trades.append(res)

    # Final Session Scorecard
    print("\n" + "=" * 84)
    print("   📊 ROSS CAMERON SESSION SUMMARY & CAPITAL PROTECTION REPORT")
    print("=" * 84)
    print(f"  Total Setups Traded : {session.trades_count}")
    print(f"  Win / Loss Record   : {session.wins} Wins / {session.losses} Losses (Win Rate: {(session.wins/max(1, session.trades_count))*100:.1f}%)")
    print(f"  Peak Session Profit : +${session.peak_pnl:.2f}")
    print(f"  Net Realized PnL    : {('+$' if session.net_pnl >= 0 else '-$')}{abs(session.net_pnl):.2f}")
    if session.walk_away_triggered:
        print(f"  Walk-Away Triggered : ⚠️ YES — {session.walk_away_reason}")
    else:
        print(f"  Walk-Away Triggered : No (Session completed within risk boundaries)")
    print("=" * 84 + "\n")

    return {
        "trades_count": session.trades_count,
        "net_pnl": session.net_pnl,
        "peak_pnl": session.peak_pnl,
        "win_rate": (session.wins / max(1, session.trades_count)) * 100.0,
        "walk_away_triggered": session.walk_away_triggered,
        "walk_away_reason": session.walk_away_reason,
        "trades": executed_trades
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ross Cameron Momentum Strategy Simulator")
    parser.add_argument("--tickers", type=str, default="", help="Comma-separated tickers")
    parser.add_argument("--scenario", type=str, default="", choices=["", "ideal_breakout", "failed_pullback", "volume_divergence"],
                        help="Specific candle scenario to mock")
    parser.add_argument("--risk", type=float, default=50.0, help="Dollar risk per trade (e.g. 25, 50, 100)")
    parser.add_argument("--capital", type=float, default=None, help="Small account starting capital (e.g. 2500)")
    args = parser.parse_args()

    t_list = [t.strip().upper() for t in args.tickers.split(",") if t.strip()] if args.tickers else None
    mock_ross_session(tickers=t_list, scenario_override=args.scenario or None,
                      account_risk_dollars=args.risk, capital=args.capital)
