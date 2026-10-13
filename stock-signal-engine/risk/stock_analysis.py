"""
Stock Analysis — trend read + 1-month confident-price projection
================================================================
Answers, for ANY ticker, the three questions the Exit Advisor panel shows:

  1. HOW is the trend?          5-signal score (−5…+5): price vs SMA20/SMA50,
                                SMA20 vs SMA50 cross, MACD vs signal,
                                20-day momentum  → UPTREND / DOWNTREND / CHOP
  2. Where is it likely to go   base / bull(+) / bear(−) prices over ~21
     in 1 month?                trading days, using the repo's √t random-walk
                                scaling (risk.cost_model.expected_move_pct)
                                tilted by the trend score (drift).
  3. Is NOW a good price?       vs SMA20, RSI-14, % of 52-week range, plus the
                                pullback zone (SMA20) and deep-value zone (SMA50).

All indicator math routes through TechnicalIndicators (market/technicals.py)
— the single source of truth — and the projection reuses cost_model, so no
duplicated formulas.

Usage:
    python -m risk.stock_analysis --ticker NVDA
"""

import logging
from typing import Any, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)

_MIN_ROWS = 60          # SMA50 needs 50 bars + momentum needs 21
_HORIZON_DAYS = 21      # ~1 month of trading days
_CONFIDENCE_PCT = 68    # ±1σ band under a normal approximation


def _verdict(bullish: bool, neutral: bool = False) -> str:
    if neutral:
        return "neutral"
    return "bullish" if bullish else "bearish"


def _fmt_pct(value: float) -> str:
    return f"{value:+.1f}%"

