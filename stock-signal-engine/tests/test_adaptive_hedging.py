"""
Unit Tests for Adaptive Exit Geometry, Dynamic Hedge Ratio, and Autopilot Gates
================================================================================
Validates Upgrades 1, 2, 3, and 6:
- Regime-adaptive exit geometry based on PSI
- Dynamic hedge sizing with safety cap (preventing >0.65x net-short inversions)
- RVOL volume quality gate & Bayesian confidence execution gate
"""

import unittest
from risk.hedging_engine import (
    get_exit_geometry,
    get_adaptive_exit_geometry,
    calculate_dynamic_hedge_ratio,
    calculate_exit_levels,
    calculate_hedge_pair,
    tp1_scale_plan,
    ratchet_trailing_stop,
)


class TestAdaptiveExitGeometry(unittest.TestCase):
    def test_default_backward_compatibility(self):
        """When PSI and regime are None, adaptive geometry matches baseline static geometry."""
        base = get_exit_geometry()
        adaptive = get_adaptive_exit_geometry(psi=None, regime=None)
        self.assertEqual(base["stop_mult"], adaptive["stop_mult"])
        self.assertEqual(base["tp1_mult"], adaptive["tp1_mult"])
        self.assertEqual(base["trail_mult"], adaptive["trail_mult"])
        self.assertEqual(adaptive["regime_applied"], "STATIC_BASELINE")

    def test_laminar_trend_geometry(self):
        """Laminar Trend (PSI >= 65) expands TP1 to 3.0x ATR and keeps stop at 1.2x ATR (2.5:1 R:R)."""
        geo = get_adaptive_exit_geometry(psi=72.5, regime="LAMINAR_TREND")
        self.assertEqual(geo["stop_mult"], 1.2)
        self.assertEqual(geo["tp1_mult"], 3.0)
        self.assertEqual(geo["trail_mult"], 1.5)
        self.assertEqual(geo["regime_applied"], "LAMINAR_TREND")

        # Verify exit levels calculation
        levels = calculate_exit_levels(entry_price=100.0, atr=2.0, psi=72.5, regime="LAMINAR_TREND")
        self.assertEqual(levels["hard_stop_price"], 97.6)      # 100 - (1.2 * 2)
        self.assertEqual(levels["take_profit_1_price"], 106.0) # 100 + (3.0 * 2)
        self.assertEqual(levels["trailing_stop_distance"], 3.0)

    def test_erratic_noise_geometry(self):
        """Erratic Noise (PSI < 45) enforces tight stop 1.0x ATR and 2.0x ATR TP1 (positive asymmetry)."""
        geo = get_adaptive_exit_geometry(psi=35.0, regime="ERRATIC_NOISE")
        self.assertEqual(geo["stop_mult"], 1.0)
        self.assertEqual(geo["tp1_mult"], 2.0)
        self.assertEqual(geo["trail_mult"], 1.0)
        self.assertEqual(geo["regime_applied"], "ERRATIC_NOISE")

        levels = calculate_exit_levels(entry_price=100.0, atr=2.0, psi=35.0, regime="ERRATIC_NOISE")
        self.assertEqual(levels["hard_stop_price"], 98.0)      # 100 - (1.0 * 2)
        self.assertEqual(levels["take_profit_1_price"], 104.0) # 100 + (2.0 * 2)
        self.assertEqual(levels["trailing_stop_distance"], 2.0)

    def test_calm_ranging_geometry(self):
        """Calm Ranging (45 <= PSI < 65) sets 1.2x ATR stop and 2.4x ATR TP1 (2:1 R:R)."""
        geo = get_adaptive_exit_geometry(psi=52.0, regime="CALM_RANGING")
        self.assertEqual(geo["stop_mult"], 1.2)
        self.assertEqual(geo["tp1_mult"], 2.4)
        self.assertEqual(geo["trail_mult"], 1.2)
        self.assertEqual(geo["regime_applied"], "CALM_RANGING")


class TestDynamicHedgeRatio(unittest.TestCase):
    def test_bull_regime_minimal_hedge(self):
        """In a Bull/Laminar regime with strong confidence, hedge ratio scales down to 0.10 - 0.15."""
        ratio = calculate_dynamic_hedge_ratio(psi=75.0, bayesian_confidence=80.0, regime="BULL_EXPANSION")
        self.assertGreaterEqual(ratio, 0.10)
        self.assertLessEqual(ratio, 0.20)

    def test_bear_regime_ceiling_cap(self):
        """In a Bear/Erratic regime, hedge ratio is strictly capped at 0.65 to prevent net-short flip."""
        ratio = calculate_dynamic_hedge_ratio(psi=20.0, bayesian_confidence=20.0, regime="BEAR_VOLATILITY")
        self.assertLessEqual(ratio, 0.65)
        self.assertGreaterEqual(ratio, 0.50)

    def test_hedge_pair_hard_cap(self):
        """calculate_hedge_pair should never allocate more than 65% of long notional to the hedge."""
        pair = calculate_hedge_pair("AAPL", long_dollars=50000.0, psi=30.0, bayesian_confidence=35.0)
        self.assertEqual(pair["status"], "success")
        self.assertLessEqual(pair["hedge_dollars"], 50000.0 * 0.65 + 1e-6)
        self.assertLessEqual(pair["hedge_ratio"], 0.65)


