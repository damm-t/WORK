"""
Five-Year Market Statistics
===========================
Simulates ~5 years of daily history across EVERY stock in the engine's market
universe (wide universe: ~90 large-caps across all 11 GICS sectors, which is
a superset of the 28-ticker core) and produces per-stock statistics:

    1. Buy & Hold      : total return, CAGR, annualized vol, Sharpe,
                         max drawdown, best / worst calendar year.
    2. Engine strategy : the house conservative style (MACD+RSI pullback,
                         1.5xATR stop, TP1 scale-out, ratchet trail, SPY
                         regime sizing, SH inverse-ETF hedge, 2% risk,
                         fractional shares) simulated bar-by-bar via
                         backtest.hedging_backtester.PairStrategySimulator —
                         both the HEDGED book and the UNHEDGED book.

Outputs:
    - ranked console leaderboard (top / bottom + sector rollup)
    - reports/five_year_stats_<date>.csv  (full table, one row per stock)
    - reports/five_year_stats_<date>.md   (readable report)

Usage:
    python backtest/five_year_stats.py                    # whole market
    python backtest/five_year_stats.py --limit 5          # smoke test
    python backtest/five_year_stats.py --universe core    # 28 mega-caps only
"""

import argparse
import math
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from backtest.hedging_backtester import (
    PairStrategySimulator,
    SimulationConfig,
    _strip_tz,
    performance_metrics,
)
from backtest.universe import get_universe
from market.price_fetcher import fetch_prices

BENCH = "SPY"
HEDGE = "SH"
REPORT_DIR = Path("reports")


# ------------------------------------------------------------------ data ----
def _load(ticker: str, years: int) -> pd.DataFrame:
    """Fetch `years` of daily bars with retries; '' on failure."""
    df = pd.DataFrame()
    for attempt in range(3):
        df = fetch_prices(ticker, period=f"{years}y", interval="1d")
        if not df.empty and len(df) > 60:
            break
        time.sleep(2.0 * (attempt + 1))
    if df.empty:
        return pd.DataFrame()
    df = _strip_tz(df)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    need = ("Open", "High", "Low", "Close", "Volume")
    return df if all(c in df.columns for c in need) else pd.DataFrame()


def _synth_inverse(df_bench: pd.DataFrame) -> pd.DataFrame:
    """-1x SPY proxy (same fallback the backtester uses when SH is missing)."""
    df_hedge = df_bench.copy()
    ret = df_bench["Close"].pct_change().fillna(0.0)
    df_hedge["Close"] = df_bench["Close"].iloc[0] * (1.0 - ret).cumprod()
    for col in ("Open", "High", "Low"):
        if col in df_hedge.columns:
            df_hedge[col] = df_hedge["Close"]
    return df_hedge


# ------------------------------------------------------- buy & hold stats ---
def buy_and_hold_stats(close: pd.Series) -> dict:
    """Total return / CAGR / vol / Sharpe / maxDD / best & worst year."""
    out = {"bh_total_return_pct": None, "bh_cagr_pct": None, "bh_vol_pct": None,
           "bh_sharpe": None, "bh_max_dd_pct": None, "bh_best_year_pct": None,
           "bh_worst_year_pct": None}
    if len(close) < 2 or float(close.iloc[0]) <= 0:
        return out

    r = close.pct_change().dropna()
    n = len(r)
    total = float(close.iloc[-1] / close.iloc[0] - 1.0)
    cagr = (float(close.iloc[-1]) / float(close.iloc[0])) ** (252.0 / n) - 1.0
    vol = float(r.std()) * math.sqrt(252) if n > 1 else 0.0
    sharpe = (float(r.mean() / r.std() * math.sqrt(252))
              if n > 1 and r.std() > 0 else 0.0)
    dd = float((close / close.cummax() - 1.0).min())

    yearly = (1.0 + r).groupby(r.index.year).prod() - 1.0
    out.update({
        "bh_total_return_pct": round(total * 100, 1),
        "bh_cagr_pct": round(cagr * 100, 1),
        "bh_vol_pct": round(vol * 100, 1),
        "bh_sharpe": round(sharpe, 2),
        "bh_max_dd_pct": round(dd * 100, 1),
        "bh_best_year_pct": round(float(yearly.max()) * 100, 1) if len(yearly) else None,
        "bh_worst_year_pct": round(float(yearly.min()) * 100, 1) if len(yearly) else None,
    })
    return out