# ------------------------------------------------------------------- trend --
def _analyze_trend(close: pd.Series) -> Dict[str, Any]:
    """5-signal trend score in [−5, +5] → {direction,label,score,max,summary,signals}."""
    from market.technicals import TechnicalIndicators     # noqa: E402

    price = float(close.iloc[-1])
    sma20 = float(TechnicalIndicators.sma(close, 20).iloc[-1])
    sma50 = float(TechnicalIndicators.sma(close, 50).iloc[-1])
    macd_line, signal_line = TechnicalIndicators.macd(close)
    hist = float(macd_line.iloc[-1]) - float(signal_line.iloc[-1])
    mom_pct = (price / float(close.iloc[-21]) - 1.0) * 100.0   # 20 sessions back

    signals: Dict[str, Dict[str, str]] = {}
    score = 0

    def add(key: str, bullish: Optional[bool], value: str,
            indicator: str, why: str, action: str) -> None:
        nonlocal score
        v = _verdict(bool(bullish), neutral=(bullish is None))
        if v == "bullish":
            score += 1
        elif v == "bearish":
            score -= 1
        signals[key] = {
            "verdict": v,
            "value": value,
            "indicator": indicator,
            "why": why,
            "action": action,
        }

    # 1. Price vs SMA20
    s20_pct = (price / sma20 - 1.0) * 100.0 if sma20 > 0 else 0.0
    s20_why = (f"Price is {s20_pct:+.1f}% vs 20-day SMA (${sma20:.2f})" +
               (" — extended above short-term mean, increasing pullback risk."
                if s20_pct >= 5.0 else
                " — holding firmly above short-term trendline." if s20_pct > 0 else
                " — trading below short-term trendline, showing short-term weakness."))
    s20_act = (f"Wait for pullback near SMA20 (${sma20:.2f}) before entering; do not chase."
               if s20_pct >= 5.0 else
               f"Use SMA20 (${sma20:.2f}) as dynamic support for dip buying." if s20_pct > 0 else
               f"Wait for reclaim above SMA20 (${sma20:.2f}) before adding size.")
    add("price_vs_sma20", None if price == sma20 else price > sma20,
        _fmt_pct(s20_pct), "Price vs SMA20", s20_why, s20_act)

    # 2. Price vs SMA50
    s50_pct = (price / sma50 - 1.0) * 100.0 if sma50 > 0 else 0.0
    s50_why = (f"Price is {s50_pct:+.1f}% vs 50-day SMA (${sma50:.2f}) — " +
               ("holding above confirms multi-month institutional uptrend."
                if s50_pct > 0 else "trading below indicates intermediate trend pressure."))
    s50_act = (f"Treat SMA50 (${sma50:.2f}) as the deep value support zone."
               if s50_pct > 0 else
               f"Expect overhead resistance near SMA50 (${sma50:.2f}); manage risk.")
    add("price_vs_sma50", None if price == sma50 else price > sma50,
        _fmt_pct(s50_pct), "Price vs SMA50", s50_why, s50_act)

    # 3. SMA20 vs SMA50
    ma_cross_pct = (sma20 / sma50 - 1.0) * 100.0 if sma50 > 0 else 0.0
    ma_why = (f"Fast SMA20 (${sma20:.2f}) is {ma_cross_pct:+.1f}% vs slow SMA50 (${sma50:.2f}) — " +
              ("bullish moving average alignment confirms upward intermediate momentum."
               if sma20 > sma50 else "bearish alignment signals intermediate downtrend structure."))
    ma_act = ("Favor buying dips on constructive pullbacks; avoid shorting the trend."
              if sma20 > sma50 else "Exercise defensive posture; wait for moving average repair.")
    add("sma20_vs_sma50", None if sma20 == sma50 else sma20 > sma50,
        _fmt_pct(ma_cross_pct), "SMA20 vs SMA50 (Trend Cross)", ma_why, ma_act)

    # 4. MACD vs Signal
    macd_why = (f"MACD histogram is {hist:+.2f} — " +
                ("positive histogram indicates expanding buyer momentum."
                 if hist > 0 else "negative or fading histogram indicates momentum deceleration."))
    macd_act = ("Allow winning positions to run; use trailing stops to lock gains."
                if hist > 0 else "Tighten trailing stops; avoid initiating breakout buys without fresh momentum.")
    add("macd_vs_signal",
        None if abs(hist) < 0.0005 * price else hist > 0,
        f"{hist:+.2f}", "MACD vs Signal", macd_why, macd_act)

    # 5. Momentum 20d
    mom_why = (f"20-session rate of change is {mom_pct:+.1f}% — " +
               ("positive monthly price velocity confirms buyer tailwind."
                if mom_pct > 0 else "negative price velocity indicates monthly net selling."))
    mom_act = ("Align trade direction with the monthly trend tailwind."
               if mom_pct > 0 else "Wait for monthly velocity to turn positive before sizing up.")
    add("momentum_20d", None if abs(mom_pct) < 1.0 else mom_pct > 0,
        _fmt_pct(mom_pct), "20-Day Momentum", mom_why, mom_act)

    if score >= 2:
        direction, label = "up", "UPTREND"
        overall_action = "Trend is bullish. Favor long dip entries near SMA20 and let runners work."
    elif score <= -2:
        direction, label = "down", "DOWNTREND"
        overall_action = "Trend is bearish. Avoid fresh long exposure; honor hard stops strictly."
    else:
        direction, label = "flat", "CHOP"
        overall_action = "Price is rangebound / chopping. Reduce position sizing and avoid breakout chasing."

    bull = sum(1 for s in signals.values() if s["verdict"] == "bullish")
    bear = sum(1 for s in signals.values() if s["verdict"] == "bearish")
    if direction == "up":
        summary = (f"{bull}/5 signals bullish — price holds above its key moving "
                   f"averages and momentum confirms")
    elif direction == "down":
        summary = (f"{bear}/5 signals bearish — price trades under its key moving "
                   f"averages and momentum is negative")
    else:
        summary = "signals disagree — no dominant trend, price is chopping"

    return {
        "direction": direction,
        "label": label,
        "score": score,
        "max": 5,
        "summary": summary,
        "signals": signals,
        "indicator": f"Trend Score ({score:+d}/5 · {label})",
        "why": summary,
        "action": overall_action,
    }

