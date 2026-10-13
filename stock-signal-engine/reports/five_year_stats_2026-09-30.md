# Five-Year Market Statistics

- **Date:** 2026-09-30  
- **Universe:** core (28 tickers requested, 28 simulated)  
- **Window:** 5 years of daily bars  
- **Config:** capital $10,000, risk 2%, style `conservative`, fractional=True

Strategy = the engine's conservative paired book (MACD+RSI pullback entries, 1.5xATR stop, TP1 scale-out, ratchet trail, SPY-regime sizing, SH inverse-ETF hedge). Buy & Hold uses closing prices (dividends not modelled).

## Leaderboard (by engine strategy final equity)

| # | Ticker | Sector | B&H CAGR | B&H MaxDD | Best Yr | Strat Ret | Strat DD | Trades | WinRate | Unhedged Ret |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | CAT | Industrials | +33.70 | -34.30 | +57.90 | +48.45 | -9.44 | 43 | 48.80 | +59.43 |
| 2 | NVDA | Technology | +62.20 | -66.40 | +238.90 | +35.82 | -10.58 | 41 | 48.80 | +52.99 |
| 3 | JPM | Financials | +15.40 | -40.60 | +40.90 | +30.50 | -14.29 | 35 | 51.40 | +46.14 |
| 4 | AAPL | Technology | +19.10 | -33.40 | +48.20 | +27.38 | -9.48 | 41 | 46.30 | +35.65 |
| 5 | AMD | Technology | +42.60 | -65.40 | +180.60 | +19.87 | -13.03 | 40 | 37.50 | +28.61 |
| 6 | GOOGL | Communication | +21.40 | -44.30 | +65.30 | +18.98 | -11.90 | 33 | 42.40 | +30.89 |
| 7 | AMZN | Consumer Disc. | +9.00 | -55.70 | +80.90 | +16.08 | -8.33 | 40 | 47.50 | +40.14 |
| 8 | KO | Staples | +10.70 | -20.90 | +24.30 | +15.23 | -14.45 | 30 | 40.00 | +16.18 |
| 9 | GS | Financials | +19.20 | -34.00 | +53.50 | +14.35 | -11.53 | 42 | 40.50 | +22.90 |
| 10 | XOM | Energy | +22.80 | -20.70 | +80.30 | +13.46 | -14.99 | 47 | 36.20 | +13.05 |
| 11 | NFLX | Communication | +2.80 | -75.90 | +83.10 | +12.39 | -13.37 | 35 | 45.70 | +25.41 |
| 12 | DUK | Utilities | +3.20 | -26.00 | +11.00 | +7.76 | -10.84 | 33 | 39.40 | +8.67 |
| 13 | UNH | Healthcare | -1.10 | -62.00 | +28.50 | +5.81 | -19.24 | 33 | 39.40 | +10.98 |
| 14 | CVX | Energy | +15.20 | -28.90 | +53.00 | +5.76 | -22.32 | 44 | 34.10 | +8.93 |
| 15 | LLY | Healthcare | +38.90 | -34.80 | +59.30 | +4.14 | -15.87 | 37 | 40.50 | +16.79 |
| 16 | MSFT | Technology | +13.00 | -37.60 | +56.80 | +3.72 | -10.33 | 39 | 38.50 | +19.10 |
| 17 | V | Financials | +10.30 | -24.50 | +25.30 | +1.69 | -17.86 | 34 | 35.30 | +3.26 |
| 18 | JNJ | Healthcare | +10.70 | -23.60 | +43.10 | +0.41 | -18.16 | 30 | 36.70 | +3.28 |
| 19 | LIN | Materials | +10.40 | -23.70 | +25.90 | -1.39 | -13.80 | 28 | 32.10 | +0.12 |
| 20 | META | Communication | +16.70 | -74.40 | +194.10 | -1.94 | -20.87 | 44 | 34.10 | +7.00 |
| 21 | FCX | Materials | +17.10 | -51.70 | +40.50 | -3.45 | -15.96 | 47 | 31.90 | -4.36 |
| 22 | HD | Consumer Disc. | -2.80 | -35.90 | +26.40 | -4.20 | -11.82 | 40 | 35.00 | +2.01 |
| 23 | TSLA | Consumer Disc. | +6.10 | -73.60 | +101.70 | -5.77 | -14.53 | 39 | 28.20 | +5.77 |
| 24 | PLD | Real Estate | +0.90 | -48.10 | +34.20 | -6.86 | -14.51 | 37 | 32.40 | -2.78 |
| 25 | NEE | Utilities | -0.60 | -47.20 | +18.90 | -7.64 | -20.32 | 33 | 27.30 | -7.24 |
| 26 | AMT | Real Estate | -9.20 | -46.10 | +10.20 | -11.61 | -18.53 | 39 | 30.80 | -8.71 |
| 27 | BA | Industrials | -3.10 | -50.30 | +36.80 | -15.17 | -17.63 | 34 | 26.50 | -10.95 |
| 28 | PG | Staples | +1.10 | -24.60 | +17.00 | -19.95 | -22.01 | 32 | 25.00 | -18.28 |

## Benchmark — SPY buy & hold

CAGR +12.40 · vol 17.20 · Sharpe 0.77 · MaxDD -25.40 · best yr +24.30 · worst yr -19.50

## Sector rollup (avg per stock)

| Sector | N | B&H CAGR | Strat Ret | Unhedged | Trades | WinRate |
|---|---:|---:|---:|---:|---:|---:|
| Technology | 4 | +34.23 | +21.70 | +34.09 | 40.2 | 42.77 |
| Industrials | 2 | +15.30 | +16.64 | +24.24 | 38.5 | 37.65 |
| Financials | 3 | +14.97 | +15.51 | +24.10 | 37.0 | 42.40 |
| Communication | 3 | +13.63 | +9.81 | +21.10 | 37.3 | 40.73 |
| Energy | 2 | +19.00 | +9.61 | +10.99 | 45.5 | 35.15 |
| Healthcare | 3 | +16.17 | +3.45 | +10.35 | 33.3 | 38.87 |
| Consumer Disc. | 3 | +4.10 | +2.04 | +15.97 | 39.7 | 36.90 |
| Utilities | 2 | +1.30 | +0.06 | +0.71 | 33.0 | 33.35 |
| Staples | 2 | +5.90 | -2.36 | -1.05 | 31.0 | 32.50 |
| Materials | 2 | +13.75 | -2.42 | -2.12 | 37.5 | 32.00 |
| Real Estate | 2 | -4.15 | -9.23 | -5.75 | 38.0 | 31.60 |
