# Crisis-Tested Financial Model

- **Date:** 2026-10-04  
- **Method:** Financial Modeling Suite — sensitivity sweep → refinement → out-of-sample validation → crisis stress tests → Monte Carlo → capital scenarios
- **NVDA:** BANNED (all pools & sims)  
- **Train:** 2016-10-01 → 2020-12-31 (incl. COVID crash) · **Test:** 2024-01-01 → today (incl. 2022 bear) · Universe: core mega-caps minus NVDA (27 used)
- **Chosen profile:** `stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend1_hedged1_be0.00+0.00_reg0_sec0_minPSI45_dynHdg`
- **Baseline:** `stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend0_hedged1_be0.00+0.00_reg0_sec0`

## Validation (2021-2023) — candidate stability

| Profile | WinRate | Return | expR |
|---|---:|---:|---:|
| stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend1_hedged1_be0.00+0.00_reg0_sec0_adpPSI_minPSI55 | 42.14% | -24.65% | -0.035 |
| stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend1_hedged1_be0.00+0.00_reg0_sec0_adpPSI_minPSI50 | 43.97% | -21.45% | -0.006 |
| stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend0_hedged1_be0.00+0.00_reg0_sec0 | 40.0% | -1.51% | +0.050 |
| stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend0_hedged0_be0.00+0.00_reg0_sec0 | 40.0% | +15.37% | +0.035 |
| stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend1_hedged0_be0.00+0.00_reg0_sec0 | 39.19% | +5.97% | -0.004 |
| stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend1_hedged1_be0.00+0.00_reg0_sec0_adpPSI_minPSI45_dynHdg | 44.3% | -10.33% | -0.062 |
| stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend1_hedged1_be0.00+0.00_reg0_sec0_adpPSI_dynHdg | 50.92% | -0.69% | +0.001 |
| stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend1_hedged1_be0.00+0.00_reg0_sec0_minPSI45_dynHdg | 38.89% | +9.05% | +0.067 |
| stop1.50_tp12.00_trail1.50_scale0.50_rsi65_trend1_hedged0_be0.00+0.00_reg0_sec0_adpPSI_minPSI45 | 44.3% | -6.08% | -0.063 |

## Stage 3 — Out-of-sample test (2024 → today)

| Book | WinRate | Return | MaxDD | Sharpe | Trades | AvgR |
|---|---:|---:|---:|---:|---:|---:|
| Tuned | 41.18% | +8.04% | -25.65% | 0.27 | 170 | +0.037 |
| Baseline | 43.6% | -4.54% | -23.89% | -0.03 | 172 | +0.145 |

### Per-year win rate (tuned)

| Year | Trades | Wins | WinRate |
|---|---:|---:|---:|
| 2024 | 60 | 28 | 46.7% |
| 2025 | 57 | 18 | 31.6% |
| 2026 | 53 | 24 | 45.3% |

## Stage 3 — Crisis stress tests

| Crisis | WinRate | Return | MaxDD | Trades |
|---|---:|---:|---:|---:|
| 2018 Q4 correction | 29.41% | -1.61% | -7.13% | 17 |
| COVID crash (pure) | 0.0% | -4.92% | -5.19% | 5 |
| COVID full cycle | 50.0% | +28.13% | -9.19% | 44 |
| 2022 bear market | 29.73% | -0.50% | -12.82% | 37 |

## Stage 4 — Monte Carlo (one-year horizon)

- P(1y profit): **51.9%** · P(DD ≥ 20%): 36.0% · P(ruin −30%): 7.9%
- Outcome bands: 5th -27.2% · median +1.0% · mean +3.3% · 95th +41.4%

## Stage 5 — Capital scenarios (out-of-sample)

| Capital | Book | Final | Return | WinRate | MaxDD | Trades |
|---:|---|---:|---:|---:|---:|---:|
| $1,000 | integer | $1,302.15 | +30.22% | 24.59% | -21.86% | 61 |
| $1,000 | fractional | $1,080.41 | +8.04% | 41.18% | -25.65% | 170 |
| $5,000 | integer | $4,519.96 | -9.60% | 38.26% | -25.06% | 149 |
| $5,000 | fractional | $5,402.02 | +8.04% | 41.18% | -25.65% | 170 |
| $10,000 | integer | $10,401.93 | +4.02% | 41.18% | -25.43% | 170 |
| $10,000 | fractional | $10,804.06 | +8.04% | 41.18% | -25.65% | 170 |

## Assumptions & limits

- Daily bars; fills at stop/TP levels with slippage modeled via round-trip cost model (spread + slippage + SEC/TAF fees).
- Fixed-fractional 2% risk, 3 concurrent slots, SH inverse-ETF hedge sized by 60-day beta × SPY regime multiplier (live-engine parity).
- Train window includes a crash; test window includes a bear market. Monte Carlo resamples actual OOS trade R's (no distribution assumptions) but assumes trade independence.
- Past performance does not guarantee future results. Paper-trading research only — not financial advice.
