"""
Tests for 3-Asset Multi-Desk Concurrent Execution & Telemetry
============================================================
Validates:
1. Crypto Perpetual Futures Strategy & Autopilot Cycle
2. CME Micro Index Futures Strategy & Autopilot Cycle
3. Multi-Desk Status API Endpoint (/api/desks/status)
"""

import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path
from fastapi.testclient import TestClient
import pandas as pd

from webapp.app import app
from strategy.crypto_perp_strategy import crypto_strategy
from execution.crypto_futures_autopilot import CryptoFuturesAutopilot
from strategy.cme_futures_strategy import cme_strategy
from execution.cme_futures_autopilot import CMEFuturesAutopilot
from strategy.forex_strategy import forex_strategy
from execution.forex_autopilot import ForexAutopilot


class TestMultiDeskArchitecture(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_crypto_perp_strategy_cascade(self):
        # Create liquidation crash pattern (z-score <= -2.2) with >= 25 bars
        prices = [60000.0] * 22 + [58000.0, 56000.0, 52000.0]
        df = pd.DataFrame({
            "Open": prices,
            "High": [p + 100.0 for p in prices],
            "Low": [p - 100.0 for p in prices],
            "Close": prices,
            "Volume": [1000] * len(prices),
        })
        sig = crypto_strategy.evaluate("BTC/USDT", df, funding_rate=0.0001)
        self.assertIsNotNone(sig)
        if sig:
            self.assertEqual(sig.side, "LONG")
            self.assertIn("LIQUIDATION", sig.strategy_type)
            self.assertGreater(sig.take_profit, sig.entry_price)
            self.assertLess(sig.stop_loss, sig.entry_price)

    def test_cme_futures_strategy_breakout(self):
        # Create 25 bars where the latest bar breaks out above prior 20 bar high
        prices = [5800.0] * 24 + [5830.0]
        df = pd.DataFrame({
            "Open": prices,
            "High": [p + 2.0 for p in prices],
            "Low": [p - 2.0 for p in prices],
            "Close": prices,
            "Volume": [500] * len(prices),
        })
        sig = cme_strategy.evaluate("MES", df)
        self.assertIsNotNone(sig)
        if sig:
            self.assertEqual(sig.symbol, "MES")
            self.assertEqual(sig.side, "LONG")
            self.assertGreater(sig.take_profit, sig.entry_price)
            self.assertLess(sig.stop_loss, sig.entry_price)

    def test_forex_strategy_breakout(self):
        from strategy.forex_strategy import forex_strategy
        prices = [1.1150] * 24 + [1.1210]  # Breakout
        df = pd.DataFrame({
            "Open": prices,
            "High": [p + 0.0005 for p in prices],
            "Low": [p - 0.0005 for p in prices],
            "Close": prices,
            "Volume": [1000] * len(prices),
        })
        sig = forex_strategy.evaluate("EUR/USD", df)
        self.assertIsNotNone(sig)
        if sig:
            self.assertEqual(sig.symbol, "EUR/USD")
            self.assertEqual(sig.side, "LONG")
            self.assertGreater(sig.take_profit, sig.entry_price)
            self.assertLess(sig.stop_loss, sig.entry_price)
            self.assertGreater(sig.pips_tp, 0)
            self.assertGreater(sig.pips_sl, 0)

    def test_forex_strategy_breakdown_short(self):
        prices = [1.1200] * 24 + [1.1140]  # Breakdown below prior 20-bar low
        df = pd.DataFrame({
            "Open": prices,
            "High": [p + 0.0005 for p in prices],
            "Low": [p - 0.0005 for p in prices],
            "Close": prices,
            "Volume": [1000] * len(prices),
        })
        sig = forex_strategy.evaluate("EUR/USD", df)
        self.assertIsNotNone(sig)
        if sig:
            self.assertEqual(sig.symbol, "EUR/USD")
            self.assertEqual(sig.side, "SHORT")
            self.assertLess(sig.take_profit, sig.entry_price)
            self.assertGreater(sig.stop_loss, sig.entry_price)
            self.assertGreater(sig.pips_tp, 0)
            self.assertGreater(sig.pips_sl, 0)

    def test_forex_strategy_overbought_fade_short(self):
        # 20 flat bars followed by a sharp spike causing Z >= 1.8 without breaking high channel (flat prior)
        prices = [1.1200] * 20 + [1.1280]
        # set prior highs high enough so breakout doesn't shadow mean reversion
        highs = [1.1350] * 20 + [1.1285]
        df = pd.DataFrame({
            "Open": prices,
            "High": highs,
            "Low": [p - 0.0005 for p in prices],
            "Close": prices,
            "Volume": [1000] * len(prices),
        })
        sig = forex_strategy.evaluate("EUR/USD", df)
        self.assertIsNotNone(sig)
        if sig:
            self.assertEqual(sig.side, "SHORT")
            self.assertEqual(sig.strategy_type, "ASIAN_MEAN_REVERSION")
            self.assertLess(sig.take_profit, sig.entry_price)
            self.assertGreater(sig.stop_loss, sig.entry_price)

    def test_desks_status_api(self):
        resp = self.client.get("/api/desks/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("summary", data)
        self.assertIn("desks", data)
        self.assertEqual(data["summary"]["total_desks"], 4)
        self.assertIn("stocks", data["desks"])
        self.assertIn("crypto_perp", data["desks"])
        self.assertIn("cme_futures", data["desks"])
        self.assertIn("forex", data["desks"])

        # Check Desk 1 Stocks (Alpaca)
        stocks = data["desks"]["stocks"]
        self.assertIn(stocks["status"], ["RUNNING", "STOPPED"])
        self.assertGreater(stocks["equity"], 0.0)

        # Check Desk 2 Crypto
        crypto = data["desks"]["crypto_perp"]
        self.assertEqual(crypto["broker"], "CCXT Demo (Binance/OKX)")
        self.assertGreaterEqual(crypto["equity"], 0.0)

        # Check Desk 3 CME Futures
        cme = data["desks"]["cme_futures"]
        self.assertEqual(cme["broker"], "CME Simulated Feed (MES, MNQ, MCL, MGC)")
        self.assertGreaterEqual(cme["equity"], 0.0)

        # Check Desk 4 Forex
        fx = data["desks"]["forex"]
        self.assertEqual(fx["broker"], "Interbank FX Demo (20:1 Margin)")
        self.assertGreaterEqual(fx["equity"], 0.0)

    @patch("webapp.app._leaderboard", return_value=[{"ticker": "AAPL", "composite_score": 90.0}])
    def test_benchmark_and_scan_api(self, mock_lb):
        bench_resp = self.client.get("/api/desks/benchmark")
        self.assertEqual(bench_resp.status_code, 200)
        bench = bench_resp.json()
        self.assertIn("champion", bench)
        self.assertIn("ranking", bench)
        self.assertEqual(len(bench["ranking"]), 4)

        scan_resp = self.client.get("/api/desks/scan?desk=all")
        self.assertEqual(scan_resp.status_code, 200)
        scan = scan_resp.json()
        self.assertIn("stocks", scan)
        self.assertIn("crypto", scan)
        self.assertIn("futures", scan)
        self.assertIn("forex", scan)

    def test_forex_shock_detector_velocity(self):
        # Long position experiencing sudden adverse drop of 25 pips (entry 1.3200 -> 1.3175)
        pos_long = {
            "entry_price": 1.3200,
            "pip_size": 0.0001,
            "side": "LONG",
            "pips_sl": 16.0,
            "ratcheted": False,
        }
        res_long = forex_strategy.detect_shock("GBP/USD", pos_long, curr_price=1.3175)
        self.assertTrue(res_long["shocked"])
        self.assertEqual(res_long["type"], "VELOCITY_SHOCK")
        self.assertIn("Adverse Pip Spike", res_long["reason"])

        # Short position experiencing sudden adverse rise of 25 pips (entry 1.3200 -> 1.3225)
        pos_short = {
            "entry_price": 1.3200,
            "pip_size": 0.0001,
            "side": "SHORT",
            "pips_sl": 16.0,
            "ratcheted": False,
        }
        res_short = forex_strategy.detect_shock("GBP/USD", pos_short, curr_price=1.3225)
        self.assertTrue(res_short["shocked"])
        self.assertEqual(res_short["type"], "VELOCITY_SHOCK")
        self.assertIn("Adverse Pip Spike", res_short["reason"])

    def test_forex_shock_detector_candle_spike(self):
        # 14 bars where standard range is ~10 pips, and last bar dislocates with 45 pips (4.5x ATR)
        base = 1.3200
        ranges = [0.0010] * 13 + [0.0045]
        opens_adverse = [base] * 13 + [base + 0.0045] # Opened high, collapsed down
        highs = [base + r for r in ranges]
        lows = [base] * 14
        closes_adverse = [base + r * 0.5 for r in ranges[:13]] + [base] # Closed at bottom (red drop)
        df_adverse = pd.DataFrame({"Open": opens_adverse, "High": highs, "Low": lows, "Close": closes_adverse})

        pos = {
            "entry_price": 1.3200,
            "pip_size": 0.0001,
            "side": "LONG",
            "pips_sl": 16.0,
            "ratcheted": True,
        }
        res = forex_strategy.detect_shock("GBP/USD", pos, curr_price=1.3200, df=df_adverse)
        self.assertTrue(res["shocked"])
        self.assertEqual(res["type"], "CANDLE_VOLATILITY_SHOCK")

        # Favorable expansion candle (green spike up in our favor) must NOT shock exit
        opens_favorable = [base] * 14
        closes_favorable = [base + r * 0.5 for r in ranges[:13]] + [base + 0.0045]
        df_favorable = pd.DataFrame({"Open": opens_favorable, "High": highs, "Low": lows, "Close": closes_favorable})
        res_fav = forex_strategy.detect_shock("GBP/USD", pos, curr_price=1.3245, df=df_favorable)
        self.assertFalse(res_fav["shocked"])

    def test_forex_near_target_exhaustion_harvest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_p = Path(tmpdir) / "forex_state.json"
            engine = ForexAutopilot(state_path=state_p)
            
            # Setup deep winner: Target 1.32321 (+32 pips), current price 1.32314 (+31.4 pips, 0.7 pips away)
            engine.state["positions"]["GBP/USD"] = {
                "symbol": "GBP/USD",
                "side": "LONG",
                "entry_price": 1.32001,
                "current_price": 1.32314,
                "stop_loss": 1.32001,
                "take_profit": 1.32321,
                "pip_size": 0.0001,
                "pips_sl": 16.0,
                "pips_tp": 32.0,
                "pip_val_usd": 10.0,
                "lots": 2.0,
                "margin_reserved": 10000.0,
                "unrealized_pnl": 626.0,
                "unrealized_pips": 31.3,
                "ratcheted": True,
                "opened_at": 1791445116.0,
            }
            # Mock fetch_live_bars to return target price
            engine.fetch_live_bars = lambda sym: pd.DataFrame({
                "Close": [1.32314], "High": [1.32314], "Low": [1.32314], "Open": [1.32314]
            })
            
            engine.manage_open_positions()
            
            # Trade must be closed under Near-Target Profit Harvest
            self.assertNotIn("GBP/USD", engine.state["positions"])
            self.assertEqual(len(engine.state["closed_trades"]), 1)
            closed = engine.state["closed_trades"][0]
            self.assertIn("Near-Target Profit Harvest", closed["reason"])
            self.assertGreater(closed["pnl"], 600.0)
            self.assertGreater(engine.state["cash"], 50000.0)

    def test_forex_scale_out_and_trailing_profit_ratchet(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_p = Path(tmpdir) / "forex_state.json"
            engine = ForexAutopilot(state_path=state_p)
            
            # Setup fresh trade: Entry 1.3200, SL 1.3184 (16 pips risk, R=16)
            engine.state["positions"]["EUR/USD"] = {
                "symbol": "EUR/USD",
                "side": "LONG",
                "entry_price": 1.3200,
                "current_price": 1.3200,
                "stop_loss": 1.3184,
                "take_profit": 1.3248,
                "pip_size": 0.0001,
                "pips_sl": 16.0,
                "pips_tp": 48.0,
                "pip_val_usd": 10.0,
                "lots": 2.0,
                "margin_reserved": 10000.0,
                "unrealized_pnl": 0.0,
                "unrealized_pips": 0.0,
                "ratcheted": True,
                "opened_at": 1791445116.0,
            }
            
            test_price = [1.3217] # +17 pips > 1.0R (16 pips)
            engine.fetch_live_bars = lambda sym: pd.DataFrame({
                "Close": [test_price[0]], "High": [test_price[0]], "Low": [test_price[0]], "Open": [test_price[0]]
            })

            # Pass 1: Should trigger 50% scale-out and move SL to entry + 1 pip green floor
            engine.manage_open_positions()
            
            pos = engine.state["positions"]["EUR/USD"]
            self.assertEqual(pos["lots"], 1.0)
            self.assertTrue(pos["scaled_out_50"])
            self.assertGreaterEqual(pos["stop_loss"], 1.3201)  # Green floor: entry + 1 pip or trailed
            self.assertGreater(engine.state["total_realized_pnl"], 150.0)
            
            # Pass 2: Price advances to 1.3225 (+25 pips >= 1.5R)
            # Unchoked trailing stop ratchets 0.6R (9.6 pips) behind peak price: 1.3225 - 0.00096 = 1.32154
            test_price[0] = 1.3225
            engine.manage_open_positions()
            
            pos_updated = engine.state["positions"]["EUR/USD"]
            self.assertTrue(pos_updated["trailed_profit"])
            self.assertAlmostEqual(pos_updated["stop_loss"], 1.32154, places=4)
            self.assertGreater(pos_updated["stop_loss"], pos_updated["entry_price"])

    def test_crypto_strategy_short_setups(self):
        prices = [60000.0] * 20 + [58500.0]  # -2.5% return in 5 bars
        volumes = [100] * 19 + [300, 300]   # high volume RVOL >= 2.0
        df = pd.DataFrame({"Open": prices, "High": [p + 50 for p in prices], "Low": [p - 50 for p in prices], "Close": prices, "Volume": volumes})
        sig = crypto_strategy.evaluate("BTC/USDT", df)
        self.assertIsNotNone(sig)
        if sig:
            self.assertEqual(sig.side, "SHORT")
            self.assertIn("WHALE_DUMP", sig.strategy_type)
            self.assertLess(sig.take_profit, sig.entry_price)
            self.assertGreater(sig.stop_loss, sig.entry_price)

    def test_crypto_profit_harvesting_and_scale_out(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_p = Path(tmpdir) / "crypto_state.json"
            engine = CryptoFuturesAutopilot(state_path=state_p)
            engine.state["positions"]["BTC/USDT"] = {
                "symbol": "BTC/USDT",
                "side": "LONG",
                "entry_price": 60000.0,
                "current_price": 60000.0,
                "stop_loss": 59000.0,
                "take_profit": 62000.0,
                "contracts": 0.5,
                "notional_margin": 10000.0,
                "leverage": 3,
                "unrealized_pnl": 0.0,
                "opened_at": 1791445116.0,
            }
            # Test scale-out at +0.8R
            test_px = [60850.0]
            engine.fetch_live_bars = lambda sym: pd.DataFrame({"Close": [test_px[0]]})
            engine.manage_open_positions()

            pos = engine.state["positions"]["BTC/USDT"]
            self.assertEqual(pos["contracts"], 0.25)
            self.assertTrue(pos["scaled_out_50"])
            self.assertGreater(pos["stop_loss"], pos["entry_price"])
            self.assertGreater(engine.state["total_realized_pnl"], 100.0)

            # Test near-target harvest at 90% of TP
            test_px[0] = 61850.0
            engine.manage_open_positions()
            self.assertNotIn("BTC/USDT", engine.state["positions"])
            self.assertIn("Near-Target Profit Harvest", engine.state["closed_trades"][0]["reason"])

    def test_cme_strategy_short_setups(self):
        prices = [5800.0] * 24 + [5750.0]  # Channel breakdown
        df = pd.DataFrame({"Open": prices, "High": [p + 2 for p in prices], "Low": [p - 2 for p in prices], "Close": prices, "Volume": [500] * len(prices)})
        sig = cme_strategy.evaluate("MES", df)
        self.assertIsNotNone(sig)
        if sig:
            self.assertEqual(sig.side, "SHORT")
            self.assertLess(sig.take_profit, sig.entry_price)
            self.assertGreater(sig.stop_loss, sig.entry_price)

    def test_cme_profit_harvesting_and_scale_out(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_p = Path(tmpdir) / "cme_state.json"
            engine = CMEFuturesAutopilot(state_path=state_p)
            engine.state["positions"]["MES"] = {
                "symbol": "MES",
                "side": "LONG",
                "entry_price": 5800.0,
                "current_price": 5800.0,
                "stop_loss": 5780.0,
                "take_profit": 5840.0,
                "contracts": 2,
                "margin_held": 2500.0,
                "point_value": 5.0,
                "unrealized_pnl": 0.0,
                "opened_at": 1791445116.0,
            }
            # Test scale out at +0.8R
            test_px = [5817.0]
            engine.fetch_live_bars = lambda sym: pd.DataFrame({"Close": [test_px[0]]})
            engine.manage_open_positions()

            pos = engine.state["positions"]["MES"]
            self.assertEqual(pos["contracts"], 1)
            self.assertTrue(pos["scaled_out_50"])
            self.assertGreater(pos["stop_loss"], pos["entry_price"])

            # Test near-target harvest at 90% of TP
            test_px[0] = 5837.0
            engine.manage_open_positions()
            self.assertNotIn("MES", engine.state["positions"])
            self.assertIn("Near-Target Profit Harvest", engine.state["closed_trades"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
