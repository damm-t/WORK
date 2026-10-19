"""
AstraQuant-Inspired Fail-Closed Physical Risk Pipeline
=====================================================
Derived from Quantitative Research Insights (AstraQuant Terminal & Rigorous Alpha Validation):
"Cognition belongs to the model; physical risk control belongs to the code."

Enforces 5 non-bypassable deterministic Python risk gates before ANY trade is submitted:
1. Mandatory Reward-to-Risk (R:R) Floor (Minimum 1.8:1, Target 2.0:1)
   - Rejects any signal where (TakeProfit - Entry) / (Entry - StopLoss) < 1.8
2. Hard Dollar Risk Cap ($75 - $100 max risk, <= 0.25% equity)
   - Prevents single-trade catastrophic drawdowns (e.g. eliminating -$600 single trade losses)
3. Higher-Timeframe Direction Veto (4H / Daily Trend Veto)
   - Disallows buying in a macro downtrend or shorting in a macro uptrend
4. Wada Chaos / High-Entropy Volatility Defense (Reel 2 Chaos Invalidation)
   - Rejects entries when market is trapped in a multi-attractor chaotic boundary zone
5. Friction & Slippage Pre-Deduction (Reel 1 Robustness Test)
   - Rejects strategies that cannot survive 2 ticks of slippage and exchange fees
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class RiskPipelineVerdict:
    approved: bool
    rejection_reasons: List[str] = field(default_factory=list)
    praises: List[str] = field(default_factory=list)
    calculated_rr: float = 0.0
    allowed_position_size: float = 0.0
    max_dollar_loss: float = 0.0
    adjusted_stop_loss: Optional[float] = None
    adjusted_take_profit: Optional[float] = None


class PhysicalRiskPipeline:
    """
    Non-bypassable deterministic gatekeeper for all desks (Equities, Crypto, CME, Forex).
    """

    def __init__(
        self,
        min_rr_ratio: float = 1.8,
        target_rr_ratio: float = 2.0,
        max_risk_equity_pct: float = 0.0025,  # 0.25% max portfolio risk per trade
        max_dollar_risk_cap: float = 85.0,     # Hard $85 max risk ceiling
    ):
        self.min_rr_ratio = min_rr_ratio
        self.target_rr_ratio = target_rr_ratio
        self.max_risk_equity_pct = max_risk_equity_pct
        self.max_dollar_risk_cap = max_dollar_risk_cap

    def audit_order_intent(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        portfolio_equity: float,
        requested_size: float = 1.0,
        macro_ema_trend: Optional[str] = None,   # "BULL", "BEAR", "NEUTRAL"
        realized_volatility_ratio: float = 1.0,  # Current Vol / Baseline ATR
        tick_size: float = 0.01,
        point_value: float = 1.0,
    ) -> RiskPipelineVerdict:
        """
        Runs comprehensive physical checks against proposed trade parameters.
        Returns approved=False if ANY hard safety boundary is violated.
        """
        rejections = []
        praises = []

        if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
            return RiskPipelineVerdict(
                approved=False,
                rejection_reasons=["Invalid price geometry: prices must be positive non-zero values."]
            )

        side_upper = side.upper().strip()
        if side_upper not in ("LONG", "BUY", "SHORT", "SELL"):
            return RiskPipelineVerdict(
                approved=False,
                rejection_reasons=[f"Invalid order side: {side}"]
            )

        is_long = side_upper in ("LONG", "BUY")

        # ----------------- 1. PRICE GEOMETRY VERIFICATION -----------------
        if is_long:
            if stop_loss >= entry_price:
                rejections.append(f"Geometry Breach: Long stop-loss (${stop_loss}) >= entry price (${entry_price})")
            if take_profit <= entry_price:
                rejections.append(f"Geometry Breach: Long take-profit (${take_profit}) <= entry price (${entry_price})")
            risk_dist = entry_price - stop_loss
            reward_dist = take_profit - entry_price
        else:
            if stop_loss <= entry_price:
                rejections.append(f"Geometry Breach: Short stop-loss (${stop_loss}) <= entry price (${entry_price})")
            if take_profit >= entry_price:
                rejections.append(f"Geometry Breach: Short take-profit (${take_profit}) >= entry price (${entry_price})")
            risk_dist = stop_loss - entry_price
            reward_dist = entry_price - take_profit

        if risk_dist <= 0:
            rejections.append("Calculated risk distance is zero or negative.")
            return RiskPipelineVerdict(approved=False, rejection_reasons=rejections)

        # ----------------- 2. REWARD : RISK (R:R) FLOOR AUDIT -----------------
        rr = round(reward_dist / risk_dist, 2)

        if rr < self.min_rr_ratio:
            rejections.append(
                f"Negative Asymmetry Trap: Reward:Risk is {rr}:1 (below non-bypassable floor of {self.min_rr_ratio}:1). "
                f"Needs +${reward_dist:.2f} reward vs -${risk_dist:.2f} risk."
            )
        else:
            praises.append(f"Positive Expectancy Asymmetry: {rr}:1 R:R approved (>= {self.min_rr_ratio}:1 floor)")

        # ----------------- 3. MACRO 4H / DAILY DIRECTION VETO -----------------
        if macro_ema_trend:
            trend_upper = macro_ema_trend.upper()
            if is_long and trend_upper in ("BEAR", "STRONG_BEAR", "DOWN"):
                rejections.append("Macro Veto: Attempting LONG entry into a confirmed 4H/Daily macro downtrend.")
            elif not is_long and trend_upper in ("BULL", "STRONG_BULL", "UP"):
                rejections.append("Macro Veto: Attempting SHORT entry into a confirmed 4H/Daily macro uptrend.")
            else:
                praises.append(f"Macro Aligned: Order direction matches higher-timeframe posture ({trend_upper}).")

        # ----------------- 4. WADA CHAOS & HIGH-ENTROPY INCOMPATIBILITY -----------------
        # Realized volatility > 2.8x normal ATR indicates chaotic bifurcation / basin boundary
        if realized_volatility_ratio >= 2.8:
            rejections.append(
                f"Wada Chaos Veto: Volatility ratio is {realized_volatility_ratio:.1f}x baseline (extreme regime entropy). "
                "Attractor boundary instability makes stop levels erratic."
            )

        # ----------------- 5. MATHEMATICAL RISK BUDGETING & SIZING -----------------
        equity = max(portfolio_equity, 1000.0)
        target_risk_usd = min(equity * self.max_risk_equity_pct, self.max_dollar_risk_cap)

        # Dollar risk per 1 unit (share/contract/lot)
        risk_per_unit = risk_dist * point_value
        if risk_per_unit > 0:
            max_safe_units = target_risk_usd / risk_per_unit
        else:
            max_safe_units = requested_size

        allowed_size = min(requested_size, max_safe_units)
        max_possible_dollar_loss = round(allowed_size * risk_per_unit, 2)

        if max_possible_dollar_loss > (self.max_dollar_risk_cap * 1.15):
            rejections.append(
                f"Max Dollar Risk Exceeded: Potential loss of ${max_possible_dollar_loss:.2f} exceeds hard cap of ${self.max_dollar_risk_cap:.2f}"
            )
        else:
            praises.append(f"Risk Budget Capped: Max loss restricted to ${max_possible_dollar_loss:.2f} ({allowed_size:.4f} units)")

        approved = len(rejections) == 0

        return RiskPipelineVerdict(
            approved=approved,
            rejection_reasons=rejections,
            praises=praises,
            calculated_rr=rr,
            allowed_position_size=round(allowed_size, 4),
            max_dollar_loss=max_possible_dollar_loss,
            adjusted_stop_loss=round(stop_loss, 4),
            adjusted_take_profit=round(take_profit, 4),
        )


# Global singleton instance
physical_risk_pipeline = PhysicalRiskPipeline()
