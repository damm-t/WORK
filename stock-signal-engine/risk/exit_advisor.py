"""
Exit Advisor — "I bought at $X … where do I get out?"
=====================================================
Given ANY stock + the user's own entry price, produces:

  • live status verdict   (STOP_ZONE / DRAWDOWN / NEAR_ENTRY / IN_PROFIT /
                           TP1_DONE / RUNNER — measured in ATR units)
  • the full exit ladder  anchored at THE USER'S entry
                          (hard stop · TP1 · runner trigger · trail dist)
  • reachability          median trading-days to each target (√t scaling)
  • 'good exit' prices    cost-floor · conservative(+1ATR) · TP1 · TP2 ·
                          trailing reference · 52w-high stretch
  • context               SMA50 proxy, upside to 52-week high
  • stock analysis        trend score · 1-month base/bull/bear projection ·
                          "is NOW a good price" assessment (risk.stock_analysis)

All math reuses hedging_engine + cost_model — no duplicated formulas.

Usage:
    python -m risk.exit_advisor --ticker NVDA --entry 180 [--shares 5]
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def analyze_exit(ticker: str, entry_price: float,
                 market: Optional[Dict[str, Any]] = None,
                 high_52w: Optional[float] = None,
                 cost_shares: int = 100) -> Dict[str, Any]:
    """
    Analyzes an existing personal position.

    `market` may be injected (unit-tests / pre-fetched features);
    otherwise it is fetched live via market.get_market_features.
    """
    from market import get_market_features                # noqa: E402
    from market.price_fetcher import fetch_prices         # noqa: E402
    from risk.cost_model import breakeven_move_pct        # noqa: E402
    from risk.hedging_engine import (calculate_exit_levels,  # noqa: E402
                                     days_to_target)

    t = str(ticker).upper().strip()
    base: Dict[str, Any] = {"ticker": t, "entry_price": entry_price}

    if entry_price <= 0:
        return {**base, "error": "entry_price must be > 0"}

    try:
        mkt = market if market is not None else get_market_features(t)
    except Exception as e:                                # noqa: BLE001
        return {**base, "error": f"market data failed: {e}"}
    if not mkt or not mkt.get("Close"):
        return {**base, "error": f"no market data for {t}"}

    price = float(mkt["Close"])
    atr = float(mkt.get("ATR", 0.0) or 0.0)
    if atr <= 0:
        return {**base, "error": f"ATR unavailable for {t}"}

    out = {**base, "current_price": round(price, 2),
           "atr": round(atr, 2),
           "daily_atr_pct": round(atr / price * 100.0, 2)}

    # ---- position state measured in ATR units ------------------------------
    dist_atr = (price - float(entry_price)) / atr
    pnl_pct = (price / float(entry_price) - 1.0) * 100.0
    out["pnl_pct"] = round(pnl_pct, 2)
    out["dist_in_atr"] = round(dist_atr, 2)

    if dist_atr <= -1.5:
        status, color = "STOP_ZONE", "bad"
        verdict = ("Price is >1.5 ATR below your entry — the original stop "
                   "thesis is broken. Exit, or consciously re-underwrite "
                   "with a NEW stop level.")
    elif dist_atr <= -0.7:
        status, color = "DRAWDOWN", "warn"
        verdict = ("Meaningful drawdown but inside the noise band. Hold only "
                   "if the entry thesis still holds; otherwise trim into any "
                   "bounce above entry − 1×ATR.")
    elif dist_atr < 0.75:
        status, color = "NEAR_ENTRY", ""
        verdict = ("Hovering around your cost — no edge either way. Hold "
                   "with the hard stop, or redeploy capital elsewhere.")
    elif dist_atr < 2.0:
        status, color = "IN_PROFIT", "good"
        verdict = ("Profit building toward TP1. Hold and prepare to scale "
                   "out half at the TP1 level.")
    elif dist_atr < 3.5:
        status, color = "TP1_DONE", "good"
        verdict = ("TP1 zone reached — scale out half here, let the rest "
                   "run with a 1.5×ATR trail from the highest close.")
    else:
        status, color = "RUNNER", "good"
        verdict = ("Deep in runner territory. Trail 1.5×ATR under the "
                   "highest close and let it work — do NOT add here.")

    out.update({"status": status, "verdict": verdict, "color": color})

    # ---- ladder anchored at the USER's entry --------------------------------
    lv = calculate_exit_levels(float(entry_price), atr)
    out["ladder"] = lv

    # ---- synthesized trade recommendation: [ indicator ] + [ why ] + [ what action ] --
    rec_ind = f"Position Status: {status} (P&L {pnl_pct:+.1f}%, {dist_atr:+.1f}×ATR)"
    rec_why = verdict
    if status == "STOP_ZONE":
        rec_act = f"Cut loss or execute protective stop immediately at ${lv.get('hard_stop_price', 0.0):.2f}. Capital preservation is rule #1."
    elif status == "IN_PROFIT":
        rec_act = f"Hold position toward TP1 (${lv.get('take_profit_1_price', 0.0):.2f}) to scale out 50%. Maintain hard stop at ${lv.get('hard_stop_price', 0.0):.2f}."
    elif status == "TP1_DONE":
        rec_act = f"Scale out 50% if not yet executed. Trail remaining runner with a 1.5×ATR stop under the highest close."
    elif status == "RUNNER":
        rec_act = f"Deep in runner territory. Let the trend work with a trailing stop. Do NOT add new size here."
    elif status == "LOSS_CONTAINED":
        rec_act = f"Monitor closely. Hold only if original thesis stands; otherwise trim into any bounce toward ${entry_price:.2f}."
    else:
        rec_act = f"Maintain position with stop loss active at ${lv.get('hard_stop_price', 0.0):.2f}."

    out["recommendation"] = {
        "indicator": rec_ind,
        "why": rec_why,
        "action": rec_act,
        "paragraph": f"[ Indicator ] {rec_ind}\n[ Why ] {rec_why}\n[ What Action ] {rec_act}",
    }

    # ---- 'good exit' price menu ---------------------------------------------
    out["good_exits"] = {
        "cover_costs_move_pct": breakeven_move_pct(entry_price, cost_shares),
        "conservative_plus_1atr": round(entry_price + atr, 2),
        "tp1_scale_out_50pct": lv.get("take_profit_1_price"),
        "runner_trigger": lv.get("take_profit_2_trigger"),
        "trail_reference_now": round(price - 1.5 * atr, 2),
    }

    # ---- market context -----------------------------------------------------
    ctx: Dict[str, Any] = {}
    sma50_proxy = mkt.get("BB_Middle")
    if sma50_proxy:
        ctx["vs_sma20_proxy"] = ("above" if price > float(sma50_proxy)
                                 else "below")
    df_1y = None
    if high_52w is None:
        try:
            df_1y = fetch_prices(t, period="1y", interval="1d")
            if df_1y is not None and not df_1y.empty:
                high_52w = float(df_1y["Close"].tail(min(len(df_1y), 252)).max())
        except Exception as e:                            # noqa: BLE001
            logger.debug(f"52w lookup {t}: {e}")
    if high_52w:
        up = (float(high_52w) / price - 1.0) * 100.0
        ctx["upside_to_52w_high_pct"] = round(up, 2)
    out["context"] = ctx

    # ---- stock analysis: trend + 1-month projection + entry quality ---------
    try:
        from risk.stock_analysis import analyze_stock     # noqa: E402
        out["stock_analysis"] = analyze_stock(t, df=df_1y)
    except Exception as e:                                # noqa: BLE001
        logger.debug(f"stock analysis {t}: {e}")
        out["stock_analysis"] = None

    return out


if __name__ == "__main__":
    import argparse                                        # noqa: E402
    import json                                            # noqa: E402

    p = argparse.ArgumentParser(description="Exit Advisor")
    p.add_argument("--ticker", required=True)
    p.add_argument("--entry", type=float, required=True)
    p.add_argument("--shares", type=int, default=0)
    a = p.parse_args()

    res = analyze_exit(a.ticker, a.entry)
    if a.shares > 0 and "current_price" in res:
        res["position_pnl_dollars"] = round(
            (res["current_price"] - a.entry) * a.shares, 2)
    print(json.dumps(res, indent=2))