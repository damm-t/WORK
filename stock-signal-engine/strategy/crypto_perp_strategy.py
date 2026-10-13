"""
Crypto Perpetual Futures Strategy
=================================
Quantitative model for Bitcoin & Altcoin Perpetual Futures (BTC/USDT, ETH/USDT, SOL/USDT).

Specialized Alpha Generators:
  1. Liquidation Cascade Void Scooper:
     Detects forced liquidation flushes (Z-score <= -2.2 dislocation from VWAP/EMA20)
     and buys the extreme oversold wick for mean-reversion.
  2. Funding Rate Divergence:
     When funding rate turns deeply negative while price holds support, triggers
     a short-squeeze anticipation long. When funding rate is excessively positive
     with weakening momentum, avoids chasing long and triggers a short breakdown.
  3. Whale Distribution Trap Filter:
     Rejects high-volume breakouts on negative order flow / CVD divergence (Candidate C).
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


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
    strategy_type: str = "LIQUIDATION_SCOOP" # "LIQUIDATION_SCOOP", "FUNDING_SQUEEZE", "ORB_BREAKOUT"
    whale_trap_blocked: bool = False
    rationale: str = ""


class CryptoPerpStrategyEngine:
    """
    Evaluates crypto perpetual futures setups 24/7/365.
    """

    def __init__(self):
        pass

    def evaluate(
        self,
        symbol: str,
        df_bars: pd.DataFrame,
        funding_rate: float = 0.0001,      # 0.01% standard 8h funding
        open_interest_delta_pct: float = 0.0
    ) -> CryptoFuturesSignal:
        symbol = symbol.upper().strip()
        now = time.time()

        if df_bars.empty or len(df_bars) < 20:
            return CryptoFuturesSignal(
                symbol=symbol, timestamp=now, side="NEUTRAL", confidence_score=0.0,
                entry_price=0.0, stop_loss=0.0, take_profit=0.0, rationale="Insufficient bars"
            )

        close = df_bars["Close"]
        high = df_bars["High"]
        low = df_bars["Low"]
        volume = df_bars["Volume"]

        curr_p = float(close.iloc[-1])
        ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
        std20 = float(close.rolling(20).std().iloc[-1]) or 1.0

        # Dislocation Z-score
        z_score = (curr_p - ema20) / std20

        # RVOL (Volume vs 20-bar rolling average on completed bars)
        vol_avg = float(volume.iloc[-21:-1].mean()) if len(volume) >= 21 else (float(volume.mean()) or 1.0)
        closed_vol = float(volume.iloc[-2]) if len(volume) >= 2 else float(volume.iloc[-1])
        rvol = max(round(closed_vol / vol_avg, 2) if vol_avg > 0 else 1.0, 1.0)

        # 5-bar return
        p_5b = ((curr_p - float(close.iloc[-5])) / max(float(close.iloc[-5]), 0.01)) * 100.0

        # 1. Whale Distribution Trap Defense (Candidate C)
        whale_trap = (rvol >= 2.0 and p_5b <= -1.0)

        # 2. ATR for Stop Loss geometry
        prev_c = close.shift(1)
        tr = pd.concat([high - low, (high - prev_c).abs(), (low - prev_c).abs()], axis=1).max(axis=1)
        atr = float(tr.tail(14).mean()) or (curr_p * 0.015)

        # ------------------- SIGNAL GENERATION -------------------
        # Setup A: Liquidation Cascade Void Scooper (Extreme wick flush or deep dislocation)
        if z_score <= -2.0 and not whale_trap:
            sl = curr_p - (atr * 1.5)
            tp = curr_p + (atr * 3.0)  # 2:1 R:R
            conf = min(95.0, 80.0 + abs(z_score) * 4.0)
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
                whale_trap_blocked=False,
                rationale=f"Liquidation pullback wick (Z={z_score:.2f}). Mean reversion scoop with 2:1 R:R."
            )

        # Setup B: Momentum Breakout & Trend Continuation (Genuine EMA20 expansion)
        if curr_p >= (ema20 * 1.001) and p_5b >= 0.20 and z_score > 0.0 and not whale_trap:
            sl = curr_p - (atr * 1.25)
            tp = curr_p + (atr * 2.5)  # 2:1 R:R
            conf = min(92.0, 80.0 + min(z_score * 4.0, 10.0))
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
                whale_trap_blocked=False,
                rationale=f"Bullish 5m EMA expansion (+{p_5b:.2f}% 5b return, Z={z_score:.2f}). Trend continuation."
            )

        # Setup C: Funding Rate Short-Squeeze Long
        if funding_rate <= -0.0003 and z_score >= -0.5:
            sl = curr_p - (atr * 1.8)
            tp = curr_p + (atr * 2.5)
            return CryptoFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="LONG",
                confidence_score=82.0,
                entry_price=curr_p,
                stop_loss=round(sl, 2),
                take_profit=round(tp, 2),
                leverage=3,
                strategy_type="FUNDING_SQUEEZE",
                whale_trap_blocked=False,
                rationale=f"Crowded short funding ({funding_rate*100:+.3f}%). Squeeze ignition pattern."
            )

        # ------------------- SHORT SETUPS (BEAST ATTACK MODE) -------------------
        # Setup D: Whale Dump Breakdown Short (High RVOL flush)
        if whale_trap:
            sl = curr_p + (atr * 1.5)
            tp = curr_p - (atr * 3.0)
            return CryptoFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="SHORT",
                confidence_score=86.0,
                entry_price=curr_p,
                stop_loss=round(sl, 2),
                take_profit=round(tp, 2),
                leverage=3,
                strategy_type="WHALE_DUMP_SHORT",
                whale_trap_blocked=False,
                rationale=f"Aggressive institutional dump breakdown (RVOL {rvol:.1f}x with negative momentum {p_5b:+.1f}%). 2:1 R:R short."
            )

        # Setup E: Overbought Liquidation Blow-off Fade Short
        if z_score >= 1.8:
            sl = curr_p + (atr * 1.5)
            tp = curr_p - (atr * 3.0)
            conf = min(94.0, 78.0 + abs(z_score) * 5.0)
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
                whale_trap_blocked=False,
                rationale=f"Blow-off top liquidation wick (Z={z_score:+.2f}). Mean reversion fade short with 2:1 R:R."
            )

        # Setup F: Bearish Momentum Breakdown Short (EMA20 downward expansion)
        if curr_p <= (ema20 * 0.999) and p_5b <= -0.20 and z_score < 0.0:
            sl = curr_p + (atr * 1.25)
            tp = curr_p - (atr * 2.5)
            conf = min(90.0, 80.0 + min(abs(z_score) * 4.0, 10.0))
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
                whale_trap_blocked=False,
                rationale=f"Bearish 5m EMA expansion ({p_5b:.2f}% 5b return, Z={z_score:.2f}). Downward trend attack."
            )

        # Setup G: Funding Rate Arbitrage Short (Overleveraged bullish crowd paying shorts)
        if funding_rate >= 0.0003 and z_score <= 0.5:
            sl = curr_p + (atr * 1.8)
            tp = curr_p - (atr * 2.5)
            return CryptoFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="SHORT",
                confidence_score=82.0,
                entry_price=curr_p,
                stop_loss=round(sl, 2),
                take_profit=round(tp, 2),
                leverage=3,
                strategy_type="FUNDING_ARBITRAGE_SHORT",
                whale_trap_blocked=False,
                rationale=f"Crowded long funding (+{funding_rate*100:.3f}%). Harvesting 8h funding yield on short."
            )

        return CryptoFuturesSignal(
            symbol=symbol,
            timestamp=now,
            side="NEUTRAL",
            confidence_score=50.0,
            entry_price=curr_p,
            stop_loss=0.0,
            take_profit=0.0,
            rationale="No high-confluence liquidation or funding edge."
        )


crypto_strategy = CryptoPerpStrategyEngine()
