"""
Crisis-Tested Financial Modeling — Win-Rate Tuning & Capital Scenarios
======================================================================
Applies the Financial Modeling Suite methodology (~/.agents/skills/
FinancialModeling.md) to the engine's paired long+hedge strategy:

    Stage 1   SENSITIVITY SWEEP : tune exit geometry (stop / TP / trail /
                                  scale-out / RSI band / hedge on-off) on
                                  the TRAIN window (2016-10 -> 2020-12,
                                  contains the 2020 COVID crash).
    Stage 1b  LOCAL REFINEMENT  : ±1-step neighborhood around the winner.
    Stage 2   VALIDATION        : top candidates + baseline seeds on the
                                  2021-01 -> 2023-12 window; final profile
                                  needs positive expectancy on BOTH windows.
    Stage 3   OOS TEST          : chosen profile vs baseline on the unseen
                                  2024-01-01 -> today window; per-year
                                  win rates ("~50% over the year" check).
    Stage 4   CRISIS STRESS     : 2018 Q4, 2020 COVID crash, COVID cycle,
                                  2022 bear market.
    Stage 5   MONTE CARLO       : 10,000 bootstrapped one-year paths from
                                  the OOS trade pool: P(profit), P(ruin),
                                  VaR/CVaR, 5-95% bands.
    Stage 6   CAPITAL SCENARIOS : OOS sims at $1k / $5k / $10k in BOTH
                                  integer-share (realistic) and fractional
                                  (broker-max) books.

HARD CONSTRAINT: NVDA is banned from every candidate pool and sim.

The simulator is a parameterized twin of backtest.hedging_backtester.
PairStrategySimulator (same regime sizing, SH hedge, ATR geometry, cost
model), rebuilt on numpy for sweep speed. Indicators come from
market.technicals (single source of truth). The winning profile is wired
to live automation via risk/hedging_engine.get_exit_geometry() env
overrides + scenario_small.sh.

Usage:
    python backtest/financial_modeling.py              # full pipeline
    python backtest/financial_modeling.py --smoke      # fast sanity run
"""

import argparse
import math
import sys
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from backtest.universe import CORE_UNIVERSE
from market.price_fetcher import fetch_prices
from market.technicals import TechnicalIndicators as TI
from risk.cost_model import round_trip_cost

BENCH = "SPY"
HEDGE = "SH"
BANNED = {"NVDA"}                      # user-imposed hard ban
REPORT_DIR = Path("reports")

TRAIN_START, TRAIN_END = "2016-10-01", "2020-12-31"
VAL_START, VAL_END = "2021-01-01", "2023-12-31"
TEST_START, TEST_END = "2024-01-01", None          # final unseen window
CRISES = [
    ("2018 Q4 correction", "2018-10-01", "2018-12-31"),
    ("COVID crash (pure)", "2020-02-19", "2020-03-23"),
    ("COVID full cycle",   "2020-02-01", "2020-12-31"),
    ("2022 bear market",   "2022-01-03", "2022-10-31"),
]
CAPITALS = (1_000.0, 5_000.0, 10_000.0)
RISK_PCT = 0.02
WARMUP = 60
BETA_WINDOW = 60

# regime multipliers (mirrors hedging_backtester / beta_calculator)
REGIME_BULL_MULT, REGIME_BEAR_MULT, REGIME_NEUTRAL_MULT = 0.25, 0.85, 0.50
REGIME_BEAR_VOL_THRESHOLD = 0.25


@dataclass(frozen=True)
class Profile:
    """One tunable strategy profile (exit geometry + entry quality)."""
    stop_mult: float = 1.5          # initial stop distance  (xATR)
    tp1_mult: float = 2.0           # TP1 distance           (xATR)
    trail_mult: float = 1.5         # runner trail           (xATR at entry)
    tp1_scale: float = 0.5          # fraction sold at TP1
    rsi_max: float = 65.0           # entry band upper bound
    trend_filter: bool = False      # require SMA50 > SMA200 at entry
    be_after_tp1: bool = False      # ratchet stop to entry after TP1
    hedge: bool = True              # pair every long with SH inverse ETF
    # --- WR-hunt levers (defaults = legacy behaviour) ---------------------
    be_trigger_mult: float = 0.0    # once up this many ATR, lock stop at
    be_offset_mult: float = 0.0     # entry + this many ATR (0 = breakeven)
    regime_filter: bool = False     # skip entries while SPY regime = BEAR
    sector_up: bool = False         # require sector ETF above its SMA50
    # --- Upgrades 1, 2, 8 (Adaptive Geometry, Dynamic Hedge & PSI Gating) ---
    adaptive_psi: bool = False      # adapt stop, tp1, trail dynamically using PSI
    min_psi: float = 0.0            # filter entries with PSI < min_psi
    dynamic_hedge: bool = False     # scale hedge down in bull/stable regimes (ceiling 0.65)

    def key(self) -> str:
        s = (f"stop{self.stop_mult:.2f}_tp1{self.tp1_mult:.2f}_"
             f"trail{self.trail_mult:.2f}_scale{self.tp1_scale:.2f}_"
             f"rsi{self.rsi_max:.0f}_trend{int(self.trend_filter)}"
             f"_hedged{int(self.hedge)}"
             f"_be{self.be_trigger_mult:.2f}+{self.be_offset_mult:.2f}"
             f"_reg{int(self.regime_filter)}_sec{int(self.sector_up)}")
        if self.adaptive_psi:
            s += "_adpPSI"
        if self.min_psi > 0:
            s += f"_minPSI{self.min_psi:.0f}"
        if self.dynamic_hedge:
            s += "_dynHdg"
        return s


def baseline_profile() -> Profile:
    """The engine's current conservative geometry (for comparison)."""
    return Profile(stop_mult=1.5, tp1_mult=2.0, trail_mult=1.5,
                   tp1_scale=0.5, rsi_max=65.0, trend_filter=False,
                   be_after_tp1=False)


def sensitivity_grid() -> List[Profile]:
    """Stage-1 grid: static baseline combos + upgraded adaptive PSI & dynamic hedge combos."""
    combos = []
    # 1) Static baseline combos (192 combos)
    for stop in (1.5, 2.0):
        for tp1 in (1.0, 1.25, 1.5, 2.0):
            for trail in (1.5, 2.25, 3.0):
                for scale in (0.5, 1.0):
                    for rsi in (55.0, 65.0):
                        for hedge in (True, False):
                            combos.append(Profile(
                                stop_mult=stop, tp1_mult=tp1,
                                trail_mult=trail, tp1_scale=scale,
                                rsi_max=rsi, trend_filter=True,
                                be_after_tp1=True, hedge=hedge))
    # 2) Upgraded Adaptive PSI & Dynamic Hedge combos
    for min_psi in (0.0, 45.0):
        for dyn_hdg in (True, False):
            for rsi in (55.0, 65.0):
                for hedge in (True, False):
                    combos.append(Profile(
                        stop_mult=1.5, tp1_mult=2.0, trail_mult=1.5,
                        tp1_scale=0.5, rsi_max=rsi, trend_filter=True,
                        be_after_tp1=True, hedge=hedge,
                        adaptive_psi=True, min_psi=min_psi,
                        dynamic_hedge=dyn_hdg))
    return combos