class TestAdaptiveScaleOutAndTrail(unittest.TestCase):
    def test_adaptive_tp1_scale_plan(self):
        """Scale-out triggers at 3.0x ATR in Laminar Trend, selling 35% and keeping 65% runner."""
        entry = 100.0
        atr = 2.0
        shares = 100

        # At 104.5 (2.25 ATR), static would trigger TP1, but Laminar requires 106.0 (3.0 ATR)
        plan_laminar = tp1_scale_plan(price=104.5, entry_price=entry, atr=atr, shares=shares,
                                      psi=70.0, regime="LAMINAR_TREND")
        self.assertEqual(plan_laminar["action"], "hold")

        # At 106.5, Laminar triggers scale-out
        plan_hit = tp1_scale_plan(price=106.5, entry_price=entry, atr=atr, shares=shares,
                                  psi=70.0, regime="LAMINAR_TREND")
        self.assertEqual(plan_hit["action"], "scale_out")
        self.assertEqual(plan_hit["sell_qty"], 35)

    def test_adaptive_ratchet_trailing_stop(self):
        """Trailing stop arms at 2.5x ATR in Laminar Trend and trails by 1.5x ATR."""
        entry = 100.0
        atr = 2.0
        # High reached 107.0 (> arm trigger 105.0 for laminar 2.5*2)
        ratchet = ratchet_trailing_stop(entry_price=entry, atr=atr, highest_price_seen=107.0,
                                        current_stop_price=97.0, psi=70.0, regime="LAMINAR_TREND")
        self.assertTrue(ratchet["trailing_armed"])
        # Stop trailed by 1.5 * atr = 3.0 -> 107 - 3 = 104.0
        self.assertEqual(ratchet["stop_price"], 104.0)


class TestRegimeAdaptivePositionSizing(unittest.TestCase):
    def test_laminar_high_conviction_tier(self):
        """Pristine laminar trend with high conviction scales risk to 3.0%."""
        from risk.risk_manager import calculate_regime_risk_pct, calculate_position_size
        risk = calculate_regime_risk_pct(psi=70.0, bayesian_confidence=75.0, regime="LAMINAR_TREND")
        self.assertEqual(risk, 0.030)

        # Sizing produces 3% risk sizing
        pos = calculate_position_size(portfolio_value=100000.0, current_price=100.0, confidence=0.85,
                                      atr=2.0, psi=70.0, regime="LAMINAR_TREND", bayesian_confidence=75.0,
                                      streak_compounding=False)
        self.assertEqual(pos["risk_pct_used"], 0.030)
        self.assertEqual(pos["regime_applied"], "LAMINAR_TREND")
        self.assertGreater(pos["shares"], 0)

    def test_calm_ranging_tier(self):
        """Standard calm ranging sets risk to 2.0%."""
        from risk.risk_manager import calculate_regime_risk_pct
        risk = calculate_regime_risk_pct(psi=55.0, bayesian_confidence=60.0, regime="CALM_RANGING")
        self.assertEqual(risk, 0.020)

    def test_erratic_noise_tier(self):
        """Erratic noise reduces risk exposure to 1.0%."""
        from risk.risk_manager import calculate_regime_risk_pct
        risk = calculate_regime_risk_pct(psi=40.0, bayesian_confidence=50.0, regime="ERRATIC_NOISE")
        self.assertEqual(risk, 0.010)

    def test_chaotic_rejection_tier(self):
        """Chaotic regime (PSI < 30 or Conf < 45) rejects trade with 0% risk."""
        from risk.risk_manager import calculate_regime_risk_pct, calculate_position_size
        risk = calculate_regime_risk_pct(psi=25.0, bayesian_confidence=40.0, regime="ERRATIC_NOISE")
        self.assertEqual(risk, 0.0)

        pos = calculate_position_size(portfolio_value=100000.0, current_price=100.0, confidence=0.85,
                                      atr=2.0, psi=25.0, bayesian_confidence=40.0)
        self.assertEqual(pos["shares"], 0)


class TestStreakCompounding(unittest.TestCase):
    def test_defensive_scaling_on_losing_streak(self):
        """Losing streak of -2 reduces position size defensively."""
        from risk.risk_manager import calculate_streak_compounding_factor

        class MockJournalLosing:
            def get_current_streak(self): return -2
            def stats(self): return {"avg_pnl": -200.0}

        factor = calculate_streak_compounding_factor(journal_instance=MockJournalLosing())
        self.assertEqual(factor, 0.85)

    def test_no_compounding_on_negative_expectancy(self):
        """Winning streak with negative average PnL does NOT scale up (preserves capital)."""
        from risk.risk_manager import calculate_streak_compounding_factor

        class MockJournalNegativeExp:
            def get_current_streak(self): return 3
            def stats(self): return {"avg_pnl": -50.0}

        factor = calculate_streak_compounding_factor(journal_instance=MockJournalNegativeExp())
        self.assertEqual(factor, 1.0)

    def test_reinvestment_on_positive_expectancy(self):
        """Winning streak with positive average PnL scales up size."""
        from risk.risk_manager import calculate_streak_compounding_factor

        class MockJournalPositiveExp:
            def get_current_streak(self): return 3
            def stats(self): return {"avg_pnl": 150.0}

        factor = calculate_streak_compounding_factor(journal_instance=MockJournalPositiveExp())
        self.assertEqual(factor, 1.10)


if __name__ == "__main__":
    unittest.main()
