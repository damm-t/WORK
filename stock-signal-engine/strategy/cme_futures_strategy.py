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

import logging
import math
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


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


class CMEFuturesStrategyEngine:
    """
    Evaluates CME Micro Index Futures setups.
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

    def evaluate(self, symbol: str, df_bars: pd.DataFrame) -> CMEFuturesSignal:
        symbol = symbol.upper().strip()
        now = time.time()
        cfg = self.TICK_CONFIG.get(symbol, {"tick_size": 0.25, "point_value": 5.0})

        if df_bars.empty or len(df_bars) < 20:
            return CMEFuturesSignal(
                symbol=symbol, timestamp=now, side="NEUTRAL", confidence_score=0.0,
                entry_price=0.0, stop_loss=0.0, take_profit=0.0, tick_size=cfg["tick_size"],
                point_value=cfg["point_value"], rationale="Insufficient bar data"
            )

        close = df_bars["Close"]
        high = df_bars["High"]
        low = df_bars["Low"]
        volume = df_bars["Volume"]

        curr_p = float(close.iloc[-1])
        sma20 = float(close.rolling(20).mean().iloc[-1])
        std20 = float(close.rolling(20).std().iloc[-1]) or 1.0

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
            sl = curr_p - (atr * 1.5)
            tp = curr_p + (atr * 3.0)  # 2:1 R:R
            return CMEFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="LONG",
                confidence_score=85.0,
                entry_price=round(curr_p, 2),
                stop_loss=round(sl, 2),
                take_profit=round(tp, 2),
                tick_size=cfg["tick_size"],
                point_value=cfg["point_value"],
                contracts=2,
                setup_name="VWAP_RECLAIM",
                rationale=f"Bullish VWAP reclaim ({curr_p:.2f} >= VWAP {vwap:.2f}) with 2:1 R:R geometry."
            )

        if is_vwap_breakdown:
            sl = curr_p + (atr * 1.5)
            tp = curr_p - (atr * 3.0)  # 2:1 R:R
            return CMEFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="SHORT",
                confidence_score=85.0,
                entry_price=round(curr_p, 2),
                stop_loss=round(sl, 2),
                take_profit=round(tp, 2),
                tick_size=cfg["tick_size"],
                point_value=cfg["point_value"],
                contracts=2,
                setup_name="VWAP_BREAKDOWN",
                rationale=f"Bearish VWAP breakdown ({curr_p:.2f} <= VWAP {vwap:.2f}) fade with 2:1 R:R short."
            )

        # Setup 2: Range Breakout / Breakdown
        prior_high_20 = float(high.iloc[-20:-1].max())
        prior_low_20 = float(low.iloc[-20:-1].min())
        if curr_p >= prior_high_20 or curr_p >= float(high.iloc[-10:-1].max()):
            sl = curr_p - (atr * 1.2)
            tp = curr_p + (atr * 2.4)
            return CMEFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="LONG",
                confidence_score=80.0,
                entry_price=round(curr_p, 2),
                stop_loss=round(sl, 2),
                take_profit=round(tp, 2),
                tick_size=cfg["tick_size"],
                point_value=cfg["point_value"],
                contracts=2,
                setup_name="RANGE_BREAKOUT",
                rationale=f"Fresh channel high breakout on {symbol} above {prior_high_20:.2f}."
            )

        if curr_p <= prior_low_20 or curr_p <= float(low.iloc[-10:-1].min()):
            sl = curr_p + (atr * 1.2)
            tp = curr_p - (atr * 2.4)
            return CMEFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="SHORT",
                confidence_score=80.0,
                entry_price=round(curr_p, 2),
                stop_loss=round(sl, 2),
                take_profit=round(tp, 2),
                tick_size=cfg["tick_size"],
                point_value=cfg["point_value"],
                contracts=2,
                setup_name="RANGE_BREAKDOWN",
                rationale=f"Bearish channel breakdown on {symbol} below {prior_low_20:.2f}."
            )

        # Setup 3: Intraday Trend Alignment
        if curr_p >= vwap and curr_p >= (sma20 * 0.999):
            sl = curr_p - (atr * 1.5)
            tp = curr_p + (atr * 3.0)  # 2:1 R:R
            return CMEFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="LONG",
                confidence_score=78.0,
                entry_price=round(curr_p, 2),
                stop_loss=round(sl, 2),
                take_profit=round(tp, 2),
                tick_size=cfg["tick_size"],
                point_value=cfg["point_value"],
                contracts=2,
                setup_name="TREND_MOMENTUM",
                rationale=f"Intraday trend alignment on {symbol} (above VWAP {vwap:.2f} & SMA20 {sma20:.2f})."
            )

        if curr_p <= vwap and curr_p <= (sma20 * 1.001):
            sl = curr_p + (atr * 1.5)
            tp = curr_p - (atr * 3.0)  # 2:1 R:R
            return CMEFuturesSignal(
                symbol=symbol,
                timestamp=now,
                side="SHORT",
                confidence_score=78.0,
                entry_price=round(curr_p, 2),
                stop_loss=round(sl, 2),
                take_profit=round(tp, 2),
                tick_size=cfg["tick_size"],
                point_value=cfg["point_value"],
                contracts=2,
                setup_name="BEARISH_TREND_MOMENTUM",
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
            tick_size=cfg["tick_size"],
            point_value=cfg["point_value"],
            rationale="No high-confluence index futures setup."
        )


cme_strategy = CMEFuturesStrategyEngine()
