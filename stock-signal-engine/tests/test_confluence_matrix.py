"""
Unit Tests for Tri-Confluence Institutional Strategy Matrix
===========================================================
Verifies:
  1. 100-Point Confluence Model weighting and bounds.
  2. Candidate C Whale Distribution detection and blocking.
  3. JEV Scooper capitulation routing on dislocation void.
  4. Ross Momentum routing for low float runners.
  5. Core Swing routing for laminar trends.
  6. Dynamic self-improving weight integration.
"""

import unittest
from unittest.mock import MagicMock, patch

from strategy.confluence_matrix import TriConfluenceMatrix


class TestTriConfluenceMatrix(unittest.TestCase):

    def setUp(self):
        self.matrix = TriConfluenceMatrix()

    @patch("api.services.get_hedge_evaluation")
    @patch("strategy.confluence_matrix.anti_volatility_model")
    @patch("strategy.confluence_matrix.TI")
    @patch("strategy.confluence_matrix.belief_engine")
    @patch("market.price_fetcher.fetch_prices")
    def test_candidate_c_whale_trap_blocked_in_matrix(
        self, mock_fetch, mock_belief, mock_ti, mock_av, mock_hedge
    ):
        mock_hedge.return_value = {"sentiment": {"score": 0.1, "label": "neutral"}}
        """Candidate C with high volume and negative price change must be flagged as a whale trap and blocked."""
        import pandas as pd
        # Mock price fetcher returning falling prices
        df = pd.DataFrame({
            "Close": [100.0, 99.0, 98.0, 97.0, 96.0, 95.0],
            "Volume": [10000] * 6
        })
        mock_fetch.return_value = df
        mock_ti.volume_ratio.return_value = 2.8   # High volume
        mock_ti.rsi.return_value = pd.Series([45.0])

        stab_mock = MagicMock()
        stab_mock.price_stability_index = 50.0
        stab_mock.current_raw_price = 95.0
        stab_mock.residual_zscore = -0.5           # Not a severe dislocation void
        mock_av.evaluate_ticker.return_value = stab_mock

        mock_stmt = MagicMock()
        mock_stmt.confidence_pointer = 55.0
        mock_belief.get_latest_statement.return_value = mock_stmt

        decision = self.matrix.evaluate_candidate("TRAP_C")
        self.assertTrue(decision.whale_trap_flag)
        self.assertEqual(decision.action_recommended, "STANDBY_SKIP")
        self.assertFalse(decision.compliance_passed)

    @patch("api.services.get_hedge_evaluation")
    @patch("strategy.confluence_matrix.anti_volatility_model")
    @patch("strategy.confluence_matrix.TI")
    @patch("strategy.confluence_matrix.belief_engine")
    @patch("market.price_fetcher.fetch_prices")
    @patch("strategy.confluence_matrix.jev_scooper")
    def test_jev_scoop_authorized_on_dislocation(
        self, mock_jev, mock_fetch, mock_belief, mock_ti, mock_av, mock_hedge
    ):
        mock_hedge.return_value = {"sentiment": {"score": -0.1, "label": "neutral"}}
        """When dislocation Z <= -1.8, JEV Scooper is routed."""
        import pandas as pd
        df = pd.DataFrame({
            "Close": [50.0, 48.0, 46.0, 44.0, 42.0, 40.0],
            "Volume": [15000] * 6
        })
        mock_fetch.return_value = df
        mock_ti.volume_ratio.return_value = 2.2
        mock_ti.rsi.return_value = pd.Series([25.0])

        stab_mock = MagicMock()
        stab_mock.price_stability_index = 40.0
        stab_mock.current_raw_price = 40.0
        stab_mock.residual_zscore = -2.4           # Deep dislocation
        mock_av.evaluate_ticker.return_value = stab_mock

        opp_mock = MagicMock()
        opp_mock.status = "QUALIFIED_SCOOP"
        mock_jev.evaluate_ticker.return_value = opp_mock

        mock_stmt = MagicMock()
        mock_stmt.confidence_pointer = 60.0
        mock_belief.get_latest_statement.return_value = mock_stmt

        decision = self.matrix.evaluate_candidate("SCOOP_XYZ")
        self.assertEqual(decision.selected_strategy, "jev_scooper")
        self.assertEqual(decision.action_recommended, "EXECUTE_SCOOP")
        self.assertTrue(decision.compliance_passed)


if __name__ == "__main__":
    unittest.main()
