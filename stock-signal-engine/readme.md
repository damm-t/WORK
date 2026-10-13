# 📈 Stock Signal Engine — Personal Quant Desk

A self-contained quantitative trading research & paper-trading system:
**FinBERT news sentiment → technical confluence → graded entries →
beta-hedged execution → ratcheting exits → measured win-rate feedback loop.**

> ⚠️ **Paper trading only.** This is an educational quant laboratory for
> managing *your own* capital with discipline. Not financial advice.

---

## 🏗️ Architecture

```
┌────────────── DATA ──────────────┐   ┌────────── INTELLIGENCE ──────────┐
│ ingestion/   news·tweets·SEC     │   │ nlp/finbert      sentiment+conf  │
│ market/      OHLCV·technicals★   │   │ model/ensemble   LGBM/rules blend│
│ market/beta_calculator  β·regime │   │ backtest/scanner sector ranking  │
└──────────────┬───────────────────┘   └──────────────┬───────────────────┘
               ▼                                      ▼
┌─────────────────────────── RISK (gates in order) ───────────────────────┐
│ shock_detector (gap/velocity freeze) → earnings blackout                │
│ → trade_scorer (grade A/B/C) → cost_model (fees viability)              │
│ → sizing (RISK_PCT · fractional Kelly) → heat cap → tail-risk cap       │
└───────────────────────────────┬─────────────────────────────────────────┘
                                ▼
┌────── EXECUTION ──────┐   ┌────── FEEDBACK LOOP ─────────────────────────┐
│ alpha_client paired   │   │ trade_journal v2 (context ledger)            │
│ Long + GTC stop       │   │ reports/dashboard.html (one-command visuals) │
│ + inverse-ETF hedge   │   │ walk_forward.py (anti-overfit style policy)  │
│ autopilot daemon      │   │ reality_check.py (Monte-Carlo expectations)  │
└───────────────────────┘   └──────────────────────────────────────────────┘
```

## 🚀 Quick Start

```bash
# 1. Environment (.env at project root)
APCA_API_KEY_ID=...        # Alpaca PAPER keys
APCA_API_SECRET_KEY=...
SEC_USER_AGENT=...         # "Name email@example.com"
INTERNAL_API_KEY=...       # protects POST endpoints

# 2. Install (Python 3.12 venv recommended)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Sanity checks
python -m unittest discover -s tests -v          # 21 regression tests
python backtest/market_scanner.py --mode scan --top 5

# 4. See the dashboard (demo data)
python -m reports/dashboard.py --demo            # then open reports/dashboard.html
```

## 📁 Project Structure

| Path | Purpose |
|---|---|
| `ingestion/` | News / Twitter / SEC fetchers (+6h-fresh cache fallback) |
| `nlp/` | FinBERT sentiment · NER · **news_memory** (SQLite narrative search) |
| `market/` | price_fetcher · **technicals** (single-source indicators) · beta/regime · **shock_detector** |
| `model/` | LightGBM predictor + rule ensemble fallback |
| `features/` | Feature-vector builder for ML |
| `risk/` | **hedging_engine** · **trade_scorer** · **cost_model** · risk_manager |
| `execution/` | Alpaca client · **autopilot daemon** · **trade_journal** |
| `backtest/` | **hedging_backtester** (2 styles) · **market_scanner** · **walk_forward** · sentiment comparator · reality_check · universe |
| `reports/` | **dashboard.py** → self-contained HTML |
| `api/` | FastAPI service (`/signal`, `/hedge/evaluate/{t}`, `/regime`, …) |
| `tests/` | Regression suite (`python -m unittest discover -s tests`) |

★ = recently added core modules

---

## 🌙 The Daily Operating Loop

**Automated via the Daily Routine Orchestrator:**

```bash
# ☀️ MORNING (~09:00 MYT): scrape universe + FinBERT + warm caches
python backtest/daily_routine.py --mode morning --universe core
cat data/briefings/briefing_$(date +%Y-%m-%d).json | head -40

# 📊 OFF-HOURS: analysis compiles tonight's PLAN (watchlist/avoids/tweaks)
python backtest/daily_routine.py --mode analyze --wf-ticker NVDA
cat reports/plan_$(date +%Y-%m-%d).md

# Schedule both automatically via cron:
# 30 7 * * *  cd /path/to/engine && .venv/bin/python backtest/daily_routine.py \
#             --mode full >> logs/routine.log 2>&1
```

The plan file includes tonight's watchlist, names to avoid (earnings/negative
sentiment), walk-forward style evidence, and env tweaks suggested by realised
trades — then paste its launch command.

```
 MORNING (optional)                EVENING (21:30 MYT = US open)        NEXT MORNING
┌──────────────────────────┐   ┌────────────────────────────────┐   ┌─────────────────────┐
│ scan → pick candidates    │   │ launch Scenario C in tmux      │   │ analytics + walk-   │
│ validate via hedge-eval   │→  │ auto-selects ≥75-score names,  │→  │ forward + dashboard │
│                           │   │ grades, sizes, hedges, journals│   │ → apply 1 tweak     │
└──────────────────────────┘   └────────────────────────────────┘   └─────────────────────┘
```

