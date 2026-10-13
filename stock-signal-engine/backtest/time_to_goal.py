"""
Time-to-Goal Simulator — "$100 -> $1,000" honesty check
=======================================================
Bootstraps the tuned profile's OUT-OF-SAMPLE trade R-multiples
(test window 2024-01-01 -> today, NVDA banned) into sequential
compounding paths and answers ONE question:

    "Starting at $100, how long until equity reaches 10x ($1,000)?"

For each per-trade risk level f (fraction of equity risked), each
simulated trade multiplies equity by (1 + f x R). Paths end when they
hit the GOAL (10x), get RUINED (drawn down to the ruin line first), or
run out of trades (censored).

Percentages are scale-free, so the result applies to $100 exactly like
to $10,000 — PROVIDED fractional shares are on (whole shares cannot
even buy one share of most mega-caps at $100) and the notional cap is
raised so the intended risk is actually realizable.

Usage:
    python backtest/time_to_goal.py                          # defaults
    python backtest/time_to_goal.py --ruin 0.2 --risks 0.05,0.10,0.15
"""

import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

import backtest.financial_modeling as fm

GOAL_MULT = 10.0          # $100 -> $1,000
RUIN_MULT = 0.5           # default "cut in half first" line (0.2 = accept -80%)
MAX_TRADES = 2000         # ~48y at 41 trades/yr — censoring horizon
N_PATHS = 20_000
RISK_LEVELS = [0.012, 0.02, 0.05, 0.10, 0.15, 0.20, 0.25]
SEED = 42


def tuned_profile() -> fm.Profile:
    """The financial_modeling winner (2026-09-20 report)."""
    return fm.Profile(stop_mult=2.0, tp1_mult=2.0, trail_mult=1.5,
                      tp1_scale=0.5, rsi_max=65.0, trend_filter=True,
                      be_after_tp1=True, hedge=True)


def oos_r_pool(bundles) -> tuple:
    res = fm._simulate_bars(bundles, tuned_profile(), 10_000.0,
                            fractional=True, start=fm.TEST_START, end=None)
    trades = res.get("trades", [])
    pool = np.array([t["r"] for t in trades], dtype=float)
    dates = pd.to_datetime([t["exit_date"] for t in trades])
    span_years = max((dates.max() - dates.min()).days / 365.25, 1e-9)
    tpy = len(trades) / span_years
    return pool, len(trades), tpy, res["metrics"]


def pool_stats(pool: np.ndarray) -> dict:
    wins = pool[pool > 0]
    losses = pool[pool <= 0]
    w = len(wins) / len(pool)
    aw = float(wins.mean()) if len(wins) else 0.0
    al = abs(float(losses.mean())) if len(losses) else 1.0
    kelly = w - (1.0 - w) / (aw / al) if al > 0 else 0.0
    return {"n": len(pool), "win_rate": round(w * 100, 1),
            "mean_r": round(float(pool.mean()), 3),
            "std_r": round(float(pool.std()), 2),
            "avg_win_r": round(aw, 2), "avg_loss_r": round(-al, 2),
            "best_r": round(float(pool.max()), 2),
            "worst_r": round(float(pool.min()), 2),
            "kelly_f": round(kelly, 3)}


def mc_time_to_goal(pool: np.ndarray, f: float, tpy: float,
                    n_paths: int = N_PATHS, seed: int = SEED,
                    goal_mult: float = GOAL_MULT,
                    ruin_mult: float = RUIN_MULT) -> dict:
    rng = np.random.default_rng(seed)
    draws = rng.choice(pool, size=(n_paths, MAX_TRADES), replace=True)
    cum = np.cumprod(1.0 + f * draws, axis=1)

    hit_goal = cum >= goal_mult
    hit_ruin = cum <= ruin_mult
    goal_idx = np.where(hit_goal.any(axis=1),
                        hit_goal.argmax(axis=1), MAX_TRADES)
    ruin_idx = np.where(hit_ruin.any(axis=1),
                        hit_ruin.argmax(axis=1), MAX_TRADES)

    # whichever threshold came FIRST decides the path's fate
    goal_first = (hit_goal.any(axis=1)
                  & (~hit_ruin.any(axis=1) | (goal_idx <= ruin_idx)))

    yrs_goal = goal_idx[goal_first] / tpy
    running_max = np.maximum.accumulate(cum, axis=1)
    dd_full = cum / running_max - 1.0
    # drawdown only up to the point the path ENDED (goal or ruin), so
    # post-goal collapse doesn't pollute the metric
    exit_idx = np.minimum(goal_idx, ruin_idx)
    col_mask = np.arange(MAX_TRADES)[None, :] <= exit_idx[:, None]
    dd_used = np.where(col_mask, dd_full, 0.0).min(axis=1)

    out = {
        "f": f,
        "p_goal_pct": round(100.0 * goal_first.mean(), 1),
        "median_years": (round(float(np.median(yrs_goal)), 1)
                         if goal_first.any() else None),
        "p_ruin_first_pct": round(100.0 * (ruin_first := (
            hit_ruin.any(axis=1) & ~goal_first)).mean(), 1),
        "p_censored_pct": round(100.0 * ((~goal_first) & (~(
            hit_ruin.any(axis=1) & ~goal_first))).mean(), 1),
        "median_max_dd_pct": (round(float(np.median(dd_used[goal_first])) * 100, 1)
                              if goal_first.any() else None),
        "p5_years": (round(float(np.percentile(yrs_goal, 5)), 1)
                     if goal_first.any() else None),
        "p95_years": (round(float(np.percentile(yrs_goal, 95)), 1)
                      if goal_first.any() else None),
    }
    for limit, key in [(1, "p_le_1y_pct"), (3, "p_le_3y_pct"),
                       (5, "p_le_5y_pct"), (10, "p_le_10y_pct")]:
        out[key] = round(float((goal_first & (goal_idx / tpy <= limit)
                                ).mean() * 100), 1)
    return out


