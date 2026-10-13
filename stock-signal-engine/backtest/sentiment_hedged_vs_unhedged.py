"""
Sentiment-Driven Hedged vs Unhedged Comparator
==============================================
Runs the LIVE pipeline end-to-end on real news:

    [RSS News] -> [FinBERT sentiment + confidence] -> [Ensemble signal]
        -> [Confidence-scaled ATR position] -> TWO parallel books:

    Book A (UNHEDGED): Long alpha only
    Book B (HEDGED):   Long alpha + inverse-ETF leg sized
                       Beta x RegimeMultiplier x LongValue

Then stress-tests BOTH books across market-shock scenarios using the asset's
live beta, so you can see exactly how the FinBERT confidence score changes
position size, and how much the hedge protects under each shock.

Usage:
    python backtest/sentiment_hedged_vs_unhedged.py --tickers NVDA,AAPL,TSLA --capital 10000
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ingestion            import fetch_all
from nlp                  import analyze_sentiment_only, pick_best_article
from market               import get_market_features
from features             import build_features
from model                import get_signal
from risk                 import evaluate_trade, calculate_hedge_pair, calculate_exit_levels


# ------------------------------------------------------------- pipeline ----
def run_signal_pipeline(ticker: str, max_articles: int = 3) -> dict:
    """News -> FinBERT -> technicals -> ensemble signal. No orders placed."""
    t = ticker.upper().strip()
    articles = fetch_all(t)[:max_articles]
    if not articles:
        return {"ticker": t, "error": f"No recent articles found for {t}"}

    enriched = [a for a in (analyze_sentiment_only(x) for x in articles) if a]
    if not enriched:
        return {"ticker": t, "error": f"FinBERT failed on all articles for {t}"}

    best = pick_best_article(enriched)
    market = get_market_features(t)
    if not market or not market.get("Close"):
        return {"ticker": t, "error": f"No market data for {t}", "news": enriched}

    price = float(market.get("Close"))
    atr = float(market.get("ATR", 0.0) or 0.0)
    features = build_features(best, market)

    signal = get_signal(
        feature_vector=features,
        sentiment_score=float(best.get("sentiment_score", 0.0)),
        sentiment=str(best.get("sentiment", "neutral")),
        current_price=price,
        atr=atr,
    )
    return {
        "ticker": t, "price": price, "atr": atr,
        "best_article": {"title": best.get("title"), "source": best.get("source"),
                         "sentiment": best.get("sentiment"),
                         "confidence": float(best.get("sentiment_score", 0.0))},
        "articles": [{"title": a.get("title"), "sentiment": a.get("sentiment"),
                      "confidence": a.get("sentiment_score")} for a in enriched],
        "signal": signal,
    }


def build_books(pipeline: dict, capital: float, benchmark: str = "SPY") -> dict:
    """Turns the signal into the two competing books (unhedged vs hedged)."""
    sig_action = str(pipeline["signal"].get("action", "HOLD")).upper()
    confidence = float(pipeline["signal"].get("confidence", 0.0) or 0.0)
    out = {"action": sig_action, "ensemble_confidence": round(confidence, 4)}

    if sig_action != "BUY":
        out.update({"unhedged": None, "hedged": None,
                    "reason": pipeline["signal"].get("reason", "No BUY signal")})
        return out

    price, atr = pipeline["price"], pipeline["atr"]

    # Book A: unhedged long
    unhedged = evaluate_trade(
        signal=pipeline["signal"], current_price=price,
        portfolio_value=capital, current_exposure=0.0, atr=atr,
    )

    # Book B: identical long + paired inverse-ETF hedge
    hedged = dict(unhedged)
    hedge, exit_levels = None, None
    if unhedged.get("approved"):
        hedge = calculate_hedge_pair(pipeline["ticker"],
                                     float(unhedged.get("position_value", 0.0)))
        if atr > 0:
            exit_levels = calculate_exit_levels(price, atr)
    out.update({"unhedged": unhedged, "hedged_long_leg": hedged,
                "hedge": hedge, "exit_levels": exit_levels})
    return out


# --------------------------------------------------------- stress testing --
SHOCKS_PCT = [-0.05, -0.03, -0.01, 0.0, 0.01, 0.03]   # SPY shock scenarios


def stress_test(pipeline: dict, books: dict) -> list:
    """
    Projects P&L for both books under SPY shocks using live beta.
      Unhedged P&L = long_value x beta x shock
      Hedged    P&L = long_value x beta x shock + hedge_value x (-shock)
                      (SH/PSQ move ~ -1x the index)
    Also includes a sentiment-alpha scenario: the stock moves WITH the news
    (confidence-scaled) while the market stays flat -> both books capture it,
    proving the hedge does not eat idiosyncratic alpha.
    """
    if not books.get("unhedged") or not books["unhedged"].get("approved"):
        return []

    long_value = float(books["unhedged"]["position_value"])
    beta = float((books.get("hedge") or {}).get("asset_beta", 1.0))
    hedge_value = float((books.get("hedge") or {}).get("hedge_dollars", 0.0))
    conf = float(pipeline["best_article"]["confidence"])

    rows = []
    for s in SHOCKS_PCT:
        stock_move = beta * s                       # systematic component
        pnl_unhedged = long_value * stock_move
        pnl_hedged = pnl_unhedged - hedge_value * s # hedge gains when market falls
        rows.append({
            "scenario": f"SPY {s:+.0%}, stock follows beta",
            "unhedged_pnl": round(pnl_unhedged, 2),
            "hedged_pnl": round(pnl_hedged, 2),
            "protection": round(pnl_hedged - pnl_unhedged, 2),
        })
    # Idiosyncratic alpha scenario: news plays out, market flat.
    # Stock drifts ~ confidence x 1 ATR upward over a few sessions.
    alpha_move = float(pipeline["atr"]) * conf
    rows.append({
        "scenario": f"News alpha plays out (+{alpha_move:.2f}/sh), SPY flat",
        "unhedged_pnl": round(long_value / pipeline["price"] * alpha_move, 2),
        "hedged_pnl": round(long_value / pipeline["price"] * alpha_move, 2),
        "protection": 0.0,
    })
    return rows


# --------------------------------------------------------------- reporting -
def print_comparison(pipeline: dict, books: dict, stress: list) -> None:
    t = pipeline["ticker"]
    print(f"\n{'=' * 74}\n  {t}  |  price ${pipeline['price']:.2f}  |  "
          f"ATR {pipeline['atr']:.2f}\n{'=' * 74}")

    best = pipeline["best_article"]
    print(f"\n[NEWS] \"{best['title']}\"")
    print(f"       source={best['source']}  ->  FinBERT: "
          f"{best['sentiment'].upper()}  confidence={best['confidence']:.4f}")
    for a in pipeline["articles"][1:]:
        print(f"       also: [{a['sentiment']} {a['confidence']:.2f}] {a['title'][:70]}")

    sig = pipeline["signal"]
    print(f"\n[SIGNAL] action={sig.get('action')}  ensemble_confidence="
          f"{sig.get('confidence')}  \n         reason: {sig.get('reason', '')}")

    unh = books.get("unhedged")
    if not unh or not unh.get("approved"):
        reason = (books.get("reason")
                  or (unh or {}).get("reason")
                  or "risk gate rejected the trade")
        print(f"\n[BOOKS] No position taken: {reason}")
        return

    hedge = books.get("hedge") or {}
    ex = books.get("exit_levels") or {}
    hdr = f"{'':<26}{'UNHEDGED':>22}{'HEDGED':>24}"
    print(f"\n{hdr}\n{'-' * len(hdr)}")
    print(f"{'Long shares':<26}{unh['shares']:>22}{unh['shares']:>24}")
    print(f"{'Long value ($)':<26}{unh['position_value']:>22,.2f}"
          f"{unh['position_value']:>24,.2f}")
    print(f"{'Hard stop ($)':<26}{unh['stop_loss_price']:>22,.2f}"
          f"{ex.get('hard_stop_price', 0):>24,.2f}")

    hedge_leg = "{} x{} (${:,.0f})".format(hedge.get("hedge_instrument", "—"),
                                           hedge.get("hedge_shares", 0),
                                           hedge.get("hedge_dollars", 0.0))
    tp_row = "{} / {}".format(ex.get("take_profit_1_price", "—"),
                              ex.get("take_profit_2_trigger", "—"))
    net_beta_unhedged = unh['position_value'] * float(hedge.get('asset_beta', 1.0))

    print(f"{'Hedge leg ($)':<26}{'—':>22}{hedge_leg:>24}")
    print(f"{'Net beta exposure':<26}{net_beta_unhedged:>22,.2f}"
          f"{hedge.get('net_beta_exposure', 0):>24,.2f}")
    if ex:
        print(f"{'TP1 / runner trigger':<26}{'—':>22}{tp_row:>24}")
    print(f"\n[HEDGE RATIONALE] {hedge.get('reason', 'n/a')}")

    if stress:
        print(f"\n{'Scenario':<46}{'Unhedged P&L':>14}{'Hedged P&L':>14}{'Protected':>12}")
        print("-" * 88)
        for r in stress:
            print(f"{r['scenario']:<46}{r['unhedged_pnl']:>14,.2f}"
                  f"{r['hedged_pnl']:>14,.2f}{r['protection']:>12,.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="News-driven FinBERT signal: hedged vs unhedged comparison")
    parser.add_argument("--tickers", type=str, default="NVDA,AAPL,TSLA")
    parser.add_argument("--capital", type=float, default=10000.0)
    parser.add_argument("--benchmark", type=str, default="SPY")
    parser.add_argument("--force-buy", action="store_true",
                        help="Demo mode: override HOLD -> BUY so the paired-hedge "
                             "mechanics can be compared even when news is bearish")
    args = parser.parse_args()

    for ticker in [t.strip().upper() for t in args.tickers.split(",") if t.strip()]:
        try:
            pipeline = run_signal_pipeline(ticker)
            if pipeline.get("error"):
                print(f"\n[{ticker}] SKIPPED: {pipeline['error']}")
                continue

            if args.force_buy and str(pipeline["signal"].get("action")) != "BUY":
                forced = max(0.60, abs(float(pipeline["signal"].get("confidence", 0.0) or 0.0)))
                pipeline["signal"]["action"] = "BUY"
                pipeline["signal"]["confidence"] = round(forced, 4)
                pipeline["signal"]["reason"] += "  [FORCED-BUY DEMO]"

            books = build_books(pipeline, args.capital, args.benchmark)
            stress = stress_test(pipeline, books)
            print_comparison(pipeline, books, stress)
        except Exception as e:
            print(f"\n[{ticker}] ERROR: {e}")


if __name__ == "__main__":
    main()