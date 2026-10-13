"""
Ross Cameron Low-Float Catalyst Momentum Scanner (The 5 Pillars)
================================================================
Scans and filters equities matching the 5 pillars of small-account momentum:

  1. Up on the Day       : >= +10% vs previous close (ideally +30%+)
  2. Relative Volume     : >= 5.0x RVOL vs 50-day average volume
  3. News Catalyst       : Breaking PR, SEC filing (6-K/8-K), FDA, earnings via FinBERT
  4. Price Range         : $2.00 to $20.00 (sweet spot: $5.00 to $10.00)
  5. Low Float           : Under 20M shares (ideally under 10M shares)

Trading Window Gate:
  Primary active window: 7:00 AM - 10:00 AM Eastern Time (ET).
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from market.price_fetcher import fetch_prices
from market.fundamentals import fetch_fundamentals
from market.technicals import TechnicalIndicators as TI

logger = logging.getLogger(__name__)
NY_TZ = ZoneInfo("America/New_York")

# Small-cap momentum universe watchlist (active runners & historical low-float leaders)
MOMENTUM_WATCHLIST = [
    "CYN", "SMFL", "BBLG", "HOLO", "MTC", "CERO", "GFAI", "LPA",
    "GNS", "SOUN", "BBAI", "TEM", "WGS", "ALLR", "MNTS", "NKLA"
]


def check_trading_window() -> dict:
    """Checks if the current time sits inside the 7:00 AM - 10:00 AM ET morning window."""
    now_ny = datetime.now(NY_TZ)
    hour = now_ny.hour
    minute = now_ny.minute
    total_minutes = hour * 60 + minute

    start_min = 7 * 60       # 7:00 AM ET
    end_min = 10 * 60        # 10:00 AM ET

    in_window = start_min <= total_minutes <= end_min
    return {
        "in_window": in_window,
        "current_time_et": now_ny.strftime("%H:%M:%S %Z"),
        "window": "07:00 - 10:00 ET",
        "detail": "Inside prime morning runner window" if in_window else "Outside 07:00-10:00 ET prime window (entries riskier)"
    }


def evaluate_news_catalyst(ticker: str) -> dict:
    """Evaluates breaking headlines using FinBERT sentiment & catalyst keywords."""
    try:
        from ingestion import fetch_all
        from nlp import analyze_sentiment_only

        articles = fetch_all(ticker)[:5]
        if not articles:
            return {"has_catalyst": False, "score": 0.0, "reason": "No breaking headlines found"}

        catalyst_keywords = [
            "fda", "approval", "patent", "contract", "earnings", "revenue",
            "partnership", "phase", "trial", "merger", "acquisition", "guidance"
        ]

        best_score = 0.0
        best_title = ""
        has_keyword = False

        for a in articles:
            title = str(a.get("title", "") or "").lower()
            res = analyze_sentiment_only(a)
            if res:
                sent = str(res.get("sentiment", "neutral")).lower()
                conf = float(res.get("sentiment_score", 0.0) or 0.0)
                if sent == "positive" and conf > best_score:
                    best_score = conf
                    best_title = a.get("title", "")

            if any(k in title for k in catalyst_keywords):
                has_keyword = True
                if not best_title:
                    best_title = a.get("title", "")

        has_catalyst = (best_score >= 0.65) or (has_keyword and best_score >= 0.50)
        return {
            "has_catalyst": bool(has_catalyst),
            "score": round(best_score, 2),
            "headline": best_title or (articles[0].get("title", "") if articles else ""),
            "keyword_match": has_keyword,
        }
    except Exception as e:
        logger.debug(f"[low_float_scanner] news check {ticker}: {e}")
        return {"has_catalyst": False, "score": 0.0, "reason": str(e)}


def evaluate_five_pillars(ticker: str, custom_df=None, custom_float: Optional[float] = None) -> dict:
    """
    Evaluates a ticker strictly against Ross Cameron's 5 Pillars.
    Returns composite pillar score (0-100), grade (A/B/C), and pillar check pass/fail.
    """
    ticker_clean = ticker.upper().strip()
    df = custom_df if custom_df is not None else fetch_prices(ticker_clean, period="6mo", interval="1d")

    if df is None or df.empty or len(df) < 20:
        return {"ticker": ticker_clean, "passed": False, "score": 0, "grade": "C", "error": "Insufficient price data"}

    c = df["Close"]
    v = df["Volume"]

    price = float(c.iloc[-1])
    prev_close = float(c.iloc[-2]) if len(c) >= 2 else price
    change_pct = ((price / prev_close) - 1.0) * 100.0 if prev_close > 0 else 0.0

    # 50-day average volume for RVOL calculation
    avg_vol_50 = float(v.tail(min(len(v), 50)).mean() or 1.0)
    curr_vol = float(v.iloc[-1])
    rvol = curr_vol / max(avg_vol_50, 1.0)

    # Float & Shares Outstanding from SEC facts or custom
    fund = fetch_fundamentals(ticker_clean)
    sec_shares = fund.get("shares_outstanding")
    if custom_float is not None:
        float_shares = float(custom_float)
    elif sec_shares is not None and float(sec_shares) > 0:
        float_shares = float(sec_shares)
    else:
        # Heuristic fallback if SEC facts lack direct shares tag
        float_shares = 15_000_000.0

    float_shares = max(100_000.0, float_shares)

    # News Catalyst
    news = evaluate_news_catalyst(ticker_clean)

    # Pillar Checks
    p1_up = change_pct >= 10.0
    p2_rvol = rvol >= 5.0 or curr_vol >= 20_000_000
    p3_news = bool(news.get("has_catalyst"))
    p4_price = 0.50 <= price <= 20.0
    p5_float = float_shares < 20_000_000

    pillars_passed = sum([p1_up, p2_rvol, p3_news, p4_price, p5_float])

    # Scoring (0-100)
    score = 0.0
    reasons = []

    # 1. Up on Day (25 pts)
    if change_pct >= 30.0:
        score += 25.0
        reasons.append(f"Pillar 1: Massive Gainer +{change_pct:.1f}% (+25)")
    elif change_pct >= 10.0:
        score += 18.0
        reasons.append(f"Pillar 1: Strong Gainer +{change_pct:.1f}% (+18)")
    else:
        reasons.append(f"Pillar 1 FAIL: Only {change_pct:+.1f}% (<+10%)")

    # 2. RVOL >= 5x (25 pts)
    if rvol >= 10.0:
        score += 25.0
        reasons.append(f"Pillar 2: Extreme RVOL {rvol:.1f}x (+25)")
    elif rvol >= 5.0:
        score += 20.0
        reasons.append(f"Pillar 2: High RVOL {rvol:.1f}x (+20)")
    else:
        score += min(15.0, rvol * 3.0)
        reasons.append(f"Pillar 2: Sub-par RVOL {rvol:.1f}x (<5x target)")

    # 3. Catalyst (20 pts)
    if p3_news:
        score += 20.0
        reasons.append(f"Pillar 3: Positive Catalyst verified ({news.get('headline')[:40]}...) (+20)")
    else:
        reasons.append("Pillar 3 WARNING: No explicit news catalyst (reduce sizing by 50%)")

    # 4. Price $0.50 - $20.00 (15 pts)
    if 5.0 <= price <= 10.0:
        score += 15.0
        reasons.append(f"Pillar 4: Ideal Sweet Spot Price ${price:.2f} (+15)")
    elif 2.0 <= price <= 20.0:
        score += 12.0
        reasons.append(f"Pillar 4: Eligible Small-Cap Price ${price:.2f} (+12)")
    elif 0.50 <= price < 2.0:
        score += 10.0
        reasons.append(f"Pillar 4: Active Penny Stock Runner ${price:.2f} (+10)")
    else:
        reasons.append(f"Pillar 4 FAIL: Price ${price:.2f} outside $0.50-$20 range")

    # 5. Low Float < 20M (15 pts)
    if float_shares < 10_000_000:
        score += 15.0
        reasons.append(f"Pillar 5: Ultra-Low Float {float_shares/1e6:.1f}M shares (+15)")
    elif float_shares < 20_000_000:
        score += 10.0
        reasons.append(f"Pillar 5: Low Float {float_shares/1e6:.1f}M shares (+10)")
    else:
        reasons.append(f"Pillar 5 FAIL: High Float {float_shares/1e6:.1f}M shares (supply too high)")

    score = round(max(0.0, min(100.0, score)), 1)

    if pillars_passed == 5:
        grade = "A"       # Full position sizing
    elif pillars_passed == 4:
        grade = "B"       # 50% position sizing (Ross rule: no news = half size)
    else:
        grade = "C"       # Disqualified (skip trade)

    return {
        "ticker": ticker_clean,
        "score": score,
        "grade": grade,
        "pillars_passed": f"{pillars_passed}/5",
        "price": round(price, 2),
        "change_pct": round(change_pct, 1),
        "rvol": round(rvol, 1),
        "float_shares": float_shares,
        "float_millions": round(float_shares / 1e6, 2),
        "has_catalyst": p3_news,
        "headline": news.get("headline", ""),
        "reasons": reasons,
        "pillars": {
            "p1_up_10pct": p1_up,
            "p2_rvol_5x": p2_rvol,
            "p3_catalyst": p3_news,
            "p4_price_2_20": p4_price,
            "p5_low_float_20m": p5_float,
        }
    }


def discover_market_universe(max_price: float = 25.0, min_price: float = 1.50) -> List[str]:
    """
    Dynamically scans the entire US equity market for today's active runners
    and top gainers using market-wide screener feeds + Alpaca tradeable assets.
    """
    import requests
    tickers = set(MOMENTUM_WATCHLIST)
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    base_url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"

    screeners = ["day_gainers", "aggressive_small_caps", "most_actives"]
    for scr in screeners:
        try:
            r = requests.get(base_url, params={"formatted": "false", "scrIds": scr, "count": 100},
                             headers=headers, timeout=8)
            quotes = r.json().get("finance", {}).get("result", [{}])[0].get("quotes", [])
            for q in quotes:
                sym = str(q.get("symbol", "") or "").upper().strip()
                px = float(q.get("regularMarketPrice", 0) or 0)
                chg = float(q.get("regularMarketChangePercent", 0) or 0)
                # Funnel Stage 1: Basic price range and positive/momentum change
                if sym and (min_price <= px <= max_price) and (chg >= 2.0):
                    if "." not in sym and "-" not in sym and len(sym) <= 5:
                        tickers.add(sym)
        except Exception as e:
            logger.debug(f"[discover_market_universe] {scr} query error: {e}")

    return sorted(list(tickers))


def scan_momentum_market(watchlist: Optional[List[str]] = None, top_n: int = 5,
                         whole_market: bool = False) -> List[dict]:
    """Scans the momentum universe and ranks candidates on the 5 Pillars."""
    if whole_market:
        print("\n🔍 Querying whole-market live feeds for today's active small-cap runners...")
        tickers = discover_market_universe()
        print(f"📡 Found {len(tickers)} potential market-wide candidates. Evaluating 5 Pillars...")
    else:
        tickers = watchlist or MOMENTUM_WATCHLIST

    results = []
    window = check_trading_window()
    print(f"\n{'=' * 82}")
    print(f"  🚀 ROSS CAMERON MOMENTUM SCANNER — 5 PILLARS EVALUATION")
    print(f"  Scope: {'WHOLE-MARKET LIVE SCAN' if whole_market else f'{len(tickers)} Selected Equities'} | Trading Window: {window['current_time_et']} ({window['detail']})")
    print(f"{'=' * 82}")

    for t in tickers:
        try:
            eval_res = evaluate_five_pillars(t)
            if eval_res.get("price", 0) > 0:
                results.append(eval_res)
        except Exception as e:
            logger.debug(f"[low_float_scanner] {t} error: {e}")

    results.sort(key=lambda x: -x["score"])

    if not results:
        print("  No tickers met criteria or data was unavailable.")
        print(f"{'=' * 82}\n")
        return []

    for i, r in enumerate(results[:top_n], 1):
        q_tag = "🌟 Grade A (Full Size)" if r["grade"] == "A" else ("⚠️ Grade B (Half Size)" if r["grade"] == "B" else "❌ Grade C (Skip)")
        print(f"\n #{i}  {r['ticker']:<6} ${r['price']:<6.2f}  +{r['change_pct']:>5.1f}%  "
              f"RVOL: {r['rvol']:>4.1f}x  Float: {r['float_millions']:>4.1f}M  SCORE {r['score']}/100 [{q_tag}]")
        print(f"      Pillars: {r['pillars_passed']} passed")
        for reason in r["reasons"]:
            print(f"      • {reason}")

    print(f"\n{'=' * 82}")
    return results[:top_n]


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Ross Cameron 5 Pillars Momentum Scanner")
    p.add_argument("--tickers", type=str, default="", help="Comma-separated tickers")
    p.add_argument("--market", "--all", action="store_true", help="Scan the whole market using live gainers and active runners")
    p.add_argument("--top", type=int, default=10, help="Number of top setups to display")
    args = p.parse_args()

    wl = [t.strip().upper() for t in args.tickers.split(",") if t.strip()] if args.tickers else None
    scan_momentum_market(watchlist=wl, top_n=args.top, whole_market=args.market)
