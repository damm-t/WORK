"""
Hedging Backtester — OOP edition
================================
Simulates the paired strategy (Long alpha + beta hedge) and compares it
against an unhedged book over identical rules.

Architecture:
    SimulationConfig      frozen dataclass holding every tunable
    PairStrategySimulator aligns data, evaluates entries/exits bar-by-bar,
                          returns (equity_curve, trades)
    run_comparison()      orchestrates fetch -> simulate -> report

Two entry styles share one engine:

    conservative  MACD-cross + RSI 35-65 pullback above SMA50.
                  1.5xATR stop -> TP1 scale-out at 2xATR -> 1.5xATR trail.
    bold          20-day-high breakout on >=1.5x volume surge, MACD>0.
                  2.0xATR stop, NO scale-out, immediate 2.0xATR trail.

Fractional shares are supported for small accounts (e.g. $100), and every
closed trade is charged a round-trip transaction cost from risk.cost_model.

Usage:
    python backtest/hedging_backtester.py --ticker NVDA --start 2026-05-26 \
        --end 2026-08-25 --capital 100 --fractional --style bold --risk-pct 0.05
"""

import argparse
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # direct-run import fix

from market.price_fetcher import fetch_prices
from market.technicals import TechnicalIndicators as TI
from risk.cost_model import round_trip_cost

# --- Exit geometry: conservative style (mirrors risk/hedging_engine.py) -------
STOP_ATR_MULT = 1.5
TP1_ATR_MULT = 2.0
TRAIL_ATR_MULT = 1.5
TP1_SCALE_OUT_PCT = 0.50

# --- Bold-style overrides ------------------------------------------------------
BOLD_STOP_ATR_MULT = 2.0
BOLD_TRAIL_ATR_MULT = 2.0
BREAKOUT_LOOKBACK = 20
VOLUME_SURGE_MULT = 1.5

# --- Regime multipliers (mirrors market/beta_calculator.py) -------------------
REGIME_BULL_MULT = 0.25
REGIME_BEAR_VOL_THRESHOLD = 0.25   # annualized vol above which = panic
REGIME_BEAR_MULT = 0.85
REGIME_NEUTRAL_MULT = 0.50


@dataclass(frozen=True)
class SimulationConfig:
    """Every tunable for one simulation pass."""
    capital: float = 10_000.0
    hedged: bool = True
    risk_pct: float = 0.02
    fractional: bool = False
    style: str = "conservative"          # 'conservative' | 'bold'
    warmup_bars: int = 60
    beta_window: int = 60


