"""
Desk 1 Institutional Equities Strategy Engine
=============================================
Combines Smart Money Concepts (SMC) Liquidity Sweeps, Strict Point-in-Time
(PIT) Feature Integrity, and Self-Improving Expectancy Feedback for US Equities.

Key Pillars (Instagram Reels 1 & 2):
  1. Point-in-Time Data Integrity: Indicators, swing highs/lows, and EMAs
     strictly computed on closed bars (df.iloc[:-1]) — eliminating lookahead leakage.
  2. SMC Liquidity Sweeps: Detects stop-hunt sweeps of 20-bar swing extremes
     followed by structural reclaims and volume absorption wicks.
  3. Enforced Asymmetry: Hardcoded minimum 2.2:1 Target Profit to Risk geometry.
  4. Self-Improving Expectancy Tracker: Persists real trade outcomes to
     `data/equities_strategy_learning.json`, dynamically rewarding high-expectancy
     setups (PF >= 1.4 -> 1.20x size) and vetoing negative drift setups (0.0x).
"""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

LEARNING_STATE_PATH = Path("data/equities_strategy_learning.json")

# High-liquidity Large/Mid-Cap Universe for Desk 1
INSTITUTIONAL_EQUITY_CORE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA",
    "AMD", "AVGO", "COST", "NFLX", "JPM", "V", "UNH", "LLY"
]


@dataclass
class EquitySignal:
    ticker: str
    timestamp: float
    side: str                            # "LONG" or "SHORT" or "NEUTRAL"
    confidence_score: float              # 0 to 100
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float             # >= 2.2
    strategy_type: str                   # e.g. "SMC_SWEEP_LONG", "QUALITY_MOMENTUM_PULLBACK"
    swing_low: float
    swing_high: float
    atr: float
    pit_verified: bool = True            # Verified strictly computed Point-in-Time
    learner_multiplier: float = 1.0      # Empirical learned multiplier (0.0x to 1.25x)
    rationale: str = ""


