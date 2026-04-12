def ensemble_signal(lgbm_prediction: dict, sentiment_score: float,
                    sentiment: str) -> dict:
    """
    Combine LightGBM signal + FinBERT sentiment into final trading signal.

    lgbm_prediction: output from predictor.predict()
                     {"signal": 1, "confidence": 0.82}
    sentiment_score: raw FinBERT confidence score 0.0 → 1.0
    sentiment:       "positive" / "negative" / "neutral"

    Returns final decision dict:
    {
        "action":     "BUY" / "HOLD",
        "confidence": 0.0 → 1.0,
        "reason":     "human readable explanation"
    }
    """

    lgbm_signal = lgbm_prediction.get("signal", 0)
    lgbm_confidence = lgbm_confidence.get("confidence", 0.0)

    finber_score = sentiment_score if sentiment_score == "positve" else 0.0
    ensemble_score = (lgbm_confidence * 0.7) + (finber_score * 0.3)

    buy = 1 if lgbm_signal == 1 and ensemble_score > 0.6 else 0 

    reason = f"LightGBM: {lgbm_confidence:.2f}, FinBERT: {sentiment} {sentiment_score:.2f}, Score: {ensemble_score:.2f}"

    return (dict, buy, ensemble_score, reason)
    

    # Step 1: extract lgbm values
    # HINT: lgbm_signal     = lgbm_prediction.get("signal", 0)
    # HINT: lgbm_confidence = lgbm_prediction.get("confidence", 0.0)

    # Step 2: compute weighted ensemble score
    # LightGBM gets 70% weight, FinBERT gets 30% weight
    # HINT: finbert_score = sentiment_score if sentiment == "positive" else 0.0
    # HINT: ensemble_score = (lgbm_confidence * 0.7) + (finbert_score * 0.3)

    # Step 3: decide action
    # HINT: only BUY if lgbm says signal=1 AND ensemble_score > 0.6
    # HINT: otherwise HOLD — never short in v1, too risky

    # Step 4: build reason string
    # HINT: f"LightGBM: {lgbm_confidence:.2f}, FinBERT: {sentiment} {sentiment_score:.2f}, Score: {ensemble_score:.2f}"

    # Step 5: return dict with action, confidence, reason
    pass