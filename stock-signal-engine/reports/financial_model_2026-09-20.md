# Crisis-Tested Financial Model

- **Date:** 2026-09-20  
- **Method:** Financial Modeling Suite — sensitivity sweep → refinement → out-of-sample validation → crisis stress tests → Monte Carlo → capital scenarios
- **NVDA:** BANNED (all pools & sims)  
- **Train:** 2016-10-01 → 2020-12-31 (incl. COVID crash) · **Test:** 2024-01-01 → today (incl. 2022 bear) · Universe: core mega-caps minus NVDA (27 used)
- **Chosen profile:** `stop2.00_tp12.00_trail1.50_scale0.50_rsi65_trend1_hedged1`
- **Baseline:** `stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend0_hedged1`

## Validation (2021-2023) — candidate stability

| Profile | WinRate | Return | expR |
|---|---:|---:|---:|
| stop1.50_tp11.50_trail1.50_scale0.25_rsi65_trend1_hedged1 | 44.62% | -17.76% | -0.010 |
| stop1.50_tp11.50_trail1.50_scale0.50_rsi65_trend1_hedged1 | 44.62% | -17.20% | -0.005 |
| stop1.50_tp11.50_trail1.50_scale0.50_rsi65_trend1_hedged1 | 44.62% | -17.20% | -0.005 |
| stop1.50_tp11.50_trail1.50_scale0.75_rsi65_trend1_hedged1 | 44.62% | -16.70% | -0.000 |
| stop1.50_tp11.50_trail1.50_scale0.50_rsi65_trend1_hedged0 | 44.62% | +5.54% | -0.013 |
| stop1.50_tp11.50_trail1.00_scale0.50_rsi65_trend1_hedged1 | 44.44% | -21.97% | -0.014 |
| stop1.50_tp11.75_trail1.50_scale0.50_rsi65_trend1_hedged1 | 40.12% | -19.70% | -0.016 |
| stop2.00_tp12.00_trail1.50_scale0.50_rsi65_trend1_hedged1 | 45.36% | +19.40% | +0.265 |
| stop2.00_tp12.00_trail1.50_scale0.50_rsi65_trend1_hedged0 | 45.36% | +46.86% | +0.263 |
| stop1.25_tp11.50_trail1.50_scale0.50_rsi65_trend1_hedged1 | 45.3% | -15.57% | +0.019 |
| stop1.50_tp12.00_trail2.25_scale0.50_rsi55_trend1_hedged0 | 37.27% | -4.68% | -0.075 |
| stop1.50_tp12.00_trail2.25_scale0.50_rsi55_trend1_hedged1 | 37.27% | -24.17% | -0.059 |
| stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend0_hedged1 | 40.0% | -1.51% | +0.051 |
| stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend0_hedged0 | 40.0% | +15.37% | +0.035 |
| stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend1_hedged0 | 39.19% | +5.97% | -0.004 |

## Stage 3 — Out-of-sample test (2024 → today)

| Book | WinRate | Return | MaxDD | Sharpe | Trades | AvgR |
|---|---:|---:|---:|---:|---:|---:|
| Tuned | 49.11% | +15.92% | -24.16% | 0.44 | 112 | +0.295 |
| Baseline | 44.77% | -1.75% | -23.89% | 0.04 | 172 | +0.155 |

### Per-year win rate (tuned)

| Year | Trades | Wins | WinRate |
|---|---:|---:|---:|
| 2024 | 34 | 21 | 61.8% |
| 2025 | 42 | 15 | 35.7% |
| 2026 | 36 | 19 | 52.8% |

## Stage 3 — Crisis stress tests

| Crisis | WinRate | Return | MaxDD | Trades |
|---|---:|---:|---:|---:|
| 2018 Q4 correction | 25.0% | +6.75% | -4.34% | 12 |
| COVID crash (pure) | 0.0% | -7.59% | -7.59% | 9 |
| COVID full cycle | 41.67% | -8.32% | -21.74% | 24 |
| 2022 bear market | 36.67% | +25.65% | -16.08% | 30 |

## Stage 4 — Monte Carlo (one-year horizon)

- P(1y profit): **85.0%** · P(DD ≥ 20%): 10.4% · P(ruin −30%): 0.8%
- Outcome bands: 5th -11.0% · median +22.4% · mean +24.9% · 95th +68.4%

## Stage 5 — Capital scenarios (out-of-sample)

| Capital | Book | Final | Return | WinRate | MaxDD | Trades |
|---:|---|---:|---:|---:|---:|---:|
| $1,000 | integer | $751.54 | -24.85% | 20.0% | -36.07% | 35 |
| $1,000 | fractional | $1,159.20 | +15.92% | 49.11% | -24.16% | 112 |
| $5,000 | integer | $5,805.32 | +16.11% | 49.52% | -22.56% | 105 |
| $5,000 | fractional | $5,795.99 | +15.92% | 49.11% | -24.16% | 112 |
| $10,000 | integer | $11,378.41 | +13.78% | 49.11% | -23.31% | 112 |
| $10,000 | fractional | $11,592.00 | +15.92% | 49.11% | -24.16% | 112 |

## Assumptions & limits

- Daily bars; fills at stop/TP levels with slippage modeled via round-trip cost model (spread + slippage + SEC/TAF fees).
- Fixed-fractional 2% risk, 3 concurrent slots, SH inverse-ETF hedge sized by 60-day beta × SPY regime multiplier (live-engine parity).
- Train window includes a crash; test window includes a bear market. Monte Carlo resamples actual OOS trade R's (no distribution assumptions) but assumes trade independence.
- Past performance does not guarantee future results. Paper-trading research only — not financial advice.