### Step-by-step

```bash
cd /Users/voonfamily/Desktop/WORK/stock-signal-engine

# ① Morning — where is the market leading?
python backtest/market_scanner.py --mode scan --universe wide --top 5

# ② Validate a candidate (sentiment + grade + cost viability + hedge plan)
python backtest/sentiment_hedged_vs_unhedged.py --tickers FCX --capital 100 --force-buy

# ③ Before 21:30 — launch overnight paper session
brew install tmux                       # once
tmux new -s operationC './scenario_c.sh --interval 900 --auto-select --top-picks 3'
#    detach: Ctrl+B then D   ·   reattach: tmux attach -t operationC

# ④ Anytime — monitor
tail -f logs/autopilot_$(date +%Y%m%d).log
python -m execution.trade_journal --stats
open reports/dashboard.html             # after regenerating (below)

# ⑤ Next morning — stand down & review
kill $(cat logs/autopilot.pid)
python -m execution.trade_journal --analytics
python backtest/walk_forward.py --ticker NVDA --months 4 --capital 100 --fractional
python -m reports.dashboard && open reports/dashboard.html
```

---

## 🧰 Command Reference

| Tool | Command | What it does |
|---|---|---|
| **Scanner** | `python backtest/market_scanner.py --mode scan [--universe wide] [--top N]` | Ranks whole universe (momentum/breakout/sector) |
| | `--mode backtest --start … --end …` | Mass sector-aggregated backtest |
| **Backtester** | `python backtest/hedging_backtester.py --ticker T [--style bold] [--fractional] [--start/--end]` | Unhedged-vs-hedged comparison |
| **Walk-forward** | `python backtest/walk_forward.py --ticker T --months 6 [--fractional]` | Anti-overfit style policy |
| **Sentiment desk** | `python backtest/sentiment_hedged_vs_unhedged.py --tickers X,Y [--force-buy]` | News-driven paired-trade preview |
| **Reality check** | `python backtest/reality_check.py` | Monte-Carlo of overnight expectations |
| **Autopilot** | `./run_autopilot.sh --interval 900 [--auto-select] [--dry-run]` | Conservative daemon |
| **Scenario C** | `./scenario_c.sh [same flags]` | Hyper-bold preset (10% risk, heat 90%, gate 65) |
| **Journal** | `python -m execution.trade_journal [--stats|--analytics|--reset]` | Ledger scoreboard / tuning tips |
| **Dashboard** | `python -m reports/dashboard.py [--demo] [--serve]` | HTML command center |

### Autopilot flags
`--watchlist A,B,C` · `--interval SEC` · `--once` · `--dry-run` ·
`--ignore-market-hours` · `--auto-select` · `--min-auto-score 70` ·
`--top-picks 3` · `--risk-pct 0.10` · `--heat 0.90` · `--min-trade-score 65`

---

## 🛡️ Safety Stack (evaluated top-down every cycle)

1. **Market-hours gate** — idles until Alpaca says OPEN
2. **Daily-loss kill-switch** (`DAILY_LOSS_LIMIT=-0.05`) — entries frozen at −5% day; exits stay managed
3. **Earnings blackout** (`EARNINGS_BLACKOUT_DAYS=1`) — no new entries near scheduled earnings
4. **Shock freeze / shock-exit** (`GAP_SHOCK_PCT=2.5`, `VELOCITY_SHOCK_PCT=1.2`) — abnormal tape detected from 5-min bars
5. **FinBERT sentiment gate** — bearish conviction = no trade
6. **Trade-quality grade** (`MIN_TRADE_SCORE=55`; C=skip, B=60% size, A=full)
7. **Cost viability** — TP must clear round-trip costs ×5
8. **Sizing** — `RISK_PCT` (default .02) ÷ ATR-stop, fractional-capable
9. **Heat cap** (`MAX_PORTFOLIO_HEAT=.20`) + **notional cap per position** (`MAX_POSITION_NOTIONAL_PCT`)
10. **Tail-risk cap** — net beta exposure ≤ 1× equity
11. **Exits** — GTC hard stop + ratcheting trail (armed after TP1; pure runner in bold)

---

## ⚙️ Configuration Knobs (env / .env — all optional)

