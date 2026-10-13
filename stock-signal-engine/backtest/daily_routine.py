"""
Daily Routine Orchestrator
==========================
Professional desk rhythm in three scheduled phases (your local time MYT):

  ☀️  MORNING   `--mode morning`   (anytime before US close, ideal ~09:00)
      Scrape the WHOLE universe -> FinBERT every headline -> store to
      news_memory + daily briefing JSON -> warm price caches so evening
      cycles never hit Yahoo rate-limits.

  📊 OFF-HOURS  `--mode analyze`   (while US market is CLOSED)
      Journal analytics + walk-forward + regime + leaderboard -> compiles a
      PRE-MARKET PLAN (reports/plan_YYYY-MM-DD.md): tonight's watchlist,
      names to AVOID (earnings/negative-sentiment), and tiny env adjustments
      suggested by realised trades.

  🌙 NIGHT      ./scenario_c.sh     (21:30–04:00 MYT) executes the plan.

Schedule with cron (example):
    30 7 * * *  cd /path && .venv/bin/python backtest/daily_routine.py \
                --mode full >> logs/routine.log 2>&1
"""

import argparse
import contextlib
import io
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stability defaults BEFORE heavy imports (same rationale as autopilot)
os.environ.setdefault("USE_LGBM_RUNTIME", "0")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from ingestion import fetch_all                       # noqa: E402
from nlp import analyze_sentiment_only, pick_best_article   # noqa: E402
from nlp.news_memory import remember                  # noqa: E402
from backtest.universe import get_universe            # noqa: E402
from backtest.market_scanner import flat_universe, rank_market  # noqa: E402
from risk.hedging_engine import without_banned       # noqa: E402
from market.price_fetcher import fetch_prices         # noqa: E402
from market.shock_detector import earnings_blackout   # noqa: E402

DATA_DIR = Path("data/briefings")
PLAN_DIR = Path("reports")


def _briefing_path(day: str | None = None) -> Path:
    day = day or date.today().isoformat()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / f"briefing_{day}.json"


def _plan_path(day: str | None = None) -> Path:
    day = day or date.today().isoformat()
    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    return PLAN_DIR / f"plan_{day}.md"


# ------------------------------------------------------- ☀️ morning phase ---
def scrape_ticker(ticker: str, max_articles: int = 3) -> dict | None:
    """News -> FinBERT for ONE ticker; stores every analysed headline."""
    articles = fetch_all(ticker)[:max_articles]
    enriched = [a for a in
                (analyze_sentiment_only(x) for x in articles) if a]
    if not enriched:
        return None

    best = pick_best_article(enriched)
    labels = [str(a.get("sentiment", "")).lower() for a in enriched]
    scores = [float(a.get("sentiment_score", 0.0) or 0.0) for a in enriched]

    for a in enriched:                                 # feed the narrative DB
        try:
            remember(ticker, a.get("title", ""),
                     a.get("sentiment", "neutral"),
                     float(a.get("sentiment_score", 0.0) or 0.0))
        except Exception:                              # noqa: BLE001
            pass

    return {
        "ticker": ticker,
        "articles": len(enriched),
        "best_label": str(best.get("sentiment", "neutral")).lower(),
        "best_score": round(float(best.get("sentiment_score", 0.0) or 0.0), 4),
        "avg_score": round(sum(scores) / len(scores), 4),
        "pos": labels.count("positive"),
        "neg": labels.count("negative"),
        "headline": str(best.get("title", ""))[:120],
    }


def run_morning(universe_name: str = "core", limit: int | None = None,
                max_articles: int = 3, warm_cache: bool = True) -> dict:
    """Scrapes + analyses the universe; writes today's briefing JSON."""
    universe = get_universe(universe_name)
    flat = without_banned([t for ts in universe.values() for t in ts])
    if limit:
        flat = flat[:int(limit)]

    rows = []
    total = len(flat)
    print(f"=== ☀️  MORNING SCRAPE: {total} tickers "
          f"(universe={universe_name}) ===")

    done = 0
    for sector, tickers in universe.items():
        for t in tickers:
            if limit and done >= int(limit):
                break
            done += 1
            print(f"  [{done:>2}/{total}] {t:<6} ({sector})", flush=True)
            info = scrape_ticker(t, max_articles)
            if info:
                info["sector"] = sector
                rows.append(info)
            else:
                rows.append({"ticker": t, "sector": sector, "no_news": True})

            if warm_cache:                           # pre-warm evening cache
                try:
                    fetch_prices(t, period="1y", interval="1d")
                except Exception:                     # noqa: BLE001
                    pass

    live = [r for r in rows if r.get("best_label")]
    bullish = sorted([r for r in live if r["best_label"] == "positive"],
                     key=lambda r: -r["best_score"])[:5]
    bearish = sorted([r for r in live if r["best_label"] == "negative"],
                     key=lambda r: -r["best_score"])[:5]

    briefing = {
        "date": date.today().isoformat(),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "universe": universe_name,
        "scraped": len(rows),
        "with_news": len(live),
        "tickers": rows,
        "bullish_top": [r["ticker"] for r in bullish],
        "bearish_top": [r["ticker"] for r in bearish],
    }

    path = _briefing_path()
    path.write_text(json.dumps(briefing, indent=2))

    print(f"\nSaved briefing -> {path}")
    print(f"  with news : {len(live)}/{len(rows)}")
    print(f"  bullish   : {', '.join(briefing['bullish_top']) or '—'}")
    print(f"  bearish   : {', '.join(briefing['bearish_top']) or '—'}")
    return briefing


def load_today_briefing() -> dict | None:
    p = _briefing_path()
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:                                      # noqa: BLE001
        return None


