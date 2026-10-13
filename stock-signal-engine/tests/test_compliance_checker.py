"""
Unit Tests for Autonomous Compliance & AI Revision Checker
==========================================================
Verifies:
  1. Whale Trap (Candidate C) defense.
  2. JEV Scooper dislocation exception.
  3. Pre-trade strict gatekeeping (daily loss limit, portfolio heat, RVOL).
  4. Post-trade feedback loop (praise vs. punish multiplier adjustments).
  5. AI review logging and persistence.
"""

import os
import tempfile
import unittest
from pathlib import Path

from compliance.ai_revision_checker import AIRevisionChecker, TradeReviewPacket
from compliance.autonomous_checker import AutonomousComplianceChecker


class TestAutonomousComplianceChecker(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_compliance.db"
        self.checker = AutonomousComplianceChecker(db_path=self.db_path)
        self.ai_checker = AIRevisionChecker(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_candidate_c_whale_trap_blocked(self):
        """High RVOL (>= 1.8x) + Negative momentum (<= -1.0%) must be BLOCKED for breakout strategies."""
        cert = self.checker.audit_pre_trade_setup(
            ticker="CAND_C",
            price=45.0,
            rvol=3.2,                 # Heavy volume
            price_change_5d_pct=-2.5, # Falling price -> Whale distribution!
            strategy_candidate="ross_momentum",
            account_equity=10000.0,
            current_heat=0.10,
            day_pnl_pct=0.0,
        )
        self.assertFalse(cert.approved)
        self.assertEqual(cert.verdict, "BLOCKED_VIOLATION")
        self.assertTrue(any("WHALE_TRAP" in v or "WHALE TRAP" in v for v in cert.violations))

    def test_jev_scooper_authorized_on_extreme_dislocation(self):
        """Whale dump capitulation void IS authorized if dislocation Z <= -1.8 for JEV Scooper."""
        cert = self.checker.audit_pre_trade_setup(
            ticker="CAND_SCOOP",
            price=22.0,
            rvol=2.5,
            price_change_5d_pct=-4.0,
            dislocation_zscore=-2.2,  # Severe dislocation void
            strategy_candidate="jev_scooper",
            account_equity=10000.0,
            current_heat=0.10,
            day_pnl_pct=0.0,
        )
        self.assertTrue(cert.approved)
        self.assertEqual(cert.verdict, "PASSED_STRICT")
        self.assertTrue(any("WHALE_DUMP_DISLOCATION" in p or "dislocation" in p.lower() for p in cert.praises))

    def test_daily_drawdown_hard_killswitch(self):
        """Day PnL <= -3% must freeze all entries unconditionally."""
        cert = self.checker.audit_pre_trade_setup(
            ticker="AAPL",
            price=220.0,
            rvol=1.5,
            price_change_5d_pct=2.0,
            sentiment_score=0.40,
            account_equity=10000.0,
            current_heat=0.10,
            day_pnl_pct=-0.035,        # -3.5% day loss!
        )
        self.assertFalse(cert.approved)
        self.assertTrue(any("DAILY_DRAWDOWN_LIMIT" in v for v in cert.violations))

    def test_heat_limit_gate(self):
        """Portfolio heat >= 50% must block further entries."""
        cert = self.checker.audit_pre_trade_setup(
            ticker="MSFT",
            price=450.0,
            rvol=1.5,
            price_change_5d_pct=1.0,
            account_equity=10000.0,
            current_heat=0.52,         # 52% heat
            day_pnl_pct=0.0,
        )
        self.assertFalse(cert.approved)
        self.assertTrue(any("HEAT_LIMIT" in v for v in cert.violations))

    def test_praise_and_punish_feedback_loop(self):
        """
        Wins and disciplined stops must be praised (scaling multiplier up).
        Undisciplined losses must be punished (scaling multiplier down).
        """
        # 1. Base multiplier starts at 1.0
        initial_mult = self.checker.get_strategy_multiplier("core_swing")
        self.assertEqual(initial_mult, 1.0)

        # 2. Praise a clean win
        fb_win = self.checker.audit_closed_trade(
            trade_id=101,
            ticker="MSFT",
            strategy_name="core_swing",
            pnl=150.0,
            entry_price=520.0,
            exit_price=535.0,
            holding_time_hours=4.5,
            reason="TP1 profit target reached",
        )
        self.assertEqual(fb_win.action, "PRAISE")
        self.assertGreater(fb_win.confidence_multiplier, 1.0)

        # 3. Praise a disciplined stop loss
        fb_stop = self.checker.audit_closed_trade(
            trade_id=102,
            ticker="AAPL",
            strategy_name="core_swing",
            pnl=-35.0,
            entry_price=225.0,
            exit_price=221.5,
            holding_time_hours=1.2,
            reason="Monotonic ratchet stop triggered",
        )
        self.assertEqual(fb_stop.action, "PRAISE")

        # 4. Punish an undisciplined panic/manual breach
        fb_bad = self.checker.audit_closed_trade(
            trade_id=103,
            ticker="XYZ",
            strategy_name="ross_momentum",
            pnl=-250.0,
            entry_price=10.0,
            exit_price=7.5,
            holding_time_hours=0.5,
            reason="Unplanned manual panic cut without stop",
        )
        self.assertEqual(fb_bad.action, "PUNISH")
        self.assertLess(fb_bad.confidence_multiplier, 1.0)

    def test_ai_reviewer_heuristic_fallback(self):
        """Autonomous AI reviewer outputs valid verdicts, praises/punishments, and rules."""
        packet = TradeReviewPacket(
            ticker="TEST_TICKER",
            strategy="core_swing",
            action="PRE_TRADE_PROPOSAL",
            price=100.0,
            rvol=2.2,
            momentum_5d_pct=3.5,
            sentiment_score=0.45,
            price_stability_index=70.0,
        )
        res = self.ai_checker.evaluate_pre_trade(packet)
        self.assertIn(res.verdict, ["APPROVED_PRAISE", "REVISED_PARAMETERS", "APPROVED_NEUTRAL"])
        self.assertGreaterEqual(res.compliance_score, 70)
        self.assertGreater(len(res.praises), 0)

        # Check audit report generation
        rep = self.checker.generate_ai_compliance_report()
        self.assertIn("strategy_weights", rep)
        self.assertIn("recent_ai_model_reviews", rep)


if __name__ == "__main__":
    unittest.main()
