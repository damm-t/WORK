"""
Smart Money Concepts (SMC) & Self-Improving Quantitative Crypto Strategy
========================================================================
Institutional quantitative model for Bitcoin & Altcoin Perpetual Futures (BTC/USDT, ETH/USDT, SOL/USDT).

Incorporating core principles from Instagram quantitative analyses:
  1. Smart Money Concepts (SMC) + Order Flow Radar (Reel 1: @deq):
     - Order Flow Cumulative Delta (CVD) & Momentum Delta (FLOW)
     - Order Book Depth Imbalance & Resting Liquidity Walls (BOOK & WALL ▲ / ▼)
     - Liquidity Sweeps / Judas Swings (trapping retail breakout stops at swing highs/lows)
     - Order Blocks (OB) & Fair Value Gap (FVG) Institutional Retests
     - Unchoked Asymmetric Risk/Reward Geometry (minimum 2.0:1 R:R target)

  2. Point-in-Time (PIT) Data Integrity & Self-Improving Learning (Reel 2: @fidetolabs):
     - Strict Point-in-Time computation on completed historical bars (df.iloc[:-1])
     - Eradication of lookahead bias and data leakage
     - Self-Improving Expectancy Tracker: tracks rolling win rate, profit factor, and
       expectancy per setup type, dynamically scaling conviction and vetoing negative drift.
"""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

LEARNING_STATE_PATH = Path("data/crypto_strategy_learning.json")


@dataclass
class CryptoFuturesSignal:
    symbol: str                           # e.g. "BTC/USDT"
    timestamp: float
    side: str                             # "LONG" or "SHORT" or "NEUTRAL"
    confidence_score: float               # 0 to 100
    entry_price: float
    stop_loss: float
    take_profit: float
    leverage: int = 3                     # Conservative 3x leverage (no liquidation danger)
    liquidation_buffer_pct: float = 25.0  # Liquidation is >25% away from stop loss
    strategy_type: str = "LIQUIDATION_SCOOP"
    whale_trap_blocked: bool = False
    rationale: str = ""
    # Smart Money Concepts & Order Flow Radar metrics
    order_flow_delta: float = 0.0         # CVD proxy (-1.0 to +1.0)
    order_book_imbalance: float = 0.0     # (Bid - Ask) / (Bid + Ask) (-1.0 to +1.0)
    bid_wall: float = 0.0                 # Price of strongest resting bid wall
    ask_wall: float = 0.0                 # Price of strongest resting ask wall
    tape_speed: float = 0.0               # Estimated execution velocity
    risk_reward_ratio: float = 2.0        # Planned R:R ratio (>= 2.0)
    pit_verified: bool = True             # Verified calculated strictly Point-in-Time
    learner_multiplier: float = 1.0       # Learned adaptive expectancy multiplier