class PairStrategySimulator:
    """Bar-by-bar simulation of one ticker's Long(+hedge) strategy."""

    def __init__(self, df_asset: pd.DataFrame, df_bench: pd.DataFrame,
                 df_hedge: pd.DataFrame, cfg: SimulationConfig):
        self.cfg = cfg
        idx = df_asset.index.intersection(df_bench.index).intersection(df_hedge.index)
        if len(idx) < 70:
            raise ValueError("insufficient overlapping bars (<70)")

        self.dates = idx
        self.asset = df_asset.loc[idx]
        self.bench_close = df_bench["Close"].loc[idx]
        self.hedge_close = df_hedge["Close"].loc[idx]

        close = self.asset["Close"]
        self.close = close
        self.high = self.asset["High"]
        self.low = self.asset["Low"]

        self.rsi = TI.rsi(close)
        self.macd_line, self.macd_signal = TI.macd(close)
        self.atr = TI.atr(self.asset)
        self.sma50 = TI.sma(close, 50)
        self.breakout_high = TI.prior_rolling_high(self.high, BREAKOUT_LOOKBACK)
        # Bold entries compare today's volume against the PRIOR average:
        self.vol_avg = TI.avg_volume(self.asset["Volume"], BREAKOUT_LOOKBACK,
                                     exclude_current=True)

        self._ret_asset = close.pct_change()
        self._ret_bench = self.bench_close.pct_change()

    # ------------------------------------------------------------------ beta --
    def _rolling_beta(self, i: int) -> float:
        lo = max(0, i - self.cfg.beta_window)
        pair = pd.concat([self._ret_asset.iloc[lo:i + 1],
                          self._ret_bench.iloc[lo:i + 1]], axis=1).dropna()
        bench_var = float(pair.iloc[:, 1].var()) if len(pair) else 0.0
        if len(pair) < 20 or bench_var == 0.0:
            return 1.0
        return float(pair.cov().iloc[0, 1] / bench_var)

    # ---------------------------------------------------------------- regime --
    @staticmethod
    def _regime_multiplier(bench_close: pd.Series, i: int) -> float:
        window = bench_close.iloc[max(0, i - 59):i + 1]
        if len(window) < 50:
            return REGIME_NEUTRAL_MULT
        price = window.iloc[-1]
        sma20 = window.tail(20).mean()
        sma60 = window.mean()
        vol20 = window.pct_change().dropna().tail(20).std() * math.sqrt(252)

        if price > sma20 and sma20 > sma60:
            return REGIME_BULL_MULT
        if price < sma60 or vol20 > REGIME_BEAR_VOL_THRESHOLD:
            return REGIME_BEAR_MULT
        return REGIME_NEUTRAL_MULT

    # ----------------------------------------------------------------- entry --
    def _style_params(self) -> Dict[str, float]:
        if self.cfg.style == "bold":
            return {"stop_mult": BOLD_STOP_ATR_MULT,
                    "trail_mult": BOLD_TRAIL_ATR_MULT}
        return {"stop_mult": STOP_ATR_MULT, "trail_mult": TRAIL_ATR_MULT}

    def _entry_signal(self, i: int, price: float) -> bool:
        macd_line_i = float(self.macd_line.iloc[i])
        if self.cfg.style == "bold":
            prev_high = float(self.breakout_high.iloc[i]) \
                if not pd.isna(self.breakout_high.iloc[i]) else float("nan")
            vol_avg = float(self.vol_avg.iloc[i]) \
                if not pd.isna(self.vol_avg.iloc[i]) else 0.0
            volume_surge = vol_avg > 0 and \
                float(self.asset["Volume"].iloc[i]) >= VOLUME_SURGE_MULT * vol_avg
            return (prev_high == prev_high and price >= prev_high
                    and volume_surge and macd_line_i > 0.0)

        macd_ok = macd_line_i > float(self.macd_signal.iloc[i])
        rsi_ok = 35.0 < float(self.rsi.iloc[i]) < 65.0
        trend_ok = price > float(TI.sma(self.close, 50).iloc[i])
        return macd_ok and rsi_ok and trend_ok

    # ------------------------------------------------------------------- run --
    def run(self) -> Tuple[pd.Series, List[Dict[str, Any]]]:
        cfg = self.cfg
        params = self._style_params()
        is_bold = cfg.style == "bold"

        cash = cfg.capital
        shares = 0.0
        entry = stop = tp1 = atr_entry = highest = cost_basis = 0.0
        trail_mult = 0.0
        tp1_done = False
        hedge_shares = 0.0
        open_trade: Optional[Dict[str, Any]] = None
        trades: List[Dict[str, Any]] = []
        curve: Dict[pd.Timestamp, float] = {}

        for i in range(len(self.dates)):
            price = float(self.close.iloc[i])
            hi = float(self.high.iloc[i])
            lo = float(self.low.iloc[i])
            sh_price = float(self.hedge_close.iloc[i])

            # ---------- 1) manage the open Long leg ----------
            if shares > 0:
                highest = max(highest, hi)
                rt_cost = float((open_trade or {}).get("rt_cost", 0.0) or 0.0)

                if lo <= stop:                                   # stop hit
                    proceeds = shares * stop
                    cash += proceeds
                    trades.append({**open_trade, "exit": round(stop, 2),
                                   "pnl": round(proceeds - cost_basis - rt_cost, 2),
                                   "result": "stop"})
                    shares = 0.0
                    if cfg.hedged and hedge_shares > 0:          # unwind hedge
                        cash += hedge_shares * sh_price
                        hedge_shares = 0.0
                elif hi >= tp1 and not tp1_done:                 # TP1 scale-out
                    sell_qty = (shares * TP1_SCALE_OUT_PCT) if cfg.fractional \
                        else int(shares * TP1_SCALE_OUT_PCT)
                    if sell_qty > 0:
                        cash += sell_qty * tp1
                        cost_basis -= cost_basis * (sell_qty / shares)
                        shares -= sell_qty
                        tp1_done = True
                if shares > 0 and tp1_done:                      # ratchet runner
                    stop = max(stop, highest - trail_mult * atr_entry)

            # ---------- 2) new entry ----------
            if shares == 0 and i >= cfg.warmup_bars:
                a_i = float(self.atr.iloc[i])
                if a_i > 0 and self._entry_signal(i, price):
                    equity_now = cash + hedge_shares * sh_price
                    stop_dist = params["stop_mult"] * a_i
                    raw_qty = (equity_now * cfg.risk_pct) / stop_dist
                    qty = float(round(raw_qty, 4)) if cfg.fractional else int(raw_qty)
                    if qty > 0 and qty * price <= equity_now * 0.95:
                        beta = self._rolling_beta(i)
                        mult = self._regime_multiplier(self.bench_close, i)

                        cash -= qty * price
                        cost_basis = qty * price
                        shares, entry = qty, price
                        stop = entry - stop_dist
                        atr_entry, highest = a_i, hi
                        trail_mult = params["trail_mult"]
                        if is_bold:
                            tp1 = float("inf")       # pure runner, no scale-out
                            tp1_done = True
                        else:
                            tp1 = entry + TP1_ATR_MULT * stop_dist
                            tp1_done = False

                        if cfg.hedged:               # ---- paired hedge leg ----
                            target_val = qty * price * abs(beta) * mult
                            add = ((target_val / sh_price) if cfg.fractional
                                   else int(target_val / sh_price)) if sh_price > 0 else 0
                            if add > 0:
                                hedge_shares += add
                                cash -= add * sh_price

                        open_trade = {
                            "entry_date": str(self.dates[i].date()),
                            "entry": round(entry, 2),
                            "qty": qty,
                            "rt_cost": round(
                                round_trip_cost(entry, max(1, round(qty)))["total"], 4),
                            "beta": round(beta, 2) if cfg.hedged else None,
                            "regime_mult": mult if cfg.hedged else None,
                        }

            # ---------- 3) mark to market ----------
            curve[self.dates[i]] = cash + shares * price + hedge_shares * sh_price

        # ---------- force-close leftovers at the final bar ----------
        if shares > 0:
            last_p = float(self.close.iloc[-1])
            cash += shares * last_p
            rt_cost = float((open_trade or {}).get("rt_cost", 0.0) or 0.0)
            trades.append({**open_trade, "exit": round(last_p, 2),
                           "pnl": round(shares * last_p - cost_basis - rt_cost, 2),
                           "result": "eod"})
            if cfg.hedged and hedge_shares > 0:
                cash += hedge_shares * float(self.hedge_close.iloc[-1])
                hedge_shares = 0.0
            curve[self.dates[-1]] = cash

        return pd.Series(curve).sort_index(), trades