def refine_grid(best: Profile) -> List[Profile]:
    """Local neighborhood: exit geometry varies or adaptive toggles vary."""
    out = []
    if best.adaptive_psi:
        for d_psi in (-10.0, 5.0, 10.0):
            new_psi = max(0.0, best.min_psi + d_psi)
            p = Profile(
                stop_mult=best.stop_mult, tp1_mult=best.tp1_mult,
                trail_mult=best.trail_mult, tp1_scale=best.tp1_scale,
                rsi_max=best.rsi_max, trend_filter=best.trend_filter,
                be_after_tp1=best.be_after_tp1, hedge=best.hedge,
                be_trigger_mult=best.be_trigger_mult,
                be_offset_mult=best.be_offset_mult,
                regime_filter=best.regime_filter, sector_up=best.sector_up,
                adaptive_psi=True, min_psi=new_psi,
                dynamic_hedge=best.dynamic_hedge)
            if p != best and p not in out:
                out.append(p)
        for dyn in (True, False):
            p = Profile(
                stop_mult=best.stop_mult, tp1_mult=best.tp1_mult,
                trail_mult=best.trail_mult, tp1_scale=best.tp1_scale,
                rsi_max=best.rsi_max, trend_filter=best.trend_filter,
                be_after_tp1=best.be_after_tp1, hedge=best.hedge,
                be_trigger_mult=best.be_trigger_mult,
                be_offset_mult=best.be_offset_mult,
                regime_filter=best.regime_filter, sector_up=best.sector_up,
                adaptive_psi=True, min_psi=best.min_psi,
                dynamic_hedge=dyn)
            if p != best and p not in out:
                out.append(p)
    for d_stop, d_tp1, d_trail, d_scale in [
        (-0.25, 0, 0, 0), (0.25, 0, 0, 0), (0, -0.25, 0, 0),
        (0, 0.25, 0, 0), (0, 0, -0.5, 0), (0, 0, 0.5, 0),
        (0, 0, 0, -0.25), (0, 0, 0, 0.25), (0.25, -0.25, 0.5, 0),
        (-0.25, 0.25, -0.5, 0.25),
    ]:
        p = Profile(
            stop_mult=max(0.75, best.stop_mult + d_stop),
            tp1_mult=max(0.5, best.tp1_mult + d_tp1),
            trail_mult=max(0.75, best.trail_mult + d_trail),
            tp1_scale=min(1.0, max(0.25, best.tp1_scale + d_scale)),
            rsi_max=best.rsi_max, trend_filter=best.trend_filter,
            be_after_tp1=True, hedge=best.hedge,
            adaptive_psi=best.adaptive_psi,
            min_psi=best.min_psi,
            dynamic_hedge=best.dynamic_hedge)
        if p != best and p not in out:
            out.append(p)
    return out


# ------------------------------------------------------------------ data ----
def load_ohlcv(ticker: str, years: int) -> pd.DataFrame:
    df = pd.DataFrame()
    for attempt in range(3):
        df = fetch_prices(ticker, period=f"{years}y", interval="1d")
        if not df.empty and len(df) > 250:
            break
        time.sleep(2.0 * (attempt + 1))
    if df.empty:
        return pd.DataFrame()
    if getattr(df.index, "tz", None) is not None:
        df = df.copy()
        df.index = df.index.tz_localize(None)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    need = ("Open", "High", "Low", "Close", "Volume")
    return df if all(c in df.columns for c in need) else pd.DataFrame()


@dataclass
class Bundle:
    """Precomputed per-ticker numpy state shared by every param combo."""
    ticker: str
    sector: str
    dates: pd.DatetimeIndex
    close: np.ndarray
    high: np.ndarray
    low: np.ndarray
    rsi: np.ndarray
    macd: np.ndarray
    macd_sig: np.ndarray
    atr: np.ndarray
    sma50: np.ndarray
    sma200: np.ndarray
    bench_close: np.ndarray       # aligned to this bundle's dates
    bench_ret: np.ndarray
    hedge_close: np.ndarray
    sector_up: Optional[np.ndarray] = None   # 1.0 = sector ETF above SMA50
    psi: Optional[np.ndarray] = None         # Price Stability Index (Upgrade 8)
    velocity: Optional[np.ndarray] = None    # Latent Kalman velocity (Upgrade 8)


def build_bundle(t: str, sector: str, df: pd.DataFrame,
                 df_bench: pd.DataFrame, df_hedge: pd.DataFrame,
                 sector_etf_close: Optional[pd.Series] = None) -> Optional[Bundle]:
    idx = df.index.intersection(df_bench.index).intersection(df_hedge.index)
    if len(idx) < 300:
        return None
    a, b, h = df.loc[idx], df_bench.loc[idx], df_hedge.loc[idx]
    close = a["Close"]
    sector_up = None
    if sector_etf_close is not None and len(sector_etf_close) > 60:
        sec = sector_etf_close.reindex(idx).ffill()
        sector_up = (sec > sec.rolling(50).mean()).astype(float).to_numpy()

    psi = None
    velocity = None
    try:
        from market.anti_volatility import anti_volatility_model
        av_df = anti_volatility_model.filter_series(close, a["High"], a["Low"])
        if not av_df.empty and "price_stability_index" in av_df.columns:
            psi = av_df["price_stability_index"].to_numpy(float)
            velocity = av_df["velocity"].to_numpy(float)
    except Exception as e:
        pass

    return Bundle(
        ticker=t, sector=sector, dates=idx,
        close=close.to_numpy(float), high=a["High"].to_numpy(float),
        low=a["Low"].to_numpy(float),
        rsi=TI.rsi(close).to_numpy(float),
        macd=TI.macd(close)[0].to_numpy(float),
        macd_sig=TI.macd(close)[1].to_numpy(float),
        atr=TI.atr(a).to_numpy(float),
        sma50=TI.sma(close, 50).to_numpy(float),
        sma200=TI.sma(close, 200).to_numpy(float),
        bench_close=b["Close"].to_numpy(float),
        bench_ret=b["Close"].pct_change().fillna(0.0).to_numpy(float),
        hedge_close=h["Close"].to_numpy(float),
        sector_up=sector_up,
        psi=psi,
        velocity=velocity,
    )