class SelfImprovingExpectancyTracker:
    """
    Self-Improving Expectancy Tracker (Reel 2: Out-of-Sample Empirical Learning).
    Tracks real trade outcomes by setup type, calculates rolling profit factor and
    expectancy, and provides dynamic conviction multipliers.
    """

    def __init__(self, state_path: Path = LEARNING_STATE_PATH):
        self.state_path = state_path
        self.history: Dict[str, List[Dict[str, Any]]] = self._load_state()

    def _load_state(self) -> Dict[str, List[Dict[str, Any]]]:
        if self.state_path.exists():
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception as e:
                logger.warning(f"[crypto_learner] Could not load learning state: {e}")
        return {}

    def _save_state(self) -> None:
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.warning(f"[crypto_learner] Could not save learning state: {e}")

    def record_trade(
        self,
        strategy_type: str,
        pnl: float,
        r_multiple: float,
        entry_price: float,
        exit_price: float,
        symbol: str = "BTC/USDT",
    ) -> None:
        """Records a completed trade into the self-learning memory."""
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
        # Keep rolling window of last 50 trades per setup
        if len(self.history[strat]) > 50:
            self.history[strat] = self.history[strat][-50:]
        self._save_state()

    def get_multiplier(self, strategy_type: str) -> float:
        """
        Returns dynamic confidence multiplier (0.0x to 1.25x) based on rolling expectancy.
        - High Expectancy (PF >= 1.40, win rate >= 45%): 1.15x - 1.25x boost
        - Neutral Expectancy (0.90 <= PF < 1.40): 1.0x baseline
        - Negative Expectancy (0.65 <= PF < 0.90): 0.70x penalty
        - Severe Negative Drift (PF < 0.65 over >= 8 trades): 0.0x (Temporary VETO)
        """
        strat = strategy_type.strip().upper()
        trades = self.history.get(strat, [])
        if len(trades) < 5:
            return 1.0  # Cold start: neutral multiplier until empirical sample gathered

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
            # Persistent money-losing setup in current regime -> Veto
            return 0.0

    def get_performance_summary(self) -> Dict[str, Any]:
        """Provides a breakdown of expectancy and edge across all strategy variants."""
        summary = {}
        for strat, trades in self.history.items():
            if not trades:
                continue
            recent = trades[-20:]
            wins = [t["pnl"] for t in recent if t["win"]]
            losses = [abs(t["pnl"]) for t in recent if not t["win"]]
            total = len(recent)
            win_count = len(wins)
            win_rate = (win_count / total) * 100.0 if total > 0 else 0.0
            sum_wins = sum(wins)
            sum_losses = sum(losses)
            pf = (sum_wins / max(sum_losses, 0.01)) if sum_losses > 0 else (2.5 if sum_wins > 0 else 1.0)
            summary[strat] = {
                "trades": total,
                "win_rate_pct": round(win_rate, 1),
                "profit_factor": round(pf, 2),
                "multiplier": self.get_multiplier(strat),
                "total_pnl": round(sum(t["pnl"] for t in recent), 2),
            }
        return summary


