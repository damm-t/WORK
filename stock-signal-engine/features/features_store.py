import pandas as pd


def build_feature_vector(nlp_result: dict, market_features: dict) -> dict:
    """
    Merge NLP sentiment + market indicators into one flat feature vector.
    """

    # Step 1: encode sentiment string → numbers
    sentiment = nlp_result.get("sentiment", "neutral")

    is_positive = 1 if sentiment == "positive" else 0
    is_negative = 1 if sentiment == "negative" else 0
    is_neutral  = 1 if sentiment == "neutral"  else 0

    # Step 2: pull market values first so we can engineer from them
    # exact pandas-ta key names — always use .get() with 0.0 default
    rsi      = market_features.get("RSI_14", 0.0)
    macd     = market_features.get("MACDh_12_26_9", 0.0)
    bb_upper = market_features.get("BBU_20_2.0", 0.0)
    bb_lower = market_features.get("BBL_20_2.0", 0.0)
    atr      = market_features.get("ATRr_14", 0.0)

    # Step 3: engineer new features from raw values
    bb_width       = bb_upper - bb_lower          # band width = volatility measure
    rsi_overbought = 1 if rsi > 70 else 0         # binary flag
    rsi_oversold   = 1 if rsi < 30 else 0         # binary flag

    # Step 4: merge everything into one flat dict
    # Python dict syntax — "key": value, comma separated, no semicolons
    feature_vector = {
        "ticker":             nlp_result.get("ticker", ""),
        "sentiment_positive": is_positive,
        "sentiment_negative": is_negative,        # fixed typo: negetive → negative
        "sentiment_neutral":  is_neutral,
        "sentiment_score":    nlp_result.get("sentiment_score", 0.0),
        "rsi":                rsi,
        "macd":               macd,
        "bb_upper":           bb_upper,
        "bb_lower":           bb_lower,
        "atr":                atr,
        "bb_width":           bb_width,           # engineered
        "rsi_overbought":     rsi_overbought,     # engineered
        "rsi_oversold":       rsi_oversold,       # engineered
    }

    return feature_vector


def add_label(feature_vector: dict, next_day_return: float, threshold: float = 0.01) -> dict:
    """
    Add the target label to the feature vector for model training.
    """

    # 1 = price went up >= 1% next day → BUY signal
    # 0 = price did not go up           → no signal
    signal = 1 if next_day_return >= threshold else 0

    feature_vector["signal"]          = signal
    feature_vector["next_day_return"] = round(next_day_return, 6)

    return feature_vector