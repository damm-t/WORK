from fastapi import FastAPI, HTTPException
from ingestion import fetch_all
from nlp       import analyze
from market    import get_market_features
from features  import build_features
from model     import get_signal
from risk      import evaluate_trade
from execution import get_client, get_portfolio_value, get_current_exposure

app = FastAPI(title="Stock Signal Engine", version="1.0")

client = get_client()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/signal/{ticker}")
def signal_endpoint(ticker: str):
    try:
        articles = fetch_all(ticker.upper())
        enriched = [analyze(a) for a in articles]
        if not enriched:
            raise HTTPException(status_code=404, detail="No articles found")

        best          = max(enriched, key=lambda x: x.get("sentiment_score", 0))
        market        = get_market_features(ticker.upper())
        features      = build_features(best, market)
        signal        = get_signal(features, best["sentiment_score"], best["sentiment"])

        portfolio_value = get_portfolio_value(client)
        exposure        = get_current_exposure(client)
        current_price   = market.get("Close", 0.0)
        decision        = evaluate_trade(signal, current_price, portfolio_value, exposure)

        return {"ticker": ticker, "signal": signal, "decision": decision}

    except HTTPException:
        raise              # re-raise 404s — don't swallow them as 500
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market/{ticker}")
def market_endpoint(ticker: str):
    try:
        result = get_market_features(ticker.upper())

        if not result:                                    # ✅ empty dict is falsy
            raise HTTPException(status_code=404, detail="No market data")

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sentiment/{ticker}")
def sentiment_endpoint(ticker: str):
    try:
        articles = fetch_all(ticker.upper())             # fetch raw articles
        enriched = [analyze(a) for a in articles]        # run NLP on each

        if not enriched:
            raise HTTPException(status_code=404, detail="No articles found")

        # return only relevant keys — dict comprehension
        # like LINQ Select() in C#
        return [
            {k: a[k] for k in ["source", "title", "sentiment",
                                "sentiment_score", "published_at"]}
            for a in enriched
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio")
def portfolio_endpoint():
    try:
        portfolio_value = get_portfolio_value(client)
        exposure        = get_current_exposure(client)

        return {
            "portfolio_value":    round(portfolio_value, 2),
            "current_exposure":   round(exposure, 2),
            "available":          round(portfolio_value - exposure, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))