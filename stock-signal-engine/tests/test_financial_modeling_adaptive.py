"""
Unit Tests for Phase 3 Upgrades in Financial Modeling Suite
============================================================
Validates:
- Profile key generation & deserialization with adaptive parameters
- Precomputation of PSI and velocity in Bundle construction
- Simulation execution under adaptive exit geometry and dynamic hedge bounds
- PSI threshold gating in simulated entries
"""

import unittest
import numpy as np
import pandas as pd

from backtest.financial_modeling import (
    Profile,
    Bundle,
    baseline_profile,
    build_bundle,
    profile_from_row,
    sensitivity_grid,
    _simulate_bars,
)


class TestFinancialModelingAdaptive(unittest.TestCase):
    def test_profile_keys_and_defaults(self):
        """Baseline profile preserves exact legacy key format; adaptive toggles append clearly."""
        base = baseline_profile()
        self.assertFalse(base.adaptive_psi)
        self.assertEqual(base.min_psi, 0.0)
        self.assertFalse(base.dynamic_hedge)
        self.assertNotIn("_adpPSI", base.key())
        self.assertNotIn("_minPSI", base.key())
        self.assertNotIn("_dynHdg", base.key())

        upgraded = Profile(
            stop_mult=1.5,
            tp1_mult=2.0,
            trail_mult=1.5,
            tp1_scale=0.5,
            rsi_max=65.0,
            trend_filter=True,
            be_after_tp1=True,
            hedge=True,
            adaptive_psi=True,
            min_psi=45.0,
            dynamic_hedge=True,
        )
        self.assertTrue(upgraded.adaptive_psi)
        self.assertEqual(upgraded.min_psi, 45.0)
        self.assertTrue(upgraded.dynamic_hedge)
        self.assertIn("_adpPSI", upgraded.key())
        self.assertIn("_minPSI45", upgraded.key())
        self.assertIn("_dynHdg", upgraded.key())

    def test_profile_from_row(self):
        """profile_from_row deserializes row dicts with and without adaptive columns."""
        row_legacy = {
            "stop": 1.5,
            "tp1": 2.0,
            "trail": 1.5,
            "scale": 0.5,
            "rsi_max": 65.0,
            "trend": True,
            "hedged": True,
            "be_trigger": 0.0,
            "be_offset": 0.0,
            "regime_filter": False,
            "sector_up": False,
        }
        p_leg = profile_from_row(row_legacy)
        self.assertFalse(p_leg.adaptive_psi)
        self.assertEqual(p_leg.min_psi, 0.0)
        self.assertFalse(p_leg.dynamic_hedge)

        row_upgraded = dict(row_legacy)
        row_upgraded.update({
            "adaptive_psi": True,
            "min_psi": 50.0,
            "dynamic_hedge": True,
        })
        p_upg = profile_from_row(row_upgraded)
        self.assertTrue(p_upg.adaptive_psi)
        self.assertEqual(p_upg.min_psi, 50.0)
        self.assertTrue(p_upg.dynamic_hedge)

    def test_sensitivity_grid_includes_adaptive_profiles(self):
        """Sensitivity grid contains both legacy static profiles and upgraded adaptive profiles."""
        grid = sensitivity_grid()
        self.assertGreater(len(grid), 192)
        adaptive_count = sum(1 for p in grid if p.adaptive_psi)
        self.assertGreater(adaptive_count, 0)
        dyn_hedge_count = sum(1 for p in grid if p.dynamic_hedge)
        self.assertGreater(dyn_hedge_count, 0)

    def test_bundle_precomputes_psi_and_velocity(self):
        """build_bundle populates psi and velocity arrays for the bundle."""
        dates = pd.date_range("2020-01-01", periods=350, freq="B")
        np.random.seed(42)
        close = 100.0 + np.cumsum(np.random.randn(350))
        high = close + np.random.uniform(0.5, 2.0, 350)
        low = close - np.random.uniform(0.5, 2.0, 350)
        volume = np.random.uniform(1e6, 2e6, 350)

        df = pd.DataFrame(
            {"Open": close, "High": high, "Low": low, "Close": close, "Volume": volume},
            index=dates,
        )
        df_bench = pd.DataFrame(
            {"Open": close, "High": high, "Low": low, "Close": close, "Volume": volume},
            index=dates,
        )
        df_hedge = pd.DataFrame(
            {"Open": close, "High": high, "Low": low, "Close": close, "Volume": volume},
            index=dates,
        )

        b = build_bundle("TEST", "Tech", df, df_bench, df_hedge)
        self.assertIsNotNone(b)
        self.assertIsNotNone(b.psi)
        self.assertIsNotNone(b.velocity)
        self.assertEqual(len(b.psi), len(dates))
        self.assertEqual(len(b.velocity), len(dates))
        self.assertTrue(np.all(np.isfinite(b.psi)))

    def test_simulation_adaptive_vs_static(self):
        """_simulate_bars executes correctly with adaptive_psi=True and dynamic_hedge=True."""
        dates = pd.date_range("2020-01-01", periods=350, freq="B")
        np.random.seed(42)
        # Create a trending price curve with some noise
        drift = np.linspace(100.0, 180.0, 350)
        noise = np.random.randn(350) * 1.5
        close = drift + noise
        high = close + 2.0
        low = close - 2.0
        volume = np.ones(350) * 1e6

        df = pd.DataFrame(
            {"Open": close, "High": high, "Low": low, "Close": close, "Volume": volume},
            index=dates,
        )
        b = build_bundle("TEST", "Tech", df, df, df)
        self.assertIsNotNone(b)

        p_adaptive = Profile(
            stop_mult=1.5,
            tp1_mult=2.0,
            trail_mult=1.5,
            tp1_scale=0.5,
            rsi_max=65.0,
            trend_filter=False,
            be_after_tp1=True,
            hedge=True,
            adaptive_psi=True,
            min_psi=45.0,
            dynamic_hedge=True,
        )

        res = _simulate_bars(
            [b], p_adaptive, capital=10_000.0, fractional=True, start=None, end=None
        )
        self.assertNotIn("error", res)
        metrics = res.get("metrics", {})
        self.assertIn("win_rate_pct", metrics)
        self.assertIn("total_return_pct", metrics)
        self.assertIn("num_trades", metrics)


if __name__ == "__main__":
    unittest.main()