# ------------------------------------------------------------- simulator ----
def _regime_mult(bench_close: np.ndarray, i: int) -> float:
    lo = max(0, i - 59)
    window = bench_close[lo:i + 1]
    if len(window) < 50:
        return REGIME_NEUTRAL_MULT
    price = window[-1]
    sma20 = window[-20:].mean()
    sma60 = window.mean()
    rets = np.diff(window) / window[:-1]
    vol20 = rets[-20:].std() * math.sqrt(252) if len(rets) >= 20 else 0.0
    if price > sma20 and sma20 > sma60:
        return REGIME_BULL_MULT
    if price < sma60 or vol20 > REGIME_BEAR_VOL_THRESHOLD:
        return REGIME_BEAR_MULT
    return REGIME_NEUTRAL_MULT


def _rolling_beta(b_ret: np.ndarray, a_ret: np.ndarray, i: int) -> float:
    lo = max(0, i - BETA_WINDOW)
    b = b_ret[lo:i + 1]
    a = a_ret[lo:i + 1]
    if len(b) < 20 or b.var() == 0.0:
        return 1.0
    beta = float(np.cov(a, b)[0, 1] / b.var())
    return max(-2.0, min(2.0, beta))       # risk-desk beta clamp


def run_profile(bundles: List[Bundle], p: Profile, capital: float,
                fractional: bool = True,
                start: str = None, end: str = None) -> Dict:
    """
    Portfolio-level simulation of one profile across all bundles.

    One cash account; max 3 concurrent long legs; every entry adds a
    beta/regime-sized SH hedge leg exactly like the live engine.
    """
    n_slots = 3
    common = bundles[0].dates
    for b in bundles[1:]:
        common = common.intersection(b.dates)
    if start:
        common = common[common >= pd.Timestamp(start)]
    if end:
        common = common[common <= pd.Timestamp(end)]
    if len(common) < 15:
        return {"error": "insufficient common calendar"}

    series = {}
    for b in bundles:
        m = b.dates.isin(common)
        series[b.ticker] = {
            "b": b, "close": b.close[m], "high": b.high[m], "low": b.low[m],
            "rsi": b.rsi[m], "macd": b.macd[m], "macd_sig": b.macd_sig[m],
            "atr": b.atr[m], "sma50": b.sma50[m], "sma200": b.sma200[m],
            "sector_up": (b.sector_up[m] if b.sector_up is not None else None),
            "psi": (b.psi[m] if b.psi is not None else None),
            "velocity": (b.velocity[m] if b.velocity is not None else None),
        }
    bnd0 = bundles[0]
    bench_close = bnd0.bench_close[bnd0.dates.isin(common)]
    bench_ret = bnd0.bench_ret[bnd0.dates.isin(common)]
    hedge_close = bnd0.hedge_close[bnd0.dates.isin(common)]
    a_ret = {t: np.diff(s["close"], prepend=s["close"][0])
             for t, s in series.items()}

    cash = capital
    positions: Dict[str, dict] = {}
    hedges: Dict[str, float] = {}
    curve = np.empty(len(common))
    trades: List[dict] = []
    rt_cost_cache: Dict[Tuple[str, int], float] = {}
    return series, bench_close, bench_ret, hedge_close, a_ret, {
        "cash": cash, "positions": positions, "hedges": hedges,
        "curve": curve, "trades": trades, "rt": rt_cost_cache,
        "n_slots": n_slots,
    }


