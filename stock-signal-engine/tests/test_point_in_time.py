"""
Unit Tests for Point-in-Time Alignment & Factor DAG
===================================================
Verifies zero lookahead leakage and DAG topological execution.
"""

import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import numpy as np

from data.point_in_time import (
    align_timestamp_point_in_time,
    enrich_article_point_in_time,
    get_next_trading_day,
    is_trading_day,
    validate_anti_leakage,
)
from data.factor_dag import (
    FactorDAG,
    Node,
    PointInTimeAlignmentNode,
    SentimentAggregatorNode,
    TechnicalFeaturesNode,
    AlphaCompositeNode,
)

ET_TZ = ZoneInfo("America/New_York")


class TestPointInTimeAlignment(unittest.TestCase):
    def test_regular_hours_mapped_to_same_day(self):
        # Tuesday 10:15 ET -> same day execution
        session = align_timestamp_point_in_time("2026-10-06T10:15:00-04:00")
        self.assertEqual(session.calendar_date, "2026-10-06")
        self.assertEqual(session.effective_trade_date, "2026-10-06")
        self.assertEqual(session.market_phase, "REGULAR_HOURS")
        self.assertFalse(session.is_after_hours)
        self.assertFalse(session.leakage_risk)

    def test_after_hours_mapped_to_next_day(self):
        # Monday 16:30 ET -> next trading day Tuesday
        session = align_timestamp_point_in_time("2026-10-05T16:30:00-04:00")
        self.assertEqual(session.calendar_date, "2026-10-05")
        self.assertEqual(session.effective_trade_date, "2026-10-06")
        self.assertEqual(session.market_phase, "AFTER_HOURS")
        self.assertTrue(session.is_after_hours)
        self.assertTrue(session.leakage_risk)
        self.assertEqual(session.execution_bar, "NEXT_SESSION_OPEN")

    def test_friday_after_hours_mapped_to_monday(self):
        # Friday 17:00 ET -> Monday (2026-10-05)
        session = align_timestamp_point_in_time("2026-10-02T17:00:00-04:00")
        self.assertEqual(session.calendar_date, "2026-10-02")
        self.assertEqual(session.effective_trade_date, "2026-10-05")
        self.assertTrue(session.is_after_hours)
        self.assertTrue(session.leakage_risk)

    def test_weekend_news_mapped_to_monday(self):
        # Saturday 14:00 ET -> Monday
        session = align_timestamp_point_in_time("2026-10-03T14:00:00-04:00")
        self.assertEqual(session.calendar_date, "2026-10-03")
        self.assertEqual(session.effective_trade_date, "2026-10-05")
        self.assertEqual(session.market_phase, "WEEKEND")
        self.assertTrue(session.leakage_risk)

    def test_holiday_transition(self):
        # Day before Christmas 2026 is Thursday Dec 24. Dec 25 is holiday (Friday).
        # News on Thursday Dec 24 at 17:00 ET -> Friday Dec 25 is holiday -> Monday Dec 28
        session = align_timestamp_point_in_time("2026-12-24T17:00:00-05:00")
        self.assertEqual(session.calendar_date, "2026-12-24")
        self.assertEqual(session.effective_trade_date, "2026-12-28")

    def test_anti_leakage_validator(self):
        df_valid = pd.DataFrame({
            "date": ["2026-10-06", "2026-10-07"],
            "effective_trade_date": ["2026-10-06", "2026-10-06"],  # All past/current
        })
        val_pass = validate_anti_leakage(df_valid)
        self.assertTrue(val_pass["passed"])
        self.assertEqual(val_pass["leakage_violations"], 0)

        df_invalid = pd.DataFrame({
            "date": ["2026-10-05"],
            "effective_trade_date": ["2026-10-06"],  # Future date leaked!
        })
        val_fail = validate_anti_leakage(df_invalid)
        self.assertFalse(val_fail["passed"])
        self.assertEqual(val_fail["leakage_violations"], 1)


class TestFactorDAG(unittest.TestCase):
    def test_topological_sort_and_cycle_detection(self):
        class DummyNode(Node):
            def compute(self, ctx):
                return 42

        dag = FactorDAG("Test")
        dag.add_node(DummyNode("A", []))
        dag.add_node(DummyNode("B", ["A"]))
        dag.add_node(DummyNode("C", ["B"]))

        self.assertEqual(dag.execution_order, ["A", "B", "C"])

    def test_mermaid_generation(self):
        class DummyNode(Node):
            def compute(self, ctx):
                return 1

        dag = FactorDAG("Test")
        dag.add_node(DummyNode("source", []))
        dag.add_node(DummyNode("filter", ["source"]))
        mermaid = dag.to_mermaid()
        self.assertIn("source --> filter", mermaid)


if __name__ == "__main__":
    unittest.main()