# ------------------------------------------------- 📊 off-hours analysis ----
def run_analyze(briefing: dict | None = None, wf_ticker: str = "MSFT",
                months: int = 3, skip_wf: bool = False,
                top_n: int = 10) -> dict:
    """Journal analytics + regime + ranking -> compiles tonight's PLAN."""
    from execution.trade_journal import journal            # noqa: E402
    from market.beta_calculator import detect_market_regime  # noqa: E402

    print("\n=== 📊 OFF-HOURS ANALYSIS ===")

    analytics = journal.analytics()
    regime = detect_market_regime("SPY")

    from backtest.market_scanner import rank_market       # noqa: E402
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        ranked = rank_market(top_n=len(flat_universe()))
    score_of = {r["ticker"]: float(r["score"]) for r in ranked}

    sent_of = {}
    if briefing:
        for row in briefing.get("tickers", []):
            if row.get("best_label"):
                sent_of[row["ticker"]] = (row["best_label"],
                                          row["best_score"])

    avoid = []
    candidates = []
    for t in without_banned(flat_universe()):
        eb = earnings_blackout(t)
        if eb.get("blackout"):
            avoid.append(f"{t} (earnings {eb.get('next_earnings')})")
            continue
        label, conf = sent_of.get(t, ("neutral", 0.0))
        s = score_of.get(t, 0.0)
        if label == "negative" and conf >= 0.75:
            continue                                        # news-vetoed
        if s >= 55:
            candidates.append({"ticker": t, "score": s,
                               "sentiment": f"{label} {conf:.2f}"})
    candidates.sort(key=lambda c: -c["score"])
    watchlist = [c["ticker"] for c in candidates[:3]]

    # optional walk-forward evidence
    wf_line = "skipped"
    if not skip_wf:
        try:
            from backtest.walk_forward import walk_forward
            out = walk_forward(ticker=wf_ticker, months=months,
                               capital=100.0, fractional=True)
            folds = out["folds"]
            acc = sum(1 for f_ in folds if f_["correct"]) / max(len(folds), 1)
            last = folds[-1]["picked"] if folds else "n/a"
            wf_line = f"accuracy {acc * 100:.0f}% over {len(folds)}mo, last={last}"
        except Exception as e:                              # noqa: BLE001
            wf_line = f"error: {e}"

    plan_lines = [
        f"# Pre-Market Plan — {date.today().isoformat()}",
        "",
        f"- SPY regime      : **{regime.get('regime')}** "
        f"(hedge ×{regime.get('hedge_multiplier')})",
        f"- Walk-forward    : {wf_line}",
        f"- Watchlist       : **{', '.join(watchlist) or '—'}**",
        f"- Avoid today     : {', '.join(avoid) or '—'}",
        "",
        "## Candidate detail",
    ]
    for c in candidates[:top_n]:
        plan_lines.append(
            f"- **{c['ticker']}** score {c['score']} · sentiment "
            f"{c['sentiment']}")
    if analytics.get("suggestions"):
        plan_lines += ["", "## Tiny adjustments (from realised trades)"]
        plan_lines += [f"- {s}" for s in analytics["suggestions"]]
    if analytics.get("avg_slippage_bps") is not None:
        plan_lines.append(
            f"- Avg slippage    : {analytics['avg_slippage_bps']} bps")

    launch = ("./scenario_small.sh --interval 900 --watchlist "
              + (",".join(without_banned(watchlist)) or "MSFT"))
    plan_lines += ["", "## Launch tonight", "", "```bash", launch, "```"]

    plan_path = _plan_path()
    plan_path.write_text("\n".join(plan_lines))

    result = {"watchlist": watchlist, "avoid": avoid, "candidates": candidates,
              "plan_path": str(plan_path), "launch_cmd": launch,
              "analytics": analytics, "regime": regime}
    print(f"\nWatchlist tonight : {', '.join(watchlist) or '—'}")
    print(f"Avoid             : {', '.join(avoid) or '—'}")
    print(f"Suggestions       : "
          f"{len(analytics.get('suggestions') or [])} item(s)")
    print(f"Plan saved        -> {plan_path}")
    return result


# --------------------------------------------------------------------- CLI --
def main() -> None:
    parser = argparse.ArgumentParser(description="Daily Routine Orchestrator")
    parser.add_argument("--mode", choices=["morning", "analyze", "full"],
                        default="full")
    parser.add_argument("--universe", choices=["core", "wide"], default="core")
    parser.add_argument("--limit", type=int, default=None,
                        help="cap tickers processed (testing)")
    parser.add_argument("--max-articles", type=int, default=3)
    parser.add_argument("--no-warm-cache", action="store_true",
                        help="skip price-cache pre-warming in morning mode")
    parser.add_argument("--wf-ticker", type=str, default="MSFT")
    parser.add_argument("--wf-months", type=int, default=3)
    parser.add_argument("--skip-wf", action="store_true",
                        help="skip walk-forward in analyze phase")
    args = parser.parse_args()

    briefing = None
    if args.mode in ("morning", "full"):
        briefing = run_morning(universe_name=args.universe,
                               limit=args.limit,
                               max_articles=args.max_articles,
                               warm_cache=not args.no_warm_cache)

    if args.mode in ("analyze", "full"):
        if briefing is None and args.mode == "analyze":
            briefing = load_today_briefing()
            if briefing is None:
                print("[daily_routine] no briefing for today — running "
                      "analysis without sentiment context (run --mode "
                      "morning first for full context)")
        run_analyze(briefing=briefing, wf_ticker=args.wf_ticker,
                    months=args.wf_months, skip_wf=args.skip_wf)


if __name__ == "__main__":
    main()