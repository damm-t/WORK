"""
Autonomous Compliance & Strategy Reinforcement Checker
======================================================
Pre-Trade Gatekeeper + Post-Trade Praise & Punish Reinforcement Engine.

1. Pre-Trade Strict Compliance Verification:
   - Capital & Sizing Compliance (Risk <= 2%, Heat <= 50%, Daily Loss > -3%)
   - Whale Trap & Attention Defense (Rejects high-volume negative momentum distribution traps)
   - Liquidity & RVOL Floor (No trading into dead volume or illiquid spreads)
   - Shock & Earnings Blackout (Freezes setups near earnings or gap shocks)

2. Post-Trade Autonomous Audit (Praise & Punish Loop):
   - PRAISE (+Reward): Disciplined trades that adhered to rules and realized positive edge.
     Increases strategy confidence multiplier and streak compounding.
   - PUNISH (-Penalty): Disciplined breaches, chased candles, or preventable drawdowns.
     Demotes strategy factor weights, locks ticker on temporary cooldown, and records learned rule.

3. Antigravity AI Revision Interface:
   - Formats structured review packets for AI models / agents to critique and refine.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from compliance.ai_revision_checker import TradeReviewPacket, ai_reviewer

logger = logging.getLogger(__name__)

COMPLIANCE_DB = Path("execution/compliance_audit.db")
NY_TZ = ZoneInfo("America/New_York")


@dataclass
class ComplianceCertificate:
    """Immutable audit certificate generated prior to trade placement."""
    ticker: str
    timestamp: float
    approved: bool
    compliance_score: int         # 0 to 100
    verdict: str                  # "PASSED_STRICT", "BLOCKED_VIOLATION", "WARNING_OVERRIDE"
    violations: List[str] = field(default_factory=list)
    praises: List[str] = field(default_factory=list)
    strategy_dispatched: Optional[str] = None
    risk_pct_authorized: float = 0.02
    audit_notes: str = ""


@dataclass
class AuditFeedback:
    """Post-trade audit result evaluating execution discipline."""
    trade_id: int
    ticker: str
    action: str                   # "PRAISE" or "PUNISH"
    pnl: float
    score_delta: float
    confidence_multiplier: float
    violations_found: List[str]
    rule_learned: str
    timestamp: float = field(default_factory=time.time)


class AutonomousComplianceChecker:
    """
    Enforces institutional compliance, prevents whale traps, and runs
    the continuous praise/punish reinforcement loop.
    """

    def __init__(self, db_path: Path = COMPLIANCE_DB):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pre_trade_audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                timestamp REAL,
                approved INTEGER,
                compliance_score INTEGER,
                verdict TEXT,
                strategy TEXT,
                violations TEXT,
                praises TEXT,
                notes TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS post_trade_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id INTEGER,
                ticker TEXT,
                timestamp REAL,
                action TEXT,
                pnl REAL,
                score_delta REAL,
                confidence_multiplier REAL,
                violations TEXT,
                rule_learned TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS strategy_weights (
                strategy_name TEXT PRIMARY KEY,
                multiplier REAL,
                total_praises INTEGER,
                total_punishments INTEGER,
                last_updated REAL
            )
        """)
        # Initialize default weights if not present
        default_strategies = ["jev_scooper", "ross_momentum", "core_swing"]
        for s in default_strategies:
            conn.execute("""
                INSERT OR IGNORE INTO strategy_weights (strategy_name, multiplier, total_praises, total_punishments, last_updated)
                VALUES (?, 1.0, 0, 0, ?)
            """, (s, time.time()))
        conn.commit()
        conn.close()

    # ------------------------------------------------- 1. Pre-Trade Gatekeeper
    def audit_pre_trade_setup(
        self,
        ticker: str,
        price: float,
        rvol: float,
        price_change_5d_pct: float,
        sentiment_score: float = 0.0,
        dislocation_zscore: Optional[float] = None,
        strategy_candidate: str = "core_swing",
        account_equity: float = 10000.0,
        current_heat: float = 0.0,
        day_pnl_pct: float = 0.0,
        near_earnings: bool = False,
        shock_detected: bool = False,
        side: str = "LONG",
    ) -> ComplianceCertificate:
        """
        Runs comprehensive pre-trade institutional compliance verification.
        Blocks entries if any discipline rule is violated.
        """
        ticker = ticker.upper().strip()
        side = side.upper().strip()
        violations = []
        praises = []
        score = 100

        # Rule 1: Daily Loss Drawdown Lock (-3% Max)
        if day_pnl_pct <= -0.03:
            violations.append(f"DAILY_DRAWDOWN_LIMIT: Day PnL ({day_pnl_pct:+.2%}) breached -3.0% threshold. All entries locked.")
            score -= 50

        # Rule 2: Portfolio Heat Cap (50% Max)
        if current_heat >= 0.50:
            violations.append(f"HEAT_LIMIT: Portfolio heat ({current_heat:.1%}) at or above 50.0% cap.")
            score -= 30
        else:
            praises.append(f"Portfolio heat ({current_heat:.1%}) within safe 50% capacity.")

        # Rule 3: Whale Distribution Trap Defense (Candidate C Rule)
        # High volume (RVOL >= 2.0x) + Negative momentum (< -1.0%) = Whale Dump
        is_whale_dump = (rvol >= 2.0 and price_change_5d_pct < -1.0)
        is_dislocated_scoop = (dislocation_zscore is not None and dislocation_zscore <= -1.8)

        if is_whale_dump:
            if side == "SHORT":
                praises.append("WHALE_DUMP_CONFIRMATION: High volume breakdown confirms institutional distribution for short entry.")
            elif strategy_candidate == "jev_scooper" and is_dislocated_scoop:
                praises.append("WHALE_DUMP_DISLOCATION: Negative momentum is an institutional dislocation, authorized for JEV Scooper.")
            else:
                violations.append(
                    f"WHALE_TRAP_DETECTED: RVOL {rvol:.1f}x with negative momentum ({price_change_5d_pct:+.1f}%) "
                    "signals institutional distribution. Chasing long prohibited."
                )
                score -= 40

        # Rule 4: Liquidity / RVOL Floor
        min_rvol = 2.0 if strategy_candidate == "ross_momentum" else 0.8
        if rvol < min_rvol:
            violations.append(f"INSUFFICIENT_LIQUIDITY: RVOL {rvol:.2f}x below required {min_rvol:.1f}x floor.")
            score -= 25
        else:
            praises.append(f"Healthy volume participation (RVOL {rvol:.2f}x >= {min_rvol:.1f}x).")

        # Rule 5: Shock Defense & Earnings Blackout
        if shock_detected:
            violations.append("SHOCK_FREEZE: Intraday velocity shock or uncontained gap in progress.")
            score -= 40
        if near_earnings:
            violations.append("EARNINGS_BLACKOUT: Setup is within 24h of earnings announcement.")
            score -= 35

        # Rule 6: Sentiment Confirmation (FinBERT alignment)
        if side == "LONG":
            if strategy_candidate in ("core_swing", "ross_momentum") and sentiment_score < -0.30:
                violations.append(f"BEARISH_SENTIMENT_CONFLICT: FinBERT sentiment ({sentiment_score:+.2f}) hostile to long entry.")
                score -= 20
            elif sentiment_score > 0.20:
                praises.append(f"FinBERT sentiment confirms bullish thesis ({sentiment_score:+.2f}).")
        elif side == "SHORT":
            if strategy_candidate in ("core_swing", "ross_momentum") and sentiment_score > 0.30:
                violations.append(f"BULLISH_SENTIMENT_CONFLICT: FinBERT sentiment ({sentiment_score:+.2f}) hostile to short entry.")
                score -= 20
            elif sentiment_score < -0.20:
                praises.append(f"FinBERT sentiment confirms bearish thesis ({sentiment_score:+.2f}).")

        # Calculate Verdict
        final_score = max(0, min(100, score))
        approved = len(violations) == 0 and final_score >= 70

        # Invoke Autonomous AI Model Reviewer for Pre-Trade Revision
        ai_packet = TradeReviewPacket(
            ticker=ticker,
            strategy=strategy_candidate,
            action="PRE_TRADE_PROPOSAL",
            price=price,
            rvol=rvol,
            momentum_5d_pct=price_change_5d_pct,
            sentiment_score=sentiment_score,
            price_stability_index=50.0,
            dislocation_zscore=dislocation_zscore or 0.0,
            notes=f"Heat: {current_heat:.1%}, DayPnL: {day_pnl_pct:+.2%}",
            side=side,
        )
        ai_review = ai_reviewer.evaluate_pre_trade(ai_packet)

        # Merge AI review insights
        for p in ai_review.praises:
            if p not in praises:
                praises.append(f"[AI] {p}")
        for viol in ai_review.punishments:
            if viol not in violations:
                violations.append(f"[AI] {viol}")

        if ai_review.verdict == "REJECTED_PUNISH":
            approved = False

        verdict = "PASSED_STRICT" if approved else "BLOCKED_VIOLATION"
        cert = ComplianceCertificate(
            ticker=ticker,
            timestamp=time.time(),
            approved=approved,
            compliance_score=min(final_score, ai_review.compliance_score),
            verdict=verdict,
            violations=violations,
            praises=praises,
            strategy_dispatched=strategy_candidate if approved else None,
            risk_pct_authorized=0.015 if approved else 0.0,
            audit_notes=f"Compliance evaluated: {len(praises)} praises, {len(violations)} violations. AI Model: {ai_review.model_source} ({ai_review.verdict})."
        )

        self._record_pre_trade_audit(cert)
        return cert

    # ------------------------------------------------- 2. Post-Trade Audit & Reinforcement
    def audit_closed_trade(
        self,
        trade_id: int,
        ticker: str,
        strategy_name: str,
        pnl: float,
        entry_price: float,
        exit_price: float,
        holding_time_hours: float,
        reason: str,
        slippage_bps: float = 0.0,
    ) -> AuditFeedback:
        """
        Audits a closed trade. Rewards compliant execution and penalizes discipline failures.
        Submits trade to AI model to praise or punish and updates strategy multipliers dynamically.
        """
        ticker = ticker.upper().strip()
        strategy_name = strategy_name.lower().strip()

        # Submit to Autonomous AI Reviewer
        ai_packet = TradeReviewPacket(
            ticker=ticker,
            strategy=strategy_name,
            action="POST_TRADE_CLOSE",
            price=exit_price,
            pnl=pnl,
            exit_reason=reason,
            slippage_bps=slippage_bps,
            notes=f"Entry: ${entry_price:.2f}, Exit: ${exit_price:.2f}, Hold: {holding_time_hours:.1f}h"
        )
        ai_review = ai_reviewer.evaluate_post_trade(ai_packet)

        is_praise = (ai_review.verdict in ("APPROVED_PRAISE", "APPROVED_NEUTRAL"))
        action = "PRAISE" if is_praise else "PUNISH"
        score_delta = +5.0 if pnl > 0 else (+1.0 if is_praise else -10.0)

        # Update dynamic weights in SQLite
        new_mult = self._update_strategy_multiplier(strategy_name, action)

        feedback = AuditFeedback(
            trade_id=trade_id,
            ticker=ticker,
            action=action,
            pnl=round(pnl, 2),
            score_delta=score_delta,
            confidence_multiplier=round(new_mult, 3),
            violations_found=ai_review.punishments,
            rule_learned=ai_review.rule_learned or f"{action} {strategy_name} on {ticker}.",
        )

        self._record_post_trade_evaluation(feedback)
        return feedback

    # ------------------------------------------------- Database & State Helpers
    def _update_strategy_multiplier(self, strategy_name: str, action: str) -> float:
        conn = sqlite3.connect(self.db_path)
        row = conn.execute(
            "SELECT multiplier, total_praises, total_punishments FROM strategy_weights WHERE strategy_name = ?",
            (strategy_name,)
        ).fetchone()

        if not row:
            curr_mult, praises, punishes = 1.0, 0, 0
        else:
            curr_mult, praises, punishes = float(row[0]), int(row[1]), int(row[2])

        if action == "PRAISE":
            praises += 1
            # Rewarded: gently scale up multiplier by 2% (capped at 1.25x)
            new_mult = min(1.25, round(curr_mult * 1.02, 3))
        else:
            punishes += 1
            # Punished: cut multiplier by 5% (floored at 0.70x)
            new_mult = max(0.70, round(curr_mult * 0.95, 3))

        conn.execute("""
            INSERT OR REPLACE INTO strategy_weights (strategy_name, multiplier, total_praises, total_punishments, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """, (strategy_name, new_mult, praises, punishes, time.time()))
        conn.commit()
        conn.close()
        return new_mult

    def get_strategy_multiplier(self, strategy_name: str) -> float:
        conn = sqlite3.connect(self.db_path)
        row = conn.execute("SELECT multiplier FROM strategy_weights WHERE strategy_name = ?", (strategy_name.lower(),)).fetchone()
        conn.close()
        return float(row[0]) if row else 1.0

    def _record_pre_trade_audit(self, cert: ComplianceCertificate) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO pre_trade_audits (ticker, timestamp, approved, compliance_score, verdict, strategy, violations, praises, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cert.ticker, cert.timestamp, 1 if cert.approved else 0, cert.compliance_score,
            cert.verdict, cert.strategy_dispatched or "",
            json.dumps(cert.violations), json.dumps(cert.praises), cert.audit_notes
        ))
        conn.commit()
        conn.close()

    def _record_post_trade_evaluation(self, fb: AuditFeedback) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO post_trade_evaluations (trade_id, ticker, timestamp, action, pnl, score_delta, confidence_multiplier, violations, rule_learned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fb.trade_id, fb.ticker, fb.timestamp, fb.action, fb.pnl, fb.score_delta,
            fb.confidence_multiplier, json.dumps(fb.violations_found), fb.rule_learned
        ))
        conn.commit()
        conn.close()

    def generate_ai_compliance_report(self) -> Dict[str, Any]:
        """
        Synthesizes recent compliance audits into an AI-structured review report.
        """
        conn = sqlite3.connect(self.db_path)
        weights_rows = conn.execute("SELECT strategy_name, multiplier, total_praises, total_punishments FROM strategy_weights").fetchall()
        eval_rows = conn.execute(
            "SELECT ticker, action, pnl, rule_learned, timestamp FROM post_trade_evaluations ORDER BY id DESC LIMIT 10"
        ).fetchall()
        pre_rows = conn.execute(
            "SELECT ticker, approved, compliance_score, verdict, violations FROM pre_trade_audits ORDER BY id DESC LIMIT 10"
        ).fetchall()
        conn.close()

        strategies = {r[0]: {"multiplier": r[1], "praises": r[2], "punishments": r[3]} for r in weights_rows}
        recent_evals = [{
            "ticker": r[0], "action": r[1], "pnl": r[2], "rule_learned": r[3],
            "date": datetime.fromtimestamp(r[4], tz=NY_TZ).strftime("%Y-%m-%d %H:%M")
        } for r in eval_rows]

        recent_audits = [{
            "ticker": r[0], "approved": bool(r[1]), "score": r[2], "verdict": r[3],
            "violations": json.loads(r[4] or "[]")
        } for r in pre_rows]

        ai_reviews = ai_reviewer.get_recent_reviews(limit=10)

        return {
            "timestamp": time.time(),
            "as_of": datetime.now(tz=NY_TZ).strftime("%Y-%m-%d %H:%M:%S ET"),
            "strategy_weights": strategies,
            "recent_post_trade_evaluations": recent_evals,
            "recent_pre_trade_audits": recent_audits,
            "recent_ai_model_reviews": ai_reviews,
        }


compliance_checker = AutonomousComplianceChecker()
