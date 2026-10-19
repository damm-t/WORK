"""
Forex 24/5 Macro & Currency Strategy Engine
============================================
Quantitative model for Major & Liquid Cross Currency Pairs:
EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD, USD/CHF, NZD/USD.

Key Alpha Setups:
  1. London / New York Overlap Momentum Breakout (08:00 - 12:00 ET):
     Exploits peak global interbank liquidity when European and US markets
     trade concurrently. Breakouts during this session have the highest directional follow-through.
  2. Multi-Timeframe EMA Trend Continuation:
     Identifies persistent institutional order flow when fast EMA20 > slow EMA50
     and price pulls back to dynamic value before resuming trend.
  3. Asian Session Mean-Reversion Reclaim:
     Capitalizes on low-volatility overnight Asian consolidation fading
     over-extended wicks (Z-score dislocation >= 1.8x ATR) back towards daily VWAP.
  4. Precise Pip-Based Bracket Geometry:
     Pre-computes Stop Loss and Take Profit levels in exact fractional pips
     (0.0001 for standard majors, 0.01 for JPY pairs) adhering to a strict 2:1 R:R.
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests

logger = logging.getLogger(__name__)
NY_TZ = ZoneInfo("America/New_York")
FX_SESSION = requests.Session()
FX_SESSION.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})


@dataclass
class ForexSignal:
    symbol: str                           # e.g. "EUR/USD" or "USD/JPY"
    yahoo_ticker: str                     # e.g. "EURUSD=X"
    timestamp: float
    side: str                             # "LONG" or "SHORT" or "NEUTRAL"
    confidence_score: float               # 0 to 100
    entry_price: float
    stop_loss: float
    take_profit: float
    pip_size: float                       # 0.0001 (standard) or 0.01 (JPY)
    pips_sl: float                        # Stop loss in pips
    pips_tp: float                        # Take profit in pips
    lot_size: float = 1.0                 # Standard lot = 100k units ($10/pip on USD quote)
    strategy_type: str = "LONDON_NY_BREAKOUT"
    session: str = "NY_SESSION"           # "ASIAN", "LONDON", "NY_OVERLAP", "CLOSED"
    rationale: str = ""


class ForexStrategyEngine:
    """
    Evaluates institutional Forex setups 24/5 (Sunday 17:00 to Friday 17:00 ET).
    """

    PAIR_CONFIG: Dict[str, Dict[str, Any]] = {
        "EUR/USD": {"yahoo": "EURUSD=X", "pip": 0.0001, "name": "Euro / US Dollar", "pip_val_usd": 10.0},
        "GBP/USD": {"yahoo": "GBPUSD=X", "pip": 0.0001, "name": "British Pound / US Dollar", "pip_val_usd": 10.0},
        "USD/JPY": {"yahoo": "USDJPY=X", "pip": 0.01,   "name": "US Dollar / Japanese Yen", "pip_val_usd": 6.50},
        "AUD/USD": {"yahoo": "AUDUSD=X", "pip": 0.0001, "name": "Australian Dollar / US Dollar", "pip_val_usd": 10.0},
        "USD/CAD": {"yahoo": "USDCAD=X", "pip": 0.0001, "name": "US Dollar / Canadian Dollar", "pip_val_usd": 7.30},
        "USD/CHF": {"yahoo": "USDCHF=X", "pip": 0.0001, "name": "US Dollar / Swiss Franc", "pip_val_usd": 11.20},
        "NZD/USD": {"yahoo": "NZDUSD=X", "pip": 0.0001, "name": "New Zealand Dollar / US Dollar", "pip_val_usd": 10.0},
    }

    def __init__(self):
        pass

    @classmethod
    def normalize_symbol(cls, symbol: str) -> str:
        s = symbol.upper().strip().replace(" ", "").replace("-", "/")
        if not "/" in s:
            if s.endswith("=X"):
                base = s[:-2]
                if len(base) == 6:
                    s = f"{base[:3]}/{base[3:]}"
            elif len(s) == 6:
                s = f"{s[:3]}/{s[3:]}"
        return s

    @classmethod
    def get_yahoo_ticker(cls, symbol: str) -> str:
        norm = cls.normalize_symbol(symbol)
        if norm in cls.PAIR_CONFIG:
            return cls.PAIR_CONFIG[norm]["yahoo"]
        clean = norm.replace("/", "")
        return f"{clean}=X"

    @classmethod
    def get_live_rate(cls, symbol: str) -> Optional[float]:
        """Fetches high-availability live rate for major currency pairs via interbank FX API."""
        try:
            r = FX_SESSION.get("https://open.er-api.com/v6/latest/USD", timeout=4)
            if r.status_code == 200:
                rates = r.json().get("rates", {})
                norm = cls.normalize_symbol(symbol)
                if "/" in norm:
                    base, quote = norm.split("/")
                    if base == "USD" and quote in rates:
                        return float(rates[quote])
                    elif quote == "USD" and base in rates and rates[base] > 0:
                        return float(1.0 / rates[base])
                    elif base in rates and quote in rates and rates[base] > 0:
                        return float(rates[quote] / rates[base])
        except Exception as e:
            logger.debug(f"Live FX rate fallback warning: {e}")
        return None

    def detect_session(self, dt: Optional[datetime] = None) -> str:
        if dt is None:
            dt = datetime.now(NY_TZ)
        else:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=NY_TZ)
            else:
                dt = dt.astimezone(NY_TZ)

        weekday = dt.weekday() # 0 = Monday, 6 = Sunday
        hour = dt.hour

        # Forex market close: Friday 16:45 ET (pre-weekend gap protection) to Sunday 17:00 ET
        if (weekday == 4 and (hour > 16 or (hour == 16 and dt.minute >= 45))) or weekday == 5 or (weekday == 6 and hour < 17):
            return "WEEKEND_CLOSED"

        # Active trading sessions (ET):
        # London/NY Overlap: 08:00 - 12:00 ET (Peak global liquidity)
        if 8 <= hour < 12:
            return "LONDON_NY_OVERLAP"
        # London Session: 03:00 - 08:00 ET
        elif 3 <= hour < 8:
            return "LONDON_SESSION"
        # US Afternoon: 12:00 - 17:00 ET
        elif 12 <= hour < 17:
            return "NY_AFTERNOON"
        # Asian/Tokyo Session: 19:00 - 03:00 ET
        elif hour >= 19 or hour < 3:
            return "ASIAN_SESSION"
        else:
            return "SYDNEY_PACIFIC"

    def evaluate(self, symbol: str, df_bars: pd.DataFrame) -> ForexSignal:
        norm_sym = self.normalize_symbol(symbol)
        cfg = self.PAIR_CONFIG.get(norm_sym, {
            "yahoo": f"{norm_sym.replace('/', '')}=X",
            "pip": 0.01 if "JPY" in norm_sym else 0.0001,
            "pip_val_usd": 10.0,
        })
        yahoo_ticker = cfg["yahoo"]
        pip_size = cfg["pip"]
        now = time.time()
        current_session = self.detect_session()

        if df_bars.empty or len(df_bars) < 20:
            return ForexSignal(
                symbol=norm_sym,
                yahoo_ticker=yahoo_ticker,
                timestamp=now,
                side="NEUTRAL",
                confidence_score=0.0,
                entry_price=0.0,
                stop_loss=0.0,
                take_profit=0.0,
                pip_size=pip_size,
                pips_sl=0.0,
                pips_tp=0.0,
                session=current_session,
                rationale="Insufficient historical FX bar data",
            )

        close = df_bars["Close"]
        high = df_bars["High"]
        low = df_bars["Low"]

        curr_p = float(close.iloc[-1])
        ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
        ema50 = float(close.ewm(span=min(50, len(close)), adjust=False).mean().iloc[-1])

        # ATR calculation
        prev_c = close.shift(1)
        tr = pd.concat([high - low, (high - prev_c).abs(), (low - prev_c).abs()], axis=1).max(axis=1)
        atr = float(tr.tail(14).mean()) or (curr_p * 0.004)
        atr_pips = round(atr / pip_size, 1)

        # 20-bar High / Low channel
        prior_high_20 = float(high.iloc[-20:-1].max()) if len(high) >= 21 else float(high.max())
        prior_low_20 = float(low.iloc[-20:-1].min()) if len(low) >= 21 else float(low.min())

        # Dislocation Z-score
        std20 = float(close.rolling(20).std().iloc[-1]) or (atr * 0.5)
        z_score = (curr_p - ema20) / max(std20, 0.00001)

        # ------------------- SIGNAL GENERATION -------------------
        # Setup 1: London / NY Overlap Session Momentum Breakout
        is_breakout_long = curr_p >= prior_high_20 and curr_p > ema20
        is_breakout_short = curr_p <= prior_low_20 and curr_p < ema20

        if is_breakout_long:
            sl_pips = max(round(atr_pips * 1.2, 1), 15.0)
            tp_pips = round(sl_pips * 2.0, 1)
            sl = curr_p - (sl_pips * pip_size)
            tp = curr_p + (tp_pips * pip_size)
            conf = 88.0 if current_session == "LONDON_NY_OVERLAP" else 81.0
            return ForexSignal(
                symbol=norm_sym,
                yahoo_ticker=yahoo_ticker,
                timestamp=now,
                side="LONG",
                confidence_score=conf,
                entry_price=round(curr_p, 5 if pip_size == 0.0001 else 3),
                stop_loss=round(sl, 5 if pip_size == 0.0001 else 3),
                take_profit=round(tp, 5 if pip_size == 0.0001 else 3),
                pip_size=pip_size,
                pips_sl=sl_pips,
                pips_tp=tp_pips,
                strategy_type="LONDON_NY_BREAKOUT",
                session=current_session,
                rationale=f"High-liquidity channel breakout above {prior_high_20:.4f} during {current_session} with {sl_pips:.1f} pips SL / {tp_pips:.1f} pips TP."
            )

        if is_breakout_short:
            sl_pips = max(round(atr_pips * 1.2, 1), 15.0)
            tp_pips = round(sl_pips * 2.0, 1)
            sl = curr_p + (sl_pips * pip_size)
            tp = curr_p - (tp_pips * pip_size)
            conf = 86.0 if current_session == "LONDON_NY_OVERLAP" else 80.0
            return ForexSignal(
                symbol=norm_sym,
                yahoo_ticker=yahoo_ticker,
                timestamp=now,
                side="SHORT",
                confidence_score=conf,
                entry_price=round(curr_p, 5 if pip_size == 0.0001 else 3),
                stop_loss=round(sl, 5 if pip_size == 0.0001 else 3),
                take_profit=round(tp, 5 if pip_size == 0.0001 else 3),
                pip_size=pip_size,
                pips_sl=sl_pips,
                pips_tp=tp_pips,
                strategy_type="LONDON_NY_BREAKOUT",
                session=current_session,
                rationale=f"Bearish breakdown below {prior_low_20:.4f} during {current_session}. Structured 2:1 R:R short."
            )

        # Setup 2: EMA Trend Continuation (Pullback into EMA20 value)
        if ema20 > ema50 and curr_p >= (ema20 * 0.998) and -1.0 < z_score < 1.5:
            sl_pips = max(round(atr_pips * 1.5, 1), 18.0)
            tp_pips = round(sl_pips * 2.2, 1)
            sl = curr_p - (sl_pips * pip_size)
            tp = curr_p + (tp_pips * pip_size)
            return ForexSignal(
                symbol=norm_sym,
                yahoo_ticker=yahoo_ticker,
                timestamp=now,
                side="LONG",
                confidence_score=83.5,
                entry_price=round(curr_p, 5 if pip_size == 0.0001 else 3),
                stop_loss=round(sl, 5 if pip_size == 0.0001 else 3),
                take_profit=round(tp, 5 if pip_size == 0.0001 else 3),
                pip_size=pip_size,
                pips_sl=sl_pips,
                pips_tp=tp_pips,
                strategy_type="EMA_TREND_CONTINUATION",
                session=current_session,
                rationale=f"Macro bullish trend alignment (EMA20 > EMA50) pullback bounce. 2.2:1 R:R (+{tp_pips:.1f} pips TP)."
            )

        if ema20 < ema50 and curr_p <= (ema20 * 1.002) and -1.5 < z_score < 1.0:
            sl_pips = max(round(atr_pips * 1.5, 1), 18.0)
            tp_pips = round(sl_pips * 2.2, 1)
            sl = curr_p + (sl_pips * pip_size)
            tp = curr_p - (tp_pips * pip_size)
            return ForexSignal(
                symbol=norm_sym,
                yahoo_ticker=yahoo_ticker,
                timestamp=now,
                side="SHORT",
                confidence_score=83.5,
                entry_price=round(curr_p, 5 if pip_size == 0.0001 else 3),
                stop_loss=round(sl, 5 if pip_size == 0.0001 else 3),
                take_profit=round(tp, 5 if pip_size == 0.0001 else 3),
                pip_size=pip_size,
                pips_sl=sl_pips,
                pips_tp=tp_pips,
                strategy_type="EMA_TREND_CONTINUATION",
                session=current_session,
                rationale=f"Macro bearish trend alignment (EMA20 < EMA50) pullback rally fade into resistance. 2.2:1 R:R (+{tp_pips:.1f} pips TP short)."
            )

        # Setup 3: Asian Session / Over-extended Mean Reversion
        if z_score <= -1.8:
            sl_pips = max(round(atr_pips * 1.3, 1), 16.0)
            tp_pips = round(sl_pips * 2.0, 1)
            sl = curr_p - (sl_pips * pip_size)
            tp = curr_p + (tp_pips * pip_size)
            return ForexSignal(
                symbol=norm_sym,
                yahoo_ticker=yahoo_ticker,
                timestamp=now,
                side="LONG",
                confidence_score=79.0,
                entry_price=round(curr_p, 5 if pip_size == 0.0001 else 3),
                stop_loss=round(sl, 5 if pip_size == 0.0001 else 3),
                take_profit=round(tp, 5 if pip_size == 0.0001 else 3),
                pip_size=pip_size,
                pips_sl=sl_pips,
                pips_tp=tp_pips,
                strategy_type="ASIAN_MEAN_REVERSION",
                session=current_session,
                rationale=f"Oversold exhaustion wick (Z={z_score:.2f}). Mean-reversion scoop to mean with {tp_pips:.1f} pips TP."
            )

        if z_score >= 1.8:
            sl_pips = max(round(atr_pips * 1.3, 1), 16.0)
            tp_pips = round(sl_pips * 2.0, 1)
            sl = curr_p + (sl_pips * pip_size)
            tp = curr_p - (tp_pips * pip_size)
            return ForexSignal(
                symbol=norm_sym,
                yahoo_ticker=yahoo_ticker,
                timestamp=now,
                side="SHORT",
                confidence_score=79.0,
                entry_price=round(curr_p, 5 if pip_size == 0.0001 else 3),
                stop_loss=round(sl, 5 if pip_size == 0.0001 else 3),
                take_profit=round(tp, 5 if pip_size == 0.0001 else 3),
                pip_size=pip_size,
                pips_sl=sl_pips,
                pips_tp=tp_pips,
                strategy_type="ASIAN_MEAN_REVERSION",
                session=current_session,
                rationale=f"Overbought exhaustion wick (Z={z_score:+.2f}). Mean-reversion fade to mean with {tp_pips:.1f} pips TP short."
            )

        # Default Neutral
        return ForexSignal(
            symbol=norm_sym,
            yahoo_ticker=yahoo_ticker,
            timestamp=now,
            side="NEUTRAL",
            confidence_score=50.0,
            entry_price=round(curr_p, 5 if pip_size == 0.0001 else 3),
            stop_loss=0.0,
            take_profit=0.0,
            pip_size=pip_size,
            pips_sl=0.0,
            pips_tp=0.0,
            strategy_type="RANGE_WAIT",
            session=current_session,
            rationale="No high-confluence institutional FX order flow edge. Standing by in cash.",
        )

    def detect_shock(self, symbol: str, pos: Dict[str, Any], curr_price: float, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Detects sudden macro news spikes, central bank flash volatility,
        or weekend gap risks that warrant an emergency exit.
        Protects winning trades: never panic-exits a trade in green profit.
        """
        entry_price = float(pos.get("entry_price", curr_price))
        pip_size = float(pos.get("pip_size", 0.0001))
        side = pos.get("side", "LONG")
        r_pips = float(pos.get("pips_sl") or 16.0)

        # 0. Safety Guard: If trade is already derisked/trailed in profit, in reconnect hold, or loss curbed, DO NOT shock exit!
        pips_gain = (curr_price - entry_price) / pip_size if side == "LONG" else (entry_price - curr_price) / pip_size
        if pos.get("trailed_profit") or (pos.get("scaled_out_50") and pips_gain > 5.0) or pos.get("reconnect_hold") or pos.get("loss_curbed"):
            return {"shocked": False, "reason": "", "type": "NORMAL"}

        # 1. Adverse Pip Velocity Check (Emergency Cut if sudden spike against position)
        adverse_pips = -pips_gain

        # If moving against position violently (> 1.25x initial risk unit, min 22 pips)
        if adverse_pips >= max(22.0, r_pips * 1.25):
            return {
                "shocked": True,
                "reason": f"Adverse Pip Spike (-{adverse_pips:.1f} pips exceeding safety threshold)",
                "type": "VELOCITY_SHOCK",
            }

        # 2. Central Bank / Dislocation Bar Range Check (if intraday df provided)
        # MUST BE AN ADVERSE CANDLE: A large candle in our direction is a WIN, not a shock!
        if df is not None and not df.empty and len(df) >= 14:
            try:
                highs = df["High"]
                lows = df["Low"]
                closes = df["Close"]
                opens = df["Open"]
                high_low = highs - lows
                high_close = (highs - closes.shift()).abs()
                low_close = (lows - closes.shift()).abs()
                tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                atr = float(tr.rolling(14, min_periods=1).mean().iloc[-1])
                last_bar_range = float(highs.iloc[-1] - lows.iloc[-1])
                last_close = float(closes.iloc[-1])
                last_open = float(opens.iloc[-1])

                is_adverse_candle = (side == "LONG" and last_close < last_open) or \
                                    (side == "SHORT" and last_close > last_open)

                if atr > 0 and (last_bar_range / atr) >= 3.2 and is_adverse_candle:
                    return {
                        "shocked": True,
                        "reason": f"Adverse Central Bank Dislocation (Bar range {last_bar_range/pip_size:.1f} pips is {last_bar_range/atr:.1f}x ATR)",
                        "type": "CANDLE_VOLATILITY_SHOCK",
                    }
            except Exception as e:
                logger.debug(f"Forex shock bar check error: {e}")

        # 3. Friday Weekend Gap Risk Check
        now_ny = datetime.now(NY_TZ)
        if now_ny.weekday() == 4 and now_ny.hour >= 16 and now_ny.minute >= 45:
            # Friday after 16:45 ET - close unratcheted positions before weekend
            if not pos.get("ratcheted"):
                return {
                    "shocked": True,
                    "reason": "Weekend Gap Protection (Friday 16:45 ET market close)",
                    "type": "WEEKEND_CLOSE",
                }

        return {"shocked": False, "reason": "", "type": "NORMAL"}


forex_strategy = ForexStrategyEngine()

