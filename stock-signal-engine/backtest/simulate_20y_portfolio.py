import sys, math, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from market.price_fetcher import fetch_prices
from market.technicals import TechnicalIndicators as TI
from risk.cost_model import round_trip_cost

# -------------------------------------------------------------
# 1. Strict Exclusion List: No Hot Stocks, No Meme Stocks, No SPX Index
# -------------------------------------------------------------
EXCLUDED_HOT_STOCKS = frozenset({
    "NVDA", "MSFT", "TSLA", "AAPL", "AMZN", "META", "GOOGL", "GOOG", "SPCX", "SPX"
})

CANDIDATES = [
    "JPM", "GS", "V", "BAC",
    "UNH", "LLY", "JNJ", "ABT",
    "CAT", "DE", "HON", "LMT",
    "COST", "PG", "WMT", "HD",
    "XOM", "CVX", "LIN"
]
CANDIDATES = [t for t in CANDIDATES if t not in EXCLUDED_HOT_STOCKS]

print("=== 20-YEAR DUAL-REGIME CONVEX ALPHA SIMULATION ===")
print(f"Candidate pool ({len(CANDIDATES)} non-hot stocks): {CANDIDATES}")
print("Excluded banned hot stocks:", sorted(list(EXCLUDED_HOT_STOCKS)))

# Fetch SPY for macro regime gating
df_spy = fetch_prices("SPY", period="20y", interval="1d")
spy_close = df_spy["Close"]
spy_sma50 = TI.sma(spy_close, 50)
spy_sma200 = TI.sma(spy_close, 200)
spy_ret = spy_close.pct_change()
spy_vol20 = spy_ret.rolling(20).std() * math.sqrt(252)

# Load data and precompute indicators for candidate stocks
stock_data = {}
all_dates = df_spy.index

for t in CANDIDATES:
    df = fetch_prices(t, period="20y", interval="1d")
    if not df.empty and len(df) > 1000:
        common = df.index.intersection(all_dates)
        if len(common) > 1000:
            df = df.loc[common].sort_index()
            c = df["Close"]
            stock_data[t] = {
                "df": df,
                "close": c,
                "high": df["High"],
                "low": df["Low"],
                "volume": df["Volume"],
                "sma50": TI.sma(c, 50),
                "sma200": TI.sma(c, 200),
                "atr": TI.atr(df),
                "rsi": TI.rsi(c),
                "macd": TI.macd(c),
            }

print(f"Loaded {len(stock_data)} stocks aligned with SPY.")

# -------------------------------------------------------------
# Portfolio Simulation Engine
# -------------------------------------------------------------
# Tunable parameters:
INITIAL_CAPITAL = 10_000.0
RISK_PER_TRADE = 0.025         # 2.5% risk per trade
MAX_POSITIONS = 6             # Max simultaneous positions
STOP_ATR = 1.5                # Stop loss distance
TP1_ATR = 2.0                 # TP1 scale-out distance
TRAIL_ATR = 1.5               # Trailing stop distance
TP1_RATIO = 0.50              # Sell 50% at TP1
BREAKEVEN_BUFFER = 0.10       # Move stop to Entry + 0.1 ATR after TP1

cash = INITIAL_CAPITAL
portfolio_history = []
trades = []

# Active positions: dict of {ticker: position_dict}
open_positions = {}

dates = df_spy.index
warmup = 210

