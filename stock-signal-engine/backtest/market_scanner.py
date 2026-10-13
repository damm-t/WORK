"""
Market-Wide Scanner & Selector
==============================
Two modes:

  backtest : Runs the paired strategy across a 27-name universe covering all
             11 GICS sectors, aggregates results BY SECTOR, and reveals
             where the strategy's edge actually lives.

  scan     : Ranks the ENTIRE universe right now on a composite momentum /
             breakout / sector-strength score (0-100) and suggests the top
             candidates — "be selective on the market, then choose the stock".

Why not a vector DB? Stock selection is numeric FACTOR RANKING (momentum %,
volume ratio, distance from highs). A sorted scorer is faster, explainable,
and needs zero infrastructure. Vector DBs become useful later when we embed
NEWS TEXT for narrative clustering — noted as future work.

Usage:
    python backtest/market_scanner.py --mode backtest --start 2026-05-26 \
        --end 2026-08-25 --capital 100 --style bold --risk-pct 0.05 --fractional
    python backtest/market_scanner.py --mode scan --top 5
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backtest.hedging_backtester import run_comparison
from backtest.universe import CORE_UNIVERSE as UNIVERSE   # single source of truth
from backtest.universe import SECTOR_ETF
from market.technicals import TechnicalIndicators as TI


def flat_universe() -> list:
    from risk.hedging_engine import without_banned
    return without_banned(
        [t for tickers in UNIVERSE.values() for t in tickers])


def sector_of(ticker: str) -> str:
    for sector, tickers in UNIVERSE.items():
        if ticker in tickers:
            return sector
    return "?"


# ------------------------------------------------------------ mass backtest --
def mass_backtest(start: str, end: str, capital: float = 100.0,
                  risk_pct: float = 0.05, style: str = "bold",
                  fractional: bool = True) -> list:
    """Runs every universe name through run_comparison; returns result rows."""
    rows = []
    total = len(flat_universe())
    done = 0
    for sector, tickers in UNIVERSE.items():
        for ticker in tickers:
            done += 1
            print(f"[{done:>2}/{total}] {ticker:<6} ({sector}) ...", flush=True)
            try:
                r = run_comparison(
                    ticker=ticker, period="1y", capital=capital,
                    risk_pct=risk_pct, start=start, end=end,
                    fractional=fractional, style=style, quiet=True,
                )
                rows.append({
                    "sector": sector,
                    "ticker": ticker,
                    "final_u": r["unhedged"]["final_equity"],
                    "final_h": r["hedged"]["final_equity"],
                    "mdd_u": r["unhedged"]["max_drawdown_pct"],
                    "mdd_h": r["hedged"]["max_drawdown_pct"],
                    "trades": r["hedged"]["num_trades"],
                    "win_rate": r["hedged"]["win_rate_pct"],
                })
            except SystemExit as e:
                print(f"    skipped: {e}")
            except Exception as e:
                print(f"    error: {e}")
    return rows


def print_mass_report(rows: list, capital: float) -> None:
    if not rows:
        print("No results collected.")
        return

    print(f"\n{'=' * 78}\n  MARKET-WIDE RESULTS  ({len(rows)} stocks, "
          f"${capital:.0f} each)\n{'=' * 78}")
    hdr = f"{'Sector':<15}{'Ticker':<7}{'Unhedged':>10}{'Hedged':>10}{"MDD-U%":>8}{'Trades':>8}"
    print(hdr)
    print("-" * len(hdr))
    for r in sorted(rows, key=lambda x: -x["final_u"]):
        print(f"{r['sector']:<15}{r['ticker']:<7}{r['final_u']:>10,.2f}"
              f"{r['final_h']:>10,.2f}{r['mdd_u']:>8.2f}{r['trades']:>8}")

    avg_u = sum(r["final_u"] for r in rows) / len(rows)
    avg_h = sum(r["final_h"] for r in rows) / len(rows)
    wins = [r for r in rows if r["final_u"] > capital]

    print("-" * len(hdr))
    print(f"AVERAGE EQUITY : unhedged ${avg_u:,.2f} ({(avg_u/capital-1)*100:+.2f}%)"
          f" | hedged ${avg_h:,.2f} ({(avg_h/capital-1)*100:+.2f}%)")
    print(f"Profitable     : {len(wins)}/{len(rows)} stocks")
    best = max(rows, key=lambda x: x["final_u"])
    worst = min(rows, key=lambda x: x["final_u"])
    print(f"BEST           : {best['ticker']} ({best['sector']}) ${best['final_u']:,.2f}")
    print(f"WORST          : {worst['ticker']} ({worst['sector']}) ${worst['final_u']:,.2f}")

    # Sector aggregation
    print(f"\n{'SECTOR LEAGUE TABLE (avg unhedged equity)':^50}")
    print("-" * 50)
    agg = {}
    for r in rows:
        s = agg.setdefault(r["sector"], {"sum": 0.0, "n": 0})
        s["sum"] += r["final_u"]
        s["n"] += 1
    for sector, s in sorted(agg.items(), key=lambda kv: -(kv[1]["sum"] / kv[1]["n"])):
        avg = s["sum"] / s["n"]
        bar = "#" * max(0, int((avg / capital - 1) * 200) + 10)
        print(f"{sector:<15}{avg:>9,.2f}  {bar}")


# ------------------------------------------------------------- live scan ----
def rank_market(top_n: int = 5, filter_junk: bool = True, sector_cap: int = 2,
                show_callout: bool = True) -> list:
    """
    Scores every universe name RIGHT NOW on a composite 0-100 scale:

      momentum (3-month return)          up to 25 pts
      proximity to 52-week high          up to 20 pts   (leaders keep leading)
      fresh 20-day-high breakout         +10 pts
      volume surge vs 20d average        up to 10 pts
      positive MACD                      +10 pts
      sector ETF above its SMA50         +10 pts
      SPY regime bonus/penalty           +/-5  pts
      fundamental quality (SEC GAAP)     up to +15 pts  (profitable, healthy balance sheet)
      unprofitable / junk penalty        -15 pts

    Returns ranked rows with sector diversification guard (max `sector_cap` per sector in top picks).
    """
    from market.price_fetcher import fetch_prices
    from market.fundamentals import evaluate_fundamental_quality
    from risk.hedging_engine import without_banned

    spy = fetch_prices("SPY", period="1y")["Close"]
    spy_up = float(spy.iloc[-1]) > float(spy.rolling(50).mean().iloc[-1])
    print(f"\nSPY regime: {'BULL (above SMA50)' if spy_up else 'BEAR (below SMA50)'}")

    rows = []
    for sector, tickers in UNIVERSE.items():
        etf = SECTOR_ETF[sector]
        ec = fetch_prices(etf, period="1y")["Close"]
        if ec.empty or len(ec) < 60:
            continue
        sector_up = float(ec.iloc[-1]) > float(ec.rolling(50).mean().iloc[-1])

        for t in without_banned(tickers):
            df = fetch_prices(t, period="1y")
            if df.empty or len(df) < 70:
                continue
            c = df["Close"]
            price = float(c.iloc[-1])
            hi20 = float(df["High"].rolling(20).max().shift(1).iloc[-1])
            hi52 = float(c.tail(min(len(c), 252)).max())
            vavg = float(TI.avg_volume(df["Volume"], length=20, exclude_current=True).iloc[-1] or 1.0)
            vol_curr = float(df["Volume"].iloc[-1])
            vol_prev = float(df["Volume"].iloc[-2]) if len(df) >= 2 else vol_curr
            vol_ratio = max(vol_curr / max(vavg, 1.0), vol_prev / max(vavg, 1.0))
            mom3 = (price / float(c.iloc[-64]) - 1.0) * 100.0 if len(c) > 64 else 0.0
            macd_pos = float(TI.macd(c)[0].iloc[-1]) > 0.0
            rsi = float(TI.rsi(c).iloc[-1])
            off_hi20 = (price / hi20 - 1.0) * 100.0 if hi20 > 0 else 0.0
            off_high = (price / hi52 - 1.0) * 100.0

            pts, reasons = 0.0, []
            m_pts = max(-10.0, min(25.0, mom3 * 0.85))
            pts += m_pts
            reasons.append(f"3m mom {mom3:+.1f}% ({m_pts:+.0f})")
            p_pts = max(0.0, 20.0 - abs(off_high) * 2.5)
            pts += p_pts
            reasons.append(f"{off_high:+.1f}% from 52wH (+{p_pts:.0f})")
            if price >= hi20:
                pts += 10.0
                reasons.append("FRESH 20d breakout (+10)")
            v_pts = min(vol_ratio, 3.0) / 3.0 * 10.0
            pts += v_pts
            reasons.append(f"vol x{vol_ratio:.1f} (+{v_pts:.0f})")

            # High-Volume Pullback / Dip Setup Detection
            is_high_vol_dip = False
            if vol_ratio >= 1.15 and (-15.0 <= off_hi20 <= -1.5) and (30.0 <= rsi <= 55.0):
                is_high_vol_dip = True
                dip_pts = min(15.0, 8.0 + (vol_ratio - 1.0) * 6.0)
                pts += dip_pts
                reasons.append(f"🔥 High-Vol Dip: vol x{vol_ratio:.1f} at {off_hi20:+.1f}% from 20dH (RSI {rsi:.0f}) (+{dip_pts:.0f})")
            elif vol_ratio >= 1.15 and rsi < 35.0:
                is_high_vol_dip = True
                pts += 12.0
                reasons.append(f"🔥 Oversold Volume Accumulation: vol x{vol_ratio:.1f} at RSI {rsi:.0f} (+12)")

            if macd_pos:
                pts += 10.0
                reasons.append("MACD+ (+10)")
            if sector_up:
                pts += 10.0
                reasons.append(f"{etf} sector uptrend (+10)")
            pts += 5.0 if spy_up else -5.0

            # Fundamental Quality Sanity Gate & Scoring (SEC EDGAR)
            fq = evaluate_fundamental_quality(t, sector=sector)
            f_pts = float(fq.get("quality_score", 0.0) or 0.0)
            pts += f_pts
            reasons.extend(fq.get("reasons", []))

            rows.append({
                "ticker": t,
                "sector": sector,
                "price": round(price, 2),
                "score": round(max(0.0, min(100.0, pts)), 1),
                "reasons": reasons,
                "fundamentals": fq.get("metrics", {}),
                "quality_score": f_pts,
                "passed_quality": fq.get("passed", True),
                "vol_ratio": round(vol_ratio, 2),
                "off_hi20_pct": round(off_hi20, 1),
                "rsi": round(rsi, 1),
                "is_high_vol_dip": is_high_vol_dip,
                "setup_type": "HIGH_VOL_DIP" if is_high_vol_dip else ("BREAKOUT" if price >= hi20 else "MOMENTUM"),
            })

    # Sort primarily by composite score
    rows.sort(key=lambda r: -r["score"])

    # Apply Sector Diversification Guard (max sector_cap per sector in top picks)
    top_picks = []
    other_picks = []
    sector_counts = {}

    for r in rows:
        if filter_junk and not r["passed_quality"]:
            other_picks.append(r)
            continue

        sec = r["sector"]
        if sector_counts.get(sec, 0) < sector_cap and len(top_picks) < top_n:
            top_picks.append(r)
            sector_counts[sec] = sector_counts.get(sec, 0) + 1
        else:
            other_picks.append(r)

    ranked_rows = top_picks + other_picks

    print(f"\n{'=' * 78}\n  MARKET LEADERBOARD — top {top_n} of {len(ranked_rows)} (Sector-Diversified)\n{'=' * 78}")
    for i, r in enumerate(ranked_rows[:top_n], 1):
        q_tag = "✅ Quality Pass" if r["passed_quality"] else "⚠️ Low Quality"
        print(f"\n #{i}  {r['ticker']}  [{r['sector']}]  ${r['price']}  "
              f"SCORE {r['score']}/100  [{q_tag}]")
        for reason in r["reasons"]:
            print(f"      • {reason}")
    if show_callout and ranked_rows:
        pick = ranked_rows[0]
        print(f"\n>>> TOP PICK: {pick['ticker']} ({pick['sector']}) "
              f"— score {pick['score']}/100")
        print(">>> Confirm with the full pipeline before entering:")
        print(f">>>   python backtest/sentiment_hedged_vs_unhedged.py "
              f"--tickers {pick['ticker']} --force-buy")
    return ranked_rows


def scan_dip_opportunities(top_n: int = 5, filter_junk: bool = True) -> list:
    """
    Specifically filters for High-Volume Pullback / Dip Accumulation setups:
    Volume ratio >= 1.10x, price discounted from 20d high (-1.5% to -15%),
    favorable RSI (25-58), passed SEC fundamental quality gate.
    """
    rows = rank_market(top_n=30, filter_junk=filter_junk, sector_cap=3, show_callout=False)
    dips = [r for r in rows if r.get("is_high_vol_dip") or (r.get("vol_ratio", 0) >= 1.1 and r.get("off_hi20_pct", 0) <= -1.5)]
    dips.sort(key=lambda x: -x["score"])

    print(f"\n{'=' * 78}\n  🎯 HIGH-VOLUME DIP & VALUE OPPORTUNITIES (Top {min(top_n, len(dips))} of {len(dips)})\n{'=' * 78}")
    if not dips:
        print("  No high-volume dip setups currently active in universe.")
    for i, r in enumerate(dips[:top_n], 1):
        print(f"\n #{i}  {r['ticker']:<6} [{r['sector']:<14}]  ${r['price']:<7.2f}  "
              f"SCORE {r['score']}/100  (Vol: {r.get('vol_ratio', 1.0):.1f}x, {r.get('off_hi20_pct', 0.0):+.1f}% from 20dH, RSI: {r.get('rsi', 50):.0f})")
        for reason in r["reasons"]:
            print(f"      • {reason}")
    return dips[:top_n]


# -------------------------------------------------------------------- CLI ---
def main() -> None:
    parser = argparse.ArgumentParser(description="Market-wide Scanner & Selector")
    parser.add_argument("--mode", choices=["backtest", "scan"], default="scan")
    parser.add_argument("--dips", action="store_true",
                        help="scan mode: show only High-Volume Dip / Discount setups")
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    parser.add_argument("--capital", type=float, default=100.0)
    parser.add_argument("--risk-pct", type=float, default=0.05)
    parser.add_argument("--style", choices=["conservative", "bold"], default="bold")
    parser.add_argument("--top", type=int, default=5, help="scan mode: show top N")
    parser.add_argument("--universe", choices=["core", "wide"], default="core",
                        help="core=28 mega-caps | wide=~90 large-caps")
    parser.add_argument("--whole-shares", dest="fractional", action="store_false",
                        help="disable fractional shares")
    parser.add_argument("--sector-cap", type=int, default=2,
                        help="maximum stocks per sector in top recommendations")
    parser.add_argument("--no-filter-junk", dest="filter_junk", action="store_false",
                        help="allow unprofitable/overleveraged stocks in top picks")
    parser.set_defaults(filter_junk=True)
    args = parser.parse_args()

    if args.universe == "wide":
        from backtest.universe import WIDE_UNIVERSE
        globals()["UNIVERSE"] = WIDE_UNIVERSE

    if args.mode == "backtest":
        if not args.start:
            raise SystemExit("backtest mode requires --start YYYY-MM-DD")
        rows = mass_backtest(args.start, args.end, capital=args.capital,
                             risk_pct=args.risk_pct, style=args.style,
                             fractional=args.fractional)
        print_mass_report(rows, args.capital)
    elif args.dips:
        scan_dip_opportunities(top_n=args.top, filter_junk=args.filter_junk)
    else:
        rank_market(top_n=args.top, filter_junk=args.filter_junk, sector_cap=args.sector_cap)


if __name__ == "__main__":
    main()