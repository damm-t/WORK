"""
Unit Test Suite for Desk 3 (CME Micro & Commodity Futures) and Desk 4 (Forex 24/5 Macro)
========================================================================================
Validates:
  1. CME Micro/Commodity Futures Strategy R:R Asymmetry (>= 2.2:1 Target Profit).
  2. CME Unchoked Trailing Ratchet (Arms at >= +1.5R with 0.6R cushion, locking +0.5R floor).
  3. CME Self-Learning Expectancy Tracker (Recording, rolling PF, multipliers, and veto).
  4. Forex Macro Strategy R:R Asymmetry (>= 2.2:1 Target Profit across EUR/USD and USD/JPY).
  5. Forex Unchoked Trailing Ratchet (Arms at >= +1.5R with 0.6R cushion, locking +0.5R floor).
  6. Forex Self-Learning Expectancy Tracker (Recording, rolling PF, multipliers, and veto).
  7. API Self-Learning Endpoint Integration (All 4 desks exposed).
"""

import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from strategy.cme_futures_strategy import (
    CMEFuturesSelfLearningTracker,
    CMEFuturesStrategyEngine,
)
from execution.cme_futures_autopilot import CMEFuturesAutopilot

from strategy.forex_strategy import (
    ForexSelfLearningTracker,
    ForexStrategyEngine,
)
from execution.forex_autopilot import ForexAutopilot


class TestCMEFuturesDeskFixes(unittest.TestCase):

    def setUp(self):
        # Create 35 synthetic 1-hour bars for CME commodity/futures testing
        dates = pd.date_range("2026-08-01", periods=35, freq="h")
        base = 25.0  # e.g., CORN or WEAT price
        records = []
        for d in dates:
            o = base
            h = o + 0.40
            l = o - 0.30
            c = o + 0.20
            v = 15000
            records.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": v})
            base = c
        self.df = pd.DataFrame(records, index=dates)

    def test_cme_target_profit_asymmetry_ge_2_2(self):
        """Verifies CME Micro/Commodity signals enforce strict >= 2.20:1 R:R floor."""
        engine = CMEFuturesStrategyEngine()

        for sym in ["CORN", "SOYB", "WEAT", "MCL", "MGC", "MES"]:
            sig = engine.evaluate(sym, self.df)
            if sig.side in ("LONG", "SHORT"):
                if sig.side == "LONG":
                    risk = sig.entry_price - sig.stop_loss
                    reward = sig.take_profit - sig.entry_price
                else:
                    risk = sig.stop_loss - sig.entry_price
                    reward = sig.entry_price - sig.take_profit

                self.assertGreater(risk, 0.0)
                rr = reward / risk
                self.assertGreaterEqual(
                    round(rr, 2),
                    2.20,
                    f"CME {sym} signal R:R {rr:.3f} failed >= 2.20:1 constraint"
                )

    def test_cme_self_learning_tracker_mechanics(self):
        """Tests CME self-learning tracker recording, win rate, and dynamic multiplier."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "cme_learning.json"
            tracker = CMEFuturesSelfLearningTracker(state_path=tmp_path)

            # Cold start baseline
            self.assertEqual(tracker.get_multiplier("VWAP_RECLAIM"), 1.0)

            # Record 5 winning trades (PF > 2.0)
            for i in range(5):
                tracker.record_trade("VWAP_RECLAIM", pnl=300.0, r_multiple=2.4, entry_price=25.0, exit_price=26.0)

            # Expect 1.20x Boost
            self.assertEqual(tracker.get_multiplier("VWAP_RECLAIM"), 1.20)
            summary = tracker.get_performance_summary()
            self.assertIn("VWAP_RECLAIM", summary)
            self.assertEqual(summary["VWAP_RECLAIM"]["win_rate_pct"], 100.0)
            self.assertGreaterEqual(summary["VWAP_RECLAIM"]["profit_factor"], 2.0)

            # Record 10 straight losses to simulate broken setup
            for i in range(10):
                tracker.record_trade("BAD_SETUP", pnl=-150.0, r_multiple=-1.0, entry_price=25.0, exit_price=24.0)

            # Expect 0.00x VETO
            self.assertEqual(tracker.get_multiplier("BAD_SETUP"), 0.0)

    def test_cme_unchoked_trailing_ratchet(self):
        """
        Validates CME Unchoked Trailing Ratchet:
          - Does not choke winner below +1.5R.
          - Arms at >= +1.5R with 0.6R cushion behind peak price.
          - Guarantees minimum +0.5R profit floor.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_state = Path(tmpdir) / "cme_state.json"
            autopilot = CMEFuturesAutopilot(state_path=tmp_state)

            # Seed an open LONG position
            entry = 100.0
            stop = 96.0  # r_pts = 4.0
            tp = 109.0   # reward = 9.0 (2.25:1)
            autopilot.state["positions"]["CORN"] = {
                "symbol": "CORN",
                "side": "LONG",
                "entry_price": entry,
                "current_price": entry,
                "stop_loss": stop,
                "orig_stop_loss": stop,
                "take_profit": tp,
                "contracts": 2,
                "point_value": 50.0,
                "margin_held": 2000.0,
                "strategy": "VWAP_RECLAIM",
                "score": 85.0,
                "opened_at": time.time(),
            }

            # Scenario A: Price is at +1.0R (104.0) - Unchoked ratchet should NOT trigger yet
            mock_df_104 = pd.DataFrame([{"Close": 104.0}])
            with patch.object(autopilot, "fetch_live_bars", return_value=mock_df_104):
                autopilot.manage_open_positions()

            pos = autopilot.state["positions"]["CORN"]
            # Stop may be moved by 50% scaleout at 0.8R to +0.5R floor (102.0), but not choked tighter
            self.assertLessEqual(pos["stop_loss"], 102.0)

            # Scenario B: Price advances to +1.8R (107.2) - Unchoked ratchet arms at >= 1.5R!
            # Peak = 107.2, trail_dist = 4.0 * 0.6 = 2.40. Proposed stop = 107.2 - 2.4 = 104.80.
            mock_df_107 = pd.DataFrame([{"Close": 107.2}])
            with patch.object(autopilot, "fetch_live_bars", return_value=mock_df_107):
                autopilot.manage_open_positions()

            pos = autopilot.state["positions"]["CORN"]
            self.assertTrue(pos.get("trailed_profit"))
            self.assertAlmostEqual(pos["stop_loss"], 104.80, places=2)
            self.assertGreaterEqual(pos["stop_loss"], entry + (4.0 * 0.5))  # >= +0.5R floor


