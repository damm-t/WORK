"""
Reality Check Simulator
=======================
Monte-Carlo of a single overnight session under different risk/win-rate
assumptions. Answers: "what does +50%-in-one-night actually require?"

Usage:
    python backtest/reality_check.py            # default scenarios
Modify SCENARIOS to test your own assumptions.
"""

import numpy as np

N_SIMS = 200_000
RUIN_DRAWDOWN = -0.30

SCENARIOS = {
    # name: (risk_per_trade, win_rate, reward_r, trades_per_night)
    "A. Current engine (2% risk, 45%WR, 1.3R, 4t)":  (0.02, 0.45, 1.3, 4),
    "B. Bold engine   (5% risk, 40%WR, 2.0R, 6t)":   (0.05, 0.40, 2.0, 6),
    "C. Hyper-bold    (10% risk, 55%WR, 2.0R, 12t)": (0.10, 0.55, 2.0, 12),
    "D. Casino        (25% risk, 40%WR, 2.0R, 6t)":  (0.25, 0.40, 2.0, 6),
}


def simulate_night(risk_per_trade: float, win_rate: float,
                   reward_r: float, n_trades: int) -> np.ndarray:
    rng = np.random.default_rng()
    eq = np.ones(N_SIMS)
    for _ in range(n_trades):
        wins = rng.random(N_SIMS) < win_rate
        eq *= np.where(wins, 1 + risk_per_trade * reward_r,
                       1 - risk_per_trade)
    return eq


def main() -> None:
    print(f"{'Scenario':<48}{'P(+50%/night)':>15}{'>=+20%':>10}"
          f"{'median':>10}{'P(-30%)':>10}")
    print("-" * 96)
    for name, (f, wr, r, nt) in SCENARIOS.items():
        eq = simulate_night(f, wr, r, nt)
        print(f"{name:<48}{(eq >= 1.5).mean() * 100:>14.3f}%"
              f"{(eq >= 1.2).mean() * 100:>9.1f}%"
              f"{np.median(eq):>9.3f}x"
              f"{(eq <= 1 + RUIN_DRAWDOWN).mean() * 100:>9.1f}%")

    f, r, p_win = 0.05, 2.0, 0.55
    need = int(np.ceil(np.log(1.5) / np.log(1 + f * r)))
    print(f"\nAt {f:.0%} risk & R={r}: {need} CONSECUTIVE wins needed "
          f"for +50%; P({need} straight @{p_win:.0%} WR) = "
          f"{p_win ** need * 100:.3f}%")


if __name__ == "__main__":
    main()