| Variable | Default | Effect |
|---|---|---|
| `RISK_PCT` | `0.02` | % of equity risked per trade (C uses 0.10) |
| `MAX_PORTFOLIO_HEAT` | `0.20` | Max total open exposure fraction |
| `MAX_POSITION_NOTIONAL_PCT` | `1.00` | Cap on any single position's value |
| `MIN_TRADE_SCORE` | `55` | Trade-grade floor (C preset: 65) |
| `MIN_AUTO_SCORE` | `70` (`65` in `./quant`) | Scanner score floor in auto-select — read by the autopilot from env |
| `GAP_SHOCK_PCT` / `VELOCITY_SHOCK_PCT` | `2.5` / `1.2` | Shock reflex thresholds |
| `EARNINGS_BLACKOUT_DAYS` | `1` | Entry-freeze days before earnings |
| `DAILY_LOSS_LIMIT` | `-0.05` | Kill-switch threshold |
| `STOP_ATR_MULT` / `TP1_ATR_MULT` / `TP2_TRIGGER_ATR_MULT` / `TRAIL_ATR_MULT` | `1.5 / 2.0 / 3.5 / 1.5` | Exit-ladder geometry (set by `scenario_small.sh` to `2.0/2.0/3.5/1.5`) |
| `TRAIL_ARM_ATR_MULT` | `=TP2 (3.5)` | Trail arming threshold (tuned preset arms right after TP1 at 2.0) |
| `TP1_SCALE_OUT_PCT` / `TP1_AUTOMATION` | `0.50` / off | TP1 scale-out fraction / autopilot sells the clip itself |
| `REQUIRE_SMA50_ABOVE_SMA200` / `TUNED_RSI_MAX` | off / off | Tuned entry filters (SMA50>SMA200, RSI 35–65) |
| `USE_LGBM_RUNTIME` | `0` (forced) | LightGBM hangs on macOS — keep 0 |

---

## 🧪 Backtesting Guide

```bash
# Style race over any window (fractional = small-account mode)
python backtest/hedging_backtester.py --ticker NVDA --start 2026-05-26 \
    --end 2026-08-25 --capital 100 --fractional --style bold --risk-pct 0.05

# Whole-market sector league (28 or 88 names)
python backtest/market_scanner.py --mode backtest --universe wide \
    --start 2022-01-01 --end 2022-12-31 --capital 100 --style bold --fractional

# Anti-overfit style policy
python backtest/walk_forward.py --ticker NVDA --months 6 --capital 100 --fractional

# "Can I double overnight?" — the honest math
python backtest/reality_check.py
```

Notes: `--start/--end` auto-fetches ~200 days of lead-in for indicator warmup;
metrics cover only your window. All price data caches to `market/cache/`.

---

## 📊 Dashboard

```bash
python -m reports.dashboard                # snapshot: regenerate on demand
python -m reports/dashboard.py --demo      # preview layout with sample trades
python -m reports/dashboard.py --serve     # also serve at localhost:8999

# LIVE MODE — auto-regenerates + browser self-refreshes every N seconds:
python -m reports/dashboard.py --watch 60 --serve
# (keep the tab open; pair it with the autopilot running in tmux)
```

Sections: account snapshot · win-rate/R:R cards · auto-balance suggestions ·
grade & session breakdowns · live leaderboard · open positions · trade ledger.

---

## 🖥️ Live Web App (`webapp/`)

The real-time version of the dashboard: FastAPI JSON backend + polling SPA.

```bash
chmod +x run_webapp.sh
./run_webapp.sh                          # http://localhost:8081
```

Open **http://localhost:8081** in a browser (keep it open during sessions —
it polls account/journal every 15s and the market leaderboard every 60s).

| Endpoint | Purpose |
|---|---|
| `GET /api/account` | Alpaca equity / cash / positions |
| `GET /api/journal/summary` | Stats + analytics + suggestions |
| `GET /api/journal/trades?limit=N` | Trade ledger |
| `GET /api/scan?top=N` | Market leaderboard (5-min TTL cache) |
| `GET /api/regime` | SPY regime snapshot |
| `POST /api/actions/rescan` | Force leaderboard refresh |
| `POST /api/actions/flatten` | **Market-exit a position + cancel its GTC stops** |

Actions require header `X-Dash-Token: <INTERNAL_API_KEY>` — the web page
prompts once and stores it locally. Every flatten is journaled as
`manual_flatten`.

---

## 🔧 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `[yfinance_news] Expecting value…` | Yahoo rate-limit | Auto-falls back to cache (6h freshness guard) — benign |
| `twitter_fetcher 401` | Invalid bearer token | Ignored gracefully; renew token in `.env` if tweets wanted |
| Hang during model load | LightGBM/OpenMP deadlock on macOS | Keep `USE_LGBM_RUNTIME=0`, `OMP_NUM_THREADS=1` (autopilot forces these) |
| FinBERT stalls at start | HF etag network check | `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` (autopilot forces) |
| `Autopilot already running` | Stale PID file | `kill $(cat logs/autopilot.pid)` then relaunch |
| Segfault with LGBM enabled | libomp/torch conflict | Same as hang fix — stay on rule ensemble |
| Orders rejected `buying power` | Heat/cash gate | Intended; lower `RISK_PCT` or raise caps knowingly |

---

## 🗺️ Roadmap

1. **Phase 1 finish** — journal analytics dashboard section ✔ · slippage tracker (signal vs fill)
2. **Phase 2** — deflated-Sharpe validation · point-in-time universe · regime attribution
3. **Phase 3** — correlation-aware sizing · cross-sectional factor ranking · Kelly from realised stats
4. **Phase 4** — Alpaca websocket streaming (sub-minute shock reflexes) · options module for defined-risk convexity

## 📜 Disclaimer

Paper trading laboratory for personal education. Markets involve substantial
risk; historical simulations do not guarantee future results. Nothing here is
financial advice — it is an engineering framework for *learning* quantitative
discipline before real money ever enters the picture.