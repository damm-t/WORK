import pandas as pd
import logging

# Set up logging instead of basic print statements
logger = logging.getLogger(__name__)

try:
    import pandas_ta as ta
except ImportError as e:
    ta = None
    logger.error(f"Failed to import pandas_ta: {e}. Technical indicators disabled.")

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Appends technical indicators to the dataframe and standardizes column names.
    Requires at least 30 rows of historical data to calculate MACD properly.
    """
    if ta is None:
        raise RuntimeError("pandas_ta is not installed.")
        
    if df is None or df.empty:
        raise ValueError("Cannot calculate indicators on an empty DataFrame.")

    # Prevent dropping all data if the dataframe is too short
    if len(df) < 30:
         raise ValueError(f"Not enough data. Need at least 30 rows, got {len(df)}.")

    try:
        # Calculate Indicators
        df.ta.rsi(length=14, append=True)
        df.ta.macd(append=True)
        df.ta.bbands(length=20, append=True)
        df.ta.atr(length=14, append=True)
        # Tuned-profile trend filter needs long moving averages in features.
        df["SMA50"] = df["Close"].rolling(50).mean()
        df["SMA200"] = df["Close"].rolling(200).mean()

        # Volume ratio vs 20d average & pullback from 20d high
        if "Volume" in df.columns:
            v_roll = df["Volume"].rolling(20).mean()
            df["Volume_Ratio"] = (df["Volume"] / v_roll.replace(0, 1.0)).fillna(1.0)
        if "High" in df.columns and "Close" in df.columns:
            hi20 = df["High"].rolling(20).max().shift(1)
            df["Hi20"] = hi20
            df["Off_Hi20_Pct"] = ((df["Close"] / hi20.replace(0, 1.0) - 1.0) * 100.0).fillna(0.0)

        # Drop NaN rows from standard lookback periods (~26 days for MACD).
        # Only require SMA200/SMA50 if sufficient history is available.
        core_cols = [c for c in df.columns if c not in ("SMA200", "SMA50")]
        df.dropna(subset=core_cols, inplace=True)
        if len(df) >= 200:
            df.dropna(subset=["SMA200"], inplace=True)
        elif len(df) >= 50:
            df.dropna(subset=["SMA50"], inplace=True)

        # STANDARDIZE COLUMN NAMES
        # This is critical so your ML model doesn't break if you change indicator lengths
        rename_map = {
            "RSI_14": "RSI",
            "MACD_12_26_9": "MACD",
            "MACDh_12_26_9": "MACD_Histogram",
            "MACDs_12_26_9": "MACD_Signal",
            "BBL_20_2.0": "BB_Lower",
            "BBM_20_2.0": "BB_Middle",
            "BBU_20_2.0": "BB_Upper",
            "BBL_20_2.0_2.0": "BB_Lower",
            "BBM_20_2.0_2.0": "BB_Middle",
            "BBU_20_2.0_2.0": "BB_Upper",
            "ATRr_14": "ATR",
            "ATR_14": "ATR",
        }
        
        # Only rename columns that actually exist in the dataframe
        df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

        return df

    except Exception as e:
        logger.error(f"[add_indicators] Calculation error: {e}")
        # Re-raise so the API can catch it and return a clean 400/500 error
        raise

def get_latest(df: pd.DataFrame) -> dict:
    """
    Extracts the most recent row as a dictionary for the feature store.
    """
    if df is None or df.empty:
        return {}

    try:
        # Convert the last row to a dictionary
        latest_row = df.iloc[-1].to_dict()
        
        # Ensure we return floats, not numpy types, so FastAPI can serialize it to JSON properly
        return {k: (float(v) if pd.api.types.is_numeric_dtype(type(v)) else v) 
                for k, v in latest_row.items()}

    except Exception as e:
        logger.error(f"[get_latest] Extraction error: {e}")
        return {}