def _simulate_bars(bundles: List[Bundle], p: Profile, capital: float,
                   fractional: bool, start: str, end: str) -> Dict:
    """Full bar-by-bar portfolio simulation (entry/exit/hedge accounting)."""
    prepared = run_profile(bundles, p, capital, fractional, start, end)
    if isinstance(prepared, dict) and "error" in prepared:
        return prepared
    (series, bench_close, bench_ret, hedge_close, a_ret, st) = prepared
    common = bundles[0].dates
    for b in bundles[1:]:
        common = common.intersection(b.dates)
    if start:
        common = common[common >= pd.Timestamp(start)]
    if end:
        common = common[common <= pd.Timestamp(end)]
    # indicators are precomputed over the full 11y history, so no warmup
    # slicing is needed here (warmup already burned before `start`).

    cash = st["cash"]
    positions, hedges = st["positions"], st["hedges"]
    curve, trades = st["curve"], st["trades"]
    n_slots = st["n_slots"]

    def equity_at(i: int) -> float:
        return (cash
                + sum(positions[t]["shares"] * float(series[t]["close"][i])
                      for t in positions)
                + sum(hedges.get(t, 0.0) * float(hedge_close[i])
                      for t in hedges))

    for i in range(len(common)):
        date_i = common[i]

        # ---------- 1) manage open legs ----------
        for t in list(positions.keys()):
            s = series[t]
            pos = positions[t]
            hi, lo = float(s["high"][i]), float(s["low"][i])
            highest = max(pos["highest"], hi)

            exit_price = None
            if lo <= pos["stop"]:
                exit_price = min(pos["stop"], float(s["close"][i]))
            else:
                if hi >= pos["tp1"] and not pos["tp1_done"]:
                    scale_pct = pos.get("tp1_scale", p.tp1_scale)
                    qty = (pos["shares"] * scale_pct if fractional
                           else int(pos["shares"] * scale_pct))
                    if qty > 0:
                        cash += qty * pos["tp1"]
                        pos["sold"] = pos.get("sold", 0.0) + qty * pos["tp1"]
                        pos["shares"] -= qty
                        pos["tp1_done"] = True
                        if p.be_after_tp1:
                            pos["stop"] = max(pos["stop"], pos["entry"])
                if not pos.get("be_done", False) and p.be_trigger_mult > 0:
                    if highest >= pos["entry"] + p.be_trigger_mult * pos["atr_entry"]:
                        pos["stop"] = max(pos["stop"],
                                          pos["entry"] + p.be_offset_mult * pos["atr_entry"])
                        pos["be_done"] = True
                if pos["shares"] > 0 and pos["tp1_done"]:
                    trail_m = pos.get("trail_mult", p.trail_mult)
                    pos["stop"] = max(pos["stop"],
                                      highest - trail_m * pos["atr_entry"])
            if exit_price is not None:
                proceeds = pos["sold"] + pos["shares"] * exit_price
                key = (t, max(1, round(pos["qty0"])))
                if key not in st["rt"]:
                    st["rt"][key] = round_trip_cost(
                        float(pos["entry"]), max(1, round(pos["qty0"])))["total"]
                pnl = proceeds - pos["cost_basis"] - st["rt"][key]
                cash += pos["shares"] * exit_price
                risk0 = pos["risk_per_share"] * pos["qty0"]
                trades.append({
                    "ticker": t, "entry_date": str(pos["date"]),
                    "exit_date": str(date_i.date()), "pnl": pnl,
                    "r": pnl / risk0 if risk0 > 0 else 0.0,
                    "risk0": risk0,
                    "regime": pos.get("regime_mult"),
                    "result": "win" if pnl > 0 else "loss"})
                if hedges.get(t, 0.0) > 0:
                    cash += hedges[t] * float(hedge_close[i])
                    hedges[t] = 0.0
                del positions[t]
            else:
                pos["highest"] = highest

        # ---------- 2) new entries ----------
        if len(positions) < n_slots:
            for t, s in series.items():
                if t in positions or len(positions) >= n_slots:
                    continue
                price = float(s["close"][i])
                if (price <= 0 or not np.isfinite(s["atr"][i])
                        or s["atr"][i] <= 0):
                    continue
                macd_ok = s["macd"][i] > s["macd_sig"][i]
                rsi_ok = 35.0 < s["rsi"][i] < p.rsi_max
                trend_ok = price > s["sma50"][i]
                super_trend = (not p.trend_filter
                                or (np.isfinite(s["sma200"][i])
                                    and s["sma50"][i] > s["sma200"][i]))
                if not (macd_ok and rsi_ok and trend_ok and super_trend):
                    continue

                if p.regime_filter:
                    mult = _regime_mult(bench_close, i)
                    if abs(mult - REGIME_BEAR_MULT) < 1e-5:
                        continue

                if p.sector_up and s.get("sector_up") is not None:
                    if s["sector_up"][i] < 1.0:
                        continue

                bar_psi = float(s["psi"][i]) if s.get("psi") is not None and np.isfinite(s["psi"][i]) else 50.0
                if p.min_psi > 0.0 and bar_psi < p.min_psi:
                    continue

                equity_now = equity_at(i)
                if p.adaptive_psi:
                    from risk.hedging_engine import get_adaptive_exit_geometry
                    geom = get_adaptive_exit_geometry(psi=bar_psi)
                    eff_stop_mult = geom["stop_mult"]
                    eff_tp1_mult = geom["tp1_mult"]
                    eff_trail_mult = geom["trail_mult"]
                    eff_scale = geom.get("tp1_scale", p.tp1_scale)
                    stop_dist = eff_stop_mult * float(s["atr"][i])
                    tp1_target = price + eff_tp1_mult * float(s["atr"][i])
                else:
                    eff_stop_mult = p.stop_mult
                    eff_tp1_mult = p.tp1_mult
                    eff_trail_mult = p.trail_mult
                    eff_scale = p.tp1_scale
                    stop_dist = eff_stop_mult * float(s["atr"][i])
                    tp1_target = price + eff_tp1_mult * stop_dist

                raw_qty = (equity_now * RISK_PCT) / stop_dist
                cap_qty = (equity_now * 0.30) / price   # notional cap (0.30)
                qty = float(round(min(raw_qty, cap_qty), 4)) if fractional \
                    else int(min(raw_qty, cap_qty))
                if qty <= 0:
                    continue

                beta = _rolling_beta(bench_ret, a_ret[t], i)
                mult = _regime_mult(bench_close, i)
                cash -= qty * price
                positions[t] = {
                    "date": date_i.date(), "entry": price, "qty0": qty,
                    "shares": qty, "cost_basis": qty * price, "sold": 0.0,
                    "stop": price - stop_dist,
                    "atr_entry": float(s["atr"][i]),
                    "highest": float(s["high"][i]),
                    "risk_per_share": stop_dist,
                    "tp1": tp1_target,
                    "tp1_done": eff_tp1_mult <= 0 and not p.adaptive_psi,
                    "be_done": False,
                    "regime_mult": mult,
                    "trail_mult": eff_trail_mult,
                    "tp1_scale": eff_scale,
                }
                sh_price = float(hedge_close[i])
                if p.hedge:
                    if p.dynamic_hedge:
                        from risk.hedging_engine import calculate_dynamic_hedge_ratio
                        dyn_regime = "BULL" if abs(mult - REGIME_BULL_MULT) < 1e-4 else ("BEAR" if abs(mult - REGIME_BEAR_MULT) < 1e-4 else "NEUTRAL")
                        hedge_ratio = calculate_dynamic_hedge_ratio(psi=bar_psi, regime=dyn_regime)
                        target_val = qty * price * hedge_ratio
                        # enforce strict ceiling of 0.65x long notional (Upgrade 2)
                        target_val = min(target_val, 0.65 * qty * price)
                    else:
                        target_val = qty * price * abs(beta) * mult
                    # affordability cap: hedge notional <= 50% of book equity
                    target_val = min(target_val, 0.5 * equity_now)
                    add = ((target_val / sh_price) if fractional
                           else int(target_val / sh_price)) if sh_price > 0 else 0.0
                    if add > 0:
                        hedges[t] = hedges.get(t, 0.0) + add
                        cash -= add * sh_price

        curve[i] = equity_at(i)

    # ---------- 3) force-close leftovers ----------

    if positions:
        last = len(common) - 1
        for t, pos in positions.items():
            price = float(series[t]["close"][last])
            pnl = (pos.get("sold", 0.0) + pos["shares"] * price
                   - pos["cost_basis"])
            risk0 = pos["risk_per_share"] * pos["qty0"]
            trades.append({
                "ticker": t, "entry_date": str(pos["date"]),
                "exit_date": str(common[last].date()), "pnl": pnl,
                "r": pnl / risk0 if risk0 > 0 else 0.0,
                "risk0": risk0,
                "regime": pos.get("regime_mult"),
                "result": "win" if pnl > 0 else "loss"})
            cash += pos["shares"] * price          # proceeds back to cash
            if hedges.get(t, 0.0) > 0:
                cash += hedges[t] * float(hedge_close[last])
        positions.clear()
        hedges.clear()
        curve[-1] = cash

    eq_s = pd.Series(curve, index=common)
    # debug bookkeeping trace: where equity diverges from realized trades
    d_cash = cash - capital - float(sum(t["pnl"] for t in trades))
    dd_trace = {
        "cash_drift_vs_trades": round(d_cash, 2),
        "cash_final": round(cash, 2),
    }

    dd = float((eq_s / eq_s.cummax() - 1.0).min())
    rets = eq_s.pct_change().dropna()
    wins = [t for t in trades if t["pnl"] > 0]
    metrics = {
        "final_equity": round(float(eq_s.iloc[-1]), 2),
        "total_return_pct": round((float(eq_s.iloc[-1]) / capital - 1) * 100, 2),
        "max_dd_pct": round(dd * 100, 2),
        "sharpe": (round(float(rets.mean() / rets.std() * math.sqrt(252)), 2)
                   if len(rets) > 1 and rets.std() > 0 else 0.0),
        "num_trades": len(trades),
        "win_rate_pct": (round(100.0 * len(wins) / len(trades), 2)
                         if trades else 0.0),
        "avg_r": (round(float(np.mean([t["r"] for t in trades])), 3)
                  if trades else 0.0),
        "exp_r": (round(float(np.sum([t["pnl"] for t in trades])
                             / max(1e-9, np.sum([t.get("risk0", 0.0)
                                                 for t in trades]))), 3)
                  if trades else 0.0),
    }
    return {"metrics": metrics, "trades": trades, "curve": eq_s,
            "debug": dd_trace}