# ------------------------------------------------------------- strategy -----
def strategy_stats(df_asset: pd.DataFrame, df_bench: pd.DataFrame,
                   df_hedge: pd.DataFrame, capital: float, risk_pct: float,
                   fractional: bool, style: str, hedged: bool) -> dict:
    """Run one book of the engine's PairStrategySimulator; return metrics."""
    cfg = SimulationConfig(capital=capital, hedged=hedged, risk_pct=risk_pct,
                           fractional=fractional, style=style)
    curve, trades = PairStrategySimulator(df_asset, df_bench, df_hedge, cfg).run()
    m = performance_metrics(curve, trades)
    book = "strat" if hedged else "unhedged"
    return {
        f"{book}_ret_pct": m["total_return_pct"],
        f"{book}_final_equity": m["final_equity"],
        f"{book}_max_dd_pct": m["max_drawdown_pct"],
        f"{book}_sharpe": m["sharpe"],
        f"{book}_trades": m["num_trades"],
        f"{book}_win_rate_pct": m["win_rate_pct"],
    }


# ------------------------------------------------------------------ main ----
def collect_tickers(universe: str) -> dict:
    """{ticker: sector} for the whole market (wide) or core only."""
    uni = get_universe(universe)
    return {t: sec for sec, ts in uni.items() for t in ts}


def run(args) -> None:
    tickers = collect_tickers(args.universe)
    names = sorted(tickers)
    if args.limit:
        names = names[: args.limit]
    total = len(names)
    print(f"=== FIVE-YEAR MARKET STATISTICS — {total} tickers "
          f"(universe={args.universe}, style={args.style}) ===", flush=True)

    # benchmark + hedge legs, fetched once and shared by every sim
    print(f"[data] {BENCH} (benchmark) ...", flush=True)
    df_bench = _load(BENCH, args.years)
    print(f"[data] {HEDGE} (hedge) ...", flush=True)
    df_hedge = _load(HEDGE, args.years)
    if df_hedge.empty or len(df_hedge) < 30:
        print(f"[data] {HEDGE} unavailable -> synthesizing -1x {BENCH}.",
              flush=True)
        df_hedge = _synth_inverse(df_bench)
    if df_bench.empty:
        raise SystemExit("[five_year_stats] No SPY data — aborting.")

    spy_bh = buy_and_hold_stats(df_bench["Close"])
    rows, failures = [], []

    for k, t in enumerate(names, 1):
        sector = tickers[t]
        try:
            df = _load(t, args.years)
            if df.empty:
                failures.append(t)
                print(f"  [{k:>2}/{total}] {t:<6} ({sector}) — NO DATA, skipped",
                      flush=True)
                continue

            row = {"ticker": t, "sector": sector,
                   "last_price": round(float(df["Close"].iloc[-1]), 2),
                   "years_of_data": round(len(df) / 252.0, 1)}
            row.update(buy_and_hold_stats(df["Close"]))
            row["bh_final_equity"] = (
                round(args.capital *
                      (1 + row["bh_total_return_pct"] / 100), 2)
                if row["bh_total_return_pct"] is not None else None)

            # trim asset to the shared bench window so sims align cleanly
            idx = df.index.intersection(df_bench.index)
            df_a, db, dh = df.loc[idx], df_bench.loc[idx], df_hedge.loc[idx]
            if len(df_a) < 70:
                failures.append(t)
                print(f"  [{k:>2}/{total}] {t:<6} ({sector}) — <70 bars, "
                      f"skipped", flush=True)
                continue

            row.update(strategy_stats(df_a, db, dh, args.capital,
                                      args.risk_pct, args.fractional,
                                      args.style, hedged=True))
            row.update(strategy_stats(df_a, db, dh, args.capital,
                                      args.risk_pct, args.fractional,
                                      args.style, hedged=False))
            if row["bh_total_return_pct"] is not None:
                row["edge_vs_bh_pp"] = round(
                    row["strat_ret_pct"] - row["bh_total_return_pct"], 1)
            rows.append(row)
            print(f"  [{k:>2}/{total}] {t:<6} ({sector:<13}) "
                  f"B&H {row['bh_total_return_pct']:>+8.1f}%  "
                  f"strat {row['strat_ret_pct']:>+8.1f}%  "
                  f"({row['strat_trades']:>3} trades, "
                  f"WR {row['strat_win_rate_pct']:>5.1f}%)  "
                  f"unhedged {row['unhedged_ret_pct']:>+8.1f}%", flush=True)
        except Exception as e:  # keep the sweep alive no matter what
            failures.append(t)
            print(f"  [{k:>2}/{total}] {t:<6} ({sector}) — ERROR {e}",
                  flush=True)

    if not rows:
        raise SystemExit("[five_year_stats] No results — every ticker failed.")

    df_out = pd.DataFrame(rows).sort_values("strat_final_equity",
                                            ascending=False)
    _save_csv(df_out)
    _report(df_out, spy_bh, failures, args, total)
    _console_summary(df_out, spy_bh, failures, args)


