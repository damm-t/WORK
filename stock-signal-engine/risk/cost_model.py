"""
Transaction-Cost Model & Target Feasibility
===========================================
Answers two questions before every entry:

 1. After fees/spread/slippage, is this trade's profit target actually
    worth it?  (cost-aware expectancy gate)
 2. Statistically, how many days until price plausibly reaches TP?
    (random-walk scaling: median days ~ (target_pct / daily_atr_pct)^2)

Alpaca US equities charge $0 commission, but real micro-costs remain:
    SEC regulatory fee (sells)    ~ 0.00278 % of notional
    FINRA TAF (sells)             ~ $0.000166 / share
    Bid/Ask half-spread           ~ 3 bps per side (liquid large caps)
    Market-order slippage         ~ 4 bps per side
Round trip ~= 0.14-0.16% of notional. Tiny vs an ATR-based TP (>= 2%),
but the viability gate protects quiet, low-volatility names whose targets
sit near the noise floor.
"""

import math
from typing import Optional

# --- Fee / friction constants -------------------------------------------------
SEC_FEE_RATE = 0.0000278           # fraction of SELL notional
TAF_PER_SHARE_SELL = 0.000166      # dollars per share sold
HALF_SPREAD_PCT = 0.0003           # 3 bps per side
SLIPPAGE_PCT_PER_SIDE = 0.0004     # 4 bps per side
MIN_EDGE_MULTIPLE = 5.0            # TP gain must be >= 5x round-trip costs


def round_trip_cost(price: float, shares: int) -> dict:
    """Estimated total friction (in $ and % of notional) for buy+sell."""
    notional = float(price) * int(shares)
    if notional <= 0 or int(shares) <= 0:
        return {"total": 0.0, "pct_of_notional": 0.0}

    buy_costs = notional * (HALF_SPREAD_PCT + SLIPPAGE_PCT_PER_SIDE)
    sell_costs = (notional * (HALF_SPREAD_PCT + SLIPPAGE_PCT_PER_SIDE)
                  + notional * SEC_FEE_RATE
                  + int(shares) * TAF_PER_SHARE_SELL)
    total = buy_costs + sell_costs
    return {
        "total": round(total, 4),
        "pct_of_notional": round(total / notional * 100.0, 4),
    }


def breakeven_move_pct(price: float, shares: int) -> float:
    """Minimum % price move needed just to cover round-trip costs (%)."""
    return round_trip_cost(price, shares)["pct_of_notional"]


def is_trade_viable(entry_price: float, target_price: float, stop_price: float,
                    shares: int, min_edge_multiple: float = MIN_EDGE_MULTIPLE) -> dict:
    """
    Veto gate: the TP move must clear round-trip costs by `min_edge_multiple`,
    and reward:risk must be >= 1.0 AFTER costs.
    """
    gain_pct = (float(target_price) - float(entry_price)) / float(entry_price)
    risk_pct = (float(entry_price) - float(stop_price)) / float(entry_price)
    if gain_pct <= 0 or risk_pct <= 0:
        return {"viable": False, "reason": "invalid target/stop levels"}

    cost = round_trip_cost(entry_price, shares)
    cost_pct = cost["pct_of_notional"] / 100.0
    required_gain_pct = cost_pct * min_edge_multiple
    reward_risk = gain_pct / risk_pct

    viable = gain_pct >= required_gain_pct and reward_risk >= 1.0
    return {
        "viable": viable,
        "gain_pct": round(gain_pct * 100, 3),
        "risk_pct": round(risk_pct * 100, 3),
        "reward_risk": round(reward_risk, 2),
        "round_trip_cost_usd": cost["total"],
        "required_gain_pct": round(required_gain_pct * 100, 3),
        "reason": (
            f"Viable: TP {gain_pct*100:.2f}% >> costs {cost_pct*100:.3f}% "
            f"x{min_edge_multiple:.0f}, R:R {reward_risk:.2f}"
        ) if viable else (
            f"Not viable: TP {gain_pct*100:.2f}% below required "
            f"{required_gain_pct*100:.2f}% (costs x{min_edge_multiple:.0f})"
        ),
    }


def days_to_target(entry_price: float, target_price: float, atr: float) -> Optional[float]:
    """
    Median number of TRADING DAYS for price to wander to `target_price`,
    assuming moves scale with sqrt(time) (standard random-walk scaling).
    This tells you HOW FAST your TP is realistically reachable.
    """
    atr_pct = float(atr) / float(entry_price) if entry_price > 0 else 0.0
    tgt_pct = (float(target_price) - float(entry_price)) / float(entry_price)
    if atr_pct <= 0 or tgt_pct <= 0:
        return None
    return round((tgt_pct / atr_pct) ** 2, 1)


def expected_move_pct(atr: float, entry_price: float, days: int = 5) -> float:
    """Statistically expected absolute move (%) over `days`, in percent."""
    if entry_price <= 0 or atr <= 0 or days <= 0:
        return 0.0
    return (float(atr) / float(entry_price)) * math.sqrt(days) * 100.0