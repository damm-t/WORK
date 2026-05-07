def ensemble_signal(lgbm_prediction: dict, sentiment_score: float,
                    sentiment: str) -> dict:
    try:
        lgbm_signal = int(lgbm_prediction.get("signal", 0) or 0)
        lgbm_confidence = float(lgbm_prediction.get("confidence", 0.0) or 0.0)
        normalized_sentiment = str(sentiment or "").lower()
        finbert_score = float(sentiment_score) if normalized_sentiment == "positive" else 0.0
        ensemble_score = (lgbm_confidence * 0.7) + (finbert_score * 0.3)
        action = "BUY" if lgbm_signal == 1 and ensemble_score > 0.6 else "HOLD"
        reason = (
            f"LightGBM: {lgbm_confidence:.2f}, "
            f"FinBERT: {normalized_sentiment or 'neutral'} {float(sentiment_score):.2f}, "
            f"Score: {ensemble_score:.2f}"
        )
        return {
            "action": action,
            "confidence": round(float(ensemble_score), 4),
            "reason": reason
        }
    except Exception as e:
        print(f"[ensemble_signal] Error: {e}")
        return {"action": "HOLD", "confidence": 0.0, "reason": "error"}
