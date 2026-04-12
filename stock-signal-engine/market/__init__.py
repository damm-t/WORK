from .price_fetcher import fetch_prices
from .indicators    import add_indicators, get_latest


def get_market_features(ticker: str) -> dict:
    """
    Fetch prices + compute indicators + return latest row as dict.
    This is the single function Layer 4 will call.
    """
    try:
        df = fetch_prices(ticker)

        if df.empty:                  # ✅ Pythonic — no == True needed
            print(f"[get_market_features] No price data for {ticker}")
            return {}

        df     = add_indicators(df)
        latest = get_latest(df)

        return latest

    except Exception as e:
        print(f"[get_market_features] Error for {ticker}: {e}")
        return {}                     # ✅ always return correct type on failure