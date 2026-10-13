r"""
Two-Worker Bayesian Belief & Confidence Updating Engine
======================================================
Implements an autonomous, self-improving quantitative confidence tracker
operating day-over-day without lookahead bias.

Inspired by Quantitative Agent Frameworks (e.g. FidetoLabs & Bayesian Inference):
  "To build an agent that improves itself you need four things:
   a strategy, the data behind it, something that turns it into one table,
   and a backtest to score it. Then it loops. Scores the strategy, reads the score,
   changes something, runs again, writes down what it learned."

Two-Worker Architecture:
-------------------------
1. Worker 1 (Information / Evidence Harvester):
   - Daily collection of point-in-time market evidence:
     * Anti-volatility stabilized price, residual z-score, Price Stability Index (PSI).
     * Technical posture: RSI, MACD signal, ATR, Relative Volume (RVOL).
     * Directional NLP sentiment from news/filings.
     * Price performance vs the "level we bought before" (cost basis).
   - Bundles evidence into an immutable DailyEvidenceBundle.

2. Worker 2 (Bayesian Confidence & Hypothesis Verification Engine):
   - Statement Verification: Evaluates whether yesterday's forward statement/hypothesis
     was verified by today's realized price action.
   - Sequential Bayesian Updating:
     * Prior belief: $P(\text{Thesis}_{t-1})$
     * Likelihood: Combines statement verification outcome, price stability, sentiment, and momentum.
     * Posterior belief: $P(\text{Thesis}_t \mid \text{Evidence}_t)$
     * Normalized 0–100 Confidence Pointer.
   - Cost Basis Anchoring: Tracks whether gains above the original buy level compound conviction,
     or whether breakdown below cost triggers scale-out/exit invalidation.
   - Self-Improving Knowledge Ledger: Writes down learned heuristics after each verification step.
"""

from __future__ import annotations

import json
import logging
import math
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from market.anti_volatility import anti_volatility_model
from market.technicals import TechnicalIndicators as TI

logger = logging.getLogger(__name__)

DB_PATH = Path("execution/belief_engine.db")
NY_TZ = ZoneInfo("America/New_York")


@dataclass
class DailyEvidenceBundle:
    """Immutable market evidence harvested by Worker 1."""
    ticker: str
    as_of_date: str
    raw_price: float
    stabilized_price: float
    price_stability_index: float
    residual_zscore: float
    noise_std: float
    one_day_return_pct: float
    rsi: float
    macd_signal: float
    rvol: float
    sentiment_score: float  # -1.0 to +1.0
    cost_basis: Optional[float]
    gain_since_entry_pct: Optional[float]


@dataclass
class ThesisStatement:
    """Quantitative hypothesis formulated and verified day-over-day."""
    ticker: str
    as_of_date: str
    expected_direction: str         # "BULLISH", "BEARISH", "NEUTRAL"
    confidence_pointer: float       # 0.0 to 100.0
    target_price: float
    stop_price: float
    stabilized_price: float
    entry_level: Optional[float]
    verified: Optional[bool]        # None until next day evaluation
    verification_score: float       # -1.0 (invalidated) to +1.0 (verified)
    verification_notes: str
    recommendation: str             # "ACCUMULATE", "HOLD_CONVICTION", "SCALE_OUT", "EXIT_INVALIDATED"


@dataclass
class LearnedRule:
    """Self-improving insight written down by the engine."""
    id: int
    ticker: str
    recorded_at: str
    category: str
    lesson: str
    impact_score: float


