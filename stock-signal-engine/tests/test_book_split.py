"""
Unit Tests for 95% Core Book & 5% Momentum Satellite Architecture
==================================================================
Tests:
  1. Default 95/5 capital split ratio resolution.
  2. Asset classification into 'core' vs 'momentum' books.
  3. Budget allocation math, utilization, and ring-fencing.
  4. Ross Cameron bracket order calculation ($50 fixed risk).
  5. Trade journal book segregation (core vs momentum stats).
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from config import get_settings
from execution.ross_execution import execute_ross_bracket_trade
from execution.trade_journal import TradeJournal
from risk.book_allocator import (
    classify_position_book,
    get_book_allocations,
    get_split_ratios,
)


class TestBookSplitArchitecture(unittest.TestCase):
    def test_split_ratios_default(self):
        ratios = get_split_ratios()
        self.assertAlmostEqual(ratios["core_pct"], 0.95, places=2)
        self.assertAlmostEqual(ratios["momentum_pct"], 0.05, places=2)

    def test_classify_position_book(self):
        # Core symbols (large-caps, index proxies, hedges)
        self.assertEqual(classify_position_book("META"), "core")
        self.assertEqual(classify_position_book("MSFT"), "core")
        self.assertEqual(classify_position_book("SH"), "core")
        self.assertEqual(classify_position_book("SPY"), "core")

        # Momentum low-float watchlist runners
        self.assertEqual(classify_position_book("CYN"), "momentum")
        self.assertEqual(classify_position_book("SMFL"), "momentum")
        self.assertEqual(classify_position_book("BBLG"), "momentum")
        self.assertEqual(classify_position_book("HOLO"), "momentum")

    def test_book_allocations_math(self):
        total_equity = 100_000.0
        alloc = get_book_allocations(total_equity=total_equity)

        self.assertEqual(alloc["total_equity"], 100_000.0)
        self.assertEqual(alloc["split_ratio"]["core_pct"], 95.0)
        self.assertEqual(alloc["split_ratio"]["momentum_pct"], 5.0)

        # 95% Core = $95,000
        self.assertEqual(alloc["core"]["budget"], 95_000.0)
        # 5% Momentum = $5,000
        self.assertEqual(alloc["momentum"]["budget"], 5_000.0)
        self.assertGreaterEqual(alloc["momentum"]["available_budget"], 0.0)

    @patch("execution.ross_execution.evaluate_five_pillars")
    def test_ross_bracket_sizing_math(self, mock_pillars):
        mock_pillars.return_value = {
            "grade": "A",
            "score": 90.0,
            "pillars_passed": "5/5",
            "price": 5.80,
        }
        # Test dry-run execution targeting $50 fixed risk
        res = execute_ross_bracket_trade(
            ticker="CYN",
            entry_price=5.80,
            stop_loss=5.59,
            hod_target=6.10,
            max_risk=50.0,
            dry_run=True,
        )

        self.assertEqual(res["status"], "dry_run_approved")
        self.assertEqual(res["ticker"], "CYN")
        self.assertEqual(res["book"], "momentum")
        self.assertEqual(res["shares"], 238)
        self.assertAlmostEqual(res["actual_risk_dollars"], 49.98, places=2)
        self.assertAlmostEqual(res["risk_per_share"], 0.21, places=2)
        self.assertGreaterEqual(res["rr_ratio"], 1.0)

    @patch("execution.ross_execution.evaluate_five_pillars")
    def test_ross_quality_gate_rejects_grade_c(self, mock_pillars):
        mock_pillars.return_value = {
            "grade": "C",
            "score": 25.0,
            "pillars_passed": "2/5",
            "price": 5.12,
        }
        res = execute_ross_bracket_trade(
            ticker="MTC",
            entry_price=5.12,
            stop_loss=4.92,
            hod_target=5.42,
            max_risk=50.0,
            dry_run=True,
        )
        self.assertEqual(res["status"], "rejected")
        self.assertEqual(res["grade"], "C")
        self.assertIn("disqualified", res["message"].lower())

    @patch("execution.ross_execution.evaluate_five_pillars")
    def test_ross_quality_gate_half_sizes_grade_b(self, mock_pillars):
        mock_pillars.return_value = {
            "grade": "B",
            "score": 75.0,
            "pillars_passed": "4/5",
            "price": 5.80,
        }
        res = execute_ross_bracket_trade(
            ticker="CYN",
            entry_price=5.80,
            stop_loss=5.59,
            hod_target=6.10,
            max_risk=50.0,
            dry_run=True,
        )
        self.assertEqual(res["status"], "dry_run_approved")
        # Full sizing was 238; Grade B half-sizing is 119 shares
        self.assertEqual(res["shares"], 119)
        self.assertAlmostEqual(res["actual_risk_dollars"], 24.99, places=2)

    def test_trade_journal_book_segregation(self):
        test_db = TradeJournal()
        # Open Core trade
        c_id = test_db.record_open(
            ticker="TEST_CORE",
            qty=10,
            entry=100.0,
            hedge="SH x10",
            grade="A",
            style="live_ensemble",
            book="core",
        )
        # Open Momentum trade
        m_id = test_db.record_open(
            ticker="TEST_MOM",
            qty=50,
            entry=5.0,
            hedge="",
            grade="A",
            style="ross_momentum",
            book="momentum",
        )

        # Close both
        test_db.record_close("TEST_CORE", exit_price=105.0, reason="test_target", pnl=50.0)
        test_db.record_close("TEST_MOM", exit_price=6.0, reason="test_hod", pnl=50.0)

        core_stats = test_db.stats(book="core")
        mom_stats = test_db.stats(book="momentum")
        all_stats = test_db.stats()

        self.assertIn("total", core_stats)
        self.assertIn("total", mom_stats)
        self.assertGreaterEqual(all_stats["n"], 2)

        # Clean up test rows
        conn = test_db._conn()
        conn.execute("DELETE FROM trades WHERE ticker IN ('TEST_CORE', 'TEST_MOM')")
        conn.commit()
        conn.close()

    def test_reconcile_broker_unfilled_orders(self):
        test_db = TradeJournal()
        tid = test_db.record_open(
            ticker="TEST_UNFILLED",
            qty=100,
            entry=10.0,
            order_id="fake-expired-oid-999",
            book="momentum",
        )
        test_db.close_unfilled_trade(tid, reason="Order Expired (0 Fills)")

        conn = test_db._conn()
        row = conn.execute("SELECT closed_at, exit, pnl, reason FROM trades WHERE id = ?", (tid,)).fetchone()
        conn.execute("DELETE FROM trades WHERE id = ?", (tid,))
        conn.commit()
        conn.close()

        self.assertIsNotNone(row[0])
        self.assertEqual(row[1], 10.0)
        self.assertEqual(row[2], 0.0)
        self.assertEqual(row[3], "Order Expired (0 Fills)")


if __name__ == "__main__":
    unittest.main()
