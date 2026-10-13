"""
Autonomous AI Strategy Revision & Compliance Checker
====================================================
Submits trade candidates and closed executions to an AI Model / Supervisor
to inspect, critique, revise parameters, and reward (praise) or penalize (punish).

Features:
  1. Dual Engine:
     - Google GenAI (Gemini) when API key is available.
     - Autonomous Institutional Quantitative Reasoner (offline zero-dependency fallback).
  2. Praise & Punish Mechanism:
     - PRAISE: Awards compliance score + boost to strategy confidence multiplier (up to 1.25x).
     - PUNISH: Penalizes violations (Candidate C whale traps, slippage, unmanaged risk),
       demotes strategy multiplier (down to 0.70x), and records explicit learned rules.
  3. Parameter Revision:
     - Automatically generates recommended parameter tweaks (e.g., tightened stops, size scaling).
  4. Antigravity IDE Integration:
     - Structured audit logging into SQLite (`execution/compliance_audit.db`).
     - Real-time endpoints for user and agent oversight.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

COMPLIANCE_DB = Path("execution/compliance_audit.db")
NY_TZ = ZoneInfo("America/New_York")


@dataclass
class TradeReviewPacket:
    """Standardized trade dossier provided to the AI auditor."""
    ticker: str
    strategy: str                         # "jev_scooper", "ross_momentum", "core_swing"
    action: str                           # "PRE_TRADE_PROPOSAL" or "POST_TRADE_CLOSE"
    price: float
    rvol: float = 1.0
    momentum_5d_pct: float = 0.0
    sentiment_score: float = 0.0
    price_stability_index: float = 50.0
    dislocation_zscore: float = 0.0
    pnl: Optional[float] = None
    exit_reason: Optional[str] = None
    slippage_bps: float = 0.0
    notes: str = ""
    side: str = "LONG"


@dataclass
class AIReviewResult:
    """Actionable critique and compliance judgment produced by the AI model."""
    ticker: str
    strategy: str
    action: str
    verdict: str                          # "APPROVED_PRAISE", "APPROVED_NEUTRAL", "REVISED_PARAMETERS", "REJECTED_PUNISH"
    compliance_score: int                 # 0 to 100
    praises: List[str] = field(default_factory=list)
    punishments: List[str] = field(default_factory=list)
    parameter_revisions: Dict[str, Any] = field(default_factory=dict)
    rule_learned: str = ""
    strategy_multiplier_delta: float = 0.0
    model_source: str = "antigravity-autonomous-heuristics"
    timestamp: float = field(default_factory=time.time)


class AIRevisionChecker:
    """
    Autonomous AI Review & Revision Engine for the Antigravity Trading System.
    """

    def __init__(self, db_path: Path = COMPLIANCE_DB):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_review_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                strategy TEXT,
                action TEXT,
                verdict TEXT,
                compliance_score INTEGER,
                praises TEXT,
                punishments TEXT,
                parameter_revisions TEXT,
                rule_learned TEXT,
                multiplier_delta REAL,
                model_source TEXT,
                timestamp REAL
            )
        """)
        conn.commit()
        conn.close()

    def evaluate_pre_trade(self, packet: TradeReviewPacket) -> AIReviewResult:
        """
        Submits a pre-trade candidate to the AI model for strict institutional
        verification, parameter revision, and approval/rejection.
        """
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            try:
                return self._evaluate_with_gemini(packet, is_pre_trade=True)
            except Exception as e:
                logger.warning(f"[ai_checker] Gemini evaluation error ({e}); using autonomous quantitative reasoner.")

        return self._evaluate_with_autonomous_heuristics(packet, is_pre_trade=True)

    def evaluate_post_trade(self, packet: TradeReviewPacket) -> AIReviewResult:
        """
        Submits a closed trade execution to the AI model to praise or punish discipline,
        extract learned trading rules, and refine strategy parameters.
        """
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            try:
                return self._evaluate_with_gemini(packet, is_pre_trade=False)
            except Exception as e:
                logger.warning(f"[ai_checker] Gemini post-trade review error ({e}); using autonomous quantitative reasoner.")

        return self._evaluate_with_autonomous_heuristics(packet, is_pre_trade=False)

    def _evaluate_with_autonomous_heuristics(
        self,
        packet: TradeReviewPacket,
        is_pre_trade: bool
    ) -> AIReviewResult:
        """
        Autonomous Institutional Quantitative Reasoner.
        Evaluates trade discipline, whale distribution traps, statistical dislocation,
        and execution slippage with strict mathematical rules.
        """
        praises = []
        punishments = []
        revisions = {}
        score = 100
        mult_delta = 0.0

        ticker = packet.ticker.upper().strip()
        strat = packet.strategy.lower().strip()

        is_short = (getattr(packet, "side", "LONG").upper() == "SHORT")
        if is_pre_trade:
            # 1. Whale Distribution Trap Detection (Candidate C Defense)
            is_whale_trap = (packet.rvol >= 1.8 and packet.momentum_5d_pct <= -0.8)
            is_dislocation_scoop = (packet.dislocation_zscore <= -1.8)

            if is_whale_trap:
                if is_short:
                    praises.append("Whale distribution breakdown confirmed for short entry.")
                    score = min(100, score + 5)
                elif strat == "jev_scooper" and is_dislocation_scoop:
                    praises.append("Identified institutional selling capitulation with severe dislocation Z-score. Authorized JEV Scooper.")
                    score = min(100, score + 5)
                else:
                    punishments.append(f"WHALE TRAP DETECTED: RVOL {packet.rvol:.1f}x with negative momentum ({packet.momentum_5d_pct:+.1f}%) signals smart-money distribution into retail liquidity.")
                    score -= 50

            # 2. Volume & Liquidity Quality
            if packet.rvol >= 2.0:
                praises.append(f"High institutional participation confirmed (RVOL {packet.rvol:.1f}x).")
            elif packet.rvol < 0.8:
                punishments.append(f"Low liquidity warning (RVOL {packet.rvol:.2f}x). High spread risk.")
                score -= 25

            # 3. Sentiment & Trend Alignment
            if is_short:
                if packet.sentiment_score > 0.30 and strat in ("core_swing", "ross_momentum"):
                    punishments.append(f"FinBERT sentiment is hostile ({packet.sentiment_score:+.2f}) against short trade.")
                    score -= 30
                elif packet.sentiment_score < -0.20:
                    praises.append(f"FinBERT sentiment confirms bearish catalyst ({packet.sentiment_score:+.2f}).")
            else:
                if packet.sentiment_score < -0.25 and strat in ("core_swing", "ross_momentum"):
                    punishments.append(f"FinBERT sentiment is hostile ({packet.sentiment_score:+.2f}) against long trade.")
                    score -= 30
                elif packet.sentiment_score > 0.20:
                    praises.append(f"FinBERT sentiment confirms bullish catalyst ({packet.sentiment_score:+.2f}).")

            # 4. PSI Stability & Volatility Revision
            if packet.price_stability_index < 35.0:
                revisions["position_size_multiplier"] = 0.70
                revisions["tighten_stop_pct"] = 0.015
                punishments.append(f"Elevated price instability (PSI {packet.price_stability_index:.1f}). Recommended position scale-down to 70%.")
                score -= 15
            else:
                praises.append(f"Laminar price structure (PSI {packet.price_stability_index:.1f}).")

            # Final Pre-Trade Decision
            whale_blocking = (is_whale_trap and not is_short)
            if score >= 80 and not punishments:
                verdict = "APPROVED_PRAISE"
                mult_delta = +0.02
                rule_learned = f"Pre-trade excellence on {ticker}: High-confluence setup passed all institutional gates."
            elif score >= 65 and len(punishments) <= 1 and not whale_blocking:
                verdict = "REVISED_PARAMETERS"
                rule_learned = f"Pre-trade cautious approval on {ticker} with revised risk constraints."
            else:
                verdict = "REJECTED_PUNISH"
                mult_delta = -0.05
                rule_learned = f"Blocked flawed setup on {ticker}: {'; '.join(punishments)}."

        else:
            # Post-trade audit
            pnl = packet.pnl or 0.0
            reason = (packet.exit_reason or "").lower()

            if pnl > 0:
                praises.append(f"Profitable execution (+${pnl:.2f}). Preserved edge and met profit target.")
                mult_delta = +0.02
                score = 95
                verdict = "APPROVED_PRAISE"
                rule_learned = f"Praise {strat} on {ticker}: Clean profit target realized adhering to plan."
            else:
                # Check whether exit honored a disciplined stop
                is_disciplined_stop = (
                    any(k in reason for k in ("stop", "ratchet", "shock", "blackout", "breached"))
                    and "without stop" not in reason
                    and "no stop" not in reason
                    and "panic" not in reason
                )
                if is_disciplined_stop:
                    praises.append(f"Disciplined risk management: Stop loss respected promptly at -${abs(pnl):.2f}. Capital protected.")
                    score = 80
                    mult_delta = +0.005  # Slight reward for disciplined risk defense
                    verdict = "APPROVED_NEUTRAL"
                    rule_learned = f"Compliant defense on {ticker}: Controlled exit preserved capital."
                else:
                    punishments.append(f"Undisciplined exit ({packet.exit_reason}) resulting in avoidable loss (-${abs(pnl):.2f}).")
                    score = 40
                    mult_delta = -0.05
                    verdict = "REJECTED_PUNISH"
                    revisions["cooldown_hours"] = 24
                    rule_learned = f"Punished {strat} on {ticker}: Unplanned exit. 24h ticker cooldown instituted."

            if packet.slippage_bps > 30.0:
                punishments.append(f"High execution slippage ({packet.slippage_bps:.1f} bps). Review limit order routing.")
                score -= 15

        result = AIReviewResult(
            ticker=ticker,
            strategy=strat,
            action="PRE_TRADE_PROPOSAL" if is_pre_trade else "POST_TRADE_CLOSE",
            verdict=verdict,
            compliance_score=max(0, min(100, score)),
            praises=praises,
            punishments=punishments,
            parameter_revisions=revisions,
            rule_learned=rule_learned,
            strategy_multiplier_delta=mult_delta,
            model_source="antigravity-autonomous-heuristics",
            timestamp=time.time(),
        )

        self._record_review(result)
        return result

    def _evaluate_with_gemini(
        self,
        packet: TradeReviewPacket,
        is_pre_trade: bool
    ) -> AIReviewResult:
        """
        Invokes Google GenAI (Gemini) with structured prompt and JSON response format.
        """
        from google import genai
        client = genai.Client()

        prompt = f"""
You are the Chief Risk Officer and Quantitative Strategy Compliance Auditor for an autonomous hedge fund trading system.
Evaluate the following trade dossier with extreme rigor.

Dossier:
- Ticker: {packet.ticker}
- Strategy: {packet.strategy}
- Phase: {'PRE_TRADE_PROPOSAL' if is_pre_trade else 'POST_TRADE_CLOSE'}
- Price: ${packet.price:.2f}
- RVOL: {packet.rvol:.2f}x
- 5-Day Momentum: {packet.momentum_5d_pct:+.2f}%
- FinBERT Sentiment: {packet.sentiment_score:+.2f}
- Price Stability Index (PSI): {packet.price_stability_index:.1f}
- Dislocation Z-Score: {packet.dislocation_zscore:+.2f}
- PnL: {f'${packet.pnl:+.2f}' if packet.pnl is not None else 'N/A'}
- Exit Reason: {packet.exit_reason or 'N/A'}
- Slippage: {packet.slippage_bps:.1f} bps
- Additional Notes: {packet.notes}

Institutional Rules:
1. Candidate C Whale Trap: If RVOL >= 1.8x but 5-day momentum is negative (< -0.8%), reject long momentum breakouts! This is whale distribution. Only JEV Scooper on extreme dislocation (Z <= -1.8) may buy.
2. Risk Discipline: Honor stops. Praise disciplined capital preservation even on minor losses. Severely punish undisciplined chasing or unmanaged exits.
3. Slippage Control: Penalize executions with > 30 bps slippage.

Respond in strict JSON format:
{{
  "verdict": "APPROVED_PRAISE" | "APPROVED_NEUTRAL" | "REVISED_PARAMETERS" | "REJECTED_PUNISH",
  "compliance_score": <int 0-100>,
  "praises": ["<praise point 1>", ...],
  "punishments": ["<punishment point 1>", ...],
  "parameter_revisions": {{"<param_name>": <value>}},
  "rule_learned": "<clear concise rule learned for future runs>",
  "strategy_multiplier_delta": <float between -0.05 and +0.02>
}}
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        data = json.loads(text)
        result = AIReviewResult(
            ticker=packet.ticker.upper().strip(),
            strategy=packet.strategy.lower().strip(),
            action="PRE_TRADE_PROPOSAL" if is_pre_trade else "POST_TRADE_CLOSE",
            verdict=data.get("verdict", "APPROVED_NEUTRAL"),
            compliance_score=int(data.get("compliance_score", 75)),
            praises=list(data.get("praises", [])),
            punishments=list(data.get("punishments", [])),
            parameter_revisions=dict(data.get("parameter_revisions", {})),
            rule_learned=str(data.get("rule_learned", "")),
            strategy_multiplier_delta=float(data.get("strategy_multiplier_delta", 0.0)),
            model_source="gemini-2.5-flash",
            timestamp=time.time(),
        )
        self._record_review(result)
        return result

    def _record_review(self, res: AIReviewResult) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO ai_review_logs (
                ticker, strategy, action, verdict, compliance_score,
                praises, punishments, parameter_revisions, rule_learned,
                multiplier_delta, model_source, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            res.ticker, res.strategy, res.action, res.verdict, res.compliance_score,
            json.dumps(res.praises), json.dumps(res.punishments),
            json.dumps(res.parameter_revisions), res.rule_learned,
            res.strategy_multiplier_delta, res.model_source, res.timestamp
        ))
        conn.commit()
        conn.close()

    def get_recent_reviews(self, limit: int = 15) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("""
            SELECT id, ticker, strategy, action, verdict, compliance_score,
                   praises, punishments, parameter_revisions, rule_learned,
                   multiplier_delta, model_source, timestamp
            FROM ai_review_logs ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "ticker": r[1],
                "strategy": r[2],
                "action": r[3],
                "verdict": r[4],
                "compliance_score": r[5],
                "praises": json.loads(r[6] or "[]"),
                "punishments": json.loads(r[7] or "[]"),
                "parameter_revisions": json.loads(r[8] or "{}"),
                "rule_learned": r[9],
                "multiplier_delta": r[10],
                "model_source": r[11],
                "timestamp": r[12],
                "formatted_time": datetime.fromtimestamp(r[12], tz=NY_TZ).strftime("%Y-%m-%d %H:%M:%S ET")
            })
        return results


ai_reviewer = AIRevisionChecker()