def simulate(df_asset: pd.DataFrame, df_bench: pd.DataFrame,
             df_hedge: pd.DataFrame, capital: float = 10_000.0,
             hedged: bool = True, risk_pct: float = 0.02,
             fractional: bool = False, style: str = "conservative"):
    """Convenience wrapper preserving the original functional API."""
    cfg = SimulationConfig(capital=capital, hedged=hedged, risk_pct=risk_pct,
                           fractional=fractional, style=style)
    return PairStrategySimulator(df_asset, df_bench, df_hedge, cfg).run()


# ------------------------------------------------------------- reporting ----
def performance_metrics(equity_curve: pd.Series, trades: List[dict]) -> dict:
    total_return = equity_curve.iloc[-1] / equity_curve.iloc[0] - 1.0
    drawdowns = equity_curve / equity_curve.cummax() - 1.0
    daily_ret = equity_curve.pct_change().dropna()
    sharpe = (float(daily_ret.mean() / daily_ret.std() * math.sqrt(252))
              if daily_ret.std() > 0 else 0.0)
    wins = [t for t in trades if t.get("pnl", 0.0) > 0]
    return {
        "final_equity": round(float(equity_curve.iloc[-1]), 2),
        "total_return_pct": round(total_return * 100, 2),
        "max_drawdown_pct": round(float(drawdowns.min()) * 100, 2),
        "sharpe": round(sharpe, 2),
        "num_trades": len(trades),
        "win_rate_pct": round(100.0 * len(wins) / len(trades), 1) if trades else 0.0,
    }


