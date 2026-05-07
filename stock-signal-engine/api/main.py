from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ingestion import fetch_all
from nlp       import analyze, analyze_sentiment_only
from market    import get_market_features
from features  import build_features
from model     import get_signal
from risk      import evaluate_trade
from execution import client, get_portfolio_value, get_current_exposure

class ExecuteRequest(BaseModel):
    ticker: str

app = FastAPI(title="Stock Signal Engine", version="1.0")

@app.post("/execute")
def execute_endpoint(request: ExecuteRequest):
    ticker = request.ticker.upper()
    try:
        # Re-run the pipeline to get decision (since no state is stored)
        articles = fetch_all(ticker)[:3]
        enriched = []
        for article in articles:
            analyzed_article = analyze_sentiment_only(article)
            if analyzed_article:
                enriched.append(analyzed_article)

        if not enriched:
            raise HTTPException(status_code=404, detail="No articles found")

        best = max(enriched, key=lambda article: article.get("sentiment_score", 0.0))
        market = get_market_features(ticker)
        if not market:
            raise HTTPException(status_code=404, detail="No market data")

        features = build_features(best, market)
        signal = get_signal(
            features,
            float(best.get("sentiment_score", 0.0) or 0.0),
            str(best.get("sentiment", "neutral"))
        )

        portfolio_value = get_portfolio_value(client)
        exposure        = get_current_exposure(client)
        current_price   = float(market.get("Close", 0.0) or 0.0)
        decision        = evaluate_trade(signal, current_price, portfolio_value, exposure)

        from execution import execute_trade
        result = execute_trade(decision, ticker)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/signal/{ticker}")
def signal_endpoint(ticker: str):
    try:
        normalized_ticker = ticker.upper()
        articles = fetch_all(normalized_ticker)[:3]
        enriched = []
        for article in articles:
            analyzed_article = analyze_sentiment_only(article)
            if analyzed_article:
                enriched.append(analyzed_article)

        if not enriched:
            raise HTTPException(status_code=404, detail="No articles found")

        best = max(enriched, key=lambda article: article.get("sentiment_score", 0.0))
        market = get_market_features(normalized_ticker)
        if not market:
            raise HTTPException(status_code=404, detail="No market data")

        features = build_features(best, market)
        signal = get_signal(
            features,
            float(best.get("sentiment_score", 0.0) or 0.0),
            str(best.get("sentiment", "neutral"))
        )

        portfolio_value = get_portfolio_value(client)
        exposure        = get_current_exposure(client)
        current_price   = float(market.get("Close", 0.0) or 0.0)
        decision        = evaluate_trade(signal, current_price, portfolio_value, exposure)

        return {"ticker": normalized_ticker, "signal": signal, "decision": decision}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market/{ticker}")
def market_endpoint(ticker: str):
    try:
        result = get_market_features(ticker.upper())
        if not result:
            raise HTTPException(status_code=404, detail="No market data")

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sentiment/{ticker}")
def sentiment_endpoint(ticker: str):
    try:
        normalized_ticker = ticker.upper()
        articles = fetch_all(normalized_ticker)
        enriched = []
        for article in articles:
            analyzed_article = analyze_sentiment_only(article)
            if analyzed_article:
                enriched.append(analyzed_article)

        if not enriched:
            raise HTTPException(status_code=404, detail="No articles found")

        return [
            {
                "source": article.get("source", ""),
                "title": article.get("title", ""),
                "sentiment": article.get("sentiment", "neutral"),
                "sentiment_score": article.get("sentiment_score", 0.0),
                "published_at": article.get("published_at", "")
            }
            for article in enriched
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
