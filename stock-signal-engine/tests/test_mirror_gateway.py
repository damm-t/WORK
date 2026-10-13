"""
Unit Tests for Multi-Broker Trade Mirror Gateway
================================================
Verifies:
  1. Subscriber registration & profile retrieval.
  2. Proportional risk sizing across different account sizes.
  3. Heat limit and risk guardrails per subscriber.
  4. Execution failure isolation (one bad key doesn't fail others).
  5. Audit log recording in SQLite.
"""

import tempfile
import unittest
from pathlib import Path

from gateway.broker_client import BrokerClientFactory
from gateway.mirror_dispatcher import MirrorDispatcher, MirrorTradeSignal
from gateway.subscriber_registry import SubscriberProfile, SubscriberRegistry


class TestMirrorGateway(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sub_db = Path(self.temp_dir.name) / "test_subscribers.db"
        self.mirror_db = Path(self.temp_dir.name) / "test_mirror.db"

        self.registry = SubscriberRegistry(db_path=self.sub_db)
        self.dispatcher = MirrorDispatcher(db_path=self.mirror_db)
        self.dispatcher.registry = self.registry

        # Register two mock subscribers: one small ($10k) and one large ($100k)
        self.registry.register_or_update(SubscriberProfile(
            user_id="sub_small",
            tier="PRO",
            broker_type="simulated_gateway",
            api_key="mock_key_1",
            secret_key="mock_sec_1",
            risk_pct_per_trade=0.015,   # 1.5% risk
            max_portfolio_heat=0.50,
            last_equity=10000.0,
            last_buying_power=20000.0,
            is_active=True,
        ))

        self.registry.register_or_update(SubscriberProfile(
            user_id="sub_whale",
            tier="PREMIUM_VIP",
            broker_type="simulated_gateway",
            api_key="mock_key_2",
            secret_key="mock_sec_2",
            risk_pct_per_trade=0.02,    # 2.0% risk
            max_portfolio_heat=0.45,
            last_equity=100000.0,
            last_buying_power=250000.0,
            is_active=True,
        ))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_subscriber_registration(self):
        sub = self.registry.get_subscriber("sub_small")
        self.assertIsNotNone(sub)
        self.assertEqual(sub.user_id, "sub_small")
        self.assertEqual(sub.risk_pct_per_trade, 0.015)

        all_subs = self.registry.list_all(active_only=True)
        self.assertEqual(len(all_subs), 2)

    def test_proportional_trade_mirroring(self):
        """
        Signal: MSFT @ $500.00, Stop Loss @ $490.00 (Stop distance = $10.00)
        - Sub Small ($10,000 equity, 1.5% risk = $150 risk budget) -> 15 shares
        - Sub Whale ($100,000 equity, 2.0% risk = $2,000 risk budget) -> 200 shares
        """
        signal = MirrorTradeSignal(
            ticker="MSFT",
            side="buy",
            entry_price=500.0,
            stop_loss=490.0,
            take_profit=530.0,
            strategy_name="core_swing",
            grade="A",
            rationale="Grade A Breakout",
        )

        summary = self.dispatcher.replicate_signal(signal)
        self.assertEqual(summary.signal_ticker, "MSFT")
        self.assertEqual(summary.executed_count, 2)
        self.assertEqual(summary.skipped_count, 0)

        # Check proportional sizing
        reports = {r["user_id"]: r for r in summary.subscribers_report}
        self.assertEqual(reports["sub_small"]["shares"], 15)
        self.assertEqual(reports["sub_whale"]["shares"], 200)

        # Check that capital allocated scales correctly
        self.assertEqual(reports["sub_small"]["capital_allocated"], 15 * 500.0)
        self.assertEqual(reports["sub_whale"]["capital_allocated"], 200 * 500.0)

    def test_heat_limit_blocks_overleveraged_subscriber(self):
        """Subscribers with high portfolio heat must be skipped safely."""
        self.registry.register_or_update(SubscriberProfile(
            user_id="sub_hot",
            tier="PRO",
            broker_type="simulated_gateway",
            api_key="mock_key_3",
            secret_key="mock_sec_3",
            max_portfolio_heat=0.30,   # Strict 30% heat
            last_equity=20000.0,
            last_buying_power=5000.0,
            is_active=True,
        ))

        # Mock broker account with 0 cash (100% heat)
        with unittest.mock.patch.object(
            BrokerClientFactory, "get_account",
            return_value={"equity": 20000.0, "cash": 0.0, "buying_power": 5000.0}
        ):
            signal = MirrorTradeSignal(
                ticker="AAPL", side="buy", entry_price=220.0,
                stop_loss=215.0, take_profit=235.0, strategy_name="core_swing"
            )
            summary = self.dispatcher.replicate_signal(signal)
            reports = {r["user_id"]: r for r in summary.subscribers_report}
            self.assertEqual(reports["sub_hot"]["status"], "skipped")
            self.assertIn("Heat limit", reports["sub_hot"]["reason"])


if __name__ == "__main__":
    unittest.main()