def _save_csv(df_out: pd.DataFrame) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"five_year_stats_{date.today()}.csv"
    df_out.to_csv(path, index=False)
    print(f"\n[saved] {path}", flush=True)
    return path


def _fmt(v, pct=False, signed=False):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    if pct:
        return f"{v:+,.1f}%" if signed else f"{v:,.1f}%"
    if isinstance(v, float):
        return f"{v:+,.2f}" if signed else f"{v:,.2f}"
    return str(v)


def _row_str(i: int, r: pd.Series) -> str:
    return (f"{i:>2} {r['ticker']:<6}{r['sector']:<15}"
            f"{_fmt(r['bh_cagr_pct'], signed=True):>10}"
            f"{_fmt(r['bh_max_dd_pct'], signed=True):>11}"
            f"{_fmt(r['bh_best_year_pct'], signed=True):>9}"
            f"{_fmt(r['strat_ret_pct'], signed=True):>11}"
            f"{_fmt(r['strat_max_dd_pct'], signed=True):>10}"
            f"{r['strat_trades']:>8}"
            f"{_fmt(r['strat_win_rate_pct']):>9}"
            f"{_fmt(r['unhedged_ret_pct'], signed=True):>10}")


def _console_summary(df_out: pd.DataFrame, spy_bh: dict, failures: list,
                     args) -> None:
    print("\n" + "=" * 118, flush=True)
    print(f"  MARKET-WIDE {args.years}-YEAR LEADERBOARD — top "
          f"{min(15, len(df_out))} of {len(df_out)} by engine strategy "
          f"(hedged) final equity", flush=True)
    print("=" * 118, flush=True)
    hdr = (f"{'#':>2} {'Ticker':<6}{'Sector':<15}{'B&H CAGR':>10}"
           f"{'B&H MaxDD':>11}{'Best Yr':>9}{'Strat Ret':>11}{'Strat DD':>10}"
           f"{'Trades':>8}{'WinRate':>9}{'Unhedged':>10}")
    print(hdr, flush=True)
    print("-" * 118, flush=True)
    for i, (_, r) in enumerate(df_out.head(15).iterrows(), 1):
        print(_row_str(i, r), flush=True)
    if len(df_out) > 20:
        print("  ...", flush=True)
        for i, (_, r) in enumerate(df_out.tail(5).iterrows(),
                                   len(df_out) - 4):
            print(_row_str(i, r), flush=True)

    print("\n--- Benchmark: SPY buy & hold (same window) ---", flush=True)
    print(f"  CAGR {_fmt(spy_bh.get('bh_cagr_pct'), signed=True)}  |  "
          f"MaxDD {_fmt(spy_bh.get('bh_max_dd_pct'), signed=True)}  |  "
          f"Sharpe {_fmt(spy_bh.get('bh_sharpe'))}  |  "
          f"Best yr {_fmt(spy_bh.get('bh_best_year_pct'), signed=True)}  |  "
          f"Worst yr {_fmt(spy_bh.get('bh_worst_year_pct'), signed=True)}",
          flush=True)

    g = df_out.groupby("sector").agg(
        n=("ticker", "count"),
        avg_bh_cagr=("bh_cagr_pct", "mean"),
        avg_strat_ret=("strat_ret_pct", "mean"),
        avg_unhedged_ret=("unhedged_ret_pct", "mean"),
        avg_trades=("strat_trades", "mean"),
        avg_win_rate=("strat_win_rate_pct", "mean"),
    ).sort_values("avg_strat_ret", ascending=False)
    print("\n--- Sector rollup (avg per stock) ---", flush=True)
    print(f"{'Sector':<15}{'N':>4}{'B&H CAGR':>11}{'Strat Ret':>11}"
          f"{'Unhedged':>11}{'Trades':>8}{'WinRate':>9}", flush=True)
    for sec, r in g.iterrows():
        print(f"{sec:<15}{int(r['n']):>4}"
              f"{_fmt(r['avg_bh_cagr'], signed=True):>11}"
              f"{_fmt(r['avg_strat_ret'], signed=True):>11}"
              f"{_fmt(r['avg_unhedged_ret'], signed=True):>11}"
              f"{r['avg_trades']:>8.1f}{_fmt(r['avg_win_rate']):>9}",
              flush=True)

    if failures:
        print(f"\n[warn] {len(failures)} ticker(s) skipped: "
              f"{', '.join(failures)}", flush=True)
    print(f"\nConfig: capital=${args.capital:,.0f}  risk={args.risk_pct:.0%}  "
          f"style={args.style}  fractional={args.fractional}  "
          f"window={args.years}y", flush=True)