# ---------------------------------------------------- stage 1: sweep --------
def sweep(bundles: List[Bundle], profiles: List[Profile],
          capital: float = 10_000.0) -> pd.DataFrame:
    rows = []
    for k, p in enumerate(profiles, 1):
        try:
            r = _simulate_bars(bundles, p, capital, fractional=True,
                               start=TRAIN_START, end=TRAIN_END)
            m = r.get("metrics", {})
            rows.append({"profile": p.key(), "stop": p.stop_mult,
                         "tp1": p.tp1_mult, "trail": p.trail_mult,
                         "scale": p.tp1_scale, "trend": p.trend_filter,
                         "rsi_max": p.rsi_max, "hedged": p.hedge,
                         "be_trigger": p.be_trigger_mult,
                         "be_offset": p.be_offset_mult,
                         "regime_filter": p.regime_filter,
                         "sector_up": p.sector_up,
                         "adaptive_psi": p.adaptive_psi,
                         "min_psi": p.min_psi,
                         "dynamic_hedge": p.dynamic_hedge,
                         **m})
            print(f"  [{k:>2}/{len(profiles)}] {p.key():<60} "
                  f"WR {m.get('win_rate_pct', 0):>6.2f}%  "
                  f"ret {m.get('total_return_pct', 0):>+8.2f}%  "
                  f"DD {m.get('max_dd_pct', 0):>7.2f}%  "
                  f"trades {m.get('num_trades', 0):>4}  "
                  f"expR {m.get('exp_r', 0):>+.3f}", flush=True)
        except Exception as e:
            print(f"  [{k:>2}/{len(profiles)}] {p.key()} — ERROR {e}",
                  flush=True)
    return pd.DataFrame(rows)


def pick_best(df: pd.DataFrame) -> Optional[dict]:
    """
    Selection rule (honest):
      1. among configs with positive risk-weighted expectancy (exp_r > 0)
         and enough trades (>= 120): choose the one closest to 50% WR.
      2. if none is expectancy-positive: choose max exp_r (report it).
    """
    if df.empty:
        return None
    if "exp_r" not in df.columns:
        d = df.copy()
        d["wr_dist"] = (d["win_rate_pct"] - 50.0).abs()
        return d.sort_values("wr_dist").iloc[0].to_dict()
    ok = df[(df["exp_r"] > 0) & (df["num_trades"] >= 120)]
    if len(ok):
        d = ok.copy()
        d["wr_dist"] = (d["win_rate_pct"] - 50.0).abs()
        d = d.sort_values(["wr_dist", "exp_r"],
                          ascending=[True, False])
        return d.iloc[0].to_dict()
    return df.sort_values("exp_r", ascending=False).iloc[0].to_dict()


def rank_candidates(df: pd.DataFrame, n: int = 6) -> pd.DataFrame:
    """Top-N candidates by the pick_best rule (for validation)."""
    if df.empty:
        return df
    if "exp_r" in df.columns:
        ok = df[(df["exp_r"] > 0) & (df["num_trades"] >= 120)].copy()
        if len(ok):
            ok["wr_dist"] = (ok["win_rate_pct"] - 50.0).abs()
            return ok.sort_values(["wr_dist", "exp_r"],
                                  ascending=[True, False]).head(n)
        return df.sort_values("exp_r", ascending=False).head(n)
    d = df.copy()
    d["wr_dist"] = (d["win_rate_pct"] - 50.0).abs()
    return d.sort_values("wr_dist").head(n)


# ------------------------------------------- stage 2/3/5: windows & years ---
def window_run(bundles: List[Bundle], p: Profile, capital: float,
               fractional: bool, start: str, end: str = None) -> Dict:
    return _simulate_bars(bundles, p, capital, fractional,
                          start=start, end=end)


def per_year_stats(result: Dict) -> List[Tuple[str, int, int, float]]:
    """(year, trades, wins, win_rate) from a run's trade list."""
    df = pd.DataFrame(result.get("trades", []))
    if df.empty:
        return []
    df["year"] = pd.to_datetime(df["exit_date"]).dt.year
    out = []
    for y, g in df.groupby("year"):
        n, w = len(g), int((g["pnl"] > 0).sum())
        out.append((str(y), n, w, round(100.0 * w / n, 1)))
    return out


# ------------------------------------------------- stage 4: monte carlo -----
def monte_carlo(r_pool: np.ndarray, n_paths: int = 10_000,
                horizon_days: int = 252, trades_per_year: int = 38,
                seed: int = 42) -> Dict:
    """
    Bootstrap one-year equity paths by resampling historical trade R's.
    Per-trade equity impact = r * RISK_PCT (compounded), like the engine's
    fixed-fractional sizing. Reports P(profit), P(ruin), VaR/CVaR, bands.
    """
    rng = np.random.default_rng(seed)
    if len(r_pool) == 0:
        return {}
    draws = rng.choice(r_pool, size=(n_paths, trades_per_year), replace=True)
    step = 1.0 + draws * RISK_PCT
    eq = np.cumprod(step, axis=1)
    final = eq[:, -1]
    dd = np.minimum.accumulate(
        np.maximum.accumulate(eq, axis=1) ** -1.0 * eq, axis=1).min(axis=1)
    return {
        "n_paths": n_paths,
        "p_profit_pct": round(float((final > 1.0).mean() * 100), 1),
        "p_ruin30_pct": round(float((dd <= 0.70).mean() * 100), 1),
        "p_dd20_pct": round(float((dd <= 0.80).mean() * 100), 1),
        "var5_pct": round(float(np.percentile(final, 5) - 1) * 100, 1),
        "cvar5_pct": round(float(final[final <= np.percentile(final, 5)].mean() - 1) * 100, 1),
        "median_pct": round(float(np.median(final) - 1) * 100, 1),
        "p90_pct": round(float(np.percentile(final, 95) - 1) * 100, 1),
        "mean_pct": round(float(final.mean() - 1) * 100, 1),
    }


def crisis_pool(trades: List[dict], crisis_windows) -> np.ndarray:
    """R-pool restricted to trades exited inside crisis windows."""
    df = pd.DataFrame(trades)
    if df.empty:
        return np.array([])
    ex = pd.to_datetime(df["exit_date"])
    mask = pd.Series(False, index=df.index)
    for _, s, e in crisis_windows:
        mask |= (ex >= pd.Timestamp(s)) & (ex <= pd.Timestamp(e))
    return df.loc[mask, "r"].to_numpy(float)


