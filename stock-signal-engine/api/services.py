# api/services.py
import logging
import os

from ingestion import fetch_all
from nlp       import analyze_sentiment_only, pick_best_article
from market    import get_market_features
from features  import build_features
from model     import get_signal
from risk      import (banned_ticker, evaluate_trade, calculate_hedge_pair,
                       calculate_exit_levels)
from risk.trade_scorer import score_trade
from execution import client, get_portfolio_value, get_current_exposure, execute_trade, execute_hedged_trade
from api.schemas import NoArticlesFoundError, MarketDataNotFoundError, NLPAnalysisError

logger = logging.getLogger(__name__)

def get_processed_signal(ticker: str):
    """
    Core pipeline logic shared across multiple endpoints.
    Fetches articles, processes NLP, gets market data, and calculates the signal.
    """
    normalized_ticker = ticker.upper()
    
    # 1. Fetch & Filter
    articles = fetch_all(normalized_ticker)[:3]
    if not articles:
        raise NoArticlesFoundError(f"No recent articles found for {normalized_ticker}.")

    # 2. NLP Processing
    enriched = [
        analyzed for article in articles 
        if (analyzed := analyze_sentiment_only(article)) is not None
    ]
    
    if not enriched:
        raise NLPAnalysisError(f"NLP processing failed for {normalized_ticker}.")

    # 3. Market Data & Features
    # Directional pick (not raw-score max): FinBERT confidence runs high for
    # BOTH bullish and bearish headlines, so raw max() let one strongly
    # negative article hijack the signal and force HOLD -> "No signal".
    best = pick_best_article(enriched)
    market = get_market_features(normalized_ticker)
    
    if not market:
        raise MarketDataNotFoundError(f"Could not retrieve market data for {normalized_ticker}.")

    # 4. Build Features
    features = build_features(best, market)
    
    # 5. GET SIGNAL
    # We carefully extract the exact variables we need from the 'best' article and 'market' data
    signal = get_signal(
        feature_vector=features,                               # Passes the features dict
        sentiment_score=float(best.get("sentiment_score", 0.0)), # Pulls score from 'best'
        sentiment=str(best.get("sentiment", "neutral")),         # Pulls sentiment from 'best'
        current_price=float(market.get("Close", 0.0) or 0.0),    # Pulls Close from 'market'
        atr=float(market.get("ATR", 0.0) or 0.0)                 # Pulls ATR from 'market'
    )

    return normalized_ticker, signal, best, market, enriched
    
