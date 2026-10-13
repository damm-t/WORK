"""
Tests for Crypto Perp Strategy Fixes
===================================
Verifies:
  1. No false bullish LONG triggers during flat or drifting downward markets.
  2. Symmetric BEARISH MOMENTUM SHORT and WHALE DUMP SHORT setups.
  3. Tier 3 Near-Target Harvest never cuts negative or neutral trades prematurely.
  4. Institutional Compliance Gate approves legitimate SHORT setups.
"""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from compliance.autonomous_checker import compliance_checker
from execution.crypto_futures_autopilot import CryptoFuturesAutopilot
from strategy.crypto_perp_strategy import crypto_strategy


class TestCryptoPerpFixes(unittest.TestCase):
    def test_no_false_long_on_flat_or_downtrend(self):
        """Flat or slightly downward prices must not trigger a bullish momentum breakout."""
        # Flat prices with slight downward drift (-0.05% in 5 bars)
        prices = [60000.0] * 15 + [59990.0, 59985.0, 59980.0, 59975.0, 59970.0]
        df = pd.DataFrame({
            "Open": prices,
            "High": [p + 10 for p in prices],
            "Low": [p - 10 for p in prices],
            "Close": prices,
            "Volume": [100] * len(prices)
        })
        sig = crypto_strategy.evaluate("BTC/USDT", df)
        self.assertIsNotNone(sig)
        # Must NOT be LONG breakout
        self.assertNotEqual(sig.strategy_type, "MOMENTUM_BREAKOUT")

    def test_bearish_momentum_short_trigger(self):
        """Clean bearish EMA downward expansion triggers MOMENTUM_BREAKDOWN_SHORT."""
        base = 60000.0
        # 20 bars with normal price oscillation
        prices = [base + ((i % 5) - 2) * 50.0 for i in range(20)]
        # then 5 bars of steady downward breakdown below EMA20 (-0.4% drop)
        last_px = prices[-1]
        for step in [0.999, 0.998, 0.997, 0.996, 0.995]:
            prices.append(last_px * step)
        df = pd.DataFrame({
            "Open": prices,
            "High": [p + 30 for p in prices],
            "Low": [p - 30 for p in prices],
            "Close": prices,
            "Volume": [100] * len(prices)
        })
        sig = crypto_strategy.evaluate("BTC/USDT", df)
        self.assertIsNotNone(sig)
        self.assertEqual(sig.side, "SHORT")
        self.assertIn("SHORT", sig.strategy_type)
        self.assertLess(sig.take_profit, sig.entry_price)
        self.assertGreater(sig.stop_loss, sig.entry_price)

    def test_near_target_harvest_never_cuts_losses(self):
        """Tier 3 near target harvest must NEVER cut when trade is at a loss or neutral."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_p = Path(tmpdir) / "crypto_state.json"
            engine = CryptoFuturesAutopilot(state_path=state_p)
            engine.state["positions"]["BTC/USDT"] = {
                "symbol": "BTC/USDT",
                "side": "LONG",
                "entry_price": 80000.0,
                "current_price": 80000.0,
                "stop_loss": 79000.0,
                "take_profit": 81000.0,
                "contracts": 0.5,
                "notional_margin": 10000.0,
                "leverage": 3,
                "unrealized_pnl": 0.0,
                "opened_at": 1791445116.0,
            }

            # Price drops slightly to 79980 (loss of -$10)
            engine.fetch_live_bars = lambda sym: pd.DataFrame({"Close": [79980.0]})
            engine.manage_open_positions()

            # Position must STILL BE OPEN! Not closed as near-target harvest!
            self.assertIn("BTC/USDT", engine.state["positions"])
            self.assertEqual(len(engine.state.get("closed_trades", [])), 0)

            # Price surges to 80920 (92% of TP distance in profit)
            engine.fetch_live_bars = lambda sym: pd.DataFrame({"Close": [80920.0]})
            engine.manage_open_positions()

            # Now it should be harvested in profit!
            self.assertNotIn("BTC/USDT", engine.state["positions"])
            self.assertEqual(len(engine.state.get("closed_trades", [])), 1)
            closed = engine.state["closed_trades"][0]
            self.assertIn("Near-Target Profit Harvest", closed["reason"])
            self.assertGreater(closed["pnl"], 400.0)

    def test_compliance_checker_approves_short(self):
        """Institutional compliance gate must approve valid SHORT setups."""
        cert = compliance_checker.audit_pre_trade_setup(
            ticker="BTC_USDT",
            price=60000.0,
            rvol=2.5,
            price_change_5d_pct=-2.5,
            sentiment_score=-0.40,
            dislocation_zscore=-0.8,
            strategy_candidate="core_swing",
            account_equity=70000.0,
            current_heat=0.10,
            day_pnl_pct=0.0,
            side="SHORT",
        )
        self.assertTrue(cert.approved, f"Short should be approved, but got violations: {cert.violations}")
        self.assertNotIn("WHALE_TRAP_DETECTED", str(cert.violations))

    def test_desks_status_session_and_lifetime_pnl(self):
        """Verifies session_realized_pnl and total_realized_pnl distinctions on multi-desk status."""
        from fastapi.testclient import TestClient
        from webapp.app import app

        client = TestClient(app)
        resp = client.get("/api/desks/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("desks", data)
        crypto = data["desks"]["crypto_perp"]
        self.assertIn("session_realized_pnl", crypto)
        self.assertIn("total_realized_pnl", crypto)
        self.assertIn("combined_portfolio_session_pnl", data["summary"])
        self.assertIn("combined_portfolio_lifetime_pnl", data["summary"])


if __name__ == "__main__":
    unittest.main()
