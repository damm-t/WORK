r"""
Anti-Volatility Model & Price Stabilization Engine
==================================================
Eliminates high-frequency market microstructure noise, transient liquidity wicks,
and false breakouts by extracting the latent "Stabilized Fair Price" trajectory.

Key Quantitative Features:
  1. 2-State Adaptive Kalman Filter:
     - Tracks latent True Price $x_t$ and Velocity $v_t$.
     - Dynamically adapts Measurement Noise $R_t$ based on instantaneous ATR / Realized Volatility.
       When volatility spikes, $R_t$ increases, dampening erratic wicks and keeping the price stabilized.
     - Dynamically adapts Process Noise $Q_t$ to allow rapid trend adaptation without lag.
  2. Price Stability Index (PSI):
     - Metric from 0% (erratic chaotic noise) to 100% (stable, laminar trend).
     - Quantifies the signal-to-noise ratio (SNR) of the current price action.
  3. Dislocation Envelope & Residual Z-Score:
     - Decomposes observed price $P_t = \text{Stabilized Price}_t + \text{Volatility Residual}_t$.
     - Computes dynamic noise bands ($2\sigma$) to identify temporary liquidity dislocations for JEV scooping.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class StabilizationResult:
    """Output metrics from the Anti-Volatility stabilization model."""
    ticker: str
    current_raw_price: float
    stabilized_price: float
    velocity: float
    volatility_residual: float
    residual_zscore: float
    price_stability_index: float  # 0.0 - 100.0%
    upper_band: float             # +2 std noise envelope
    lower_band: float             # -2 std noise envelope
    noise_std: float
    regime: str                   # "LAMINAR_TREND", "CALM_RANGING", "ERRATIC_NOISE", "LIQUIDITY_DISLOCATION"
    history: Optional[pd.DataFrame] = None


class AntiVolatilityModel:
    """
    Adaptive State-Space Price Stabilizer utilizing a noise-damped Kalman Filter.
    """

    def __init__(self, default_q: float = 0.01, r_multiplier: float = 1.5):
        """
        :param default_q: Base process noise variance (trend flexibility).
        :param r_multiplier: Multiplier on rolling True Range variance to set measurement noise R.
        """
        self.default_q = default_q
        self.r_multiplier = r_multiplier

    def filter_series(
        self,
        prices: Union[pd.Series, List[float], np.ndarray],
        highs: Optional[Union[pd.Series, List[float], np.ndarray]] = None,
        lows: Optional[Union[pd.Series, List[float], np.ndarray]] = None,
    ) -> pd.DataFrame:
        """
        Filters a price time-series and returns a DataFrame with:
        [raw_price, stabilized_price, velocity, residual, upper_band, lower_band, zscore, psi]
        """
        if isinstance(prices, (list, np.ndarray)):
            p_series = pd.Series(prices, dtype=float)
        else:
            p_series = prices.astype(float).copy()

        n = len(p_series)
        if n == 0:
            return pd.DataFrame()

        # Fallback highs/lows if not provided
        if highs is None or lows is None:
            rolling_std = p_series.pct_change().rolling(14, min_periods=2).std().fillna(0.01)
            h_series = p_series * (1.0 + rolling_std)
            l_series = p_series * (1.0 - rolling_std)
        else:
            h_series = pd.Series(highs, index=p_series.index, dtype=float)
            l_series = pd.Series(lows, index=p_series.index, dtype=float)

        # Estimate instantaneous volatility (ATR proxy)
        tr1 = h_series - l_series
        tr2 = (h_series - p_series.shift(1)).abs()
        tr3 = (l_series - p_series.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.ewm(span=14, min_periods=1).mean().fillna(p_series.iloc[0] * 0.01)

        # Kalman Filter Initialization
        # State vector x = [price, velocity]^T
        dt = 1.0
        F = np.array([[1.0, dt],
                      [0.0, 1.0]])
        H = np.array([[1.0, 0.0]])

        # Initial state estimate
        x = np.array([[float(p_series.iloc[0])], [0.0]])
        P = np.array([[1.0, 0.0],
                      [0.0, 1.0]])

        stabilized = np.zeros(n)
        velocities = np.zeros(n)
        residuals = np.zeros(n)
        est_variances = np.zeros(n)

        for t in range(n):
            z = float(p_series.iloc[t])
            current_atr = max(float(atr.iloc[t]), 1e-4)

            # Adaptive Measurement Noise R: proportional to squared ATR
            # In volatile periods, R surges, causing the filter to heavily reject noisy spikes
            R = (current_atr * self.r_multiplier) ** 2

            # Adaptive Process Noise Q: allows velocity to change during strong trends
            q_var = self.default_q * (current_atr ** 2)
            Q = np.array([[(dt ** 4) / 4.0, (dt ** 3) / 2.0],
                          [(dt ** 3) / 2.0, dt ** 2]]) * q_var

            # 1. Predict
            x_pred = F @ x
            P_pred = F @ P @ F.T + Q

            # 2. Update
            y = z - (H @ x_pred)[0, 0]  # Measurement residual (innovation)
            S = (H @ P_pred @ H.T)[0, 0] + R  # Innovation covariance
            K = (P_pred @ H.T) / S  # Optimal Kalman Gain

            x = x_pred + K * y
            P = (np.eye(2) - K @ H) @ P_pred

            stabilized[t] = x[0, 0]
            velocities[t] = x[1, 0]
            residuals[t] = z - x[0, 0]
            est_variances[t] = max(S - R, 1e-6)

        df_out = pd.DataFrame(
            {
                "raw_price": p_series.values,
                "stabilized_price": stabilized,
                "velocity": velocities,
                "residual": residuals,
            },
            index=p_series.index,
        )

        # Dynamic noise bands (2-sigma envelope of residuals)
        rolling_noise_std = df_out["residual"].rolling(20, min_periods=3).std().bfill().fillna(1e-3)
        df_out["noise_std"] = rolling_noise_std
        df_out["upper_band"] = df_out["stabilized_price"] + (2.0 * rolling_noise_std)
        df_out["lower_band"] = df_out["stabilized_price"] - (2.0 * rolling_noise_std)
        df_out["residual_zscore"] = (df_out["residual"] / rolling_noise_std.replace(0.0, np.nan)).fillna(0.0)

        # Price Stability Index (PSI)
        # SNR = 1 - (Noise Variance / Total Signal Variance)
        total_var = df_out["raw_price"].rolling(20, min_periods=3).var().bfill().fillna(1e-4)
        noise_var = (rolling_noise_std ** 2)
        var_ratio = (noise_var / (total_var + 1e-5)).clip(0.0, 1.0)
        psi = (1.0 - var_ratio) * 100.0
        # Smooth PSI for stable telemetry
        df_out["price_stability_index"] = psi.ewm(span=5, min_periods=1).mean().clip(5.0, 98.0)

        return df_out

    def evaluate_ticker(
        self,
        ticker: str,
        df_bars: Optional[pd.DataFrame] = None,
        period: str = "3mo",
    ) -> StabilizationResult:
        """
        Fetches prices or uses provided bars to evaluate anti-volatility metrics for a ticker.
        """
        ticker = ticker.upper().strip()
        if df_bars is None or df_bars.empty:
            from market.price_fetcher import fetch_prices
            df_bars = fetch_prices(ticker, period=period)

        if df_bars.empty:
            raise ValueError(f"No price data available to stabilize {ticker}")

        close_col = "Close" if "Close" in df_bars.columns else df_bars.columns[0]
        high_col = "High" if "High" in df_bars.columns else close_col
        low_col = "Low" if "Low" in df_bars.columns else close_col

        df_filtered = self.filter_series(
            prices=df_bars[close_col],
            highs=df_bars[high_col],
            lows=df_bars[low_col],
        )

        last_row = df_filtered.iloc[-1]
        raw_px = float(last_row["raw_price"])
        stab_px = float(last_row["stabilized_price"])
        vel = float(last_row["velocity"])
        res = float(last_row["residual"])
        zscore = float(last_row["residual_zscore"])
        psi = float(last_row["price_stability_index"])
        ub = float(last_row["upper_band"])
        lb = float(last_row["lower_band"])
        n_std = float(last_row["noise_std"])

        # Regime Classification
        if zscore < -2.0:
            regime = "LIQUIDITY_DISLOCATION_OVERSOLD"
        elif zscore > 2.0:
            regime = "LIQUIDITY_DISLOCATION_OVERBOUGHT"
        elif psi >= 65.0 and abs(vel) > 0.05:
            regime = "LAMINAR_TREND"
        elif psi >= 50.0:
            regime = "CALM_RANGING"
        else:
            regime = "ERRATIC_NOISE"

        return StabilizationResult(
            ticker=ticker,
            current_raw_price=round(raw_px, 2),
            stabilized_price=round(stab_px, 2),
            velocity=round(vel, 4),
            volatility_residual=round(res, 2),
            residual_zscore=round(zscore, 2),
            price_stability_index=round(psi, 1),
            upper_band=round(ub, 2),
            lower_band=round(lb, 2),
            noise_std=round(n_std, 2),
            regime=regime,
            history=df_filtered,
        )


# Singleton instance
anti_volatility_model = AntiVolatilityModel()
