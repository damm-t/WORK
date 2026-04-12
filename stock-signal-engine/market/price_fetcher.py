import yfinance as yf
import pandas as pd


def fetch_prices(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch OHLCV price data for a ticker.

    period:   how far back — "1mo", "3mo", "6mo", "1y"
    interval: candle size  — "1d" daily, "1h" hourly

    Returns a pandas DataFrame with columns:
    Open, High, Low, Close, Volume
    """
    try:
        # yf.Ticker gives us a rich object — like new StockClient(ticker)
        stock = yf.Ticker(ticker)

        # .history() fetches OHLCV — call it on the object, not yf.download
        df = stock.history(period=period, interval=interval)

        # pandas DataFrames use .empty — NOT "if not df"
        if df.empty:
            print(f"[fetch_prices] No data returned for {ticker}")
            return pd.DataFrame()

        return df

    except Exception as e:
        print(f"[fetch_prices] Error for {ticker}: {e}")
        return pd.DataFrame()