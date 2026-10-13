import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Keys & Secrets
    APCA_API_KEY_ID: str
    APCA_API_SECRET_KEY: str
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"
    
    TWITTER_BEARER_TOKEN: str = "optional_default"
    SEC_USER_AGENT: str
    
    # Engine Settings
    USE_LGBM_RUNTIME: bool = True
    INTERNAL_API_KEY: str  # For protecting your endpoints
    CORS_ORIGINS: str = 'http://localhost:3000'
    DASHBOARD_PIN: str = "8888"  # 4-digit PIN for remote mobile dashboard access

    # Risk Management Defaults
    DEFAULT_MAX_RISK_PCT: float = 0.02
    DEFAULT_MAX_HEAT: float = 0.20

    # 95/5 Capital Architecture Split
    CORE_CAPITAL_PCT: float = 0.95
    MOMENTUM_CAPITAL_PCT: float = 0.05
    MOMENTUM_MAX_TRADE_RISK: float = 50.0

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()