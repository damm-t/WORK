"""
Historical Dataset Generator & Triple-Barrier Labeling
======================================================
Builds quantitative training datasets across equity universes using
Triple-Barrier Labeling (Marcos López de Prado's method) and technical/NLP features.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from backtest.universe import get_universe
from market.price_fetcher import fetch_prices
from market.indicators import add_indicators

logger = logging.getLogger(__name__)

FEATURE_COLS = [
    "sentiment_positive", "sentiment_negative", "sentiment_neutral",
    "sentiment_score", "rsi", "macd", "bb_upper", "bb_lower",
    "atr", "bb_width", "rsi_overbought", "rsi_oversold"
]
LABEL_COL = "signal"


def generate_triple_barrier_labels(
    df: pd.DataFrame,
    tp_atr: float = 2.0,
    sl_atr: float = 1.5,
    horizon: int = 10,
) -> np.ndarray:
    """
    Computes Triple-Barrier Labels based on real trade execution geometry:
      - Upper Barrier (Take-Profit) = Close + tp_atr * ATR
      - Lower Barrier (Stop-Loss)    = Close - sl_atr * ATR
      - Vertical Barrier (Holding)  = horizon bars (days)

    Returns:
      labels: np.ndarray of shape (N,) containing:
        1: Upper barrier (TP) hit first (profitable setup)
        0: Lower barrier (SL) hit first or expired below entry (losing/neutral setup)
        -1: Unlabeled (boundary bars at the end of the time series)
    """
    n = len(df)
    labels = np.full(n, -1, dtype=int)
    if n <= horizon:
        return labels

    highs = df["High"].values
    lows = df["Low"].values
    closes = df["Close"].values
    atrs = df["ATR"].values if "ATR" in df.columns else np.full(n, np.nan)

    for i in range(n - horizon):
        entry = closes[i]
        atr = atrs[i]
        if np.isnan(atr) or atr <= 0:
            continue

        up = entry + tp_atr * atr
        down = entry - sl_atr * atr

        hit_up_step = -1
        hit_down_step = -1

        for step in range(1, horizon + 1):
            idx = i + step
            if hit_up_step == -1 and highs[idx] >= up:
                hit_up_step = step
            if hit_down_step == -1 and lows[idx] <= down:
                hit_down_step = step
            if hit_up_step != -1 and hit_down_step != -1:
                break

        if hit_up_step != -1 and (hit_down_step == -1 or hit_up_step <= hit_down_step):
            labels[i] = 1
        elif hit_down_step != -1 and (hit_up_step == -1 or hit_down_step < hit_up_step):
            labels[i] = 0
        else:
            # Time barrier reached: label 1 if price appreciated by at least 0.25 ATR
            gain = closes[i + horizon] - entry
            labels[i] = 1 if gain >= 0.25 * atr else 0

    return labels


def build_historical_dataset(
    universe_name: str = "core",
    period: str = "2y",
    tp_atr: float = 2.0,
    sl_atr: float = 1.5,
    horizon: int = 10,
    save_parquet: Optional[str] = "data/training_features.parquet",
    save_csv: Optional[str] = "data/training_features.csv",
) -> pd.DataFrame:
    """
    Generates a full quantitative training dataset across all tickers in the given universe.
    Computes technical indicators, derives realistic sentiment distributions,
    applies Triple-Barrier labeling, and saves to disk.
    """
    uni = get_universe(universe_name)
    all_tickers = [t for group in uni.values() for t in group]
    logger.info(f"Building historical dataset for {len(all_tickers)} tickers ({universe_name}, period={period})...")

    records = []
    rng = np.random.default_rng(42)

    for ticker in all_tickers:
        try:
            df = fetch_prices(ticker, period=period)
            if df.empty or len(df) < 60:
                continue

            df = add_indicators(df)
            bbu_col = "BB_Upper" if "BB_Upper" in df.columns else ([c for c in df.columns if c.startswith("BBU_")] or [None])[0]
            bbl_col = "BB_Lower" if "BB_Lower" in df.columns else ([c for c in df.columns if c.startswith("BBL_")] or [None])[0]
            if not bbu_col or not bbl_col:
                continue

            labels = generate_triple_barrier_labels(df, tp_atr=tp_atr, sl_atr=sl_atr, horizon=horizon)

            # Start from bar 30 so all rolling indicators (SMA20, RSI14, BB20) are fully formed
            for i in range(30, len(df) - horizon):
                lbl = labels[i]
                if lbl < 0:
                    continue

                c = float(df["Close"].iloc[i])
                rsi = float(df["RSI"].iloc[i])
                macd = float(df["MACD_Histogram"].iloc[i])
                bb_upper = float(df[bbu_col].iloc[i])
                bb_lower = float(df[bbl_col].iloc[i])
                atr = float(df["ATR"].iloc[i])

                if any(np.isnan([c, rsi, macd, bb_upper, bb_lower, atr])):
                    continue

                bb_width = bb_upper - bb_lower
                rsi_overbought = 1 if rsi > 70.0 else 0
                rsi_oversold = 1 if rsi < 30.0 else 0

                # Derive realistic historical sentiment distribution based on momentum + noise
                # Real news sentiment tends to correlate with 5-day return with idiosyncratic variance
                ret5 = (c / float(df["Close"].iloc[i - 5]) - 1.0) if i >= 5 else 0.0
                noise = rng.normal(0.0, 0.02)
                sentiment_signal = ret5 + noise

                if sentiment_signal > 0.015:
                    sent_pos = 1
                    sent_neg = 0
                    sent_neu = 0
                    sent_score = round(float(np.clip(0.65 + sentiment_signal * 5.0 + rng.uniform(0.0, 0.2), 0.50, 0.98)), 4)
                elif sentiment_signal < -0.015:
                    sent_pos = 0
                    sent_neg = 1
                    sent_neu = 0
                    sent_score = round(float(np.clip(0.65 + abs(sentiment_signal) * 5.0 + rng.uniform(0.0, 0.2), 0.50, 0.98)), 4)
                else:
                    sent_pos = 0
                    sent_neg = 0
                    sent_neu = 1
                    sent_score = round(float(rng.uniform(0.40, 0.60)), 4)

                records.append({
                    "ticker": ticker,
                    "date": str(df.index[i]),
                    "sentiment_positive": sent_pos,
                    "sentiment_negative": sent_neg,
                    "sentiment_neutral": sent_neu,
                    "sentiment_score": sent_score,
                    "rsi": round(rsi, 2),
                    "macd": round(macd, 4),
                    "bb_upper": round(bb_upper, 2),
                    "bb_lower": round(bb_lower, 2),
                    "atr": round(atr, 2),
                    "bb_width": round(bb_width, 2),
                    "rsi_overbought": rsi_overbought,
                    "rsi_oversold": rsi_oversold,
                    "signal": int(lbl),
                })
        except Exception as e:
            logger.debug(f"[dataset_generator] Error processing {ticker}: {e}")

    dataset_df = pd.DataFrame(records)
    if dataset_df.empty:
        logger.warning("[dataset_generator] Warning: Dataset is empty.")
        return dataset_df

    # Sort chronologically by date to preserve temporal ordering for TimeSeriesSplit
    dataset_df.sort_values(by=["date", "ticker"], inplace=True)
    dataset_df.reset_index(drop=True, inplace=True)

    # Save to disk
    if save_parquet:
        try:
            p_path = Path(save_parquet)
            p_path.parent.mkdir(parents=True, exist_ok=True)
            dataset_df.to_parquet(p_path, index=False)
            logger.info(f"Saved dataset ({len(dataset_df)} rows) to {p_path}")
        except Exception as e:
            logger.debug(f"[dataset_generator] Parquet export skipped (install pyarrow to enable): {e}")

    if save_csv:
        c_path = Path(save_csv)
        c_path.parent.mkdir(parents=True, exist_ok=True)
        dataset_df.to_csv(c_path, index=False)
        logger.info(f"Saved dataset ({len(dataset_df)} rows) to {c_path}")

    return dataset_df
