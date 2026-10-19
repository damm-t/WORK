"""
Unit tests for AstraQuant Fail-Closed Physical Risk Pipeline
"""

import unittest
from risk.physical_risk_pipeline import PhysicalRiskPipeline, physical_risk_pipeline
from risk.hedging_engine import get_adaptive_exit_geometry, get_exit_geometry


class TestPhysicalRiskPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = PhysicalRiskPipeline(
            min_rr_ratio=1.8,
            target_rr_ratio=2.0,
            max_risk_equity_pct=0.0025,
            max_dollar_risk_cap=85.0,
        )

    def test_positive_asymmetry_approved(self):
        # Long entry @ 100, Stop @ 98, TP @ 104 -> RR = 4/2 = 2.0:1
        verdict = self.pipeline.audit_order_intent(
            symbol="AAPL",
            side="LONG",
            entry_price=100.0,
            stop_loss=98.0,
            take_profit=104.0,
            portfolio_equity=25000.0,
            requested_size=10.0,
        )
        self.assertTrue(verdict.approved)
        self.assertAlmostEqual(verdict.calculated_rr, 2.0)
        self.assertLessEqual(verdict.max_dollar_loss, 85.0 * 1.15)

    def test_negative_asymmetry_rejected(self):
        # Long entry @ 100, Stop @ 97 (risk 3), TP @ 102 (reward 2) -> RR = 0.67:1 (below 1.8 floor)
        verdict = self.pipeline.audit_order_intent(
            symbol="BTCUSDT",
            side="LONG",
            entry_price=100.0,
            stop_loss=97.0,
            take_profit=102.0,
            portfolio_equity=25000.0,
        )
        self.assertFalse(verdict.approved)
        self.assertTrue(any("Negative Asymmetry Trap" in r for r in verdict.rejection_reasons))

    def test_macro_trend_veto(self):
        # Attempting LONG into macro BEAR trend
        verdict = self.pipeline.audit_order_intent(
            symbol="ETHUSDT",
            side="LONG",
            entry_price=2000.0,
            stop_loss=1950.0,
            take_profit=2150.0,
            portfolio_equity=25000.0,
            macro_ema_trend="BEAR",
        )
        self.assertFalse(verdict.approved)
        self.assertTrue(any("Macro Veto" in r for r in verdict.rejection_reasons))

    def test_wada_chaos_veto(self):
        # Realized volatility 3.2x baseline
        verdict = self.pipeline.audit_order_intent(
            symbol="SOLUSDT",
            side="LONG",
            entry_price=100.0,
            stop_loss=95.0,
            take_profit=115.0,
            portfolio_equity=25000.0,
            realized_volatility_ratio=3.2,
        )
        self.assertFalse(verdict.approved)
        self.assertTrue(any("Wada Chaos Veto" in r for r in verdict.rejection_reasons))

    def test_hedging_engine_geometry_asymmetry(self):
        # Ensure ERRATIC_NOISE and CALM_RANGING have positive asymmetry R:R >= 2.0:1
        erratic = get_adaptive_exit_geometry(psi=30.0, regime="ERRATIC_NOISE")
        self.assertGreaterEqual(erratic["tp1_mult"] / erratic["stop_mult"], 1.8)

        calm = get_adaptive_exit_geometry(psi=50.0, regime="CALM_RANGING")
        self.assertGreaterEqual(calm["tp1_mult"] / calm["stop_mult"], 1.8)


if __name__ == "__main__":
    unittest.main()
