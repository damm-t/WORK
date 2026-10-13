import os
import logging

from .predictor import load_model, predict
from .ensemble  import ensemble_signal

logger = logging.getLogger(__name__)

model = None
USE_LGBM_RUNTIME = os.getenv("USE_LGBM_RUNTIME", "0") == "1"


def _fallback_prediction(feature_vector: dict) -> dict:
    """
    A rule-based backup if the LightGBM model fails to load or is disabled.
    Updated to handle standardized indicator keys (RSI, MACD) and negative sentiment.
    """
    try:
        # 1. Safely extract values (Checking both uppercase and lowercase just in case)
        sentiment_score = float(feature_vector.get("sentiment_score", 0.0))
        macd = float(feature_vector.get("MACD", feature_vector.get("macd", 0.0)))
        rsi = float(feature_vector.get("RSI", feature_vector.get("rsi", 50.0)))

        # 2. Start at a neutral 50% confidence
        confidence = 0.50 

        # 3. Apply Sentiment Adjustments
        # Positive score adds to confidence, negative score subtracts
        confidence += (sentiment_score * 0.30)

        # 4. Apply Technical Adjustments
        if macd > 0:
            confidence += 0.15  # Bullish momentum
        elif macd < 0:
            confidence -= 0.15  # Bearish momentum

        if rsi < 30: 
            confidence += 0.15  # Oversold (Price likely to bounce)
        elif rsi > 70:
            confidence -= 0.15  # Overbought (Price likely to drop)

        # 5. Clamp between 0.0 and 1.0 to prevent mathematical errors downstream
        confidence = max(0.0, min(1.0, confidence))
        
        # 6. Generate Signal
        signal = 1 if confidence >= 0.60 else 0
        
        return {"signal": signal, "confidence": round(confidence, 4)}
        
    except Exception as e:
        logger.error(f"[fallback_prediction] Error: {e}")
        return {"signal": 0, "confidence": 0.0}


def get_signal(
    feature_vector: dict, 
    sentiment_score: float,
    sentiment: str,
    current_price: float = 0.0,  # <-- NEW: Needed for dynamic ensemble
    atr: float = None            # <-- NEW: Needed for dynamic ensemble
) -> dict:
    """
    Retrieves the ML prediction and blends it with NLP sentiment.
    """
    try:
        global model

        if USE_LGBM_RUNTIME:
            if model is None:
                logger.info("Loading LightGBM model into memory...")
                model = load_model()
            lgbm_result = predict(model, feature_vector)
        else:
            lgbm_result = _fallback_prediction(feature_vector)

        # Pass all the new dynamic parameters to the ensemble!
        ensemble_result = ensemble_signal(
            lgbm_prediction=lgbm_result, 
            sentiment_score=sentiment_score, 
            sentiment=sentiment,
            current_price=current_price,
            atr=atr
        )
        
        return ensemble_result

    except Exception as e:
        logger.error(f"[get_signal] Error: {e}")
        return {
            "action":     "HOLD",
            "confidence": 0.0,
            "reason":     "Pipeline error in model execution."
        }