def growth_optimal_f(pool: np.ndarray) -> tuple:
    """Scan f for the maximum expected log-growth per trade E[ln(1+fR)].

    Grid stops at 0.40 because the worst observed R is -2.25 (1 + 0.40 x
    -2.25 = 0.10 > 0) — beyond ~44% some single trade would bankrupt the
    account outright (log undefined).
    """
    best_f, best_g = 0.0, -1e9
    grid = np.arange(0.005, 0.4005, 0.005)
    curve = []
    for f in grid:
        g = float(np.mean(np.log1p(f * pool)))
        curve.append((f, g))
        if g > best_g:
            best_f, best_g = f, g
    return best_f, best_g, curve


def savings_months(start: float, monthly: float, goal: float,
                   annual_return: float) -> int:
    eq, months = start, 0
    while eq < goal and months < 600:
        eq *= (1.0 + annual_return) ** (1.0 / 12.0)
        eq += monthly
        months += 1
    return months


def main() -> None:
    ap = argparse.ArgumentParser(description="$100 -> $1,000 time-to-goal MC")
    ap.add_argument("--goal", type=float, default=GOAL_MULT,
                    help="target multiple (10 = 10x)")
    ap.add_argument("--ruin", type=float, default=RUIN_MULT,
                    help="equity floor that ends the path (0.2 = accept -80%%)")
    ap.add_argument("--risks", type=str, default=None,
                    help="comma list of per-trade risk levels, e.g. 0.05,0.10")
    ap.add_argument("--paths", type=int, default=N_PATHS)
    args = ap.parse_args()

    risks = ([float(x) for x in args.risks.split(",")] if args.risks
             else RISK_LEVELS)
    print(f"=== TIME-TO-GOAL: 1x -> {args.goal:.0f}x "
          f"(ruin floor at {1 - args.ruin:.0%} loss) ===", flush=True)
    tickers = {t: s for s, ts in fm.CORE_UNIVERSE.items()
               for t in ts if t not in fm.BANNED}
    df_bench = fm.load_ohlcv(fm.BENCH, 11)
    df_hedge = fm.load_ohlcv(fm.HEDGE, 11)
    bundles = []
    for t in sorted(tickers):
        df = fm.load_ohlcv(t, 11)
        b = fm.build_bundle(t, tickers[t], df, df_bench, df_hedge)
        if b is not None:
            bundles.append(b)
    print(f"[data] {len(bundles)} bundles", flush=True)

    pool, n_trades, tpy, metrics = oos_r_pool(bundles)
    st = pool_stats(pool)
    best_f, best_g, _ = growth_optimal_f(pool)
    print(f"[pool] OOS trades n={n_trades} (~{tpy:.0f}/yr)  "
          f"WR {st['win_rate']}%  meanR {st['mean_r']:+.3f}  "
          f"std {st['std_r']}  avgWin {st['avg_win_r']:+.2f}R  "
          f"avgLoss {st['avg_loss_r']:+.2f}R  worst {st['worst_r']:+.2f}R  "
          f"Kelly f*={st['kelly_f']:.1%}", flush=True)
    print(f"[growth-optimal] f* = {best_f:.1%} "
          f"(E[ln(1+fR)] = {best_g:.4f}/trade -> {best_g * tpy:.3f}/yr "
          f"-> ln({args.goal:.0f})/{best_g * tpy:.3f} = "
          f"{np.log(args.goal) / (best_g * tpy):.1f}y theoretical median)",
          flush=True)
    print(f"[check] OOS test metrics: WR {metrics['win_rate_pct']}%  "
          f"ret {metrics['total_return_pct']:+.2f}%  "
          f"DD {metrics['max_dd_pct']}%", flush=True)

    rows = [mc_time_to_goal(pool, f, tpy, n_paths=args.paths,
                            goal_mult=args.goal, ruin_mult=args.ruin)
            for f in risks]
    df = pd.DataFrame(rows)

    hdr = (f"{'risk/trade':>10} {'P(goal 1st)':>11} {'med yrs':>9} "
           f"{'P(<=1y)':>8} {'P(<=3y)':>8} {'P(<=5y)':>8} {'P(<=10y)':>9} "
           f"{'P(ruin 1st)':>12} {'med maxDD':>10}")
    print("\n" + hdr, flush=True)
    print("-" * len(hdr), flush=True)
    for _, r in df.iterrows():
        my = f"{r['median_years']:.1f}" if r["median_years"] is not None else "—"
        dd = f"{r['median_max_dd_pct']:.0f}%" if r["median_max_dd_pct"] is not None else "—"
        print(f"{r['f']:>9.1%} {r['p_goal_pct']:>10.1f}% {my:>9} "
              f"{r['p_le_1y_pct']:>7.1f}% {r['p_le_3y_pct']:>7.1f}% "
              f"{r['p_le_5y_pct']:>7.1f}% {r['p_le_10y_pct']:>8.1f}% "
              f"{r['p_ruin_first_pct']:>11.1f}% {dd:>10}", flush=True)

    # --- the savings reality check at $100 scale -------------------------
    print("\n--- reality check: deposits vs trading at $100 scale ---", flush=True)
    for monthly in (50, 100, 200):
        m0 = savings_months(100.0, monthly, 1000.0, 0.0)
        m5 = savings_months(100.0, monthly, 1000.0, 0.059)
        print(f"  $100 start + ${monthly:>3}/mo -> $1,000 in "
              f"{m0} months (0% return) / {m5} months (at the system's "
              f"OOS ~5.9%/yr)", flush=True)

    # --- persist ---------------------------------------------------------
    out_dir = fm.REPORT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    md = out_dir / f"time_to_goal_{date.today()}.md"
    lines = [
        f"# Time-to-Goal: 1x -> {args.goal:.0f}x "
        f"(ruin floor at {1 - args.ruin:.0%} loss)",
        "",
        f"- Bootstrapped from {st['n']} OOS trades (~{tpy:.0f}/yr), "
        f"WR {st['win_rate']}%, mean {st['mean_r']:+.3f}R, "
        f"Kelly f* {st['kelly_f']:.1%}",
        f"- Growth-optimal risk f* = {best_f:.1%} "
        f"(E[ln(1+fR)] = {best_g:.4f}/trade)",
        f"- Goal {args.goal:.0f}x · ruin floor {args.ruin:.2f}x · "
        f"{args.paths:,} paths per risk level",
        "",
        "| risk/trade | P(goal 1st) | med yrs | p5–p95 yrs | P(<=1y) | "
        "P(<=3y) | P(<=5y) | P(<=10y) | P(ruin 1st) | med maxDD |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in df.iterrows():
        my = f"{r['median_years']:.1f}" if r["median_years"] is not None else "—"
        dd = f"{r['median_max_dd_pct']:.0f}%" if r["median_max_dd_pct"] is not None else "—"
        rng = (f"{r['p5_years']}–{r['p95_years']}"
               if r.get("p5_years") is not None else "—")
        lines.append(f"| {r['f']:.1%} | {r['p_goal_pct']}% | {my} | {rng} | "
                     f"{r['p_le_1y_pct']}% | {r['p_le_3y_pct']}% | "
                     f"{r['p_le_5y_pct']}% | {r['p_le_10y_pct']}% | "
                     f"{r['p_ruin_first_pct']}% | {dd} |")
    lines += [
        "",
        "Notes: fractional shares required at $100 (whole shares cannot buy",
        "most universe names); the default 30% notional cap limits realized",
        "risk to ~1.2%/trade — raise MAX_POSITION_NOTIONAL_PCT to realize",
        "higher f. Cash accounts are 1x leverage: with 2xATR stops (~4-6% of",
        "price) the max REALIZABLE per-trade risk at $100 is ~4-6%; beyond",
        "that needs a margin account (broker minimum usually $2k+).",
        f"Growth-optimal f* = {best_f:.1%} — betting beyond it makes the",
        "median slower, not faster.",
        "",
        "Past performance does not guarantee future results.",
    ]
    md.write_text("\n".join(lines) + "\n")
    print(f"\n[saved] {md}", flush=True)


if __name__ == "__main__":
    main()
