"""
TechnicalIndicators — single source of truth for all indicator math.
====================================================================
Every module (backtester, scanner, live pipeline) computes indicators
through this class, eliminating duplicated formulas drifting apart.

Conventions:
    - RSI   : Wilder smoothing (ewm alpha=1/length), neutral-filled at 50
    - MACD  : EMA(fast) - EMA(slow), signal = EMA(macd, signal)
    - ATR   : True-range Wilder smoothing
    - Rolling helpers are shifted by one bar where a *prior* value is
      required (breakout highs, average volume) to avoid look-ahead bias.
"""

import numpy as np
import pandas as pd


class TechnicalIndicators:
    """Stateless indicator factory operating on pandas Series/DataFrames."""

    # ---------------------------------------------------------------- trend --
    @staticmethod
    def sma(close: pd.Series, length: int = 50) -> pd.Series:
        return close.rolling(length).mean()

    @staticmethod
    def ema(close: pd.Series, span: int) -> pd.Series:
        return close.ewm(span=span, adjust=False).mean()

    # -------------------------------------------------------------- momentum -
    @staticmethod
    def rsi(close: pd.Series, length: int = 14) -> pd.Series:
        delta = close.diff()
        gain = delta.clip(lower=0.0)
        loss = (-delta).clip(lower=0.0)
        avg_gain = gain.ewm(alpha=1.0 / length, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / length, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0.0, np.nan)
        return (100.0 - (100.0 / (1.0 + rs))).fillna(50.0)

    @classmethod
    def macd(cls, close: pd.Series, fast: int = 12, slow: int = 26,
             signal_period: int = 9):
        macd_line = cls.ema(close, fast) - cls.ema(close, slow)
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        return macd_line, signal_line

    # ------------------------------------------------------------ volatility -
    @staticmethod
    def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
        prev_close = df["Close"].shift(1)
        true_range = pd.concat([
            df["High"] - df["Low"],
            (df["High"] - prev_close).abs(),
            (df["Low"] - prev_close).abs(),
        ], axis=1).max(axis=1)
        return true_range.ewm(alpha=1.0 / length, adjust=False).mean()

    @staticmethod
    def realized_vol(close: pd.Series, bars: int = 20,
                     annualize: bool = True) -> pd.Series:
        vol = close.pct_change().rolling(bars).std()
        return vol * (252 ** 0.5) if annualize else vol

    # ------------------------------------------------------- price structure -
    @staticmethod
    def prior_rolling_high(high: pd.Series, length: int = 20) -> pd.Series:
        """Highest high of the PREVIOUS `length` bars (shifted => no lookahead)."""
        return high.rolling(length).max().shift(1)

    @staticmethod
    def avg_volume(volume: pd.Series, length: int = 20,
                   exclude_current: bool = False) -> pd.Series:
        series = volume.shift(1) if exclude_current else volume
        return series.rolling(length).mean()

    @classmethod
    def volume_ratio(cls, volume: pd.Series, length: int = 20) -> float:
        """Latest volume vs its rolling average (>1 = above-average activity)."""
        avg = cls.avg_volume(volume, length).iloc[-1]
        return float(volume.iloc[-1]) / float(avg) if avg else 0.0