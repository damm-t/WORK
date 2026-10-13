import sys, math, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from market.price_fetcher import fetch_prices
from market.technicals import TechnicalIndicators as TI

EXCLUDED_HOT_STOCKS = frozenset({
    "NVDA", "MSFT", "TSLA", "AAPL", "AMZN", "META", "GOOGL", "GOOG", "SPCX", "SPX"
})

CANDIDATE_TICKERS = [
    "JPM", "GS", "V", "BAC",
    "UNH", "LLY", "JNJ", "ABT",
    "CAT", "DE", "HON", "LMT",
    "COST", "PG", "WMT", "HD",
    "XOM", "CVX", "LIN"
]
CANDIDATE_TICKERS = [t for t in CANDIDATE_TICKERS if t not in EXCLUDED_HOT_STOCKS]

print(f"Target Universe ({len(CANDIDATE_TICKERS)} tickers): {CANDIDATE_TICKERS}")

print("Fetching 20y SPY benchmark for regime detection...")
df_spy = fetch_prices("SPY", period="20y", interval="1d")
if df_spy.empty or len(df_spy) < 500:
    print("Error fetching SPY")
    sys.exit(1)

ticker_dfs = {}
for t in CANDIDATE_TICKERS:
    df = fetch_prices(t, period="20y", interval="1d")
    if not df.empty and len(df) > 1000:
        common_idx = df.index.intersection(df_spy.index)
        if len(common_idx) > 1000:
            ticker_dfs[t] = df.loc[common_idx].sort_index()
            print(f"Loaded {t}: {len(ticker_dfs[t])} bars ({ticker_dfs[t].index[0].date()} to {ticker_dfs[t].index[-1].date()})")

print(f"\nSuccessfully loaded {len(ticker_dfs)} high-quality non-hot stocks with full 20y history.")