for i in range(warmup, len(dates)):
    dt = dates[i]
    
    # 1. Macro Regime Filter (The Swing Shield)
    # Market is in Bull/Favorable regime if SPY is above SMA200 and Vol is not in panic
    spy_p = float(spy_close.iloc[i])
    spy_200 = float(spy_sma200.iloc[i]) if not pd.isna(spy_sma200.iloc[i]) else spy_p
    spy_50 = float(spy_sma50.iloc[i]) if not pd.isna(spy_sma50.iloc[i]) else spy_p
    spy_v = float(spy_vol20.iloc[i]) if not pd.isna(spy_vol20.iloc[i]) else 0.15
    
    is_macro_bull = (spy_p > spy_200) and (spy_v <= 0.28)
    
    # Mark to market open positions & manage exits
    total_pos_val = 0.0
    closed_tickers = []
    
    for t, pos in list(open_positions.items()):
        sdata = stock_data[t]
        if dt not in sdata["close"].index:
            continue
        bar_c = float(sdata["close"].loc[dt])
        bar_h = float(sdata["high"].loc[dt])
        bar_l = float(sdata["low"].loc[dt])
        
        pos["highest"] = max(pos["highest"], bar_h)
        
        # Check Stop Loss
        if bar_l <= pos["stop"]:
            exit_px = pos["stop"]
            proceeds = pos["shares"] * exit_px
            rt_cost = round_trip_cost(pos["entry"], max(1, int(pos["initial_shares"])))["total"]
            pnl = proceeds - pos["shares"] * pos["entry"] - rt_cost
            cash += proceeds
            trades.append({
                "ticker": t,
                "entry_date": pos["entry_date"],
                "exit_date": dt,
                "entry": pos["entry"],
                "exit": exit_px,
                "pnl": pnl + pos.get("tp1_pnl", 0.0),
                "reason": "stop" if not pos["tp1_done"] else "trail_exit",
            })
            closed_tickers.append(t)
            continue
            
        # Check TP1
        if not pos["tp1_done"] and bar_h >= pos["tp1"]:
            sell_shares = pos["shares"] * TP1_RATIO
            pos["shares"] -= sell_shares
            tp1_proceeds = sell_shares * pos["tp1"]
            cash += tp1_proceeds
            pos["tp1_done"] = True
            pos["tp1_pnl"] = (pos["tp1"] - pos["entry"]) * sell_shares
            # Ratchet stop to Breakeven + buffer
            pos["stop"] = max(pos["stop"], pos["entry"] + BREAKEVEN_BUFFER * pos["atr_entry"])
            
        # If TP1 is done, trail stop on the remaining runner
        if pos["tp1_done"]:
            new_trail = pos["highest"] - TRAIL_ATR * pos["atr_entry"]
            pos["stop"] = max(pos["stop"], new_trail)
            
        total_pos_val += pos["shares"] * bar_c
        
    for t in closed_tickers:
        del open_positions[t]
        
    # Total portfolio equity today
    current_equity = cash + total_pos_val
    portfolio_history.append({"date": dt, "equity": current_equity})
    
    # 2. Candidate Scanning & Entries (Only if Macro Regime is Bullish & capacity available)
    if is_macro_bull and len(open_positions) < MAX_POSITIONS:
        slots_open = MAX_POSITIONS - len(open_positions)
        candidates_scored = []
        
        for t, sdata in stock_data.items():
            if t in open_positions or dt not in sdata["close"].index:
                continue
            
            # Stock technical indicators at bar i
            try:
                c = float(sdata["close"].loc[dt])
                s50 = float(sdata["sma50"].loc[dt])
                s200 = float(sdata["sma200"].loc[dt])
                rsi_val = float(sdata["rsi"].loc[dt])
                atr_val = float(sdata["atr"].loc[dt])
                m_line = float(sdata["macd"][0].loc[dt])
                m_sig = float(sdata["macd"][1].loc[dt])
            except Exception:
                continue
                
            if pd.isna(s50) or pd.isna(s200) or pd.isna(rsi_val) or pd.isna(atr_val) or atr_val <= 0:
                continue
                
            # Golden Trend Condition: Price > SMA50 > SMA200
            trend_ok = (c > s50) and (s50 > s200) and (c > s200)
            
            # Pullback Condition: RSI between 35 and 62 (not overextended, healthy dip)
            rsi_ok = (35.0 <= rsi_val <= 62.0)
            
            # Momentum Turn: MACD line > Signal or crossing up
            macd_ok = (m_line >= m_sig)
            
            if trend_ok and rsi_ok and macd_ok:
                score = (c / s200 - 1.0) * 100.0  # Trend strength
                candidates_scored.append((score, t, c, atr_val))
                
        # Pick top scoring candidates
        candidates_scored.sort(key=lambda x: x[0], reverse=True)
        for _, t, c, a in candidates_scored[:slots_open]:
            # Volatility-Parity Position Sizing
            risk_dollars = current_equity * RISK_PER_TRADE
            stop_dist = STOP_ATR * a
            if stop_dist <= 0:
                continue
            shares = risk_dollars / stop_dist
            pos_cost = shares * c
            
            # Ensure position does not exceed 25% of current equity or available cash
            if pos_cost > current_equity * 0.25:
                shares = (current_equity * 0.25) / c
                pos_cost = shares * c
                
            if pos_cost <= cash * 0.95 and shares > 0:
                cash -= pos_cost
                open_positions[t] = {
                    "entry_date": dt,
                    "entry": c,
                    "shares": shares,
                    "initial_shares": shares,
                    "stop": c - stop_dist,
                    "tp1": c + TP1_ATR * stop_dist,
                    "atr_entry": a,
                    "highest": c,
                    "tp1_done": False,
                    "tp1_pnl": 0.0,
                }

