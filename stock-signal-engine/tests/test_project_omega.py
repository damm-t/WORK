"""
Unit Tests for Project Omega: Zero-Trust Survival Architecture
==============================================================
Validates:
1. CRIT-1: Circuit breaker halt and snapshot gap detection in shock_detector
2. CRIT-2: Broker-verified clock check in deadmans_switch
3. CRIT-3: 5-day realized beta tracker and correlation break flag in beta_calculator
4. HIGH-1: Mandatory hedge integrity gate in hedging_engine & alpha_client
5. HIGH-2: Fail-closed market status on API timeout in autopilot
6. Pillars 2 & 4: Convex tail risk engine & pre-market circuit sentry
"""

import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np

from market.shock_detector import detect_intraday_shock
from execution.deadmans_switch import is_us_equity_market_open
from market.beta_calculator import calculate_asset_beta
from risk.hedging_engine import calculate_hedge_pair
from execution.alpha_client import submit_pair_orders
from execution.autopilot import market_is_open
from risk.convex_tail import convex_tail_engine


class TestProjectOmega(unittest.TestCase):

    def test_crit1_circuit_halt_detection(self):
        """When intraday bars are empty during market hours, shock_detector flags market halt."""
        with patch("execution.deadmans_switch.is_us_equity_market_open", return_value=True):
            res = detect_intraday_shock("SPY", df_intraday=pd.DataFrame(), prev_close=500.0)
            self.assertTrue(res["shocked"])
            self.assertEqual(res["status"], "market_halt")
            self.assertTrue(res.get("circuit_breaker"))

    def test_crit1_snapshot_gap_detection(self):
        """When intraday bars are empty but pre-market snapshot reveals a massive gap."""
        with patch("execution.deadmans_switch.is_us_equity_market_open", return_value=False), \
             patch("market.price_fetcher.fetch_latest_price", return_value=450.0):
            res = detect_intraday_shock("SPY", df_intraday=pd.DataFrame(), prev_close=500.0)
            self.assertTrue(res["shocked"])
            self.assertEqual(res["status"], "halt_gap")
            self.assertEqual(res["direction"], "down")
            self.assertAlmostEqual(res["gap_pct"], -10.0, places=1)

    def test_crit2_broker_verified_clock(self):
        """Deadman switch queries broker clock first."""
        mock_clock = MagicMock()
        mock_clock.is_open = True
        with patch("execution.client.get_clock", return_value=mock_clock):
            self.assertTrue(is_us_equity_market_open())

        mock_clock.is_open = False
        with patch("execution.client.get_clock", return_value=mock_clock):
            self.assertFalse(is_us_equity_market_open())

    def test_crit3_realized_beta_correlation_break(self):
        """Beta calculator detects crisis correlation break and computes effective beta."""
        # Create synthetic data with a sudden correlation / beta jump in the last 5 days
        dates = pd.date_range("2026-01-01", periods=60, freq="B")
        # Baseline: asset is low beta (0.3x)
        bench = np.linspace(100, 110, 60) + np.random.normal(0, 0.5, 60)
        asset = np.linspace(50, 52, 60) + np.random.normal(0, 0.2, 60)
        # Last 5 days: asset plunges at 2.5x beta
        bench[-5:] = bench[-6] * np.array([0.98, 0.96, 0.94, 0.92, 0.90])
        asset[-5:] = asset[-6] * np.array([0.95, 0.90, 0.85, 0.80, 0.75])

        df_bench = pd.DataFrame({"Close": bench}, index=dates)
        df_asset = pd.DataFrame({"Close": asset}, index=dates)

        with patch("market.beta_calculator.fetch_prices") as mock_fetch:
            mock_fetch.side_effect = lambda t, **kwargs: df_asset if t == "AAPL" else df_bench
            info = calculate_asset_beta("AAPL", "SPY")
            self.assertEqual(info["status"], "success")
            self.assertIsNotNone(info["realized_beta_5d"])
            self.assertTrue(info["correlation_break"])
            self.assertGreaterEqual(info["effective_beta"], 1.0)

    def test_high1_mandatory_hedge_failure_gate(self):
        """Hedging engine flags hedge_failed if price is zero or shares is zero for positive hedge dollars."""
        with patch("risk.hedging_engine._latest_close", return_value=0.0):
            res = calculate_hedge_pair("AAPL", long_dollars=20000.0)
            self.assertEqual(res["status"], "hedge_pricing_failed")
            self.assertTrue(res["hedge_failed"])
            self.assertFalse(res["hedge_integrity"])

    def test_high1_alpha_client_aborts_unhedged_entry(self):
        """submit_pair_orders rejects execution if mandatory hedge has failed."""
        mock_client = MagicMock()
        failed_hedge = {
            "hedge_failed": True,
            "hedge_dollars": 5000.0,
            "hedge_shares": 0,
            "reason": "Hedge price unavailable"
        }
        res = submit_pair_orders(mock_client, "AAPL", shares=100, stop_loss_price=95.0, hedge=failed_hedge)
        self.assertEqual(res["status"], "rejected")
        # Ensure alpha BUY order was NOT submitted
        mock_client.submit_order.assert_not_called()

    def test_high2_fail_closed_market_status(self):
        """Autopilot market_is_open fails closed if broker clock throws an error."""
        with patch("execution.autopilot.services.client.get_clock", side_effect=RuntimeError("503 Service Unavailable")):
            is_open, msg = market_is_open()
            self.assertFalse(is_open)
            self.assertIn("Fail-Closed", msg)

    def test_convex_tail_engine_circuit_sentry(self):
        """Convex tail sentry detects severe pre-market gap and flags DEFCON 1."""
        dates = pd.date_range("2026-01-01", periods=5, freq="B")
        df_daily = pd.DataFrame({"Close": [580.0, 580.0, 580.0, 580.0, 580.0]}, index=dates)
        with patch("risk.convex_tail.fetch_prices", return_value=df_daily), \
             patch("market.price_fetcher.fetch_latest_price", return_value=540.0):
            sentry = convex_tail_engine.check_pre_market_circuit_sentry("SPY")
            self.assertTrue(sentry["circuit_breaker_threat"])
            self.assertEqual(sentry["defcon_level"], "DEFCON_1")
            self.assertEqual(sentry["action_required"], "PRE_MARKET_ATOMIC_CASH_SWEEP")


if __name__ == "__main__":
    unittest.main()
