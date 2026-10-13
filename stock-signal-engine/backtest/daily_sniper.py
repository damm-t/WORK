#!/usr/bin/env python3
"""
Daily Quality Sniper: Single Best Setup Selector
=================================================
Binds all strategy modules into a single, high-conviction decision:
  1. SPY Macro Regime & Volatility Check (Bull / Chop / Bear)
  2. Sector ETF Tailwind Check (Relative Strength)
  3. Fundamental Balance Sheet & Profitability Gate (SEC EDGAR)
  4. Technical Momentum & Trend Pullback (SMA50>SMA200, 35<=RSI<=65, MACD+)
  5. News Sentiment & Earnings Blackout Check (FinBERT conviction)
  6. Exact Bracket & Sizing Construction (Stop 2.0xATR, TP1 2.0xATR, Trail 1.5xATR, SH Hedge)

Usage:
    .venv/bin/python backtest/daily_sniper.py
    .venv/bin/python backtest/daily_sniper.py --capital 5000 --risk-pct 0.02
"""

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backtest.universe import CORE_UNIVERSE, SECTOR_ETF
from backtest.market_scanner import rank_market
from market.beta_calculator import detect_market_regime, calculate_asset_beta
from market.price_fetcher import fetch_prices
from market.shock_detector import earnings_blackout, detect_intraday_shock
from market.technicals import TechnicalIndicators as TI
from risk.hedging_engine import without_banned


def get_sniper_setup(capital: float = 10_000.0, risk_pct: float = 0.02) -> dict:
    """Finds the #1 highest-conviction setup across the entire market."""
    today_str = date.today().isoformat()

    # 1. Macro Regime Check
    regime = detect_market_regime("SPY")
    regime_name = regime.get("regime", "CHOP_NEUTRAL")
    hedge_mult = regime.get("hedge_multiplier", 0.50)

    # Dynamic risk scaling based on SPY regime
    if regime_name == "BEAR_VOLATILITY":
        effective_risk_pct = risk_pct * 0.50  # scale down risk to 1% in Bear
    else:
        effective_risk_pct = risk_pct

    # 2. Intraday Shock Protection
    shock = detect_intraday_shock("SPY")
    is_shock = shock.get("status") == "shock_detected"

    # 3. Market Scan & Quality Rank
    ranked = rank_market(top_n=10, filter_junk=True, sector_cap=1, show_callout=False)

    # 4. Filter for Top Candidate with all gates passed
    best_candidate = None
    skipped_candidates = []
    for cand in ranked:
        ticker = cand["ticker"]

        # Check Earnings Blackout
        eb = earnings_blackout(ticker)
        if eb.get("blackout", False):
            skipped_candidates.append(f"{ticker} (earnings blackout)")
            continue

        # Technical Indicators for Entry Geometry
        df = fetch_prices(ticker, period="1y", interval="1d")
        if df.empty or len(df) < 60:
            skipped_candidates.append(f"{ticker} (insufficient data)")
            continue

        close = float(df["Close"].iloc[-1])
        atr_val = float(TI.atr(df).iloc[-1])
        rsi_val = float(TI.rsi(df["Close"]).iloc[-1])

        # Technical sanity: avoid buying if RSI is overheated (>68) or dumped (<32)
        if rsi_val > 68.0:
            skipped_candidates.append(f"{ticker} (overbought RSI {rsi_val:.1f} > 68)")
            continue
        if rsi_val < 32.0:
            skipped_candidates.append(f"{ticker} (oversold RSI {rsi_val:.1f} < 32)")
            continue
        if atr_val <= 0:
            skipped_candidates.append(f"{ticker} (invalid ATR)")
            continue

        # Stop & Target levels (Tuned 2.0x ATR Geometry)
        stop_dist = 2.0 * atr_val
        stop_price = round(close - stop_dist, 2)
        tp1_price = round(close + 2.0 * stop_dist, 2)  # TP1 at +2.0 R

        # Position Sizing
        dollar_risk = capital * effective_risk_pct
        shares_raw = dollar_risk / stop_dist
        max_notional = capital * 0.30  # 30% position cap
        shares_capped = min(shares_raw, max_notional / close)
        shares = round(shares_capped, 4) if capital <= 5000 else int(shares_capped)

        if shares <= 0:
            shares = 1 if capital >= close else round(shares_capped, 2)

        # Asset Beta and Inverse Hedge Calculation
        beta_info = calculate_asset_beta(ticker, "SPY")
        beta = float(beta_info.get("beta", 1.0) or 1.0)
        long_notional = shares * close

        # SH Inverse Hedge Sizing
        df_sh = fetch_prices("SH", period="1mo", interval="1d")
        sh_price = float(df_sh["Close"].iloc[-1]) if not df_sh.empty else 15.0
        target_hedge_val = long_notional * abs(beta) * hedge_mult
        target_hedge_val = min(target_hedge_val, 0.50 * capital)
        sh_shares = round(target_hedge_val / sh_price, 2) if capital <= 5000 else int(target_hedge_val / sh_price)

        best_candidate = {
            "date": today_str,
            "ticker": ticker,
            "sector": cand["sector"],
            "score": cand["score"],
            "price": close,
            "atr": round(atr_val, 2),
            "rsi": round(rsi_val, 1),
            "reasons": cand["reasons"],
            "regime": regime_name,
            "hedge_multiplier": hedge_mult,
            "effective_risk_pct": effective_risk_pct,
            "dollar_risk": round(dollar_risk, 2),
            "shares": shares,
            "notional": round(long_notional, 2),
            "stop_price": stop_price,
            "stop_dist": round(stop_dist, 2),
            "tp1_price": tp1_price,
            "tp1_scale_pct": "50%",
            "trail_atr": round(1.5 * atr_val, 2),
            "beta": round(beta, 2),
            "sh_shares": sh_shares,
            "sh_price": round(sh_price, 2),
            "sh_notional": round(sh_shares * sh_price, 2),
            "is_shock": is_shock,
            "skipped_candidates": skipped_candidates,
        }
        break

    return best_candidate


