"""
Tri-Confluence Institutional Strategy Matrix
===========================================
Fuses all 3 quantitative decision engines into a single unified orchestrator:
  1. JEV Liquidity Scooper (Capitulation voids & mean-reversion scoops)
  2. Ross Cameron Momentum (Low-float 1-min micro-breakouts)
  3. Core Swing Book (FinBERT NLP + Anti-Volatility PSI + Paired ETF Hedge)

Includes:
  - Whale Trap Attention Filter (Candidate A breakout vs. Candidate C distribution trap)
  - 100-Point Confluence Scoring Model
  - Pre-Trade Autonomous Compliance Verification
  - Dynamic Self-Improving Strategy Weights (Praised vs. Punished)
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from compliance.autonomous_checker import (
    ComplianceCertificate,
    compliance_checker,
)
from market.anti_volatility import anti_volatility_model
from market.technicals import TechnicalIndicators as TI
from model.bayesian_confidence import belief_engine
from strategy.jev_scooper import jev_scooper

logger = logging.getLogger(__name__)


@dataclass
class ConfluenceDecision:
    """Unified master decision for a trade candidate."""
    ticker: str
    evaluated_at: float
    composite_score: float             # 0 to 100
    volume_score: float                # max 30
    momentum_score: float              # max 25
    sentiment_score: float             # max 25
    stability_score: float             # max 20
    whale_trap_flag: bool              # True if Candidate C distribution detected
    dislocation_zscore: float
    price_stability_index: float
    bayesian_confidence: float
    selected_strategy: str             # "jev_scooper", "ross_momentum", "core_swing", "NONE"
    strategy_multiplier: float         # Self-improving learned weight (0.70x to 1.25x)
    effective_conviction: float
    compliance_passed: bool
    compliance_verdict: str
    compliance_violations: List[str]
    compliance_praises: List[str]
    action_recommended: str            # "EXECUTE_SCOOP", "EXECUTE_MOMENTUM", "EXECUTE_CORE_SWING", "STANDBY_SKIP"
    summary_rationale: str


class TriConfluenceMatrix:
    """
    Evaluates market candidates across the 3 decision engines simultaneously,
    filtering false signals through institutional compliance and whale trap detection.
    """

    def __init__(self):
        self.checker = compliance_checker

    def evaluate_candidate(
        self,
        ticker: str,
        account_equity: float = 10000.0,
        current_heat: float = 0.0,
        day_pnl_pct: float = 0.0,
        float_shares_millions: Optional[float] = None,
    ) -> ConfluenceDecision:
        ticker = ticker.upper().strip()
        now = time.time()

        # 1. Fetch market indicators & stability
        stability = anti_volatility_model.evaluate_ticker(ticker)
        psi = stability.price_stability_index
        raw_price = stability.current_raw_price
        z_score = stability.residual_zscore

        # 2. Technical Posture (RVOL, 5d return, RSI)
        from market.price_fetcher import fetch_prices
        df = fetch_prices(ticker, period="1mo")
        if df.empty or len(df) < 5:
            # Fallback for illiquid / error
            rvol = 1.0
            p_change_5d = 0.0
            rsi = 50.0
        else:
            c = df["Close"].iloc[-1]
            c_5d_ago = df["Close"].iloc[-5] if len(df) >= 5 else df["Close"].iloc[0]
            p_change_5d = ((c - c_5d_ago) / max(c_5d_ago, 0.01)) * 100.0
            rvol = TI.volume_ratio(df["Volume"]) if "Volume" in df and not df["Volume"].empty else 1.0
            rsi = float(TI.rsi(df["Close"]).iloc[-1]) if "Close" in df and not df["Close"].empty else 50.0

        # 3. Bayesian Belief & Conviction
        stmt = belief_engine.get_latest_statement(ticker)
        bayes_conf = stmt.confidence_pointer if stmt else 50.0

        # 4. Sentiment Score (FinBERT)
        sentiment_score = 0.0
        try:
            from api import services
            hedge_eval = services.get_hedge_evaluation(ticker)
            sent = hedge_eval.get("sentiment") or {}
            sentiment_score = float(sent.get("score", 0.0) or 0.0)
            if sent.get("label") == "negative":
                sentiment_score = -sentiment_score
        except Exception:
            sentiment_score = 0.0

        # ------------------------------------------------------------- 100-Point Confluence Scoring
        # A. Volume & RVOL (30 pts max)
        # 1x -> 0, 3x+ -> 30
        vol_ratio = max(0.0, (rvol - 1.0) / 2.0)
        volume_score = min(30.0, max(0.0, vol_ratio * 30.0))

        # B. Price Momentum (25 pts max)
        # 0% -> 0, +10% -> 25
        mom_ratio = max(0.0, min(1.0, p_change_5d / 10.0))
        momentum_score = mom_ratio * 25.0

        # C. Sentiment & Catalyst (25 pts max)
        # -1.0 -> 0, +1.0 -> 25
        sent_ratio = max(0.0, min(1.0, (sentiment_score + 1.0) / 2.0))
        sentiment_score_pts = sent_ratio * 25.0

        # D. PSI Stability & Bayesian Conviction (20 pts max)
        # PSI (10 pts) + Bayesian Conf (10 pts)
        stab_pts = (max(0.0, min(100.0, psi)) / 100.0) * 10.0
        bayes_pts = (max(0.0, min(100.0, bayes_conf)) / 100.0) * 10.0
        stability_score = round(stab_pts + bayes_pts, 1)

        raw_composite = round(volume_score + momentum_score + sentiment_score_pts + stability_score, 1)

        # ------------------------------------------------------------- Whale Trap Detection
        # High volume (RVOL >= 2.0x) + Negative momentum (<= -1.0%) = Distribution Trap!
        whale_trap = (rvol >= 2.0 and p_change_5d <= -1.0)
        is_dislocated_scoop = (z_score <= -1.8)

        # ------------------------------------------------------------- Multi-Strategy Dispatch
        selected_strategy = "NONE"
        action_recommended = "STANDBY_SKIP"

        # Check JEV Dislocation Void first (Scooping institutional capitulation)
        if is_dislocated_scoop:
            jev_opp = jev_scooper.evaluate_ticker(ticker)
            if jev_opp.status == "QUALIFIED_SCOOP":
                selected_strategy = "jev_scooper"
                action_recommended = "EXECUTE_SCOOP"

        # Check Ross Momentum (Low float morning runner)
        elif float_shares_millions is not None and float_shares_millions < 20.0 and rvol >= 2.0:
            if not whale_trap:  # Protect against Candidate C!
                selected_strategy = "ross_momentum"
                action_recommended = "EXECUTE_MOMENTUM"

        # Check Core Swing (Laminar trend, high stability)
        elif raw_composite >= 65.0 and psi >= 45.0 and bayes_conf >= 55.0:
            if not whale_trap:
                selected_strategy = "core_swing"
                action_recommended = "EXECUTE_CORE_SWING"

        # ------------------------------------------------------------- Self-Improving Multiplier
        strat_mult = self.checker.get_strategy_multiplier(selected_strategy) if selected_strategy != "NONE" else 1.0
        effective_conviction = round(raw_composite * strat_mult, 1)

        # ------------------------------------------------------------- Compliance Verification
        cert = self.checker.audit_pre_trade_setup(
            ticker=ticker,
            price=raw_price,
            rvol=rvol,
            price_change_5d_pct=p_change_5d,
            sentiment_score=sentiment_score,
            dislocation_zscore=z_score,
            strategy_candidate=selected_strategy,
            account_equity=account_equity,
            current_heat=current_heat,
            day_pnl_pct=day_pnl_pct,
            near_earnings=False,
            shock_detected=False,
        )

        if not cert.approved:
            action_recommended = "STANDBY_SKIP"

        rationale = (
            f"Composite Score: {raw_composite}/100 [Vol: {volume_score:.1f}, Mom: {momentum_score:.1f}, "
            f"Sent: {sentiment_score_pts:.1f}, Stab: {stability_score:.1f}]. "
            f"Strategy: {selected_strategy} (weight multiplier {strat_mult:.2f}x). "
            f"Compliance: {cert.verdict} ({len(cert.violations)} violations)."
        )

        return ConfluenceDecision(
            ticker=ticker,
            evaluated_at=now,
            composite_score=raw_composite,
            volume_score=round(volume_score, 1),
            momentum_score=round(momentum_score, 1),
            sentiment_score=round(sentiment_score_pts, 1),
            stability_score=round(stability_score, 1),
            whale_trap_flag=whale_trap and not is_dislocated_scoop,
            dislocation_zscore=round(z_score, 2),
            price_stability_index=round(psi, 1),
            bayesian_confidence=round(bayes_conf, 1),
            selected_strategy=selected_strategy,
            strategy_multiplier=round(strat_mult, 3),
            effective_conviction=effective_conviction,
            compliance_passed=cert.approved,
            compliance_verdict=cert.verdict,
            compliance_violations=cert.violations,
            compliance_praises=cert.praises,
            action_recommended=action_recommended,
            summary_rationale=rationale,
        )


confluence_matrix = TriConfluenceMatrix()