class TestForexDeskFixes(unittest.TestCase):

    def setUp(self):
        # Create 35 synthetic 1-hour FX bars
        dates = pd.date_range("2026-08-01", periods=35, freq="h")
        base = 1.0850
        records = []
        for d in dates:
            o = base
            h = o + 0.0030
            l = o - 0.0020
            c = o + 0.0015
            records.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": 1000})
            base = c
        self.df = pd.DataFrame(records, index=dates)

    def test_forex_target_profit_asymmetry_ge_2_2(self):
        """Verifies Forex signals enforce strict >= 2.20:1 R:R floor across standard & JPY pairs."""
        engine = ForexStrategyEngine()

        for pair in ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"]:
            sig = engine.evaluate(pair, self.df)
            if sig.side in ("LONG", "SHORT"):
                rr = sig.pips_tp / max(sig.pips_sl, 0.1)
                self.assertGreaterEqual(
                    round(rr, 2),
                    2.20,
                    f"Forex {pair} signal R:R {rr:.3f} failed >= 2.20:1 constraint"
                )

    def test_forex_self_learning_tracker_mechanics(self):
        """Tests Forex self-learning tracker recording, win rate, and dynamic multiplier."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "forex_learning.json"
            tracker = ForexSelfLearningTracker(state_path=tmp_path)

            # Cold start baseline
            self.assertEqual(tracker.get_multiplier("LONDON_NY_BREAKOUT"), 1.0)

            # Record 5 winning trades (PF > 2.0)
            for i in range(5):
                tracker.record_trade("LONDON_NY_BREAKOUT", pnl=250.0, r_multiple=2.3, entry_price=1.0850, exit_price=1.0920)

            # Expect 1.20x Boost
            self.assertEqual(tracker.get_multiplier("LONDON_NY_BREAKOUT"), 1.20)
            summary = tracker.get_performance_summary()
            self.assertIn("LONDON_NY_BREAKOUT", summary)
            self.assertEqual(summary["LONDON_NY_BREAKOUT"]["win_rate_pct"], 100.0)

            # Record 8 straight losses
            for i in range(8):
                tracker.record_trade("POOR_DRIFT", pnl=-120.0, r_multiple=-1.0, entry_price=1.0850, exit_price=1.0800)

            # Expect 0.00x VETO
            self.assertEqual(tracker.get_multiplier("POOR_DRIFT"), 0.0)

    def test_forex_unchoked_trailing_ratchet(self):
        """
        Validates Forex Unchoked Trailing Ratchet:
          - Arms at >= +1.5R with 0.6R cushion behind peak price.
          - Guarantees minimum +0.5R profit floor.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_state = Path(tmpdir) / "forex_state.json"
            autopilot = ForexAutopilot(state_path=tmp_state)

            # Seed an open LONG position on EUR/USD
            entry = 1.1000
            stop = 1.0980  # r_pips = 20 pips
            tp = 1.1045   # 45 pips (2.25:1)
            autopilot.state["positions"]["EUR/USD"] = {
                "symbol": "EUR/USD",
                "side": "LONG",
                "entry_price": entry,
                "current_price": entry,
                "stop_loss": stop,
                "orig_stop_loss": stop,
                "take_profit": tp,
                "pip_size": 0.0001,
                "pips_sl": 20.0,
                "pips_tp": 45.0,
                "pip_val_usd": 10.0,
                "lots": 0.10,
                "margin_reserved": 500.0,
                "strategy": "LONDON_NY_BREAKOUT",
                "score": 85.0,
                "opened_at": time.time(),
            }

            # Advance price to +35 pips (1.1035, which is 1.75R >= 1.5R)
            # Peak = 1.1035, trail_pips = max(8.0, 20.0 * 0.6) = 12.0 pips.
            # Proposed stop = 1.1035 - 0.0012 = 1.1023. Floor stop = 1.1000 + 10 pips = 1.1010.
            mock_df_1035 = pd.DataFrame([{"Close": 1.1035}])
            with patch.object(autopilot, "fetch_live_bars", return_value=mock_df_1035):
                autopilot.manage_open_positions()

            pos = autopilot.state["positions"]["EUR/USD"]
            self.assertTrue(pos.get("trailed_profit"))
            self.assertAlmostEqual(pos["stop_loss"], 1.1023, places=4)
            self.assertGreaterEqual(pos["stop_loss"], 1.1010)  # Locked above +0.5R floor


class TestSystemSelfLearningAPI(unittest.TestCase):

    def test_api_self_learning_all_four_desks(self):
        """Verifies webapp api_self_learning exposes all 4 desks."""
        from webapp.app import api_self_learning
        res = api_self_learning()

        self.assertIn("timestamp", res)
        self.assertIn("equities", res)
        self.assertIn("crypto_perp", res)
        self.assertIn("cme_futures", res)
        self.assertIn("forex", res)


if __name__ == "__main__":
    unittest.main()
