import joblib
import pandas as pd

FEATURE_COLS = [
    "sentiment_positive", "sentiment_negative", "sentiment_neutral",
    "sentiment_score", "rsi", "macd", "bb_upper", "bb_lower",
    "atr", "bb_width", "rsi_overbought", "rsi_oversold"
]


def load_model(model_path: str = "model/lgbm_model.pkl"):
    """
    Load trained model from disk.
    Returns the model object.
    """
    try:
        model = joblib.load(model_path)  # ✅ save the result
        if hasattr(model, "set_params"):
            try:
                model.set_params(n_jobs=1)
            except Exception:
                pass
        print(f"Model loaded from {model_path}")
        return model                     # ✅ return it

    except Exception as e:
        print(f"[load_model] Error loading {model_path}: {e}")
        return None                      # ✅ explicit None on failure


def predict(model, feature_vector: dict) -> dict:
    """
    Run prediction on a single feature vector.
    Returns dict with "signal" and "confidence" keys.
    """
    try:
        # Convert dict → DataFrame with correct column order
        data = pd.DataFrame([feature_vector])[FEATURE_COLS]

        # predict() → class label: 0 or 1
        signal = model.predict(data)[0]          # [0] = first (only) row

        # predict_proba() → [[prob_class_0, prob_class_1]]
        # [0]    = first sample
        # [1]    = probability of class 1 (BUY signal)
        confidence = model.predict_proba(data)[0][1]  # ✅ 2D indexing

        return {
            "signal":     int(signal),            # ✅ actual value, cast to int
            "confidence": round(float(confidence), 4)  # ✅ actual value, rounded
        }

    except Exception as e:
        print(f"[predict] Error: {e}")
        return {"signal": 0, "confidence": 0.0}