# ------------------------------------------------------------ data windowing -
def _strip_tz(df: pd.DataFrame) -> pd.DataFrame:
    if getattr(df.index, "tz", None) is not None:
        df = df.copy()
        df.index = df.index.tz_localize(None)
    return df


def _trim(df: pd.DataFrame, start=None, end=None) -> pd.DataFrame:
    df = _strip_tz(df)
    if start is not None:
        df = df[df.index >= pd.Timestamp(start)]
    if end is not None:
        df = df[df.index <= pd.Timestamp(end)]
    return df


def _window(curve: pd.Series, trades: list, start_ts, end_ts):
    c = curve[(curve.index >= start_ts) & (curve.index <= end_ts)] if len(curve) else curve
    s, e = str(pd.Timestamp(start_ts).date()), str(pd.Timestamp(end_ts).date())
    t = [x for x in trades if s <= x.get("entry_date", "") <= e]
    return c, t


# ------------------------------------------------------------ orchestration --
def run_comparison(ticker: str = "NVDA", period: str = "2y",
                   capital: float = 10_000.0, risk_pct: float = 0.02,
                   start: str = None, end: str = None,
                   fractional: bool = False, style: str = "conservative",
                   quiet: bool = False) -> dict:
    """
    Fetches data, runs BOTH books (unhedged vs beta-hedged) over the same
    window, and reports metrics. With --start/--end, ~200 days of lead-in
    data is fetched so indicators are warm before the window opens; reported
    metrics then cover only the requested window.
    """
    fetch_start = (pd.Timestamp(start) - pd.Timedelta(days=200)) if start else None
    fetch_end = pd.Timestamp(end) if end else None
    if start:
        years_back = max(1, math.ceil((pd.Timestamp.today() - fetch_start).days / 365.25))
        period = f"{years_back}y"

    label = f"{start or 'inception'} -> {end or 'today'}"
    if not quiet:
        print(f"\n=== Hedging Backtest: {ticker} [{style}] vs SPY "
              f"(period={period}, window={label}) ===")

    df_asset = _trim(fetch_prices(ticker.upper(), period=period, interval="1d"),
                     fetch_start, fetch_end)
    df_bench = _trim(fetch_prices("SPY", period=period, interval="1d"),
                     fetch_start, fetch_end)
    df_hedge = _trim(fetch_prices("SH", period=period, interval="1d"),
                     fetch_start, fetch_end)

    for name, df in (("asset", df_asset), ("benchmark", df_bench)):
        if df.empty:
            raise SystemExit(f"[hedging_backtester] No {name} data — aborting.")

    # Synthetic -1x SPY proxy if the inverse ETF is unavailable
    if df_hedge.empty or len(df_hedge) < 30:
        if not quiet:
            print("[hedging_backtester] SH unavailable -> synthesizing -1x SPY.")
        df_hedge = df_bench.copy()
        ret = df_bench["Close"].pct_change().fillna(0.0)
        df_hedge["Close"] = df_bench["Close"].iloc[0] * (1.0 - ret).cumprod()
        for col in ("Open", "High", "Low"):
            if col in df_hedge.columns:
                df_hedge[col] = df_hedge["Close"]

    curve_u, trades_u = simulate(df_asset, df_bench, df_hedge, capital,
                                 hedged=False, risk_pct=risk_pct,
                                 fractional=fractional, style=style)
    curve_h, trades_h = simulate(df_asset, df_bench, df_hedge, capital,
                                 hedged=True, risk_pct=risk_pct,
                                 fractional=fractional, style=style)

    # Report only the analysis window (lead-in was just for indicator warmup)
    if start:
        w_end = fetch_end or (curve_u.index[-1] if len(curve_u) else pd.Timestamp.today())
        curve_u, trades_u = _window(curve_u, trades_u, pd.Timestamp(start), w_end)
        curve_h, trades_h = _window(curve_h, trades_h, pd.Timestamp(start), w_end)

    if len(curve_u) < 2 or len(curve_h) < 2:
        raise SystemExit("[hedging_backtester] Not enough data points inside the "
                         "requested window — widen --start/--end.")

    results = {
        "ticker": ticker.upper(),
        "period": period,
        "window": label,
        "style": style,
        "start_equity": capital,
        "unhedged": performance_metrics(curve_u, trades_u),
        "hedged": performance_metrics(curve_h, trades_h),
        "unhedged_trades": trades_u,
        "hedged_trades": trades_h,
    }

    _print_report(results, quiet=quiet)
    return results


