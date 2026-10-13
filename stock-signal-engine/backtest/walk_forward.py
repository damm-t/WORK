"""
Walk-Forward Style Selector
===========================
Anti-overfit harness answering ONE question with out-of-sample evidence:

    "Which entry technique should be allowed LIVE — conservative pullbacks,
     or bold breakouts?"

Method (no peeking):
    For each of the last N months:
      TRAIN : run both styles on the PRIOR 2 months -> pick higher Sharpe
      TEST  : run BOTH styles on that unseen month -> score the choice

If the picker keeps choosing right, we earn a style-policy (e.g. allow bold
only when it's been winning lately). If it flips randomly, neither style has
stable edge and sizing must stay humble.

Usage:
    python backtest/walk_forward.py --ticker NVDA --months 6 \
        --capital 100 --fractional
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from backtest.hedging_backtester import run_comparison

STYLES = ("conservative", "bold")


def _run_style(ticker: str, start: str, end: str, capital: float,
               risk_pct: float, fractional: bool, style: str) -> dict:
    """Quiet single-style run returning the HEDGED book metrics."""
    try:
        r = run_comparison(ticker=ticker, period="1y", capital=capital,
                           risk_pct=risk_pct, start=start, end=end,
                           fractional=fractional, style=style, quiet=True)
        return {"sharpe": r["hedged"]["sharpe"],
                "final": r["hedged"]["final_equity"],
                "trades": r["hedged"]["num_trades"]}
    except SystemExit as e:
        return {"sharpe": 0.0, "final": capital, "trades": 0, "skipped": str(e)}
    except Exception as e:
        return {"sharpe": 0.0, "final": capital, "trades": 0, "error": str(e)}


def month_folds(months: int, train_months: int = 2,
                end: pd.Timestamp = None) -> list:
    """
    Builds rolling folds ending last full month:
        [(train_start, train_end, test_start, test_end), ...]
    """
    end = pd.Timestamp(end) if end is not None else pd.Timestamp.today().normalize()
    folds = []
    for k in range(int(months), 0, -1):
        test_start = (end - pd.DateOffset(months=k)).replace(day=1)
        test_end = test_start + pd.offsets.MonthEnd(0)
        train_start = (test_start - pd.DateOffset(months=train_months))
        train_end = test_start - pd.Timedelta(days=1)
        folds.append((str(train_start.date()), str(train_end.date()),
                      str(test_start.date()), str(test_end.date())))
    return folds


def walk_forward(ticker: str, months: int = 6, capital: float = 10_000.0,
                 risk_pct: float = 0.02, fractional: bool = False,
                 train_months: int = 2) -> dict:
    """Runs the rolling experiment; returns fold rows + policy summary."""
    rows = []
    print(f"\n=== WALK-FORWARD: {ticker} | {months} test months | "
          f"train={train_months}mo ===")

    for tr_s, tr_e, te_s, te_e in month_folds(months, train_months):
        train_sharpe = {}
        for st in STYLES:
            train_sharpe[st] = _run_style(ticker, tr_s, tr_e, capital,
                                          risk_pct, fractional, st)["sharpe"]
        picked = max(STYLES, key=lambda s: train_sharpe[s])
        other = [s for s in STYLES if s != picked][0]

        test = {}
        for st in STYLES:                       # score BOTH to judge honestly
            test[st] = _run_style(ticker, te_s, te_e, capital,
                                  risk_pct, fractional, st)

        correct = test[picked]["sharpe"] >= test[other]["sharpe"]
        row = {
            "test_month": te_e[:7],
            "picked": picked,
            "train_sharpes": {s: round(v, 2) for s, v in train_sharpe.items()},
            "test_sharpe_picked": round(test[picked]["sharpe"], 2),
            "test_sharpe_other": round(test[other]["sharpe"], 2),
            "correct": correct,
        }
        rows.append(row)
        mark = "✓" if correct else "✗"
        print(f"  {row['test_month']}  picked={picked:<12} "
              f"train={row['train_sharpes']}  ->  test "
              f"{row['test_sharpe_picked']} vs {row['test_sharpe_other']}  {mark}")

    return {"ticker": ticker.upper(), "folds": rows}


def _policy_summary(rows: list) -> None:
    if not rows:
        print("No folds evaluated.")
        return
    n = len(rows)
    correct = sum(1 for r in rows if r["correct"])
    bold_picked = sum(1 for r in rows if r["picked"] == "bold")
    recent = rows[-3:]
    recent_correct = sum(1 for r in recent if r["correct"])

    print(f"\n{'=' * 66}\n  WALK-FORWARD POLICY SUMMARY\n{'=' * 66}")
    print(f" Picker accuracy : {correct}/{n} ({100 * correct / n:.0f}%)")
    print(f" Bold picked     : {bold_picked}/{n} months")
    print(f" Recent-3 acc    : {recent_correct}/3")

    if n >= 4 and correct / n >= 0.67:
        dominant = "bold" if bold_picked > n / 2 else "conservative"
        print(f"\n SUGGESTION: picker is reliable ({100 * correct / n:.0f}%). "
              f"Default live STYLE may follow its latest pick "
              f"(last={rows[-1]['picked']}).")
        if dominant == "bold":
            print(" Consider ALLOWING bold live with the C risk budget.")
    else:
        print("\n SUGGESTION: picker unreliable (<67%). Run BOTH styles at "
              "half-risk each, or stay conservative until edge stabilises.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Walk-Forward Style Selector")
    parser.add_argument("--ticker", type=str, default="NVDA")
    parser.add_argument("--months", type=int, default=6,
                        help="Number of unseen test months (rolling)")
    parser.add_argument("--train-months", type=int, default=2)
    parser.add_argument("--capital", type=float, default=10_000.0)
    parser.add_argument("--risk-pct", type=float, default=0.02)
    parser.add_argument("--fractional", action="store_true")
    args = parser.parse_args()

    out = walk_forward(ticker=args.ticker, months=args.months,
                       capital=args.capital, risk_pct=args.risk_pct,
                       fractional=args.fractional,
                       train_months=args.train_months)
    _policy_summary(out["folds"])


if __name__ == "__main__":
    main()