from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader

from api.schemas import ExecuteRequest, EngineException, NoArticlesFoundError, MarketDataNotFoundError, NLPAnalysisError
from api import services
from config import get_settings

settings = get_settings()
API_KEY_HEADER = APIKeyHeader(name="X-API-KEY", auto_error=True)

app = FastAPI(title="Stock Signal Engine", version="2.1")

# --- Middleware: CORS for your Dashboard ---
allowed_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(',') if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security: API Key Validation ---
def validate_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    if api_key_header != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid Internal API Key")
    return api_key_header

# --- Global Exception Handlers ---
@app.exception_handler(NoArticlesFoundError)
@app.exception_handler(MarketDataNotFoundError)
@app.exception_handler(NLPAnalysisError)
async def domain_not_found_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=404, content={"error": type(exc).__name__, "message": str(exc)})

@app.exception_handler(EngineException)
async def engine_logic_handler(request: Request, exc: EngineException):
    return JSONResponse(status_code=400, content={"error": "LogicError", "message": str(exc)})

@app.exception_handler(Exception)
async def global_crash_handler(request: Request, exc: Exception):
    # Log the full stack trace here in a real production environment
    return JSONResponse(status_code=500, content={"error": "InternalServerError", "message": "An unexpected error occurred."})

# --- Endpoints ---

@app.post("/execute", dependencies=[Depends(validate_api_key)])
async def execute_endpoint(request: ExecuteRequest):
    return services.process_trade_execution(request.ticker)

@app.get("/signal/{ticker}")
async def signal_endpoint(ticker: str):
    normalized_ticker, signal, best, market, _ = services.get_processed_signal(ticker)
    
    # Logic extracted from services to keep main clean
    from risk import evaluate_trade
    from execution import client, get_portfolio_value, get_current_exposure
    
    portfolio_value = get_portfolio_value(client)
    exposure = get_current_exposure(client)
    current_price = float(market.get("Close", 0.0) or 0.0)
    
    decision = evaluate_trade(signal, current_price, portfolio_value, exposure)
    return {"ticker": normalized_ticker, "signal": signal, "decision": decision}

@app.get("/market/{ticker}")
async def market_endpoint(ticker: str):
    from market import get_market_features
    result = get_market_features(ticker.upper())
    if not result:
        raise MarketDataNotFoundError(f"No market data found for {ticker}")
    return result

@app.get("/sentiment/{ticker}")
async def sentiment_endpoint(ticker: str):
    _, _, _, _, enriched = services.get_processed_signal(ticker)
    return [
        {
            "source": a.get("source", ""),
            "title": a.get("title", ""),
            "sentiment": a.get("sentiment", "neutral"),
            "sentiment_score": a.get("sentiment_score", 0.0),
            "published_at": a.get("published_at", "")
        } for a in enriched
    ]

@app.get("/portfolio")
async def portfolio_endpoint():
    return services.get_portfolio_summary()

@app.get("/regime")
async def regime_endpoint(benchmark: str = "SPY"):
    """Market regime detection: BULL_MOMENTUM / CHOP_NEUTRAL / BEAR_VOLATILITY."""
    return services.get_regime(benchmark)

@app.get("/hedge/evaluate/{ticker}")
async def hedge_evaluate_endpoint(ticker: str):
    """Dry-run paired trade plan: signal + risk decision + beta hedge diagnostics."""
    return services.get_hedge_evaluation(ticker)

@app.post("/autopilot/run-once")
async def autopilot_run_once(request: ExecuteRequest):
    """Single autopilot cycle over the watchlist (position mgmt + scan)."""
    from execution.autopilot import run_autopilot
    run_autopilot(watchlist=[request.ticker.upper()], once=True, dry_run=False)
    return {"status": "cycle_complete", "ticker": request.ticker.upper()}

@app.get("/purchases")
async def purchases_endpoint(limit: int = 50):
    from execution.purchase_logger import get_purchase_logs, get_purchase_log_text
    return {
        "purchases": get_purchase_logs(limit=limit),
        "raw_text": get_purchase_log_text(),
    }

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.2-hedged", "model_runtime": settings.USE_LGBM_RUNTIME}