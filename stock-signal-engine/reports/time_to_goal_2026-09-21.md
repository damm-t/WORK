# Time-to-Goal: 1x -> 10x (ruin floor at 80% loss)

- Bootstrapped from 112 OOS trades (~42/yr), WR 49.1%, mean +0.295R, Kelly f* 16.1%
- Growth-optimal risk f* = 12.5% (E[ln(1+fR)] = 0.0183/trade)
- Goal 10x · ruin floor 0.20x · 20,000 paths per risk level

| risk/trade | P(goal 1st) | med yrs | p5–p95 yrs | P(<=1y) | P(<=3y) | P(<=5y) | P(<=10y) | P(ruin 1st) | med maxDD |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2.0% | 100.0% | 9.8 | 6.3–15.3 | 0.0% | 0.0% | 0.6% | 52.2% | 0.0% | -25% |
| 5.0% | 99.9% | 4.3 | 2.1–8.9 | 0.0% | 21.4% | 63.0% | 97.0% | 0.1% | -45% |
| 8.0% | 97.4% | 2.9 | 1.1–7.2 | 2.7% | 50.8% | 80.6% | 96.3% | 2.6% | -57% |
| 10.0% | 92.8% | 2.4 | 0.8–6.5 | 8.2% | 59.2% | 81.7% | 92.3% | 7.2% | -63% |
| 12.0% | 85.9% | 2.0 | 0.6–5.6 | 14.1% | 62.7% | 79.1% | 85.6% | 14.1% | -67% |
| 15.0% | 73.9% | 1.5 | 0.5–4.6 | 21.8% | 61.6% | 71.0% | 73.8% | 26.1% | -70% |
| 20.0% | 55.5% | 0.9 | 0.3–3.0 | 29.1% | 52.6% | 55.2% | 55.5% | 44.5% | -71% |
| 25.0% | 43.0% | 0.6 | 0.2–2.0 | 31.0% | 42.6% | 43.0% | 43.0% | 57.0% | -70% |

Notes: fractional shares required at $100 (whole shares cannot buy
most universe names); the default 30% notional cap limits realized
risk to ~1.2%/trade — raise MAX_POSITION_NOTIONAL_PCT to realize
higher f. Cash accounts are 1x leverage: with 2xATR stops (~4-6% of
price) the max REALIZABLE per-trade risk at $100 is ~4-6%; beyond
that needs a margin account (broker minimum usually $2k+).
Growth-optimal f* = 12.5% — betting beyond it makes the
median slower, not faster.

Past performance does not guarantee future results.
