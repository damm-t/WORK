import os

from .predictor import load_model, predict
from .ensemble  import ensemble_signal

model = None
USE_LGBM_RUNTIME = os.getenv("USE_LGBM_RUNTIME", "0") == "1"


def _fallback_prediction(feature_vector: dict) -> dict:
    try:
        sentiment_score = float(feature_vector.get("sentiment_score", 0.0) or 0.0)
        macd = float(feature_vector.get("macd", 0.0) or 0.0)
        rsi = float(feature_vector.get("rsi", 50.0) or 50.0)
        rsi_overbought = int(feature_vector.get("rsi_overbought", 0) or 0)
        rsi_oversold = int(feature_vector.get("rsi_oversold", 0) or 0)

        confidence = sentiment_score * 0.5
        if macd > 0:
            confidence += 0.25
        if rsi_oversold == 1:
            confidence += 0.15
        if 35 <= rsi <= 65:
            confidence += 0.10
        if rsi_overbought == 1:
            confidence -= 0.20

        confidence = max(0.0, min(1.0, confidence))
        signal = 1 if confidence >= 0.6 else 0
        return {"signal": signal, "confidence": round(confidence, 4)}
    except Exception as e:
        print(f"[fallback_prediction] Error: {e}")
        return {"signal": 0, "confidence": 0.0}


def get_signal(feature_vector: dict, sentiment_score: float,
               sentiment: str) -> dict:
    try:
        global model

        if USE_LGBM_RUNTIME:
            if model is None:
                model = load_model()
            lgbm_result = predict(model, feature_vector)
        else:
            lgbm_result = _fallback_prediction(feature_vector)

        ensemble_result = ensemble_signal(lgbm_result, sentiment_score, sentiment)
        return ensemble_result

    except Exception as e:
        print(f"[get_signal] Error: {e}")
        return {
            "action":     "HOLD",
            "confidence": 0.0,
            "reason":     "error"
        }
