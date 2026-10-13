import pandas as pd

def build_feature_vector(nlp_result: dict, market_features: dict) -> dict:
    try:
        nlp_data = dict(nlp_result or {})
        market_data = dict(market_features or {})
        
        # Standardize sentiment
        sentiment = str(nlp_data.get("sentiment", "neutral")).lower()
        
        # Pull from the standardized keys created in market/indicators.py
        rsi = float(market_data.get("RSI", 0.0))
        macd = float(market_data.get("MACD_Histogram", 0.0))
        bb_upper = float(market_data.get("BB_Upper", 0.0))
        bb_lower = float(market_data.get("BB_Lower", 0.0))
        atr = float(market_data.get("ATR", 0.0))
        
        return {
            "ticker":             str(nlp_data.get("ticker", "")),
            "sentiment_positive": 1 if sentiment == "positive" else 0,
            "sentiment_negative": 1 if sentiment == "negative" else 0,
            "sentiment_neutral":  1 if sentiment == "neutral" else 0,
            "sentiment_score":    float(nlp_data.get("sentiment_score", 0.0)),
            "rsi":                rsi,
            "macd":               macd,
            "bb_upper":           bb_upper,
            "bb_lower":           bb_lower,
            "atr":                atr,
            "bb_width":           bb_upper - bb_lower,
            "rsi_overbought":     1 if rsi > 70 else 0,
            "rsi_oversold":       1 if rsi < 30 else 0,
        }
    except Exception as e:
        print(f"[features_store] Sync Error: {e}")
        return {}

def add_label(feature_vector: dict, next_day_return: float, threshold: float = 0.01) -> dict:
    try:
        feature_data = dict(feature_vector or {})
        signal = 1 if next_day_return >= threshold else 0
        feature_data["signal"] = signal
        return feature_data
    except Exception as e:
        print(f"[add_label] Error: {e}")
        return {}