def _report(df_out: pd.DataFrame, spy_bh: dict, failures: list, args,
            total: int) -> None:
    """Markdown version of the whole sweep."""
    path = REPORT_DIR / f"five_year_stats_{date.today()}.md"
    lines = [
        "# Five-Year Market Statistics",
        "",
        f"- **Date:** {date.today()}  ",
        f"- **Universe:** {args.universe} ({total} tickers requested, "
        f"{len(df_out)} simulated)  ",
        f"- **Window:** {args.years} years of daily bars  ",
        f"- **Config:** capital ${args.capital:,.0f}, risk "
        f"{args.risk_pct:.0%}, style `{args.style}`, "
        f"fractional={args.fractional}",
        "",
        "Strategy = the engine's conservative paired book (MACD+RSI pullback "
        "entries, 1.5xATR stop, TP1 scale-out, ratchet trail, SPY-regime "
        "sizing, SH inverse-ETF hedge). Buy & Hold uses closing prices "
        "(dividends not modelled).",
        "",
        "## Leaderboard (by engine strategy final equity)",
        "",
        "| # | Ticker | Sector | B&H CAGR | B&H MaxDD | Best Yr | "
        "Strat Ret | Strat DD | Trades | WinRate | Unhedged Ret |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for i, (_, r) in enumerate(df_out.iterrows(), 1):
        lines.append(
            f"| {i} | {r['ticker']} | {r['sector']} | "
            f"{_fmt(r['bh_cagr_pct'], signed=True)} | "
            f"{_fmt(r['bh_max_dd_pct'], signed=True)} | "
            f"{_fmt(r['bh_best_year_pct'], signed=True)} | "
            f"{_fmt(r['strat_ret_pct'], signed=True)} | "
            f"{_fmt(r['strat_max_dd_pct'], signed=True)} | "
            f"{r['strat_trades']} | {_fmt(r['strat_win_rate_pct'])} | "
            f"{_fmt(r['unhedged_ret_pct'], signed=True)} |")
    lines += [
        "",
        "## Benchmark — SPY buy & hold",
        "",
        f"CAGR {_fmt(spy_bh.get('bh_cagr_pct'), signed=True)} · "
        f"vol {_fmt(spy_bh.get('bh_vol_pct'))} · "
        f"Sharpe {_fmt(spy_bh.get('bh_sharpe'))} · "
        f"MaxDD {_fmt(spy_bh.get('bh_max_dd_pct'), signed=True)} · "
        f"best yr {_fmt(spy_bh.get('bh_best_year_pct'), signed=True)} · "
        f"worst yr {_fmt(spy_bh.get('bh_worst_year_pct'), signed=True)}",
        "",
        "## Sector rollup (avg per stock)",
        "",
        "| Sector | N | B&H CAGR | Strat Ret | Unhedged | Trades | "
        "WinRate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    g = df_out.groupby("sector").agg(
        n=("ticker", "count"), avg_bh_cagr=("bh_cagr_pct", "mean"),
        avg_strat=("strat_ret_pct", "mean"),
        avg_un=("unhedged_ret_pct", "mean"),
        avg_tr=("strat_trades", "mean"),
        avg_wr=("strat_win_rate_pct", "mean"),
    ).sort_values("avg_strat", ascending=False)
    for sec, r in g.iterrows():
        lines.append(f"| {sec} | {int(r['n'])} | "
                     f"{_fmt(r['avg_bh_cagr'], signed=True)} | "
                     f"{_fmt(r['avg_strat'], signed=True)} | "
                     f"{_fmt(r['avg_un'], signed=True)} | "
                     f"{r['avg_tr']:.1f} | {_fmt(r['avg_wr'])} |")
    if failures:
        lines += ["", f"## Skipped ({len(failures)})", "",
                  ", ".join(failures)]
    path.write_text("\n".join(lines) + "\n")
    print(f"[saved] {path}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="5-year stats for the whole market universe")
    ap.add_argument("--universe", default="wide", choices=["core", "wide"])
    ap.add_argument("--years", type=int, default=5)
    ap.add_argument("--capital", type=float, default=10_000.0)
    ap.add_argument("--risk-pct", type=float, default=0.02)
    ap.add_argument("--style", default="conservative",
                    choices=["conservative", "bold"])
    ap.add_argument("--no-fractional", dest="fractional",
                    action="store_false", default=True)
    ap.add_argument("--limit", type=int, default=0,
                    help="only first N tickers (smoke test)")
    run(ap.parse_args())


if __name__ == "__main__":
    main()



