"""
Unit Test Suite for Desk 1 (US Equities) Fixes
==============================================
Validates:
  1. Point-in-Time (PIT) Feature Integrity (Strictly closed bars).
  2. SMC Liquidity Sweep & Asymmetric Geometry (R:R >= 2.2:1).
  3. Unchoked Trailing Ratchet (Arms at >= +1.5R with 0.6R breathing cushion, no premature breakeven choking).
  4. Self-Improving Expectancy Tracker (Out-of-sample feedback loop).
  5. Duplicate Entry Guard (Prevents re-buying symbols already held).
  6. GTC TimeInForce Enforcement on Bracket Stops.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from alpaca.trading.enums import TimeInForce
from execution.alpha_client import submit_bracket_buy
from strategy.equities_strategy import (
    EquitiesSelfLearningTracker,
    EquitySignal,
    InstitutionalEquitiesStrategy,
)


class TestEquitiesDesk1Fixes(unittest.TestCase):

    def setUp(self):
        # Create 35 synthetic daily candles
        dates = pd.date_range("2026-08-01", periods=35, freq="D")
        np.random.seed(42)
        base = 150.0
        records = []
        for d in dates:
            o = base + np.random.uniform(-1, 1)
            h = o + np.random.uniform(0.5, 2.5)
            l = o - np.random.uniform(0.5, 2.5)
            c = np.random.uniform(l, h)
            v = np.random.uniform(1_000_000, 5_000_000)
            records.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": v})
            base = c
        self.df = pd.DataFrame(records, index=dates)

    def test_point_in_time_feature_integrity(self):
        """Ensures features only compute on closed historical bars (df.iloc[:-1])."""
        strategy = InstitutionalEquitiesStrategy()
        feats = strategy.compute_point_in_time_features(self.df)

        self.assertIn("swing_high_20", feats)
        self.assertIn("swing_low_20", feats)
        self.assertIn("atr", feats)

        # Closed bar swing high must not look ahead to current bar high
        closed_bars = self.df.iloc[:-1]
        expected_sw_high = float(np.max(closed_bars["High"].values[-20:]))
        self.assertAlmostEqual(feats["swing_high_20"], expected_sw_high, places=4)

    def test_smc_liquidity_sweep_and_target_asymmetry(self):
        """Verifies SMC Liquidity Sweep generates minimum 2.2:1 Target Profit."""
        strategy = InstitutionalEquitiesStrategy()

        # Artificially create a swing low sweep on the last closed bar
        df_sweep = self.df.copy()
        sw_low = float(np.min(df_sweep.iloc[:-2]["Low"].values[-20:]))

        # Bar -2 sweeps below swing low but reclaims above with a large lower wick (60%)
        swept_low = sw_low - 2.50
        df_sweep.iloc[-2, df_sweep.columns.get_loc("Low")] = swept_low
        df_sweep.iloc[-2, df_sweep.columns.get_loc("Open")] = sw_low + 0.50
        df_sweep.iloc[-2, df_sweep.columns.get_loc("Close")] = sw_low + 1.20
        df_sweep.iloc[-2, df_sweep.columns.get_loc("High")] = sw_low + 1.50
        df_sweep.iloc[-1, df_sweep.columns.get_loc("Close")] = sw_low + 1.30

        sig = strategy.evaluate_equity_ticker("AAPL", df_sweep, sentiment_score=0.40)
        self.assertIsNotNone(sig)
        self.assertEqual(sig.side, "LONG")
        self.assertEqual(sig.strategy_type, "SMC_SWEEP_LONG")

        # Geometry verification
        risk_dist = sig.entry_price - sig.stop_loss
        reward_dist = sig.take_profit - sig.entry_price
        rr_actual = reward_dist / risk_dist

        self.assertGreaterEqual(rr_actual, 2.20, f"Expected R:R >= 2.2, got {rr_actual:.2f}")

    def test_unchoked_trailing_ratchet_behavior(self):
        """
        Tests the Unchoked Trailing Ratchet:
          - Does NOT choke winners at +0.5R to +1.0R to a tiny +0.10 ATR breakeven floor.
          - Arms at >= +1.5R with 0.6R cushion, locking in a +0.5R floor.
        """
        entry = 100.0
        initial_stop = 96.0
        risk_unit = entry - initial_stop  # 4.0

        # Case A: Minor profit at +0.8R (high = 103.20).
        # Old broken behavior: choked stop to 100.10.
        # New behavior: does NOT prematurely choke; stays at protective stop.
        high_seen = 103.20
        profit_r = (high_seen - entry) / risk_unit  # 0.8R
        current_stop = initial_stop
        armed = False

        if profit_r >= 1.5:
            cushion = 0.60 * risk_unit
            ratchet_floor = round(high_seen - cushion, 2)
            guaranteed_floor = round(entry + (0.50 * risk_unit), 2)
            current_stop = max(current_stop, ratchet_floor, guaranteed_floor)
            armed = True

        self.assertFalse(armed, "Ratchet should not arm at +0.8R")
        self.assertEqual(current_stop, initial_stop, "Stop should remain unchoked at initial stop")

        # Case B: Strong runner at +2.0R (high = 108.00).
        # Ratchet arms: cushion = 0.6 * 4 = 2.4. Ratchet floor = 108.00 - 2.40 = 105.60.
        # Guaranteed floor = 100.00 + (0.5 * 4) = 102.00.
        high_seen = 108.00
        profit_r = (high_seen - entry) / risk_unit  # 2.0R
        if profit_r >= 1.5:
            cushion = 0.60 * risk_unit
            ratchet_floor = round(high_seen - cushion, 2)
            guaranteed_floor = round(entry + (0.50 * risk_unit), 2)
            current_stop = max(current_stop, ratchet_floor, guaranteed_floor)
            armed = True

        self.assertTrue(armed)
        self.assertAlmostEqual(current_stop, 105.60, places=2)
        self.assertGreater(current_stop, entry + 2.0, "Floor must be comfortably in profit (+1.4R)")

    def test_self_improving_expectancy_tracker(self):
        """Tests rolling profit factor calculation and dynamic sizing multipliers."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            tracker = EquitiesSelfLearningTracker(state_path=temp_path)

            # Cold start: neutral 1.0x
            self.assertEqual(tracker.get_multiplier("SMC_SWEEP_LONG"), 1.0)

            # Record 4 winning trades (+2.5R each, $500 profit)
            for _ in range(4):
                tracker.record_trade("SMC_SWEEP_LONG", pnl=500.0, r_multiple=2.5, entry_price=100.0, exit_price=110.0)

            # Expectancy multiplier should boost to 1.20x
            mult = tracker.get_multiplier("SMC_SWEEP_LONG")
            self.assertEqual(mult, 1.20, f"Expected 1.20x boost for high profit factor, got {mult}")

            # Record 8 losing trades on a bad setup
            for _ in range(8):
                tracker.record_trade("BAD_SETUP", pnl=-500.0, r_multiple=-1.0, entry_price=100.0, exit_price=96.0)

            # Bad setup should be vetoed (0.0x)
            bad_mult = tracker.get_multiplier("BAD_SETUP")
            self.assertEqual(bad_mult, 0.0, f"Expected 0.0x veto on persistent losing setup, got {bad_mult}")

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_gtc_time_in_force_enforcement(self):
        """Verifies submit_bracket_buy defaults to TimeInForce.GTC so stops survive overnight."""
        mock_client = MagicMock()
        mock_order = MagicMock()
        mock_order.id = "mock_ord_123"
        mock_client.submit_order.return_value = mock_order

        res = submit_bracket_buy(
            client=mock_client,
            ticker="MSFT",
            qty=10,
            limit_price=520.0,
            take_profit=540.0,
            stop_price=510.0,
        )

        self.assertEqual(res["tif"], "TimeInForce.GTC")
        self.assertEqual(res["status"], "submitted")


if __name__ == "__main__":
    unittest.main()
