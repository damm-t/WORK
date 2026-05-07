from .features_store import build_feature_vector, add_label


def build_features(nlp_result: dict, market_features: dict) -> dict:
    try:
        return build_feature_vector(nlp_result, market_features)
    except Exception as e:
        print(f"[build_features] Error: {e}")
        return {}
