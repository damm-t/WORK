import sys, math, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from market.price_fetcher import fetch_prices
from market.technicals import TechnicalIndicators as TI

# Diversified Non-Hot High-Quality Universe (No NVDA, MSFT, TSLA, AAPL, AMZN, META, GOOGL, SPCX)
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
                "sma50": TI.sma(c, 50), "sma200": TI.sma(c, 200),
                "atr": TI.atr(df), "rsi": TI.rsi(c),
                "high20": df["High"].rolling(20).max().shift(1),
                "low20": df["Low"].rolling(20).min().shift(1),
                "high50": df["High"].rolling(50).max().shift(1),
                "low20_trail": df["Low"].rolling(15).min().shift(1),
                "ret_6m": c.pct_change(126), # 6-month momentum
            }

dates = df_spy.index
warmup = 250

def run_test(name, entry_style="pullback", trail_mult=2.5, risk_pct=0.035, max_pos=4, max_alloc=0.30):
    cash = 10000.0
    open_pos = {}
    history = []
    trade_list = []
    
    for i in range(warmup, len(dates)):
        dt = dates[i]
        spy_p = float(spy_close.iloc[i])
        spy_200 = float(spy_sma200.iloc[i]) if not pd.isna(spy_sma200.iloc[i]) else spy_p
        is_bull = (spy_p > spy_200)
        
        # Mark to market and check exits
        tot_val = 0.0
        closed = []
        for t, pos in list(open_pos.items()):
            s = stock_data[t]
            if dt not in s["close"].index: continue
            c, h, l = float(s["close"].loc[dt]), float(s["high"].loc[dt]), float(s["low"].loc[dt])
            pos["highest"] = max(pos["highest"], h)
            
            # Stop loss check
            stop_hit = (l <= pos["stop"])
            # Or if macro flipped to bear, tighten stop
            if not is_bull:
                pos["stop"] = max(pos["stop"], pos["highest"] - 1.5 * pos["atr_entry"])
                
            if stop_hit:
                proceeds = pos["shares"] * pos["stop"]
                pnl = proceeds - pos["shares"] * pos["entry"]
                cash += proceeds
                trade_list.append({"t": t, "pnl": pnl + pos.get("tp1_pnl", 0.0)})
                closed.append(t)
                continue
                
            # TP1 check (scale out 35%, letting 65% run)
            if not pos["tp1_done"] and h >= pos["tp1"]:
                sell_sh = pos["shares"] * 0.35
                pos["shares"] -= sell_sh
                cash += sell_sh * pos["tp1"]
                pos["tp1_done"] = True
                pos["tp1_pnl"] = (pos["tp1"] - pos["entry"]) * sell_sh
                pos["stop"] = max(pos["stop"], pos["entry"] + 0.1 * pos["atr_entry"])
                
            # Trailing stop update
            if pos["tp1_done"]:
                trail = pos["highest"] - trail_mult * pos["atr_entry"]
                pos["stop"] = max(pos["stop"], trail)
            else:
                # Ratchet initial stop up as price expands
                if h >= pos["entry"] + 1.0 * pos["atr_entry"]:
                    pos["stop"] = max(pos["stop"], pos["entry"])
                    
            tot_val += pos["shares"] * c
            
        for t in closed: del open_pos[t]
        
        equity = cash + tot_val
        history.append(equity)
        
        # New entries if bull market and slots open
        if is_bull and len(open_pos) < max_pos:
            slots = max_pos - len(open_pos)
            cands = []
            for t, s in stock_data.items():
                if t in open_pos or dt not in s["close"].index: continue
                try:
                    c = float(s["close"].loc[dt])
                    s50, s200 = float(s["sma50"].loc[dt]), float(s["sma200"].loc[dt])
                    atr_val = float(s["atr"].loc[dt])
                    r6m = float(s["ret_6m"].loc[dt])
                    h20 = float(s["high20"].loc[dt])
                    h50 = float(s["high50"].loc[dt])
                    rsi_v = float(s["rsi"].loc[dt])
                except Exception: continue
                
                if pd.isna(s50) or pd.isna(s200) or pd.isna(atr_val) or atr_val <= 0: continue
                
                # Check entry style
                if entry_style == "breakout":
                    # Breakout to 20-day high with Golden cross and strong 6m momentum
                    cond = (c >= h20) and (c > s50 > s200) and (r6m > 0.05)
                elif entry_style == "quality_pullback":
                    # Pullback to 50 SMA in structural uptrend
                    cond = (c > s50 > s200) and (40 <= rsi_v <= 60) and (r6m > 0.05)
                else: # combined hybrid
                    cond = ((c >= h20) or (40 <= rsi_v <= 58)) and (c > s50 > s200) and (r6m > 0.05)
                    
                if cond:
                    cands.append((r6m, t, c, atr_val))
                    
            cands.sort(key=lambda x: x[0], reverse=True)
            for _, t, c, a in cands[:slots]:
                risk_dlrs = equity * risk_pct
                stop_d = 1.5 * a
                sh = risk_dlrs / stop_d
                cost = sh * c
                if cost > equity * max_alloc:
                    sh = (equity * max_alloc) / c
                    cost = sh * c
                if cost <= cash * 0.95 and sh > 0:
                    cash -= cost
                    open_pos[t] = {
                        "entry": c, "shares": sh, "stop": c - stop_d,
                        "tp1": c + 2.0 * stop_d, "atr_entry": a,
                        "highest": c, "tp1_done": False, "tp1_pnl": 0.0
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
    print(f"{name:<25} | Final: ${curve.iloc[-1]:>10,.0f} | CAGR: {cagr*100:>6.2f}% | MaxDD: {max_dd*100:>6.2f}% | Sharpe: {sharpe:>4.2f} | WR: {wr:>4.1f}% | Trades: {len(trade_list)}")

print("Running model comparisons...")
run_test("1. Baseline Pullback (1.5x trail)", entry_style="quality_pullback", trail_mult=1.5, risk_pct=0.025, max_pos=6, max_alloc=0.20)
run_test("2. Breakout + 2.5x trail", entry_style="breakout", trail_mult=2.5, risk_pct=0.035, max_pos=4, max_alloc=0.28)
run_test("3. Breakout + 3.0x trail", entry_style="breakout", trail_mult=3.0, risk_pct=0.040, max_pos=4, max_alloc=0.30)
run_test("4. Hybrid Momentum + 2.5x trail", entry_style="combined", trail_mult=2.5, risk_pct=0.035, max_pos=4, max_alloc=0.28)
run_test("5. Hybrid + 3.0x trail (Compounding)", entry_style="combined", trail_mult=3.0, risk_pct=0.045, max_pos=3, max_alloc=0.35)
