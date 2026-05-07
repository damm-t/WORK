import pandas as pd

try:
    import pandas_ta as ta
except Exception as e:
    ta = None
    print(f"[indicators] Error: {e}")


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    try:
        if ta is None or df.empty or not hasattr(df, "ta"):
            return pd.DataFrame()

        df.ta.rsi(length=14, append=True)
        df.ta.macd(append=True)
        df.ta.bbands(length=20, append=True)
        df.ta.atr(length=14, append=True)
        df.dropna(inplace=True)

        return df

    except Exception as e:
        print(f"[add_indicators] Error: {e}")
        return pd.DataFrame()


def get_latest(df: pd.DataFrame) -> dict:
    try:
        latest_row = df.iloc[-1]
        return latest_row.to_dict()

    except Exception as e:
        print(f"[get_latest] Error: {e}")
        return {}