# ------------------------------------------------------- 1-month projection --
def _project_1m(price: float, atr: float, trend_score: int) -> Dict[str, Any]:
    """
    1-month (~21 trading-day) scenario band using the repo's √t random-walk
    scaling (risk.cost_model.expected_move_pct), tilted by the trend score:

        sigma_move_pct = ATR% · √21                    → ±1σ ≈ 68% band
        drift_pct      = (score / 5) · 0.5 · sigma    → capped half-sigma tilt

        bear = price·(1 + (drift−σ)/100)   base = price·(1 + drift/100)
        bull = price·(1 + (drift+σ)/100)
    """
    from risk.cost_model import expected_move_pct      # noqa: E402

    sigma = expected_move_pct(atr, price, days=_HORIZON_DAYS)
    if sigma <= 0:
        return {}
    drift = round((trend_score / 5.0) * 0.5 * sigma, 2)
    return {
        "days": _HORIZON_DAYS,
        "sigma_move_pct": round(sigma, 2),
        "drift_pct": drift,
        "bear": round(price * (1.0 + (drift - sigma) / 100.0), 2),
        "base": round(price * (1.0 + drift / 100.0), 2),
        "bull": round(price * (1.0 + (drift + sigma) / 100.0), 2),
        "confidence_pct": _CONFIDENCE_PCT,
        "note": "ATR·√t random-walk band, drift-tilted by the trend score",
    }


# ------------------------------------------------------ entry quality read ---
def _assess_entry(close: pd.Series) -> Dict[str, Any]:
    """
    "Is NOW a good price (to buy)?" — where price sits inside its own structure:

      good   back at/near the SMA20 pullback zone, RSI not overheated, and not
             pinned at 52-week highs  → buying weakness, not the chase
      poor   extended ≥ +6% over SMA20, or RSI ≥ 72, or ≥ 92% of 52w range
      fair   everything in between
    """
    from market.technicals import TechnicalIndicators   # noqa: E402

    price = float(close.iloc[-1])
    sma20 = float(TechnicalIndicators.sma(close, 20).iloc[-1])
    sma50 = float(TechnicalIndicators.sma(close, 50).iloc[-1])
    rsi14 = float(TechnicalIndicators.rsi(close, 14).iloc[-1])

    win = close.tail(min(len(close), 252))
    low_52w, high_52w = float(win.min()), float(win.max())
    span = high_52w - low_52w
    pct_range = (price - low_52w) / span * 100.0 if span > 0 else 50.0
    vs_sma20 = (price / sma20 - 1.0) * 100.0 if sma20 > 0 else 0.0

    indicator = (f"Price vs SMA20 ({vs_sma20:+.1f}%) · RSI-14 ({rsi14:.1f}) · "
                 f"52w Range ({pct_range:.1f}%)")

    if vs_sma20 <= 2.0 and rsi14 < 62.0 and pct_range <= 75.0:
        quality = "good"
        verdict = ("Sitting at/near the pullback zone (SMA20) with cooled "
                   "momentum — historically the better entry area, not the chase.")
        why = (f"Price is sitting just {vs_sma20:+.1f}% from the SMA20 pullback zone (${sma20:.2f}) "
               f"with cooled momentum (RSI {rsi14:.1f}) and moderate 52-week positioning ({pct_range:.1f}%). "
               f"Entering here offers favorable risk/reward without buying at an exhausted top.")
        action = (f"Favorable entry area: look for long entries near the SMA20 pullback zone (${sma20:.2f}) "
                  f"with a stop loss placed below deep value (${sma50:.2f}).")
    elif vs_sma20 >= 6.0 or rsi14 >= 72.0 or pct_range >= 92.0:
        quality = "poor"
        verdict = ("Extended above its moving average / momentum is hot — "
                   "chasing here risks buying the top of the band; wait for "
                   "a pullback toward SMA20.")
        triggers = []
        if vs_sma20 >= 6.0:
            triggers.append(f"extended {vs_sma20:+.1f}% above SMA20 (${sma20:.2f})")
        if rsi14 >= 72.0:
            triggers.append(f"overbought RSI ({rsi14:.1f})")
        if pct_range >= 92.0:
            triggers.append(f"pinned at {pct_range:.1f}% of 52-week high (${high_52w:.2f})")
        trigger_str = ", ".join(triggers) if triggers else "momentum is overheated"
        why = (f"Price is {trigger_str}. Chasing here risks buying the upper boundary of the "
               f"volatility band right before a mean-reverting pullback.")
        action = (f"Do NOT chase at market price (${price:.2f}). Wait for a pullback toward the "
                  f"SMA20 zone (${sma20:.2f}) or deep value (${sma50:.2f}). If holding, maintain tight stops.")
    else:
        quality = "fair"
        verdict = ("Mid-structure: neither a discount nor overheated. "
                   "Scaling in is reasonable; full size wants a dip.")
        why = (f"Price is at {pct_range:.1f}% of 52-week range, {vs_sma20:+.1f}% vs SMA20, and RSI is {rsi14:.1f}. "
               f"Market structure is balanced: neither an oversold bargain nor severely overextended.")
        action = (f"Scale in cautiously with 1/3 to 1/2 normal position size. Keep remaining dry powder "
                  f"ready to buy dips toward the SMA20 pullback zone (${sma20:.2f}).")

    reasoning_paragraph = (f"[ Indicator ] {indicator}\n"
                           f"[ Why ] {why}\n"
                           f"[ What Action ] {action}")

    return {
        "quality": quality,
        "verdict": verdict,
        "vs_sma20_pct": round(vs_sma20, 2),
        "rsi_14": round(rsi14, 1),
        "pct_of_52w_range": round(pct_range, 1),
        "low_52w": round(low_52w, 2),
        "high_52w": round(high_52w, 2),
        "pullback_zone": round(sma20, 2),
        "deep_value_zone": round(sma50, 2),
        "indicator": indicator,
        "why": why,
        "action": action,
        "reasoning_paragraph": reasoning_paragraph,
    }