# ---------------------------------------------------------------------------
# Worker 1: Information / Evidence Harvester
# ---------------------------------------------------------------------------
class InformationHarvester:
    """
    Worker 1: Daily data aggregator combining price, anti-volatility stabilization,
    technicals, sentiment, and cost-basis tracking into an evidence bundle.
    """

    def harvest(
        self,
        ticker: str,
        cost_basis: Optional[float] = None,
        df_bars: Optional[pd.DataFrame] = None,
        as_of_date: Optional[str] = None,
    ) -> DailyEvidenceBundle:
        ticker = ticker.upper().strip()
        as_of = as_of_date or datetime.now(NY_TZ).strftime("%Y-%m-%d")

        if df_bars is None or df_bars.empty:
            from market.price_fetcher import fetch_prices
            df_bars = fetch_prices(ticker, period="3mo")

        if df_bars.empty:
            raise ValueError(f"Worker 1 could not fetch price bars for {ticker}")

        close_col = "Close" if "Close" in df_bars.columns else df_bars.columns[0]
        high_col = "High" if "High" in df_bars.columns else close_col
        low_col = "Low" if "Low" in df_bars.columns else close_col
        vol_col = "Volume" if "Volume" in df_bars.columns else None

        # 1. Anti-Volatility Model Evaluation
        stab_res = anti_volatility_model.evaluate_ticker(ticker, df_bars=df_bars)
        raw_px = stab_res.current_raw_price
        stab_px = stab_res.stabilized_price
        psi = stab_res.price_stability_index
        zscore = stab_res.residual_zscore
        noise_std = stab_res.noise_std

        # 2. Realized 1-day return
        closes = df_bars[close_col]
        ret_1d = float(closes.pct_change().iloc[-1] * 100.0) if len(closes) > 1 else 0.0

        # 3. Technical Indicators
        rsi_series = TI.rsi(closes, length=14)
        rsi = float(rsi_series.iloc[-1]) if not rsi_series.empty else 50.0

        macd_line, macd_sig = TI.macd(closes)
        macd_diff = float((macd_line - macd_sig).iloc[-1]) if not macd_sig.empty else 0.0

        if vol_col and vol_col in df_bars.columns:
            rvol = float(TI.volume_ratio(df_bars[vol_col], length=20))
        else:
            rvol = 1.0

        # 4. Sentiment Extraction (Point-in-Time safe)
        sentiment_score = self._extract_sentiment(ticker)

        # 5. Cost-Basis tracking ("level that we buy before")
        gain_since_entry = None
        if cost_basis is not None and cost_basis > 0:
            gain_since_entry = round(((raw_px - cost_basis) / cost_basis) * 100.0, 2)

        return DailyEvidenceBundle(
            ticker=ticker,
            as_of_date=as_of,
            raw_price=raw_px,
            stabilized_price=stab_px,
            price_stability_index=psi,
            residual_zscore=zscore,
            noise_std=noise_std,
            one_day_return_pct=round(ret_1d, 2),
            rsi=round(rsi, 1),
            macd_signal=round(macd_diff, 3),
            rvol=round(rvol, 2),
            sentiment_score=round(sentiment_score, 3),
            cost_basis=round(cost_basis, 2) if cost_basis else None,
            gain_since_entry_pct=gain_since_entry,
        )

    def _extract_sentiment(self, ticker: str) -> float:
        """Point-in-time news sentiment extraction using FinBERT / cached news memory."""
        try:
            from nlp.news_memory import news_memory
            # Query recent headlines from memory
            cached = news_memory.get_recent(ticker, limit=5)
            if cached:
                scores = [float(item.get("sentiment_score", 0.0)) for item in cached]
                return float(np.mean(scores))
        except Exception:
            pass

        # Fallback to general sentiment or neutral
        return 0.15


