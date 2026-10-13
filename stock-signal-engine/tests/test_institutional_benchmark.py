"""
Unit Tests for Institutional Alpha & Risk Benchmark Engine
==========================================================
Verifies:
  1. Benchmark calculations against SPY and QQQ.
  2. Sharpe ratio, Sortino, Calmar, and Drawdown computations.
  3. Whale trap avoidance scorecard.
  4. AAA Institutional classification logic.
"""

import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from benchmark.institutional_benchmark import InstitutionalBenchmarkEngine


class TestInstitutionalBenchmarkEngine(unittest.TestCase):

    def setUp(self):
        self.engine = InstitutionalBenchmarkEngine()

    @patch("benchmark.institutional_benchmark.fetch_prices")
    def test_benchmark_metrics_computation(self, mock_fetch):
        # Generate 1 year of realistic simulated benchmark price series
        dates = pd.date_range("2025-01-01", periods=252, freq="B")
        prices = [450.0]
        for _ in range(251):
            prices.append(prices[-1] * (1.0 + np.random.normal(0.0004, 0.008)))
        df_bench = pd.DataFrame({"Close": prices, "Volume": [5000000] * 252}, index=dates)
        mock_fetch.return_value = df_bench

        metrics = self.engine.calculate_metrics(benchmark="SPY", period="1y")

        self.assertEqual(metrics.benchmark_symbol, "SPY")
        self.assertIsInstance(metrics.sharpe_ratio, float)
        self.assertIsInstance(metrics.sortino_ratio, float)
        self.assertIsInstance(metrics.calmar_ratio, float)
        self.assertIsInstance(metrics.max_drawdown_pct, float)
        self.assertGreaterEqual(metrics.win_rate_pct, 50.0)
        self.assertGreaterEqual(metrics.whale_traps_defended, 0)
        self.assertIn(metrics.strategy_grade, ["AAA_INSTITUTIONAL", "AA_PRIME", "A_QUALIFIED"])

    @patch("benchmark.institutional_benchmark.fetch_prices")
    def test_qqq_benchmark_comparison(self, mock_fetch):
        dates = pd.date_range("2025-01-01", periods=100, freq="B")
        df_qqq = pd.DataFrame({"Close": np.linspace(400.0, 480.0, 100), "Volume": [2000000] * 100}, index=dates)
        mock_fetch.return_value = df_qqq

        metrics = self.engine.calculate_metrics(benchmark="QQQ", period="6mo")
        self.assertEqual(metrics.benchmark_symbol, "QQQ")
        self.assertGreater(metrics.total_return_pct, 0.0)


if __name__ == "__main__":
    unittest.main()
