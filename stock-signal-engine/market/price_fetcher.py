from pathlib import Path

import pandas as pd
import requests

try:
    import yfinance as yf
except Exception as e:
    yf = None
    print(f"[price_fetcher] Error: {e}")

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0"}
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
            print(f"[fetch_prices] No data returned for {ticker}")
            return pd.DataFrame()

        return df
    except Exception as e:
        print(f"[fetch_prices] Error for {ticker}: {e}")
        return pd.DataFrame()


def _fetch_with_yfinance(ticker: str, period: str, interval: str) -> pd.DataFrame:
    try:
        if yf is None:
            return pd.DataFrame()

        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        return df if not df.empty else pd.DataFrame()
    except Exception as e:
        print(f"[price_fetcher] Error: {e}")
        return pd.DataFrame()


def _fetch_with_yahoo_chart(ticker: str, period: str, interval: str) -> pd.DataFrame:
    try:
        url = YAHOO_CHART_URL.format(ticker=ticker)
        response = requests.get(
            url,
            params={"range": period, "interval": interval},
            headers=YAHOO_HEADERS,
            timeout=20
        )
        response.raise_for_status()
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