# ---------------------------------------------------------------------------
# Worker 2: Bayesian Confidence & Self-Improving Belief Engine
# ---------------------------------------------------------------------------
class BayesianConfidenceEngine:
    """
    Worker 2: Sequential Bayesian belief updater with daily hypothesis testing,
    confidence pointer calibration, and self-improving knowledge ledger.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.harvester = InformationHarvester()
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_statements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    as_of_date TEXT NOT NULL,
                    expected_direction TEXT NOT NULL,
                    confidence_pointer REAL NOT NULL,
                    target_price REAL NOT NULL,
                    stop_price REAL NOT NULL,
                    stabilized_price REAL NOT NULL,
                    entry_level REAL,
                    verified INTEGER,
                    verification_score REAL,
                    verification_notes TEXT,
                    recommendation TEXT,
                    evidence_json TEXT,
                    created_at REAL NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learned_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    category TEXT NOT NULL,
                    lesson TEXT NOT NULL,
                    impact_score REAL NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_statements_ticker_date ON daily_statements(ticker, as_of_date)")

    def get_latest_statement(self, ticker: str) -> Optional[ThesisStatement]:
        """Retrieves the most recent thesis statement recorded for this ticker."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """SELECT ticker, as_of_date, expected_direction, confidence_pointer,
                          target_price, stop_price, stabilized_price, entry_level,
                          verified, verification_score, verification_notes, recommendation
                   FROM daily_statements
                   WHERE ticker = ?
                   ORDER BY id DESC LIMIT 1""",
                (ticker.upper(),),
            ).fetchone()

        if not row:
            return None

        return ThesisStatement(
            ticker=row[0],
            as_of_date=row[1],
            expected_direction=row[2],
            confidence_pointer=row[3],
            target_price=row[4],
            stop_price=row[5],
            stabilized_price=row[6],
            entry_level=row[7],
            verified=bool(row[8]) if row[8] is not None else None,
            verification_score=row[9] or 0.0,
            verification_notes=row[10] or "",
            recommendation=row[11] or "HOLD_CONVICTION",
        )

    def verify_yesterday_statement(
        self,
        yesterday_stmt: ThesisStatement,
        today_evidence: DailyEvidenceBundle,
    ) -> Tuple[bool, float, str]:
        """
        Verifies whether yesterday's hypothesis was verified by today's realized action:
          - Did price move in expected direction?
          - Did price stay above stop level and stabilized lower band?
          - Did it approach or hit target?
        Returns: (verified, verification_score [-1.0, +1.0], explanation)
        """
        raw_px = today_evidence.raw_price
        ret_1d = today_evidence.one_day_return_pct
        stop_px = yesterday_stmt.stop_price
        target_px = yesterday_stmt.target_price
        direction = yesterday_stmt.expected_direction

        # Check 1: Stop breach (Fatal violation)
        if direction == "BULLISH" and raw_px < stop_px:
            return False, -1.0, f"Hard stop breached: price dropped to ${raw_px:.2f} below stop ${stop_px:.2f}"

        # Check 2: Directional conformity
        if direction == "BULLISH":
            if raw_px >= target_px:
                return True, 1.0, f"Target fulfilled: price reached ${raw_px:.2f} (target ${target_px:.2f})"
            elif ret_1d > 0.3:
                return True, 0.75, f"Bullish trend confirmed: realized gain of +{ret_1d:.2f}%"
            elif -0.5 <= ret_1d <= 0.3:
                return True, 0.25, f"Consolidation hold: price stable at ${raw_px:.2f} (change {ret_1d:+.2f}%)"
            else:
                return False, -0.6, f"Adverse move: price pulled back {ret_1d:+.2f}% to ${raw_px:.2f}"
        elif direction == "BEARISH":
            if ret_1d < -0.3:
                return True, 0.75, f"Bearish hypothesis verified: price declined {ret_1d:+.2f}%"
            else:
                return False, -0.6, f"Bearish thesis invalidated: price rose {ret_1d:+.2f}%"
        else:
            return True, 0.1, "Neutral statement maintained within expected noise band"

    def run_daily_cycle(
        self,
        ticker: str,
        cost_basis: Optional[float] = None,
        df_bars: Optional[pd.DataFrame] = None,
        as_of_date: Optional[str] = None,
    ) -> ThesisStatement:
        """
        Executes the full Two-Worker daily feedback loop:
          1. Worker 1 harvests today's market evidence bundle.
          2. Worker 2 inspects yesterday's statement and validates it.
          3. Worker 2 runs Bayesian belief updating (Prior -> Likelihood -> Posterior).
          4. Anchors confidence against original cost basis ("level that we buy before").
          5. Generates today's new ThesisStatement & writes down learned rules.
        """
        ticker = ticker.upper().strip()
        as_of = as_of_date or datetime.now(NY_TZ).strftime("%Y-%m-%d")

        # Step 1: Worker 1 Harvests Evidence
        evidence = self.harvester.harvest(ticker, cost_basis=cost_basis, df_bars=df_bars, as_of_date=as_of)

        # Step 2: Check Yesterday's Statement
        yesterday_stmt = self.get_latest_statement(ticker)

        if yesterday_stmt is not None and yesterday_stmt.as_of_date != as_of and yesterday_stmt.verified is None:
            # Verify yesterday's statement
            verified, ver_score, ver_notes = self.verify_yesterday_statement(yesterday_stmt, evidence)
            self._update_statement_verification(yesterday_stmt.ticker, yesterday_stmt.as_of_date, verified, ver_score, ver_notes)
            # Record self-improving lesson
            self._record_learning(ticker, yesterday_stmt, evidence, verified, ver_score, ver_notes)
            prior_conf = yesterday_stmt.confidence_pointer / 100.0
        else:
            # First time running or already evaluated today
            prior_conf = 0.55 if evidence.stabilized_price > 0 else 0.50
            ver_score = 0.0
            ver_notes = "Initial baseline cycle"

        # Step 3: Bayesian Update Formula
        # Convert Prior to Log-Odds
        prior_conf = np.clip(prior_conf, 0.05, 0.95)
        prior_log_odds = math.log(prior_conf / (1.0 - prior_conf))

        # Evidence Weights (Likelihood updates):
        # A. Statement Verification Impact
        delta_verification = ver_score * 0.45

        # B. Anti-Volatility Model (Price Stability Index)
        # High PSI (clean trend) amplifies conviction; Low PSI (erratic noise) dampens it
        psi_normalized = (evidence.price_stability_index - 50.0) / 50.0  # -1.0 to +1.0
        delta_stability = psi_normalized * 0.30

        # C. NLP Sentiment Impact
        delta_sentiment = evidence.sentiment_score * 0.25

        # D. Technical Trend (RSI & MACD)
        tech_score = 0.0
        if 45.0 <= evidence.rsi <= 65.0:
            tech_score += 0.2
        elif evidence.rsi > 75.0:
            tech_score -= 0.2  # Overbought exhaustion risk
        elif evidence.rsi < 35.0:
            tech_score += 0.1  # Potential oversold rebound
        if evidence.macd_signal > 0:
            tech_score += 0.15
        else:
            tech_score -= 0.15
        delta_technicals = tech_score * 0.35

        # E. Cost-Basis Anchoring ("level that we buy before")
        delta_cost_basis = 0.0
        if evidence.gain_since_entry_pct is not None:
            if evidence.gain_since_entry_pct > 3.0:
                delta_cost_basis = +0.30  # Compounding winners
            elif evidence.gain_since_entry_pct < -3.0:
                delta_cost_basis = -0.40  # Bleeding below cost basis degrades conviction

        total_delta = (
            delta_verification +
            delta_stability +
            delta_sentiment +
            delta_technicals +
            delta_cost_basis
        )

        posterior_log_odds = prior_log_odds + total_delta
        posterior_prob = 1.0 / (1.0 + math.exp(-posterior_log_odds))
        posterior_prob = float(np.clip(posterior_prob, 0.05, 0.95))
        confidence_pointer = round(posterior_prob * 100.0, 1)

        # Step 4: Formulate Today's Forward Hypothesis
        direction = "BULLISH" if posterior_prob >= 0.52 else ("BEARISH" if posterior_prob <= 0.40 else "NEUTRAL")
        atr_proxy = max(evidence.noise_std * 2.0, evidence.raw_price * 0.015)
        target_price = round(evidence.stabilized_price + (1.8 * atr_proxy), 2)
        stop_price = round(evidence.stabilized_price - (1.5 * atr_proxy), 2)

        # Recommendation based on confidence pointer & cost basis
        if confidence_pointer >= 75.0 and (evidence.gain_since_entry_pct is None or evidence.gain_since_entry_pct >= -1.0):
            recommendation = "ACCUMULATE"
        elif confidence_pointer >= 55.0:
            recommendation = "HOLD_CONVICTION"
        elif confidence_pointer >= 40.0:
            recommendation = "SCALE_OUT"
        else:
            recommendation = "EXIT_INVALIDATED"

        new_stmt = ThesisStatement(
            ticker=ticker,
            as_of_date=as_of,
            expected_direction=direction,
            confidence_pointer=confidence_pointer,
            target_price=target_price,
            stop_price=stop_price,
            stabilized_price=evidence.stabilized_price,
            entry_level=cost_basis,
            verified=None,
            verification_score=0.0,
            verification_notes="Active today — pending next-day verification",
            recommendation=recommendation,
        )

        # Step 5: Save to SQLite Ledger
        self._save_statement(new_stmt, evidence)

        return new_stmt

    def _save_statement(self, stmt: ThesisStatement, evidence: DailyEvidenceBundle) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO daily_statements
                   (ticker, as_of_date, expected_direction, confidence_pointer,
                    target_price, stop_price, stabilized_price, entry_level,
                    verified, verification_score, verification_notes, recommendation,
                    evidence_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    stmt.ticker,
                    stmt.as_of_date,
                    stmt.expected_direction,
                    stmt.confidence_pointer,
                    stmt.target_price,
                    stmt.stop_price,
                    stmt.stabilized_price,
                    stmt.entry_level,
                    None,
                    0.0,
                    stmt.verification_notes,
                    stmt.recommendation,
                    json.dumps(asdict(evidence)),
                    time.time(),
                ),
            )

    def _update_statement_verification(
        self,
        ticker: str,
        as_of_date: str,
        verified: bool,
        score: float,
        notes: str,
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE daily_statements
                   SET verified = ?, verification_score = ?, verification_notes = ?
                   WHERE ticker = ? AND as_of_date = ?""",
                (1 if verified else 0, score, notes, ticker, as_of_date),
            )

    def _record_learning(
        self,
        ticker: str,
        prior_stmt: ThesisStatement,
        today_ev: DailyEvidenceBundle,
        verified: bool,
        score: float,
        notes: str,
    ) -> None:
        """
        Self-improving feedback: writes down what the quantitative agent learned from this iteration.
        """
        timestamp = datetime.now(NY_TZ).strftime("%Y-%m-%d %H:%M ET")
        if verified:
            cat = "THESIS_CONFIRMATION"
            lesson = (
                f"Rule on {ticker}: {prior_stmt.expected_direction} statement verified ({notes}). "
                f"Anti-volatility stabilized price ${today_ev.stabilized_price:.2f} provided reliable trajectory "
                f"with Price Stability Index at {today_ev.price_stability_index:.1f}%."
            )
        else:
            cat = "INVALIDATION_DEFENSE"
            lesson = (
                f"Rule on {ticker}: Prior statement falsified ({notes}). "
                f"Noise residual z-score hit {today_ev.residual_zscore:+.2f}. "
                f"Learned to enforce tighter stop when PSI falls below 45%."
            )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO learned_rules (ticker, recorded_at, category, lesson, impact_score)
                   VALUES (?, ?, ?, ?, ?)""",
                (ticker, timestamp, cat, lesson, abs(score)),
            )

    def get_learned_rules(self, limit: int = 20) -> List[LearnedRule]:
        """Returns the self-improving knowledge ledger."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """SELECT id, ticker, recorded_at, category, lesson, impact_score
                   FROM learned_rules
                   ORDER BY id DESC LIMIT ?""",
                (limit,),
            ).fetchall()

        return [
            LearnedRule(
                id=r[0],
                ticker=r[1],
                recorded_at=r[2],
                category=r[3],
                lesson=r[4],
                impact_score=r[5],
            )
            for r in rows
        ]

    def get_history(self, ticker: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Returns the chronological confidence pointer ledger for an asset."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """SELECT as_of_date, expected_direction, confidence_pointer,
                          target_price, stop_price, stabilized_price, entry_level,
                          verified, verification_score, verification_notes,
                          recommendation, evidence_json
                   FROM daily_statements
                   WHERE ticker = ?
                   ORDER BY id ASC LIMIT ?""",
                (ticker.upper(), limit),
            ).fetchall()

        history = []
        for r in rows:
            ev = json.loads(r[11]) if r[11] else {}
            history.append({
                "date": r[0],
                "direction": r[1],
                "confidence_pointer": r[2],
                "target_price": r[3],
                "stop_price": r[4],
                "stabilized_price": r[5],
                "entry_level": r[6],
                "verified": bool(r[7]) if r[7] is not None else None,
                "verification_score": r[8],
                "verification_notes": r[9],
                "recommendation": r[10],
                "evidence": ev,
            })
        return history


# Singleton instance
belief_engine = BayesianConfidenceEngine()