def _print_report(results: dict, quiet: bool = False) -> None:
    if quiet:
        return

    hdr = f"{'Metric':<22}{'Unhedged Long':>16}{'Beta-Hedged':>16}"
    print("\n" + "=" * len(hdr))
    print(hdr)
    print("=" * len(hdr))
    for label, key in [("Final Equity ($)", "final_equity"),
                       ("Total Return (%)", "total_return_pct"),
                       ("Max Drawdown (%)", "max_drawdown_pct"),
                       ("Sharpe Ratio", "sharpe"),
                       ("Trades", "num_trades"),
                       ("Win Rate (%)", "win_rate_pct")]:
        u, h = results["unhedged"][key], results["hedged"][key]
        print(f"{label:<22}{u:>16,.2f}{h:>16,.2f}")
    print("=" * len(hdr))

    dd_gain = (results["unhedged"]["max_drawdown_pct"]
               - results["hedged"]["max_drawdown_pct"])
    print(f"Hedge drawdown improvement: {dd_gain:+.2f} percentage points\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Hedging vs Unhedged Backtester")
    parser.add_argument("--ticker", type=str, default="NVDA")
    parser.add_argument("--period", type=str, default="2y")
    parser.add_argument("--capital", type=float, default=10_000.0)
    parser.add_argument("--risk-pct", type=float, default=0.02)
    parser.add_argument("--start", type=str, default=None,
                        help="Analysis window start, YYYY-MM-DD")
    parser.add_argument("--end", type=str, default=None,
                        help="Analysis window end, YYYY-MM-DD")
    parser.add_argument("--fractional", action="store_true",
                        help="Allow fractional shares (tiny accounts)")
    parser.add_argument("--style", choices=["conservative", "bold"],
                        default="conservative")
    args = parser.parse_args()

    run_comparison(ticker=args.ticker, period=args.period,
                   capital=args.capital, risk_pct=args.risk_pct,
                   start=args.start, end=args.end,
                   fractional=args.fractional, style=args.style)


if __name__ == "__main__":
    main()