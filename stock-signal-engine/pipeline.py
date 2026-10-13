"""
Nightly Orchestrator — THE GLUE
===============================
Chains every feature into one flow:

  ① wide-sector scan            (scanner scores, warm caches)
  ② top confident candidates    (score >= --min-scan)
  ③ news deep-dive              (~3-month STACKING archive per name,
                                 FinBERT on new headlines only)
  ④ COMPOSITE SCORE             = 40% scanner + 35% sentiment + 25% technical
  ⑤ pre-market price & gap      (adverse gap => skip; momentum gap => note)
  ⑥ PRE-PLACED BRACKET ORDERS   limit entry + TP(+2xATR) + SL(2xATR) queued
                                BEFORE the open (--execute to arm live)

Phases:
    --phase brief    morning scrape+briefing (delegates to daily_routine)
    --phase night    the glue above (dry by default, --execute for real)

Usage:
    python pipeline.py --phase night --top 3 --min-scan 70
    python pipeline.py --phase night --top 3 --execute          # arms orders
"""

import argparse
import contextlib
import io
import json
import logging
import math
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

logger = logging.getLogger("pipeline")

# stability defaults before heavy imports
os.environ.setdefault("USE_LGBM_RUNTIME", "0")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from ingestion import fetch_all                       # noqa: E402
from nlp import analyze_sentiment_only                # noqa: E402
from nlp.news_memory import remember                  # noqa: E402
from backtest.universe import get_universe            # noqa: E402
from backtest.market_scanner import rank_market       # noqa: E402
from market.price_fetcher import fetch_prices         # noqa: E402
from market.shock_detector import earnings_blackout, fetch_prev_close  # noqa: E402
from execution.trade_journal import journal                           # noqa: E402

WEIGHTS = {"scanner": 0.40, "sentiment": 0.35, "technical": 0.25}
BOLD_STOP_ATR_MULT = 2.0
BOLD_TP_ATR_MULT = 2.0
ADVERSE_GAP_SKIP_PCT = -2.5        # skip longs gapping down harder than this


def _seen_titles() -> set:
    """Titles already stacked in the news archive (dedupe on ingest)."""
    p = Path("nlp/news_memory.db")
    if not p.exists():
        return set()
    conn = sqlite3.connect(p)
    try:
        rows = conn.execute("SELECT title FROM articles").fetchall()
    finally:
        conn.close()
    return {r[0] for r in rows}


# ------------------------------------------------- ③ news deep-dive ---------
def news_deep_dive(ticker: str, max_articles: int = 10,
                   store: bool = True) -> dict:
    """
    Stacks fresh coverage onto the ticker's persistent news archive and
    returns the aggregated conviction (0-100) + representative headline.
    The archive compounds every nightly run toward months of depth.
    """
    seen = _seen_titles()
    enriched, new_count = [], 0

    for a in fetch_all(ticker)[:max_articles]:
        title = str(a.get("title", "") or "")
        res = analyze_sentiment_only(a)
        if not res:
            continue
        label = str(res.get("sentiment", "neutral")).lower()
        score = float(res.get("sentiment_score", 0.0) or 0.0)
        enriched.append({"title": title, "label": label, "score": score,
                         "source": str(a.get("source", ""))})
        if store and title and title not in seen:
            try:
                remember(ticker, title, label, score)
                seen.add(title)
                new_count += 1
            except Exception:                              # noqa: BLE001
                pass

    if not enriched:
        return {"ticker": ticker, "n": 0, "conviction": 50.0,
                "label": "neutral", "best_score": 0.0,
                "headlines": [], "new_stored": 0}

    dir_map = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}
    total_w = 0.0
    weighted_dir_score = 0.0
    best_score = 0.0

    for i, a in enumerate(enriched):
        lbl = str(a.get("label", "neutral")).lower()
        sc = float(a.get("score", 0.0) or 0.0)
        direction = dir_map.get(lbl, 0.0)

        # Recency/rank decay weight (1.0 for first, 0.85 for 2nd, etc.)
        w = 0.85 ** i
        weighted_dir_score += direction * sc * w
        total_w += w

        if sc > best_score:
            best_score = sc

    agg_sentiment = (weighted_dir_score / total_w) if total_w > 0.0 else 0.0
    conviction = max(0.0, min(100.0, 50.0 + agg_sentiment * 60.0))

    if agg_sentiment > 0.10:
        dominant_label = "positive"
    elif agg_sentiment < -0.10:
        dominant_label = "negative"
    else:
        dominant_label = str(enriched[0].get("label", "neutral"))

    return {
        "ticker": ticker, "n": len(enriched),
        "conviction": round(conviction, 1),
        "label": dominant_label, "best_score": round(best_score, 4),
        "headlines": enriched[:5], "new_stored": new_count,
    }


