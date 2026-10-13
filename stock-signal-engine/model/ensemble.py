import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def ensemble_signal(
    lgbm_prediction: Dict[str, Any], 
    sentiment_score: float,
    sentiment: str,
    current_price: float,
    atr: float = None,
    buy_threshold: float = 0.60
) -> Dict[str, Any]:
    """
    Combines ML predictions with NLP sentiment. 
    Dynamically adjusts weights based on market volatility (ATR).
    """
    try:
        lgbm_signal = int(lgbm_prediction.get("signal", 0))
        lgbm_confidence = float(lgbm_prediction.get("confidence", 0.0))
        
        normalized_sentiment = str(sentiment or "neutral").strip().lower()
        raw_sentiment_score = float(sentiment_score)
        
        # 1. Directional Sentiment (Positive adds, Negative subtracts)
        if normalized_sentiment == "positive":
            directional_sentiment = raw_sentiment_score
        elif normalized_sentiment == "negative":
            directional_sentiment = -raw_sentiment_score
        else:
            directional_sentiment = 0.0
            
        # 2. DYNAMIC WEIGHTING BASED ON VOLATILITY
        # Default weights (Calm Market)
        lgbm_weight = 0.70
        sentiment_weight = 0.30
        
        if atr and current_price > 0:
            volatility_pct = atr / current_price
            
            # If the stock is highly volatile (e.g., moving more than 4% a day on average)
            # We trust technicals less, and trust the news sentiment more.
            if volatility_pct > 0.04:
                logger.info("High volatility detected. Shifting weight to NLP Sentiment.")
                lgbm_weight = 0.40       # Drop technical weight
                sentiment_weight = 0.60  # News drives the stock now
            
            # If volatility is moderately high (e.g., 2% to 4%)
            elif volatility_pct > 0.02:
                lgbm_weight = 0.55
                sentiment_weight = 0.45

        # 3. Calculate Final Dynamic Score
        ensemble_score = (lgbm_confidence * lgbm_weight) + (directional_sentiment * sentiment_weight)
        
        # 4. Determine Action
        action = "HOLD"
        if lgbm_signal == 1 and ensemble_score >= buy_threshold:
            action = "BUY"
            
        # 5. Format Reason for logging
        reason = (
            f"LGBM({lgbm_weight*100:.0f}% Conf:{lgbm_confidence:.2f}), "
            f"NLP({sentiment_weight*100:.0f}% {normalized_sentiment.upper()} {raw_sentiment_score:.2f}), "
            f"Final:{ensemble_score:.2f}"
        )
        
        final_confidence = max(0.0, min(float(ensemble_score), 1.0))

        return {
            "action": action,
            "confidence": round(final_confidence, 4),
            "reason": reason
        }

    except Exception as e:
        logger.error(f"[ensemble_signal] Error: {e}")
        return {"action": "HOLD", "confidence": 0.0, "reason": "System error in ensemble"}