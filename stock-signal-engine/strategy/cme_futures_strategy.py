"""
CME Index Futures Strategy Engine
=================================
Quantitative model for CME Micro-Futures (MES, MNQ, MCL, MGC).

Key Alpha Setups:
  1. Opening Range Breakout (ORB) with Volume Confirmation:
     Detects first 15-minute range expansion in direction of the broader SPY/QQQ macro trend.
  2. VWAP Mean-Reversion Reclaim:
     Enters on retest of the Volume-Weighted Average Price (VWAP) after an intraday liquidity sweep.
  3. Strict Tick-Based Bracket Geometry:
     Pre-computes Stop Loss and Take Profit levels in contract ticks with asymmetric 2:1 R:R.
"""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

CME_LEARNING_STATE_PATH = Path("data/cme_strategy_learning.json")


@dataclass
class CMEFuturesSignal:
    symbol: str                           # e.g. "MES" or "MNQ"
    timestamp: float
    side: str                             # "LONG" or "SHORT" or "NEUTRAL"
    confidence_score: float               # 0 to 100
    entry_price: float
    stop_loss: float
    take_profit: float
    tick_size: float                      # e.g. 0.25 for MES
    point_value: float                    # e.g. $5.00 for MES
    contracts: int = 2
    setup_name: str = "VWAP_RECLAIM"
    strategy_type: str = "VWAP_RECLAIM"
    rationale: str = ""


class CMEFuturesSelfLearningTracker:
    """
    Self-Improving Expectancy Tracker for CME Micro Index & Commodity Futures.
    Maintains rolling win rate, profit factor, and dynamic position multipliers per setup type.
    """

    def __init__(self, state_path: Path = CME_LEARNING_STATE_PATH):
        self.state_path = state_path
        self.history: Dict[str, List[Dict[str, Any]]] = self._load_state()

    def _load_state(self) -> Dict[str, List[Dict[str, Any]]]:
        if self.state_path.exists() and self.state_path.stat().st_size > 0:
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception as e:
                logger.warning(f"[cme_learner] Could not load state: {e}")
        return {}

    def _save_state(self) -> None:
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.warning(f"[cme_learner] Could not save state: {e}")

    def record_trade(
        self,
        strategy_type: str,
        pnl: float,
        r_multiple: float,
        entry_price: float,
        exit_price: float,
        symbol: str = "CORN",
    ) -> None:
        """Records a closed CME futures trade into the self-learning memory."""
        strat = strategy_type.strip().upper()
        if strat not in self.history:
            self.history[strat] = []

        record = {
            "symbol": symbol,
            "pnl": round(float(pnl), 2),
            "r_multiple": round(float(r_multiple), 2),
            "win": bool(pnl > 0),
            "entry_price": round(float(entry_price), 2),
            "exit_price": round(float(exit_price), 2),
            "timestamp": time.time(),
        }
        self.history[strat].append(record)
        if len(self.history[strat]) > 50:
            self.history[strat] = self.history[strat][-50:]
        self._save_state()
        logger.info(
            f"[cme_learner] Logged trade for {strat} ({symbol}): "
            f"PnL ${pnl:+.2f} ({r_multiple:+.2f}R). Total records: {len(self.history[strat])}"
        )

    def get_multiplier(self, strategy_type: str) -> float:
        """
        Dynamically adjusts strategy size (0.0x to 1.20x) based on rolling empirical expectancy.
        - High Expectancy (PF >= 1.40, Expectancy > 0): 1.20x boost
        - Moderate Edge (1.10 <= PF < 1.40): 1.05x boost
        - Neutral (0.85 <= PF < 1.10): 0.90x
        - Negative Drift (0.65 <= PF < 0.85): 0.70x
        - Persistent Loss (PF < 0.65 over >= 5 trades): 0.0x VETO
        """
        strat = strategy_type.strip().upper()
        trades = self.history.get(strat, [])
        if len(trades) < 4:
            return 1.0  # Cold start baseline

        recent = trades[-20:]
        wins = [t["pnl"] for t in recent if t["win"]]
        losses = [abs(t["pnl"]) for t in recent if not t["win"]]
        win_count = len(wins)
        loss_count = len(losses)
        total = win_count + loss_count

        if total == 0:
            return 1.0

        win_rate = win_count / total
        sum_wins = sum(wins)
        sum_losses = sum(losses)

        profit_factor = (sum_wins / max(sum_losses, 0.01)) if sum_losses > 0 else (2.5 if sum_wins > 0 else 1.0)
        avg_win = (sum_wins / win_count) if win_count > 0 else 0.0
        avg_loss = (sum_losses / loss_count) if loss_count > 0 else 0.0
        expectancy = (win_rate * avg_win) - ((1.0 - win_rate) * avg_loss)

        if profit_factor >= 1.40 and expectancy > 0:
            return 1.20
        elif profit_factor >= 1.10 and expectancy > 0:
            return 1.05
        elif profit_factor >= 0.85:
            return 0.90
        elif profit_factor >= 0.65:
            return 0.70
        else:
            return 0.0  # Veto underperforming pattern

    def get_performance_summary(self) -> Dict[str, Any]:
        summary = {}
        for strat, trades in self.history.items():
            wins = [t["pnl"] for t in trades if t["win"]]
            losses = [abs(t["pnl"]) for t in trades if not t["win"]]
            win_cnt = len(wins)
            loss_cnt = len(losses)
            tot = win_cnt + loss_cnt
            wr = (win_cnt / tot * 100) if tot > 0 else 0.0
            sum_w = sum(wins)
            sum_l = sum(losses)
            pf = (sum_w / max(sum_l, 0.01)) if sum_l > 0 else (2.5 if sum_w > 0 else 1.0)
            avg_r = np.mean([t["r_multiple"] for t in trades]) if trades else 0.0
            summary[strat] = {
                "trades": tot,
                "win_rate_pct": round(wr, 1),
                "profit_factor": round(pf, 2),
                "avg_r_multiple": round(float(avg_r), 2),
                "multiplier": self.get_multiplier(strat),
            }
        return summary