# ------------------------------------------------- ⑤ pre-market snapshot ----
def premarket_snapshot(ticker: str) -> dict:
    prev_close = fetch_prev_close(ticker)
    pre_price = None
    try:
        import yfinance as yf                               # noqa: E402
        tk = yf.Ticker(ticker)
        info = getattr(tk, "info", None)
        if isinstance(info, dict):
            pre_price = info.get("preMarketPrice") or None
    except Exception as e:                                  # noqa: BLE001
        logger.debug(f"premarket info unavailable {ticker}: {e}")
        pre_price = None

    gap_pct = None
    if pre_price and prev_close:
        gap_pct = round((float(pre_price) / float(prev_close) - 1.0) * 100.0, 2)

    adverse = gap_pct is not None and gap_pct <= ADVERSE_GAP_SKIP_PCT
    return {"premarket": pre_price, "prev_close": prev_close,
            "gap_pct": gap_pct, "adverse_gap": bool(adverse)}


# ------------------------------------------------- ④ composite scoring ------
def composite_score(scanner_score: float, sentiment_conviction: float,
                    technical_score: float) -> float:
    return round(WEIGHTS["scanner"] * scanner_score
                 + WEIGHTS["sentiment"] * sentiment_conviction
                 + WEIGHTS["technical"] * technical_score, 1)


def build_candidate(ticker: str, scanner_row: dict, deep: dict,
                    market: dict, equity: float, risk_pct: float,
                    notional_pct: float) -> dict:
    """
    Assembles one candidate: composite score + pre-market gap guard +
    bracket-order plan (limit entry at pre-market/last, TP +2xATR,
    SL 2xATR, sized by risk budget then notional-capped).
    """
    from risk.trade_scorer import score_trade               # noqa: E402

    tech = score_trade(
        {"label": deep.get("label") or "neutral",
         "score": deep.get("best_score", 0.0)},
        market, {"regime": None})
    comp = composite_score(float(scanner_row.get("score", 0.0)),
                           float(deep.get("conviction", 50.0)),
                           float(tech.get("score", 0.0)))

    atr = float(market.get("ATR", 0.0) or 0.0)
    price_ref = float(deep.get("premarket") or market.get("Close") or 0.0)
    if atr <= 0 or price_ref <= 0:
        return {"ticker": ticker, "skip": "no ATR/price",
                "composite": comp, "tech_grade": tech["grade"]}

    stop_dist = BOLD_STOP_ATR_MULT * atr
    raw_qty = (equity * risk_pct) / stop_dist
    qty = int(raw_qty)

    max_notional = equity * notional_pct
    if qty > 0 and qty * price_ref > max_notional:
        qty = int(max_notional / price_ref)

    return {
        "ticker": ticker,
        "sector": scanner_row.get("sector"),
        "scanner_score": scanner_row.get("score"),
        "sentiment_conviction": deep.get("conviction"),
        "tech_score": tech.get("score"),
        "tech_grade": tech.get("grade"),
        "composite": comp,
        "price_ref": round(price_ref, 2),
        "premarket_gap_pct": deep.get("gap_pct"),
        "qty": int(qty),
        "tp": round(price_ref + BOLD_TP_ATR_MULT * atr, 2),
        "sl": round(price_ref - stop_dist, 2),
        "risk_dollars": round(int(qty) * stop_dist, 2),
        "notional": round(int(qty) * price_ref, 2),
        "headlines": deep.get("headlines", []),
        "order_ready": int(qty) > 0,
    }


