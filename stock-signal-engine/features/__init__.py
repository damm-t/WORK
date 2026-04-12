from .feature_store import build_feature_vector, add_label


def build_features(nlp_result: dict, market_features: dict) -> dict:
    """
    Single entry point for Layer 4.
    Combines NLP + market into one feature vector.
    """
    return build_feature_vector(nlp_result, market_features)