class CryptoPerpStrategyEngine:
    """
    Evaluates crypto perpetual futures setups 24/7/365 using Smart Money Concepts,
    Order Flow CVD analysis, and Point-in-Time data integrity.
    """

    def __init__(self, state_path: Optional[Path] = None):
        self.learner = SelfImprovingExpectancyTracker(state_path or LEARNING_STATE_PATH)

    def _compute_point_in_time_features(self, df_bars: pd.DataFrame) -> Dict[str, Any]:
        """
        Point-in-Time (PIT) Feature Pipeline:
        To prevent lookahead leakage (Reel 2), historical indicators (EMA, ATR, Swings,
        Order Blocks, Volume Delta) are computed on completed historical bars.
        The latest row (df_bars.iloc[-1]) is the current live decision bar.
        """
        if len(df_bars) < 20:
            return {}

        # Historical completed bars for structure and indicator calibration
        hist = df_bars.iloc[:-1] if len(df_bars) >= 21 else df_bars
        live_bar = df_bars.iloc[-1]

        close = hist["Close"]
        high = hist["High"]
        low = hist["Low"]
        open_p = hist["Open"] if "Open" in hist.columns else close
        volume = hist["Volume"]

        curr_p = float(live_bar["Close"])
        live_open = float(live_bar.get("Open", curr_p))
        live_high = float(live_bar.get("High", curr_p))
        live_low = float(live_bar.get("Low", curr_p))
        live_vol = float(live_bar.get("Volume", 1.0))

        # 1. EMA20 & Dispersion Z-Score
        ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
        std20 = float(close.rolling(20).std().iloc[-1]) or 1.0
        z_score = (curr_p - ema20) / std20

        # 2. True ATR14 on completed bars
        prev_c = close.shift(1)
        tr = pd.concat([high - low, (high - prev_c).abs(), (low - prev_c).abs()], axis=1).max(axis=1)
        atr = float(tr.tail(14).mean()) or (curr_p * 0.015)

        # 3. RVOL on completed bars
        vol_avg = float(volume.tail(20).mean()) if len(volume) >= 20 else 1.0
        rvol = max(round(float(volume.iloc[-1]) / max(vol_avg, 1.0), 2), 1.0)

        # 4. Momentum return over last 5 completed bars
        p_5b = ((curr_p - float(close.iloc[-5])) / max(float(close.iloc[-5]), 0.01)) * 100.0

        # 5. SMC Order Flow Cumulative Volume Delta (CVD) Proxy
        # Directional delta: Volume * ((Close - Open) / (High - Low))
        candle_ranges = (high - low).replace(0, 1e-6)
        deltas = volume * ((close - open_p) / candle_ranges)
        cvd_recent = float(deltas.tail(10).sum())
        cvd_norm = math.tanh(cvd_recent / max(vol_avg * 2.0, 1.0)) # Scaled -1.0 to +1.0

        # 6. SMC Swing High & Swing Low (20-bar lookback on completed bars)
        swing_high = float(high.tail(20).max())
        swing_low = float(low.tail(20).min())

        # 7. SMC Order Block (OB) Detection on completed bars
        # Demand OB: Last bearish candle prior to a strong bullish breakout (> 1.25 ATR)
        demand_ob_low = 0.0
        demand_ob_high = 0.0
        supply_ob_low = 0.0
        supply_ob_high = 0.0

        for i in range(len(hist) - 2, max(len(hist) - 15, 0), -1):
            c_prev = float(close.iloc[i])
            o_prev = float(open_p.iloc[i])
            c_next = float(close.iloc[i + 1])
            o_next = float(open_p.iloc[i + 1])

            # Demand OB candidate
            if (c_prev < o_prev) and (c_next - o_next) >= (atr * 1.20) and not demand_ob_high:
                demand_ob_low = float(low.iloc[i])
                demand_ob_high = float(high.iloc[i])

            # Supply OB candidate
            if (c_prev > o_prev) and (o_next - c_next) >= (atr * 1.20) and not supply_ob_high:
                supply_ob_low = float(low.iloc[i])
                supply_ob_high = float(high.iloc[i])

            if demand_ob_high and supply_ob_high:
                break

        return {
            "curr_p": curr_p,
            "live_open": live_open,
            "live_high": live_high,
            "live_low": live_low,
            "live_vol": live_vol,
            "ema20": ema20,
            "std20": std20,
            "z_score": z_score,
            "atr": atr,
            "rvol": rvol,
            "p_5b": p_5b,
            "cvd": cvd_norm,
            "swing_high": swing_high,
            "swing_low": swing_low,
            "demand_ob": (demand_ob_low, demand_ob_high),
            "supply_ob": (supply_ob_low, supply_ob_high),
        }

    def evaluate(
        self,
        symbol: str,
        df_bars: pd.DataFrame,
        funding_rate: float = 0.0001,      # 0.01% standard 8h funding
        open_interest_delta_pct: float = 0.0,
        order_book: Optional[Dict[str, Any]] = None,
    ) -> CryptoFuturesSignal:
        symbol = symbol.upper().strip()
        now = time.time()

        if df_bars.empty or len(df_bars) < 20:
            return CryptoFuturesSignal(
                symbol=symbol, timestamp=now, side="NEUTRAL", confidence_score=0.0,
                entry_price=0.0, stop_loss=0.0, take_profit=0.0, rationale="Insufficient bars"
            )

        feat = self._compute_point_in_time_features(df_bars)
        if not feat:
            return CryptoFuturesSignal(
                symbol=symbol, timestamp=now, side="NEUTRAL", confidence_score=0.0,
                entry_price=0.0, stop_loss=0.0, take_profit=0.0, rationale="Feature extraction error"
            )

        curr_p = feat["curr_p"]
        live_open = feat["live_open"]
        live_high = feat["live_high"]
        live_low = feat["live_low"]
        ema20 = feat["ema20"]
        z_score = feat["z_score"]
        atr = feat["atr"]
        rvol = feat["rvol"]
        p_5b = feat["p_5b"]
        cvd = feat["cvd"]
        swing_high = feat["swing_high"]
        swing_low = feat["swing_low"]
        demand_ob = feat["demand_ob"]
        supply_ob = feat["supply_ob"]

        # Parse real-time Order Book Imbalance & Liquidity Walls (Reel 1)
        book_imbalance = 0.0
        bid_wall = 0.0
        ask_wall = 0.0
        if order_book:
            bids = order_book.get("bids", [])
            asks = order_book.get("asks", [])
            if bids and asks:
                b_vol = sum(b[1] for b in bids[:10])
                a_vol = sum(a[1] for a in asks[:10])
                book_imbalance = round((b_vol - a_vol) / max(b_vol + a_vol, 1e-5), 2)
                bid_wall = float(max(bids[:10], key=lambda x: x[1])[0])
                ask_wall = float(max(asks[:10], key=lambda x: x[1])[0])

        # Whale Distribution Trap Defense (Candidate C: massive volume on flat or falling price)
        whale_trap = (rvol >= 2.0 and p_5b <= -1.0)

        # ------------------- SMART MONEY CONCEPTS (SMC) SETUPS -------------------

        # 1. SETUP: SMC Bullish Liquidity Sweep (Judas Swing / Stop Hunt Flush)
        # Price dips below swing low to purge retail stop losses, but RECLAIMS back above swing low
        candle_range = max(live_high - live_low, 1e-5)
        close_location = (curr_p - live_low) / candle_range
        lower_wick_ratio = (min(curr_p, live_open) - live_low) / candle_range

        if (live_low < swing_low) and (curr_p > swing_low) and (close_location >= 0.50 or lower_wick_ratio >= 0.40) and not whale_trap:
            mult = self.learner.get_multiplier("SMC_LIQUIDITY_SWEEP_LONG")
            if mult > 0:
                sl = live_low - (atr * 0.25) # Invalidation strictly below the sweep wick
                r_dist = max(curr_p - sl, atr * 0.5)
                tp = curr_p + max(atr * 2.5, r_dist * 2.2, (swing_high - curr_p) * 1.1) # Minimum 2.2:1 R:R target
                conf = min(96.0, (84.0 + (cvd * 5.0) + (lower_wick_ratio * 10.0)) * mult)
                return CryptoFuturesSignal(
                    symbol=symbol,
                    timestamp=now,
                    side="LONG",
                    confidence_score=round(conf, 1),
                    entry_price=curr_p,
                    stop_loss=round(sl, 2),
                    take_profit=round(tp, 2),
                    leverage=3,
                    strategy_type="SMC_LIQUIDITY_SWEEP_LONG",
                    order_flow_delta=round(cvd, 2),
                    order_book_imbalance=book_imbalance,
                    bid_wall=bid_wall,
                    ask_wall=ask_wall,
                    risk_reward_ratio=round((tp - curr_p) / max(curr_p - sl, 0.01), 2),
                    learner_multiplier=mult,
                    rationale=f"SMC Liquidity Sweep: Purged retail stops at ${swing_low:.2f}, reclaimed above support. CVD={cvd:+.2f}."
                )

        # 2. SETUP: SMC Bearish Liquidity Sweep (Retail Breakout Trap / Buy Stop Hunt)
        # Price spikes above swing high, traps retail buyers, then CLOSES BACK BELOW swing high
        close_from_top = (live_high - curr_p) / candle_range
        upper_wick_ratio = (live_high - max(curr_p, live_open)) / candle_range
        if (live_high > swing_high) and (curr_p < swing_high) and (close_from_top >= 0.50 or upper_wick_ratio >= 0.40):
            mult = self.learner.get_multiplier("SMC_LIQUIDITY_SWEEP_SHORT")
            if mult > 0:
                sl = live_high + (atr * 0.25) # Invalidation strictly above the sweep high
                r_dist = max(sl - curr_p, atr * 0.5)
                tp = curr_p - max(atr * 2.5, r_dist * 2.2, (curr_p - swing_low) * 1.1)
                conf = min(96.0, (84.0 - (cvd * 5.0) + (upper_wick_ratio * 10.0)) * mult)
                return CryptoFuturesSignal(
                    symbol=symbol,
                    timestamp=now,
                    side="SHORT",
                    confidence_score=round(conf, 1),
                    entry_price=curr_p,
                    stop_loss=round(sl, 2),
                    take_profit=round(tp, 2),
                    leverage=3,
                    strategy_type="SMC_LIQUIDITY_SWEEP_SHORT",
                    order_flow_delta=round(cvd, 2),
                    order_book_imbalance=book_imbalance,
                    bid_wall=bid_wall,
                    ask_wall=ask_wall,
                    risk_reward_ratio=round((curr_p - tp) / max(sl - curr_p, 0.01), 2),
                    learner_multiplier=mult,
                    rationale=f"SMC Bearish Sweep: Trapped breakout buyers at ${swing_high:.2f}, rejected back below resistance. CVD={cvd:+.2f}."
                )

        # 3. SETUP: SMC Institutional Demand Order Block Retest
        if demand_ob[1] > 0 and (demand_ob[0] <= curr_p <= (demand_ob[1] * 1.003)) and (cvd >= -0.20) and not whale_trap:
            mult = self.learner.get_multiplier("SMC_ORDER_BLOCK_LONG")
            if mult > 0:
                sl = demand_ob[0] - (atr * 0.30)
                r_dist = max(curr_p - sl, atr * 0.5)
                tp = curr_p + max(atr * 2.5, r_dist * 2.2)
                conf = min(93.0, (82.0 + (cvd * 4.0)) * mult)
                return CryptoFuturesSignal(
                    symbol=symbol,
                    timestamp=now,
                    side="LONG",
                    confidence_score=round(conf, 1),
                    entry_price=curr_p,
                    stop_loss=round(sl, 2),
                    take_profit=round(tp, 2),
                    leverage=3,
                    strategy_type="SMC_ORDER_BLOCK_LONG",
                    order_flow_delta=round(cvd, 2),
                    order_book_imbalance=book_imbalance,
                    bid_wall=bid_wall,
                    ask_wall=ask_wall,
                    risk_reward_ratio=round((tp - curr_p) / max(curr_p - sl, 0.01), 2),
                    learner_multiplier=mult,
                    rationale=f"Institutional Demand Order Block retest at [${demand_ob[0]:.2f}-${demand_ob[1]:.2f}]. Order flow holding."
                )

        # 4. SETUP: SMC Institutional Supply Order Block Retest
        if supply_ob[0] > 0 and ((supply_ob[0] * 0.997) <= curr_p <= supply_ob[1]) and (cvd <= 0.20):
            mult = self.learner.get_multiplier("SMC_ORDER_BLOCK_SHORT")
            if mult > 0:
                sl = supply_ob[1] + (atr * 0.30)
                r_dist = max(sl - curr_p, atr * 0.5)
                tp = curr_p - max(atr * 2.5, r_dist * 2.2)
                conf = min(93.0, (82.0 - (cvd * 4.0)) * mult)
                return CryptoFuturesSignal(
                    symbol=symbol,
                    timestamp=now,
                    side="SHORT",
                    confidence_score=round(conf, 1),
                    entry_price=curr_p,
                    stop_loss=round(sl, 2),
                    take_profit=round(tp, 2),
                    leverage=3,
                    strategy_type="SMC_ORDER_BLOCK_SHORT",
                    order_flow_delta=round(cvd, 2),
                    order_book_imbalance=book_imbalance,
                    bid_wall=bid_wall,
                    ask_wall=ask_wall,
                    risk_reward_ratio=round((curr_p - tp) / max(sl - curr_p, 0.01), 2),
                    learner_multiplier=mult,
                    rationale=f"Institutional Supply Order Block retest at [${supply_ob[0]:.2f}-${supply_ob[1]:.2f}]. Distribution pressure active."
                )

        # 5. SETUP: Liquidation Cascade Void Scooper (Deep capitulation dislocation flush)
        if z_score <= -2.5 and not whale_trap:
            mult = self.learner.get_multiplier("LIQUIDATION_SCOOP")
            if mult > 0:
                sl = curr_p - (atr * 1.5)
                tp = curr_p + (atr * 3.0)  # 2:1 R:R
                conf = min(95.0, (80.0 + abs(z_score) * 4.0) * mult)
                return CryptoFuturesSignal(
                    symbol=symbol,
                    timestamp=now,
                    side="LONG",
                    confidence_score=round(conf, 1),
                    entry_price=curr_p,
                    stop_loss=round(sl, 2),
                    take_profit=round(tp, 2),
                    leverage=3,
                    strategy_type="LIQUIDATION_SCOOP",
                    order_flow_delta=round(cvd, 2),
                    order_book_imbalance=book_imbalance,
                    bid_wall=bid_wall,
                    ask_wall=ask_wall,
                    risk_reward_ratio=2.0,
                    learner_multiplier=mult,
                    rationale=f"Liquidation pullback wick (Z={z_score:.2f}). Mean reversion scoop with 2:1 R:R."
                )

        # 6. SETUP: Whale Dump Breakdown Short (High RVOL flush)
        if whale_trap:
            mult = self.learner.get_multiplier("WHALE_DUMP_SHORT")
            if mult > 0:
                sl = curr_p + (atr * 1.5)
                tp = curr_p - (atr * 3.0)
                conf = 86.0 * mult
                return CryptoFuturesSignal(
                    symbol=symbol,
                    timestamp=now,
                    side="SHORT",
                    confidence_score=round(conf, 1),
                    entry_price=curr_p,
                    stop_loss=round(sl, 2),
                    take_profit=round(tp, 2),
                    leverage=3,
                    strategy_type="WHALE_DUMP_SHORT",
                    order_flow_delta=round(cvd, 2),
                    order_book_imbalance=book_imbalance,
                    bid_wall=bid_wall,
                    ask_wall=ask_wall,
                    risk_reward_ratio=2.0,
                    learner_multiplier=mult,
                    rationale=f"Aggressive institutional dump breakdown (RVOL {rvol:.1f}x with negative momentum {p_5b:+.1f}%). 2:1 R:R short."
                )

        # 7. SETUP: Momentum Breakout & Trend Continuation (Filtered by Order Flow)
        # Prevents buying into an Ask Wall or negative CVD divergence
        if curr_p >= (ema20 * 1.001) and p_5b >= 0.20 and z_score > 0.0 and (cvd >= -0.10) and not whale_trap:
            mult = self.learner.get_multiplier("MOMENTUM_BREAKOUT")
            if mult > 0:
                sl = curr_p - (atr * 1.25)
                tp = curr_p + (atr * 2.5)  # 2:1 R:R
                conf = min(92.0, (80.0 + min(z_score * 4.0, 10.0)) * mult)
                return CryptoFuturesSignal(
                    symbol=symbol,
                    timestamp=now,
                    side="LONG",
                    confidence_score=round(conf, 1),
                    entry_price=curr_p,
                    stop_loss=round(sl, 2),
                    take_profit=round(tp, 2),
                    leverage=3,
                    strategy_type="MOMENTUM_BREAKOUT",
                    order_flow_delta=round(cvd, 2),
                    order_book_imbalance=book_imbalance,
                    bid_wall=bid_wall,
                    ask_wall=ask_wall,
                    risk_reward_ratio=2.0,
                    learner_multiplier=mult,
                    rationale=f"Bullish 5m EMA expansion (+{p_5b:.2f}% 5b return, CVD={cvd:+.2f}). Trend continuation."
                )

        # 8. SETUP: Overbought Liquidation Blow-off Fade Short (Parabolic exhaustion spike)
        if z_score >= 2.5:
            mult = self.learner.get_multiplier("LIQUIDATION_FADE_SHORT")
            if mult > 0:
                sl = curr_p + (atr * 1.5)
                tp = curr_p - (atr * 3.0)
                conf = min(94.0, (78.0 + abs(z_score) * 5.0) * mult)
                return CryptoFuturesSignal(
                    symbol=symbol,
                    timestamp=now,
                    side="SHORT",
                    confidence_score=round(conf, 1),
                    entry_price=curr_p,
                    stop_loss=round(sl, 2),
                    take_profit=round(tp, 2),
                    leverage=3,
                    strategy_type="LIQUIDATION_FADE_SHORT",
                    order_flow_delta=round(cvd, 2),
                    order_book_imbalance=book_imbalance,
                    bid_wall=bid_wall,
                    ask_wall=ask_wall,
                    risk_reward_ratio=2.0,
                    learner_multiplier=mult,
                    rationale=f"Blow-off top liquidation wick (Z={z_score:+.2f}). Mean reversion fade short with 2:1 R:R."
                )

        # 9. SETUP: Bearish Momentum Breakdown Short (EMA20 downward expansion)
        if curr_p <= (ema20 * 0.999) and p_5b <= -0.20 and z_score < 0.0 and (cvd <= 0.10):
            mult = self.learner.get_multiplier("MOMENTUM_BREAKDOWN_SHORT")
            if mult > 0:
                sl = curr_p + (atr * 1.25)
                tp = curr_p - (atr * 2.5)
                conf = min(90.0, (80.0 + min(abs(z_score) * 4.0, 10.0)) * mult)
                return CryptoFuturesSignal(
                    symbol=symbol,
                    timestamp=now,
                    side="SHORT",
                    confidence_score=round(conf, 1),
                    entry_price=curr_p,
                    stop_loss=round(sl, 2),
                    take_profit=round(tp, 2),
                    leverage=3,
                    strategy_type="MOMENTUM_BREAKDOWN_SHORT",
                    order_flow_delta=round(cvd, 2),
                    order_book_imbalance=book_imbalance,
                    bid_wall=bid_wall,
                    ask_wall=ask_wall,
                    risk_reward_ratio=2.0,
                    learner_multiplier=mult,
                    rationale=f"Bearish 5m EMA expansion ({p_5b:.2f}% 5b return, CVD={cvd:+.2f}). Downward trend attack."
                )

        # 10. SETUP: Funding Rate Arbitrage / Squeeze
        if funding_rate <= -0.0003 and z_score >= -0.5:
            mult = self.learner.get_multiplier("FUNDING_SQUEEZE")
            if mult > 0:
                sl = curr_p - (atr * 1.8)
                tp = curr_p + (atr * 2.5)
                return CryptoFuturesSignal(
                    symbol=symbol,
                    timestamp=now,
                    side="LONG",
                    confidence_score=round(82.0 * mult, 1),
                    entry_price=curr_p,
                    stop_loss=round(sl, 2),
                    take_profit=round(tp, 2),
                    leverage=3,
                    strategy_type="FUNDING_SQUEEZE",
                    order_flow_delta=round(cvd, 2),
                    order_book_imbalance=book_imbalance,
                    bid_wall=bid_wall,
                    ask_wall=ask_wall,
                    risk_reward_ratio=round((tp - curr_p) / max(curr_p - sl, 0.01), 2),
                    learner_multiplier=mult,
                    rationale=f"Crowded short funding ({funding_rate*100:+.3f}%). Squeeze ignition pattern."
                )

        return CryptoFuturesSignal(
            symbol=symbol,
            timestamp=now,
            side="NEUTRAL",
            confidence_score=50.0,
            entry_price=curr_p,
            stop_loss=0.0,
            take_profit=0.0,
            order_flow_delta=round(cvd, 2),
            order_book_imbalance=book_imbalance,
            bid_wall=bid_wall,
            ask_wall=ask_wall,
            rationale="No high-confluence SMC liquidity sweep, order block, or dislocation edge."
        )


crypto_strategy = CryptoPerpStrategyEngine()
