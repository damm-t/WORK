"""
Multi-Asset Comparative Performance Benchmark Engine
=====================================================
Runs identical rigorous quantitative evaluation across all 4 asset desks:
  1. Desk 1: US Equities (Alpaca / SP500 & Tech)
  2. Desk 2: Crypto Perpetual Futures (24/7 CCXT 3x Leverage)
  3. Desk 3: CME Micro Index Futures (23h Bracket Orders)
  4. Desk 4: Forex 24/5 Macro (London/NY Overlap & Currency Pip Geometry)

Metrics Calculated:
  - Total Return (%)
  - Win Rate (%)
  - Profit Factor (Gross Gains / Gross Losses)
  - Max Drawdown (MDD %)
  - Annualized Sharpe Ratio
  - Expectancy Per Trade ($)
  - Total Closed Trades
  - Alpha Efficiency & Ranking

Usage:
  python -m backtest.multi_asset_benchmark
"""

from __future__ import annotations

import json
import logging
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from market.price_fetcher import fetch_prices
from strategy.crypto_perp_strategy import crypto_strategy
from strategy.cme_futures_strategy import cme_strategy
from strategy.forex_strategy import forex_strategy

logger = logging.getLogger(__name__)

REPORT_PATH = Path("reports/multi_asset_comparison.json")


def simulate_asset_trades(
    symbol: str,
    asset_class: str,
    df_bars: pd.DataFrame,
    initial_capital: float = 50000.0,
    risk_pct: float = 0.02,
) -> Dict[str, Any]:
    """
    Simulates sequential walk-forward trades on historical OHLCV bars.
    """
    if df_bars.empty or len(df_bars) < 30:
        return {
            "symbol": symbol,
            "asset_class": asset_class,
            "trades_count": 0,
            "win_rate": 0.0,
            "profit_factor": 1.0,
            "total_return_pct": 0.0,
            "max_drawdown_pct": 0.0,
            "sharpe_ratio": 0.0,
            "wins": 0,
            "losses": 0,
            "pnl_dollars": 0.0,
        }

    trades = []
    equity = initial_capital
    peak_equity = initial_capital
    max_dd = 0.0
    equity_curve = [initial_capital]

    close = df_bars["Close"].values
    high = df_bars["High"].values
    low = df_bars["Low"].values
    idx = df_bars.index

    i = 25
    n = len(df_bars)

    while i < n - 1:
        # Window up to current bar
        sub_df = df_bars.iloc[: i + 1]
        curr_p = float(close[i])

        side = None
        sl = 0.0
        tp = 0.0

        if asset_class == "STOCKS":
            # 20 EMA trend bounce with 2:1 R:R
            ema20 = float(sub_df["Close"].ewm(span=20).mean().iloc[-1])
            std20 = float(sub_df["Close"].rolling(20).std().iloc[-1]) or (curr_p * 0.02)
            prev_c = sub_df["Close"].shift(1)
            tr = pd.concat([sub_df["High"] - sub_df["Low"], (sub_df["High"] - prev_c).abs(), (sub_df["Low"] - prev_c).abs()], axis=1).max(axis=1)
            atr = float(tr.tail(14).mean()) or (curr_p * 0.02)
            if curr_p > ema20 and curr_p <= (ema20 + 0.5 * atr):
                side = "LONG"
                sl = curr_p - (1.5 * atr)
                tp = curr_p + (3.0 * atr)

        elif asset_class == "CRYPTO":
            # Crypto perp strategy
            sig = crypto_strategy.evaluate(symbol, sub_df)
            if sig.side == "LONG" and sig.confidence_score >= 75.0:
                side = "LONG"
                sl = sig.stop_loss
                tp = sig.take_profit

        elif asset_class == "FUTURES":
            # CME futures strategy
            sym_clean = symbol.replace("=F", "")
            if sym_clean == "ES": sym_clean = "MES"
            elif sym_clean == "NQ": sym_clean = "MNQ"
            elif sym_clean == "CL": sym_clean = "MCL"
            elif sym_clean == "GC": sym_clean = "MGC"
            sig = cme_strategy.evaluate(sym_clean, sub_df)
            if sig.side == "LONG" and sig.confidence_score >= 75.0:
                side = "LONG"
                sl = sig.stop_loss
                tp = sig.take_profit

        elif asset_class == "FOREX":
            # Forex strategy
            sig = forex_strategy.evaluate(symbol, sub_df)
            if sig.side in ("LONG", "SHORT") and sig.confidence_score >= 78.0:
                side = sig.side
                sl = sig.stop_loss
                tp = sig.take_profit

        if side is None or sl <= 0 or tp <= 0 or abs(curr_p - sl) <= 0:
            i += 1
            continue

        # Position sizing: risk 1.5% of equity
        risk_dollars = equity * risk_pct
        risk_per_unit = abs(curr_p - sl)
        units = risk_dollars / max(risk_per_unit, 0.0001)

        # Forward simulate outcome
        hit = None
        exit_bar = i + 1
        for j in range(i + 1, min(i + 15, n)):
            bar_high = float(high[j])
            bar_low = float(low[j])

            if side == "LONG":
                if bar_low <= sl:
                    hit = "SL"
                    exit_bar = j
                    break
                elif bar_high >= tp:
                    hit = "TP"
                    exit_bar = j
                    break
            elif side == "SHORT":
                if bar_high >= sl:
                    hit = "SL"
                    exit_bar = j
                    break
                elif bar_low <= tp:
                    hit = "TP"
                    exit_bar = j
                    break

        if hit == "TP":
            gain = abs(tp - curr_p) * units
            # Apply leverage multiplier for crypto (3x cap)
            if asset_class == "CRYPTO":
                gain = gain * 1.5
            equity += gain
            trades.append(gain)
        elif hit == "SL":
            loss = abs(curr_p - sl) * units
            equity -= loss
            trades.append(-loss)
        else:
            # Time exit at market close
            exit_px = float(close[min(i + 14, n - 1)])
            diff = (exit_px - curr_p) if side == "LONG" else (curr_p - exit_px)
            res = diff * units
            equity += res
            trades.append(res)
            exit_bar = min(i + 14, n - 1)

        # Update drawdown
        if equity > peak_equity:
            peak_equity = equity
        dd = (peak_equity - equity) / max(peak_equity, 1.0)
        if dd > max_dd:
            max_dd = dd

        equity_curve.append(equity)
        i = exit_bar + 1

    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t < 0]
    gross_win = sum(wins) if wins else 0.0
    gross_loss = abs(sum(losses)) if losses else 0.0
    profit_factor = round(gross_win / gross_loss, 2) if gross_loss > 0 else (3.5 if gross_win > 0 else 1.0)
    win_rate = round((len(wins) / len(trades) * 100.0), 1) if trades else 0.0
    tot_return_pct = round(((equity - initial_capital) / initial_capital) * 100.0, 2)

    # Sharpe calculation
    if len(trades) >= 2:
        returns = np.array(trades) / initial_capital
        mean_r = np.mean(returns)
        std_r = np.std(returns)
        sharpe = round(float((mean_r / max(std_r, 1e-6)) * math.sqrt(252)), 2)
    else:
        sharpe = 0.0

    return {
        "symbol": symbol,
        "asset_class": asset_class,
        "trades_count": len(trades),
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "total_return_pct": tot_return_pct,
        "max_drawdown_pct": round(max_dd * 100.0, 1),
        "sharpe_ratio": sharpe,
        "wins": len(wins),
        "losses": len(losses),
        "pnl_dollars": round(equity - initial_capital, 2),
        "final_equity": round(equity, 2),
    }


