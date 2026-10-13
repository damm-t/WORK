# api/schemas.py
from pydantic import BaseModel, Field

# --- Pydantic Models for Input Validation ---
class ExecuteRequest(BaseModel):
    # Enforces 1 to 5 alphabetical characters (e.g., AAPL, TSLA, F)
    ticker: str = Field(..., pattern=r"^[a-zA-Z]{1,5}$", description="The stock ticker symbol")

# --- Custom Domain Exceptions ---
class EngineException(Exception):
    """Base exception for the signal engine."""
    pass

class NoArticlesFoundError(EngineException):
    pass

class MarketDataNotFoundError(EngineException):
    pass

class NLPAnalysisError(EngineException):
    pass