"""
Beta Calculator & Market Regime Detection Engine
Calculates rolling market beta, correlation, and volatility against benchmark index (SPY/QQQ).
"""

import logging
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from market.price_fetcher import fetch_prices

logger = logging.getLogger(__name__)

BENCHMARK_SPY = "SPY"
BENCHMARK_QQQ = "QQQ"


def calculate_asset_beta(
    ticker: str,
    benchmark_ticker: str = BENCHMARK_SPY,
    period: str = "6mo",
    interval: str = "1d"
) -> Dict[str, Any]:
    """
    Computes rolling beta, correlation, and annualized volatility of a ticker
    relative to a benchmark index (default SPY).
    
    Formula: Beta = Cov(R_asset, R_benchmark) / Var(R_benchmark)
    """
    ticker_clean = ticker.upper().strip()
    benchmark_clean = benchmark_ticker.upper().strip()

    try:
        # Fetch asset prices
        df_asset = fetch_prices(ticker_clean, period=period, interval=interval)
        if df_asset.empty or len(df_asset) < 20:
            return {
                "status": "error",
                "ticker": ticker_clean,
                "message": f"Insufficient price data for {ticker_clean}"
            }

        # Fetch benchmark prices
        df_bench = fetch_prices(benchmark_clean, period=period, interval=interval)
        if df_bench.empty or len(df_bench) < 20:
            return {
                "status": "error",
                "ticker": ticker_clean,
                "message": f"Insufficient price data for benchmark {benchmark_clean}"
            }

        # Align closes on matching date indices
        close_asset = df_asset["Close"].rename("Asset")
        close_bench = df_bench["Close"].rename("Benchmark")

        combined = pd.concat([close_asset, close_bench], axis=1).dropna()
        if len(combined) < 20:
            return {
                "status": "error",
                "ticker": ticker_clean,
                "message": f"Not enough overlapping trading days between {ticker_clean} and {benchmark_clean}"
            }

        # Calculate daily percentage returns
        returns = combined.pct_change().dropna()
        asset_ret = returns["Asset"]
        bench_ret = returns["Benchmark"]

        # Covariance & Variance
        covariance = float(np.cov(asset_ret, bench_ret)[0][1])
        bench_variance = float(np.var(bench_ret, ddof=1))

        if bench_variance == 0:
            beta = 1.0
        else:
            beta = covariance / bench_variance

        # Correlation (Pearson)
        corr = float(asset_ret.corr(bench_ret))

        # Annualized Volatility (assuming 252 trading days)
        asset_vol = float(asset_ret.std() * np.sqrt(252))
        bench_vol = float(bench_ret.std() * np.sqrt(252))

        # PROJECT OMEGA: Rolling 5-Day Realized Beta & Crisis Correlation Break Tracker
        realized_beta_5d = None
        correlation_break = False
        effective_beta = float(beta)

        if len(returns) >= 5:
            ret_5d = returns.tail(5)
            cov_5d = float(np.cov(ret_5d["Asset"], ret_5d["Benchmark"])[0][1])
            var_5d = float(np.var(ret_5d["Benchmark"], ddof=1))
            if var_5d > 1e-7:
                realized_beta_5d = float(cov_5d / var_5d)
            else:
                realized_beta_5d = float(beta)

            # Crisis correlation convergence: realized short-term beta spikes vs historical 6mo
            beta_divergence = abs(realized_beta_5d - float(beta))
            if beta_divergence >= 0.50 or (corr >= 0.85 and realized_beta_5d > float(beta)):
                correlation_break = True
                effective_beta = max(float(beta), realized_beta_5d, 1.0)

        return {
            "status": "success",
            "ticker": ticker_clean,
            "benchmark": benchmark_clean,
            "beta": round(float(beta), 3),
            "realized_beta_5d": round(float(realized_beta_5d), 3) if realized_beta_5d is not None else None,
            "effective_beta": round(float(effective_beta), 3),
            "correlation_break": correlation_break,
            "correlation": round(float(corr), 3),
            "asset_volatility": round(float(asset_vol), 4),
            "benchmark_volatility": round(float(bench_vol), 4),
            "sample_days": len(combined)
        }

    except Exception as e:
        logger.error(f"[calculate_asset_beta] Error for {ticker_clean}: {e}")
        return {
            "status": "error",
            "ticker": ticker_clean,
            "message": str(e),
            "beta": 1.0  # Safe neutral default
        }


def detect_market_regime(benchmark_ticker: str = BENCHMARK_SPY) -> Dict[str, Any]:
    """
    Detects current macro market regime based on 20-day vs 50-day moving averages,
    RSI, and recent volatility of the benchmark index.
    
    Regimes:
    - 'BULL_MOMENTUM': Price > SMA20 > SMA50, Low/Normal Volatility (aggressive long, light hedge)
    - 'CHOP_NEUTRAL': Range-bound consolidation (balanced market-neutral hedge)
    - 'BEAR_VOLATILITY': Price < SMA50 or High Volatility / Panic (heavy hedge or cash preservation)
    """
    try:
        df = fetch_prices(benchmark_ticker, period="6mo", interval="1d")
        if df.empty or len(df) < 50:
            return {
                "regime": "CHOP_NEUTRAL",
                "hedge_multiplier": 0.50,
                "reason": "Insufficient data to detect regime; using neutral hedge."
            }

        closes = df["Close"]
        latest_price = float(closes.iloc[-1])
        sma20 = float(closes.rolling(20).mean().iloc[-1])
        sma50 = float(closes.rolling(50).mean().iloc[-1])

        # 20-day returns volatility
        recent_ret = closes.pct_change().dropna().tail(20)
        recent_vol = float(recent_ret.std() * np.sqrt(252))

        # Regime determination
        if latest_price > sma20 and sma20 > sma50:
            regime = "BULL_MOMENTUM"
            hedge_multiplier = 0.25  # 25% hedge ratio (let winners run)
            description = "Market in confirmed uptrend (Price > SMA20 > SMA50). Light beta hedge applied."
        elif latest_price < sma50 or recent_vol > 0.25:
            regime = "BEAR_VOLATILITY"
            hedge_multiplier = 0.85  # 85-100% hedge ratio (defensive capital preservation)
            description = "Market under pressure or elevated volatility. Heavy defensive hedge applied."
        else:
            regime = "CHOP_NEUTRAL"
            hedge_multiplier = 0.50  # 50% hedge ratio (market neutral)
            description = "Market in sideways consolidation. 50% balanced hedge applied."

        return {
            "status": "success",
            "benchmark": benchmark_ticker,
            "latest_price": round(latest_price, 2),
            "sma20": round(sma20, 2),
            "sma50": round(sma50, 2),
            "annualized_volatility": round(recent_vol, 4),
            "regime": regime,
            "hedge_multiplier": hedge_multiplier,
            "description": description
        }

    except Exception as e:
        logger.error(f"[detect_market_regime] Error: {e}")
        return {
            "status": "error",
            "regime": "CHOP_NEUTRAL",
            "hedge_multiplier": 0.50,
            "description": f"Fallback to neutral hedge due to error: {e}"
        }
