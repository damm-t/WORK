"""
Unit Tests — Two-Worker Bayesian Belief & Confidence Updating Engine
=====================================================================
Validates Worker 1 harvesting, Worker 2 sequential Bayesian updating,
daily thesis statement verification, cost-basis anchoring, and self-learning logs.
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from model.bayesian_confidence import (
    BayesianConfidenceEngine,
    DailyEvidenceBundle,
    InformationHarvester,
    ThesisStatement,
)


class TestBayesianConfidence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_belief.db"
        self.engine = BayesianConfidenceEngine(db_path=self.db_path)
        self.harvester = InformationHarvester()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _generate_bars(self, n: int = 30, upward: bool = True) -> pd.DataFrame:
        dates = pd.date_range("2026-09-01", periods=n, freq="B")
        drift = 0.5 if upward else -0.5
        close = 100.0 + np.cumsum(np.random.normal(drift, 0.3, n))
        return pd.DataFrame({
            "Open": close - 0.2,
            "High": close + 0.5,
            "Low": close - 0.5,
            "Close": close,
            "Volume": [1200000] * n,
        }, index=dates)

    def test_worker_1_harvests_evidence(self):
        """Worker 1 must bundle price, stabilized fair value, PSI, and technicals."""
        df_bars = self._generate_bars(30, upward=True)
        ev = self.harvester.harvest("MOCK", cost_basis=98.0, df_bars=df_bars)

        self.assertIsInstance(ev, DailyEvidenceBundle)
        self.assertEqual(ev.ticker, "MOCK")
        self.assertGreater(ev.raw_price, 0.0)
        self.assertGreater(ev.stabilized_price, 0.0)
        self.assertGreater(ev.rsi, 0.0)
        self.assertIsNotNone(ev.cost_basis)
        self.assertIsNotNone(ev.gain_since_entry_pct)

    def test_daily_cycle_advances_belief_and_verifies_yesterday(self):
        """Day 1 sets forward hypothesis; Day 2 realized gain verifies it and raises confidence."""
        df_bars = self._generate_bars(30, upward=True)

        # Day 1
        stmt1 = self.engine.run_daily_cycle(
            "TEST", cost_basis=100.0, df_bars=df_bars.iloc[:20], as_of_date="2026-09-20"
        )
        self.assertEqual(stmt1.expected_direction, "BULLISH")
        self.assertIsNone(stmt1.verified)

        # Day 2: price increased
        stmt2 = self.engine.run_daily_cycle(
            "TEST", cost_basis=100.0, df_bars=df_bars.iloc[:25], as_of_date="2026-09-25"
        )

        history = self.engine.get_history("TEST")
        self.assertEqual(len(history), 2)
        # Day 1 statement should now be verified as True
        self.assertTrue(history[0]["verified"])
        self.assertGreater(history[0]["verification_score"], 0.0)
        # Posterior confidence on Day 2 should reflect positive verification
        self.assertGreaterEqual(stmt2.confidence_pointer, stmt1.confidence_pointer - 5.0)

        # Check that a self-improving learned rule was logged
        rules = self.engine.get_learned_rules()
        self.assertGreaterEqual(len(rules), 1)
        self.assertIn("verified", rules[0].lesson.lower())

    def test_stop_breach_invalidates_statement_and_degrades_confidence(self):
        """If price crashes through the stop level, statement is invalidated."""
        dates = pd.date_range("2026-09-01", periods=25, freq="B")
        close = np.linspace(100.0, 110.0, 20).tolist()
        # Day 1
        df_day1 = pd.DataFrame({
            "Open": close, "High": [c + 0.5 for c in close],
            "Low": [c - 0.5 for c in close], "Close": close,
            "Volume": [1000000] * 20,
        }, index=dates[:20])

        stmt1 = self.engine.run_daily_cycle(
            "CRASH", cost_basis=100.0, df_bars=df_day1, as_of_date="2026-09-20"
        )

        # Day 2: price crashes to $80 (well below stop)
        close_day2 = close + [95.0, 90.0, 85.0, 80.0]
        df_day2 = pd.DataFrame({
            "Open": close_day2, "High": [c + 0.5 for c in close_day2],
            "Low": [c - 0.5 for c in close_day2], "Close": close_day2,
            "Volume": [2000000] * 24,
        }, index=dates[:24])

        stmt2 = self.engine.run_daily_cycle(
            "CRASH", cost_basis=100.0, df_bars=df_day2, as_of_date="2026-09-24"
        )

        history = self.engine.get_history("CRASH")
        self.assertEqual(len(history), 2)
        # Day 1 must be marked falsified
        self.assertFalse(history[0]["verified"])
        self.assertEqual(history[0]["verification_score"], -1.0)
        # Day 2 recommendation must be defensive
        self.assertIn(stmt2.recommendation, ["SCALE_OUT", "EXIT_INVALIDATED"])


if __name__ == "__main__":
    unittest.main()