def process_trade_execution(ticker: str, include_hedge: bool = True):
    """Handles the execution pipeline including risk evaluation."""
    normalized_ticker, signal, best, market, _ = get_processed_signal(ticker)
    
    from risk.book_allocator import get_book_allocations
    alloc = get_book_allocations(client=client)
    portfolio_value = alloc["core"]["budget"]
    exposure        = alloc["core"]["market_value"]
    
    current_price   = float(market.get("Close", 0.0) or 0.0)
    current_atr     = market.get("ATR")
    
    # TRADE QUALITY GRADE: composite of news conviction, trend, momentum,
    # RSI zone and volatility sanity. Grade C (<55) = skip entirely,
    # B = 60% size, A = full size.
    grade = score_trade(
        {"label": best.get("sentiment"), "score": best.get("sentiment_score")},
        market,
    )
    min_score = float(os.getenv("MIN_TRADE_SCORE", "55"))
    if banned_ticker(normalized_ticker):
        return {
            "ticker": normalized_ticker,
            "execution": {"status": "skipped"},
            "decision": {"approved": False,
                         "reason": "Banned symbol (tuned small-account preset)",
                         "trade_grade": grade},
            "hedge": None,
            "trade_grade": grade
        }
    strict_trend = os.getenv("REQUIRE_SMA50_ABOVE_SMA200", "0") == "1"
    strict_rsi = os.getenv("TUNED_RSI_MAX", "")
    if strict_trend:
        sma50 = market.get("SMA50")
        sma200 = market.get("SMA200")
        if (sma50 is not None and sma200 is not None
                and float(sma50) <= float(sma200)):
            return {
                "ticker": normalized_ticker,
                "execution": {"status": "skipped"},
                "decision": {"approved": False,
                             "reason": "SMA50 below SMA200 (tuned trend filter)",
                             "trade_grade": grade},
                "hedge": None,
                "trade_grade": grade
            }
    if strict_rsi:
        try:
            rsi_cap = float(strict_rsi)
            rsi_now = float(market.get("RSI", 50.0) or 50.0)
            if not (35.0 <= rsi_now <= rsi_cap):
                return {
                    "ticker": normalized_ticker,
                    "execution": {"status": "skipped"},
                    "decision": {"approved": False,
                                 "reason": f"RSI {rsi_now:.1f} outside 35-{rsi_cap:.0f}",
                                 "trade_grade": grade},
                    "hedge": None,
                    "trade_grade": grade
                }
        except (TypeError, ValueError):
            pass
    if float(grade.get("score", 0.0) or 0.0) < min_score:
        return {
            "ticker": normalized_ticker,
            "execution": {"status": "skipped"},
            "decision": {"approved": False,
                         "reason": f"Low trade score {float(grade.get('score', 0.0)):.0f} "
                                   f"(grade {grade.get('grade')}, need {min_score:.0f})",
                         "trade_grade": grade},
            "hedge": None,
            "trade_grade": grade
        }
    if grade["size_multiplier"] < 1.0:
        signal["confidence"] = round(
            float(signal.get("confidence", 0.0) or 0.0) * grade["size_multiplier"], 4)

    # Extract Anti-Volatility and Bayesian conviction if available
    _psi = None
    _regime = None
    _conf = None
    try:
        from market.anti_volatility import anti_volatility_model
        _stab = anti_volatility_model.evaluate_ticker(normalized_ticker)
        _psi = _stab.price_stability_index
        _regime = _stab.regime
    except Exception:
        pass
    try:
        from model.bayesian_confidence import belief_engine
        _stmt = belief_engine.get_latest_statement(normalized_ticker)
        if _stmt:
            _conf = _stmt.confidence_pointer
    except Exception:
        pass

    # RISK EVALUATION (Regime-adaptive sizing + ATR stop-loss logic)
    decision = evaluate_trade(
        signal=signal, 
        current_price=current_price, 
        portfolio_value=portfolio_value, 
        current_exposure=exposure,
        atr=current_atr,
        psi=_psi,
        regime=_regime,
        bayesian_confidence=_conf,
    )

    # PAIRED EXECUTION: Long alpha leg + dynamically sized inverse-ETF hedge leg
    hedge = None
    if decision.get("approved") and include_hedge and current_atr:
        hedge = calculate_hedge_pair(
            normalized_ticker,
            float(decision.get("position_value", 0.0) or 0.0),
            psi=_psi,
            bayesian_confidence=_conf,
        )
        decision["exit_levels"] = calculate_exit_levels(
            current_price, current_atr, psi=_psi, regime=_regime
        )
        result = execute_hedged_trade(decision, normalized_ticker, hedge)
    else:
        result = execute_trade(decision, normalized_ticker)

    if result.get("status") == "submitted":
        try:
            from execution.purchase_logger import log_purchase
            log_purchase(
                ticker=normalized_ticker,
                qty=int(decision.get("shares", 0) or 0),
                price=current_price,
                order_id=result.get("buy_id") or result.get("order_id"),
                order_type="MARKET BUY",
                status="SUBMITTED",
                portfolio_equity=portfolio_value,
                decision=decision,
                market=market,
                sentiment=best,
                trade_grade=grade,
                hedge=hedge,
                exit_levels=decision.get("exit_levels"),
            )
        except Exception as log_err:
            print(f"[services] Purchase logging warning: {log_err}")

    return {
        "ticker": normalized_ticker,
        "execution": result,
        "decision": decision,
        "hedge": hedge,
        "trade_grade": grade,
        "market": market,
        "sentiment": best,
    }

