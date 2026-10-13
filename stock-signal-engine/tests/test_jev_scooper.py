"""
Unit Tests — Joint Expected Value (JEV) Liquidity Scooper Strategy
==================================================================
Validates mathematical expectancy calculation, dislocation identification,
$50 risk bounding, and book allocation categorization.
"""

import unittest
import numpy as np
import pandas as pd

from execution.jev_execution import execute_jev_scoop_trade
from strategy.jev_scooper import JEVLiquidityScooper, ScoopOpportunity


class TestJEVLiquidityScooper(unittest.TestCase):
    def setUp(self):
        self.scooper = JEVLiquidityScooper(
            min_dislocation_zscore=-1.5,
            min_win_prob=0.52,
            min_jev_edge_pct=0.8,
            min_rr_ratio=1.2,
        )

    def test_calm_tape_has_no_edge(self):
        """When price trades tightly around stabilized fair value, status is NO_EDGE."""
        dates = pd.date_range("2026-09-01", periods=30, freq="B")
        close = [100.0 + (i % 2) * 0.1 for i in range(30)]
        df_bars = pd.DataFrame({
            "Open": close, "High": [c + 0.2 for c in close],
            "Low": [c - 0.2 for c in close], "Close": close,
            "Volume": [1000000] * 30,
        }, index=dates)

        opp = self.scooper.evaluate_ticker("CALM", df_bars=df_bars)
        self.assertIsInstance(opp, ScoopOpportunity)
        self.assertEqual(opp.status, "NO_EDGE")
        self.assertGreater(opp.dislocation_zscore, -1.0)

    def test_sharp_downward_dislocation_qualifies_scoop(self):
        """Severe price drop with volume spike creates a QUALIFIED_SCOOP opportunity."""
        np.random.seed(42)
        dates = pd.date_range("2026-09-01", periods=35, freq="B")
        trend = np.linspace(100.0, 110.0, 35)
        # Flush on last bar
        trend[-1] = trend[-2] - 5.0
        vols = [1000000] * 34 + [3500000]

        df_bars = pd.DataFrame({
            "Open": trend, "High": trend + 0.3,
            "Low": trend - 0.3, "Close": trend,
            "Volume": vols,
        }, index=dates)

        opp = self.scooper.evaluate_ticker("DISLOCATED", df_bars=df_bars)
        self.assertIsInstance(opp, ScoopOpportunity)
        self.assertEqual(opp.status, "QUALIFIED_SCOOP")
        self.assertLess(opp.dislocation_zscore, -1.5)
        self.assertGreater(opp.win_probability_pct, 55.0)
        self.assertGreater(opp.jev_dollars, 0.0)
        self.assertGreater(opp.take_profit_target, opp.current_price)
        self.assertLess(opp.stop_loss, opp.current_price)

    def test_jev_mathematical_consistency(self):
        """JEV = (P_rev * Upside) - ((1 - P_rev) * Downside)."""
        dates = pd.date_range("2026-09-01", periods=30, freq="B")
        close = np.linspace(50.0, 55.0, 30)
        close[-1] = 51.0  # dip

        df_bars = pd.DataFrame({
            "Open": close, "High": close + 0.4,
            "Low": close - 0.4, "Close": close,
            "Volume": [1000000] * 30,
        }, index=dates)

        opp = self.scooper.evaluate_ticker("MATH", df_bars=df_bars)
        p_rev = opp.win_probability_pct / 100.0
        expected_jev = (p_rev * opp.upside_reward) - ((1.0 - p_rev) * opp.downside_risk)
        self.assertAlmostEqual(opp.jev_dollars, expected_jev, places=1)

    def test_dry_run_execution_enforces_risk_bound(self):
        """execute_jev_scoop_trade dry run must size trade so total risk <= max_risk."""
        res = execute_jev_scoop_trade(
            ticker="META",
            entry_price=700.0,
            take_profit=720.0,
            stop_loss=690.0,
            max_risk=50.0,
            dry_run=True,
        )

        self.assertEqual(res["status"], "dry_run")
        self.assertEqual(res["ticker"], "META")
        self.assertIn(res["book"], ["core", "momentum"])
        self.assertGreater(res["shares"], 0)
        # Risk per share is 700 - 690 = 10; 50 / 10 = 5 shares
        self.assertLessEqual(res["total_risk_dollars"], 50.0)


if __name__ == "__main__":
    unittest.main()