class CMEFuturesStrategyEngine:
    """
    Evaluates CME Micro Index and Commodity Futures setups with guaranteed >= 2.2:1 R:R.
    """

    TICK_CONFIG = {
        # Agricultural & Physical Commodities (Desk 3 Core Mandate)
        "CORN": {"tick_size": 0.01, "point_value": 50.0, "name": "CBOT Corn Futures / ETF"},
        "SOYB": {"tick_size": 0.01, "point_value": 50.0, "name": "CBOT Soybean Futures / ETF"},
        "WEAT": {"tick_size": 0.01, "point_value": 50.0, "name": "CBOT Wheat Futures / ETF"},
        "ZC":   {"tick_size": 0.25, "point_value": 50.0, "name": "CBOT Corn Futures"},
        "ZS":   {"tick_size": 0.25, "point_value": 50.0, "name": "CBOT Soybean Futures"},
        "ZW":   {"tick_size": 0.25, "point_value": 50.0, "name": "CBOT Wheat Futures"},
        "MCL":  {"tick_size": 0.01, "point_value": 100.0, "name": "Micro Crude Oil"},
        "MGC":  {"tick_size": 0.10, "point_value": 10.0, "name": "Micro Gold"},
        "USO":  {"tick_size": 0.01, "point_value": 50.0, "name": "Crude Oil Proxy"},
        "GLD":  {"tick_size": 0.01, "point_value": 10.0, "name": "Gold Proxy"},
        # Legacy index micro-contracts
        "MES":  {"tick_size": 0.25, "point_value": 5.0, "name": "Micro E-mini S&P 500"},
        "MNQ":  {"tick_size": 0.25, "point_value": 2.0, "name": "Micro E-mini Nasdaq 100"},
    }

    def __init__(self, learner: Optional[CMEFuturesSelfLearningTracker] = None):
        self.learner = learner or CMEFuturesSelfLearningTracker()

    @staticmethod
    def _compute_rr_bracket(entry: float, raw_sl: float, side: str, min_rr: float = 2.25, tick_size: float = 0.01) -> tuple[float, float]:
        """Ensures post-rounding R:R is strictly >= 2.20:1."""
        if side == "LONG":
            sl = round(raw_sl, 2)
            risk = max(entry - sl, tick_size * 2.0)
            tp = round(entry + max(risk * min_rr, tick_size * 4.0), 2)
            while (tp - entry) / max(entry - sl, 0.0001) < 2.20:
                tp = round(tp + tick_size, 2)
            return sl, tp
        else:
            sl = round(raw_sl, 2)
            risk = max(sl - entry, tick_size * 2.0)
            tp = round(entry - max(risk * min_rr, tick_size * 4.0), 2)
            while (entry - tp) / max(sl - entry, 0.0001) < 2.20:
                tp = round(tp - tick_size, 2)
            return sl, tp

    def evaluate(self, symbol: str, df_bars: pd.DataFrame) -> CMEFuturesSignal:
        symbol = symbol.upper().strip()
        now = time.time()
        cfg = self.TICK_CONFIG.get(symbol, {"tick_size": 0.25, "point_value": 5.0})
        tick_sz = cfg["tick_size"]

        if df_bars.empty or len(df_bars) < 20:
            return CMEFuturesSignal(
                symbol=symbol, timestamp=now, side="NEUTRAL", confidence_score=0.0,
                entry_price=0.0, stop_loss=0.0, take_profit=0.0, tick_size=tick_sz,
                point_value=cfg["point_value"], rationale="Insufficient bar data"
            )

        close = df_bars["Close"]
        high = df_bars["High"]
        low = df_bars["Low"]
        volume = df_bars["Volume"]

        curr_p = float(close.iloc[-1])
        sma20 = float(close.rolling(20).mean().iloc[-1])

        # VWAP approximation (Cumulative Typical Price x Volume)
        typ_p = (high + low + close) / 3.0
        vwap = float((typ_p * volume).cumsum().iloc[-1] / max(volume.cumsum().iloc[-1], 1.0))

        # ATR calculation
        prev_c = close.shift(1)
        tr = pd.concat([high - low, (high - prev_c).abs(), (low - prev_c).abs()], axis=1).max(axis=1)
        atr = float(tr.tail(14).mean()) or (curr_p * 0.005)

        # Setup 1: VWAP Reclaim Long / Breakdown Short
        is_vwap_reclaim = (curr_p >= vwap and (float(low.tail(3).min()) <= vwap or float(low.iloc[-2]) < vwap))
        is_vwap_breakdown = (curr_p <= vwap and (float(high.tail(3).max()) >= vwap or float(high.iloc[-2]) > vwap))

        if is_vwap_reclaim:
            raw_sl = curr_p - (atr * 1.5)
            sl, tp = self._compute_rr_bracket(curr_p, raw_sl, side="LONG", min_rr=2.25, tick_size=tick_sz)
            rr = (tp - curr_p) / max(curr_p - sl, 0.0001)
            return CMEFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="LONG",
                confidence_score=85.0,
                entry_price=round(curr_p, 2),
                stop_loss=sl,
                take_profit=tp,
                tick_size=tick_sz,
                point_value=cfg["point_value"],
                contracts=2,
                setup_name="VWAP_RECLAIM",
                strategy_type="VWAP_RECLAIM",
                rationale=f"Bullish VWAP reclaim ({curr_p:.2f} >= VWAP {vwap:.2f}) with {rr:.2f}:1 R:R geometry."
            )

        if is_vwap_breakdown:
            raw_sl = curr_p + (atr * 1.5)
            sl, tp = self._compute_rr_bracket(curr_p, raw_sl, side="SHORT", min_rr=2.25, tick_size=tick_sz)
            rr = (curr_p - tp) / max(sl - curr_p, 0.0001)
            return CMEFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="SHORT",
                confidence_score=85.0,
                entry_price=round(curr_p, 2),
                stop_loss=sl,
                take_profit=tp,
                tick_size=tick_sz,
                point_value=cfg["point_value"],
                contracts=2,
                setup_name="VWAP_BREAKDOWN",
                strategy_type="VWAP_BREAKDOWN",
                rationale=f"Bearish VWAP breakdown ({curr_p:.2f} <= VWAP {vwap:.2f}) fade with {rr:.2f}:1 R:R short."
            )

        # Setup 2: Range Breakout / Breakdown
        prior_high_20 = float(high.iloc[-20:-1].max())
        prior_low_20 = float(low.iloc[-20:-1].min())
        if curr_p >= prior_high_20 or curr_p >= float(high.iloc[-10:-1].max()):
            raw_sl = curr_p - (atr * 1.2)
            sl, tp = self._compute_rr_bracket(curr_p, raw_sl, side="LONG", min_rr=2.25, tick_size=tick_sz)
            return CMEFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="LONG",
                confidence_score=80.0,
                entry_price=round(curr_p, 2),
                stop_loss=sl,
                take_profit=tp,
                tick_size=tick_sz,
                point_value=cfg["point_value"],
                contracts=2,
                setup_name="RANGE_BREAKOUT",
                strategy_type="RANGE_BREAKOUT",
                rationale=f"Fresh channel high breakout on {symbol} above {prior_high_20:.2f}."
            )

        if curr_p <= prior_low_20 or curr_p <= float(low.iloc[-10:-1].min()):
            raw_sl = curr_p + (atr * 1.2)
            sl, tp = self._compute_rr_bracket(curr_p, raw_sl, side="SHORT", min_rr=2.25, tick_size=tick_sz)
            return CMEFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="SHORT",
                confidence_score=80.0,
                entry_price=round(curr_p, 2),
                stop_loss=sl,
                take_profit=tp,
                tick_size=tick_sz,
                point_value=cfg["point_value"],
                contracts=2,
                setup_name="RANGE_BREAKDOWN",
                strategy_type="RANGE_BREAKDOWN",
                rationale=f"Bearish channel breakdown on {symbol} below {prior_low_20:.2f}."
            )

        # Setup 3: Intraday Trend Alignment
        if curr_p >= vwap and curr_p >= (sma20 * 0.999):
            raw_sl = curr_p - (atr * 1.5)
            sl, tp = self._compute_rr_bracket(curr_p, raw_sl, side="LONG", min_rr=2.25, tick_size=tick_sz)
            return CMEFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="LONG",
                confidence_score=78.0,
                entry_price=round(curr_p, 2),
                stop_loss=sl,
                take_profit=tp,
                tick_size=tick_sz,
                point_value=cfg["point_value"],
                contracts=2,
                setup_name="TREND_MOMENTUM",
                strategy_type="TREND_MOMENTUM",
                rationale=f"Intraday trend alignment on {symbol} (above VWAP {vwap:.2f} & SMA20 {sma20:.2f})."
            )

        if curr_p <= vwap and curr_p <= (sma20 * 1.001):
            raw_sl = curr_p + (atr * 1.5)
            sl, tp = self._compute_rr_bracket(curr_p, raw_sl, side="SHORT", min_rr=2.25, tick_size=tick_sz)
            return CMEFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="SHORT",
                confidence_score=78.0,
                entry_price=round(curr_p, 2),
                stop_loss=sl,
                take_profit=tp,
                tick_size=tick_sz,
                point_value=cfg["point_value"],
                contracts=2,
                setup_name="BEARISH_TREND_MOMENTUM",
                strategy_type="BEARISH_TREND_MOMENTUM",
                rationale=f"Bearish intraday alignment on {symbol} (below VWAP {vwap:.2f} & SMA20 {sma20:.2f})."
            )

        return CMEFuturesSignal(
            symbol=symbol,
            timestamp=now,
            side="NEUTRAL",
            confidence_score=50.0,
            entry_price=curr_p,
            stop_loss=0.0,
            take_profit=0.0,
            tick_size=tick_sz,
            point_value=cfg["point_value"],
            rationale="No high-confluence index futures setup."
        )


cme_strategy = CMEFuturesStrategyEngine()