# ------------------------------------------------- ⑥ NIGHT phase ------------
def phase_night(top: int = 3, min_scan: float = 70.0, capital: float = None,
                risk_pct: float = 0.10, notional_pct: float = 0.30,
                universe_name: str = "wide", max_articles: int = 10,
                execute: bool = False) -> list:
    uni_count = sum(len(v) for v in get_universe(universe_name).values())

    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        ranked = rank_market(top_n=uni_count, filter_junk=True, sector_cap=2)

    candidates_in = [r for r in ranked
                     if float(r.get("score", 0.0)) >= min_scan and r.get("passed_quality", True)][:top]
    if not candidates_in:
        print("[night] no candidates above scan threshold or passed quality — staying flat.")
        return []

    from execution import client as alpaca_client           # noqa: E402
    from execution.alpha_client import submit_bracket_buy   # noqa: E402
    from execution.trade_journal import journal             # noqa: E402
    from market import get_market_features                  # noqa: E402

    if capital is None:
        try:
            capital = float(alpaca_client.get_account().equity)
        except Exception as e:                              # noqa: BLE001
            print(f"[night] account read failed ({e}) — default $10k")
            capital = 10_000.0

    print(f"\n=== 🌙 NIGHT PIPELINE | universe={universe_name}({uni_count}) "
          f"| candidates={len(candidates_in)} | "
          f"mode={'EXECUTE' if execute else 'DRY'} ===")

    results, armed = [], []
    for row in candidates_in:
        t = str(row["ticker"]).upper()

        eb = earnings_blackout(t)
        if eb.get("blackout"):
            print(f"  {t}: SKIP earnings blackout ({eb.get('next_earnings')})")
            continue

        pm = premarket_snapshot(t)
        if pm["adverse_gap"]:
            print(f"  {t}: SKIP adverse pre-market gap {pm['gap_pct']}%")
            continue

        deep = news_deep_dive(t, max_articles=max_articles)
        market = get_market_features(t)
        if not market:
            print(f"  {t}: SKIP no market features")
            continue

        cand = build_candidate(t, row, {**deep, **pm}, market, capital,
                               risk_pct, notional_pct)
        cand["premarket"] = pm["premarket"]
        results.append(cand)

        ready = "READY" if cand["order_ready"] else "[qty<1 skip]"
        print(f"  {t}: composite {cand['composite']} "
              f"(scan {cand['scanner_score']} · sent "
              f"{cand['sentiment_conviction']} · tech {cand['tech_score']} "
              f"[{cand['tech_grade']}]) qty={cand['qty']} "
              f"TP {cand['tp']} SL {cand['sl']} {ready}")

    results.sort(key=lambda c: -float(c.get("composite", 0)))

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"night_{stamp}.json"
    out_file.write_text(json.dumps(results, indent=2, default=str))

    for cand in results:
        if not cand.get("order_ready"):
            continue
        if execute and alpaca_client is not None:
            order = submit_bracket_buy(alpaca_client, cand["ticker"],
                                       cand["qty"], cand["price_ref"],
                                       cand["tp"], cand["sl"], tif="day")
            cand["bracket"] = order
            armed.append(cand["ticker"])
            try:
                journal.record_open(cand["ticker"], qty=cand["qty"],
                                    entry=cand["price_ref"], hedge="AUTO bracket",
                                    grade="A" if cand["composite"] >= 70 else "B",
                                    style="bold_breakout_preplaced",
                                    score=cand["composite"],
                                    order_id=order["order_id"])
            except Exception as je:
                print(f"  [trade_journal] Warning: {je}")
            try:
                from execution.purchase_logger import log_purchase
                log_purchase(
                    ticker=cand["ticker"],
                    qty=cand["qty"],
                    price=cand["price_ref"],
                    order_id=order["order_id"],
                    order_type="BRACKET BUY (LIMIT)",
                    status="ARMED",
                    score=cand["composite"],
                    grade="A" if cand["composite"] >= 70 else "B",
                    why_custom={
                        "scanner": {
                            "threshold": 70.0,
                            "breakdown": [f"Nightly scan composite score: {cand['composite']:.1f}/100",
                                          "Setup: bold_breakout_preplaced"],
                        },
                        "exit_plan": {
                            "stop_loss": {"price": cand["sl"], "desc": "Pre-placed bracket stop loss"},
                            "take_profit_1": {"price": cand["tp"], "desc": "Pre-placed bracket take profit limit"},
                        },
                    },
                )
            except Exception as pe:
                print(f"  [purchase_logger] Warning: {pe}")
            print(f"  ✅ ARMED {cand['ticker']} bracket "
                  f"(id {str(order['order_id'])[:8]}…)")
        else:
            print(f"  [DRY] would arm {cand['ticker']} bracket")

    mode = "ARMED" if execute else "DRY-PLAN"
    print(f"\n[{mode}] done — saved -> {out_file}")
    return results


# ------------------------------------------------------------------ CLI -----
def main() -> None:
    parser = argparse.ArgumentParser(description="Nightly Orchestrator (GLUE)")
    parser.add_argument("--phase", choices=["brief", "night"], default="night")
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--min-scan", type=float, default=70.0)
    parser.add_argument("--capital", type=float, default=None,
                        help="default: live Alpaca equity")
    parser.add_argument("--risk-pct", type=float, default=0.10)
    parser.add_argument("--notional-pct", type=float, default=0.30)
    parser.add_argument("--universe", choices=["core", "wide"],
                        default="wide")
    parser.add_argument("--max-articles", type=int, default=10)
    parser.add_argument("--execute", action="store_true",
                        help="actually submit bracket orders (else dry)")
    args = parser.parse_args()

    if args.phase == "brief":
        from backtest.daily_routine import run_morning       # noqa: E402
        run_morning(universe_name=args.universe,
                    max_articles=args.max_articles)
    else:
        phase_night(top=args.top, min_scan=args.min_scan,
                    capital=args.capital, risk_pct=args.risk_pct,
                    notional_pct=args.notional_pct,
                    universe_name=args.universe,
                    max_articles=args.max_articles,
                    execute=args.execute)


if __name__ == "__main__":
    main()