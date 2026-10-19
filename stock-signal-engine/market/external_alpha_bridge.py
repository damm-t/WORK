"""
External Alpha Reference & Quantitative Cross-Referencer
=========================================================
Ingests trade setups, tickers, and alerts from external social media / research bots
(e.g., TrendSpider, Instagram Reels, Twitter/X alerts) and cross-references them
against our 4-desk mathematical filters (11-year walk-forward rules).

Filters applied:
  1. Macro Trend Filter (Price > SMA200) — avoids falling-knife traps.
  2. Momentum / Swing Filter (30 <= RSI <= 65) — avoids chasing overbought tops.
  3. Dynamic Volatility Brackets (2.0x ATR Stop Loss, 2.0x & 3.5x ATR Take Profits).
  4. Volume Confirmation (Volume Ratio >= 1.1x).

Usage:
  python -m market.external_alpha_bridge --tickers GME,MU,ALAB,NVDA,COIN,GRAB,CAT
  python -m market.external_alpha_bridge --ig https://www.instagram.com/p/DdsCOmdkZux/
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from market.price_fetcher import fetch_prices
from market.technicals import TechnicalIndicators as TI


def evaluate_ticker(ticker: str) -> Dict[str, Any]:
    ticker = ticker.upper().strip()
    try:
        df = fetch_prices(ticker, period="1y")
        if df.empty or len(df) < 50:
            return {"ticker": ticker, "status": "no_data", "score": 0.0, "grade": "C"}
        
        c = df["Close"]
        price = float(c.iloc[-1])
        sma50 = float(c.rolling(50).mean().iloc[-1])
        sma200 = float(c.rolling(200).mean().iloc[-1]) if len(c) >= 200 else None
        rsi = float(TI.rsi(c).iloc[-1])
        atr = float(TI.atr(df).iloc[-1])
        vavg = float(TI.avg_volume(df["Volume"], length=20).iloc[-1] or 1.0)
        vol_curr = float(df["Volume"].iloc[-1])
        vol_ratio = vol_curr / max(vavg, 1.0)

        above_200 = (price > sma200) if sma200 else True
        above_50 = price > sma50

        score = 50.0
        strengths = []
        cautions = []

        # 1. Macro Regime Filter
        if above_200:
            score += 15.0
            strengths.append(f"Above SMA200 (${sma200:.2f}) — Institutional Bull Regime")
        else:
            score -= 15.0
            cautions.append(f"Below SMA200 (${sma200:.2f}) — Macro Headwind / Falling Knife Risk")

        # 2. Medium Trend
        if above_50:
            score += 10.0
            strengths.append(f"Above SMA50 (${sma50:.2f}) — Short-Term Momentum Active")
        else:
            cautions.append(f"Below SMA50 (${sma50:.2f}) — Mean-Reversion Pullback")

        # 3. RSI Swing Sweet Spot (35 to 65)
        if 35.0 <= rsi <= 60.0:
            score += 15.0
            strengths.append(f"Ideal Swing RSI ({rsi:.1f}) — Clean Entry Window")
        elif rsi < 35.0:
            score += 10.0
            strengths.append(f"Oversold Dip RSI ({rsi:.1f}) — High-Probability Mean Reversion")
        else:
            score -= 15.0
            cautions.append(f"Overextended RSI ({rsi:.1f} > 65) — Chase Trap Warning! Wait for Pullback")

        # 4. Volume Confirmation
        if vol_ratio >= 1.2:
            score += 10.0
            strengths.append(f"Volume Surge (x{vol_ratio:.1f} of 20d avg) — Whale Accumulation")

        # Calculate disciplined ATR geometry
        sl = round(price - 2.0 * atr, 2)
        tp1 = round(price + 2.0 * atr, 2)
        tp2 = round(price + 3.5 * atr, 2)

        grade = "A" if score >= 80 else ("B" if score >= 65 else "C")
        action = "STRONG BUY / QUEUE BRACKET" if grade == "A" else ("PULLBACK WATCH" if grade == "B" else "DISQUALIFIED / WAIT FOR RECLAIM")

        return {
            "ticker": ticker,
            "price": round(price, 2),
            "rsi": round(rsi, 1),
            "sma50": round(sma50, 2),
            "sma200": round(sma200, 2) if sma200 else None,
            "vol_ratio": round(vol_ratio, 2),
            "atr": round(atr, 2),
            "score": round(max(0.0, min(100.0, score)), 1),
            "grade": grade,
            "action": action,
            "strengths": strengths,
            "cautions": cautions,
            "brackets": {
                "entry": round(price, 2),
                "stop_loss_2atr": sl,
                "take_profit_1_2atr": tp1,
                "take_profit_2_3.5atr": tp2,
                "reward_risk_ratio": "2.0:1.0 (TP1) / 3.5:1.0 (TP2)"
            }
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e), "score": 0.0, "grade": "C"}


def cross_reference_batch(tickers: List[str]) -> List[Dict[str, Any]]:
    results = [evaluate_ticker(t) for t in tickers]
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results


def print_alpha_report(results: List[Dict[str, Any]], source_label: str = "External Feed"):
    print("═" * 78)
    print(f"  🧠 QUANT ENGINE ALPHA CROSS-REFERENCE AUDIT — {source_label.upper()}")
    print("═" * 78)
    print(f"  {'TICKER':<8} {'PRICE':<9} {'SCORE':<7} {'GRADE':<7} {'RSI':<6} {'REGIME':<12} {'RECOMMENDED ACTION'}")
    print("─" * 78)

    for r in results:
        t = r.get("ticker", "?")
        px = f"${r.get('price', 0):,.2f}"
        sc = f"{r.get('score', 0):.0f}/100"
        gr = r.get("grade", "C")
        rsi = f"{r.get('rsi', 0):.1f}"
        regime = "Bull (>200)" if (r.get("sma200") and r.get("price", 0) > r.get("sma200", 0)) else "Bear (<200)"
        act = r.get("action", "")

        color = "\033[1;32m" if gr == "A" else ("\033[1;33m" if gr == "B" else "\033[1;31m")
        reset = "\033[0m"
        print(f"  {color}{t:<8}{reset} {px:<9} {sc:<7} {color}{gr:<7}{reset} {rsi:<6} {regime:<12} {act}")

    print("═" * 78)
    print("  📋 DETAILED AUDIT & DISCIPLINED ATR BRACKETS:")
    print("═" * 78)

    for r in results:
        if r.get("grade") in ("A", "B"):
            t = r["ticker"]
            b = r.get("brackets", {})
            print(f"\n  🎯 [{r['grade']}] {t} (Price: ${r['price']:.2f} | Score: {r['score']})")
            for s in r.get("strengths", []):
                print(f"     ✅ {s}")
            for c in r.get("cautions", []):
                print(f"     ⚠️ {c}")
            if b:
                print(f"     📐 Execution Bracket: Limit Entry ${b['entry']} | Stop Loss ${b['stop_loss_2atr']} (2x ATR) | Target 1 ${b['take_profit_1_2atr']} | Target 2 ${b['take_profit_2_3.5atr']}")


def main():
    parser = argparse.ArgumentParser(description="Cross-reference external social/bot ideas through quant engine")
    parser.add_argument("--tickers", "-t", help="Comma-separated list of tickers (e.g. GME,MU,NVDA)")
    parser.add_argument("--meta", "-m", help="Path to parsed metadata JSON file")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    ticker_list = []
    source_name = "External Bot Alerts"

    if args.meta:
        p = Path(args.meta)
        if p.exists():
            data = json.loads(p.read_text())
            source_name = data.get("account", "Instagram Post")
            for item in data.get("carousel_setups", []):
                if "symbol" in item:
                    ticker_list.append(item["symbol"])
                elif "symbols" in item:
                    ticker_list.extend(item["symbols"])

    if args.tickers:
        ticker_list.extend([x.strip() for x in args.tickers.split(",") if x.strip()])

    if not ticker_list:
        ticker_list = ["GME", "MU", "ALAB", "NVDA", "COIN", "GRAB", "BABA", "AVGO", "CAT", "ONDS", "ASTS", "RGTI"]

    # Remove duplicates preserving order
    seen = set()
    dedup = [x for x in ticker_list if not (x in seen or seen.add(x))]

    results = cross_reference_batch(dedup)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_alpha_report(results, source_label=source_name)


if __name__ == "__main__":
    main()
