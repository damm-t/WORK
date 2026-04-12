from .predictor import load_model, predict
from .ensemble  import ensemble_signal

# Load model once at startup — like a static singleton in C#
model = load_model()


def get_signal(feature_vector: dict, sentiment_score: float,
               sentiment: str) -> dict:
    """
    Full model pipeline — takes feature vector, returns trading signal.
    """
    try:
        lgbm_result     = predict(model, feature_vector)
        ensemble_result = ensemble_signal(lgbm_result, sentiment_score, sentiment)
        return ensemble_result

    except Exception as e:
        print(f"[get_signal] Error: {e}")              # ✅ always use e, not other variables
        return {
            "action":     "HOLD",
            "confidence": 0.0,
            "reason":     "error"
        }