# ------------------------------------------------------------------ public ----
def analyze_stock(ticker: str,
                  df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Full stock-analysis block for the Exit Advisor panel:
        {trend, projection_1m, entry_assessment}
    `df` (1y daily OHLCV) may be injected by the caller to avoid a re-fetch;
    otherwise it is fetched live via market.price_fetcher.fetch_prices.
    """
    from market.price_fetcher import fetch_prices       # noqa: E402
    from market.technicals import TechnicalIndicators   # noqa: E402

    t = str(ticker).upper().strip()
    err = {"ticker": t}

    if df is None or len(df) < _MIN_ROWS:
        try:
            df = fetch_prices(t, period="1y", interval="1d")
        except Exception as e:                            # noqa: BLE001
            return {**err, "error": f"price history failed: {e}"}
    if df is None or len(df) < _MIN_ROWS or "Close" not in df.columns:
        return {**err, "error": f"need ≥{_MIN_ROWS} bars of history for {t}"}

    close = df["Close"].dropna()
    if len(close) < _MIN_ROWS:
        return {**err, "error": f"need ≥{_MIN_ROWS} close bars for {t}"}

    price = float(close.iloc[-1])
    has_ohlc = {"High", "Low"} <= set(map(str, df.columns))
    atr = float(TechnicalIndicators.atr(df, 14).iloc[-1]) if has_ohlc else 0.0

    out: Dict[str, Any] = {
        "ticker": t,
        "price": round(price, 2),
        "trend": _analyze_trend(close),
    }
    out["projection_1m"] = (
        _project_1m(price, atr, int(out["trend"]["score"])) if atr > 0 else {})
    out["entry_assessment"] = _assess_entry(close)
    return out


if __name__ == "__main__":
    import argparse                                     # noqa: E402
    import json                                         # noqa: E402

    p = argparse.ArgumentParser(
        description="Stock Analysis — trend + 1-month projection + entry quality")
    p.add_argument("--ticker", required=True)
    a = p.parse_args()

    print(json.dumps(analyze_stock(a.ticker), indent=2))