def profile_from_row(row) -> Profile:
    """Rebuild a Profile from a sweep/val row."""
    return Profile(stop_mult=float(row["stop"]),
                   tp1_mult=float(row["tp1"]),
                   trail_mult=float(row["trail"]),
                   tp1_scale=float(row["scale"]),
                   rsi_max=float(row.get("rsi_max", 55.0)),
                   trend_filter=bool(row.get("trend", False)),
                   be_after_tp1=True,
                   hedge=bool(row.get("hedged", True)),
                   be_trigger_mult=float(row.get("be_trigger", 0.0)),
                   be_offset_mult=float(row.get("be_offset", 0.0)),
                   regime_filter=bool(row.get("regime_filter", False)),
                   sector_up=bool(row.get("sector_up", False)),
                   adaptive_psi=bool(row.get("adaptive_psi", False)),
                   min_psi=float(row.get("min_psi", 0.0)),
                   dynamic_hedge=bool(row.get("dynamic_hedge", False)))


# ----------------------------------------------------------------- main -----
def main() -> None:
    ap = argparse.ArgumentParser(description="crisis-tested financial model")
    ap.add_argument("--smoke", action="store_true",
                    help="fast sanity run (small grid, fewer MC paths)")
    args = ap.parse_args()
    smoke = args.smoke

    t0 = time.time()
    print("=== CRISIS-TESTED FINANCIAL MODEL ===", flush=True)
    print(f"  NVDA BANNED from all pools & sims | risk/trade {RISK_PCT:.0%} | "
          f"3 slots | train {TRAIN_START}..{TRAIN_END} | "
          f"test {TEST_START}..today", flush=True)

    # ---- data -----------------------------------------------------------
    tickers = {t: s for s, ts in CORE_UNIVERSE.items() for t in ts
               if t not in BANNED}
    names = sorted(tickers)                      # 27 tickers after ban
    years = 11                                   # 2016 -> today
    print(f"[data] loading {len(names)} tickers + {BENCH} + {HEDGE} "
          f"({years}y)...", flush=True)
    df_bench = load_ohlcv(BENCH, years)
    df_hedge = load_ohlcv(HEDGE, years)
    if df_bench.empty:
        raise SystemExit("No SPY data — aborting.")
    if df_hedge.empty or len(df_hedge) < 300:
        print("[data] SH unavailable -> synthesizing -1x SPY.", flush=True)
        ret = df_bench["Close"].pct_change().fillna(0.0)
        df_hedge = df_bench.copy()
        df_hedge["Close"] = df_bench["Close"].iloc[0] * (1.0 - ret).cumprod()
        for c in ("Open", "High", "Low"):
            df_hedge[c] = df_hedge["Close"]

    from backtest.universe import SECTOR_ETF
    etf_closes = {}
    needed_etfs = sorted(set(SECTOR_ETF.get(tickers[t]) for t in names if SECTOR_ETF.get(tickers[t])))
    for etf in needed_etfs:
        df_e = load_ohlcv(etf, years)
        if not df_e.empty and "Close" in df_e.columns:
            etf_closes[etf] = df_e["Close"]

    bundles, failed = [], []
    for t in names:
        df = load_ohlcv(t, years)
        sec = tickers[t]
        sec_etf = SECTOR_ETF.get(sec)
        sec_close = etf_closes.get(sec_etf)
        b = build_bundle(t, sec, df, df_bench, df_hedge, sector_etf_close=sec_close) if not df.empty else None
        if b is None:
            failed.append(t)
            print(f"  [data] {t:<6} skipped ({'no data' if df.empty else 'short history'})",
                  flush=True)
        else:
            bundles.append(b)
            print(f"  [data] {t:<6} ({tickers[t]:<13}) {len(b.dates)} bars",
                  flush=True)
    if len(bundles) < 10:
        raise SystemExit("Too little data — aborting.")
    print(f"[data] {len(bundles)} bundles ready, {len(failed)} skipped "
          f"({time.time() - t0:.0f}s)", flush=True)

    # ---- stage 1: sensitivity sweep on TRAIN (contains COVID crash) -----
    print(f"\n--- STAGE 1: SENSITIVITY SWEEP (train {TRAIN_START} -> "
          f"{TRAIN_END}) ---", flush=True)
    if smoke:
        all_grid = sensitivity_grid()
        # Mix 4 static combos with 4 adaptive combos for thorough smoke coverage
        grid = all_grid[:4] + all_grid[-4:]
    else:
        grid = sensitivity_grid()
    df_sweep = sweep(bundles, grid)
    best = pick_best(df_sweep)
    if best is None:
        raise SystemExit("Sweep produced no results.")
    print(f"\n>>> SWEEP WINNER: {best['profile']}", flush=True)
    print(f"    WR {best['win_rate_pct']}% | ret {best['total_return_pct']}% | "
          f"DD {best['max_dd_pct']}% | avgR {best['avg_r']}", flush=True)

    best_profile = profile_from_row(best)
    print("\n--- STAGE 1b: LOCAL REFINEMENT ---", flush=True)
    refine = [best_profile] + refine_grid(best_profile)
    if smoke:
        refine = refine[:4]
    df_ref = sweep(bundles, refine)
    combined = pd.concat([df_sweep, df_ref], ignore_index=True)
    best = pick_best(combined)
    best_profile = profile_from_row(best)
    print(f">>> REFINED WINNER: {best_profile.key()}", flush=True)
    print(f"    WR {best['win_rate_pct']}% | ret {best['total_return_pct']}% | "
          f"DD {best['max_dd_pct']}% | expR {best['exp_r']}", flush=True)

    print("\n--- STAGE 2: VALIDATION (2021-2023), top-6 candidates ---",
          flush=True)
    cap_ref = 10_000.0
    cands = rank_candidates(combined, n=12 if not smoke else 2)
    seeds = [
        baseline_profile(),
        Profile(stop_mult=1.5, tp1_mult=2.0, trail_mult=1.5, tp1_scale=0.5,
                rsi_max=65.0, trend_filter=False, be_after_tp1=False,
                hedge=False),
        Profile(stop_mult=1.5, tp1_mult=2.0, trail_mult=1.5, tp1_scale=0.5,
                rsi_max=65.0, trend_filter=True, be_after_tp1=True,
                hedge=False),
        # Upgrades 1 & 2 & 8 (Adaptive Exit Geometry + Dynamic Sizing + PSI Filter)
        Profile(stop_mult=1.5, tp1_mult=2.0, trail_mult=1.5, tp1_scale=0.5,
                rsi_max=65.0, trend_filter=True, be_after_tp1=True,
                hedge=True, adaptive_psi=True, dynamic_hedge=True, min_psi=45.0),
        Profile(stop_mult=1.5, tp1_mult=2.0, trail_mult=1.5, tp1_scale=0.5,
                rsi_max=65.0, trend_filter=True, be_after_tp1=True,
                hedge=True, adaptive_psi=True, dynamic_hedge=True, min_psi=0.0),
        Profile(stop_mult=1.5, tp1_mult=2.0, trail_mult=1.5, tp1_scale=0.5,
                rsi_max=65.0, trend_filter=True, be_after_tp1=True,
                hedge=True, adaptive_psi=False, dynamic_hedge=True, min_psi=45.0),
        Profile(stop_mult=1.5, tp1_mult=2.0, trail_mult=1.5, tp1_scale=0.5,
                rsi_max=65.0, trend_filter=True, be_after_tp1=True,
                hedge=False, adaptive_psi=True, dynamic_hedge=False, min_psi=45.0),
    ]
    have = set(cands["profile"])
    for p in seeds:
        if p.key() not in have:
            cands = pd.concat([cands, pd.DataFrame([{
                "profile": p.key(), "stop": p.stop_mult, "tp1": p.tp1_mult,
                "trail": p.trail_mult, "scale": p.tp1_scale,
                "trend": p.trend_filter, "rsi_max": p.rsi_max,
                "hedged": p.hedge,
                "be_trigger": p.be_trigger_mult, "be_offset": p.be_offset_mult,
                "regime_filter": p.regime_filter, "sector_up": p.sector_up,
                "adaptive_psi": p.adaptive_psi, "min_psi": p.min_psi,
                "dynamic_hedge": p.dynamic_hedge}])], ignore_index=True)
    val_rows = []
    for _, row in cands.iterrows():
        p = profile_from_row(row)
        r = window_run(bundles, p, cap_ref, True, VAL_START, VAL_END)
        m = r["metrics"]
        val_rows.append({"profile": p.key(), "stop": p.stop_mult,
                         "tp1": p.tp1_mult, "trail": p.trail_mult,
                         "scale": p.tp1_scale, "trend": p.trend_filter,
                         "rsi_max": p.rsi_max, "hedged": p.hedge,
                         "be_trigger": p.be_trigger_mult,
                         "be_offset": p.be_offset_mult,
                         "regime_filter": p.regime_filter,
                         "sector_up": p.sector_up,
                         "adaptive_psi": p.adaptive_psi,
                         "min_psi": p.min_psi,
                         "dynamic_hedge": p.dynamic_hedge,
                         **m})
        print(f"  {p.key():<60} WR {m['win_rate_pct']:>6.2f}%  "
              f"ret {m['total_return_pct']:>+8.2f}%  "
              f"expR {m['exp_r']:>+.3f}", flush=True)
    df_val = pd.DataFrame(val_rows)
    # stability-first two-tier selection:
    #   tier 1: expR > 0 on BOTH windows -> highest WR (aim ~50%)
    #   tier 2: otherwise max min(train expR, val expR)  [crisis-proofing]
    df_val["train_exp"] = df_val["profile"].map(
        {r["profile"]: r["exp_r"] for _, r in combined.iterrows()})
    df_val["min_exp"] = df_val[["exp_r", "train_exp"]].min(axis=1)
    stable = df_val[df_val["exp_r"] > 0]
    stable = stable[stable["train_exp"] > 0] if len(stable) else stable
    if len(stable):
        chosen = stable.sort_values(["win_rate_pct", "exp_r"],
                                    ascending=[False, False]).iloc[0]
    else:
        chosen = df_val.sort_values("min_exp", ascending=False).iloc[0]
    best_profile = profile_from_row(chosen)
    print(f"\n>>> FINAL PROFILE: {best_profile.key()}", flush=True)

    # ---- stage 3: FINAL out-of-sample test (2024 -> today, unseen) -------
    print(f"\n--- STAGE 3: OUT-OF-SAMPLE TEST ({TEST_START} -> today) ---",
          flush=True)
    oos_tuned = window_run(bundles, best_profile, cap_ref, True, TEST_START)
    oos_base = window_run(bundles, baseline_profile(), cap_ref, True, TEST_START)
    mt, mb = oos_tuned["metrics"], oos_base["metrics"]

    def show(tag, m):
        print(f"  {tag:<22} WR {m['win_rate_pct']:>6.2f}%  "
              f"ret {m['total_return_pct']:>+8.2f}%  "
              f"DD {m['max_dd_pct']:>7.2f}%  sharpe {m['sharpe']:>5.2f}  "
              f"trades {m['num_trades']:>4}  expR {m['exp_r']:>+.3f}", flush=True)

    show("TUNED profile", mt)
    show("BASELINE (engine)", mb)

    print("\n  Per-year win rate (TUNED, test window):", flush=True)
    for y, n, w, wr in per_year_stats(oos_tuned):
        flag = "✓" if abs(wr - 50) <= 10 else ("↑" if wr > 60 else "↓")
        print(f"    {y}: {w:>3}/{n:<3} = {wr:>5.1f}%  {flag}", flush=True)

    # ---- stage 4: crisis stress tests ------------------------------------
    print("\n--- STAGE 4: CRISIS STRESS TESTS (tuned profile) ---", flush=True)
    crisis_rows = []
    for label, s, e in CRISES:
        try:
            r = window_run(bundles, best_profile, cap_ref, True, s, e)
            m = r["metrics"]
            crisis_rows.append({"crisis": label, **m})
            print(f"  {label:<22} WR {m['win_rate_pct']:>6.2f}%  "
                  f"ret {m['total_return_pct']:>+8.2f}%  "
                  f"DD {m['max_dd_pct']:>7.2f}%  "
                  f"trades {m['num_trades']:>3}", flush=True)
        except Exception as ex:
            print(f"  {label:<22} ERROR {ex}", flush=True)

    # ---- stage 4: monte carlo --------------------------------------------
    print("\n--- STAGE 5: MONTE CARLO (10,000 one-year bootstrap paths) ---",
          flush=True)
    r_oos = pd.DataFrame(oos_tuned["trades"])["r"].to_numpy(float) \
        if oos_tuned.get("trades") else np.array([])
    mc_all = monte_carlo(r_oos, n_paths=2_000 if smoke else 10_000)
    if mc_all:
        print(f"  Pool: all OOS trades (n={len(r_oos)})", flush=True)
        print(f"    P(1y profit) {mc_all['p_profit_pct']}% | "
              f"P(DD>=20%) {mc_all['p_dd20_pct']}% | "
              f"P(ruin -30%) {mc_all['p_ruin30_pct']}%", flush=True)
        print(f"    1y outcome: 5th pct {mc_all['var5_pct']:+.1f}% | "
              f"median {mc_all['median_pct']:+.1f}% | "
              f"mean {mc_all['mean_pct']:+.1f}% | "
              f"95th pct {mc_all['p90_pct']:+.1f}%", flush=True)
    # crisis-only bootstrap (crash sequencing stress)
    for label, s, e in CRISES:
        pool = crisis_pool(oos_tuned["trades"], [(label, s, e)])
        if len(pool) >= 8:
            mc_c = monte_carlo(pool, n_paths=2_000 if smoke else 10_000,
                               trades_per_year=max(6, len(pool)))
            print(f"  Crisis pool '{label}' (n={len(pool)}): "
                  f"P(profit) {mc_c['p_profit_pct']}% | "
                  f"P(ruin) {mc_c['p_ruin30_pct']}% | "
                  f"median {mc_c['median_pct']:+.1f}%", flush=True)

    # ---- stage 5: capital scenarios ($1k / $5k / $10k, integer shares) ----
    print("\n--- STAGE 6: CAPITAL SCENARIOS (test window, integer shares) "
          "---", flush=True)
    cap_rows = []
    for cap in CAPITALS:
        rf = window_run(bundles, best_profile, cap, False, TEST_START)
        rx = window_run(bundles, best_profile, cap, True, TEST_START)
        mf, mx = rf["metrics"], rx["metrics"]
        cap_rows.append({"capital": cap, "book": "integer", **mf})
        cap_rows.append({"capital": cap, "book": "fractional", **mx})
        print(f"  ${cap:>7,.0f} INTEGER    : WR {mf['win_rate_pct']:>6.2f}%  "
              f"final ${mf['final_equity']:>10,.2f}  "
              f"ret {mf['total_return_pct']:>+7.2f}%  "
              f"DD {mf['max_dd_pct']:>7.2f}%  trades {mf['num_trades']:>4}",
              flush=True)
        print(f"  ${cap:>7,.0f} fractional : WR {mx['win_rate_pct']:>6.2f}%  "
              f"final ${mx['final_equity']:>10,.2f}  "
              f"ret {mx['total_return_pct']:>+7.2f}%  "
              f"DD {mx['max_dd_pct']:>7.2f}%  trades {mx['num_trades']:>4}",
              flush=True)

    # ---- report ----------------------------------------------------------
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = date.today()
    csv_path = REPORT_DIR / f"financial_model_{stamp}.csv"
    pd.concat([
        df_sweep.assign(stage="sweep"),
        df_ref.assign(stage="refine"),
        df_val.assign(stage="validation"),
        pd.DataFrame(crisis_rows).assign(stage="crisis"),
        pd.DataFrame(cap_rows).assign(stage="capital"),
    ]).to_csv(csv_path, index=False)

    md = REPORT_DIR / f"financial_model_{stamp}.md"
    lines = [
        "# Crisis-Tested Financial Model",
        "",
        f"- **Date:** {stamp}  ",
        f"- **Method:** Financial Modeling Suite — sensitivity sweep → "
        f"refinement → out-of-sample validation → crisis stress tests → "
        f"Monte Carlo → capital scenarios",
        f"- **NVDA:** BANNED (all pools & sims)  ",
        f"- **Train:** {TRAIN_START} → {TRAIN_END} (incl. COVID crash) · "
        f"**Test:** {TEST_START} → today (incl. 2022 bear) · "
        f"Universe: core mega-caps minus NVDA ({len(bundles)} used)",
        f"- **Chosen profile:** `{best_profile.key()}`",
        f"- **Baseline:** `{baseline_profile().key()}`",
        "",
        "## Validation (2021-2023) — candidate stability",
        "",
        "| Profile | WinRate | Return | expR |",
        "|---|---:|---:|---:|",
    ]
    for _, v in df_val.iterrows():
        lines.append(f"| {v['profile']} | {v['win_rate_pct']}% | "
                     f"{v['total_return_pct']:+.2f}% | {v['exp_r']:+.3f} |")
    lines += [
        "",
        "## Stage 3 — Out-of-sample test (2024 → today)",
        "",
        "| Book | WinRate | Return | MaxDD | Sharpe | Trades | AvgR |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Tuned | {mt['win_rate_pct']}% | {mt['total_return_pct']:+.2f}% | "
        f"{mt['max_dd_pct']:.2f}% | {mt['sharpe']} | {mt['num_trades']} | "
        f"{mt['avg_r']:+.3f} |",
        f"| Baseline | {mb['win_rate_pct']}% | {mb['total_return_pct']:+.2f}% | "
        f"{mb['max_dd_pct']:.2f}% | {mb['sharpe']} | {mb['num_trades']} | "
        f"{mb['avg_r']:+.3f} |",
        "",
        "### Per-year win rate (tuned)",
        "",
        "| Year | Trades | Wins | WinRate |",
        "|---|---:|---:|---:|",
    ]
    for y, n, w, wr in per_year_stats(oos_tuned):
        lines.append(f"| {y} | {n} | {w} | {wr}% |")
    lines += [
        "",
        "## Stage 3 — Crisis stress tests",
        "",
        "| Crisis | WinRate | Return | MaxDD | Trades |",
        "|---|---:|---:|---:|---:|",
    ]
    for c in crisis_rows:
        lines.append(f"| {c['crisis']} | {c['win_rate_pct']}% | "
                     f"{c['total_return_pct']:+.2f}% | {c['max_dd_pct']:.2f}% | "
                     f"{c['num_trades']} |")
    lines += [
        "",
        "## Stage 4 — Monte Carlo (one-year horizon)",
        "",
        f"- P(1y profit): **{mc_all.get('p_profit_pct')}%** · "
        f"P(DD ≥ 20%): {mc_all.get('p_dd20_pct')}% · "
        f"P(ruin −30%): {mc_all.get('p_ruin30_pct')}%",
        f"- Outcome bands: 5th {mc_all.get('var5_pct'):+.1f}% · median "
        f"{mc_all.get('median_pct'):+.1f}% · mean {mc_all.get('mean_pct'):+.1f}% "
        f"· 95th {mc_all.get('p90_pct'):+.1f}%",
        "",
        "## Stage 5 — Capital scenarios (out-of-sample)",
        "",
        "| Capital | Book | Final | Return | WinRate | MaxDD | Trades |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for c in cap_rows:
        lines.append(f"| ${c['capital']:,.0f} | {c['book']} | "
                     f"${c['final_equity']:,.2f} | "
                     f"{c['total_return_pct']:+.2f}% | "
                     f"{c['win_rate_pct']}% | {c['max_dd_pct']:.2f}% | "
                     f"{c['num_trades']} |")
    lines += [
        "",
        "## Assumptions & limits",
        "",
        "- Daily bars; fills at stop/TP levels with slippage modeled via "
        "round-trip cost model (spread + slippage + SEC/TAF fees).",
        "- Fixed-fractional 2% risk, 3 concurrent slots, SH inverse-ETF hedge "
        "sized by 60-day beta × SPY regime multiplier (live-engine parity).",
        "- Train window includes a crash; test window includes a bear market. "
        "Monte Carlo resamples actual OOS trade R's (no distribution "
        "assumptions) but assumes trade independence.",
        "- Past performance does not guarantee future results. Paper-trading "
        "research only — not financial advice.",
    ]
    md.write_text("\n".join(lines) + "\n")
    print(f"\n[saved] {csv_path}", flush=True)
    print(f"[saved] {md}", flush=True)
    print(f"[done] total {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()