def get_portfolio_summary():
    """Fetches current Alpaca portfolio metrics."""
    portfolio_value = get_portfolio_value(client)
    exposure        = get_current_exposure(client)
    
    return {
        "portfolio_value": round(portfolio_value, 2),
        "current_exposure": round(exposure, 2),
        "available": round(portfolio_value - exposure, 2)
    }

def get_hedge_evaluation(ticker: str):
    """
    Dry-run of a PAIRED trade: signal -> risk decision -> beta hedge plan
    and exit ladder, WITHOUT placing any orders. Powers /hedge/evaluate
    and the autopilot's scan phase.
    """
    normalized_ticker, signal, best, market, _ = get_processed_signal(ticker)

    current_price = float(market.get("Close", 0.0) or 0.0)
    current_atr   = float(market.get("ATR", 0.0) or 0.0)
    from risk.book_allocator import get_book_allocations
    alloc = get_book_allocations(client=client)
    portfolio_value = alloc["core"]["budget"]
    exposure        = alloc["core"]["market_value"]

    # Anti-Volatility and Bayesian metrics for sizing, exit levels & hedge sizing
    _psi = None
    _regime = None
    _conf = None
    try:
        from market.anti_volatility import anti_volatility_model
        _stab = anti_volatility_model.evaluate_ticker(normalized_ticker)
        _psi = _stab.price_stability_index
        _regime = _stab.regime
    except Exception:
        pass
    try:
        from model.bayesian_confidence import belief_engine
        _stmt = belief_engine.get_latest_statement(normalized_ticker)
        if _stmt:
            _conf = _stmt.confidence_pointer
    except Exception:
        pass

    decision = evaluate_trade(
        signal=signal,
        current_price=current_price,
        portfolio_value=portfolio_value,
        current_exposure=exposure,
        atr=current_atr,
        psi=_psi,
        regime=_regime,
        bayesian_confidence=_conf,
    )

    hedge = None
    if decision.get("approved"):
        hedge = calculate_hedge_pair(
            normalized_ticker,
            float(decision.get("position_value", 0.0) or 0.0),
            psi=_psi,
            bayesian_confidence=_conf,
        )
        if current_atr > 0:
            decision["exit_levels"] = calculate_exit_levels(
                current_price, current_atr, psi=_psi, regime=_regime
            )

    grade = score_trade(
        {"label": best.get("sentiment"), "score": best.get("sentiment_score")},
        market,
        hedge or None
    )

    return {
        "ticker": normalized_ticker,
        "signal": signal,
        "sentiment": {
            "label": best.get("sentiment"),
            "score": best.get("sentiment_score"),
            "raw_score": best.get("raw_sentiment_score"),
            "decay_weight": best.get("decay_weight"),
            "age_hours": best.get("age_hours"),
        },
        "best_article": {
            "title": best.get("title"),
            "source": best.get("source"),
            "url": best.get("url"),
            "published_at": best.get("published_at"),
            "decay_weight": best.get("decay_weight"),
            "age_hours": best.get("age_hours"),
            "raw_sentiment_score": best.get("raw_sentiment_score"),
        },
        "market": {"close": current_price, "atr": current_atr},
        "decision": decision,
        "hedge": hedge,
        "trade_grade": grade
    }

def get_regime(benchmark: str = "SPY"):
    """Exposes market-regime diagnostics (BULL_MOMENTUM / CHOP_NEUTRAL / BEAR_VOLATILITY)."""
    from market.beta_calculator import detect_market_regime

    info = detect_market_regime(benchmark.upper().strip())
    if info.get("status") == "error":
        raise MarketDataNotFoundError(f"Could not detect regime for {benchmark}: "
                                      f"{info.get('description', 'unknown error')}")
    return info