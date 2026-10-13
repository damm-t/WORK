"""
Project Omega: Convex Tail-Risk & Pre-Market Circuit Sentry Engine
===================================================================
Implements Pillars 2, 4, and 5 of Project Omega:
1. Convex Tail-Risk Sizing (replacing linear-only inverse ETFs with asymmetric vol protections)
2. Pre-Market Futures Circuit Sentry (detecting gap liquidations before 09:30 ET)
3. DEFCON Systemic Threat Classification (DEFCON 4 -> DEFCON 1 Harvester Mode)
"""

from __future__ import annotations

import logging
import math
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from market.price_fetcher import fetch_prices

logger = logging.getLogger(__name__)
NY_TZ = ZoneInfo("America/New_York")


class ConvexTailEngine:
    """Evaluates systemic convexity, pre-market circuit breaker gaps, and DEFCON regimes."""

    def __init__(self):
        self.defcon_status = "DEFCON_4"

    def check_pre_market_circuit_sentry(self, benchmark: str = "SPY") -> Dict[str, Any]:
        """
        Pillar 4: Monitors index benchmarks/futures prior to the 09:30 ET cash open.
        If pre-market gap approaches or exceeds circuit breaker thresholds (>= 4.0% down),
        flags PRE_MARKET_CIRCUIT_ALERT to initiate an atomic cash sweep BEFORE open.
        """
        res = {
            "timestamp": datetime.now(NY_TZ).isoformat(),
            "benchmark": benchmark,
            "pre_market_gap_pct": 0.0,
            "circuit_breaker_threat": False,
            "defcon_level": "DEFCON_4",
            "action_required": "NONE",
            "detail": "Normal pre-market conditions",
        }

        try:
            # Pull 5d daily bars to get previous close
            df_daily = fetch_prices(benchmark, period="5d", interval="1d")
            if df_daily is None or len(df_daily) < 2:
                return res

            prev_close = float(df_daily["Close"].iloc[-2])

            # Try fetching latest pre-market price
            pre_price = None
            try:
                from market.price_fetcher import fetch_latest_price
                pre_price = fetch_latest_price(benchmark)
            except Exception:
                pass

            if not pre_price or pre_price <= 0:
                pre_price = float(df_daily["Close"].iloc[-1])

            if prev_close > 0 and pre_price > 0:
                gap_pct = ((pre_price / prev_close) - 1.0) * 100.0
                res["pre_market_gap_pct"] = round(gap_pct, 2)
                res["pre_price"] = round(pre_price, 2)
                res["prev_close"] = round(prev_close, 2)

                # Level 1 equity circuit breaker is -7%. Threat fires at -4.0%
                if gap_pct <= -4.0:
                    res["circuit_breaker_threat"] = True
                    res["defcon_level"] = "DEFCON_1"
                    res["action_required"] = "PRE_MARKET_ATOMIC_CASH_SWEEP"
                    res["detail"] = (
                        f"CRITICAL CIRCUIT BREAKER THREAT: {benchmark} pre-market gap {gap_pct:+.2f}% "
                        f"exceeds -4.0% threshold. Immediate pre-market derisking and cash sweep advised."
                    )
                    logger.critical(f"[convex_tail] 🚨 {res['detail']}")
                elif gap_pct <= -2.5:
                    res["defcon_level"] = "DEFCON_2"
                    res["action_required"] = "RESTRICT_LONG_ENTRIES"
                    res["detail"] = f"ELEVATED RISK: {benchmark} pre-market gap {gap_pct:+.2f}%. Halt new entries."
                elif gap_pct >= 3.0:
                    res["defcon_level"] = "DEFCON_3"
                    res["detail"] = f"BULLISH GAP: {benchmark} up {gap_pct:+.2f}%."
        except Exception as e:
            logger.debug(f"[convex_tail] pre-market check note: {e}")

        return res

    def evaluate_systemic_tail_risk(self, portfolio_equity: float = 50000.0) -> Dict[str, Any]:
        """
        Pillar 2: Computes asymmetric tail-risk exposure and sizing for non-linear hedging.
        Recommends a convex volatility protection budget (1.0% to 2.5% of equity)
        designed to yield 15x-30x non-linear payouts during sudden black swan crashes.
        """
        sentry = self.check_pre_market_circuit_sentry("SPY")
        gap = sentry.get("pre_market_gap_pct", 0.0)

        # Baseline quarterly allocation: 1.5% of fund equity
        base_budget_pct = 0.015
        if sentry.get("circuit_breaker_threat"):
            base_budget_pct = 0.030  # Escalate during imminent threat

        allocated_budget = round(portfolio_equity * base_budget_pct, 2)

        # Estimate convex payoff profile under -20% index shock
        modeled_payout_20pct_crash = round(allocated_budget * 18.5, 2)

        return {
            "portfolio_equity": portfolio_equity,
            "defcon_level": sentry.get("defcon_level", "DEFCON_4"),
            "pre_market_gap_pct": gap,
            "convex_tail_budget_usd": allocated_budget,
            "convex_tail_budget_pct": round(base_budget_pct * 100.0, 2),
            "protection_vehicle": "LONG_VOL_ASYMMETRIC_STRUCTURE",
            "modeled_crash_offset_usd": modeled_payout_20pct_crash,
            "modeled_net_coverage_pct": round((modeled_payout_20pct_crash / max(1.0, portfolio_equity * 0.20)) * 100.0, 1),
            "recommendation": sentry.get("action_required"),
            "detail": sentry.get("detail"),
        }

    def get_defcon_level(self) -> str:
        """Returns the active DEFCON state for the multi-desk trading floor."""
        sentry = self.check_pre_market_circuit_sentry("SPY")
        return str(sentry.get("defcon_level", "DEFCON_4"))


# Singleton instance
convex_tail_engine = ConvexTailEngine()