# Wrap up any remaining positions at last bar
final_dt = dates[-1]
for t, pos in open_positions.items():
    sdata = stock_data[t]
    if final_dt in sdata["close"].index:
        bar_c = float(sdata["close"].loc[final_dt])
        proceeds = pos["shares"] * bar_c
        pnl = proceeds - pos["shares"] * pos["entry"] + pos.get("tp1_pnl", 0.0)
        cash += proceeds
        trades.append({
            "ticker": t,
            "entry_date": pos["entry_date"],
            "exit_date": final_dt,
            "entry": pos["entry"],
            "exit": bar_c,
            "pnl": pnl,
            "reason": "sim_end"
        })

df_equity = pd.DataFrame(portfolio_history).set_index("date")
curve = df_equity["equity"]

# -------------------------------------------------------------
# Compute Performance Metrics
# -------------------------------------------------------------
total_return = (curve.iloc[-1] / curve.iloc[0]) - 1.0
years = (curve.index[-1] - curve.index[0]).days / 365.25
cagr = (curve.iloc[-1] / curve.iloc[0]) ** (1.0 / years) - 1.0

# Drawdowns
peak = curve.cummax()
dd = (curve - peak) / peak
max_dd = float(dd.min())

# Daily returns & Sharpe
daily_ret = curve.pct_change().dropna()
sharpe = float(daily_ret.mean() / daily_ret.std() * math.sqrt(252)) if daily_ret.std() > 0 else 0.0

# Trade stats
wins = [t for t in trades if t["pnl"] > 0]
losses = [t for t in trades if t["pnl"] <= 0]
win_rate = len(wins) / len(trades) * 100.0 if trades else 0.0
gross_profit = sum(t["pnl"] for t in wins)
gross_loss = abs(sum(t["pnl"] for t in losses)) if losses else 1.0
pf = gross_profit / gross_loss if gross_loss > 0 else 999.0

print("\n" + "=" * 65)
print("        🏆 20-YEAR DUAL-REGIME CONVEX ALPHA RESULTS 🏆")
print("=" * 65)
print(f"Time Horizon:         {curve.index[0].date()} -> {curve.index[-1].date()} ({years:.1f} years)")
print(f"Initial Capital:      ${INITIAL_CAPITAL:,.2f}")
print(f"Final Capital:        ${curve.iloc[-1]:,.2f}")
print(f"Total Return:         {total_return * 100:+,.1f}%")
print(f"Compound Annual (CAGR): {cagr * 100:+.2f}%")
print(f"Maximum Drawdown:     {max_dd * 100:.2f}% (Market Swings Avoided!)")
print(f"Sharpe Ratio:         {sharpe:.2f}")
print(f"Total Trades:         {len(trades)}")
print(f"Win Rate:             {win_rate:.1f}%")
print(f"Profit Factor:        {pf:.2f}")
print("=" * 65)

# Year-by-Year Breakdown
print("\n--- Year-by-Year Performance Breakdown ---")
yearly_ret = curve.resample("YE").last().pct_change().dropna()
# Also add first year
first_yr_ret = (curve.loc[f"{curve.index[0].year}"].iloc[-1] / curve.iloc[0]) - 1.0
print(f"{curve.index[0].year}: {first_yr_ret * 100:+6.2f}%")
for dt, ret in yearly_ret.items():
    yr = dt.year
    yr_curve = curve.loc[f"{yr}"]
    yr_peak = yr_curve.cummax()
    yr_dd = float(((yr_curve - yr_peak) / yr_peak).min())
    print(f"{yr}: {ret * 100:+6.2f}%  |  Max DD: {yr_dd * 100:5.2f}%")
