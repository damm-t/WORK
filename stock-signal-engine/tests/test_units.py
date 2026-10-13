"""Regression suite for the refactored engine. Run:
    python -m unittest discover -s tests -v
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from market.technicals import TechnicalIndicators as TI
from risk.cost_model import (round_trip_cost, is_trade_viable,
                             days_to_target, expected_move_pct)
from risk.hedging_engine import calculate_exit_levels, ratchet_trailing_stop
from risk.risk_manager import calculate_compounder_size, check_tail_risk
from risk.trade_scorer import score_trade


def _synthetic_asset(n: int = 220, seed: int = 5, drift: float = 0.0008,
                     vol: float = 0.015, start: float = 150.0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2025-01-02", periods=n)
    close = start * np.exp(np.cumsum(rng.normal(drift, vol, n)))
    return pd.DataFrame({"Open": close, "High": close * 1.008,
                         "Low": close * 0.992, "Close": close,
                         "Volume": 5e6}, index=idx)


class TestTechnicalIndicators(unittest.TestCase):
    def test_flat_series_rsi_is_neutral(self):
        rsi = TI.rsi(pd.Series([100.0] * 60))
        self.assertTrue((rsi == 50.0).all())

    def test_macd_positive_in_deterministic_uptrend(self):
        up = pd.Series(np.linspace(100.0, 200.0, 80))
        line, signal = TI.macd(up)
        self.assertEqual(len(line), len(up))
        self.assertGreater(float(line.iloc[-1]), float(signal.iloc[-1]))

    def test_sma(self):
        s = pd.Series(range(1, 11), dtype=float)
        self.assertEqual(float(TI.sma(s, 10).iloc[-1]), 5.5)

    def test_atr_positive(self):
        atr = TI.atr(_synthetic_asset(60))
        self.assertGreater(float(atr.iloc[-1]), 0.0)

    def test_prior_rolling_high_excludes_current_bar(self):
        rh = TI.prior_rolling_high(pd.Series([10.0, 11.0, 12.0, 13.0]), 2)
        self.assertTrue(pd.isna(rh.iloc[0]))
        self.assertEqual(float(rh.iloc[2]), 11.0)

    def test_volume_ratio_detects_surge(self):
        v = pd.Series([1e6] * 19 + [3e6])
        # mean(1e6 x19 + 3e6) / 20 = 1.1e6 -> ratio = 3e6 / 1.1e6
        self.assertAlmostEqual(TI.volume_ratio(v), 2.727272727, places=5)


class TestCostModel(unittest.TestCase):
    def test_round_trip_cost_bounded(self):
        cost = round_trip_cost(210.0, 48)
        self.assertLessEqual(0.10, cost["pct_of_notional"])
        self.assertLessEqual(cost["pct_of_notional"], 0.20)

    def test_viability_gate(self):
        self.assertTrue(is_trade_viable(100, 104, 97, 100)["viable"])
        self.assertFalse(is_trade_viable(100, 100.2, 99, 100)["viable"])

    def test_days_to_target_sqrt_scaling(self):
        self.assertEqual(days_to_target(100, 101, 1.0), 1.0)
        self.assertEqual(days_to_target(100, 102, 1.0), 4.0)
        self.assertAlmostEqual(expected_move_pct(1.0, 100, 5), 2.236, places=3)


class TestExitEngine(unittest.TestCase):
    def test_ladder_geometry(self):
        lv = calculate_exit_levels(100, 2)
        for key, want in [("hard_stop_price", 97.0),
                          ("take_profit_1_price", 104.0),
                          ("take_profit_2_trigger", 107.0)]:
            self.assertEqual(lv[key], want)
        self.assertIn("tp1_days_median", lv)
        self.assertIn("expected_move_5d_pct", lv)

    def test_ladder_geometry_env_override(self):
        import os
        from risk.hedging_engine import get_exit_geometry
        os.environ["STOP_ATR_MULT"] = "2.0"
        try:
            lv = calculate_exit_levels(100, 2)
            self.assertEqual(lv["hard_stop_price"], 96.0)
            self.assertEqual(get_exit_geometry()["stop_mult"], 2.0)
        finally:
            del os.environ["STOP_ATR_MULT"]
        self.assertEqual(calculate_exit_levels(100, 2)["hard_stop_price"], 97.0)

    def test_nvda_ban_helpers(self):
        from risk.hedging_engine import banned_ticker, without_banned
        self.assertTrue(banned_ticker("nvda"))
        self.assertFalse(banned_ticker("MSFT"))
        self.assertEqual(without_banned(["NVDA", "MSFT", "AAPL"]),
                         ["MSFT", "AAPL"])


class TestTp1Automation(unittest.TestCase):
    def test_scale_out_plan_at_and_above_tp1(self):
        from risk.hedging_engine import tp1_scale_plan
        # entry 100, ATR 2 -> TP1 = 104 (tp1_mult 2.0), scale 50% of 10 = 5
        plan = tp1_scale_plan(104.0, 100.0, 2.0, 10)
        self.assertEqual(plan["action"], "scale_out")
        self.assertEqual(plan["sell_qty"], 5)
        self.assertEqual(plan["tp1_price"], 104.0)

    def test_hold_below_tp1(self):
        from risk.hedging_engine import tp1_scale_plan
        plan = tp1_scale_plan(103.0, 100.0, 2.0, 10)
        self.assertEqual(plan["action"], "hold")
        self.assertEqual(plan["sell_qty"], 0)

    def test_whole_share_floor_keeps_runner(self):
        from risk.hedging_engine import tp1_scale_plan
        # 3 shares x 50% = 1.5 -> floor 1, runner keeps 2
        plan = tp1_scale_plan(104.0, 100.0, 2.0, 3)
        self.assertEqual(plan["action"], "scale_out")
        self.assertEqual(plan["sell_qty"], 1)

    def test_tiny_position_not_scalable(self):
        from risk.hedging_engine import tp1_scale_plan
        # 1 share: scale-out would leave 0 runner -> hold
        plan = tp1_scale_plan(104.0, 100.0, 2.0, 1)
        self.assertEqual(plan["action"], "hold")

    def test_trail_arms_after_tp1_when_env_set(self):
        import os
        from risk.hedging_engine import ratchet_trailing_stop
        os.environ["STOP_ATR_MULT"] = "2.0"          # tuned profile
        os.environ["TRAIL_ARM_ATR_MULT"] = "2.0"
        try:
            # entry 100, ATR 2 -> arm at 104; highest 105 arms trail at 102
            r = ratchet_trailing_stop(100, 2, 105)
            self.assertTrue(r["trailing_armed"])
            self.assertEqual(r["stop_price"], 102.0)
            # below arm trigger -> not armed, hard stop floor (2 ATR)
            r0 = ratchet_trailing_stop(100, 2, 103)
            self.assertFalse(r0["trailing_armed"])
            self.assertEqual(r0["stop_price"], 96.0)
        finally:
            del os.environ["STOP_ATR_MULT"]
            del os.environ["TRAIL_ARM_ATR_MULT"]

    def test_record_partial_inserts_closed_clip(self):
        import execution.trade_journal as tj
        with tempfile.TemporaryDirectory() as tmp:
            tj.DB_PATH = Path(tmp) / "jp.db"
            j = tj.TradeJournal(tj.DB_PATH)
            j.record_open("MSFT", 10, 100, grade="A")
            j.record_partial("MSFT", 104.0, 5, pnl=20.0,
                             reason="tp1_scale_out")
            conn_rows = j._conn().execute(
                """SELECT closed_at, pnl FROM trades
                   WHERE reason='tp1_scale_out'""").fetchall()
            self.assertEqual(len(conn_rows), 1)
            self.assertIsNotNone(conn_rows[0][0])
            self.assertEqual(conn_rows[0][1], 20.0)
            # runner row still open
            open_n = j._conn().execute(
                "SELECT COUNT(*) FROM trades WHERE closed_at IS NULL"
            ).fetchone()[0]
            self.assertEqual(open_n, 1)
            j.record_close("MSFT", 106.0, "stop")
            self.assertEqual(j.stats()["n"], 2)

    def test_ratchet_never_moves_down(self):
        r1 = ratchet_trailing_stop(100, 2, 105)
        self.assertFalse(r1["trailing_armed"])
        r2 = ratchet_trailing_stop(100, 2, 110)
        self.assertTrue(r2["trailing_armed"] and r2["stop_price"] == 107.0)
        r3 = ratchet_trailing_stop(100, 2, 108, current_stop_price=107.5)
        self.assertEqual(r3["stop_price"], 107.5)


class TestScorer(unittest.TestCase):
    BULL_MARKET = {"Close": 105, "BB_Middle": 100, "MACD_Histogram": 0.5,
                   "RSI": 55, "ATR": 2.5}
    BEAR_MARKET = {"Close": 95, "BB_Middle": 100, "MACD_Histogram": -0.5,
                   "RSI": 75, "ATR": 12}

    def test_grade_a_for_clean_setup(self):
        g = score_trade({"label": "positive", "score": 0.9}, self.BULL_MARKET,
                        {"regime": "BULL_MOMENTUM"})
        self.assertEqual(g["grade"], "A")
        self.assertEqual(g["size_multiplier"], 1.0)

    def test_grade_c_for_dirty_setup(self):
        g = score_trade({"label": "negative", "score": 0.9}, self.BEAR_MARKET,
                        {"regime": "BEAR_VOLATILITY"})
        self.assertEqual(g["grade"], "C")
        self.assertEqual(g["score"], 0.0)

    def test_grade_for_high_vol_dip_setup(self):
        dip_market = {
            "Close": 95, "BB_Middle": 100, "MACD_Histogram": -0.05,
            "RSI": 42, "ATR": 2.5, "Volume_Ratio": 1.5, "Off_Hi20_Pct": -5.0
        }
        g = score_trade({"label": "positive", "score": 0.8}, dip_market,
                        {"regime": "BULL_MOMENTUM"})
        self.assertIn(g["grade"], ["A", "B"])
        self.assertGreaterEqual(g["score"], 55.0)
        self.assertTrue(any("high-vol dip" in c for c in g["checks"]))


class TestRiskManager(unittest.TestCase):
    def test_kelly_capped_by_max_risk(self):
        s = calculate_compounder_size(10_000, 100, 1.0, atr=2.0)
        self.assertEqual(s["shares"], 50)
        self.assertLessEqual(s["risk_pct_used"], 0.02)

    def test_tail_risk_cap(self):
        self.assertFalse(check_tail_risk(15_000, 10_000)["approved"])
        self.assertTrue(check_tail_risk(5_000, 10_000)["approved"])


class TestNewsMemory(unittest.TestCase):
    def test_remember_and_similar(self):
        import nlp.news_memory as nm
        with tempfile.TemporaryDirectory() as tmp:
            nm.DB_PATH = Path(tmp) / "test.db"
            nm.remember("NVDA",
                        "NVIDIA beats earnings expectations on data center demand",
                        "positive", 0.94)
            nm.remember("META", "Meta faces regulatory probe over privacy",
                        "negative", 0.81)
            hits = nm.similar("chip company beats earnings on AI demand", top_k=1)
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["ticker"], "NVDA")
            self.assertGreater(hits[0]["similarity"], 0.3)
            self.assertEqual(nm.stats()["total"], 2)


class TestSimulatorSmoke(unittest.TestCase):
    def test_both_styles_produce_curves(self):
        from backtest.hedging_backtester import simulate
        rng = np.random.default_rng(9)
        n = 220
        idx = pd.bdate_range("2025-06-02", periods=n)
        close = 120 * np.exp(np.cumsum(rng.normal(0.0007, 0.014, n)))
        df_a = pd.DataFrame({"Open": close, "High": close * 1.008,
                             "Low": close * 0.992, "Close": close,
                             "Volume": np.full(n, 5e6)}, index=idx)
        df_b = pd.DataFrame({"Close": np.full(n, 400.0)}, index=idx)
        df_h = pd.DataFrame({"Close": np.full(n, 40.0)}, index=idx)

        for style in ("conservative", "bold"):
            curve, trades = simulate(df_a, df_b, df_h, 100.0, hedged=True,
                                     fractional=True, style=style)
            self.assertGreater(len(curve), 180)
            self.assertGreater(float(curve.iloc[0]), 0.0)
            self.assertIsInstance(trades, list)


class TestShockDetector(unittest.TestCase):
    def _intra(self, closes):
        idx = pd.date_range("2026-08-26 09:30", periods=len(closes), freq="5min")
        return pd.DataFrame({"Close": closes, "Volume": 1e6}, index=idx)

    def test_downward_velocity_shock_detected(self):
        from market.shock_detector import detect_intraday_shock
        closes = [100.0] * 20 + [99.0, 98.4, 97.8, 97.0]     # -3% in 20 min
        res = detect_intraday_shock("TEST", df_intraday=self._intra(closes),
                                    prev_close=100.0)
        self.assertTrue(res["shocked"])
        self.assertEqual(res["direction"], "down")

    def test_calm_tape_not_flagged(self):
        from market.shock_detector import detect_intraday_shock
        closes = [100 + 0.01 * i for i in range(24)]          # gentle drift
        res = detect_intraday_shock("TEST", df_intraday=self._intra(closes),
                                    prev_close=99.0)
        self.assertFalse(res["shocked"])

    def test_gap_shock_vs_prev_close(self):
        from market.shock_detector import detect_intraday_shock
        res = detect_intraday_shock("TEST", df_intraday=self._intra([103.0] * 10),
                                    prev_close=100.0)          # +3% overnight gap
        self.assertTrue(res["shocked"])


class TestJournalV2(unittest.TestCase):
    def test_context_analytics_and_suggestions(self):
        import execution.trade_journal as tj
        with tempfile.TemporaryDirectory() as tmp:
            tj.DB_PATH = Path(tmp) / "j.db"
            j = tj.TradeJournal(tj.DB_PATH)

            for _ in range(3):                       # grade A: clean winners
                j.record_open("NVDA", 10, 100, grade="A", score=80,
                              regime="BULL_MOMENTUM")
                j.record_close("NVDA", 106, "stop")
            for _ in range(6):                       # grade B: bleeders
                j.record_open("META", 10, 300, grade="B", score=60)
                j.record_close("META", 297, "stop")

            a = j.analytics()
            self.assertEqual(a["by_grade"]["A"]["n"], 3)
            self.assertEqual(a["by_grade"]["A"]["win_rate"], 100.0)
            self.assertEqual(a["by_grade"]["B"]["n"], 6)
            self.assertTrue(any("Grade B" in s for s in a["suggestions"]),
                            a["suggestions"])
            self.assertIn("overall", a)

            st = j.stats()
            self.assertEqual(st["open_trades"], 0)


class TestJournalV3(unittest.TestCase):
    def test_fill_capture_slippage_and_equity_curve(self):
        import execution.trade_journal as tj
        with tempfile.TemporaryDirectory() as tmp:
            tj.DB_PATH = Path(tmp) / "j.db"
            j = tj.TradeJournal(tj.DB_PATH)

            rid = j.record_open("NVDA", 10, 100.0, grade="A", score=85,
                                order_id="oid-1")
            pend = j.pending_fills()
            self.assertEqual(len(pend), 1)
            self.assertEqual(pend[0]["order_id"], "oid-1")

            j.set_actual_entry(rid, 100.5)               # +0.5% => 50 bps
            self.assertEqual(j.pending_fills(), [])

            j.record_close("NVDA", 105.0, "stop")
            a = j.analytics()
            self.assertEqual(a["avg_slippage_bps"], 50.0)

            curve = j.equity_curve()
            self.assertEqual(len(curve), 1)
            self.assertAlmostEqual(curve[0]["cum_pnl"],
                                   (105.0 - 100.5) * 10, places=1)

    def test_equity_curve_empty_state(self):
        import execution.trade_journal as tj
        with tempfile.TemporaryDirectory() as tmp:
            tj.DB_PATH = Path(tmp) / "empty.db"
            j = tj.TradeJournal(tj.DB_PATH)
            self.assertEqual(j.equity_curve(), [])

    def test_get_exits_ledger(self):
        import execution.trade_journal as tj
        with tempfile.TemporaryDirectory() as tmp:
            tj.DB_PATH = Path(tmp) / "exits.db"
            j = tj.TradeJournal(tj.DB_PATH)

            j.record_open("AAPL", 50, 300.0, grade="A", score=75)
            # TP1 partial scale-out
            j.record_partial("AAPL", 310.0, 25, pnl=250.0, reason="tp1_scale_out")
            # Final runner close
            j.record_close("AAPL", 320.0, "trailing_stop", pnl=500.0)

            exits = j.get_exits()
            self.assertEqual(len(exits), 2)
            self.assertTrue(all(x["ticker"] == "AAPL" for x in exits))
            types = {x["type"] for x in exits}
            self.assertEqual(types, {"FULL EXIT", "PARTIAL TP1"})
            partial = next(x for x in exits if x["type"] == "PARTIAL TP1")
            self.assertEqual(partial["pnl"], 250.0)
            self.assertEqual(partial["qty"], 25.0)
            full = next(x for x in exits if x["type"] == "FULL EXIT")
            self.assertEqual(full["pnl"], 500.0)


class TestExitAdvisor(unittest.TestCase):
    MKT = {"Close": 105.0, "ATR": 2.0, "BB_Middle": 100.0}

    def test_in_profit_zone(self):
        from risk.exit_advisor import analyze_exit
        r = analyze_exit("TEST", 103.0, market=self.MKT)   # +1.0 ATR
        self.assertEqual(r["status"], "IN_PROFIT")
        # ladder anchors at USER entry: 103 −1.5×ATR(2) = 100
        self.assertEqual(r["ladder"]["hard_stop_price"], 100.0)
        self.assertEqual(r["good_exits"]["tp1_scale_out_50pct"], 107.0)
        self.assertEqual(r["dist_in_atr"], 1.0)

    def test_stop_zone_detected(self):
        from risk.exit_advisor import analyze_exit
        r = analyze_exit("TEST", 110.0, market=self.MKT)   # −2.5 ATR
        self.assertEqual(r["status"], "STOP_ZONE")

    def test_runner_zone_detected(self):
        from risk.exit_advisor import analyze_exit
        r = analyze_exit("TEST", 98.0, market=self.MKT)    # +3.5 ATR
        self.assertEqual(r["status"], "RUNNER")

    def test_bad_input(self):
        from risk.exit_advisor import analyze_exit
        r = analyze_exit("TEST", -5, market=self.MKT)
        self.assertIn("error", r)

    def test_structured_recommendation(self):
        from risk.exit_advisor import analyze_exit
        r = analyze_exit("TEST", 103.0, market=self.MKT)
        self.assertIn("recommendation", r)
        rec = r["recommendation"]
        self.assertIn("indicator", rec)
        self.assertIn("why", rec)
        self.assertIn("action", rec)
        self.assertIn("[ Indicator ]", rec["paragraph"])
        self.assertIn("[ Why ]", rec["paragraph"])
        self.assertIn("[ What Action ]", rec["paragraph"])


class TestArticleSelection(unittest.TestCase):
    """nlp.pick_best_article must rank by DIRECTION, not raw confidence.

    Regression: FinBERT confidence runs high (0.7-0.95) for both bullish and
    bearish headlines, so raw-score max() let one strongly negative headline
    hijack the signal and force HOLD ("No signal") on viable candidates.
    """

    def test_positive_beats_higher_confidence_negative(self):
        from nlp import pick_best_article
        arts = [{"title": "bull", "sentiment": "positive",
                 "sentiment_score": 0.71},
                {"title": "bear", "sentiment": "negative",
                 "sentiment_score": 0.95}]
        self.assertEqual(pick_best_article(arts)["title"], "bull")

    def test_least_severe_bear_ranks_best_when_all_negative(self):
        # All-negative set: signed ranking picks the bear CLOSEST to
        # positive (mildest) — the most favorable info available; the
        # negative directional value still forces HOLD downstream.
        from nlp import pick_best_article
        arts = [{"title": "mild", "sentiment": "negative",
                 "sentiment_score": 0.60},
                {"title": "severe", "sentiment": "negative",
                 "sentiment_score": 0.95}]
        self.assertEqual(pick_best_article(arts)["title"], "mild")

    def test_all_neutral_falls_back_to_highest_confidence(self):
        from nlp import pick_best_article
        arts = [{"title": "weak", "sentiment": "neutral",
                 "sentiment_score": 0.60},
                {"title": "strong", "sentiment": "neutral",
                 "sentiment_score": 0.93}]
        self.assertEqual(pick_best_article(arts)["title"], "strong")

    def test_directional_sentiment_signs(self):
        from nlp import directional_sentiment
        self.assertAlmostEqual(directional_sentiment(
            {"sentiment": "positive", "sentiment_score": 0.8}), 0.8)
        self.assertAlmostEqual(directional_sentiment(
            {"sentiment": "negative", "sentiment_score": 0.8}), -0.8)
        self.assertAlmostEqual(directional_sentiment(
            {"sentiment": "neutral", "sentiment_score": 0.9}), 0.0)


class TestPurchaseLogger(unittest.TestCase):
    def test_format_and_log_purchase(self):
        import tempfile
        from pathlib import Path
        import execution.purchase_logger as pl
        import execution.trade_journal as tj

        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            pl.PURCHASE_LOG_FILE = tmp_p / "purchases.log"
            pl.PURCHASE_JSONL_FILE = tmp_p / "purchases.jsonl"
            tj.DB_PATH = tmp_p / "test_trades.db"
            tj.journal = tj.TradeJournal(tj.DB_PATH)

            entry = pl.log_purchase(
                ticker="TEST",
                qty=10,
                price=100.0,
                order_id="test-order-123",
                name="Test Corp",
                sector="Technology",
                score=75.0,
                grade="A",
                rank=1,
                universe_size=28,
                portfolio_equity=50000.0,
                decision={
                    "approved": True,
                    "shares": 10,
                    "stop_loss_price": 95.0,
                    "exit_levels": {
                        "stop_loss": 95.0,
                        "conservative_exit": 103.0,
                        "take_profit_1": 106.0,
                        "runner": 110.0,
                    },
                },
                market={"Close": 100.0, "ATR": 3.0, "RSI": 58.0, "SMA50": 98.0},
                sentiment={"label": "POSITIVE", "score": 0.90, "headlines": ["Test catalyst headline"]},
            )

            self.assertEqual(entry["ticker"], "TEST")
            self.assertEqual(entry["notional"], 1000.0)
            self.assertEqual(entry["portfolio_pct"], 2.0)
            self.assertTrue(pl.PURCHASE_LOG_FILE.exists())
            self.assertTrue(pl.PURCHASE_JSONL_FILE.exists())

            # Verify formatted log text contains all 5 sections
            log_text = pl.PURCHASE_LOG_FILE.read_text()
            self.assertIn("[STOCK PURCHASE EXECUTION]", log_text)
            self.assertIn("Ticker: TEST", log_text)
            self.assertIn("Order ID: test-order-123", log_text)
            self.assertIn("WHY WAS THIS STOCK PURCHASED?", log_text)
            self.assertIn("[1] Market Leaderboard", log_text)
            self.assertIn("[2] Model Signal", log_text)
            self.assertIn("[3] Sentiment Analysis", log_text)
            self.assertIn("[4] Safety Gates", log_text)
            self.assertIn("[5] Exit Roadmap", log_text)

            # Verify retrieval
            logs = pl.get_purchase_logs(limit=10)
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]["ticker"], "TEST")
            self.assertEqual(logs[0]["order_id"], "test-order-123")


class TestAlpacaNews(unittest.TestCase):
    def test_normalize_alpaca_dict(self):
        from ingestion.news_fetcher import _normalize_alpaca
        raw_dict = {
            "headline": "Tech giant announces record revenue",
            "summary": "Full summary of earnings beat.",
            "created_at": "2026-09-06T10:00:00Z",
            "url": "https://example.com/news/123",
            "source": "benzinga",
            "author": "Jane Doe",
        }
        item = _normalize_alpaca(raw_dict, "AAPL")
        self.assertEqual(item["ticker"], "AAPL")
        self.assertEqual(item["title"], "Tech giant announces record revenue")
        self.assertEqual(item["body"], "Full summary of earnings beat.")
        self.assertEqual(item["source"], "alpaca_benzinga")
        self.assertEqual(item["url"], "https://example.com/news/123")
        self.assertEqual(item["author"], "Jane Doe")
        self.assertEqual(item["published_at"], "2026-09-06T10:00:00Z")

    def test_normalize_alpaca_object(self):
        from ingestion.news_fetcher import _normalize_alpaca
        from types import SimpleNamespace
        raw_obj = SimpleNamespace(
            headline="Semiconductor demand accelerates",
            summary="Strong quarter reported.",
            created_at=None,
            updated_at="2026-09-06T09:00:00+00:00",
            url="https://example.com/news/456",
            source="benzinga",
            author="John Smith",
        )
        item = _normalize_alpaca(raw_obj, "NVDA")
        self.assertEqual(item["ticker"], "NVDA")
        self.assertEqual(item["title"], "Semiconductor demand accelerates")
        self.assertEqual(item["source"], "alpaca_benzinga")
        self.assertEqual(item["published_at"], "2026-09-06T09:00:00+00:00")


class TestTimeDecay(unittest.TestCase):
    def test_half_life_math(self):
        from datetime import datetime, timezone, timedelta
        from nlp import compute_time_decay

        now = datetime.now(timezone.utc)

        # 0 hours old -> decay_weight == 1.0
        age_0, w_0 = compute_time_decay(now.isoformat(), half_life_hours=18.0)
        self.assertAlmostEqual(w_0, 1.0, places=2)

        # 18 hours old (1 half-life) -> decay_weight == 0.50
        t_18 = (now - timedelta(hours=18)).isoformat()
        age_18, w_18 = compute_time_decay(t_18, half_life_hours=18.0)
        self.assertAlmostEqual(w_18, 0.50, places=2)

        # 36 hours old (2 half-lives) -> decay_weight == 0.25
        t_36 = (now - timedelta(hours=36)).isoformat()
        age_36, w_36 = compute_time_decay(t_36, half_life_hours=18.0)
        self.assertAlmostEqual(w_36, 0.25, places=2)

    def test_pick_best_article_prefers_fresh_news(self):
        from nlp import pick_best_article

        # Stale article: high raw score (0.95), but 72 hours old (decayed ~0.059)
        stale_article = {
            "title": "Old Massive Earnings Beat",
            "sentiment": "positive",
            "sentiment_score": 0.059,
            "raw_sentiment_score": 0.95,
            "decayed_sentiment_score": 0.059,
            "decay_weight": 0.0625,
            "age_hours": 72.0,
        }

        # Fresh article: moderate raw score (0.75), but 1 hour old (decayed ~0.72)
        fresh_article = {
            "title": "Fresh Product Upgrade Announced",
            "sentiment": "positive",
            "sentiment_score": 0.72,
            "raw_sentiment_score": 0.75,
            "decayed_sentiment_score": 0.72,
            "decay_weight": 0.96,
            "age_hours": 1.0,
        }

        best = pick_best_article([stale_article, fresh_article], use_decay=True)
        self.assertEqual(best["title"], "Fresh Product Upgrade Announced")

    def test_directional_ranking(self):
        from nlp import pick_best_article

        positive_article = {
            "title": "Expansion Announced",
            "sentiment": "positive",
            "sentiment_score": 0.60,
            "decayed_sentiment_score": 0.60,
            "raw_sentiment_score": 0.60,
        }
        negative_article = {
            "title": "Lawsuit Filed",
            "sentiment": "negative",
            "sentiment_score": 0.85,
            "decayed_sentiment_score": 0.85,
            "raw_sentiment_score": 0.85,
        }

        best = pick_best_article([negative_article, positive_article], use_decay=True)
        self.assertEqual(best["title"], "Expansion Announced")


class TestTwitterSuppression(unittest.TestCase):
    def test_dummy_token_returns_empty_without_error(self):
        from ingestion.twitter_fetcher import fetch_tweets
        tweets = fetch_tweets("AAPL")
        self.assertEqual(tweets, [])


class TestFundamentals(unittest.TestCase):
    def test_evaluate_profitable_healthy(self):
        from unittest.mock import patch
        from market.fundamentals import evaluate_fundamental_quality

        mock_metrics = {
            "ticker": "GOOD",
            "revenue": 100_000_000,
            "net_income": 25_000_000,
            "eps": 3.50,
            "assets": 200_000_000,
            "liabilities": 50_000_000,
            "equity": 150_000_000,
            "profit_margin_pct": 25.0,
            "debt_to_equity": 0.33,
            "roe_pct": 16.7,
            "is_profitable": True,
        }

        with patch("market.fundamentals.fetch_fundamentals", return_value=mock_metrics):
            res = evaluate_fundamental_quality("GOOD", sector="Technology")
            self.assertTrue(res["passed"])
            self.assertEqual(res["quality_score"], 15.0)  # +8 profit +4 D/E +3 margin
            self.assertTrue(any("Profitable" in r for r in res["reasons"]))
            self.assertTrue(any("Healthy D/E" in r for r in res["reasons"]))
            self.assertTrue(any("High Margin" in r for r in res["reasons"]))

    def test_unprofitable_company_penalized(self):
        from unittest.mock import patch
        from market.fundamentals import evaluate_fundamental_quality

        mock_metrics = {
            "ticker": "BAD",
            "revenue": 50_000_000,
            "net_income": -10_000_000,
            "eps": -0.85,
            "assets": 80_000_000,
            "liabilities": 60_000_000,
            "equity": 20_000_000,
            "profit_margin_pct": -20.0,
            "debt_to_equity": 3.0,
            "roe_pct": -50.0,
            "is_profitable": False,
        }

        with patch("market.fundamentals.fetch_fundamentals", return_value=mock_metrics):
            res = evaluate_fundamental_quality("BAD", sector="Technology")
            self.assertFalse(res["passed"])
            self.assertLessEqual(res["quality_score"], -10.0)
            self.assertTrue(any("UNPROFITABLE" in r for r in res["reasons"]))

    def test_overleveraged_nonfinancial_rejected(self):
        from unittest.mock import patch
        from market.fundamentals import evaluate_fundamental_quality

        mock_metrics = {
            "ticker": "DEBT",
            "revenue": 100_000_000,
            "net_income": 5_000_000,
            "eps": 1.20,
            "assets": 500_000_000,
            "liabilities": 450_000_000,
            "equity": 50_000_000,
            "profit_margin_pct": 5.0,
            "debt_to_equity": 9.0,
            "roe_pct": 10.0,
            "is_profitable": True,
        }

        with patch("market.fundamentals.fetch_fundamentals", return_value=mock_metrics):
            res = evaluate_fundamental_quality("DEBT", sector="Industrials", max_debt_to_equity=3.5)
            self.assertFalse(res["passed"])
            self.assertTrue(any("OVERLEVERAGED" in r for r in res["reasons"]))

    def test_financial_sector_structural_leverage_allowed(self):
        from unittest.mock import patch
        from market.fundamentals import evaluate_fundamental_quality

        # Bank with 12x D/E (typical customer deposits) and 14% ROE
        mock_metrics = {
            "ticker": "BANK",
            "revenue": 100_000_000,
            "net_income": 20_000_000,
            "eps": 5.0,
            "assets": 1_000_000_000,
            "liabilities": 920_000_000,
            "equity": 80_000_000,
            "profit_margin_pct": 20.0,
            "debt_to_equity": 11.5,
            "roe_pct": 25.0,
            "is_profitable": True,
        }

        with patch("market.fundamentals.fetch_fundamentals", return_value=mock_metrics):
            res = evaluate_fundamental_quality("BANK", sector="Financials", max_debt_to_equity=3.5)
            self.assertTrue(res["passed"])
            self.assertEqual(res["quality_score"], 15.0)  # +8 profit, +4 capital efficient financial, +3 margin
            self.assertTrue(any("Capital efficient" in r for r in res["reasons"]))


class TestScannerQualityGate(unittest.TestCase):
    def test_sector_diversification_cap(self):
        # 3 Tech stocks and 1 Healthcare stock
        rows = [
            {"ticker": "TECH1", "sector": "Technology", "score": 90.0, "passed_quality": True},
            {"ticker": "TECH2", "sector": "Technology", "score": 88.0, "passed_quality": True},
            {"ticker": "TECH3", "sector": "Technology", "score": 85.0, "passed_quality": True},
            {"ticker": "HEALTH1", "sector": "Healthcare", "score": 80.0, "passed_quality": True},
        ]

        top_picks = []
        other_picks = []
        sector_counts = {}
        sector_cap = 2
        top_n = 3

        for r in rows:
            sec = r["sector"]
            if sector_counts.get(sec, 0) < sector_cap and len(top_picks) < top_n:
                top_picks.append(r)
                sector_counts[sec] = sector_counts.get(sec, 0) + 1
            else:
                other_picks.append(r)

        self.assertEqual(len(top_picks), 3)
        # Verify tech is capped at 2
        tech_picks = [p for p in top_picks if p["sector"] == "Technology"]
        self.assertEqual(len(tech_picks), 2)
        # Third pick must be Healthcare
        self.assertEqual(top_picks[2]["ticker"], "HEALTH1")

    def test_junk_filtering_prioritizes_quality(self):
        rows = [
            {"ticker": "JUNK_MOMENTUM", "sector": "Technology", "score": 85.0, "passed_quality": False},
            {"ticker": "QUALITY_LEADER", "sector": "Technology", "score": 75.0, "passed_quality": True},
        ]

        # With filter_junk=True
        top_picks = []
        other_picks = []
        for r in rows:
            if not r["passed_quality"]:
                other_picks.append(r)
                continue
            top_picks.append(r)

        ranked = top_picks + other_picks
        self.assertEqual(ranked[0]["ticker"], "QUALITY_LEADER")
        self.assertEqual(ranked[1]["ticker"], "JUNK_MOMENTUM")


class TestTripleBarrier(unittest.TestCase):
    def test_upper_barrier_hit_produces_buy_label(self):
        from data.dataset_generator import generate_triple_barrier_labels
        prices = np.linspace(100.0, 120.0, 20)
        df = pd.DataFrame({
            "Open": prices,
            "High": prices + 0.5,
            "Low": prices - 0.5,
            "Close": prices,
            "ATR": [2.0] * 20,
        })
        labels = generate_triple_barrier_labels(df, tp_atr=2.0, sl_atr=1.5, horizon=5)
        # First bar enters at 100, upper barrier 104 reached in ~4 bars, lower barrier 97 never touched
        self.assertEqual(labels[0], 1)

    def test_lower_barrier_hit_produces_hold_label(self):
        from data.dataset_generator import generate_triple_barrier_labels
        prices = np.linspace(100.0, 80.0, 20)
        df = pd.DataFrame({
            "Open": prices,
            "High": prices + 0.5,
            "Low": prices - 0.5,
            "Close": prices,
            "ATR": [2.0] * 20,
        })
        labels = generate_triple_barrier_labels(df, tp_atr=2.0, sl_atr=1.5, horizon=5)
        # Lower barrier 97 reached in ~3 bars
        self.assertEqual(labels[0], 0)

    def test_boundary_bars_unlabeled(self):
        from data.dataset_generator import generate_triple_barrier_labels
        df = pd.DataFrame({
            "Open": [100.0] * 10,
            "High": [101.0] * 10,
            "Low": [99.0] * 10,
            "Close": [100.0] * 10,
            "ATR": [2.0] * 10,
        })
        labels = generate_triple_barrier_labels(df, horizon=5)
        # Last 5 bars must be unlabeled (-1)
        self.assertTrue((labels[-5:] == -1).all())


class TestDatasetGenerator(unittest.TestCase):
    def test_feature_columns_match_predictor(self):
        from data.dataset_generator import FEATURE_COLS as GEN_COLS
        from model.predictor import FEATURE_COLS as PRED_COLS
        from model.trainer import FEATURE_COLS as TRAIN_COLS

        self.assertEqual(GEN_COLS, PRED_COLS)
        self.assertEqual(GEN_COLS, TRAIN_COLS)

    def test_generated_dataset_integrity(self):
        from pathlib import Path
        csv_path = Path("data/training_features.csv")
        self.assertTrue(csv_path.exists())
        df = pd.read_csv(csv_path)
        self.assertGreater(len(df), 5000)
        for col in ["sentiment_positive", "sentiment_negative", "sentiment_neutral",
                    "sentiment_score", "rsi", "macd", "bb_upper", "bb_lower",
                    "atr", "bb_width", "rsi_overbought", "rsi_oversold", "signal"]:
            self.assertIn(col, df.columns)
            self.assertEqual(df[col].isna().sum(), 0)
        # Binary target
        self.assertTrue(set(df["signal"].unique()).issubset({0, 1}))


class TestRossMomentumStrategy(unittest.TestCase):
    def test_five_pillars_grade_a(self):
        from market.low_float_scanner import evaluate_five_pillars
        import pandas as pd
        import numpy as np

        # Construct synthetic stock: up +25%, RVOL 6x, price $7.50
        dates = pd.bdate_range("2026-01-01", periods=60)
        closes = [6.0] * 58 + [6.0, 7.50]  # +25% on last day
        vols = [100_000] * 59 + [750_000]   # 7.5x RVOL
        df = pd.DataFrame({
            "Open": closes, "High": [c * 1.02 for c in closes],
            "Low": [c * 0.98 for c in closes], "Close": closes,
            "Volume": vols
        }, index=dates)

        res_no_news = evaluate_five_pillars("TEST", custom_df=df, custom_float=8_000_000)
        self.assertGreaterEqual(res_no_news["score"], 65.0)
        self.assertEqual(res_no_news["grade"], "B")  # 4/5 pillars (no news = Grade B half size)
        self.assertTrue(res_no_news["pillars"]["p1_up_10pct"])
        self.assertTrue(res_no_news["pillars"]["p2_rvol_5x"])
        self.assertTrue(res_no_news["pillars"]["p4_price_2_20"])
        self.assertTrue(res_no_news["pillars"]["p5_low_float_20m"])

        # With news catalyst mocked
        from unittest.mock import patch
        with patch("market.low_float_scanner.evaluate_news_catalyst", return_value={"has_catalyst": True, "headline": "FDA Fast-Track Approved"}):
            res_news = evaluate_five_pillars("TEST", custom_df=df, custom_float=8_000_000)
            self.assertGreaterEqual(res_news["score"], 85.0)
            self.assertEqual(res_news["grade"], "A")
            self.assertEqual(res_news["pillars_passed"], "5/5")

    def test_five_pillars_disqualified_grade_c(self):
        from market.low_float_scanner import evaluate_five_pillars
        import pandas as pd

        dates = pd.bdate_range("2026-01-01", periods=60)
        closes = [0.10] * 60  # price $0.10 (< $0.50 penny floor)
        vols = [100_000] * 60
        df = pd.DataFrame({
            "Open": closes, "High": closes, "Low": closes, "Close": closes, "Volume": vols
        }, index=dates)

        res = evaluate_five_pillars("JUNK", custom_df=df, custom_float=100_000_000)
        self.assertEqual(res["grade"], "C")
        self.assertFalse(res["pillars"]["p1_up_10pct"])
        self.assertFalse(res["pillars"]["p4_price_2_20"])
        self.assertFalse(res["pillars"]["p5_low_float_20m"])

    def test_simulator_ideal_execution_and_scaleout(self):
        from backtest.ross_momentum_sim import (generate_synthetic_candles,
                                               run_ross_momentum_sim,
                                               RossSessionManager)

        session = RossSessionManager(max_daily_loss=300.0)
        candles = generate_synthetic_candles("CYN", start_price=5.0, scenario="ideal_breakout")
        pillar_info = {
            "ticker": "CYN", "grade": "A", "price": 5.0,
            "float_millions": 5.0, "has_catalyst": True, "score": 90.0
        }

        trade = run_ross_momentum_sim("CYN", candles, pillar_info, session, account_risk_dollars=100.0)
        self.assertIsNotNone(trade)
        self.assertEqual(trade.status, "CLOSED")
        self.assertTrue(trade.tp1_shares > 0)          # 50% TP1 scale-out executed
        self.assertTrue(trade.breakeven_active)        # Stop raised to breakeven
        self.assertGreater(trade.realized_pnl, 0.0)    # Net winning trade
        self.assertIn("Topping Tail", trade.final_exit_reason)

    def test_simulator_stops_out_on_failed_pullback(self):
        from backtest.ross_momentum_sim import (generate_synthetic_candles,
                                               run_ross_momentum_sim,
                                               RossSessionManager)

        session = RossSessionManager(max_daily_loss=300.0)
        candles = generate_synthetic_candles("FAIL", start_price=5.0, scenario="failed_pullback")
        pillar_info = {
            "ticker": "FAIL", "grade": "A", "price": 5.0,
            "float_millions": 5.0, "has_catalyst": True, "score": 90.0
        }

        trade = run_ross_momentum_sim("FAIL", candles, pillar_info, session, account_risk_dollars=100.0)
        self.assertIsNotNone(trade)
        self.assertEqual(trade.status, "CLOSED")
        self.assertLess(trade.realized_pnl, 0.0)       # Controlled loss
        self.assertIn("Hard Stop Hit", trade.final_exit_reason)

    def test_walk_away_profit_giveback(self):
        from backtest.ross_momentum_sim import RossSessionManager

        session = RossSessionManager(max_daily_loss=300.0, profit_giveback_pct=0.50)
        # Session reaches +$400 peak
        session.register_trade_result(400.0)
        halted, _ = session.check_walk_away()
        self.assertFalse(halted)

        # Gives back -$220 (net drops to $180, which is < 50% of $400 peak)
        session.register_trade_result(-220.0)
        halted, reason = session.check_walk_away()
        self.assertTrue(halted)
        self.assertIn("Profit Giveback Rule Triggered", reason)


if __name__ == "__main__":
    unittest.main()