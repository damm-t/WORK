import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

logging.getLogger("yfinance").setLevel(logging.CRITICAL)

try:
    import yfinance as yf
except Exception:
    yf = None

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "*/*",
}
SESSION = requests.Session()
SESSION.headers.update(YAHOO_HEADERS)
CACHE_DIR = Path("market/cache")


def fetch_prices(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    try:
        df = _fetch_with_yahoo_chart(ticker, period, interval)
        if not df.empty:
            _save_cache(ticker, period, interval, df)
            return df

        df = _fetch_with_yfinance(ticker, period, interval)
        if not df.empty:
            _save_cache(ticker, period, interval, df)
            return df

        df = _load_cache(ticker, period, interval)
        if df.empty:
            return pd.DataFrame()

        return df
    except Exception as e:
        return pd.DataFrame()


def _fetch_with_yfinance(ticker: str, period: str, interval: str) -> pd.DataFrame:
    try:
        if yf is None:
            return pd.DataFrame()

        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def _fetch_with_yahoo_chart(ticker: str, period: str, interval: str) -> pd.DataFrame:
    try:
        url = YAHOO_CHART_URL.format(ticker=ticker)
        import re, time
        now_ts = int(time.time())
        query_params = {"interval": interval}
        m = re.match(r"^(\d+)(y|mo|d)$", str(period).strip().lower())
        if m:
            val, unit = int(m.group(1)), m.group(2)
            if unit == "y":
                delta_sec = int(val * 365.25 * 86400)
            elif unit == "mo":
                delta_sec = int(val * 30.5 * 86400)
            else:
                delta_sec = int(val * 86400)
            query_params["period1"] = now_ts - delta_sec
            query_params["period2"] = now_ts
        else:
            query_params["range"] = period

        response = SESSION.get(
            url,
            params=query_params,
            timeout=15
        )
        if response.status_code != 200:
            return pd.DataFrame()

        data = response.json()
        result = (data.get("chart", {}).get("result") or [{}])[0]
        timestamps = result.get("timestamp", [])
        quote = (result.get("indicators", {}).get("quote") or [{}])[0]
        adjclose_data = (result.get("indicators", {}).get("adjclose") or [{}])[0]

        if not timestamps or not quote:
            return pd.DataFrame()

        df = pd.DataFrame(
            {
                "Open": quote.get("open", []),
                "High": quote.get("high", []),
                "Low": quote.get("low", []),
                "Close": quote.get("close", []),
                "Adj Close": adjclose_data.get("adjclose", quote.get("close", [])),
                "Volume": quote.get("volume", []),
            },
            index=pd.to_datetime(timestamps, unit="s", utc=True)
        )
        df.dropna(inplace=True)
        return df if not df.empty else pd.DataFrame()
    except Exception as e:
        print(f"[price_fetcher] Error: {e}")
        return pd.DataFrame()


def _save_cache(ticker: str, period: str, interval: str, df: pd.DataFrame) -> None:
    try:
        if df.empty:
            return None

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path = _get_cache_path(ticker, period, interval)
        df.to_csv(cache_path)
        return None
    except Exception as e:
        print(f"[price_fetcher] Error: {e}")
        return None


def _load_cache(ticker: str, period: str, interval: str) -> pd.DataFrame:
    try:
        cache_path = _get_cache_path(ticker, period, interval)
        if not cache_path.exists():
            return pd.DataFrame()

        return pd.read_csv(cache_path, index_col=0, parse_dates=True)
    except Exception as e:
        print(f"[price_fetcher] Error: {e}")
        return pd.DataFrame()


def _get_cache_path(ticker: str, period: str, interval: str) -> Path:
    try:
        safe_ticker = str(ticker).upper()
        return CACHE_DIR / f"{safe_ticker}_{period}_{interval}.csv"
    except Exception as e:
        print(f"[price_fetcher] Error: {e}")
        return Path("market/cache/invalid.csv")


def fetch_latest_price(ticker: str) -> Optional[float]:
    """Retrieves the latest available traded price or close for a ticker."""
    try:
        df = fetch_prices(ticker, period="1d", interval="1m")
        if df is not None and not df.empty and "Close" in df.columns:
            return float(df["Close"].iloc[-1])
        df_daily = fetch_prices(ticker, period="5d", interval="1d")
        if df_daily is not None and not df_daily.empty and "Close" in df_daily.columns:
            return float(df_daily["Close"].iloc[-1])
    except Exception as e:
        pass
    return None

