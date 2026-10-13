"""
Unit Tests — Anti-Volatility Model & Price Stabilizer
=====================================================
Validates adaptive Kalman filter, zero-lag price smoothing,
Price Stability Index (PSI), and liquidity dislocation detection.
"""

import unittest
import numpy as np
import pandas as pd

from market.anti_volatility import AntiVolatilityModel, StabilizationResult


class TestAntiVolatilityModel(unittest.TestCase):
    def setUp(self):
        self.model = AntiVolatilityModel(default_q=0.01, r_multiplier=1.5)

    def test_flat_series_produces_zero_velocity_and_high_stability(self):
        """Constant prices should yield zero velocity and near-zero residuals."""
        prices = [100.0] * 30
        df = self.model.filter_series(prices)

        self.assertEqual(len(df), 30)
        self.assertAlmostEqual(df["stabilized_price"].iloc[-1], 100.0, places=1)
        self.assertAlmostEqual(df["velocity"].iloc[-1], 0.0, places=2)
        self.assertAlmostEqual(df["residual"].iloc[-1], 0.0, places=2)

    def test_uptrend_produces_positive_velocity_and_laminar_regime(self):
        """Clean linear uptrend should have positive velocity and high PSI."""
        prices = np.linspace(100.0, 150.0, 50)
        df = self.model.filter_series(prices)

        self.assertGreater(df["velocity"].iloc[-1], 0.5)
        self.assertGreaterEqual(df["price_stability_index"].iloc[-1], 50.0)
        self.assertAlmostEqual(df["stabilized_price"].iloc[-1], 150.0, delta=2.5)

    def test_flash_dip_triggers_liquidity_dislocation_oversold(self):
        """A sudden 4-standard-deviation flash dip must trigger dislocation regime."""
        np.random.seed(42)
        trend = np.linspace(100, 110, 40)
        noise = np.random.normal(0, 0.2, 40)
        prices = trend + noise
        # Sudden flush at final bar
        prices[-1] = prices[-2] - 4.0

        dates = pd.date_range("2026-09-01", periods=40, freq="B")
        df_bars = pd.DataFrame({
            "Open": prices,
            "High": prices + 0.3,
            "Low": prices - 0.3,
            "Close": prices,
            "Volume": [1000000] * 40,
        }, index=dates)

        res = self.model.evaluate_ticker("TEST", df_bars=df_bars)
        self.assertIsInstance(res, StabilizationResult)
        self.assertLess(res.residual_zscore, -2.0)
        self.assertEqual(res.regime, "LIQUIDITY_DISLOCATION_OVERSOLD")
        self.assertGreater(res.stabilized_price, res.current_raw_price)

    def test_dynamic_noise_bands_bracket_price(self):
        """Upper band should exceed stabilized price, lower band should be below."""
        prices = [50.0 + np.sin(i / 5.0) * 2.0 for i in range(40)]
        df = self.model.filter_series(prices)

        last = df.iloc[-1]
        self.assertGreater(last["upper_band"], last["stabilized_price"])
        self.assertLess(last["lower_band"], last["stabilized_price"])


if __name__ == "__main__":
    unittest.main()