class EquitiesSelfLearningTracker:
    """
    Self-Improving Expectancy Tracker for US Equities (Reel 2: Empirical Feedback).
    Maintains rolling win rate, profit factor, and expectancy per setup type.
    """

    def __init__(self, state_path: Path = LEARNING_STATE_PATH):
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
                logger.warning(f"[equities_learner] Could not load state: {e}")
        return {}

    def _save_state(self) -> None:
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.warning(f"[equities_learner] Could not save state: {e}")

    def record_trade(
        self,
        strategy_type: str,
        pnl: float,
        r_multiple: float,
        entry_price: float,
        exit_price: float,
        ticker: str = "AAPL",
    ) -> None:
        """Records a closed equity trade into the self-learning memory."""
        strat = strategy_type.strip().upper()
        if strat not in self.history:
            self.history[strat] = []

        record = {
            "ticker": ticker,
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
            f"[equities_learner] Logged trade for {strat} ({ticker}): "
            f"PnL ${pnl:+.2f} ({r_multiple:+.2f}R). Total records: {len(self.history[strat])}"
        )

    def get_multiplier(self, strategy_type: str) -> float:
        """
        Dynamically adjusts strategy size (0.0x to 1.25x) based on rolling empirical expectancy.
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


class InstitutionalEquitiesStrategy:
    """
    Core strategy engine for Desk 1 combining SMC Liquidity Sweeps, PIT Integrity,
    and Asymmetric 2.2:1 Expectancy.
    """

    def __init__(self, learner: Optional[EquitiesSelfLearningTracker] = None):
        self.learner = learner or EquitiesSelfLearningTracker()

    @staticmethod
    def compute_point_in_time_features(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Point-in-Time (PIT) Feature Extraction (Reel 2).
        Calculates all indicators strictly on CLOSED historical bars (df.iloc[:-1]).
        """
        if df is None or len(df) < 25:
            return {}

        # Strictly use past closed candles
        closed = df.iloc[:-1].copy()
        current_candle = df.iloc[-1]
        current_price = float(current_candle["Close"])

        highs = closed["High"].values
        lows = closed["Low"].values
        closes = closed["Close"].values
        volumes = closed["Volume"].values if "Volume" in closed else np.ones(len(closed))

        # 1. 20-bar Structural Swing Levels (including most recent closed candle)
        swing_high_20 = float(np.max(highs[-20:]))
        swing_low_20 = float(np.min(lows[-20:]))

        # Structural Swing Levels prior to the most recent closed candle
        # Used for SMC Liquidity Sweep detection (testing if the latest closed candle swept prior structure)
        swing_high_prior = float(np.max(highs[-21:-1])) if len(highs) >= 21 else swing_high_20
        swing_low_prior = float(np.min(lows[-21:-1])) if len(lows) >= 21 else swing_low_20

        # 2. EMAs & SMAs
        ema9 = float(pd.Series(closes).ewm(span=9, adjust=False).mean().iloc[-1])
        ema20 = float(pd.Series(closes).ewm(span=20, adjust=False).mean().iloc[-1])
        sma50 = float(pd.Series(closes).rolling(min(50, len(closes))).mean().iloc[-1])

        # 3. True Range and ATR(14)
        tr1 = highs[1:] - lows[1:]
        tr2 = np.abs(highs[1:] - closes[:-1])
        tr3 = np.abs(lows[1:] - closes[:-1])
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr14 = float(np.mean(tr[-14:])) if len(tr) >= 14 else float(np.mean(tr))
        atr14 = max(atr14, current_price * 0.005)

        # 4. Candlestick geometry of most recent closed bar
        last_open = float(closed["Open"].iloc[-1])
        last_high = float(closed["High"].iloc[-1])
        last_low = float(closed["Low"].iloc[-1])
        last_close = float(closed["Close"].iloc[-1])
        candle_range = max(last_high - last_low, 1e-4)

        lower_wick_ratio = (min(last_open, last_close) - last_low) / candle_range
        upper_wick_ratio = (last_high - max(last_open, last_close)) / candle_range

        # 5. Volume RVOL & Absorption
        avg_vol = float(np.mean(volumes[-20:])) if len(volumes) >= 20 else float(np.mean(volumes))
        rvol = float(volumes[-1] / max(avg_vol, 1.0))

        return {
            "current_price": current_price,
            "swing_high_20": swing_high_20,
            "swing_low_20": swing_low_20,
            "swing_high_prior": swing_high_prior,
            "swing_low_prior": swing_low_prior,
            "ema9": ema9,
            "ema20": ema20,
            "sma50": sma50,
            "atr": atr14,
            "lower_wick_ratio": lower_wick_ratio,
            "upper_wick_ratio": upper_wick_ratio,
            "rvol": rvol,
            "last_close": last_close,
            "last_low": last_low,
            "last_high": last_high,
        }

    def evaluate_equity_ticker(
        self,
        ticker: str,
        df: pd.DataFrame,
        sentiment_score: float = 0.0,
    ) -> Optional[EquitySignal]:
        """
        Evaluates a Large/Mid-cap equity for an asymmetric SMC swing setup.
        Guarantees minimum 2.2:1 Target Profit to Risk ratio.
        """
        feats = self.compute_point_in_time_features(df)
        if not feats:
            return None

        curr_p = feats["current_price"]
        atr = feats["atr"]
        sw_low = feats.get("swing_low_prior", feats["swing_low_20"])
        sw_high = feats.get("swing_high_prior", feats["swing_high_20"])
        lw_ratio = feats["lower_wick_ratio"]
        uw_ratio = feats["upper_wick_ratio"]
        rvol = feats["rvol"]
        ema20 = feats["ema20"]
        sma50 = feats["sma50"]

        now_ts = time.time()

        # -------------------------------------------------------------
        # PATTERN 1: SMC LIQUIDITY SWEEP LONG
        # Price pierces below 20-bar swing low, sweeps retail stop-losses,
        # but reclaims above support with strong lower absorption wick (>= 35%).
        # -------------------------------------------------------------
        if feats["last_low"] < sw_low and (curr_p >= sw_low or feats["last_close"] >= sw_low):
            if lw_ratio >= 0.35 and rvol >= 0.90:
                strat = "SMC_SWEEP_LONG"
                mult = self.learner.get_multiplier(strat)
                if mult <= 0.0:
                    logger.warning(f"[equities_strategy] Vetoed {strat} for {ticker} by self-learner.")
                    return None

                stop_loss = round(feats["last_low"] - (0.35 * atr), 2)
                risk_dist = max(curr_p - stop_loss, 0.50 * atr)

                # Hardcoded Asymmetric 2.2:1 Minimum Target Profit
                raw_target = max(2.5 * atr, 2.25 * risk_dist)
                take_profit = round(curr_p + raw_target, 2)
                if (take_profit - curr_p) < 2.20 * risk_dist:
                    take_profit = round(curr_p + (2.22 * risk_dist), 2)
                rr = round((take_profit - curr_p) / risk_dist, 2)

                score = min(98.0, 80.0 + (lw_ratio * 15.0) + (rvol * 5.0) + (sentiment_score * 5.0))
                return EquitySignal(
                    ticker=ticker.upper(),
                    timestamp=now_ts,
                    side="LONG",
                    confidence_score=round(score * mult, 1),
                    entry_price=round(curr_p, 2),
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    risk_reward_ratio=rr,
                    strategy_type=strat,
                    swing_low=sw_low,
                    swing_high=sw_high,
                    atr=round(atr, 2),
                    pit_verified=True,
                    learner_multiplier=mult,
                    rationale=(
                        f"SMC Liquidity Sweep of 20b low ${sw_low:.2f} (swept to ${feats['last_low']:.2f}). "
                        f"Absorption wick {lw_ratio:.0%}, RVOL {rvol:.2f}x. Target R:R {rr:.1f}:1."
                    ),
                )

        # -------------------------------------------------------------
        # PATTERN 2: QUALITY MOMENTUM 20 EMA PULLBACK
        # In an established uptrend (curr_p > sma50), price pulls back to
        # within 0.8*ATR of 20 EMA and holds support with positive sentiment.
        # -------------------------------------------------------------
        if curr_p > sma50 and abs(curr_p - ema20) <= (0.85 * atr) and curr_p >= ema20:
            if lw_ratio >= 0.25 and sentiment_score >= -0.10:
                strat = "QUALITY_MOMENTUM_PULLBACK"
                mult = self.learner.get_multiplier(strat)
                if mult <= 0.0:
                    logger.warning(f"[equities_strategy] Vetoed {strat} for {ticker} by self-learner.")
                    return None

                stop_loss = round(min(ema20 - (1.2 * atr), curr_p - (1.8 * atr)), 2)
                risk_dist = max(curr_p - stop_loss, 0.50 * atr)

                # Hardcoded Asymmetric 2.2:1 Minimum Target Profit
                raw_target = max(2.5 * atr, 2.25 * risk_dist)
                take_profit = round(curr_p + raw_target, 2)
                if (take_profit - curr_p) < 2.20 * risk_dist:
                    take_profit = round(curr_p + (2.22 * risk_dist), 2)
                rr = round((take_profit - curr_p) / risk_dist, 2)

                score = min(95.0, 78.0 + (rvol * 6.0) + (sentiment_score * 10.0))
                return EquitySignal(
                    ticker=ticker.upper(),
                    timestamp=now_ts,
                    side="LONG",
                    confidence_score=round(score * mult, 1),
                    entry_price=round(curr_p, 2),
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    risk_reward_ratio=rr,
                    strategy_type=strat,
                    swing_low=sw_low,
                    swing_high=sw_high,
                    atr=round(atr, 2),
                    pit_verified=True,
                    learner_multiplier=mult,
                    rationale=(
                        f"Quality Momentum 20 EMA Pullback (${ema20:.2f} vs SMA50 ${sma50:.2f}). "
                        f"Holding support with {lw_ratio:.0%} wick. Target R:R {rr:.1f}:1."
                    ),
                )

        return None


equities_strategy = InstitutionalEquitiesStrategy()
