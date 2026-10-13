import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from market.price_fetcher import fetch_prices
from market.technicals import TechnicalIndicators as TI

CANDIDATES = [
    "JPM", "GS", "V", "BAC",
    "UNH", "LLY", "JNJ", "ABT",
    "CAT", "DE", "HON", "LMT",
    "COST", "PG", "WMT", "HD",
    "XOM", "CVX", "LIN"
]

df_spy = fetch_prices("SPY", period="20y", interval="1d")
spy_close = df_spy["Close"]
spy_sma200 = TI.sma(spy_close, 200)

stock_data = {}
for t in CANDIDATES:
    df = fetch_prices(t, period="20y", interval="1d")
    if not df.empty and len(df) > 1000:
        common = df.index.intersection(df_spy.index)
        if len(common) > 1000:
            df = df.loc[common].sort_index()
            c = df["Close"]
            stock_data[t] = {
                "df": df, "close": c, "high": df["High"], "low": df["Low"],
                "sma20": TI.sma(c, 20), "sma50": TI.sma(c, 50), "sma200": TI.sma(c, 200),
                "atr": TI.atr(df), "rsi": TI.rsi(c),
            }

dates = df_spy.index
warmup = 250

def run_mean_reversion(rsi_buy=32, rsi_sell=65, hold_max_days=10, stop_mult=2.0, max_pos=5, risk_pct=0.04):
    cash = 10000.0
    open_pos = {}
    history = []
    trade_list = []
    
    for i in range(warmup, len(dates)):
        dt = dates[i]
        spy_p = float(spy_close.iloc[i])
        spy_200 = float(spy_sma200.iloc[i]) if not pd.isna(spy_sma200.iloc[i]) else spy_p
        is_bull = (spy_p > spy_200) # Macro Regime Shield
        
        tot_val = 0.0
        closed = []
        for t, pos in list(open_pos.items()):
            s = stock_data[t]
            if dt not in s["close"].index: continue
            c, h, l = float(s["close"].loc[dt]), float(s["high"].loc[dt]), float(s["low"].loc[dt])
            pos["days_held"] += 1
            rsi_val = float(s["rsi"].loc[dt]) if not pd.isna(s["rsi"].loc[dt]) else 50.0
            
            # Exit conditions:
            # 1. Stop loss hit
            stop_hit = (l <= pos["stop"])
            # 2. Mean reversion target hit (RSI > rsi_sell or close > SMA20)
            target_hit = (rsi_val >= rsi_sell or c >= pos["target"])
            # 3. Max holding days reached
            time_exit = (pos["days_held"] >= hold_max_days)
            
            if stop_hit:
                exit_p = pos["stop"]
                pnl = pos["shares"] * (exit_p - pos["entry"])
                cash += pos["shares"] * exit_p
                trade_list.append({"t": t, "pnl": pnl, "res": "stop"})
                closed.append(t)
            elif target_hit or time_exit:
                exit_p = c
                pnl = pos["shares"] * (exit_p - pos["entry"])
                cash += pos["shares"] * exit_p
                trade_list.append({"t": t, "pnl": pnl, "res": "target" if target_hit else "time"})
                closed.append(t)
            else:
                tot_val += pos["shares"] * c
                
        for t in closed: del open_pos[t]
        equity = cash + tot_val
        history.append(equity)
        
        # Entries only if macro regime is bull (prevents catching falling knives in 2008 / 2022)
        if is_bull and len(open_pos) < max_pos:
            slots = max_pos - len(open_pos)
            cands = []
            for t, s in stock_data.items():
                if t in open_pos or dt not in s["close"].index: continue
                try:
                    c = float(s["close"].loc[dt])
                    s200 = float(s["sma200"].loc[dt])
                    s20 = float(s["sma20"].loc[dt])
                    rsi_v = float(s["rsi"].loc[dt])
                    atr_val = float(s["atr"].loc[dt])
                except Exception: continue
                if pd.isna(s200) or pd.isna(rsi_v) or pd.isna(atr_val) or atr_val <= 0: continue
                
                # Setup: Structural uptrend (c > s200) but short-term deep oversold dip (RSI < rsi_buy)
                if (c > s200) and (rsi_v <= rsi_buy):
                    cands.append((rsi_v, t, c, atr_val, s20))
                    
            cands.sort(key=lambda x: x[0]) # Most oversold first
            for _, t, c, a, s20 in cands[:slots]:
                risk_dlrs = equity * risk_pct
                stop_d = stop_mult * a
                sh = risk_dlrs / stop_d
                cost = sh * c
                if cost > equity * 0.25:
                    sh = (equity * 0.25) / c
                    cost = sh * c
                if cost <= cash * 0.95 and sh > 0:
                    cash -= cost
                    open_pos[t] = {
                        "entry": c, "shares": sh, "stop": c - stop_d,
                        "target": s20, "days_held": 0, "atr": a
                    }
                    
    curve = pd.Series(history, index=dates[warmup:])
    yrs = (curve.index[-1] - curve.index[0]).days / 365.25
    cagr = (curve.iloc[-1] / curve.iloc[0]) ** (1.0 / yrs) - 1.0
    peak = curve.cummax()
    max_dd = float(((curve - peak) / peak).min())
    daily_ret = curve.pct_change().dropna()
    sharpe = float(daily_ret.mean() / daily_ret.std() * math.sqrt(252)) if daily_ret.std() > 0 else 0.0
    wins = [x for x in trade_list if x["pnl"] > 0]
    wr = len(wins) / len(trade_list) * 100.0 if trade_list else 0.0
    print(f"RSI<{rsi_buy} -> {rsi_sell} (Max {hold_max_days}d) | Final: ${curve.iloc[-1]:>10,.0f} | CAGR: {cagr*100:>6.2f}% | MaxDD: {max_dd*100:>6.2f}% | Sharpe: {sharpe:>4.2f} | WR: {wr:>4.1f}% | Trades: {len(trade_list)}")

print("Testing JEV Mean-Reversion Sweeps on 20y Non-Hot Stocks...")
run_mean_reversion(rsi_buy=35, rsi_sell=60, hold_max_days=7, stop_mult=1.5, risk_pct=0.03)
run_mean_reversion(rsi_buy=32, rsi_sell=65, hold_max_days=10, stop_mult=2.0, risk_pct=0.035)
run_mean_reversion(rsi_buy=30, rsi_sell=60, hold_max_days=12, stop_mult=2.5, risk_pct=0.04)
run_mean_reversion(rsi_buy=28, rsi_sell=55, hold_max_days=8, stop_mult=2.0, risk_pct=0.045)
