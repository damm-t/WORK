import pandas as pd
import pandas_ta as ta


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a price DataFrame from fetch_prices.
    Adds RSI, MACD, Bollinger Bands, ATR columns.
    Returns enriched DataFrame.
    """
    try:
        df.ta.rsi(length=14, append=True)
        df.ta.macd(append=True)
        df.ta.bbands(length=20, append=True)
        df.ta.atr(length=14, append=True)
        df.dropna(inplace=True)

        return df

    except Exception as e:
        print(f"[add_indicators] Error: {e}")   # ✅ removed {ticker} — not in scope
        return pd.DataFrame()                    # ✅ safe empty DataFrame, not bare return


def get_latest(df: pd.DataFrame) -> dict:
    """
    Extract the most recent row of indicators as a plain dict.
    This is what gets passed to the feature store in Layer 4.
    """
    try:
        latest_row = df.iloc[-1]
        return latest_row.to_dict()

    except Exception as e:
        print(f"[get_latest] Error: {e}")   # ✅ fixed function name in message
        return {}                            # ✅ safe empty dict, not bare return