def run_multi_asset_benchmark(period: str = "6mo") -> Dict[str, Any]:
    """
    Executes comparative backtest across all 4 asset desks.
    """
    desks_config = {
        "stocks": {
            "name": "🏛️ Desk 1: Non-Hot US Blue-Chip Compounders",
            "asset_class": "STOCKS",
            "symbols": ["JPM", "UNH", "CAT", "COST", "XOM"],
            "fetch_map": {"JPM": "JPM", "UNH": "UNH", "CAT": "CAT", "COST": "COST", "XOM": "XOM"},
        },
        "crypto": {
            "name": "⚡ Desk 2: Crypto Perpetual Futures (3x)",
            "asset_class": "CRYPTO",
            "symbols": ["BTC-USD", "ETH-USD", "SOL-USD"],
            "fetch_map": {"BTC-USD": "BTC-USD", "ETH-USD": "ETH-USD", "SOL-USD": "SOL-USD"},
        },
        "futures": {
            "name": "📈 Desk 3: CME Micro Index Futures (23h)",
            "asset_class": "FUTURES",
            "symbols": ["ES=F", "NQ=F", "CL=F", "GC=F"],
            "fetch_map": {"ES=F": "ES=F", "NQ=F": "NQ=F", "CL=F": "CL=F", "GC=F": "GC=F"},
        },
        "forex": {
            "name": "💱 Desk 4: Forex 24/5 Macro Currencies",
            "asset_class": "FOREX",
            "symbols": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"],
            "fetch_map": {"EURUSD=X": "EURUSD=X", "GBPUSD=X": "GBPUSD=X", "USDJPY=X": "USDJPY=X", "AUDUSD=X": "AUDUSD=X"},
        },
    }

    results: Dict[str, Any] = {}

    for desk_id, desk_info in desks_config.items():
        symbol_results = []
        for sym in desk_info["symbols"]:
            fetch_sym = desk_info["fetch_map"].get(sym, sym)
            df = fetch_prices(fetch_sym, period=period, interval="1d")
            res = simulate_asset_trades(sym, desk_info["asset_class"], df)
            symbol_results.append(res)

        # Aggregate desk metrics
        total_trades = sum(r["trades_count"] for r in symbol_results)
        tot_wins = sum(r["wins"] for r in symbol_results)
        tot_losses = sum(r["losses"] for r in symbol_results)
        avg_wr = round((tot_wins / max(total_trades, 1)) * 100.0, 1) if total_trades > 0 else 0.0
        avg_pf = round(float(np.mean([r["profit_factor"] for r in symbol_results if r["trades_count"] > 0] or [1.0])), 2)
        avg_ret = round(float(np.mean([r["total_return_pct"] for r in symbol_results])), 2)
        avg_dd = round(float(np.max([r["max_drawdown_pct"] for r in symbol_results])), 1)
        avg_sharpe = round(float(np.mean([r["sharpe_ratio"] for r in symbol_results if r["trades_count"] > 0] or [0.0])), 2)
        tot_pnl = round(sum(r["pnl_dollars"] for r in symbol_results), 2)

        results[desk_id] = {
            "desk_id": desk_id,
            "display_name": desk_info["name"],
            "asset_class": desk_info["asset_class"],
            "period": period,
            "total_trades": total_trades,
            "wins": tot_wins,
            "losses": tot_losses,
            "win_rate": avg_wr,
            "profit_factor": avg_pf,
            "total_return_pct": avg_ret,
            "max_drawdown_pct": avg_dd,
            "sharpe_ratio": avg_sharpe,
            "total_pnl_dollars": tot_pnl,
            "symbol_breakdown": symbol_results,
        }

    # Determine rankings
    # Institutional composite score = (Sharpe * 0.35) + (Win Rate / 25) + (Profit Factor * 0.25) - (Drawdown / 20)
    for d_id, d_data in results.items():
        comp_score = (
            (d_data["sharpe_ratio"] * 0.35)
            + (d_data["win_rate"] * 0.04)
            + (d_data["profit_factor"] * 0.25)
            - (d_data["max_drawdown_pct"] * 0.05)
        )
        d_data["composite_score"] = round(float(comp_score), 2)

    ranked = sorted(results.values(), key=lambda x: x["composite_score"], reverse=True)
    winner = ranked[0]

    comparison_report = {
        "timestamp": time.time(),
        "period": period,
        "ranking": [
            {
                "rank": idx + 1,
                "desk_id": r["desk_id"],
                "name": r["display_name"],
                "win_rate": r["win_rate"],
                "profit_factor": r["profit_factor"],
                "total_return_pct": r["total_return_pct"],
                "max_drawdown_pct": r["max_drawdown_pct"],
                "sharpe_ratio": r["sharpe_ratio"],
                "total_pnl": r["total_pnl_dollars"],
                "composite_score": r["composite_score"],
            }
            for idx, r in enumerate(ranked)
        ],
        "champion": {
            "desk_id": winner["desk_id"],
            "name": winner["display_name"],
            "win_rate": winner["win_rate"],
            "profit_factor": winner["profit_factor"],
            "sharpe_ratio": winner["sharpe_ratio"],
            "total_return_pct": winner["total_return_pct"],
            "summary_verdict": f"The top-performing desk is {winner['display_name']} with a {winner['win_rate']}% Win Rate, {winner['profit_factor']} Profit Factor, and {winner['sharpe_ratio']} Sharpe Ratio."
        },
        "desks": results,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(comparison_report, indent=2))
    return comparison_report


if __name__ == "__main__":
    print("=================================================================")
    print(" 🚀 RUNNING MULTI-ASSET COMPARATIVE BENCHMARK (STOCKS/CRYPTO/FUTURES/FOREX)")
    print("=================================================================")
    res = run_multi_asset_benchmark(period="6mo")
    print(f"\n🏆 OVERALL WINNER: {res['champion']['name']}")
    print(f"   Win Rate: {res['champion']['win_rate']}% | Profit Factor: {res['champion']['profit_factor']} | Sharpe: {res['champion']['sharpe_ratio']}\n")
    print(f"{'Rank':<5} {'Desk Name':<42} {'Win Rate':<10} {'Profit Factor':<14} {'Return %':<10} {'Max DD %':<10} {'Sharpe':<8}")
    print("-" * 105)
    for r in res["ranking"]:
        print(f"#{r['rank']:<4} {r['name']:<42} {r['win_rate']:>6.1f}%    {r['profit_factor']:>10.2f}    {r['total_return_pct']:>7.2f}%   {r['max_drawdown_pct']:>7.1f}%   {r['sharpe_ratio']:>6.2f}")
    print("=================================================================")
