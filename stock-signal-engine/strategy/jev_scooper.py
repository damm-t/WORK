r"""
Joint Expected Value (JEV) Liquidity Scooper Strategy
=====================================================
Active mean-reversion liquidity execution engine for equities and futures.

Inspired by Institutional Liquidity Dislocation & Expected Value Optimization:
  When aggressive institutional liquidations or retail stop runs push an asset's
  market price sharply below its Anti-Volatility Stabilized Price ($P_{\text{stab}}$),
  a temporary liquidity void is created. Once selling volume exhausts, the price
  mean-reverts to its latent equilibrium.

Mathematical Formulation:
--------------------------
1. Dislocation Identification:
   - Residual: $e_t = P_{\text{raw}} - P_{\text{stab}}$
   - Standardized Z-Score: $Z_t = \frac{e_t}{\sigma_{\text{noise}}}$
   - Oversold trigger condition: $Z_t \le -1.8$ (Price pierced below 2-sigma lower noise envelope).

2. Joint Reversion Probability ($P_{\text{rev}}$):
   Modeled jointly across 4 orthogonal dimensions:
     - Dislocation Depth $|Z_t|$ (Capitulation depth)
     - Price Stability Index (PSI) from Anti-Volatility Model (Signal-to-noise quality)
     - Bayesian Belief Confidence ($C_{\text{belief}}$) from Worker 2
     - Volume Exhaustion (RVOL > 1.2)
   $$P_{\text{rev}} = \text{sigmoid}\left( 0.2 + 0.65 \cdot |Z_t| + 0.8 \cdot \frac{\text{PSI}}{100} + 0.5 \cdot \frac{C_{\text{belief}}}{100} + 0.3 \cdot (\text{RVOL} - 1.0) \right)$$
   Clamped into $[0.30, 0.88]$.

3. Joint Expected Value (JEV):
   - Upside Reward: $R_{\text{up}} = P_{\text{stab}} - P_{\text{entry}}$
   - Downside Risk: $R_{\text{down}} = P_{\text{entry}} - P_{\text{stop}}$
   $$JEV = (P_{\text{rev}} \times R_{\text{up}}) - ((1 - P_{\text{rev}}) \times R_{\text{down}})$$
   $$\text{JEV Edge \%} = \frac{JEV}{P_{\text{entry}}} \times 100\%$$

4. Sizing & Capital Allocation:
   - Supports 5% Momentum Satellite (fixed $50 risk atomic bracket)
   - Supports 95% Core Book (Kelly-fractional dip accumulation)
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from market.anti_volatility import anti_volatility_model
from market.technicals import TechnicalIndicators as TI
from model.bayesian_confidence import belief_engine

logger = logging.getLogger(__name__)


@dataclass
class ScoopOpportunity:
    """Quantitative setup flagged by the JEV Liquidity Scooper."""
    ticker: str
    detected_at: float
    current_price: float
    stabilized_price: float
    lower_band: float
    dislocation_zscore: float
    price_stability_index: float
    bayesian_confidence: float
    win_probability_pct: float
    take_profit_target: float
    stop_loss: float
    upside_reward: float
    downside_risk: float
    risk_reward_ratio: float
    jev_dollars: float
    jev_edge_pct: float
    status: str                 # "QUALIFIED_SCOOP", "MONITORING_DIP", "NO_EDGE"
    book_target: str            # "momentum" or "core"
    recommended_shares_50_risk: int
    recommended_notional: float
    rationale: str


class JEVLiquidityScooper:
    """
    Active trading scanner and execution engine computing Joint Expected Value (JEV)
    to scoop temporary liquidity voids.
    """

    def __init__(
        self,
        min_dislocation_zscore: float = -1.5,
        min_win_prob: float = 0.52,
        min_jev_edge_pct: float = 0.8,
        min_rr_ratio: float = 1.2,
    ):
        self.min_dislocation_zscore = min_dislocation_zscore
        self.min_win_prob = min_win_prob
        self.min_jev_edge_pct = min_jev_edge_pct
        self.min_rr_ratio = min_rr_ratio

    def evaluate_ticker(
        self,
        ticker: str,
        df_bars: Optional[pd.DataFrame] = None,
        cost_basis: Optional[float] = None,
    ) -> ScoopOpportunity:
        ticker = ticker.upper().strip()

        # Step 1: Run Anti-Volatility model
        stab_res = anti_volatility_model.evaluate_ticker(ticker, df_bars=df_bars)
        raw_px = stab_res.current_raw_price
        stab_px = stab_res.stabilized_price
        zscore = stab_res.residual_zscore
        psi = stab_res.price_stability_index
        noise_std = max(stab_res.noise_std, raw_px * 0.005)
        lower_band = stab_res.lower_band

        # Step 2: Retrieve Worker 2 Bayesian Belief Confidence
        latest_stmt = belief_engine.get_latest_statement(ticker)
        if latest_stmt:
            bayes_conf = latest_stmt.confidence_pointer
        else:
            bayes_conf = 55.0  # neutral prior

        # Step 3: RVOL calculation
        rvol = 1.0
        if df_bars is not None and "Volume" in df_bars.columns:
            rvol = float(TI.volume_ratio(df_bars["Volume"], length=20))

        # Step 4: Joint Reversion Probability Math
        # Z-score is negative for dips. |zscore| drives capitulation rebound probability.
        abs_z = max(0.0, -zscore) if zscore < 0 else 0.0
        logit = (
            0.15 +
            (0.50 * abs_z) +
            (0.80 * (psi / 100.0)) +
            (0.60 * (bayes_conf / 100.0)) +
            (0.25 * max(0.0, rvol - 1.0))
        )
        p_rev = 1.0 / (1.0 + math.exp(-logit))
        p_rev = float(np.clip(p_rev, 0.30, 0.88))
        win_prob_pct = round(p_rev * 100.0, 1)

        # Step 5: Payoff Bracket Geometry
        # Target is mean-reversion back to the stabilized price
        take_profit = max(round(stab_px, 2), round(raw_px * 1.01, 2))
        upside = max(0.01, round(take_profit - raw_px, 2))

        # Stop loss is placed below the dynamic noise band / support buffer
        stop_dist = max(round(1.5 * noise_std, 2), round(raw_px * 0.02, 2))
        stop_loss = round(raw_px - stop_dist, 2)
        downside = max(0.01, round(raw_px - stop_loss, 2))

        rr_ratio = round(upside / downside, 2) if downside > 0 else 1.0

        # Step 6: Joint Expected Value (JEV)
        # JEV = P(rev) * Reward - P(fail) * Risk
        jev_dollars = round((p_rev * upside) - ((1.0 - p_rev) * downside), 2)
        jev_edge_pct = round((jev_dollars / raw_px) * 100.0, 2)

        # Step 7: Sizing & Routing
        # Default $50 fixed risk for momentum / intraday scoops
        shares_50 = int(50.0 / downside) if downside > 0 else 0
        notional_50 = round(shares_50 * raw_px, 2)

        # Determine target book
        from risk.book_allocator import classify_position_book
        book = classify_position_book(ticker)

        # Step 8: Qualification Decision
        is_qualified = (
            zscore <= self.min_dislocation_zscore and
            p_rev >= self.min_win_prob and
            jev_edge_pct >= self.min_jev_edge_pct and
            rr_ratio >= self.min_rr_ratio
        )

        if is_qualified:
            status = "QUALIFIED_SCOOP"
            rationale = (
                f"🎯 High-JEV Dislocation on {ticker}: Raw price ${raw_px:.2f} is dislocated "
                f"Z={zscore:.2f} below stabilized fair value ${stab_px:.2f}. "
                f"Win probability: {win_prob_pct}%, Expected Edge: +{jev_edge_pct:.2f}%, R:R {rr_ratio}:1."
            )
        elif zscore <= -1.0:
            status = "MONITORING_DIP"
            rationale = (
                f"👀 Mild dislocation on {ticker} (Z={zscore:.2f}). "
                f"JEV Edge: {jev_edge_pct:+.2f}%. Awaiting cleaner exhaustion."
            )
        else:
            status = "NO_EDGE"
            rationale = (
                f"⚖️ {ticker} trading near stabilized equilibrium (${stab_px:.2f}, Z={zscore:.2f}). No scoop edge."
            )

        return ScoopOpportunity(
            ticker=ticker,
            detected_at=time.time(),
            current_price=raw_px,
            stabilized_price=stab_px,
            lower_band=round(lower_band, 2),
            dislocation_zscore=round(zscore, 2),
            price_stability_index=round(psi, 1),
            bayesian_confidence=round(bayes_conf, 1),
            win_probability_pct=win_prob_pct,
            take_profit_target=take_profit,
            stop_loss=stop_loss,
            upside_reward=upside,
            downside_risk=downside,
            risk_reward_ratio=rr_ratio,
            jev_dollars=jev_dollars,
            jev_edge_pct=jev_edge_pct,
            status=status,
            book_target=book,
            recommended_shares_50_risk=shares_50,
            recommended_notional=notional_50,
            rationale=rationale,
        )

    def scan_market(
        self,
        watchlist: Optional[List[str]] = None,
        top_n: int = 6,
    ) -> List[ScoopOpportunity]:
        """
        Scans a basket of equities/tickers and returns ranked JEV scoop opportunities.
        """
        if watchlist is None:
            # High-liquidity active names + momentum watchlist
            from market.low_float_scanner import MOMENTUM_WATCHLIST
            watchlist = ["META", "MSFT", "NVDA", "SPY", "QQQ"] + MOMENTUM_WATCHLIST[:4]

        opportunities = []
        for ticker in watchlist:
            try:
                opp = self.evaluate_ticker(ticker)
                opportunities.append(opp)
            except Exception as e:
                logger.warning(f"Error evaluating JEV for {ticker}: {e}")

        # Rank by JEV Edge % descending
        opportunities.sort(key=lambda o: (o.status == "QUALIFIED_SCOOP", o.jev_edge_pct), reverse=True)
        return opportunities[:top_n]


# Singleton instance
jev_scooper = JEVLiquidityScooper()
