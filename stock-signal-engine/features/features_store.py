import pandas as pd


def build_feature_vector(nlp_result: dict, market_features: dict) -> dict:
    try:
        nlp_data = dict(nlp_result or {})
        market_data = dict(market_features or {})
        sentiment = str(nlp_data.get("sentiment", "neutral")).lower()
        is_positive = 1 if sentiment == "positive" else 0
        is_negative = 1 if sentiment == "negative" else 0
        is_neutral = 1 if sentiment == "neutral" else 0
        rsi = float(market_data.get("RSI_14", 0.0) or 0.0)
        macd = float(market_data.get("MACDh_12_26_9", 0.0) or 0.0)
        bb_upper = float(market_data.get("BBU_20_2.0", 0.0) or 0.0)
        bb_lower = float(market_data.get("BBL_20_2.0", 0.0) or 0.0)
        atr = float(market_data.get("ATRr_14", 0.0) or 0.0)
        bb_width = bb_upper - bb_lower
        rsi_overbought = 1 if rsi > 70 else 0
        rsi_oversold = 1 if rsi < 30 else 0
        return {
            "ticker":             str(nlp_data.get("ticker", "")),
            "sentiment_positive": is_positive,
            "sentiment_negative": is_negative,
            "sentiment_neutral":  is_neutral,
            "sentiment_score":    float(nlp_data.get("sentiment_score", 0.0) or 0.0),
            "rsi":                rsi,
            "macd":               macd,
            "bb_upper":           bb_upper,
            "bb_lower":           bb_lower,
            "atr":                atr,
            "bb_width":           bb_width,
            "rsi_overbought":     rsi_overbought,
            "rsi_oversold":       rsi_oversold,
        }
    except Exception as e:
        print(f"[build_feature_vector] Error: {e}")
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