def main():
    import contextlib
    import io
    import json
    import os

    ap = argparse.ArgumentParser(description="Daily Quality Sniper: Single Best Setup")
    ap.add_argument("--capital", type=float, default=10_000.0, help="Account capital in USD")
    ap.add_argument("--risk-pct", type=float, default=float(os.getenv("RISK_PCT", "0.02")), help="Risk per trade (default 0.02 = 2%)")
    ap.add_argument("--ticker-only", action="store_true", help="Output only the winning ticker symbol")
    ap.add_argument("--json", action="store_true", help="Output setup as JSON")
    ap.add_argument("--quiet", action="store_true", help="Suppress intermediate scanner tables")
    args = ap.parse_args()

    if args.ticker_only or args.json or args.quiet:
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink):
            setup = get_sniper_setup(capital=args.capital, risk_pct=args.risk_pct)
    else:
        print("\n" + "=" * 75)
        print("       🎯 DAILY QUALITY SNIPER: SINGLE BEST SETUP SELECTOR")
        print("=" * 75)
        setup = get_sniper_setup(capital=args.capital, risk_pct=args.risk_pct)

    # Persist setup state so shell scripts can read it without rescanning
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    setup_path = data_dir / "sniper_setup.json"
    if setup:
        setup_path.write_text(json.dumps(setup, indent=2))
    elif setup_path.exists():
        setup_path.unlink()

    if args.ticker_only:
        if setup and setup.get("ticker"):
            print(setup["ticker"])
        else:
            print("NONE")
        return

    if args.json:
        print(json.dumps(setup or {}, indent=2))
        return

    if not setup:
        print("\n  [Notice] No Grade A candidate satisfied all quality & macro gates today.")
        print("  Recommendation: Stay in cash. Patience is an edge.\n")
        return

    print(f"\n  [Macro SPY State] : {setup['regime']} (Hedge Mult: {setup['hedge_multiplier']}x)")
    print(f"  [Account Capital] : ${args.capital:,.2f} | Dynamic Risk: {setup['effective_risk_pct']:.1%} (${setup['dollar_risk']:,.2f})")
    print("-" * 75)
    if setup.get("skipped_candidates"):
        print(f"  ⚡ Safety Filter Passed Over : {', '.join(setup['skipped_candidates'])}")
    print(f"  🎯 THE QUALITY SNIPER PICK : {setup['ticker']} ({setup['sector']})")
    print(f"  Composite Score           : {setup['score']:.1f} / 100 [Grade A Quality]")
    print(f"  Key Catalysts             : {', '.join(setup['reasons'][:4])}")
    print("-" * 75)
    print("  📋 EXECUTION PLAN (Enter pre-market / market open):")
    print(f"    • Action               : BUY {setup['shares']} shares of {setup['ticker']} @ ~${setup['price']:.2f}")
    print(f"    • Position Value       : ${setup['notional']:,.2f}")
    print(f"    • Stop Loss (2.0xATR)  : ${setup['stop_price']:.2f} (Risk distance: ${setup['stop_dist']:.2f})")
    print(f"    • Take Profit 1 (TP1)  : ${setup['tp1_price']:.2f} (Sell 50% clip for +2.0R)")
    print(f"    • Runner Trailing Stop : Trail {setup['trail_atr']} below highest high after TP1 hits")
    print("-" * 75)
    print("  🛡️ CRISIS BALLAST (Paired Inverse Hedge):")
    print(f"    • Stock Beta           : {setup['beta']:.2f} vs SPY")
    print(f"    • Pair Hedge Action    : BUY {setup['sh_shares']} shares of SH @ ~${setup['sh_price']:.2f} (${setup['sh_notional']:,.2f})")
    print("-" * 75)
    print("  🧘 THE DISCIPLINE:")
    print("    1. Enter the trade.")
    print("    2. Set the stop-loss & TP1 bracket orders.")
    print("    3. Then DO NOTHING and JUST WAIT.")
    print("    Let the 2.0x ATR geometry and trailing runner do the mathematical compounding.")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
