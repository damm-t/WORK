"""
Composite Trade Quality Scorer (0-100, grades A/B/C)
====================================================
The "is this a smart scoop?" gate. Blends six weighted factors:

    1. FinBERT news conviction      weight 30  (positive adds, negative SUBTRACTS)
    2. Trend: price vs SMA20 proxy  weight 15  (BB middle band)
    3. Momentum: MACD histogram     weight 15
    4. RSI positioning              weight 15  (35-65 sweet spot, <35 dip-zone)
    5. Volatility sanity (ATR%)     weight 15  (dead or chaotic names penalised)
    6. Regime alignment             weight 10  (BULL/CHOP/BEAR multipliers)

Grades:
    A (>=70) -> full size      B (55-69) -> 60% size      C (<55) -> SKIP
"""

import os


def score_trade(sentiment: dict, market: dict, hedge: dict = None) -> dict:
    """Returns {score, grade, size_multiplier, checks[]} for an entry setup."""
    try:
        sentiment = sentiment or {}
        market = market or {}
        hedge = hedge or {}

        label = str(sentiment.get("label", "neutral") or "neutral").lower()
        conf = float(sentiment.get("score", 0.0) or 0.0)
        close = float(market.get("Close", 0.0) or 0.0)
        atr = float(market.get("ATR", 0.0) or 0.0)
        checks = []

        # 1. News conviction (30)
        if label == "positive":
            news_pts = 30.0 * conf
        elif label == "neutral":
            news_pts = 8.0 * conf
        else:
            news_pts = -20.0 * conf
        score = news_pts
        checks.append(f"news {label} {conf:.2f}: {news_pts:+.0f}")

        vol_ratio = float(market.get("Volume_Ratio", 1.0) or 1.0)
        off_hi20 = float(market.get("Off_Hi20_Pct", 0.0) or 0.0)
        rsi = float(market.get("RSI", 50.0) or 50.0)
        is_dip_candidate = (vol_ratio >= 1.15 or market.get("is_high_vol_dip")) and (30.0 <= rsi <= 55.0)

        # 2. Trend vs SMA20 proxy — BB middle band (15)
        mid = market.get("BB_Middle")
        if close > 0 and mid:
            above = close > float(mid)
            if above:
                trend_pts = 15.0
                checks.append("price above SMA20: +15")
            elif is_dip_candidate:
                trend_pts = 12.0
                checks.append(f"high-vol dip at support (vol x{vol_ratio:.1f}, RSI {rsi:.0f}): +12")
            elif market.get("SMA50") and close > float(market.get("SMA50")):
                trend_pts = 5.0
                checks.append("pullback in macro uptrend (above SMA50): +5")
            else:
                trend_pts = -10.0
                checks.append("price below SMA20: -10")
            score += trend_pts

        # 3. Momentum — MACD histogram (15)
        mh = market.get("MACD_Histogram")
        if mh is not None:
            if float(mh) > 0:
                mom_pts = 15.0
                checks.append(f"macd_hist {float(mh):+.3f}: +15")
            elif is_dip_candidate:
                mom_pts = 5.0
                checks.append(f"macd_hist {float(mh):+.3f} (dip accumulation): +5")
            else:
                mom_pts = -12.0
                checks.append(f"macd_hist {float(mh):+.3f}: -12")
            score += mom_pts

        # 4. RSI positioning (15)
        rsi = float(market.get("RSI", 50.0) or 50.0)
        if 35.0 <= rsi <= 65.0:
            rsi_pts = 15.0
        elif rsi < 35.0:
            rsi_pts = 8.0          # oversold dip-buy zone
        else:
            rsi_pts = -12.0        # chasing overbought
        score += rsi_pts
        checks.append(f"rsi {rsi:.0f}: {rsi_pts:+.0f}")

        # 5. Volatility sanity (15)
        atr_pct = (atr / close * 100.0) if (close > 0 and atr > 0) else 0.0
        if 1.0 <= atr_pct <= 6.0:
            vol_pts = 15.0
        elif 0.5 <= atr_pct < 1.0 or 6.0 < atr_pct <= 9.0:
            vol_pts = 7.0
        else:
            vol_pts = -10.0        # dead stock or chaos — bad scoop either way
        score += vol_pts
        checks.append(f"atr% {atr_pct:.1f}: {vol_pts:+.0f}")

        # 6. Regime alignment (10)
        regime = str(hedge.get("regime", "") or "")
        if regime == "BULL_MOMENTUM":
            reg_pts = 10.0
        elif regime == "CHOP_NEUTRAL":
            reg_pts = 5.0
        elif regime == "BEAR_VOLATILITY":
            reg_pts = -5.0
        else:
            reg_pts = 0.0
        score += reg_pts
        checks.append(f"regime {regime or 'n/a'}: {reg_pts:+.0f}")

        # 7. High-Volume Dip / Accumulation bonus (up to +10)
        if vol_ratio >= 1.15 and (-15.0 <= off_hi20 <= -1.5) and 30.0 <= rsi <= 55.0:
            dip_bonus = min(10.0, 5.0 + (vol_ratio - 1.0) * 5.0)
            score += dip_bonus
            checks.append(f"high-vol dip bonus (vol x{vol_ratio:.1f}, {off_hi20:+.1f}% off 20dH): +{dip_bonus:.0f}")

        score = max(0.0, min(100.0, score))
        if score >= 70.0:
            grade, mult = "A", 1.0
        elif score >= 55.0:
            grade, mult = "B", 0.6
        else:
            grade, mult = "C", 0.0

        return {
            "score": round(score, 1),
            "grade": grade,
            "size_multiplier": mult,
            "min_score_threshold": float(os.getenv("MIN_TRADE_SCORE", "55")),
            "checks": checks,
        }
    except Exception as e:
        return {"score": 0.0, "grade": "C", "size_multiplier": 0.0,
                "checks": [], "error": str(e)}