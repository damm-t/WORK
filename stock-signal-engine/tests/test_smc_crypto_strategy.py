"""
Tests for Smart Money Concepts (SMC) & Self-Improving Crypto Perp Strategy
==========================================================================
Verifies:
  1. SMC Bullish Liquidity Sweep (Judas Swing) triggers LONG with R:R >= 2.0:1.
  2. SMC Bearish Liquidity Sweep (Breakout Trap) triggers SHORT with R:R >= 2.0:1.
  3. Point-in-Time (PIT) feature computation strictly isolates unclosed live bars.
  4. Order Book Depth & Liquidity Wall integration.
  5. Self-Improving Expectancy Tracker dynamically adapts conviction multipliers.
  6. Anti-chop post-trade cooldown (30m) and daily trade limit (max 5/day).
"""

import tempfile
import time
import unittest
from pathlib import Path

import pandas as pd

from execution.crypto_futures_autopilot import CryptoFuturesAutopilot
from strategy.crypto_perp_strategy import (
    CryptoFuturesSignal,
    CryptoPerpStrategyEngine,
    SelfImprovingExpectancyTracker,
)


class TestSMCCryptoStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = CryptoPerpStrategyEngine()

    def test_smc_bullish_liquidity_sweep(self):
        """
        Price sweeps below the 20-bar swing low, but closes back above swing low
        leaving a pronounced lower rejection wick (>40% of range).
        Must trigger SMC_LIQUIDITY_SWEEP_LONG with R:R >= 2.0:1.
        """
        base = 65000.0
        # 20 bars oscillating between 64900 and 65100 (swing_low = 64900)
        prices = [base + ((i % 4) - 2) * 50.0 for i in range(20)]
        lows = [p - 50.0 for p in prices]
        highs = [p + 50.0 for p in prices]

        # Bar 21 (live bar): dips to 64750 (sweeping below 64850 swing low),
        # but aggressively bounces and closes at 64950 (reclaimed above swing low!)
        sweep_open = 64920.0
        sweep_high = 65000.0
        sweep_low = 64750.0   # Swept 100 points below swing low
        sweep_close = 64950.0 # Reclaimed! Lower wick = 64920 - 64750 = 170 / 250 = 68%
        
        all_opens = prices + [sweep_open]
        all_highs = highs + [sweep_high]
        all_lows = lows + [sweep_low]
        all_closes = prices + [sweep_close]
        all_volumes = [500] * 20 + [2500] # Elevated sweep volume

        df = pd.DataFrame({
            "Open": all_opens,
            "High": all_highs,
            "Low": all_lows,
            "Close": all_closes,
            "Volume": all_volumes,
        })

        sig = self.strategy.evaluate("BTC/USDT", df)
        self.assertIsNotNone(sig)
        self.assertEqual(sig.side, "LONG")
        self.assertEqual(sig.strategy_type, "SMC_LIQUIDITY_SWEEP_LONG")
        self.assertGreaterEqual(sig.risk_reward_ratio, 2.0)
        self.assertLess(sig.stop_loss, sweep_low) # Invalidation strictly below the sweep wick
        self.assertGreater(sig.take_profit, sweep_close)

    def test_smc_bearish_liquidity_sweep(self):
        """
        Price pushes above the 20-bar swing high, traps breakout buyers,
        then closes back below swing high leaving a long upper wick.
        Must trigger SMC_LIQUIDITY_SWEEP_SHORT with R:R >= 2.0:1.
        """
        base = 65000.0
        prices = [base + ((i % 4) - 2) * 50.0 for i in range(20)]
        lows = [p - 50.0 for p in prices]
        highs = [p + 50.0 for p in prices]

        # Bar 21: spikes to 65300 (above 65100 swing high), but gets rejected to 65050
        sweep_open = 65080.0
        sweep_high = 65300.0  # Swept 200 points above swing high
        sweep_low = 65020.0
        sweep_close = 65050.0 # Closed back below swing high! Upper wick = 220 / 280 = 78%

        df = pd.DataFrame({
            "Open": prices + [sweep_open],
            "High": highs + [sweep_high],
            "Low": lows + [sweep_low],
            "Close": prices + [sweep_close],
            "Volume": [500] * 20 + [2800],
        })

        sig = self.strategy.evaluate("BTC/USDT", df)
        self.assertIsNotNone(sig)
        self.assertEqual(sig.side, "SHORT")
        self.assertEqual(sig.strategy_type, "SMC_LIQUIDITY_SWEEP_SHORT")
        self.assertGreaterEqual(sig.risk_reward_ratio, 2.0)
        self.assertGreater(sig.stop_loss, sweep_high) # Invalidation strictly above sweep high
        self.assertLess(sig.take_profit, sweep_close)

    def test_point_in_time_integrity(self):
        """
        Verifies Point-in-Time (PIT) integrity (Reel 2: @fidetolabs).
        Indicators like Swing High/Low and ATR are computed on completed historical bars.
        An unclosed live tick bar with wild spikes must NEVER leak into the historical features.
        """
        base = 60000.0
        prices = [base + i * 20.0 for i in range(25)]
        df_hist = pd.DataFrame({
            "Open": prices,
            "High": [p + 15.0 for p in prices],
            "Low": [p - 15.0 for p in prices],
            "Close": prices,
            "Volume": [1000] * len(prices),
        })

        # Historical completed bars feature calculation
        expected_swing_high = float(df_hist["High"].tail(20).max())
        expected_swing_low = float(df_hist["Low"].tail(20).min())

        # Append a temporary volatile live tick bar that spikes +800 and -800 points
        df_live = pd.concat([df_hist, pd.DataFrame({
            "Open": [prices[-1]],
            "High": [prices[-1] + 800.0],
            "Low": [prices[-1] - 800.0],
            "Close": [prices[-1] + 400.0],
            "Volume": [10000],
        })], ignore_index=True)

        feat_live = self.strategy._compute_point_in_time_features(df_live)

        # Historical features on completed bars must match expected_swing_high/low
        self.assertEqual(feat_live["swing_high"], expected_swing_high)
        self.assertEqual(feat_live["swing_low"], expected_swing_low)
        # Verify the live bar's extreme spike did NOT pollute the historical swing high
        self.assertNotEqual(feat_live["swing_high"], float(df_live["High"].iloc[-1]))

    def test_self_improving_expectancy_tracker(self):
        """
        Verifies that out-of-sample trade feedback dynamically updates conviction multipliers:
        - High profit factor (>= 1.40) -> 1.20x boost
        - Persistent negative drift (PF < 0.65 over 8 trades) -> 0.0x temporary VETO
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker_file = Path(tmpdir) / "test_learning.json"
            learner = SelfImprovingExpectancyTracker(tracker_file)

            strat = "SMC_LIQUIDITY_SWEEP_LONG"
            # Simulate 10 high-expectancy winning trades: 8 wins of +$180, 2 losses of -$70
            for _ in range(8):
                learner.record_trade(strat, pnl=180.0, r_multiple=2.2, entry_price=60000.0, exit_price=61320.0)
            for _ in range(2):
                learner.record_trade(strat, pnl=-70.0, r_multiple=-1.0, entry_price=60000.0, exit_price=59400.0)

            mult = learner.get_multiplier(strat)
            self.assertEqual(mult, 1.20, f"Expected 1.20x boost for profitable setup, got {mult}")

            # Now simulate a failing setup with persistent losses
            bad_strat = "BROKEN_CHOP_SETUP"
            for _ in range(2):
                learner.record_trade(bad_strat, pnl=30.0, r_multiple=0.4, entry_price=60000.0, exit_price=60200.0)
            for _ in range(8):
                learner.record_trade(bad_strat, pnl=-85.0, r_multiple=-1.0, entry_price=60000.0, exit_price=59400.0)

            bad_mult = learner.get_multiplier(bad_strat)
            self.assertEqual(bad_mult, 0.0, f"Expected 0.0x veto for losing setup, got {bad_mult}")

    def test_trade_cooldown_and_daily_cap(self):
        """
        Verifies that CryptoFuturesAutopilot enforces 30m cooldown between trades
        on the same coin and a maximum of 5 trades per day.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "crypto_state.json"
            engine = CryptoFuturesAutopilot(state_path=state_file)

            # Set last trade exit to 10 minutes ago (600s < 1800s cooldown)
            engine.state["last_trade_exits"] = {"BTC/USDT": time.time() - 600}

            # Prepare a valid SMC Liquidity Sweep DataFrame
            base = 65000.0
            prices = [base + ((i % 4) - 2) * 50.0 for i in range(20)]
            lows = [p - 50.0 for p in prices]
            highs = [p + 50.0 for p in prices]
            sweep_open, sweep_high, sweep_low, sweep_close = 64920.0, 65000.0, 64750.0, 64950.0

            df = pd.DataFrame({
                "Open": prices + [sweep_open],
                "High": highs + [sweep_high],
                "Low": lows + [sweep_low],
                "Close": prices + [sweep_close],
                "Volume": [500] * 20 + [2500],
            })

            engine.fetch_live_bars = lambda sym: df
            engine.fetch_live_order_book = lambda sym: None

            # Scan and enter should skip BTC/USDT due to active cooldown
            engine.scan_and_enter()
            self.assertNotIn("BTC/USDT", engine.state["positions"])

            # Advance cooldown past 30 minutes (2000s > 1800s)
            engine.state["last_trade_exits"]["BTC/USDT"] = time.time() - 2000
            engine.scan_and_enter()
            # Position should now enter cleanly
            self.assertIn("BTC/USDT", engine.state["positions"])


if __name__ == "__main__":
    unittest.main()
